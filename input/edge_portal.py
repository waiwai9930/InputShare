import time
import threading
import pynput
from typing import Callable
from utils import screen_size

screen_width, screen_height = screen_size()
mouse_controller = pynput.mouse.Controller()
stop_event = threading.Event()
edge_portal_passing_event = threading.Event()

def create_edge_portal():
    while not stop_event.is_set():
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
        time.sleep(1 / 30)
    stop_event.clear()

def edge_portal_thread_factory() -> Callable[[], None]:
    def stop_edge_portal():
        stop_event.set()
    threading.Thread(target=create_edge_portal).start()
    return stop_edge_portal
