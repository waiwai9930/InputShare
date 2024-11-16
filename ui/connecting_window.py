import sys
import threading
import adbutils
import customtkinter as ctk

from dataclasses import dataclass
from queue import Queue

from adb_controller import try_connect_device, try_pairing
from ui import ICON_ICO_PATH
from utils.config_manager import CONFIG
from utils.logger import LOGGER, LogType, unreachable
from utils.scan_port import scan_port
from utils.ip_check import get_ip_from_ip_port, is_valid_ip, is_valid_ip_port
from utils.i18n import I18N

def mount_pairing_view(tabview: ctk.CTkTabview, connecting_addr_entry: ctk.CTkEntry):
    def pair_callback():
        global connecting_window
        nonlocal addr_entry, pairing_code_entry, error_label
        error_label.configure(text="")

        addr = addr_entry.get().strip()
        pairing_code = pairing_code_entry.get().strip()
        if not is_valid_ip_port(addr):
            error_label.configure(text=I18N(["Invalid pairing address!", "配对地址无效！"]))
            return
        ret = try_pairing(addr, pairing_code)
        if not ret:
            error_label.configure(text=I18N(["Pairing Failed!", "配对失败！"]))
            return
        device_ip = get_ip_from_ip_port(addr)
        connecting_addr_entry.delete(0, ctk.END)
        connecting_addr_entry.insert(0, device_ip)
        tabview.set(I18N(["Connecting", "连接"]))
        connecting_window.deiconify()
        connecting_window.focus()

    def need_not_pairing_callback():
        nonlocal tabview
        tabview.set(I18N(["Connecting", "连接"]))
    
    def validate_entry(text: str):
        text_len = len(text)
        return text_len == 0 or\
            text.isdigit() and\
            text_len <= 6

    frame = tabview.tab(I18N(["Pairing", "配对"]))
    vcmd = (tabview.register(validate_entry), "%P")
    normal_font = I18N([ctk.CTkFont(family="Arial", size=16), ctk.CTkFont(family="Microsoft YaHei", size=16)])
    larger_font = I18N([ctk.CTkFont(family="Arial", size=18), ctk.CTkFont(family="Microsoft YaHei", size=18)])

    prompt_label1 = ctk.CTkLabel(
        master=frame, font=larger_font,
        text=I18N(["Wireless debugging pairing IP address and port:", "无线调试配对 IP 地址和端口：                "]),
    )
    prompt_label2 = ctk.CTkLabel(
        master=frame, font=larger_font,
        text=I18N(["Wireless debugging pairing code:", "无线调试配对码："]),
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
    @dataclass
    class ProcessOk: ip_port_str: str
    @dataclass
    class ProcessError: msg: str

    process_data_queue: Queue[ProcessOk | ProcessError] = Queue()

    def scan_and_connect(addr: str):
        nonlocal process_data_queue
        valid_ip = is_valid_ip(addr)
        valid_ip_port = is_valid_ip_port(addr)
        if not valid_ip and not valid_ip_port:
            process_data_queue.put(
                ProcessError(I18N(["Invalid connecting address!", "连接地址无效！"])))
            return
        # format address string into ip_part only string
        ip_addr_part = addr if valid_ip else get_ip_from_ip_port(addr)

        target_ports = scan_port(ip_addr_part)
        for port in target_ports:
            connect_addr = f"{ip_addr_part}:{port}"
            ret = try_connect_device(connect_addr)
            if ret is not None:
                process_data_queue.put(ProcessOk(connect_addr))
                return
        LOGGER.write(LogType.Error, "Scanned ports: " + str(target_ports))
        process_data_queue.put(
            ProcessError(I18N(["Port scanning failed, please check the IP address.", "扫描端口失败，请检查 IP 地址是否正确。"])))

    def direct_connect(addr: str):
        nonlocal process_data_queue
        if not is_valid_ip_port(addr):
            process_data_queue.put(
                ProcessError(I18N(["Invalid connecting address!", "连接地址无效！"])))
            return
        ret = try_connect_device(addr)
        if ret is not None:
            process_data_queue.put(ProcessOk(addr))
            return
        process_data_queue.put(
            ProcessError(I18N(["Connecting failed, please retry.", "连接失败，请重试。"])))

    def process_ip_port(addr: str, to_scan_port: bool):
        if to_scan_port: scan_and_connect(addr)
        else: direct_connect(addr)

    def process_callback():
        global connecting_window
        nonlocal process_data_queue, auto_scan_port,\
                 error_label, waiting_label
        if process_data_queue.empty():
            # wait for ip_port data processed
            connecting_window.after(func=process_callback, ms=100)
            return

        result = process_data_queue.get()
        if type(result) == ProcessError:
            error_label.configure(text=result.msg)
            waiting_label.configure(text="")
            connecting_window.configure(cursor="arrow")
            enable_widgets()
        elif type(result) == ProcessOk:
            CONFIG.config.scan_port = bool(auto_scan_port.get())
            CONFIG.config.device_ip1 = get_ip_from_ip_port(result.ip_port_str)
            connecting_window.destroy()
        else: unreachable("Connection result: " + str(result))

    def enable_widgets():
        nonlocal addr_entry, auto_scan_port, button1, button2
        for wid in [addr_entry, auto_scan_port, button1, button2]:
            wid.configure(state="normal")

    def disable_widgets():
        nonlocal addr_entry, auto_scan_port, button1, button2
        for wid in [addr_entry, auto_scan_port, button1, button2]:
            wid.configure(state="disabled")

    def connect_callback():
        global connecting_window
        nonlocal addr_entry, auto_scan_port, error_label, waiting_label
        error_label.configure(text=""); error_label.update()
        waiting_label.configure(text=I18N(["Connecting, may take some time...", "连接中，可能需要一些时间..."])); waiting_label.update()

        disable_widgets()
        connecting_window.configure(cursor="watch")

        adb_addr = addr_entry.get().strip()
        to_scan_port = bool(auto_scan_port.get())
        threading.Thread(target=process_ip_port, args=[adb_addr, to_scan_port]).start()
        connecting_window.after(func=process_callback, ms=100)

    def need_not_connection_callback():
        connecting_window.destroy()

    normal_font = I18N([ctk.CTkFont(family="Arial", size=16), ctk.CTkFont(family="Microsoft YaHei", size=16)])
    larger_font = I18N([ctk.CTkFont(family="Arial", size=18), ctk.CTkFont(family="Microsoft YaHei", size=18)])

    frame = tabview.tab(I18N(["Connecting", "连接"]))
    prompt_label = ctk.CTkLabel(
        master=frame, font=larger_font,
        text=I18N(["Wireless debugging IP address and port:    ", "无线调试 IP 地址和端口：                       "]),
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
    auto_scan_port = ctk.CTkCheckBox(
        master=frame, font=normal_font,
        text=I18N(["Auto detect port", "自动检测端口"]),
    )
    waiting_label = ctk.CTkLabel(master=frame, text="", font=normal_font)

    addr_entry.insert(0, CONFIG.config.device_ip1)
    if CONFIG.config.scan_port: auto_scan_port.select()

    prompt_label.grid(row=0, column=0, padx=20, pady=(10, 4), sticky="w")
    addr_entry.grid(row=1, column=0, padx=20, sticky="we")
    auto_scan_port.grid(row=2, column=0, padx=20, pady=(10, 4), sticky="w")
    error_label.grid(row=3, column=0, padx=20, pady=(10, 4), sticky="w")
    waiting_label.grid(row=4, column=0, padx=20, pady=2, sticky="w")

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
    # expose the addr_entry to mainwindow
    return addr_entry

def open_connecting_window():
    global connecting_window
    def delete_window_callback():
        connecting_window.destroy()
        adbutils.AdbClient().server_kill()
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

    connecting_addr_entry = mount_connecting_view(tabview)
    mount_pairing_view(tabview, connecting_addr_entry)

    if CONFIG.is_first_use:
        tabview.set(I18N(["Connecting", "连接"]))

    connecting_window.protocol("WM_DELETE_WINDOW", delete_window_callback)
    connecting_window.mainloop()
