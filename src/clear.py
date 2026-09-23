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

#合并被硬换行切断的句子（PDF 常见问题）,上一行【短】且【不以句末标点结尾】→ 认为是被切断的，和下一行合并
def merge_broken_lines(text,max_len=20):

    out = []
    for line in text.split("\n"):
        s = line.strip()
        if out and s:
            prev = out[-1].strip()
            if prev and len(prev) <= max_len and prev[-1] not in "。！？.!?:：;；":
                out[-1] = out[-1].rstrip() + s
                continue
        out.append(line)
    return "\n".join(out)

def drop_toc_lines(text,min_dots=5):
    """去掉目录行（带点线引导符的行）
    
    PDF 目录的特征：标题 + 一串点 + 页码
    例：1.1 basename ................ 5
    """
    keep = []
    for line in text.split("\n"):
        #连续 5 个以上的点/中圆点/省略号 → 判断为目录行
        if re.search(r"[.·…．]{5,}",line):
            continue
        keep.append(line)
    return "\n".join(keep)


def drop_toc_pages(text,threshold=0.5):
    """整页是目录的话，跳过这一页
    
    判断依据：目录行占比超过 threshold
    """
    lines = [l for l in text.split("\n") if l.strip()]
    if not lines:
        return text
    
    toc_count = sum(1 for l in lines if re.search(r"[.·…．]{5,}",l))
    if toc_count / len(lines) >= threshold:
        return ""            #整页丢弃
    return text

#数据清洗
def clean_text(text,merge_lines=False):
    text =  normalize_newlines(text)
    text = drop_toc_pages(text)
    text = drop_toc_lines(text)
    text = page_lines(text)
    text = drop_repeated_lines(text)
    if merge_lines:
        text = merge_broken_lines(text)
    text = strip_lines(text)
    text = blank_lines(text)
    return text.strip()