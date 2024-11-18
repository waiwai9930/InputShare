import gc
import threading
import customtkinter as ctk

from ui import ICON_ICO_PATH
from utils.config_manager import get_config
from utils.i18n import get_i18n, ENGLISH_LANGUAGE, CHINESE_LANGUAGE

settings_window: ctk.CTk | None = None
show_window_event = threading.Event()

def check_event():
    global settings_window
    if settings_window is None: return
    if show_window_event.is_set():
        settings_window.deiconify()
        settings_window.focus()
        show_window_event.clear()
    settings_window.after(func=check_event, ms=int(1000 / 30))

def mount_elements(root: ctk.CTk):
    def mouse_theme_section():
        nonlocal settings_scroll_frame, smaller_font, normal_font, larger_font, theme_var
        theme_frame = ctk.CTkFrame(master=settings_scroll_frame)
        theme_label = ctk.CTkLabel(
            master=theme_frame,
            font=larger_font,
            text=i18n(["Theme: ", "界面主题："]))
        system_radio = ctk.CTkRadioButton(
            master=theme_frame,
            text=i18n(["System", "跟随系统"]),
            font=normal_font,
            variable=theme_var, value="system")
        dark_radio = ctk.CTkRadioButton(
            master=theme_frame,
            text=i18n(["Dark theme", "夜间模式"]),
            font=normal_font,
            variable=theme_var, value="dark")
        light_radio = ctk.CTkRadioButton(
            master=theme_frame,
            text=i18n(["Light theme", "日间模式"]),
            font=normal_font,
            variable=theme_var, value="light")
        theme_frame.pack(fill="x", pady=(10, 4))
        theme_label.grid(row=0, padx=20, pady=(0, 6), sticky="w")
        system_radio.grid(row=1, padx=20, pady=4, sticky="w")
        dark_radio.grid(row=2, padx=20, pady=4, sticky="w")
        light_radio.grid(row=3, padx=20, pady=4, sticky="w")

    def mount_speed_section():
        nonlocal settings_scroll_frame, smaller_font, normal_font, larger_font, speed_var
        speed_frame = ctk.CTkFrame(master=settings_scroll_frame)
        speed_label = ctk.CTkLabel(
            master=speed_frame,
            font=larger_font,
            anchor="w",
            text=i18n(["Mouse speed: ", "鼠标移动速度："]))
        speed_slider_frame = ctk.CTkFrame(master=speed_frame)
        low_label = ctk.CTkLabel(
            master=speed_slider_frame,
            text=i18n(["low", "低"]),
            font=smaller_font)
        high_label = ctk.CTkLabel(
            master=speed_slider_frame,
            text=i18n(["high", "高"]),
            font=smaller_font)
        speed_slider = ctk.CTkSlider(
            master=speed_slider_frame,
            from_=1, to=4,
            variable=speed_var,
            number_of_steps=10)
        speed_frame.pack(fill="x", pady=(10, 4))
        speed_label.pack(fill="x", padx=20, pady=(0, 6))
        speed_slider_frame.pack(fill="x", padx=(16, 16), pady=4)
        low_label.pack(side=ctk.LEFT, padx=(10, 0))
        speed_slider.pack(side=ctk.LEFT, expand=True)
        high_label.pack(side=ctk.LEFT, padx=(0, 10))

    def mount_language_section():
        nonlocal settings_scroll_frame, smaller_font, normal_font, larger_font, language_var
        language_frame = ctk.CTkFrame(master=settings_scroll_frame)
        language_label = ctk.CTkLabel(
            master=language_frame,
            font=larger_font,
            text=i18n(["Language: ", "语言："]))
        chinese_radio = ctk.CTkRadioButton(
            master=language_frame,
            text="简体中文",
            font=ctk.CTkFont(family="Microsoft YaHei", size=16),
            variable=language_var, value=CHINESE_LANGUAGE)
        english_radio = ctk.CTkRadioButton(
            master=language_frame,
            text="English",
            font=normal_font,
            variable=language_var, value=ENGLISH_LANGUAGE)
        language_frame.pack(fill="x", pady=(10, 20))
        language_label.grid(row=0, padx=20, pady=(0, 6), sticky="w")
        chinese_radio.grid(row=1, padx=20, pady=4, sticky="w")
        english_radio.grid(row=2, padx=20, pady=4, sticky="w")

    def cancel():
        nonlocal root
        root.destroy()

    def confirm():
        nonlocal root, theme_var, speed_var, language_var
        get_config().theme = theme_var.get()
        get_config().mouse_speed = speed_var.get()
        get_config().language = language_var.get()
        root.destroy()

    i18n = get_i18n()
    smaller_font = i18n([ctk.CTkFont(family="Arial", size=12), ctk.CTkFont(family="Microsoft YaHei", size=12)])
    normal_font = i18n([ctk.CTkFont(family="Arial", size=16), ctk.CTkFont(family="Microsoft YaHei", size=16)])
    larger_font = i18n([ctk.CTkFont(family="Arial", size=18), ctk.CTkFont(family="Microsoft YaHei", size=18)])

    settings_scroll_frame = ctk.CTkScrollableFrame(master=root, height=320)
    settings_scroll_frame.pack(fill="x", expand=True)
    theme_var = ctk.StringVar(master=settings_scroll_frame, value=get_config().theme)
    speed_var = ctk.DoubleVar(master=settings_scroll_frame, value=get_config().mouse_speed)
    language_var = ctk.StringVar(master=settings_scroll_frame, value=i18n([ENGLISH_LANGUAGE, CHINESE_LANGUAGE]))

    mouse_theme_section()
    mount_speed_section()
    mount_language_section()

    button_frame = ctk.CTkFrame(master=root)
    cancel_button = ctk.CTkButton(
        master=button_frame,
        text=i18n(["Cancel", "取消"]),
        font=normal_font,
        command=cancel)
    confirm_button = ctk.CTkButton(
        master=button_frame,
        text=i18n(["Confirm", "确定"]),
        font=normal_font,
        command=confirm)
    button_frame.pack(fill="x")
    confirm_button.pack(padx=4, pady=10, side=ctk.RIGHT)
    cancel_button.pack(padx=4, pady=10, side=ctk.RIGHT)

def start_settings_window():
    global settings_window

    settings_window = ctk.CTk()
    settings_window.iconbitmap(ICON_ICO_PATH)
    settings_window.wm_title(get_i18n()(["InputShare Settings", "输入流转 —— 设置"]))
    settings_window.geometry("400x420")
    settings_window.minsize(400, 420)

    mount_elements(settings_window)
    settings_window.after(0, func=check_event)
    settings_window.mainloop()
    settings_window = None

    # manually do the GC,
    # prevent the automatical GC after this child thread closed
    # from causing errors with the tk variable
    gc.collect()

def open_settings_window():
    global settings_window, show_window_event
    if settings_window is not None:
        show_window_event.set()
        return
    thread = threading.Thread(target=start_settings_window)
    thread.start()
    return thread
