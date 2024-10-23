from enum import IntEnum

POINTER_ID_MOUSE = 0xffffffffffffffff
# SC_POINTER_ID_GENERIC_FINGER = -2
# Used for injecting an additional virtual pointer for pinch-to-zoom
# SC_POINTER_ID_VIRTUAL_FINGER = -3

class AMotionEventAction(IntEnum):
    """Motion event actions"""

    # Bit mask of the parts of the action code that are the action itself.
    AMOTION_EVENT_ACTION_MASK = 0xff
    
    # Bits in the action code that represent a pointer index, used with
    # AMOTION_EVENT_ACTION_POINTER_DOWN and AMOTION_EVENT_ACTION_POINTER_UP.
    # Shifting down by AMOTION_EVENT_ACTION_POINTER_INDEX_SHIFT provides the actual pointer
    # index where the data for the pointer going up or down can be found.
    AMOTION_EVENT_ACTION_POINTER_INDEX_MASK = 0xff00
    
    # A pressed gesture has started, the motion contains the initial starting location.
    AMOTION_EVENT_ACTION_DOWN = 0
    
    # A pressed gesture has finished, the motion contains the final release location
    # as well as any intermediate points since the last down or move event.
    AMOTION_EVENT_ACTION_UP = 1
    
    # A change has happened during a press gesture (between AMOTION_EVENT_ACTION_DOWN and
    # AMOTION_EVENT_ACTION_UP). The motion contains the most recent point, as well as
    # any intermediate points since the last down or move event.
    AMOTION_EVENT_ACTION_MOVE = 2
    
    # The current gesture has been aborted.
    # You will not receive any more points in it. You should treat this as
    # an up event, but not perform any action that you normally would.
    AMOTION_EVENT_ACTION_CANCEL = 3
    
    # A movement has happened outside of the normal bounds of the UI element.
    # This does not provide a full gesture, but only the initial location of the movement/touch.
    AMOTION_EVENT_ACTION_OUTSIDE = 4
    
    # A non-primary pointer has gone down.
    # The bits in AMOTION_EVENT_ACTION_POINTER_INDEX_MASK indicate which pointer changed.
    AMOTION_EVENT_ACTION_POINTER_DOWN = 5

    # A non-primary pointer has gone up.
    # The bits in AMOTION_EVENT_ACTION_POINTER_INDEX_MASK indicate which pointer changed.
    AMOTION_EVENT_ACTION_POINTER_UP = 6
    
    # A change happened but the pointer is not down (unlike AMOTION_EVENT_ACTION_MOVE).
    # The motion contains the most recent point, as well as any intermediate points since
    # the last hover move event.
    AMOTION_EVENT_ACTION_HOVER_MOVE = 7
    
    # The motion event contains relative vertical and/or horizontal scroll offsets.
    # Use getAxisValue to retrieve the information from AMOTION_EVENT_AXIS_VSCROLL
    # and AMOTION_EVENT_AXIS_HSCROLL.
    # The pointer may or may not be down when this event is dispatched.
    # This action is always delivered to the window under the pointer, which
    # may not be the window currently touched.
    AMOTION_EVENT_ACTION_SCROLL = 8
    
    # The pointer is not down but has entered the boundaries of a window or view.
    AMOTION_EVENT_ACTION_HOVER_ENTER = 9
    
    # The pointer is not down but has exited the boundaries of a window or view.
    AMOTION_EVENT_ACTION_HOVER_EXIT = 10
    
    # One or more buttons have been pressed.
    AMOTION_EVENT_ACTION_BUTTON_PRESS = 11
    
    # One or more buttons have been released.
    AMOTION_EVENT_ACTION_BUTTON_RELEASE = 12

class AMotionEventButtons(IntEnum):
    AMOTION_EVENT_BUTTON_NONE = 0

    ''' primary: left mouse button'''
    AMOTION_EVENT_BUTTON_PRIMARY = 1 << 0
    ''' secondary: right mouse button '''
    AMOTION_EVENT_BUTTON_SECONDARY = 1 << 1
    ''' tertiary: middle mouse button '''
    AMOTION_EVENT_BUTTON_TERTIARY = 1 << 2
    ''' back '''
    AMOTION_EVENT_BUTTON_BACK = 1 << 3
    ''' forward '''
    AMOTION_EVENT_BUTTON_FORWARD = 1 << 4
    AMOTION_EVENT_BUTTON_STYLUS_PRIMARY = 1 << 5
    AMOTION_EVENT_BUTTON_STYLUS_SECONDARY = 1 << 6

# --- --- --- --- --- ---

HID_ID_MOUSE = 2
HID_MOUSE_INPUT_SIZE = 4
HID_INPUT_DATA_MAX_SIZE = 15

HID_MOUSE_REPORT_DESC = bytes([
    # Usage Page (Generic Desktop)
    0x05, 0x01,
    # Usage (Mouse)
    0x09, 0x02,

    # Collection (Application)
    0xA1, 0x01,

    # Usage (Pointer)
    0x09, 0x01,

    # Collection (Physical)
    0xA1, 0x00,

    # Usage Page (Buttons)
    0x05, 0x09,

    # Usage Minimum (1)
    0x19, 0x01,
    # Usage Maximum (5)
    0x29, 0x05,
    # Logical Minimum (0)
    0x15, 0x00,
    # Logical Maximum (1)
    0x25, 0x01,
    # Report Count (5)
    0x95, 0x05,
    # Report Size (1)
    0x75, 0x01,
    # Input (Data, Variable, Absolute): 5 buttons bits
    0x81, 0x02,

    # Report Count (1)
    0x95, 0x01,
    # Report Size (3)
    0x75, 0x03,
    # Input (Constant): 3 bits padding
    0x81, 0x01,

    # Usage Page (Generic Desktop)
    0x05, 0x01,
    # Usage (X)
    0x09, 0x30,
    # Usage (Y)
    0x09, 0x31,
    # Usage (Wheel)
    0x09, 0x38,
    # Logical Minimum (-127)
    0x15, 0x81,
    # Logical Maximum (127)
    0x25, 0x7F,
    # Report Size (8)
    0x75, 0x08,
    # Report Count (3)
    0x95, 0x03,
    # Input (Data, Variable, Relative): 3 position bytes (X, Y, Wheel)
    0x81, 0x06,

    # End Collection
    0xC0,

    # End Collection
    0xC0,
])
