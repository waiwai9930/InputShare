import re
import os
import sys
import subprocess
import adbutils
from pathlib import Path

from utils.logger import LogType, LOGGER

script_path = Path(__file__).resolve().parent
adb_relative_path = "adb-bin/adb.exe"
adb_bin_path = Path.joinpath(script_path, adb_relative_path)
__adb_client_instance: adbutils.AdbClient | None = None
os.environ["ADBUTILS_ADB_PATH"] = str(adb_bin_path)
ADB_BIN_PATH = str(adb_bin_path)
ADB_SERVER_PORT = 5038

def get_adb_client() -> adbutils.AdbClient:
    global __adb_client_instance
    if __adb_client_instance is None:
        # use non-default port to prevent conflict with Android Studio
        __adb_client_instance = adbutils.AdbClient(port=ADB_SERVER_PORT)
    return __adb_client_instance

def start_adb_server() -> bool:
    command = f"{ADB_BIN_PATH} -P {ADB_SERVER_PORT} start-server"
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        process.wait()
        return True
    except Exception as e:
        process.terminate()
        LOGGER.write(LogType.Error, "ADB server failed to start: " + str(e))
        return False

def try_pairing(addr: str, pairing_code: str, timeout=3.0) -> bool:
    command = f"{ADB_BIN_PATH} -P {ADB_SERVER_PORT} pair {addr} {pairing_code}"
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        process.wait(timeout)
        _, stderr = process.communicate()
        if stderr: raise Exception(stderr)
        return True
    except Exception as e:
        process.terminate()
        LOGGER.write(LogType.Error, "ADB failed to pair: " + str(e))
        return False

def try_connect_device(addr: str, timeout: float=3.0) -> adbutils.AdbClient | None:
    client = get_adb_client()
    try:
        output = client.connect(addr, timeout)
        assert len(client.device_list()) > 0
        LOGGER.write(LogType.Server, output)
    except adbutils.AdbTimeout as e:
        client.disconnect(addr)
        LOGGER.write(LogType.Error, "Connect timeout: " + str(e))
        return None
    except Exception as e:
        client.disconnect(addr)
        LOGGER.write(LogType.Error, "Connect failed: " + str(e))
        return None
    return client

def get_display_size(adb_client: adbutils.AdbClient) -> tuple[int, int]:
    device = adb_client.device_list()[0]
    output = str(device.shell("dumpsys window displays"))

    size_pattern = re.compile(r'cur=\d+x\d+')
    size_match = size_pattern.search(output)

    if size_match is None:
        LOGGER.write(LogType.Error, "Get device size failed.")
        sys.exit(1)
    size = size_match.group(0).split('=')[1]
    width, height = map(int, size.split('x'))
    return (width, height)
