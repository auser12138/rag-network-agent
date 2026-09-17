from .embedder import embed_text
from .xiangliangku import get_biao
from  .bm_25 import BM25
from  .hybrid import rrf_fusion
from .rerank import Rerank
from .chunk_id import make_chunk_hash

    #向量相似度比较,向量库内置相似度比较
def xiangsibijiao(quer_text,top_k=20):
        vec = embed_text(quer_text)
        res = get_biao().query(
            query_embeddings = [vec],
            n_results = top_k,
            include = ["documents","metadatas","distances"],#distances相似度值
        )
        vector_results = []
        for text,meta,dist in zip(res['documents'][0],
                                  res['metadatas'][0],
                                  res['distances'][0]
                                  ):
            source=meta["source"]
            vector_results.append({"text": text,
                                   "source":meta["source"],
                                   "distance":dist,
                                   "chunk_id":make_chunk_hash(source,text)
                                   })
                                  
        return vector_results

def create_chunks(chunks):
        return BM25(chunks)

def BM25_bijiao(query_text:str,vector_results,bm25,top_k=20, final_top_k=20):
        
        bm25_results = bm25.query(query_text,top_k)
        
        results = rrf_fusion(
            vector_results,
            bm25_results,
            top_k= final_top_k,
        )

        return results
    
_rerank_model = None
def get_rerank():
    global _rerank_model #全局变量声明，用于函数内修改全局变量
    if _rerank_model is None:
        _rerank_model = Rerank()
    return _rerank_model

def rerank_results(query_text,results,top_k=4):
        if not results:
            return[]
        final_reuslt= get_rerank().rerank_re(
            query=query_text,
            rrf_result=results,
            top_k=top_k
        )
        return final_reuslt