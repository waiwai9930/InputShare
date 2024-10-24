import tkinter as tk
import threading
from typing import Callable

stop_event = threading.Event()

def window_created(root: tk.Tk, toplevel: tk.Toplevel):
    root.focus()
    toplevel.lift()

def check_event(root: tk.Tk):
    if stop_event.is_set():
        stop_event.clear()
        root.quit()
    else:
        root.after(33, check_event, root)

def open_mask_window():
    root = tk.Tk()
    root.attributes('-alpha', 0.01)
    root.attributes('-fullscreen', True)
    root.wm_title("ADB Control Mask")
    root.wm_attributes("-topmost", True)

    label_toplevel = tk.Toplevel(root)
    label_toplevel.overrideredirect(True)
    label_toplevel.geometry("+20+20")
    label_toplevel.attributes('-alpha', 0.6)
    label_toplevel.wm_attributes("-topmost", True)

    label1 = tk.Label(
        label_toplevel,
        text="Use <Shift>+<Alt>+q to quit    ",
        bg="white",
        fg="black",
        font=("Arial", 18)
    )
    label2 = tk.Label(
        label_toplevel,
        text="Use <Shift>+<Alt>+s to toggle",
        bg="white",
        fg="black",
        font=("Arial", 18)
    )
    label1.pack(padx=4, pady=4)
    label2.pack(padx=4, pady=4)
    
    check_event(root)
    root.after(0, window_created, root, label_toplevel)
    root.mainloop()

def mask_thread_factory() -> Callable[[], None]:
    def close_mask():
        stop_event.set()

    threading.Thread(target=open_mask_window).start()
    return close_mask
