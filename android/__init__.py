import struct
from pynput import mouse

from utils import CLAMP
from .keycode import AKeyCode
from .keyevent import AKeyEventAction
from .coords import ScreenPosition
from .motion_event import HID_ID_MOUSE, HID_MOUSE_INPUT_SIZE, HID_MOUSE_REPORT_DESC, POINTER_ID_MOUSE, AMotionEventAction, AMotionEventButtons
from .msg_type import ControlMsgType

class InjectKeyCode:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_INJECT_KEYCODE
    key_code: AKeyCode
    action: AKeyEventAction
    repeat: int = 0
    metastate: int = 0

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

# --- --- --- --- --- ---

class InjectTouchEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_INJECT_TOUCH_EVENT
    action: AMotionEventAction
    action_button: AMotionEventButtons
    buttons: AMotionEventButtons
    pointer_id = POINTER_ID_MOUSE
    position: ScreenPosition
    pressure: int

    def __init__(
        self,
        position: ScreenPosition,
        action: AMotionEventAction,
        buttons: AMotionEventButtons = AMotionEventButtons.AMOTION_EVENT_BUTTON_SECONDARY,
        action_button: AMotionEventButtons = AMotionEventButtons.AMOTION_EVENT_BUTTON_NONE,
    ) -> None:
        is_up = action == AMotionEventAction.AMOTION_EVENT_ACTION_UP
        self.pressure = 0 if is_up else 1
        self.position = position

        self.action = action
        self.buttons = buttons
        self.action_button = action_button

    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BBQIIHHHII",
            self.msg_type.value, # 8
            self.action.value, # 8
            self.pointer_id, # 64
            self.position.point.x, # 32
            self.position.point.y, # 32
            self.position.size.width, # 16
            self.position.size.height, # 16
            self.pressure, # 16
            self.action_button, # 32
            self.buttons, # 32
        )
        return buf
def TouchMoveEvent(position: ScreenPosition) -> InjectTouchEvent:
    return InjectTouchEvent(
        position,
        AMotionEventAction.AMOTION_EVENT_ACTION_HOVER_MOVE,
    )
def TouchClickEvent(position: ScreenPosition, button: mouse.Button, pressed: bool) -> InjectTouchEvent:
    abutton = None
    match button:
        case mouse.Button.left:
            abutton = AMotionEventButtons.AMOTION_EVENT_BUTTON_PRIMARY
        case mouse.Button.right:
            abutton = AMotionEventButtons.AMOTION_EVENT_BUTTON_SECONDARY
        case _:
            abutton = AMotionEventButtons.AMOTION_EVENT_BUTTON_NONE
    
    action = None
    if pressed:
        action = AMotionEventAction.AMOTION_EVENT_ACTION_DOWN
    else:
        action = AMotionEventAction.AMOTION_EVENT_ACTION_UP

    return InjectTouchEvent(
        position,
        action,
        abutton,
        abutton,
    )

# --- --- --- --- --- ---

# struct {
#     uint16_t id;
#     const char *name; // pointer to static data
#     uint16_t report_desc_size;
#     const uint8_t *report_desc; // pointer to static data
# } uhid_create;
# struct {
#     uint16_t id;
#     uint16_t size;
#     uint8_t data[SC_HID_MAX_SIZE];
# } uhid_input;
class UHIDCreateEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_UHID_CREATE # 8
    id_: int = HID_ID_MOUSE # 16
    name = 0 # 8
    report_desc_size: int = len(HID_MOUSE_REPORT_DESC) # 16
    report_desc: bytes = HID_MOUSE_REPORT_DESC
    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BHBH",
            self.msg_type.value,
            self.id_,
            self.name,
            self.report_desc_size,
        )
        buf += self.report_desc
        return buf

class HIOInputEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_UHID_INPUT # 8
    id_: int = HID_ID_MOUSE # 16
    size: int = HID_MOUSE_INPUT_SIZE # 16
    data: bytes

    def __init__(self, data: list[int]) -> None:
        self.data = bytes(data)

    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BHH",
            self.msg_type.value,
            self.id_,
            self.size,
        )
        buf += self.data
        return buf

def MouseMoveEvent(x: int, y: int, buttons_state: AMotionEventButtons) -> HIOInputEvent:
    data = [0, 0, 0, 0]
    data[0] = buttons_state.value
    data[1] = CLAMP(x, -127, 127) % 256
    data[2] = CLAMP(y, -127, 127) % 256
    data[3] = 0
    input_event = HIOInputEvent(data)
    return input_event

def MouseClickEvent(buttons_state: AMotionEventButtons) -> HIOInputEvent:
    data = [0, 0, 0, 0]
    data[0] = buttons_state.value
    input_event = HIOInputEvent(data)
    return input_event
