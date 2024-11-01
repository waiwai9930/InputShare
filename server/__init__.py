import socket
import subprocess
import sys
import time
import threading

from pathlib import Path
from adbutils import AdbClient, AdbDevice

from adb_controller import ADB_BIN_PATH
from scrcpy_client.clipboard_event import GetClipboardEventResponse
from utils import Clipboard, script_abs_path

SERVER_PORT = 1234

def push_server(device: AdbDevice):
    server_relative_path = "scrcpy-server"
    target_path = "/data/local/tmp/scrcpy-server-manual.jar"
    script_path = script_abs_path(__file__)
    server_binary_path = Path.joinpath(script_path, server_relative_path)
    device.push(str(server_binary_path), target_path)

def server_process_factory(adb_client: AdbClient):
    device = adb_client.device_list()[0]
    push_server(device)
    device.forward(f"tcp:{SERVER_PORT}", "localabstract:scrcpy")

    command = "CLASSPATH=/data/local/tmp/scrcpy-server-manual.jar app_process / com.genymobile.scrcpy.Server 2.7 tunnel_forward=true video=false audio=false control=true cleanup=false raw_stream=true max_size=1920"
    try:
        process = subprocess.Popen(
            [ADB_BIN_PATH, "shell", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        output = process.stdout.readline() # type: ignore
    except Exception as e:
        print("[Error] Failed to start subprocess: ", e)
        sys.exit(1)

    print(output)
    time.sleep(0.5)
    return process

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
        data = client_socket.recv(2048)
        if len(data) > 0:
            text = GetClipboardEventResponse.deserialize(data)
            if text is None:
                return True

            # prevent duplicated clipboard content
            current_clipboard_text = Clipboard.safe_paste()
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
