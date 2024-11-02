import socket

from subprocess import Popen
from typing import Callable
from pynput import mouse, keyboard
from scrcpy_client import key_scancode_map
from scrcpy_client.android_def import AKeyCode, AKeyEventAction
from scrcpy_client.hid_def import HID_KEYBOARD_MAX_KEYS, HID_MouseButton, HIDKeymod, KeymodStateStore, MouseButtonStateStore
from scrcpy_client.hid_event import HIDKeyboardInitEvent, KeyEmptyEvent, KeyEvent, MouseClickEvent, MouseMoveEvent, MouseScrollEvent, HIDMouseInitEvent
from scrcpy_client.inject_event import InjectKeyCode
from scrcpy_client.sdl_def import SDL_Scancode
from input.edge_portal import edge_portal_passing_event
from utils import StopException

SendDataCallback = Callable[[bytes], None]
KeyEventCallback = Callable[[keyboard.Key | keyboard.KeyCode, bool], None]
MouseMoveCallback = Callable[[int, int, bool], None]
MouseClickCallback = Callable[[int, int, mouse.Button, bool, bool], None]
MouseScrollCallback = Callable[[int, int, int, int, bool], None]

def callback_context_wrapper(
    client_socket: socket.socket,
    server_process: Popen[str],
) -> tuple[
    SendDataCallback,
    KeyEventCallback, KeyEventCallback,
    MouseMoveCallback, MouseClickCallback, MouseScrollCallback,
]:
    def send_data(data: bytes):
        try:
            client_socket.sendall(data)
        except Exception as e:
            print("[Error] Send data error: ", e)
            client_socket.close()
            server_process.terminate()
            raise StopException

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
        return None

    def keyboard_press_callback(k: keyboard.Key | keyboard.KeyCode, is_redirecting: bool):
        if k not in key_scancode_map: return
        generic_key = key_scancode_map[k]
        shortcut_data = customized_shortcuts(generic_key, is_redirecting)
        if shortcut_data is not None:
            for data in shortcut_data: send_data(data)
            return

        if isinstance(generic_key, HIDKeymod):
            keymod_state.keydown(generic_key)

        if not is_redirecting: return
        if isinstance(generic_key, AKeyCode):
            inject_key_code = InjectKeyCode(generic_key, AKeyEventAction.AKEY_EVENT_ACTION_DOWN)
            send_data(inject_key_code.serialize())
            return
        if isinstance(generic_key, SDL_Scancode) and generic_key not in key_list:
            key_list.append(generic_key)
            if len(key_list) > HID_KEYBOARD_MAX_KEYS:
                key_to_remove = key_list[0]
                key_list.remove(key_to_remove)
        key_event = KeyEvent(keymod_state, key_list)
        send_data(key_event.serialize())

    def keyboard_release_callback(k: keyboard.Key | keyboard.KeyCode, is_redirecting: bool):
        if k not in key_scancode_map: return
        generic_key = key_scancode_map[k]
        if isinstance(generic_key, HIDKeymod):
            keymod_state.keyup(generic_key)

        if not is_redirecting: return
        if isinstance(generic_key, AKeyCode):
            inject_key_code = InjectKeyCode(generic_key, AKeyEventAction.AKEY_EVENT_ACTION_UP)
            send_data(inject_key_code.serialize())
            return
        if isinstance(generic_key, SDL_Scancode) and generic_key in key_list:
            key_list.remove(generic_key)
        key_event = KeyEvent(keymod_state, key_list)
        send_data(key_event.serialize())

    # --- --- --- --- --- ---

    mouse_init = HIDMouseInitEvent()
    send_data(mouse_init.serialize())
    last_mouse_point: tuple[int, int] | None = None
    mouse_button_state = MouseButtonStateStore()

    def compute_mouse_pointer_diff(cur_x: int, cur_y: int) -> tuple[int, int] | None:
        nonlocal last_mouse_point
        if last_mouse_point is None:
            last_mouse_point = (cur_x, cur_y)
            return None
        smooth_factor = 0.8
        last_x, last_y = last_mouse_point
        last_mouse_point = (cur_x, cur_y)

        smoothed_x = int(smooth_factor * cur_x + (1 - smooth_factor) * last_x)
        smoothed_y = int(smooth_factor * cur_y + (1 - smooth_factor) * last_y)
        diff_x = smoothed_x - last_x
        diff_y = smoothed_y - last_y
        return (diff_x, diff_y)

    def mouse_move_callback(cur_x: int, cur_y: int, is_redirecting: bool):
        nonlocal last_mouse_point
        if not is_redirecting:
            last_mouse_point = None
            return
    
        if edge_portal_passing_event.is_set():
            last_mouse_point = None
            edge_portal_passing_event.clear()
            return
        res = compute_mouse_pointer_diff(cur_x, cur_y)
        if res is None:
            return
        diff_x, diff_y = res
        mouse_move_event = MouseMoveEvent(diff_x, diff_y, mouse_button_state)
        send_data(mouse_move_event.serialize())

    def mouse_click_callback(_cur_x: int, _cur_y: int, button: mouse.Button, pressed: bool, is_redirecting: bool):
        nonlocal last_mouse_point
        if not is_redirecting:
            return
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
        send_data(mouse_move_event.serialize())
    
    def mouse_scroll_callback(_cur_x: int, _cur_y: int, _dx: int, dy: int, is_redirecting: bool):
        if not is_redirecting:
            return
        mouse_scroll_event = MouseScrollEvent(dy)
        send_data(mouse_scroll_event.serialize())

    return (
        send_data,
        keyboard_press_callback,
        keyboard_release_callback,
        mouse_move_callback,
        mouse_click_callback,
        mouse_scroll_callback,
    )
