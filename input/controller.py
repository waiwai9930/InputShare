from pynput import keyboard, mouse
from android.hid_event import KeyEmptyEvent
from input.callbacks import KeyEventCallback, MouseClickCallback, MouseMoveCallback, MouseScrollCallback, SendDataCallback
from input.edge_portal import edge_portal_thread_factory
from ui.fullscreen_mask import mask_thread_factory
from utils import StopException

is_redirecting = False
to_toggle_flag = False
to_exit_flag = False
to_program_move_mouse_flag = False
keyboard_listener = None
mouse_listener = None

def schedule_toggle():
    global to_toggle_flag
    to_toggle_flag = True

def schedule_exit():
    global to_exit_flag
    schedule_toggle()
    to_exit_flag = True

switch_key_combination = "<ctrl>+<alt>+s"
exit_key_combination = "<ctrl>+<alt>+q"
switch_hotkey = keyboard.HotKey(keyboard.HotKey.parse(switch_key_combination), schedule_toggle)
exit_hotkey = keyboard.HotKey(keyboard.HotKey.parse(exit_key_combination), schedule_exit)

def keyboard_press_handler_factory(callback: KeyEventCallback):
    def keyboard_press_handler(k: keyboard.Key):
        global to_toggle_flag, to_exit_flag, is_redirecting
        canonical_k = keyboard_listener.canonical(k) # type: ignore
        switch_hotkey.press(canonical_k)
        exit_hotkey.press(canonical_k)

        if to_toggle_flag == True:
            is_redirecting = not is_redirecting
            return False

        try:
            callback(canonical_k, is_redirecting)
        except StopException:
            to_exit_flag = True
            return False
    return keyboard_press_handler

def keyboard_release_handler_factory(callback: KeyEventCallback):
    def keyboard_release_handler(k: keyboard.Key):
        global to_toggle_flag, to_exit_flag, is_redirecting
        canonical_k = keyboard_listener.canonical(k) # type: ignore
        switch_hotkey.release(canonical_k)
        exit_hotkey.release(canonical_k)

        try:
            callback(canonical_k, is_redirecting)
        except StopException:
            to_exit_flag = True
            return False
    return keyboard_release_handler

def mouse_move_handler_factory(callback: MouseMoveCallback):
    def mouse_move_handler(x: int, y: int):
        global to_exit_flag, is_redirecting
        try:
            callback(x, y, is_redirecting)
        except StopException:
            to_exit_flag = True
            return False
    return mouse_move_handler

def mouse_click_handler_factory(callback: MouseClickCallback):
    def mouse_click_handler(x: int, y: int, button: mouse.Button, pressed: bool):
        global to_exit_flag, is_redirecting
        try:
            callback(x, y, button, pressed, is_redirecting)
        except StopException:
            to_exit_flag = True
            return False
    return mouse_click_handler

def mouse_scroll_handler_factory(callback: MouseScrollCallback):
    def mouse_scroll_handler(x: int, y: int, dx: int, dy: int):
        global to_exit_flag, is_redirecting
        if callback is not None:
            try:
                callback(x, y, dx, dy, is_redirecting)
            except StopException:
                to_exit_flag = True
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
    global keyboard_listener, to_toggle_flag

    def toggle_redirecting_state():
        nonlocal close_mask, close_edge_portal
        if is_redirecting:
            close_mask = mask_thread_factory()
            close_edge_portal = edge_portal_thread_factory()
            print("[Info] Input redirecting enabled.")
        else:
            send_data(KeyEmptyEvent().serialize())
            if close_mask is not None:
                close_mask()
                close_mask = None
            if close_edge_portal is not None:
                close_edge_portal()
                close_edge_portal = None
            print("[Info] Input redirecting disabled.")

    show_function_message()
    close_mask = None
    close_edge_portal = None

    while not to_exit_flag:
        toggle_redirecting_state()

        with keyboard.Listener(
                suppress=is_redirecting,
                on_press=keyboard_press_handler_factory(keyboard_press_callback), # type: ignore
                on_release=keyboard_release_handler_factory(keyboard_release_callback), # type: ignore
            ) as keyboard_listener,\
            mouse.Listener(
                on_move=mouse_move_handler_factory(mouse_move_callback),
                on_click=mouse_click_handler_factory(mouse_click_callback),
                on_scroll=mouse_scroll_handler_factory(mouse_scroll_callback),
            ) as mouse_listener:
            keyboard_listener.join()
            if to_toggle_flag:
                to_toggle_flag = False
                continue
            mouse_listener.join()

    if close_mask is not None: close_mask(True)
    if close_edge_portal is not None: close_edge_portal()
