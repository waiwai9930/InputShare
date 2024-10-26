import customtkinter as ctk

from adb_controller import try_connecting, try_pairing
from utils import i18n, is_valid_ipv4_addr, is_valid_ipv6_addr

def mount_pairing_view(tabview: ctk.CTkTabview):
    def pair_callback():
        nonlocal addr_textbox, pairing_code_textbox, error_label

        addr = addr_textbox.get("1.0", ctk.END).strip()
        pairing_code = pairing_code_textbox.get("1.0", ctk.END).strip()
        if not is_valid_ipv4_addr(addr) and not is_valid_ipv6_addr(addr):
            error_label.configure(text=i18n(["Invalid pairing address!", "配对地址无效！"]))
            return
        ret = try_pairing(addr, pairing_code)
        if ret == False:
            error_label.configure(text=i18n(["Pairing Failed!", "配对失败！"]))
            return
        tabview.set(i18n(["Connecting", "连接"]))

    def need_not_pairing_callback():
        nonlocal tabview
        tabview.set(i18n(["Connecting", "连接"]))

    frame = tabview.tab(i18n(["Pairing", "配对"]))
    prompt_label1 = ctk.CTkLabel(
        master=frame,
        text=i18n(["Wireless debugging pairing IP address and port:", "无线调试配对 IP 地址和端口：                "]),
        font=larger_font,
    )
    prompt_label2 = ctk.CTkLabel(
        master=frame,
        text=i18n(["Wireless debugging pairing code:", "无线调试配对码："]),
        font=larger_font,
    )
    error_label = ctk.CTkLabel(
        master=frame,
        text="",
        text_color="red",
        font=larger_font,
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
        text=i18n(["Paired? Skip >", "已配对？跳过"]),
        font=normal_font,
        command=need_not_pairing_callback,
    )
    button2 = ctk.CTkButton(
        master=button_frame,
        text=i18n(["Pair", "配对"]),
        font=normal_font,
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
            error_label.configure(text=i18n(["Invalid connecting address!", "配对地址无效！"]))
            return
        ret = try_connecting(adb_addr)
        if ret is None:
            error_label.configure(text=i18n(["Connecting failed!", "连接失败！"]))
            return
        connecting_window.destroy()
    
    def need_not_connection_callback():
        connecting_window.destroy()

    frame = tabview.tab(i18n(["Connecting", "连接"]))
    prompt_label = ctk.CTkLabel(
        master=frame,
        text=i18n(["Wireless debugging IP address and port:    ", "无线调试 IP 地址和端口：                       "]),
        font=larger_font,
    )
    addr_textbox = ctk.CTkTextbox(
        master=frame,
        height=1,
    )
    error_label = ctk.CTkLabel(
        master=frame,
        text="",
        font=larger_font,
        text_color="red",
    )
    blank_label = ctk.CTkLabel(
        master=frame,
        text="",
        font=larger_font,
    )

    prompt_label.grid(row=0, column=0, padx=20, pady=(10, 4), sticky="w")
    addr_textbox.grid(row=1, column=0, padx=20, sticky="we")
    error_label.grid(row=2, column=0, padx=20, pady=(10, 4), sticky="w")
    blank_label.grid(row=3, column=0, padx=20, pady=(10, 4), sticky="w")

    button_frame = ctk.CTkFrame(master=frame)
    button1 = ctk.CTkButton(
        master=button_frame,
        text=i18n(["Wired? Skip >", "有线连接？跳过"]),
        font=normal_font,
        command=need_not_connection_callback,
    )
    button2 = ctk.CTkButton(
        master=button_frame,
        text=i18n(["Connect", "连接"]),
        font=normal_font,
        command=connect_callback,
    )
    button_frame.grid(row=4, column=0, padx=20, pady=10, sticky="we")
    button1.pack(side=ctk.LEFT)
    button2.pack(side=ctk.RIGHT)

def open_connecting_window():
    global connecting_window, normal_font, larger_font
    connecting_window = ctk.CTk()
    connecting_window.wm_title(i18n(["InputShare Connection", "输入流转 —— 连接"]))
    connecting_window.geometry("500x320")
    connecting_window.resizable(width=False, height=False)

    normal_font = i18n([
    ctk.CTkFont(family="Arial", size=16),
    ctk.CTkFont(family="Microsoft YaHei", size=16),
    ])
    larger_font = i18n([
        ctk.CTkFont(family="Arial", size=18),
        ctk.CTkFont(family="Microsoft YaHei", size=18),
    ])

    tabview = ctk.CTkTabview(master=connecting_window)
    tabview.add(i18n(["Pairing", "配对"]))
    tabview.add(i18n(["Connecting", "连接"]))
    tabview.pack()

    mount_pairing_view(tabview)
    mount_connecting_view(tabview)

    connecting_window.protocol("WM_DELETE_WINDOW", lambda: exit(0))
    connecting_window.mainloop()
