# 输入流转

__输入流转__ 能够让你的安卓设备通过有线/无线的方式和电脑**共享键鼠**。

## 特点

- __无感切换__：通过键盘热键快捷地在电脑和安卓设备间切换
- __有线/无线连接__：支持 USB 有线和局域网无线两种方式连接你的设备
- __强兼容性__：适用于多种安卓设备，不局限于特定品牌的电脑和安卓设备
- __剪贴板同步__：让电脑与手机的剪贴板内容无缝同步
- __简单易用的图像界面__

## 屏幕截图

![配对界面](./screenshots/pairing_zh.png)
![连接界面](./screenshots/connecting_zh.png)
![系统托盘](./screenshots/tray_selections_zh.png)

## 安装

请前往[发布界面][https://github.com/BHznJNs/InputShare/releases]下载最新版本的压缩包，解压，运行其中的 `.exe` 可执行文件。

## 使用方法

你首先需要启用你的安卓设备上的 __开发者选项__。

__对于有线连接：__

1. 在 __开发者选项__ 界面下启用 __USB 调试__
2. 使用 USB 数据线连接你的电脑和安卓设备
3. 运行可执行文件，跳过配对和连接步骤
4. 你可以开始正常使用了

__对于无线连接：__

1. 在 开发者选项 页面中开启 无线调试
2. 运行可执行文件
3. 在安卓设备上：打开“使用配对码配对设备”选项，并在电脑端连接窗口的配对标签页中输入 IP 地址、端口及配对码，点击“配对”按钮（此为配对步骤，通常只在第一次使用软件时需要）
4. 将安卓设备上“无线调试”界面下的 IP 地址和端口输入到连接窗口的连接标签页中，点击“连接”按钮
5. 你可以开始正常使用了

## 快捷键

下面的快捷键在你连接设备完成后可用：

| 快捷键 | 功能描述 |
| --- | --- |
| `<Ctrl>+<Alt>+s` | 在您的电脑和 Android 设备间切换控制 |
| `<Ctrl>+<Alt>+q` | 退出程序 |
| `F1` | 多任务切换 |
| `F2` | 回到桌面 |
| `F3` | 返回 |
| `F4` | 上一首歌曲 |
| `F5` | 播放 / 暂停 歌曲 |
| `F6` | 下一首歌曲 |
| `F7` | 降低音量 |
| `F8` | 提升音量 |
| `F9` | 降低亮度 |
| `F10` | 提升亮度 |
| `F11` | 熄屏 |
| `F12` | 亮屏 |

下面的快捷键在你连接设备完成后且没有共享输入时可用：

| 快捷键 | 功能描述 |
| --- | --- |
| `<Alt>+UP` | 向上滚动 |
| `<Alt>+DOWN` | 向下滚动 |
| `<Alt>+[` | 上一首歌曲 |
| `<Alt>+]` | 下一首歌曲 |
| `<Alt>+\` | 播放 / 暂停 歌曲 |

## 常见问题

### 启用无线调试太麻烦，有没有途径快速启用？

你可以参考这个视频，将无线调试设置到系统下拉通知栏：
[安卓手机快捷启用无线调试
](https://www.bilibili.com/video/BV1r1UKYjEWj/)

### 这会把安卓设备的屏幕也共享到电脑吗？

不会，__输入流转__ 只会共享键盘和鼠标，不会将安卓设备的屏幕内容投屏到电脑。

### 我需要自己配置 ADB 吗？

不需要，软件内打包了adb，会自动调用。

## 开发

克隆此仓库：

```bash
git clone https://github.com/BHznJNs/InputShare
cd InputShare
```

安装依赖项：

```bash
pip install -r requirements.txt
```

运行入口文件：

```bash
python main.py
```

如果你想要自己构建这个项目，请继续阅读：

### 构建

安装 pyinstaller：

```bash
pip install pyinstaller
```

获取 `customtkinter` 库的路径

```bash
pip show customtkinter
```

这会输出一个类似于下面这样的路径： `c:\users\<user_name>\appdata\local\programs\python\python310\lib\site-packages`

然后你就可以使用这个命令来构建项目（替换 `<CustomTkinter Location>` 为上面获得的 `customtkinter` 库路径）：

```bash
pyinstaller --windowed --icon=ui/icon.ico --add-data "./ui/icon.ico;ui/" --add-data "./ui/icon.png;ui/" --add-data "./adb-bin/;adb-bin/" --add-data "./server/scrcpy-server;server/" --add-data "<CustomTkinter Location>/customtkinter;customtkinter/" main.py
```
