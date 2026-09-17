"""启动装配：从向量库重建 BM25 索引 + 注册工具。
FastAPI / Streamlit 启动时调用 setup()，之后每次同步完调用 refresh()。"""
from .config import COLLECTION_NAME
from .bm_25 import BM25
from .tools import create_knowledge
from . import xiangliangku as vdb

_index_cache = {}      # {知识库名: BM25 索引}，每个库一份，懒加载


def get_bm25(collection=COLLECTION_NAME,force=False):
    """取某个知识库的 BM25 索引：没有就建，有就复用；force=True 强制重建"""
    if force or collection not in _index_cache:
        chunks = vdb.get_all_chunks(collection)
        print(f"[索引] 重建 {collection}：{len(chunks)} 个块")
        _index_cache[collection] = BM25(chunks)
    return _index_cache[collection]


def setup(collection=COLLECTION_NAME):
    """启动装配：建索引 + 注册工具"""
    bm25 = get_bm25(collection)
    create_knowledge(bm25)
    print(f"[装配] {collection} 就绪，可用工具：knowledge")
    return bm25


def refresh(collection=COLLECTION_NAME):
    """同步入库之后调用：重建索引并重新注册工具（让新文件立刻能被 BM25 搜到）"""
    bm25 = get_bm25(collection,force=True)
    create_knowledge(bm25)
    return bm25