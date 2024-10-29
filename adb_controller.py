import re
import os
import sys
import subprocess
import adbutils
from pathlib import Path

script_path = Path(__file__).resolve().parent
adb_relative_path = "adb-bin/adb.exe"
adb_bin_path = Path.joinpath(script_path, adb_relative_path)
os.environ["ADBUTILS_ADB_PATH"] = str(adb_bin_path)
ADB_BIN_PATH = str(adb_bin_path)

def try_connecting(addr: str, timeout: float=4.0) -> adbutils.AdbClient | None:
    client = adbutils.AdbClient()
    try:
        output = client.connect(addr, timeout)
        assert len(client.device_list()) > 0
        print("[ADB]", output)
    except adbutils.AdbTimeout as e:
        print("[Error] Connect timeout: ", e)
        return None
    except Exception as e:
        print("[Error] Connect failed: ", e)
        return None
    return client

def try_pairing(addr: str, pairing_code: str) -> bool:
    command = f"{ADB_BIN_PATH} pair {addr} {pairing_code}"
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
        print("[Error] ADB failed to pair: ", e)
        return False

def get_display_size(adb_client: adbutils.AdbClient) -> tuple[int, int]:
    device = adb_client.device_list()[0]
    output = str(device.shell("dumpsys window displays"))

    size_pattern = re.compile(r'cur=\d+x\d+')
    size_match = size_pattern.search(output)

    if size_match is None:
        print("[Error] Get device size failed.")
        sys.exit(1)
    size = size_match.group(0).split('=')[1]
    width, height = map(int, size.split('x'))
    return (width, height)
