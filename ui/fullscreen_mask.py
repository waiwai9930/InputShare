import customtkinter as ctk
import threading
from typing import Callable
from utils import screen_size

stop_event = threading.Event()
screen_width, screen_height = screen_size()

def window_created(root: ctk.CTk, toplevel: ctk.CTkToplevel):
    root.focus()
    toplevel.lift()

def check_event(root: ctk.CTk):
    if stop_event.is_set():
        stop_event.clear()
        root.quit()
    else:
        root.after(33, check_event, root)

def open_mask_window():
    root = ctk.CTk()
    root.wm_title("InputShare Mask")
    root.wm_attributes("-alpha", 0.01)
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-fullscreen", True)
    root.overrideredirect(True)
    root.geometry(f"{screen_width}x{screen_height}")

    label_toplevel = ctk.CTkToplevel(master=root)
    label_toplevel.geometry("+20+20")
    label_toplevel.wm_title("InputShare Prompt")
    label_toplevel.wm_attributes('-alpha', 0.6)
    label_toplevel.wm_attributes("-topmost", True)
    label_toplevel.overrideredirect(True)

    label1 = ctk.CTkLabel(
        master=label_toplevel,
        text="Use <Shift>+<Alt>+q to quit    ",
        font=("Arial", 18),
    )
    label2 = ctk.CTkLabel(
        master=label_toplevel,
        text="Use <Shift>+<Alt>+s to toggle",
        font=("Arial", 18),
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
