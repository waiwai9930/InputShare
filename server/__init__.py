import subprocess
import sys
import time

from pathlib import Path
from adbutils import AdbClient, AdbDevice

from adb_controller import ADB_BIN_PATH
from utils import script_abs_path

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
