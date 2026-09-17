#扫描文本的哈希进行校验匹配三种状态：新增，更新，跳过不保存，新增入库，更新将旧块删除入库，跳过不执行入库
#jiaoyan.py,lodaer,splitter,repos_sql,config,xiangliangku
from pathlib import Path
from .jiaoyan import check_chunk,check_file,NEW,SKIP,UPDATE
from .config import data_dir as DEFAULT_DATA_DIR, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP
from .lodaer import Dacome, lodaer_file_all,lodaer_file
from .splitter import RecursiveTextSplitter
from .repos_sql import add_file,update_file,deleted_file,list_file
from . import xiangliangku as vdb


def sync(data_path = DEFAULT_DATA_DIR,collection = COLLECTION_NAME):
    data_path = Path(data_path)
    files = lodaer_file_all(data_path)
    
    if not files:
        print("目录里没有文件")
    
    splitter = RecursiveTextSplitter(CHUNK_SIZE,CHUNK_OVERLAP)
    added = update = skipped = 0
    
    for path,source,file_hash in files:
        status = check_file(source,file_hash,collection)
        #校验文本是否存在
        if status == SKIP:
            print(f"跳过:{source}")
            skipped +=1
            continue
        
        text = lodaer_file(path)
        if not text.strip():
            print(f"跳过空内容:{source}")
            skipped +=1
            continue
        #切分，去重
        doc =Dacome(content=text,source = source,file_hash=file_hash)
        chunks = check_chunk(splitter.split_Dacome([doc]))
        
        #先删除旧块
        if status == UPDATE:
            vdb.delete_source(source,collection)
        #导入向量库    
        vdb.add_chunks(chunks,collection)
        
        #mysql
        chunk_count = len(chunks)
        
        if status == NEW:
            add_file(source,file_hash,chunk_count,collection)
            added +=1
            print(f"新增:{source} ({chunk_count}块)")
        else:
            update_file(source,file_hash,chunk_count,collection)
            update +=1
            print(f"更新:{source} ({chunk_count}块)")
            
    #记录删除
    deleted = 0
    seen = {source for _,source,_ in files}
    for row in list_file(collection):
        if row["source"] not in seen:
            vdb.delete_source(row["source"],collection)
            deleted_file(row["source"],collection)
            deleted +=1
            print(f"删除:{row['source']}")
            
    print(f"[同步] 新增 {added} / 更新 {update} / 跳过 {skipped} / 删除 {deleted}")
    return {"added": added, "updated": update, "skipped": skipped, "deleted": deleted}


if __name__ == "__main__":
    sync()            
        
            
    