import socket, time
from android import InjectKeyCode, AKeyCode, AKeyEventAction
from input_controller import main_loop, Key, KeyCode
from adb_controller import try_connect, key_event_map

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 1234))

inject_key_code = InjectKeyCode(AKeyCode.AKEYCODE_A, AKeyEventAction.AKEY_EVENT_ACTION_DOWN) 
for i in range(10):
    data = inject_key_code.serialize()
    client_socket.send(data)
    time.sleep(1)

# --- --- --- --- --- ---

# def keyboard_callback(k: Key | KeyCode, is_redirecting: bool):
#     if not is_redirecting:
#         return
#     if k not in key_event_map:
#         return
#     # device.keyevent(key_event_map[k])

# main_loop(keyboard_callback)
