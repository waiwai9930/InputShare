from typing import Callable
from pynput import keyboard, mouse

from ui import mask_thread_factory

is_redirecting = False
keyboard_listener = None
mouse_listener = None
to_toggle_flag = False
to_exit_flag = False

Key = keyboard.Key
KeyCode = keyboard.KeyCode
KeyEventCallback = Callable[[Key | KeyCode, bool], None]
MouseMoveCallback = Callable[[int, int, bool], None]
MouseClickCallback = Callable[[int, int, mouse.Button, bool, bool], None]

class StopException(Exception):
    """If an event listener callback raises this exception, the current
    listener is stopped.
    """
    pass

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

def keyboard_press_handler_factory(
    callback: KeyEventCallback | None
):
    def keyboard_press_handler(k: Key):
        global to_toggle_flag, to_exit_flag, is_redirecting
        canonical_k = keyboard_listener.canonical(k) # type: ignore
        switch_hotkey.press(canonical_k)
        exit_hotkey.press(canonical_k)

        if callback is not None:
            try:
                callback(canonical_k, is_redirecting)
            except StopException:
                to_exit_flag = True
                return False

        if to_toggle_flag == True:
            is_redirecting = not is_redirecting
            return False
    return keyboard_press_handler

def keyboard_release_handler_factory(
    callback: KeyEventCallback | None
):
    def keyboard_release_handler(k: Key):
        global to_toggle_flag, to_exit_flag, is_redirecting
        canonical_k = keyboard_listener.canonical(k) # type: ignore
        switch_hotkey.release(canonical_k)
        exit_hotkey.release(canonical_k)

        if callback is not None:
            try:
                callback(canonical_k, is_redirecting)
            except StopException:
                to_exit_flag = True
                return False
    return keyboard_release_handler

def mouse_move_handler_factory(
    callback: MouseMoveCallback | None
):
    def mouse_move_release_handler(x: int, y: int):
        global to_exit_flag, is_redirecting
        if callback is not None:
            try:
                callback(x, y, is_redirecting)
            except StopException:
                to_exit_flag = True
                return False
    return mouse_move_release_handler

def mouse_click_handler_factory(
    callback: MouseClickCallback | None
):
    def mouse_click_release_handler(x: int, y: int, button: mouse.Button, pressed: bool):
        global to_exit_flag, is_redirecting
        if callback is not None:
            try:
                callback(x, y, button, pressed, is_redirecting)
            except StopException:
                to_exit_flag = True
                return False
    return mouse_click_release_handler

def show_function_message():
    print(f'''\
Push {switch_key_combination} to enable/disable redirecting mouse and keyboard input.
Push {exit_key_combination} to exit.''')

def main_loop(
    keyboard_press_callback: KeyEventCallback,
    keyboard_release_callback: KeyEventCallback,
    mouse_move_callback: MouseMoveCallback,
    mouse_click_callback: MouseClickCallback,
):
    global keyboard_listener, to_toggle_flag

    show_function_message()
    mask_closer = None

    while not to_exit_flag:
        if is_redirecting:
            mask_closer = mask_thread_factory()
            print("[Info] Input redirecting enabled.")
        else:
            if mask_closer is not None: mask_closer()
            print("[Info] Input redirecting disabled.")

        with keyboard.Listener(
                suppress=is_redirecting,
                on_press=keyboard_press_handler_factory(keyboard_press_callback),
                on_release=keyboard_release_handler_factory(keyboard_release_callback),
            ) as keyboard_listener,\
            mouse.Listener(
                on_move=mouse_move_handler_factory(mouse_move_callback),
                on_click=mouse_click_handler_factory(mouse_click_callback),
            ) as mouse_listener:
            keyboard_listener.join()
            if to_toggle_flag:
                to_toggle_flag = False
                continue
            mouse_listener.join()

    if mask_closer is not None: mask_closer()
