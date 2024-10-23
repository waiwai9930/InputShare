import tkinter as tk
import threading
from typing import Callable

stop_event = threading.Event()

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
    root.wm_attributes("-topmost", True)

    label_window = tk.Toplevel(root)
    label_window.overrideredirect(True)
    label_window.geometry("+20+20")
    label_window.attributes('-alpha', 0.6)

    label1 = tk.Label(
        label_window,
        text="Use <Shift>+<Alt>+q to quit    ",
        bg="white",
        fg="black",
        font=("Arial", 18)
    )
    label2 = tk.Label(
        label_window,
        text="Use <Shift>+<Alt>+s to toggle",
        bg="white",
        fg="black",
        font=("Arial", 18)
    )
    label1.pack(padx=4, pady=4)
    label2.pack(padx=4, pady=4)

    label_window.deiconify()
    label_window.lift()
    root.update_idletasks()
    
    check_event(root)
    root.mainloop()

def mask_thread_factory() -> Callable[[], None]:
    def close_mask():
        stop_event.set()

    threading.Thread(target=open_mask_window).start()
    return close_mask
