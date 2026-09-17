# 问答效果测试报告（fixed）

- 知识库块数：5
- 检索：向量 top20 + BM25 top20 -> RRF top20
- 重排：未启用（RERANK_BACKEND=api）
- 生成：RAG 提示词 + 大模型，资料取前 4 条

## 1. 交换机接口显示 down，应该怎么排查？

检索：向量 5 条 -> RRF 5 条 -> 最终 4 条；检索耗时 1.57s，生成耗时 1.55s

检索过程诊断：

向量检索 top3：
  1. `yunwei.md`（距离 0.2894）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路：
  2. `yunwei.md`（距离 0.4578）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致
  3. `yunwei.md`（距离 0.5249）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是

BM25 检索 top3：
  1. `yunwei.md`（分数 4.1654）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路：
  2. `yunwei.md`（分数 0.6933）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致
  3. `yunwei.md`（分数 0.6917）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是

命中的资料：

1. `yunwei.md`（分数 0.0328）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路： - Interface is down - Line protocol is down - Link down - Ethernet link failure 典型查看命令： show interf
2. `yunwei.md`（分数 0.0323）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致，可能出现： - 大量丢包 - CRC errors - late collisions - 网络性能下降 建议优先使用双方自动协商，而不是强制配置不一致的速率和双工。 ## 6. 排查顺序 推荐按照
3. `yunwei.md`（分数 0.0317）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是否匹配 如果接口完全没有 Link，优先检查物理链路。 ## 3. 检查接口配置 执行： show running-config interface GigabitEthernet0/1 确认接口没有
4. `linux.md`（分数 0.0312）：# Linux 网络故障排查 ## 1. 查看网卡状态 执行： ip addr 检查网卡是否存在 IP 地址。 执行： ip link 检查网卡是否处于 UP 状态。 ## 2. 检查默认路由 执行： ip route 确认存在 default route。 例如： default via 192.168.1.1 de

回答：

根据资料，交换机接口显示 down 时，可按以下内容排查：

1. **查看接口状态**：执行 `show interface GigabitEthernet0/1`，重点关注 interface status、line protocol status、input errors、CRC、output errors、interface resets、speed、duplex。
2. **检查 shutdown**：执行 `show running-config interface GigabitEthernet0/1`，确认接口没有配置 `shutdown`。如果发现 `shutdown`，说明接口被管理员关闭，可根据变更流程决定是否执行 `no shutdown`。
3. **检查物理链路**：检查网线、光模块和对端设备，包括网线是否松动、光模块是否正常、对端设备接口是否开启、光纤是否存在断纤。如果接口完全没有 Link，优先检查物理链路。
4. **检查对端接口**。
5. **检查 speed / duplex**：执行 `show interface GigabitEthernet0/1`，关注 Speed、Duplex。如果两端配置不一致，可能出现大量丢包、CRC errors、late collisions、网络性能下降。建议优先使用双方自动协商，而不是强制配置不一致的速率和双工。
6. **检查 CRC / input errors**：如果接口存在大量 CRC errors，通常需要检查网线质量、光纤、光模块、对端接口、双工配置。如果 CRC errors 持续增长，应重点排查物理层。
7. **查看接口日志**。
8. **必要时更换端口或硬件**。

推荐排查顺序为：查看接口状态 → 检查 shutdown → 检查网线/光模块 → 检查对端接口 → 检查 speed / duplex → 检查 CRC / input errors → 查看接口日志 → 必要时更换端口或硬件。

注意事项：涉及修改生产设备配置时，应遵循变更管理流程；未经确认不要直接执行 `shutdown`、`no shutdown`、interface configuration changes。

## 2. Linux 服务器怎么查看网卡状态和默认路由？

检索：向量 5 条 -> RRF 5 条 -> 最终 4 条；检索耗时 0.14s，生成耗时 0.90s

检索过程诊断：

向量检索 top3：
  1. `linux.md`（距离 0.4866）：# Linux 网络故障排查 ## 1. 查看网卡状态 执行： ip addr 检查网卡是否存在 IP 地址。 执行： 
  2. `linux.md`（距离 0.6747）：## 5. 检查端口 使用： ss -lntp 查看当前监听端口。 例如： LISTEN 0 128 0.0.0.0:8
  3. `yunwei.md`（距离 1.0278）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路：

BM25 检索 top3：
  1. `linux.md`（分数 3.4103）：# Linux 网络故障排查 ## 1. 查看网卡状态 执行： ip addr 检查网卡是否存在 IP 地址。 执行： 
  2. `linux.md`（分数 2.0396）：## 5. 检查端口 使用： ss -lntp 查看当前监听端口。 例如： LISTEN 0 128 0.0.0.0:8
  3. `yunwei.md`（分数 0.4916）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致

命中的资料：

1. `linux.md`（分数 0.0328）：# Linux 网络故障排查 ## 1. 查看网卡状态 执行： ip addr 检查网卡是否存在 IP 地址。 执行： ip link 检查网卡是否处于 UP 状态。 ## 2. 检查默认路由 执行： ip route 确认存在 default route。 例如： default via 192.168.1.1 de
2. `linux.md`（分数 0.0323）：## 5. 检查端口 使用： ss -lntp 查看当前监听端口。 例如： LISTEN 0 128 0.0.0.0:8080 说明服务器正在监听 8080 端口。 ## 6. 检查防火墙 可以查看： iptables -L 或者： nft list ruleset 检查是否存在阻止目标流量的规则。 ## 7. 排查顺
3. `yunwei.md`（分数 0.0315）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路： - Interface is down - Line protocol is down - Link down - Ethernet link failure 典型查看命令： show interf
4. `yunwei.md`（分数 0.0315）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致，可能出现： - 大量丢包 - CRC errors - late collisions - 网络性能下降 建议优先使用双方自动协商，而不是强制配置不一致的速率和双工。 ## 6. 排查顺序 推荐按照

回答：

根据资料1，Linux 服务器查看网卡状态和默认路由的方法如下：

**查看网卡状态：**
- 执行 `ip addr`，检查网卡是否存在 IP 地址。
- 执行 `ip link`，检查网卡是否处于 UP 状态。

**检查默认路由：**
- 执行 `ip route`，确认存在 default route。
- 例如：`default via 192.168.1.1 dev eth0`
- 如果没有默认路由，服务器可能无法访问外部网络。

## 3. 接口出现大量 CRC 错误，需要检查哪些方面？

检索：向量 5 条 -> RRF 5 条 -> 最终 4 条；检索耗时 0.17s，生成耗时 0.71s

检索过程诊断：

向量检索 top3：
  1. `yunwei.md`（距离 0.3863）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是
  2. `yunwei.md`（距离 0.4916）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致
  3. `yunwei.md`（距离 0.6806）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路：

BM25 检索 top3：
  1. `yunwei.md`（分数 2.7205）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是
  2. `yunwei.md`（分数 1.6133）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致
  3. `yunwei.md`（分数 1.5815）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路：

命中的资料：

1. `yunwei.md`（分数 0.0328）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是否匹配 如果接口完全没有 Link，优先检查物理链路。 ## 3. 检查接口配置 执行： show running-config interface GigabitEthernet0/1 确认接口没有
2. `yunwei.md`（分数 0.0323）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致，可能出现： - 大量丢包 - CRC errors - late collisions - 网络性能下降 建议优先使用双方自动协商，而不是强制配置不一致的速率和双工。 ## 6. 排查顺序 推荐按照
3. `yunwei.md`（分数 0.0317）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路： - Interface is down - Line protocol is down - Link down - Ethernet link failure 典型查看命令： show interf
4. `linux.md`（分数 0.0312）：# Linux 网络故障排查 ## 1. 查看网卡状态 执行： ip addr 检查网卡是否存在 IP 地址。 执行： ip link 检查网卡是否处于 UP 状态。 ## 2. 检查默认路由 执行： ip route 确认存在 default route。 例如： default via 192.168.1.1 de

回答：

根据资料，接口存在大量 CRC errors 时，通常需要检查以下方面：

- 网线质量
- 光纤
- 光模块
- 对端接口
- 双工配置

如果 CRC errors 持续增长，应重点排查物理层。

## 4. 公司年假有多少天？

检索：向量 5 条 -> RRF 5 条 -> 最终 4 条；检索耗时 0.18s，生成耗时 0.46s

检索过程诊断：

向量检索 top3：
  1. `yunwei.md`（距离 1.6958）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路：
  2. `linux.md`（距离 1.7253）：## 5. 检查端口 使用： ss -lntp 查看当前监听端口。 例如： LISTEN 0 128 0.0.0.0:8
  3. `yunwei.md`（距离 1.7386）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是

BM25 检索 top3：
  1. `yunwei.md`（分数 0.0000）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路：
  2. `yunwei.md`（分数 0.0000）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是
  3. `yunwei.md`（分数 0.0000）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致

命中的资料：

1. `yunwei.md`（分数 0.0328）：# 交换机接口 Down 故障排查手册 ## 1. 故障现象 当交换机接口出现以下状态时，通常表示接口无法正常建立链路： - Interface is down - Line protocol is down - Link down - Ethernet link failure 典型查看命令： show interf
2. `yunwei.md`（分数 0.0320）：1. 网线是否松动 2. 光模块是否正常 3. 对端设备接口是否开启 4. 光纤是否存在断纤 5. 接口两端速率和双工是否匹配 如果接口完全没有 Link，优先检查物理链路。 ## 3. 检查接口配置 执行： show running-config interface GigabitEthernet0/1 确认接口没有
3. `linux.md`（分数 0.0315）：## 5. 检查端口 使用： ss -lntp 查看当前监听端口。 例如： LISTEN 0 128 0.0.0.0:8080 说明服务器正在监听 8080 端口。 ## 6. 检查防火墙 可以查看： iptables -L 或者： nft list ruleset 检查是否存在阻止目标流量的规则。 ## 7. 排查顺
4. `yunwei.md`（分数 0.0315）：show interface GigabitEthernet0/1 关注： Speed Duplex 如果两端配置不一致，可能出现： - 大量丢包 - CRC errors - late collisions - 网络性能下降 建议优先使用双方自动协商，而不是强制配置不一致的速率和双工。 ## 6. 排查顺序 推荐按照

回答：

资料中未找到相关信息。
