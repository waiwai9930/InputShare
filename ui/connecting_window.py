import sys
import customtkinter as ctk

from adb_controller import try_connect_device, try_pairing
from ui import ICON_ICO_PATH
from utils import get_ip_from_addr_str, is_valid_ipv4_addr, is_valid_ipv6_addr, script_abs_path
from utils.i18n import I18N

def mount_pairing_view(tabview: ctk.CTkTabview, connecting_addr_entry: ctk.CTkEntry):
    def pair_callback():
        nonlocal addr_entry, pairing_code_entry, error_label

        addr = addr_entry.get().strip()
        pairing_code = pairing_code_entry.get().strip()
        if not is_valid_ipv4_addr(addr) and not is_valid_ipv6_addr(addr):
            error_label.configure(text=I18N(["Invalid pairing address!", "配对地址无效！"]))
            return
        ret = try_pairing(addr, pairing_code)
        if ret == False:
            error_label.configure(text=I18N(["Pairing Failed!", "配对失败！"]))
            return
        device_ip = get_ip_from_addr_str(addr)
        connecting_addr_entry.insert(0, device_ip)
        tabview.set(I18N(["Connecting", "连接"]))

    def need_not_pairing_callback():
        nonlocal tabview
        tabview.set(I18N(["Connecting", "连接"]))
    
    def validate_entry(text: str):
        return text.isdigit() and len(text) <= 6

    frame = tabview.tab(I18N(["Pairing", "配对"]))
    vcmd = (tabview.register(validate_entry), "%P")
    normal_font = I18N([ctk.CTkFont(family="Arial", size=16), ctk.CTkFont(family="Microsoft YaHei", size=16)])
    larger_font = I18N([ctk.CTkFont(family="Arial", size=18), ctk.CTkFont(family="Microsoft YaHei", size=18)])

    prompt_label1 = ctk.CTkLabel(
        master=frame,
        text=I18N(["Wireless debugging pairing IP address and port:", "无线调试配对 IP 地址和端口：                "]),
        font=larger_font,
    )
    prompt_label2 = ctk.CTkLabel(
        master=frame,
        text=I18N(["Wireless debugging pairing code:", "无线调试配对码："]),
        font=larger_font,
    )
    error_label = ctk.CTkLabel(
        master=frame,
        text="",
        text_color="red",
        font=larger_font,
    )
    addr_entry = ctk.CTkEntry(
        master=frame,
        font=normal_font,
    )
    pairing_code_entry = ctk.CTkEntry(
        master=frame,
        font=normal_font,
        validate="key",
        validatecommand=vcmd,
    )

    prompt_label1.grid(row=0, column=0, padx=20, pady=(10, 4), sticky="w")
    addr_entry.grid(row=1, column=0, padx=20, sticky="we")
    prompt_label2.grid(row=2, column=0, padx=20, pady=(10, 4), sticky="w")
    pairing_code_entry.grid(row=3, column=0, padx=20, sticky="we")
    error_label.grid(row=4, column=0, padx=20, pady=(10, 4), sticky="w")

    button_frame = ctk.CTkFrame(master=frame)
    button1 = ctk.CTkButton(
        master=button_frame,
        text=I18N(["Paired? Skip >", "已配对？跳过"]),
        font=normal_font,
        command=need_not_pairing_callback,
    )
    button2 = ctk.CTkButton(
        master=button_frame,
        text=I18N(["Pair", "配对"]),
        font=normal_font,
        command=pair_callback,
    )
    button_frame.grid(row=6, column=0, padx=20, pady=10, sticky="we")
    button1.pack(side=ctk.LEFT)
    button2.pack(side=ctk.RIGHT)

def mount_connecting_view(tabview: ctk.CTkTabview) -> ctk.CTkEntry:
    def connect_callback():
        nonlocal addr_entry, error_label

        adb_addr = addr_entry.get().strip()
        if not is_valid_ipv4_addr(adb_addr) and not is_valid_ipv6_addr(adb_addr):
            error_label.configure(text=I18N(["Invalid connecting address!", "配对地址无效！"]))
            return
        ret = try_connect_device(adb_addr)
        if ret is None:
            error_label.configure(text=I18N(["Connecting failed!", "连接失败！"]))
            return
        connecting_window.destroy()
    
    def need_not_connection_callback():
        connecting_window.destroy()

    normal_font = I18N([ctk.CTkFont(family="Arial", size=16), ctk.CTkFont(family="Microsoft YaHei", size=16)])
    larger_font = I18N([ctk.CTkFont(family="Arial", size=18), ctk.CTkFont(family="Microsoft YaHei", size=18)])

    frame = tabview.tab(I18N(["Connecting", "连接"]))
    prompt_label = ctk.CTkLabel(
        master=frame,
        text=I18N(["Wireless debugging IP address and port:    ", "无线调试 IP 地址和端口：                       "]),
        font=larger_font,
    )
    addr_entry = ctk.CTkEntry(
        master=frame,
        font=normal_font,
    )
    error_label = ctk.CTkLabel(
        master=frame,
        text="",
        font=larger_font,
        text_color="red",
    )
    blank_label1 = ctk.CTkLabel(master=frame, text="", font=larger_font)
    blank_label2 = ctk.CTkLabel(master=frame, text="", font=larger_font)

    prompt_label.grid(row=0, column=0, padx=20, pady=(10, 4), sticky="w")
    addr_entry.grid(row=1, column=0, padx=20, sticky="we")
    error_label.grid(row=2, column=0, padx=20, pady=(10, 4), sticky="w")
    blank_label1.grid(row=3, column=0, padx=20, pady=2, sticky="w")
    blank_label2.grid(row=4, column=0, padx=20, pady=2, sticky="w")

    button_frame = ctk.CTkFrame(master=frame)
    button1 = ctk.CTkButton(
        master=button_frame,
        text=I18N(["Wired? Skip >", "有线连接？跳过"]),
        font=normal_font,
        command=need_not_connection_callback,
    )
    button2 = ctk.CTkButton(
        master=button_frame,
        text=I18N(["Connect", "连接"]),
        font=normal_font,
        command=connect_callback,
    )
    button_frame.grid(row=5, column=0, padx=20, pady=10, sticky="we")
    button1.pack(side=ctk.LEFT)
    button2.pack(side=ctk.RIGHT)
    # expose the addr_textbox to mainwindow
    return addr_entry

def open_connecting_window():
    global connecting_window #, normal_font, larger_font
    def delete_window_callback():
        connecting_window.destroy()
        sys.exit(0)

    connecting_window = ctk.CTk()
    connecting_window.iconbitmap(ICON_ICO_PATH)
    connecting_window.wm_title(I18N(["InputShare Connection", "输入流转 —— 连接"]))
    connecting_window.geometry("500x320")
    connecting_window.resizable(width=False, height=False)

    tabview = ctk.CTkTabview(master=connecting_window)
    tabview.add(I18N(["Pairing", "配对"]))
    tabview.add(I18N(["Connecting", "连接"]))
    tabview.pack()

    connecting_addr_textbox = mount_connecting_view(tabview)
    mount_pairing_view(tabview, connecting_addr_textbox)

    connecting_window.protocol("WM_DELETE_WINDOW", delete_window_callback)
    connecting_window.mainloop()
