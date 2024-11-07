import time
import threading
import pynput
from typing import Callable
from utils import screen_size
from utils.logger import LOGGER, LogType

screen_width, screen_height = screen_size()
mouse_controller = pynput.mouse.Controller()
start_event = threading.Event()
pause_event = threading.Event()
close_event = threading.Event()
edge_portal_passing_event = threading.Event()

def portal_loop(interval_sec: float):
    if close_event.is_set():
        return
    pause_event.clear()
    while not pause_event.is_set():
        x, y = mouse_controller.position
        is_at_left_side = x <= 0
        is_at_right_side = x >= screen_width - 1
        is_at_top_side = y <= 0
        is_at_bottom_side = y >= screen_height - 1
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
        time.sleep(interval_sec)

def create_edge_portal():
    interval_sec = 1 / 120
    while not close_event.is_set():
        start_event.wait()
        portal_loop(interval_sec)
        start_event.clear()
    LOGGER.write(LogType.Info, "Edge portal closed.")

def edge_portal_thread_factory() -> tuple[
    Callable[[], None], Callable[[], None], Callable[[], None]
]:
    def start_edge_portal():
        start_event.set()
    def pause_edge_portal():
        pause_event.set()
    def close_edge_portal():
        close_event.set()
        pause_event.set()
        start_event.set()

    threading.Thread(target=create_edge_portal).start()
    return start_edge_portal, pause_edge_portal, close_edge_portal
