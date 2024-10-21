from enum import Enum, auto

class ControlMsgType(Enum):
    """
    Represents the types of control messages.
    """
    MSG_TYPE_INJECT_KEYCODE = 0
    MSG_TYPE_INJECT_TEXT = auto()
    MSG_TYPE_INJECT_TOUCH_EVENT = auto()
    MSG_TYPE_INJECT_SCROLL_EVENT = auto()
    MSG_TYPE_BACK_OR_SCREEN_ON = auto()
    MSG_TYPE_EXPAND_NOTIFICATION_PANEL = auto()
    MSG_TYPE_EXPAND_SETTINGS_PANEL = auto()
    MSG_TYPE_COLLAPSE_PANELS = auto()
    MSG_TYPE_GET_CLIPBOARD = auto()
    MSG_TYPE_SET_CLIPBOARD = auto()
    MSG_TYPE_SET_SCREEN_POWER_MODE = auto()
    MSG_TYPE_ROTATE_DEVICE = auto()
    MSG_TYPE_UHID_CREATE = auto()
    MSG_TYPE_UHID_INPUT = auto()
    MSG_TYPE_UHID_DESTROY = auto()
    MSG_TYPE_OPEN_HARD_KEYBOARD_SETTINGS = auto()
