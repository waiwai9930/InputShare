from enum import IntEnum

class AKeyEventAction(IntEnum):
    """
    Represents the action for an Android key event.
    """
    AKEY_EVENT_ACTION_DOWN = 0
    """
    The key has been pressed down.
    """

    AKEY_EVENT_ACTION_UP = 1
    """
    The key has been released.
    """

    AKEY_EVENT_ACTION_MULTIPLE = 2
    """
    Multiple duplicate key events have occurred in a row, or a complex string is being delivered.
    The repeat_count property of the key event contains the number of times the given key code should be executed.
    """
