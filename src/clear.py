import re

#统一换行符
def normalize_newlines(text):
    return text.replace("\r\n","\n").replace("\r","\n")

#清空首尾空白
def strip_lines(text):
    return "\n".join(line.strip() for line in text.split("\n"))

#压缩空行
def blank_lines(text,maxblank=1):
    return re.sub(r"\n{%d,}" % (maxblank+1),"\n"*(maxblank+1),text)

#去除页码行
def page_lines(text):
    patterns = [
        re.compile(r"^\s第\s*\d+\s页\s*(共\s*\d+\s*页)?\s*$"),
        re.compile(r"^\s第\s*\d+\s页\s*[，,/]\s*共\s*\d+\s*页\s*$"),
        re.compile(r"^\sPage\s+\d+(\s+of\s+\d)?s*$",re.I),
        re.compile(r"^\s*\d+\s*/\s*\d+\s*$"),
        re.compile(r"^\s*-\s*\d+\s*-\s*$"),
        re.compile(r"^\s*\d{1,3}\s*$"),
    ]
    
    keep = []
    
    for line in text.split("\n"):
        if any(p.match(line) for p in patterns):
            continue
        keep.append(line)
    return "\n".join(keep)

#去掉反复出现的【短行】（页眉/页脚常见特征）多次出现相同内容短行
def drop_repeated_lines(text,min_count=5,min_len=2,max_len=40):
    lines = text.split("\n")
    count = {}
    for line in lines:
        s =  line.strip()
        if min_len<=len(s)<=max_len:
            count[s] = count.get(s,0) +1
    repeated = {s for s,c in count.items() if c >=min_count}
    if not repeated:
        return text
    return "\n".join(l for l in lines if l.strip() not in repeated)

#结构性行：编号标题 / 第X章 / 列表项 / 选项 / 命令+参数
#这类行再短也不该和下一行合并，否则标题会被粘进正文
STRUCT_LINE = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\s+\S"                    #1 文件管理 / 1.1 basename
    r"|第\s*[一二三四五六七八九十百\d]+\s*[章节篇]"
    r"|[-*+·]\s"                                     #列表项
    r"|--\S"                                         #--help / --version
    r"|\S+\s*\[[^\]\n]*\])"                          #chgrp [-cfhRv][--help]
)

#合并被硬换行切断的句子（PDF 常见问题）
#上一行【短】且【不以句末标点结尾】且两行都【不是结构性行】→ 才认定被切断并合并
def merge_broken_lines(text,max_len=20):

    out = []
    for line in text.split("\n"):
        s = line.strip()
        if out and s:
            prev = out[-1].strip()
            if (prev and len(prev) <= max_len
                    and prev[-1] not in "。！？.!?:：;；"
                    and not STRUCT_LINE.match(prev)
                    and not STRUCT_LINE.match(s)):
                out[-1] = out[-1].rstrip() + s
                continue
        out.append(line)
    return "\n".join(out)

#目录行：标题 + 一串点 + 页码
TOC_LINE = re.compile(r"[.·…．]{5,}")

def toc_line_ratio(text):
    """点线行占非空行的比例（目录页通常 > 0.8）"""
    lines = [l for l in text.split("\n") if l.strip()]
    if not lines:
        return 0.0
    return sum(1 for l in lines if TOC_LINE.search(l)) / len(lines)

def is_toc_page(text,threshold=0.5,min_lines=8):
    """判断【这一页】是不是目录页

    min_lines：非空行少于 8 行时结构太简单，比例不可靠，一律不算目录页
    """
    if len([l for l in text.split("\n") if l.strip()]) < min_lines:
        return False
    return toc_line_ratio(text) >= threshold

def drop_toc_lines(text):
    """去掉目录行（带点线引导符的行）
    
    PDF 目录的特征：标题 + 一串点 + 页码
    例：1.1 basename ................ 5
    """
    keep = []
    for line in text.split("\n"):
        #连续 5 个以上的点/中圆点/省略号 → 判断为目录行
        if TOC_LINE.search(line):
            continue
        keep.append(line)
    return "\n".join(keep)

def drop_toc_pages(text,threshold=0.5,min_lines=8):
    """整页是目录的话，跳过这一页（返回空串）
    
    判断依据：目录行占比超过 threshold，且非空行数不少于 min_lines
    """
    if is_toc_page(text,threshold,min_lines):
        return ""            #整页丢弃
    return text

#最小清洗（安全阀用的兜底版本：只统一换行、去首尾空白、压空行）
def basic_clean(text):
    text = normalize_newlines(text)
    text = strip_lines(text)
    text = blank_lines(text)
    return text.strip()

#数据清洗
def clean_text(text,merge_lines=False,safe_ratio=0.3):
    """按顺序去噪

    safe_ratio：安全阀。整篇清洗后剩余不足原文的 safe_ratio 时，
                判定为规则误伤（而不是"文档真的很脏"），回退到最小清洗
    """
    text =  normalize_newlines(text)
    raw_len = len(text.strip())

    out = drop_toc_pages(text)
    toc_dropped = (out == "")   #整页目录是主动丢弃，不走安全阀
    if not toc_dropped:
        out = drop_toc_lines(out)
        out = page_lines(out)
        out = drop_repeated_lines(out)
        if merge_lines:
            out = merge_broken_lines(out)
    out = strip_lines(out)
    out = blank_lines(out)
    out = out.strip()

    #安全阀：非目录页却被洗得只剩不到 30% → 认定规则误伤，回退
    if not toc_dropped and raw_len > 200 and len(out) < raw_len * safe_ratio:
        return basic_clean(text)
    return out
