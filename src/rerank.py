
import requests

from .config import RERANK_BACKEND,RERANK_MODEL,RERANK_USE_FP16,RERANK_TOP_N ,RERANK_API_URL,RERANK_API_KEY,RERANK_API_STYLE

RERANK_MIN_SCORE = 0.3

class Rerank:
    def __init__(self):
            self.backend = RERANK_BACKEND
            self.model = None
    def _load_model(self):

        if self.backend != "local":
                return

        if self.model is None:

            from FlagEmbedding import FlagReranker

            self.model = FlagReranker(
                RERANK_MODEL,
                use_fp16=RERANK_USE_FP16
                )

    def rerank_re(self,query,rrf_result,top_k=None):
        if not rrf_result:
            return []
        
        if top_k is None:
            top_k = RERANK_TOP_N
            
        if self.backend == "local":    
            return self._rerank_local(
                query,
                rrf_result,
                top_k
            )
        
        if self.backend == "api":
            return self._rerank_api(query,rrf_result,top_k)
        raise ValueError(f"未知的 RERANK_BACKEND：{self.backend}")   
    
    def _rerank_local(self,query,rrf_result,top_k):
        self._load_model()
        pairs = [[query,doc["text"]] for doc in rrf_result]
        scores = self.model.compute_score(pairs,normalize=True)
        if isinstance(scores,(int,float)):        #只有一条候选时返回标量
            scores = [scores]
        return self._merge(rrf_result,scores,top_k)
    
    def _rerank_api(self,query,rrf_result,top_K):
        if not RERANK_API_URL:
            raise ValueError("RERANK_API_URL 未配置")
        if not RERANK_API_KEY:
            raise ValueError("RERANK_API_API 未配置")
        
        docs = [doc["text"] for doc in rrf_result]
        headers = {
            "Authorization":f"Bearer {RERANK_API_KEY}",
            "Content-Type":"application/json",
        }
        
        if RERANK_API_STYLE == "dashscope":
            playoad ={
                "model":RERANK_MODEL,
                "input":{"query":query,"document":docs},
                "parameters":{"top_n":len(docs),"return_documents":False},
            }
            resp = requests.post(RERANK_API_KEY,json = payload,headers = headers,time_out=30)
            resp.raise_for_status()
            rows = resp.json()["output"]["results"]
            
        else:
            payload = {
                "model":RERANK_MODEL,
                "query":query,
                "documents":docs,
                "top_n":len(docs),
                "return_documents":False
                
            }
            resp = requests.post(RERANK_API_URL,json=payload,headers=headers,timeout=30)
            resp.raise_for_status()
            rows = resp.json()["results"]
        
        scores = [0,0] *len(docs) 
        
        for row in rows:
            scores[row["index"]] = float(row["relevance_score"])
        return self._merge(rrf_result,scores,top_K)
    
    @staticmethod
    def _merge(rrf_result,scores,top_k):
        merge = []
        
        for doc,score in zip(rrf_result,scores):
            merge.append({**doc,"rerank_score":float(score)})
        merge.sort(key= lambda x:x["rerank_score"],reverse=True)
        
        filtered = [d for d in merge if d["rerank_score"] >= RERANK_MIN_SCORE]
        return (filtered or merge)[:top_k]
            