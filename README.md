# InputShare

__InputShare__ enables you share keyboard and mouse of your computer with an Android device via ADB in wired / wireless way.

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

## Usage

You firstly need to enable the __Developer Settings__ of your device.

For wired connection:

1. Enable the __USB Debugging__ in the __Developer Settings__ page
2. Connect your device with computer via a USB cable
3. Just run the script with `python main.py` and skip steps
4. Enjoy your mouse and keyboard on Android device

For wireless connection:

1. Enable the __Wireless Debugging__ in the Developer Settings page
2. Run the script with `python main.py`
3. Open __Pair device with pairing code__ option and input the IP address and port and the pairing code into the pairing tab of connecting window
4. Input the IP address and port in the main __Wireless Debugging__ into the connecting tab of connection window
5. Enjoy your mouse and keyboard on Android device

## Shortcuts

The shortcuts following are available after connection

`<Ctrl>+<Shift>+s`: toggle the control between your computer and your Android device
`<Ctrl>+<Shift>+q`: quit the program

## Development

Build project:

```bash
pyinstaller --windowed --add-data "./adb-bin/;adb-bin/" --add-data "./server/scrcpy-server;server/" main.py
```
