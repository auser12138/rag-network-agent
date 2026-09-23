#检索文件统一文件格式，使用pathlib的rglob("*")进行查询文件夹下存在的文件
#1.定义文件输出的样式。2 定义检索的文件格式范围 3 对文件夹下的文件进行检索，根据编码不同情况进行if else  4 汇总放入类中
#防重复，使用哈希计算出文档的哈希值，文档变动哈希值也会变动
from pathlib import Path
import hashlib
from .loaders import load_text 

#定义输出样式
class Dacome:
    
    def __init__(self,content:str , source:str,file_hash):
        self.content = content#块内容
        self.source = source#块出处
        self.file_hash = file_hash
        
    def __repr__(self):
        return f"Dacome(source={self.source!r},chars={len(self.content)},hash={self.file_hash[:8]})"    
    
text_houzhui={".txt",".md",".pdf",".docx",".csv",".html",".log",".htm"}

#文件进行检索
def lodaer_file(path: Path):
    return load_text(path)

#计算文件哈希
def load_file_hash(path:Path):
    sha256 =hashlib.sha256()
    
    with path.open("rb") as f:
        while chunk := f.read(1024*1024):
            sha256.update(chunk)
    return sha256.hexdigest()
    
#扫描目录下的文件,使用rglob("*")
def lodaer_file_all(data_dir:Path):
    docs: list[Dacome]= [] #这是一个列表
    for path in sorted(data_dir.rglob("*")): #data文件地址存放在config中
        if path.suffix.lower() not in text_houzhui:
           continue
        if path.stat().st_size == 0:
            continue
        source = str(path.relative_to(data_dir))#relative_to公共前缀，剩下相对部分
        docs.append((path,source,load_file_hash(path)))
        
    return docs

