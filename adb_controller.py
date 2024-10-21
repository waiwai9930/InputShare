import adbutils
from input_controller import Key, KeyCode

def try_connect(addr: str, timeout: float=4.0) -> adbutils.AdbClient:
    client = adbutils.AdbClient()
    try:
        output = client.connect(addr, timeout)
        print(output)
    except adbutils.AdbTimeout as e:
        print("Connect failed: ", e)
        exit()
    return client

key_event_map = {
    KeyCode.from_char("a"): 29, # A
    KeyCode.from_char("b"): 30, # B
    KeyCode.from_char("c"): 31, # C
    KeyCode.from_char("d"): 32, # D
    KeyCode.from_char("e"): 33, # E
    KeyCode.from_char("f"): 34, # F
    KeyCode.from_char("g"): 35, # G
    KeyCode.from_char("h"): 36, # H
    KeyCode.from_char("i"): 37, # I
    KeyCode.from_char("j"): 38, # J
    KeyCode.from_char("k"): 39, # K
    KeyCode.from_char("l"): 40, # L
    KeyCode.from_char("m"): 41, # M
    KeyCode.from_char("n"): 42, # N
    KeyCode.from_char("o"): 43, # O
    KeyCode.from_char("p"): 44, # P
    KeyCode.from_char("q"): 45, # Q
    KeyCode.from_char("r"): 46, # R
    KeyCode.from_char("s"): 47, # S
    KeyCode.from_char("t"): 48, # T
    KeyCode.from_char("u"): 49, # U
    KeyCode.from_char("v"): 50, # V
    KeyCode.from_char("w"): 51, # W
    KeyCode.from_char("x"): 52, # X
    KeyCode.from_char("y"): 53, # Y
    KeyCode.from_char("z"): 54, # Z

    Key.alt_l: 57,
    Key.alt_l: 58,
    Key.shift_l: 59,
    Key.shift_r: 60,
    Key.tab: 61,
    KeyCode.from_vk(32): 62, # space
    KeyCode.from_vk(13): 66, # enter
    KeyCode.from_vk(8 ): 67, # backspace
    # KeyCode.from_vk(Key.enter): 66,
}
