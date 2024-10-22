import socket
from subprocess import Popen
from android import InjectKeyCode, AKeyEventAction
from input_controller import Key, KeyCode, StopException
from adb_controller import key_event_map

def callback_context_wrapper(
    client_socket: socket.socket,
    server_process: Popen[str],
):
    def keyboard_press_callback(k: Key | KeyCode, is_redirecting: bool):
        if not is_redirecting:
            return
        if k not in key_event_map:
            return
        akey_code = key_event_map[k]
        inject_key_code = InjectKeyCode(akey_code, AKeyEventAction.AKEY_EVENT_ACTION_DOWN)
        try:
            data = inject_key_code.serialize()
            client_socket.sendall(data)
        except ConnectionAbortedError as e:
            print("[Error] Server error: ", e)
            client_socket.close()
            server_process.terminate()
            raise StopException
        except:
            print("[Error] Send message error.")

    def keyboard_release_callback(k: Key | KeyCode, is_redirecting: bool):
        if not is_redirecting:
            return
        if k not in key_event_map:
            return
        akey_code = key_event_map[k]
        inject_key_code = InjectKeyCode(akey_code, AKeyEventAction.AKEY_EVENT_ACTION_UP)
        try:
            data = inject_key_code.serialize()
            client_socket.sendall(data)
        except ConnectionAbortedError as e:
            print("[Error] Server error: ", e)
            client_socket.close()
            server_process.terminate()
            raise StopException
        except:
            print("[Error] Send message error.")
    
    return [
        keyboard_press_callback,
        keyboard_release_callback,
    ]