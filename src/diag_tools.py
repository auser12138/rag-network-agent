"""诊断工具：ping / DNS / TCP 端口 / 读日志
"""
import os
import re
import socket
import subprocess
import time
from pathlib import Path

from .tool import registry
from .config import LOG_DIR_ALLOWLIST

#host 只允许字母数字、点、横线、冒号（IPv4/IPv6/域名）
_HOST_PATTERN = re.compile(r"^[A-Za-z0-9\.\-:]{1,253}$")


def _check_host(host):
    """校验 host 格式，防止命令注入"""
    host = (host or "").strip()
    if not _HOST_PATTERN.match(host):
        raise ValueError(f"host 格式不合法：{host!r}（只允许 IP 或域名）")
    return host


# ---------------- ① ping ----------------
def ping_host(host,count=4,timeout=15):
    """检测连通性：丢包率 + 平均延迟"""
    host = _check_host(host)
    count = max(1,min(int(count),10))
    
    flag = "-n" if os.name == "nt" else "-c"   
    cmd = ["ping",flag,str(count),host]        #列表传参，不用 shell
    
    try:
        proc = subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
    except subprocess.TimeoutExpired:
        return f"ping {host} 超时（{timeout}s）：目标可能不可达，或禁用了 ICMP"
    except FileNotFoundError:
        return "系统里没有 ping 命令（容器镜像需要装 iputils-ping）"
    
    out = (proc.stdout or "") + (proc.stderr or "")
    return (
        f"ping {host}（{count} 次）\n"
        f"丢包率：{_parse_loss(out)}\n"
        f"平均延迟：{_parse_rtt(out)}\n"
        f"原始输出：\n{out[:600]}"
    )


def _parse_loss(text):
    m = re.search(r"(\d+(?:\.\d+)?)%\s*packet loss",text)
    if m:
        return f"{m.group(1)}%"
    m = re.search(r"丢失\s*=\s*(\d+)",text)
    if m:
        return f"{m.group(1)} 个包丢失"
    return "未知"


def _parse_rtt(text):
    m = re.search(r"=\s*([\d\.]+)/([\d\.]+)/([\d\.]+)",text)
    if m:
        return f"{m.group(2)} ms（min/avg/max = {m.group(1)}/{m.group(2)}/{m.group(3)}）"
    m = re.search(r"平均\s*=\s*(\d+)ms",text)
    if m:
        return f"{m.group(1)} ms"
    return "未知"


# ---------------- ② DNS ----------------
def dns_lookup(domain):
    """解析域名，返回 IP 列表和解析耗时"""
    domain = _check_host(domain)
    start = time.time()
    try:
        infos = socket.getaddrinfo(domain,None)
        ips = sorted({i[4][0] for i in infos})
        cost = (time.time() - start) * 1000
        return f"DNS 解析 {domain}\n耗时：{cost:.0f} ms\n解析结果：{', '.join(ips)}"
    except socket.gaierror as e:
        cost = (time.time() - start) * 1000
        return (
            f"DNS 解析 {domain} 失败（耗时 {cost:.0f} ms）：{e}\n"
            f"可能原因：域名不存在 / DNS 服务器不可达 / 网络不通"
        )


# ---------------- ③ TCP 端口 ----------------
def tcp_port_check(host,port,timeout=3):
    """检测端口连通性，区分'超时'和'拒绝连接'"""
    host = _check_host(host)
    port = int(port)
    if not (1 <= port <= 65535):
        raise ValueError(f"端口不合法：{port}")
    
    start = time.time()
    try:
        with socket.create_connection((host,port),timeout=timeout):
            cost = (time.time() - start) * 1000
            return f"TCP {host}:{port} 可连通（耗时 {cost:.0f} ms）"
    except socket.timeout:
        return (
            f"TCP {host}:{port} 连接超时（{timeout}s）\n"
            f"判断：包被丢弃（防火墙 DROP / 目标不可达）——不是服务没起"
        )
    except ConnectionRefusedError:
        return (
            f"TCP {host}:{port} 拒绝连接\n"
            f"判断：目标主机可达，但该端口没有服务在监听（或防火墙 REJECT）"
        )
    except Exception as e:
        return f"TCP {host}:{port} 检测失败：{type(e).__name__}: {e}"


# ---------------- ④ 读日志 ----------------
def read_log(path,keyword="",lines=50):
    """读取日志文件尾部，可按关键字过滤"""
    p = Path(path).resolve()
    
    allowed = [Path(d).resolve() for d in LOG_DIR_ALLOWLIST]
    if not any(p.is_relative_to(d) for d in allowed):
        return f"拒绝访问：只允许读取 {LOG_DIR_ALLOWLIST} 目录下的日志文件"
    if not p.is_file():
        return f"文件不存在：{path}"
    
    lines = max(1,min(int(lines),200))
    tail = _tail(p,2000)
    if keyword:
        tail = [l for l in tail if keyword in l]
    
    picked = tail[-lines:]
    if not picked:
        return f"没有匹配的日志行（关键字：{keyword}）"
    return f"{path} 最后 {len(picked)} 行：\n" + "\n".join(picked)


def _tail(path: Path,max_lines: int):
    
    with path.open("rb") as f:
        f.seek(0,os.SEEK_END)
        size = f.tell()
        block = min(size,256 * 1024)
        f.seek(size - block)
        data = f.read(block)
    return data.decode("utf-8",errors="ignore").splitlines()[-max_lines:]


# ---------------- 注册 ----------------
def create_diag_tools():
    registry.regist(
        name="ping_host",
        description="检测目标主机/域名的网络连通性，返回丢包率和平均延迟。参数：host（IP或域名）、count（次数，默认4）",
        func=ping_host,
    )
    registry.regist(
        name="dns_lookup",
        description="解析域名对应的 IP，并给出解析耗时。参数：domain（域名）",
        func=dns_lookup,
    )
    registry.regist(
        name="tcp_port_check",
        description="检测目标主机的指定端口是否可连通，能区分'超时'和'拒绝连接'。参数：host（IP或域名）、port（端口号）",
        func=tcp_port_check,
    )
    registry.regist(
        name="read_log",
        description="读取日志文件的最近内容，可按关键字过滤。参数：path（日志文件路径）、keyword（可选，过滤关键字）、lines（返回行数，默认50）",
        func=read_log,
    )