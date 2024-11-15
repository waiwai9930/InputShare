import socket
import threading
import time

from queue import Queue
from typing import Callable
from pynput import mouse, keyboard
from scrcpy_client import key_scancode_map
from scrcpy_client.android_def import AKeyCode, AKeyEventAction
from scrcpy_client.hid_def import HID_KEYBOARD_MAX_KEYS, HID_MouseButton, HIDKeymod, KeymodStateStore, MouseButtonStateStore
from scrcpy_client.hid_event import HIDKeyboardInitEvent, KeyEmptyEvent, KeyEvent, MouseClickEvent, MouseMoveEvent, MouseScrollEvent, HIDMouseInitEvent
from scrcpy_client.inject_event import InjectKeyCode
from scrcpy_client.sdl_def import SDL_Scancode
from input.edge_portal import edge_portal_passing_event
from utils.config_manager import CONFIG

CallbackResult = Exception | None
SendDataCallback = Callable[[bytes], CallbackResult]
KeyEventCallback = Callable[[keyboard.Key | keyboard.KeyCode, bool], CallbackResult]
MouseMoveCallback = Callable[[int, int, bool], CallbackResult]
MouseClickCallback = Callable[[int, int, mouse.Button, bool, bool], CallbackResult]
MouseScrollCallback = Callable[[int, int, int, int, bool], CallbackResult]

def callback_context_wrapper(
    client_socket: socket.socket,
) -> tuple[
    SendDataCallback,
    KeyEventCallback, KeyEventCallback,
    MouseMoveCallback, MouseClickCallback, MouseScrollCallback,
]:
    def send_data(data: bytes) -> CallbackResult:
        nonlocal client_socket
        try:
            client_socket.sendall(data)
        except Exception as e:
            return e
        return None

    keyboard_init = HIDKeyboardInitEvent()
    send_data(keyboard_init.serialize())
    keymod_state = KeymodStateStore()
    key_list: list[SDL_Scancode] = []

    def customized_shortcuts(k: SDL_Scancode | HIDKeymod | AKeyCode, is_redirecting: bool) -> list[bytes] | None:
        if is_redirecting: return None
        if keymod_state.has_key(HIDKeymod.HID_MOD_LEFT_ALT) or keymod_state.has_key(HIDKeymod.HID_MOD_RIGHT_ALT):
            if k in [SDL_Scancode.SDL_SCANCODE_UP, SDL_Scancode.SDL_SCANCODE_DOWN]:
                return [KeyEvent(KeymodStateStore(), [k]).serialize(), KeyEmptyEvent().serialize()]
            if k == SDL_Scancode.SDL_SCANCODE_LEFTBRACKET:
                return [
                    InjectKeyCode(AKeyCode.AKEYCODE_MEDIA_PREVIOUS, AKeyEventAction.AKEY_EVENT_ACTION_DOWN).serialize(),
                    InjectKeyCode(AKeyCode.AKEYCODE_MEDIA_PREVIOUS, AKeyEventAction.AKEY_EVENT_ACTION_UP).serialize()
                ]
            if k == SDL_Scancode.SDL_SCANCODE_RIGHTBRACKET:
                return [
                    InjectKeyCode(AKeyCode.AKEYCODE_MEDIA_NEXT, AKeyEventAction.AKEY_EVENT_ACTION_DOWN).serialize(),
                    InjectKeyCode(AKeyCode.AKEYCODE_MEDIA_NEXT, AKeyEventAction.AKEY_EVENT_ACTION_UP).serialize()
                ]
            if k == SDL_Scancode.SDL_SCANCODE_BACKSLASH:
                return [
                    InjectKeyCode(AKeyCode.AKEYCODE_MEDIA_PLAY_PAUSE, AKeyEventAction.AKEY_EVENT_ACTION_DOWN).serialize(),
                    InjectKeyCode(AKeyCode.AKEYCODE_MEDIA_PLAY_PAUSE, AKeyEventAction.AKEY_EVENT_ACTION_UP).serialize()
                ]
        return None

    def keyboard_press_callback(k: keyboard.Key | keyboard.KeyCode, is_redirecting: bool) -> CallbackResult:
        if k not in key_scancode_map: return None
        generic_key = key_scancode_map[k]
        shortcut_data = customized_shortcuts(generic_key, is_redirecting)
        if shortcut_data is not None:
            for data in shortcut_data:
                res = send_data(data)
                if res is not None:
                    return res
            return None

        if isinstance(generic_key, HIDKeymod):
            keymod_state.keydown(generic_key)

        if not is_redirecting: return None
        if isinstance(generic_key, AKeyCode):
            inject_key_code = InjectKeyCode(generic_key, AKeyEventAction.AKEY_EVENT_ACTION_DOWN)
            return send_data(inject_key_code.serialize())
        if isinstance(generic_key, SDL_Scancode) and generic_key not in key_list:
            key_list.append(generic_key)
            if len(key_list) > HID_KEYBOARD_MAX_KEYS:
                key_to_remove = key_list[0]
                key_list.remove(key_to_remove)
        key_event = KeyEvent(keymod_state, key_list)
        return send_data(key_event.serialize())

    def keyboard_release_callback(k: keyboard.Key | keyboard.KeyCode, is_redirecting: bool) -> CallbackResult:
        if k not in key_scancode_map: return None
        generic_key = key_scancode_map[k]
        if isinstance(generic_key, HIDKeymod):
            keymod_state.keyup(generic_key)

        if not is_redirecting: return None
        if isinstance(generic_key, AKeyCode):
            inject_key_code = InjectKeyCode(generic_key, AKeyEventAction.AKEY_EVENT_ACTION_UP)
            return send_data(inject_key_code.serialize())
        if isinstance(generic_key, SDL_Scancode) and generic_key in key_list:
            key_list.remove(generic_key)
        key_event = KeyEvent(keymod_state, key_list)
        return send_data(key_event.serialize())

    # --- --- --- --- --- ---

    mouse_init = HIDMouseInitEvent()
    send_data(mouse_init.serialize())
    last_mouse_point: tuple[int, int] | None = None
    mouse_button_state = MouseButtonStateStore()
    movement_queue: Queue[tuple[int, int]] = Queue(maxsize=4)

    from input.controller import schedule_exit
    def mouse_movement_sender():
        nonlocal send_data
        DEFAULT_INTERVAL_SEC = 1 / 120
        INTERVAL_INCR = 1 / 30
        INTERVAL_INCR_FACTOR = 60

        interval_sec = DEFAULT_INTERVAL_SEC
        no_move_counter = 0
        last_call_time = time.perf_counter()
        while True:
            call_time_diff = time.perf_counter() - last_call_time
            last_call_time = time.perf_counter()
            if call_time_diff < interval_sec:
                time.sleep(interval_sec - call_time_diff)

            if movement_queue.empty():
                no_move_counter += 1
                if no_move_counter > INTERVAL_INCR_FACTOR:
                    interval_sec = INTERVAL_INCR
                event = MouseMoveEvent(0, 0, mouse_button_state)
                res = send_data(event.serialize())
                if res is not None: schedule_exit(res); break
                continue

            no_move_counter = 0
            interval_sec = DEFAULT_INTERVAL_SEC
            x, y = movement_queue.get()
            event = MouseMoveEvent(x, y, mouse_button_state)
            res = send_data(event.serialize())
            if res is not None: schedule_exit(res); break
    threading.Thread(target=mouse_movement_sender, daemon=True).start()

    def compute_mouse_pointer_diff(cur_x: int, cur_y: int) -> tuple[int, int] | None:
        nonlocal last_mouse_point
        if last_mouse_point is None:
            last_mouse_point = (cur_x, cur_y)
            return None
        last_x, last_y = last_mouse_point
        last_mouse_point = (cur_x, cur_y)

        diff_x = cur_x - last_x
        diff_y = cur_y - last_y
        speed = (diff_x ** 2 + diff_y ** 2) ** 0.5
        adjusted_scale = 1 if speed == 0 else min(1, 2 / (speed ** 0.5))
        diff_x = int(diff_x * adjusted_scale)
        diff_y = int(diff_y * adjusted_scale)
        return diff_x, diff_y

    def mouse_move_callback(cur_x: int, cur_y: int, is_redirecting: bool) -> CallbackResult:
        nonlocal last_mouse_point
        if not is_redirecting or CONFIG.config.share_keyboard_only:
            last_mouse_point = None
            return None

        if edge_portal_passing_event.is_set():
            last_mouse_point = None
            edge_portal_passing_event.clear()
            return None
        res = compute_mouse_pointer_diff(cur_x, cur_y)
        if res is None: return None
        movement_queue.put(res)

    def mouse_click_callback(_cur_x: int, _cur_y: int, button: mouse.Button, pressed: bool, is_redirecting: bool) -> CallbackResult:
        nonlocal last_mouse_point
        if not is_redirecting or CONFIG.config.share_keyboard_only:
            return None

        hid_button = HID_MouseButton.MOUSE_BUTTON_NONE
        match button:
            case mouse.Button.left:
                hid_button = HID_MouseButton.MOUSE_BUTTON_LEFT
            case mouse.Button.right:
                hid_button = HID_MouseButton.MOUSE_BUTTON_RIGHT
            case mouse.Button.middle:
                hid_button = HID_MouseButton.MOUSE_BUTTON_MIDDLE
        if pressed:
            mouse_button_state.mouse_down(hid_button)
        else:
            mouse_button_state.mouse_up(hid_button)
        mouse_move_event = MouseClickEvent(mouse_button_state)
        return send_data(mouse_move_event.serialize())
    
    def mouse_scroll_callback(_cur_x: int, _cur_y: int, _dx: int, dy: int, is_redirecting: bool) -> CallbackResult:
        if not is_redirecting or CONFIG.config.share_keyboard_only:
            return None
        mouse_scroll_event = MouseScrollEvent(dy)
        return send_data(mouse_scroll_event.serialize())

    return (
        send_data,
        keyboard_press_callback,
        keyboard_release_callback,
        mouse_move_callback,
        mouse_click_callback,
        mouse_scroll_callback,
    )
