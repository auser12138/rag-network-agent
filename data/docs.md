重点检查：

设备型号和IOS/IOS XE版本
运行时间
CPU和内存
启动配置是否正常
接口模块和序列号
2.2 查看接口状态
show ip interface brief
show interfaces status
show interfaces counters errors

接口状态需要重点关注：

administratively down：接口被管理员关闭
down/down：物理链路或对端连接异常
up/down：物理链路正常但二层或三层协议异常
CRC、input errors、output errors持续增长
3. VLAN检查
show vlan brief
show interfaces trunk
show interfaces switchport

检查VLAN是否存在、端口VLAN是否正确、Trunk允许列表是否符合设计。

4. STP检查
show spanning-tree
show spanning-tree vlan 10

检查根桥、端口角色、端口状态以及是否存在频繁拓扑变化。

5. EtherChannel检查
show etherchannel summary
show interfaces port-channel

如果成员端口状态异常，应检查LACP模式、速率、双工、VLAN和Trunk参数。

6. 三层路由检查
show ip route
show ip protocols
show arp

确认路由表是否存在目标网段，ARP是否正常学习。

7. BGP检查
show ip bgp summary
show ip bgp neighbors

重点关注邻居状态。常见状态包括 Idle、Active、OpenSent、OpenConfirm、Established。

8. OSPF检查
show ip ospf neighbor
show ip ospf interface brief

重点检查邻居是否达到Full状态，以及Area、Router ID、网络类型和认证配置。

9. 日常维护
变更前备份配置。
变更后保存配置并验证业务。
不直接修改生产设备配置，必须遵循变更流程。
故障处理需要记录时间、现象、操作和结果。
""",

"manuals/Juniper交换机运维手册.md": """# Juniper交换机运维手册

1. 适用范围

适用于Juniper EX系列交换机和Junos系统的基础运维。

2. 基础信息检查
show version
show chassis hardware
show system uptime
show configuration
3. 接口检查
show interfaces terse
show interfaces extensive
show interfaces statistics

重点关注接口Link状态、Input errors、Output errors、CRC errors、Drops以及速率协商。

4. VLAN检查
show vlans
show ethernet-switching interfaces
show ethernet-switching table

检查VLAN是否存在、端口是否加入正确VLAN以及MAC地址学习是否正常。

5. 路由检查
show route
show arp

确认目标路由是否存在以及下一跳ARP解析是否正常。

6. OSPF检查
show ospf neighbor
show ospf interface

检查邻居状态、区域和接口参数。

7. BGP检查
show bgp summary
show bgp neighbor

确认邻居是否处于Established状态。

8. 配置变更

Junos支持候选配置机制。典型流程：

configure
set ...
commit check
commit

执行正式commit前应使用commit check检查配置语法和基本一致性。

9. 回滚

如果变更导致异常，应根据变更方案执行rollback，并验证业务恢复情况。
""",

"manuals/网络设备日常巡检规范.md": """# 网络设备日常巡检规范

1. 巡检目标

及时发现设备资源、接口、链路、路由协议和配置方面的异常。

2. 设备级检查

每日检查：

CPU利用率
内存利用率
设备运行时间
温度和电源状态
风扇状态
日志告警
3. 接口级检查

重点检查：

接口Up/Down状态
CRC错误
Input errors
Output errors
丢包和丢弃
光模块状态
速率和双工
4. 协议级检查

检查：

STP
LACP
OSPF
BGP
VRRP
DHCP Relay
5. 配置级检查

确认运行配置与基线配置一致。重要设备应定期备份配置。

6. 巡检记录

巡检记录至少包含设备名称、IP地址、检查时间、检查项目、异常现象、处理结果和责任人。
""",

"troubleshooting/接口down故障处理.md": """# 接口Down故障处理

1. 故障现象

交换机接口显示down，业务中断或终端无法访问网络。

2. 第一阶段：确认接口状态

Cisco：

show ip interface brief
show interfaces GigabitEthernet1/0/1

Juniper：

show interfaces terse
show interfaces ge-0/0/1 extensive

判断接口是administratively down、down/down还是up/down。

3. 第二阶段：检查物理链路

检查：

网线或光纤是否松动
对端设备接口是否正常
光模块是否匹配
接口速率和双工是否一致
是否存在物理层告警
4. 第三阶段：检查配置

确认接口没有被shutdown，VLAN、Trunk、速率和双工配置正确。

Cisco：

show running-config interface GigabitEthernet1/0/1
5. 第四阶段：查看错误计数器
show interfaces counters errors

如果CRC、input errors持续增长，应进一步检查链路质量、光模块、网线和对端端口。

6. 处理原则

先确认现象，再检查物理层，随后检查接口配置，最后验证业务恢复。生产环境禁止未经授权直接修改配置。
""",

"troubleshooting/BGP邻居down故障处理.md": """# BGP邻居Down故障处理

1. 故障现象

BGP邻居从Established变为Idle、Active或其他非Established状态。

2. 检查邻居状态

Cisco：

show ip bgp summary
show ip bgp neighbors <peer-ip>

Juniper：

show bgp summary
show bgp neighbor <peer-ip>
3. 排查TCP连接

BGP使用TCP 179端口。检查两端是否能够建立TCP连接。

4. 检查路由可达性

确认本端是否存在到对端BGP邻居地址的路由。

5. 检查配置

重点检查：

peer IP
AS号
update-source
ebgp-multihop
authentication
本地地址
VRF
6. 检查ACL和防火墙

确认TCP/179没有被ACL、防火墙或安全策略阻断。

7. 检查日志

搜索BGP邻居状态变化、TCP reset、authentication failure等日志。

8. 处理原则

不要直接重启BGP进程。应先确定故障层级，再针对性处理，并记录邻居恢复时间。
""",

"troubleshooting/OSPF邻居异常处理.md": """# OSPF邻居异常处理

1. 常见现象

OSPF邻居无法建立，或者邻居停留在Init、2-Way、ExStart、Exchange等状态。

2. 查看邻居

Cisco：

show ip ospf neighbor

Juniper：

show ospf neighbor
3. 检查关键参数

两端应重点检查：

Area
Hello interval
Dead interval
Network type
Authentication
MTU
Router ID
接口地址和掩码
4. ExStart/Exchange异常

如果邻居长期停留在ExStart或Exchange，重点检查MTU不一致以及重复Router ID等问题。

5. 检查链路

确认接口状态正常、VLAN正确、二层链路没有丢包。

6. 处理

修正参数后重新观察邻居状态，正常情况下邻居最终应进入Full状态。
""",

"troubleshooting/CRC错误排查.md": """# CRC错误排查

1. 故障现象

接口CRC错误持续增长，可能伴随丢包、重传和业务访问异常。

2. 查看计数器

Cisco：

show interfaces <interface>
show interfaces counters errors

Juniper：

show interfaces <interface> extensive
3. 常见原因
网线损坏
光纤污染或弯折
光模块异常
接口硬件故障
速率/双工协商异常
对端设备接口异常
电磁干扰
4. 排查顺序
确认CRC是否持续增加。
检查两端接口。
更换网线或光纤。
更换光模块。
更换交换机端口。
对比对端错误计数器。
5. 判断

如果更换物理介质后CRC停止增长，通常说明问题与物理链路相关；如果问题跟随设备端口移动，应进一步检查硬件。
""",

"troubleshooting/丢包故障排查.md": """# 丢包故障排查

1. 故障现象

用户访问服务器延迟高、Ping丢包或业务连接不稳定。

2. 基础测试
ping <destination>
traceroute <destination>

Windows可以使用：

ping -t <destination>
tracert <destination>
3. 判断丢包位置

从客户端、接入交换机、汇聚交换机、核心设备逐段测试，确定丢包开始出现的位置。

4. 检查接口

重点查看：

CRC
Input errors
Output errors
Drops
Queue drops
Utilization
5. 检查设备资源

CPU持续高、内存异常、接口拥塞和队列丢弃都可能导致业务异常。

6. 检查路由

确认是否存在错误路由、路由震荡或ECMP路径异常。

7. 处理原则

不要仅根据单次Ping判断链路故障，应结合持续测试、接口计数器、路径和业务指标综合判断。
""",

"troubleshooting/DHCP故障排查.md": """# DHCP故障排查

1. 故障现象

终端无法自动获取IP地址，或者获取到了错误网段地址。

2. 检查客户端

确认客户端DHCP功能正常，并观察是否获得169.254.x.x等自动私有地址。

3. 检查DHCP Server

确认：

DHCP服务运行正常
地址池有剩余地址
网关配置正确
DNS配置正确
租约没有耗尽
4. 检查交换机VLAN

确认终端所在接口属于正确VLAN。

5. 检查DHCP Relay

跨网段时检查：

show running-config interface <interface>

确认ip helper-address指向正确的DHCP服务器。

6. 检查网络策略

确认ACL、防火墙或安全设备没有阻断DHCP流量。

7. 验证

重新获取地址后检查IP、网关、DNS和租约信息，并进行连通性测试。
""",

"operation/交换机巡检规范.md": """# 交换机巡检规范

巡检项目
类别	检查内容
设备	CPU、内存、温度、电源、风扇
接口	Up/Down、CRC、错误、丢弃
VLAN	VLAN状态、端口归属
STP	根桥、拓扑变化、异常端口
LACP	聚合成员状态
路由	路由表、ARP
OSPF	邻居状态
BGP	邻居Established状态
日志	Error、Warning、链路变化
异常处理

发现异常后先截图或保存命令输出，再按照故障处理流程进行分析。未经审批不得执行生产配置变更。
""",

"operation/网络变更操作规范.md": """# 网络变更操作规范

1. 变更前

必须明确：

变更目的
影响范围
操作设备
操作人员
开始和结束时间
回退方案
2. 变更前检查

执行配置备份，并检查CPU、内存、接口、路由协议和关键业务状态。

3. 变更执行

按照经过审批的变更步骤执行。每完成一个关键步骤都进行验证。

4. 变更后验证

检查：

接口状态
VLAN
路由
OSPF/BGP邻居
Ping和业务连通性
日志
5. 回退

如果业务异常且达到回退条件，应按照预定回退方案恢复配置。

6. 记录

保存变更前后配置、命令输出、时间和验证结果。
""",

"operation/故障升级规范.md": """# 故障升级规范

1. P1重大故障

影响核心网络、大量用户或关键业务时，应立即通知网络负责人和相关业务负责人。

2. P2重要故障

影响部分业务或关键设备，但存在替代路径时，应在规定时间内升级。

3. P3一般故障

单个接口、单台终端或低影响问题，可以由一线运维按照标准流程处理。

4. 升级信息

升级时必须提供：

故障开始时间
影响范围
故障现象
已执行操作
命令输出
日志
初步判断
当前恢复情况
5. 禁止事项

不得为了快速恢复而绕过审批直接执行高风险生产变更。
""",

"logs/switch_001.log": """2026-09-17 08:31:02 SWITCH-001 %LINK-3-UPDOWN: Interface GigabitEthernet1/0/24, changed state to down
2026-09-17 08:31:03 SWITCH-001 %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet1/0/24, changed state to down
2026-09-17 08:33:17 SWITCH-001 %LINK-3-UPDOWN: Interface GigabitEthernet1/0/24, changed state to up
2026-09-17 08:33:18 SWITCH-001 %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet1/0/24, changed state to up
2026-09-17 09:12:44 SWITCH-001 %ETHCNTR-3-LOOPBACK_DETECTED: Loopback detected on GigabitEthernet1/0/12
2026-09-17 09:13:10 SWITCH-001 %SPANTREE-2-LOOPGUARD_BLOCK: Loop guard blocking port GigabitEthernet1/0/12
2026-09-17 10:21:55 SWITCH-001 %SYS-5-CONFIG_I: Configured from console by admin
""",

"logs/router_001.log": """2026-09-17 11:02:11 ROUTER-001 BGP-5-ADJCHANGE: neighbor 10.0.0.2 Down Peer closed the session
2026-09-17 11:02:12 ROUTER-001 TCP-3-RESET: TCP connection reset from 10.0.0.2:179
2026-09-17 11:03:40 ROUTER-001 BGP-5-ADJCHANGE: neighbor 10.0.0.2 Active
2026-09-17 11:06:02 ROUTER-001 BGP-5-ADJCHANGE: neighbor 10.0.0.2 Established
2026-09-17 12:44:31 ROUTER-001 %OSPF-4-ERRRCV: Received invalid packet from 10.0.1.2, interface Ethernet0/0
2026-09-17 12:44:32 ROUTER-001 %OSPF-5-ADJCHG: Neighbor 10.0.1.2 state changed from FULL to DOWN
""",

"logs/firewall_001.log": """2026-09-17 13:15:20 FIREWALL-001 policy=WEB-OUT action=deny src=10.10.10.25 dst=172.16.20.10 proto=TCP sport=51231 dport=443 reason=policy
2026-09-17 13:16:02 FIREWALL-001 policy=WEB-OUT action=deny src=10.10.10.25 dst=172.16.20.10 proto=TCP sport=51248 dport=443 reason=policy
2026-09-17 13:20:45 FIREWALL-001 policy=WEB-OUT action=allow src=10.10.10.25 dst=172.16.20.10 proto=TCP sport=51302 dport=443
2026-09-17 14:02:17 FIREWALL-001 system=warning cpu=86% memory=72%
""",

"incidents/INC-001.md": """# INC-001：交换机接口频繁Down

基本信息
时间：2026-09-17 08:31
设备：SWITCH-001
接口：GigabitEthernet1/0/24
影响：接入终端短时无法访问网络
现象

接口在08:31 Down，约2分钟后恢复。

排查
查看接口日志，确认发生LINK UP/DOWN。
查看接口错误计数器。
检查对端设备接口。
检查网线和水晶头。
更换网线后观察接口。
处理结果

更换网线后接口保持稳定，错误计数器不再增长。

根因

初步判断为物理链路质量异常，具体原因需要结合现场介质检测确认。
""",

"incidents/INC-002.md": """# INC-002：BGP邻居中断

基本信息
时间：2026-09-17 11:02
设备：ROUTER-001
邻居：10.0.0.2
影响：部分外部路由短时不可达
现象

BGP邻居从Established变为Down，随后进入Active，约4分钟后恢复Established。

排查

检查BGP状态、TCP/179连接、邻居路由和设备日志。

关键日志
BGP-5-ADJCHANGE: neighbor 10.0.0.2 Down Peer closed the session
TCP-3-RESET: TCP connection reset from 10.0.0.2:179
BGP-5-ADJCHANGE: neighbor 10.0.0.2 Established
处理结果

邻居自动恢复，未执行重启操作。

后续

继续监控邻居状态；如果重复发生，应检查对端设备和中间链路。
""",

"incidents/INC-003.md": """# INC-003：终端无法获取DHCP地址

基本信息
时间：2026-09-17 15:20
影响：办公区VLAN 20部分终端
故障类型：DHCP地址获取失败
现象

终端无法获得正常业务IP地址，部分客户端获得169.254.x.x地址。

排查
检查接入交换机VLAN 20。
检查DHCP Relay。
检查DHCP服务器地址池。
检查防火墙策略。
从交换机到DHCP服务器逐段测试连通性。
发现

DHCP地址池剩余地址数量正常，交换机VLAN配置正常。检查Relay配置发现服务器地址配置错误。

处理

修正DHCP Relay服务器地址并重新获取IP。

结果

终端成功获取VLAN 20地址、网关和DNS配置，业务恢复。
"""
}

for rel, content in files.items():
p = root / rel
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(content, encoding="utf-8")

print(f"已生成 {len(files)} 个文件，共 {sum(len(v) for v in files.values()):,} 个字符。")
print(root)