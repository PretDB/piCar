# 要求
本系统的正常运行需要有WiFi网络。使用手机或无线路由器创建名为“zcm”的无线网络，并设置其密码为“11111111”（八个"1”）。等待片刻即可，当链接成功后，手机APP界面的“链接”字样会变为绿色，如果没有链接上，则“链接”为红色，部分链接（一部分设备在线）则为黄色。

# 操作
## 光定位模块
### 安装
在最初安装的时候，请注意安装顺序

# 技术细节
## 通信
1. 心跳包：心跳包是用来确认设备存活的一个工具。小车在正常运行的时候，会自动向所在的网络中发送心跳包，app可以通过侦听特定的端口来检查小车是否在线/正常运行。在心跳包中还包含了一些重要的信息，例如小车的IP地址、ID号码以及小车的地址。心跳包发送的频率为0.5Hz。为了保证实时性，心跳包以一部分稳定性为代价，保证了实时性。
2. 控制流：控制流是APP控制的小车运动的手段，控制流将向小车发送移动指令以及模式切换指令。控制流上的数据使用稳定的网络传输协议。
