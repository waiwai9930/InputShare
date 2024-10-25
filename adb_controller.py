import re
import os
import subprocess
import adbutils
from pathlib import Path
from android import AKeyCode
from input.controller import Key, KeyCode

script_path = Path(__file__).resolve().parent
adb_relative_path = "adb-bin/adb.exe"
adb_bin_path = Path.joinpath(script_path, adb_relative_path)
os.environ["ADBUTILS_ADB_PATH"] = str(adb_bin_path)
ADB_BIN_PATH = str(adb_bin_path)

key_event_map = {
    KeyCode.from_char("0"): AKeyCode.AKEYCODE_0,
    KeyCode.from_char("1"): AKeyCode.AKEYCODE_1,
    KeyCode.from_char("2"): AKeyCode.AKEYCODE_2,
    KeyCode.from_char("3"): AKeyCode.AKEYCODE_3,
    KeyCode.from_char("4"): AKeyCode.AKEYCODE_4,
    KeyCode.from_char("5"): AKeyCode.AKEYCODE_5,
    KeyCode.from_char("6"): AKeyCode.AKEYCODE_6,
    KeyCode.from_char("7"): AKeyCode.AKEYCODE_7,
    KeyCode.from_char("8"): AKeyCode.AKEYCODE_8,
    KeyCode.from_char("9"): AKeyCode.AKEYCODE_9,

    KeyCode.from_char("a"): AKeyCode.AKEYCODE_A,
    KeyCode.from_char("b"): AKeyCode.AKEYCODE_B,
    KeyCode.from_char("c"): AKeyCode.AKEYCODE_C,
    KeyCode.from_char("d"): AKeyCode.AKEYCODE_D,
    KeyCode.from_char("e"): AKeyCode.AKEYCODE_E,
    KeyCode.from_char("f"): AKeyCode.AKEYCODE_F,
    KeyCode.from_char("g"): AKeyCode.AKEYCODE_G,
    KeyCode.from_char("h"): AKeyCode.AKEYCODE_H,
    KeyCode.from_char("i"): AKeyCode.AKEYCODE_I,
    KeyCode.from_char("j"): AKeyCode.AKEYCODE_J,
    KeyCode.from_char("k"): AKeyCode.AKEYCODE_K,
    KeyCode.from_char("l"): AKeyCode.AKEYCODE_L,
    KeyCode.from_char("m"): AKeyCode.AKEYCODE_M,
    KeyCode.from_char("n"): AKeyCode.AKEYCODE_N,
    KeyCode.from_char("o"): AKeyCode.AKEYCODE_O,
    KeyCode.from_char("p"): AKeyCode.AKEYCODE_P,
    KeyCode.from_char("q"): AKeyCode.AKEYCODE_Q,
    KeyCode.from_char("r"): AKeyCode.AKEYCODE_R,
    KeyCode.from_char("s"): AKeyCode.AKEYCODE_S,
    KeyCode.from_char("t"): AKeyCode.AKEYCODE_T,
    KeyCode.from_char("u"): AKeyCode.AKEYCODE_U,
    KeyCode.from_char("v"): AKeyCode.AKEYCODE_V,
    KeyCode.from_char("w"): AKeyCode.AKEYCODE_W,
    KeyCode.from_char("x"): AKeyCode.AKEYCODE_X,
    KeyCode.from_char("y"): AKeyCode.AKEYCODE_Y,
    KeyCode.from_char("z"): AKeyCode.AKEYCODE_Z,

    KeyCode.from_char(","): AKeyCode.AKEYCODE_COMMA,
    KeyCode.from_char("."): AKeyCode.AKEYCODE_PERIOD,
    KeyCode.from_char("`"): AKeyCode.AKEYCODE_GRAVE,
    KeyCode.from_char("-"): AKeyCode.AKEYCODE_MINUS,
    KeyCode.from_char("="): AKeyCode.AKEYCODE_EQUALS,
    KeyCode.from_char("["): AKeyCode.AKEYCODE_LEFT_BRACKET,
    KeyCode.from_char("]"): AKeyCode.AKEYCODE_RIGHT_BRACKET,
    KeyCode.from_char("\\"): AKeyCode.AKEYCODE_BACKSLASH,
    KeyCode.from_char(";"): AKeyCode.AKEYCODE_SEMICOLON,
    KeyCode.from_char("'"): AKeyCode.AKEYCODE_APOSTROPHE,
    KeyCode.from_char("/"): AKeyCode.AKEYCODE_SLASH,
    KeyCode.from_char("@"): AKeyCode.AKEYCODE_AT,

    Key.alt_l:   AKeyCode.AKEYCODE_ALT_LEFT,
    Key.alt_r:   AKeyCode.AKEYCODE_ALT_RIGHT,
    Key.shift_l: AKeyCode.AKEYCODE_SHIFT_LEFT,
    Key.shift_r: AKeyCode.AKEYCODE_SHIFT_RIGHT,

    KeyCode.from_vk(8 ): AKeyCode.AKEYCODE_DEL, # backspace
    KeyCode.from_vk(9 ): AKeyCode.AKEYCODE_TAB,
    KeyCode.from_vk(13): AKeyCode.AKEYCODE_ENTER,
    KeyCode.from_vk(20): AKeyCode.AKEYCODE_CAPS_LOCK,
    KeyCode.from_vk(32): AKeyCode.AKEYCODE_SPACE,
    KeyCode.from_vk(37): AKeyCode.AKEYCODE_DPAD_LEFT,
    KeyCode.from_vk(38): AKeyCode.AKEYCODE_DPAD_UP,
    KeyCode.from_vk(39): AKeyCode.AKEYCODE_DPAD_RIGHT,
    KeyCode.from_vk(40): AKeyCode.AKEYCODE_DPAD_DOWN,
    KeyCode.from_vk(45): AKeyCode.AKEYCODE_INSERT,
    KeyCode.from_vk(46): AKeyCode.AKEYCODE_FORWARD_DEL,
}

def try_connecting(addr: str, timeout: float=4.0) -> adbutils.AdbClient | None:
    client = adbutils.AdbClient()
    try:
        output = client.connect(addr, timeout)
        print("[ADB] ", output)
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
        exit(1)
    size = size_match.group(0).split('=')[1]
    width, height = map(int, size.split('x'))
    return (width, height)
