import time
import threading
import pynput

from typing import Callable
from server.reporter_receiver import DevicePosition, append_edge_toggling_callback
from utils import screen_size
from utils.config_manager import get_config
from utils.logger import LOGGER, LogType

EDGE_PORTAL_LOOP_INTERVAL_SEC = 1 / 250

screen_width, screen_height = screen_size()
mouse_controller = pynput.mouse.Controller()
pause_event = threading.Event()
close_event = threading.Event()
pause_edge_toggling_event = threading.Event()
edge_portal_passing_event = threading.Event()

config = get_config()

is_edge_toggling_enabled = config.edge_toggling
if is_edge_toggling_enabled:
    device_position     = config.device_position
    trigger_margin      = config.trigger_margin
    is_device_at_top    = device_position == DevicePosition.TOP
    is_device_at_right  = device_position == DevicePosition.RIGHT
    is_device_at_bottom = device_position == DevicePosition.BOTTOM
    is_device_at_left   = device_position == DevicePosition.LEFT

def pause_edge_toggling():
    LOGGER.write(LogType.Info, "Edge toggling paused.")
    pause_edge_toggling_event.set()
def resume_edge_toggling():
    LOGGER.write(LogType.Info, "Edge toggling resumed.")
    pause_edge_toggling_event.clear()

def create_edge_portal():
    from input.controller import schedule_toggle

    def move_mouse_to_edge():
        nonlocal x, y
        if pause_event.is_set() or pause_edge_toggling_event.is_set(): return
        if   is_device_at_right : mouse_controller.position = (screen_width - 2, y)
        elif is_device_at_left  : mouse_controller.position = (2, y)
        elif is_device_at_bottom: mouse_controller.position = (x, screen_height - 2)
    append_edge_toggling_callback(move_mouse_to_edge)

    while not close_event.is_set():
        x, y = mouse_controller.position
        is_at_left_side = x <= 0
        is_at_right_side = x >= screen_width - 1
        is_at_top_side = y <= 0
        is_at_bottom_side = y >= screen_height - 1

        if pause_event.is_set():
            if not is_edge_toggling_enabled or pause_edge_toggling_event.is_set():
                time.sleep(EDGE_PORTAL_LOOP_INTERVAL_SEC)
                continue
            is_y_at_target_range = trigger_margin < y < screen_height - trigger_margin
            if (is_device_at_right  and is_at_right_side and is_y_at_target_range) or\
               (is_device_at_left   and is_at_left_side  and is_y_at_target_range) or\
               (is_device_at_top    and is_at_top_side)    or\
               (is_device_at_bottom and is_at_bottom_side):
                schedule_toggle()
        else:
            if is_at_left_side or is_at_right_side or is_at_top_side or is_at_bottom_side:
                edge_portal_passing_event.set()
            if is_at_left_side:
                mouse_controller.move(screen_width - 1, 0)
            if is_at_right_side:
                mouse_controller.move(1 - screen_width, 0)
            if is_at_top_side:
                mouse_controller.move(0, screen_height - 1)
            if is_at_bottom_side:
                mouse_controller.move(0, 1 - screen_height)

        time.sleep(EDGE_PORTAL_LOOP_INTERVAL_SEC)
    LOGGER.write(LogType.Info, "Edge portal closed.")

def edge_portal_thread_factory() -> tuple[
    Callable[[], None], Callable[[], None], Callable[[], None]
]:
    def start_edge_portal():
        pause_event.clear()
    def pause_edge_portal():
        pause_event.set()
    def close_edge_portal():
        close_event.set()

    pause_event.set()
    threading.Thread(target=create_edge_portal, daemon=True).start()
    return start_edge_portal, pause_edge_portal, close_edge_portal
