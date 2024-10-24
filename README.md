# ADB Input Control

__ADB Input Control__ enables you share keyboard and mouse of your computer with an Android device via ADB.

## Features

- __Seamless Switching__: Quickly switch keyboard and mouse input between the PC and Android device with hotkey.
- __Wired / Wireless Connection__: Supports both wired and wireless connections for flexible input sharing.
- __Wide Compatibility__: Compatible with various Android devices, not a specific brand.

## Install

Currently, this program is not completed, and there are some functions unavailable, so there is no pre-build binary and you have to clone and run with source code.

```bash
git clone https://github.com/BHznJNs/adb_input_control
cd adb_input_control
pip install -r requirements.txt
```

Then you have to enable the USB Debugging / Wireless Debugging (depends on the wired / wireless you want), pair your device, and then,

```bash
python main.py
```
