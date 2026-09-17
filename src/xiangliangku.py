import chromadb
from  chromadb.config import Settings
from  .config import db_dir, COLLECTION_NAME
from .embedder import embed_texts
from .chunk_id import make_chunk_hash
from .lodaer import Dacome

#初始化db客户端，数据持久化
def get_client():
    return chromadb.PersistentClient(
        path=str(db_dir),
        settings=Settings(anonymized_telemetry=False),
    )
    
#获取/创建集合（集合不存在则创建），相当于数据库创建表
def get_biao(collection_name=None):
    return get_client().get_or_create_collection(name=collection_name or COLLECTION_NAME)

#删除文件全部块
def delete_source(source,collection_name=None):
    get_biao(collection_name).delete(where = {'source': source})

#查看文件有多少块
def number_chunks(source,collection_name=None):
    res = get_biao(collection_name).get(where = {"source":source},include = ["metadatas"])
    return len(res["ids"])

#分好的向量填入向量库
def add_chunks(chunks,collection_name=None ):
    if not chunks:
        return 0
    texts = [d.content for d in  chunks]
    vectors = embed_texts(texts)#每个块向量化
    ids = [make_chunk_hash(d.source,d.content) for d in chunks]#每个块的id
    metadatas = [{"source": d.source, "file_hash": d.file_hash,"chunk_id":cid} for d,cid in zip(chunks,ids)] #每个块的出处
    
    #写入库中
    get_biao(collection_name).upsert(
        ids = ids,
        documents= texts,
        embeddings= vectors,
        metadatas= metadatas,
    )
    return len(chunks)
def add_xiangliang(Dacoms,collection_name=None):
    return add_chunks(Dacoms,collection_name)


#从向量库读出某个知识库的全部块（重建 BM25 索引用）
def get_all_chunks(collection_name=None):
    res = get_biao(collection_name).get(include=["documents","metadatas"])
    
    chunks = []
    for text,meta in zip(res["documents"],res["metadatas"]):
        chunks.append(Dacome(
            content=text,
            source=meta["source"],
            file_hash=meta.get("file_hash",""),
        ))
    return chunks
