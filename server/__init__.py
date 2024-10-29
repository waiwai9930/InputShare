import socket
import subprocess
import sys
import time
import threading

from pathlib import Path
from adbutils import AdbClient, AdbDevice
import pyperclip

from adb_controller import ADB_BIN_PATH
from scrcpy_client.clipboard_event import GetClipboardEventResponse

SERVER_PORT = 1234

def push_server(device: AdbDevice):
    server_relative_path = "scrcpy-server"
    target_path = "/data/local/tmp/scrcpy-server-manual.jar"
    script_path = Path(__file__).resolve().parent
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
    except Exception as e:
        print("[Error] Failed to start subprocess: ", e)
        sys.exit(1)

    output = process.stdout.readline() # type: ignore
    print(output)
    time.sleep(0.5)

    return process

def server_receiver_factory(client_socket: socket.socket) -> threading.Thread:
    def receiver(client_socket: socket.socket):
        def data_recv() -> bool:
            data = client_socket.recv(2048)
            if len(data) > 0:
                text = GetClipboardEventResponse.deserialize(data)
                if text != pyperclip.paste():
                    # prevent duplicated clipboard content
                    pyperclip.copy(text)
                return True
            else:
                print("[Server] Server closed the connection")
                return False

        while True:
            try:
                if not data_recv():
                    break
            except ConnectionAbortedError:
                print("[Error] Connection aborted")
            except ConnectionResetError:
                print("[Error] Connection reset")
                break
            except Exception as e:
                print("[Error] Getting clipboard data error: ", e)
                break
        print("[Server] Receiver stopped")

    thread = threading.Thread(target=receiver, args=[client_socket])
    thread.start()
    return thread
