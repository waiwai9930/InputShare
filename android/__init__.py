import struct
from .keycode import AKeyCode
from .keyevent import AKeyEventAction
from .msg_type import ControlMsgType
from binary import write32be

class InjectKeyCode:
    key_code: AKeyCode
    action: AKeyEventAction
    repeat: int = 0
    metastate: int = 0
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_INJECT_KEYCODE

    def __init__(self, key_code: AKeyCode, action: AKeyEventAction) -> None:
        self.key_code = key_code
        self.action = action

    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BBIII",
            self.msg_type.value,
            self.action.value,
            self.key_code.value,
            self.repeat,
            self.metastate,
        )
        return buf

        # buf = array.array('B', [0] * 14)
        # buf[0] = self.msg_type.value
        # buf[1] = self.action.value
        # write32be(buf, 2, self.key_code.value)
        # write32be(buf, 6, self.repeat)
        # write32be(buf, 10, self.metastate)
        return buf
