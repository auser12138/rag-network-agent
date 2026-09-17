# 交换机接口 Down 故障排查手册

## 1. 故障现象

当交换机接口出现以下状态时，通常表示接口无法正常建立链路：

- Interface is down
- Line protocol is down
- Link down
- Ethernet link failure

典型查看命令：

show interface GigabitEthernet0/1

需要重点关注：

- interface status
- line protocol status
- input errors
- CRC
- output errors
- interface resets
- speed
- duplex

## 2. 检查物理链路

首先检查网线、光模块和对端设备。

检查内容：

1. 网线是否松动
2. 光模块是否正常
3. 对端设备接口是否开启
4. 光纤是否存在断纤
5. 接口两端速率和双工是否匹配

如果接口完全没有 Link，优先检查物理链路。

## 3. 检查接口配置

执行：

show running-config interface GigabitEthernet0/1

确认接口没有配置：

shutdown

如果发现：

interface GigabitEthernet0/1
 shutdown

说明接口被管理员关闭。

可以根据变更流程决定是否执行：

no shutdown

## 4. 检查 CRC 错误

如果接口存在大量 CRC errors，通常需要检查：

- 网线质量
- 光纤
- 光模块
- 对端接口
- 双工配置

如果 CRC errors 持续增长，应重点排查物理层。

## 5. 检查速率和双工

执行：

show interface GigabitEthernet0/1

关注：

Speed
Duplex

如果两端配置不一致，可能出现：

- 大量丢包
- CRC errors
- late collisions
- 网络性能下降

建议优先使用双方自动协商，而不是强制配置不一致的速率和双工。

## 6. 排查顺序

推荐按照以下顺序排查：

1. 查看接口状态
2. 检查 shutdown
3. 检查网线/光模块
4. 检查对端接口
5. 检查 speed / duplex
6. 检查 CRC / input errors
7. 查看接口日志
8. 必要时更换端口或硬件

## 7. 注意事项

涉及修改生产设备配置时，应遵循变更管理流程。

未经确认不要直接执行：

shutdown
no shutdown
interface configuration changes