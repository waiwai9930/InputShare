import threading
import time
import clipman

from typing import Callable

clipman.init()

def clipboard_monitor_factory(callback: Callable[[str], None]) -> tuple[
    Callable[[], None], Callable[[], None]
]:
    pause_event = threading.Event()
    def clipboard_monitor():
        last_text = clipman.paste()
        while not pause_event.is_set():
            current_text = clipman.paste()
            if current_text != last_text:
                callback(current_text)
                last_text = current_text
            time.sleep(1 / 10)
        pause_event.clear()

    def start_monitor():
        threading.Thread(target=clipboard_monitor).start()
    def pause_monitor():
        pause_event.set()
    return start_monitor, pause_monitor
