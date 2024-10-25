import customtkinter as ctk

from adb_controller import try_connecting, try_pairing
from utils import is_valid_ipv4_addr, is_valid_ipv6_addr

def mount_pairing_view(tabview: ctk.CTkTabview):
    def pair_callback():
        nonlocal addr_textbox, pairing_code_textbox, error_label

        addr = addr_textbox.get("1.0", ctk.END).strip()
        pairing_code = pairing_code_textbox.get("1.0", ctk.END).strip()
        if not is_valid_ipv4_addr(addr) and not is_valid_ipv6_addr(addr):
            error_label.configure(text="Invalid pairing address!")
            return
        ret = try_pairing(addr, pairing_code)
        if ret == False:
            error_label.configure(text="Pairing Failed!")
            return
        tabview.set("Connecting")

    def need_not_pair_callback():
        nonlocal tabview
        tabview.set("Connecting")

    frame = tabview.tab("Pairing")
    prompt_label1 = ctk.CTkLabel(
        master=frame,
        text="Wireless debugging pairing IP address and port:",
        font=("Arial", 18),
    )
    prompt_label2 = ctk.CTkLabel(
        master=frame,
        text="Wireless debugging pairing code:",
        font=("Arial", 18),
    )
    error_label = ctk.CTkLabel(
        master=frame,
        text="",
        text_color="red",
        font=("Arial", 18),
    )
    addr_textbox = ctk.CTkTextbox(
        master=frame,
        height=1,
    )
    pairing_code_textbox = ctk.CTkTextbox(
        master=frame,
        height=1,
    )

    prompt_label1.grid(row=0, column=0, padx=20, pady=(10, 4), sticky="w")
    addr_textbox.grid(row=1, column=0, padx=20, sticky="we")
    prompt_label2.grid(row=2, column=0, padx=20, pady=(10, 4), sticky="w")
    pairing_code_textbox.grid(row=3, column=0, padx=20, sticky="we")
    error_label.grid(row=4, column=0, padx=20, pady=(10, 4), sticky="w")

    button_frame = ctk.CTkFrame(master=frame)
    button1 = ctk.CTkButton(
        master=button_frame,
        text="Paired? Skip >",
        font=("Arial", 16),
        command=need_not_pair_callback,
    )
    button2 = ctk.CTkButton(
        master=button_frame,
        text="Pair",
        font=("Arial", 16),
        command=pair_callback,
    )
    button_frame.grid(row=6, column=0, padx=20, pady=10, sticky="we")
    button1.pack(side=ctk.LEFT)
    button2.pack(side=ctk.RIGHT)

def mount_connecting_view(tabview: ctk.CTkTabview):
    def connect_callback():
        nonlocal addr_textbox, error_label

        adb_addr = addr_textbox.get("1.0", ctk.END).strip()
        if not is_valid_ipv4_addr(adb_addr) and not is_valid_ipv6_addr(adb_addr):
            error_label.configure(text="Invalid pairing address!")
            return
        ret = try_connecting(adb_addr)
        if ret is None:
            error_label.configure(text="Connecting failed!")
            return
        connecting_window.destroy()

    frame = tabview.tab("Connecting")
    prompt_label = ctk.CTkLabel(
        master=frame,
        text="Wireless debugging IP address and port:",
        font=("Arial", 18),
    )
    addr_textbox = ctk.CTkTextbox(
        master=frame,
        height=1,
    )
    error_label = ctk.CTkLabel(
        master=frame,
        text="",
        font=("Arial", 18),
        text_color="red",
    )
    blank_label = ctk.CTkLabel(
        master=frame,
        text="",
        font=("Arial", 18),
    )
    button = ctk.CTkButton(
        master=frame,
        text="Connect",
        font=("Arial", 16),
        command=connect_callback,
    )

    prompt_label.grid(row=0, column=0, padx=20, pady=(10, 4), sticky="w")
    addr_textbox.grid(row=1, column=0, padx=20, sticky="we")
    error_label.grid(row=2, column=0, padx=20, pady=(10, 4), sticky="w")
    blank_label.grid(row=3, column=0, padx=20, pady=(10, 4), sticky="w")
    button.grid(row=4, column=0, padx=20, pady=10, sticky="e")

def open_connecting_window():
    global connecting_window
    connecting_window = ctk.CTk()
    connecting_window.wm_title("InputShare Connection")
    connecting_window.geometry("500x320")
    connecting_window.resizable(width=False, height=False)

    tabview = ctk.CTkTabview(connecting_window)
    tabview.add("Pairing")
    tabview.add("Connecting")
    tabview.pack()

    mount_pairing_view(tabview)
    mount_connecting_view(tabview)

    connecting_window.protocol("WM_DELETE_WINDOW", lambda: exit(0))
    connecting_window.mainloop()
