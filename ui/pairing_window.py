import customtkinter as ctk

from adb_controller import try_pairing
from utils import is_valid_ipv4_addr, is_valid_ipv6_addr

def pair_callback():
    addr = addr_textbox.get("1.0", ctk.END)
    pairing_code = pairing_code_textbox.get("1.0", ctk.END)
    if not is_valid_ipv4_addr(addr) and not is_valid_ipv6_addr(addr):
        error_label.configure(text="Invalid pairing address!")
        return
    ret = try_pairing(addr, pairing_code)
    if ret == False:
        error_label.configure(text="Pairing Failed!")
        return
    connect_window.quit()

def need_not_pair_callback():
    pass

def on_closing():
    exit(0)

def open_pairing_window():
    global connect_window, addr_textbox, pairing_code_textbox, error_label
    root = ctk.CTk()
    root.wm_title("ADB Pairer")
    connect_window = root

    prompt_label1 = ctk.CTkLabel(
        master=root,
        text="Please input your pairing address here:",
        font=("Arial", 18),
    )
    prompt_label2 = ctk.CTkLabel(
        master=root,
        text="Please input your pairing code here:",
        font=("Arial", 18),
    )
    error_label = ctk.CTkLabel(
        master=root,
        text="",
        text_color="red",
        font=("Arial", 18),
    )
    addr_textbox = ctk.CTkTextbox(
        master=root,
        height=1,
    )
    pairing_code_textbox = ctk.CTkTextbox(
        master=root,
        height=1,
    )

    prompt_label1.grid(row=0, column=0, padx=20, pady=(10, 4), sticky="w")
    addr_textbox.grid(row=1, column=0, padx=20, sticky="we")
    prompt_label2.grid(row=2, column=0, padx=20, pady=(10, 4), sticky="w")
    pairing_code_textbox.grid(row=3, column=0, padx=20, sticky="we")
    error_label.grid(row=4, column=0, padx=20, pady=(10, 4), sticky="w")

    button_frame = ctk.CTkFrame(
        master=root,
    )
    button1 = ctk.CTkButton(
        master=button_frame,
        text="Paired? Skip >",
        command=need_not_pair_callback,
    )
    button2 = ctk.CTkButton(
        master=button_frame,
        text="Pair",
        command=pair_callback,
    )
    button_frame.grid(row=6, column=0, padx=20, pady=10, sticky="we")
    button1.pack(side=ctk.LEFT)
    button2.pack(side=ctk.RIGHT)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
