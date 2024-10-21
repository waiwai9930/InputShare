from input_controller import main_loop, Key, KeyCode
from adb_controller import try_connect, key_event_map

client = try_connect("192.168.119.84:33761")
device = client.device()

def keyboard_callback(k: Key | KeyCode, is_redirecting: bool):
    if not is_redirecting:
        return
    if k not in key_event_map:
        return
    # device.keyevent(key_event_map[k])

main_loop(keyboard_callback)
