import threading
from pynput import keyboard, mouse  # https://github.com/moses-palmer/pynput

is_redirecting = False
keyboard_listener = None
to_toggle_flag = False

def schedule_toggle():
    global to_toggle_flag
    to_toggle_flag = True

switch_key_combination = '<ctrl>+<alt>+s'
switch_hotkey = keyboard.HotKey(keyboard.HotKey.parse(switch_key_combination), schedule_toggle)

def keyboard_press_handler(k):
    global to_toggle_flag, is_redirecting
    print(k)
    canonical_k = keyboard_listener.canonical(k)
    switch_hotkey.press(canonical_k)

    if to_toggle_flag == True:
        to_toggle_flag = False
        is_redirecting = not is_redirecting
        return False

def keyboard_release_handler(k):
    canonical_k = keyboard_listener.canonical(k)
    switch_hotkey.release(canonical_k)

while True:
    if is_redirecting:
        print("Input redirecting enabled.")
    else:
        print("Input redirecting disabled.")

    with keyboard.Listener(
            suppress=is_redirecting,
            on_press=keyboard_press_handler, # type: ignore
            on_release=keyboard_release_handler,
        ) as keyboard_listener:
        keyboard_listener.join()

# class InputController:
#     def __init__(self):
#         self.is_to_switch = False
#         self.is_redirecting = False

#         self.switch_key_combination = '<ctrl>+<alt>+s'
#         self.exit_key_combination = '<ctrl>+<alt>+q'
#         # self.exit_hotkey = keyboard.HotKey(keyboard.HotKey.parse(self.exit_key_combination), self.exit)
#         self.switch_hotkey = keyboard.HotKey(keyboard.HotKey.parse(self.switch_key_combination), self.switch)

#         self.show_function_message()
#         self.disable_redirect()

#     def switch(self):
#         if self.is_redirecting:
#             self.is_redirecting = False
#             self.disable_redirect()
#         else:
#             self.is_redirecting = True
#             self.enable_redirect()

#     def enable_redirect(self):
#         # with mouse.Listener(
#         #         # suppress=True,
#         #         on_move=self.mouse_move_handler,
#         #     ) as self.mouse_listener, \
#         #     keyboard.Listener(
#         #         suppress=True,
#         #         on_press=self.keyboard_press_handler,
#         #         on_release=self.keyboard_release_handler,
#         #     ) as self.keyboard_listener:
#         #     print("Input redirecting enabled.")
#         #     self.mouse_listener.join()
#         #     self.keyboard_listener.join()
#         print("Input redirecting enabled.")
#         with keyboard.Listener(
#                 suppress=True,
#                 on_press=self.keyboard_press_handler,
#                 on_release=self.keyboard_release_handler,
#             ) as self.keyboard_listener:
#             print(threading.active_count())
#             self.keyboard_listener.join()

#     def disable_redirect(self):
#         print("Input redirecting disabled.")
#         with keyboard.Listener(
#                 on_press=self.keyboard_press_handler,
#                 on_release=self.keyboard_release_handler,
#             ) as self.keyboard_listener:
#             print(threading.active_count())
#             self.keyboard_listener.join()

#     def keyboard_press_handler(self, k):
#         canonical_k = self.keyboard_listener.canonical(k)
#         self.switch_hotkey.press(canonical_k)
#         # if canonical_k.ctrl and canonical_k.alt and canonical_k.value == 's':
#         #     self.is_to_switch = False
#         #     self.switch()
#         #     return False
#         # self.exit_hotkey.press(canonical_k)

#     def keyboard_release_handler(self, k):
#         canonical_k = self.keyboard_listener.canonical(k)
#         self.switch_hotkey.release(canonical_k)
#         # return False
#         # self.exit_hotkey.release(canonical_k)

#     def mouse_move_handler(self, x, y):
#         print(x, y)
    
#     # def exit(self):
#         # if self.mouse_listener: self.mouse_listener.stop()
#         # if self.keyboard_listener: self.keyboard_listener.stop()

#     def show_function_message(self):
#         print(f'''
# Push {self.switch_key_combination} to enable/disable redirecting mouse and keyboard input.
# Push {self.exit_key_combination} to exit.''')

# if __name__ == '__main__':
#     InputController()

# --- --- --- --- --- ---

# from pynput import keyboard, mouse  # https://github.com/moses-palmer/pynput
# import threading

# class SupressInput:
#     def __init__(self):
#         self.keyboard_listener = None
#         self.key_combination = '<ctrl>+<alt>+s'
#         self.switch_hotkey = keyboard.HotKey(keyboard.HotKey.parse(self.key_combination), self.enable_all)

#     def switch(self):
#         pass

#     def disable_all(self):
#         print(self.keyboard_listener)
#         if self.keyboard_listener is not None:
#             self.keyboard_listener.stop()
#             self.keyboard_listener = None

#         with keyboard.Listener(
#                 suppress=True,
#                 on_press=self.keyboard_press_handler,
#                 on_release=self.keyboard_release_handler,
#             ) as self.keyboard_listener:
#             print(threading.active_count())
#             self.keyboard_listener.join()

#     def enable_all(self):
#         # self.mouse_listener.stop()
#         print(self.keyboard_listener)
#         if self.keyboard_listener is not None:
#             self.keyboard_listener.stop()
#             self.keyboard_listener = None

#         with keyboard.Listener(
#                 on_press=self.keyboard_press_handler,
#                 on_release=self.keyboard_release_handler,
#             ) as self.keyboard_listener:
#             print(threading.active_count())
#             self.keyboard_listener.join()

#     def keyboard_press_handler(self, k):
#         canonical_k = self.keyboard_listener.canonical(k)
#         print(canonical_k)
#         self.switch_hotkey.press(canonical_k)
#         # self.exit_hotkey.press(canonical_k)

#     def keyboard_release_handler(self, k):
#         canonical_k = self.keyboard_listener.canonical(k)
#         self.switch_hotkey.release(canonical_k)
#         # self.exit_hotkey.release(canonical_k)

#     def show_unblock_message(self):
#         print()
#         print(f'Push {self.key_combination} to unblock mouse and keyboard input...')


# def main():
#     supress_input = SupressInput()
#     supress_input.show_unblock_message()
#     supress_input.disable_all()


# if __name__ == '__main__':
#     main()