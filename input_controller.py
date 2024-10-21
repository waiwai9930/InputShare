from typing import Callable
from pynput import keyboard, mouse

is_redirecting = False
keyboard_listener = None
to_toggle_flag = False
to_exit_flag = False

Key = keyboard.Key
KeyCode = keyboard.KeyCode
KeyEventCallback = Callable[[Key | KeyCode, bool], None]

def schedule_toggle():
    global to_toggle_flag
    to_toggle_flag = True

def schedule_exit():
    global to_exit_flag
    schedule_toggle()
    to_exit_flag = True

switch_key_combination = '<ctrl>+<alt>+s'
exit_key_combination = '<ctrl>+<alt>+q'
switch_hotkey = keyboard.HotKey(keyboard.HotKey.parse(switch_key_combination), schedule_toggle)
exit_hotkey = keyboard.HotKey(keyboard.HotKey.parse(exit_key_combination), schedule_exit)

def keyboard_press_handler_factory(
    callback: KeyEventCallback | None
):
    def keyboard_press_handler(k: keyboard.Key):
        global to_toggle_flag, is_redirecting
        canonical_k = keyboard_listener.canonical(k) # type: ignore
        switch_hotkey.press(canonical_k)
        exit_hotkey.press(canonical_k)

        if callback is not None:
            callback(canonical_k, is_redirecting)

        if to_toggle_flag == True:
            to_toggle_flag = False
            is_redirecting = not is_redirecting
            return False
    return keyboard_press_handler

def keyboard_release_handler(k):
    canonical_k = keyboard_listener.canonical(k) # type: ignore
    switch_hotkey.release(canonical_k)
    exit_hotkey.release(canonical_k)

def show_function_message():
    print(f'''\
Push {switch_key_combination} to enable/disable redirecting mouse and keyboard input.
Push {exit_key_combination} to exit.\
    ''')

def main_loop(key_event_callback: KeyEventCallback | None = None):
    global keyboard_listener

    show_function_message()
    while not to_exit_flag:
        if is_redirecting:
            print("Input redirecting enabled.")
        else:
            print("Input redirecting disabled.")

        with keyboard.Listener(
                suppress=is_redirecting,
                on_press=keyboard_press_handler_factory(key_event_callback),
                on_release=keyboard_release_handler,
            ) as keyboard_listener:
            keyboard_listener.join()
