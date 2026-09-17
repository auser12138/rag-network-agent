from .config import COLLECTION_NAME
from .repos_sql import get_file
from .chunk_id import make_chunk_hash



NEW = "new"          # 库里没有 → 需要新增
SKIP = "skip"        # 有记录且哈希相同 → 跳过
UPDATE = "update"    # 有记录但哈希不同 → 需要更新

def check_file(source,file_hash,collection = COLLECTION_NAME):
    old = get_file(source,collection)
    
    if old is None:
        return NEW
    if old["status"] != "active":        # 登记过但已被标记删除 → 现在又回来了
        return UPDATE
    if old["file_hash"] ==file_hash:
        return SKIP
    return UPDATE



def check_chunk(chunks):
    chunk ={}
    for d in chunks:
        chunk[make_chunk_hash(d.source,d.content)] = d
    return list(chunk.values())

