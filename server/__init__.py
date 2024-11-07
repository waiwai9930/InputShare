import socket
import subprocess
import sys
import time

from pathlib import Path
from adbutils import AdbClient, AdbDevice
from adb_controller import ADB_BIN_PATH
from utils import script_abs_path
from utils.logger import LOGGER, LogType

SERVER_PORT = 1234

def push_server(device: AdbDevice):
    server_relative_path = "scrcpy-server"
    target_path = "/data/local/tmp/scrcpy-server-manual.jar"
    script_path = script_abs_path(__file__)
    server_binary_path = Path.joinpath(script_path, server_relative_path)
    device.push(str(server_binary_path), target_path)

def server_process_factory():
    adb_client = AdbClient()
    device = adb_client.device_list()[0]
    push_server(device)
    device.forward(f"tcp:{SERVER_PORT}", "localabstract:scrcpy")

    command = "CLASSPATH=/data/local/tmp/scrcpy-server-manual.jar \
app_process / com.genymobile.scrcpy.Server 2.7 \
tunnel_forward=true video=false audio=false control=true \
cleanup=false raw_stream=true send_dummy_byte=true max_size=4096"
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
        LOGGER.write(LogType.Error, "Failed to start subprocess: " + str(e))
        sys.exit(1)

    LOGGER.write(LogType.Server, output)
    time.sleep(1)
    return process

class InvalidDummyByteException(Exception): pass

def try_connect_server(host: str, port: int=SERVER_PORT) -> socket.socket | Exception:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    client_socket.settimeout(3)
    try:
        dummy = client_socket.recv(4)
        client_socket.settimeout(None)
    except socket.timeout as e: return e
    except Exception as e: return e

    LOGGER.write(LogType.Info, "dummy byte: " + str(dummy))
    if len(dummy) == 1 and dummy[0] == 0x00:
        return client_socket
    return InvalidDummyByteException()
