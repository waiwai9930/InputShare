import threading
from pynput import keyboard, mouse
from scrcpy_client.clipboard_event import GetClipboardEvent, SetClipboardEvent
from scrcpy_client.hid_event import KeyEmptyEvent
from input.callbacks import KeyEventCallback, MouseClickCallback, MouseMoveCallback, MouseScrollCallback, SendDataCallback
from input.edge_portal import edge_portal_thread_factory
from server.receiver import ReceivedClipboardText
from ui.fullscreen_mask import mask_thread_factory
from utils import Clipboard, StopException

is_redirecting = False
toggle_event = threading.Event()
exit_event = threading.Event()
keyboard_listener = None

def schedule_toggle():
    global toggle_event
    toggle_event.set()

def schedule_exit():
    global exit_event
    schedule_toggle()
    exit_event.set()

switch_key_combination = "<ctrl>+<alt>+s"
exit_key_combination = "<ctrl>+<alt>+q"
switch_hotkey = keyboard.HotKey(keyboard.HotKey.parse(switch_key_combination), schedule_toggle)
exit_hotkey = keyboard.HotKey(keyboard.HotKey.parse(exit_key_combination), schedule_exit)

def keyboard_press_handler_factory(callback: KeyEventCallback):
    def keyboard_press_handler(k: keyboard.Key):
        global is_redirecting
        canonical_k = keyboard_listener.canonical(k) # type: ignore
        switch_hotkey.press(canonical_k)
        exit_hotkey.press(canonical_k)

        try:
            callback(canonical_k, is_redirecting)
        except StopException:
            schedule_exit()
            return False
    return keyboard_press_handler

def keyboard_release_handler_factory(callback: KeyEventCallback):
    def keyboard_release_handler(k: keyboard.Key):
        global is_redirecting
        canonical_k = keyboard_listener.canonical(k) # type: ignore
        switch_hotkey.release(canonical_k)
        exit_hotkey.release(canonical_k)

        try:
            callback(canonical_k, is_redirecting)
        except StopException:
            schedule_exit()
            return False
    return keyboard_release_handler

def mouse_move_handler_factory(callback: MouseMoveCallback):
    def mouse_move_handler(x: int, y: int):
        global is_redirecting
        try:
            callback(x, y, is_redirecting)
        except StopException:
            schedule_exit()
            return False
    return mouse_move_handler

def mouse_click_handler_factory(callback: MouseClickCallback):
    def mouse_click_handler(x: int, y: int, button: mouse.Button, pressed: bool):
        global is_redirecting
        try:
            callback(x, y, button, pressed, is_redirecting)
        except StopException:
            schedule_exit()
            return False
    return mouse_click_handler

def mouse_scroll_handler_factory(callback: MouseScrollCallback):
    def mouse_scroll_handler(x: int, y: int, dx: int, dy: int):
        global is_redirecting
        if callback is not None:
            try:
                callback(x, y, dx, dy, is_redirecting)
            except StopException:
                schedule_exit()
                return False
    return mouse_scroll_handler

def show_function_message():
    print(f'''\
Push {switch_key_combination} to enable/disable redirecting mouse and keyboard input.
Push {exit_key_combination} to exit.''')

def main_loop(
    send_data: SendDataCallback,
    keyboard_press_callback: KeyEventCallback,
    keyboard_release_callback: KeyEventCallback,
    mouse_move_callback: MouseMoveCallback,
    mouse_click_callback: MouseClickCallback,
    mouse_scroll_callback: MouseScrollCallback,
):
    global is_redirecting, keyboard_listener

    def try_send_data(data: bytes):
        try:
            send_data(data)
        except StopException:
            schedule_exit()

    def toggle_redirecting_state(is_redirecting: bool):
        nonlocal show_mask, hide_mask,\
            start_edge_portal, pause_edge_portal
        if is_redirecting:
            show_mask()
            start_edge_portal()
            print("[Info] Input redirecting enabled.")
        else:
            try_send_data(KeyEmptyEvent().serialize())
            hide_mask()
            pause_edge_portal()
            print("[Info] Input redirecting disabled.")
    
    def toggle_callback(is_redirecting: bool):
        if is_redirecting:
            last_received = ReceivedClipboardText.read()
            current_clipboard_content = Clipboard.safe_paste()
            if not Clipboard.sync_clipboard: return
            if last_received is None: return
            if current_clipboard_content is None: return
            if last_received == current_clipboard_content: return
            try_send_data(SetClipboardEvent(current_clipboard_content).serialize())

    show_function_message()
    try_send_data(GetClipboardEvent().serialize()) # start server clipboard sync
    show_mask, hide_mask, exit_mask = mask_thread_factory()
    start_edge_portal, pause_edge_portal, close_edge_portal = edge_portal_thread_factory()

    mouse_listener = mouse.Listener(
        on_move=mouse_move_handler_factory(mouse_move_callback),
        on_click=mouse_click_handler_factory(mouse_click_callback),
        on_scroll=mouse_scroll_handler_factory(mouse_scroll_callback),
    )
    mouse_listener.start()
    while not exit_event.is_set():
        toggle_redirecting_state(is_redirecting)
        keyboard_listener = keyboard.Listener(
            suppress=is_redirecting,
            on_press=keyboard_press_handler_factory(keyboard_press_callback), # type: ignore
            on_release=keyboard_release_handler_factory(keyboard_release_callback), # type: ignore
        )
        keyboard_listener.start()
        toggle_event.wait()
        is_redirecting = not is_redirecting
        toggle_callback(is_redirecting)
        toggle_event.clear()
        keyboard_listener.stop()

    mouse_listener.stop()
    exit_mask()
    close_edge_portal()
