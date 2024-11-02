import socket
import threading

from scrcpy_client.clipboard_event import GetClipboardEventResponse
from utils import Clipboard

class ReceivedClipboardText:
    lock = threading.Lock()
    text: str | None = None
    @staticmethod
    def read():
        with ReceivedClipboardText.lock:
            current_text = ReceivedClipboardText.text
        return current_text
    @staticmethod
    def write(new_text: str):
        with ReceivedClipboardText.lock:
            ReceivedClipboardText.text = new_text

def server_receiver_factory(client_socket: socket.socket) -> threading.Thread:
    def data_recv(client_socket: socket.socket) -> bool:
        data = client_socket.recv(4096)
        if len(data) > 0:
            text = GetClipboardEventResponse.deserialize(data)
            if text is None: return True

            # prevent duplicated clipboard content
            current_clipboard_text = Clipboard.safe_paste()
            if not Clipboard.sync_clipboard: return True
            if current_clipboard_text is not None and text != current_clipboard_text:
                Clipboard.safe_copy(text)
                ReceivedClipboardText.write(text)
            return True
        else:
            print("[Server] Server closed the connection")
            return False

    def receiver(client_socket: socket.socket):
        while True:
            try:
                if not data_recv(client_socket):
                    break
            except (ConnectionAbortedError, ConnectionResetError) as e:
                print("[Error] Connection error: ", e)
                break
            except Exception as e:
                print("[Error] Getting clipboard data error: ", e)
                break
        print("[Server] Receiver stopped")

    thread = threading.Thread(target=receiver, args=[client_socket])
    thread.start()
    return thread