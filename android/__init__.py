import array
import keycode
import keyevent
import msg_type
from binary import write32be

ControlMsgType = msg_type.ControlMsgType
AKeyCode = keycode.AKeyCode
AKeyEventAction = keyevent.AKeyEventAction

class InjectKeyCode:
    key_code: AKeyCode
    action: AKeyEventAction
    repeat: int = 1
    metastate: int = 0
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_INJECT_KEYCODE

    def __init__(self, key_code: AKeyCode, action: AKeyEventAction) -> None:
        self.key_code = key_code
        self.action = action

    def serialize(self) -> array.array:
        buf = array.array('B', [0] * 14)
        buf[0] = self.msg_type.value
        buf[1] = self.action.value
        write32be(buf, 2, self.key_code)
        write32be(buf, 6, self.repeat)
        write32be(buf, 10, self.metastate)
        return buf
