# Linux 网络故障排查

## 1. 查看网卡状态

执行：

ip addr

检查网卡是否存在 IP 地址。

执行：

ip link

检查网卡是否处于 UP 状态。

## 2. 检查默认路由

执行：

ip route

确认存在 default route。

例如：

default via 192.168.1.1 dev eth0

如果没有默认路由，服务器可能无法访问外部网络。

## 3. 检查 DNS

查看：

cat /etc/resolv.conf

测试：

nslookup example.com

如果 IP 可以访问，但是域名无法解析，应优先检查 DNS。

## 4. 检查网络连通性

首先：

ping 127.0.0.1

然后：

ping 本机网关

最后：

ping 目标服务器

通过逐层测试确定网络故障位置。

## 5. 检查端口

使用：

ss -lntp

查看当前监听端口。

例如：

LISTEN 0 128 0.0.0.0:8080

说明服务器正在监听 8080 端口。

## 6. 检查防火墙

可以查看：

iptables -L

或者：

nft list ruleset

检查是否存在阻止目标流量的规则。

## 7. 排查顺序

1. 网卡状态
2. IP 地址
3. 默认路由
4. 网关连通性
5. DNS
6. 目标服务器
7. 防火墙
8. 应用端口11