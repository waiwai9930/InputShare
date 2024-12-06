# 已知缺陷

## 设备熄屏后会自动断开连接

在程序成功连接后，无论是电脑端还是安卓端熄屏，都会导致连接断开。此时需要重新启动程序并重新连接才能继续使用。

**解决办法**：目前程序内提供了“保持设备屏幕常亮”设置，开启后可以防止安卓端设备熄屏，从而避免此问题。

## 与 Bonjour 冲突

一些同类软件，如 [barrier](https://github.com/debauchee/barrier) 和 [deskflow](https://github.com/deskflow/deskflow)，会使用 [Bonjour](https://developer.apple.com/bonjour/) 来简化网络连接。
但根据部分用户反馈，在电脑上运行 barrier 并启动 Bonjour 后，再使用本软件时，会导致本软件的连接成功率显著降低。

**解决办法**：目前本软件与 Bonjour 的冲突原因尚不清楚。你可以尝试先使用本软件连接，再启动 barrier 来规避此问题。
