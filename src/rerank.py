
from .config import RERANK_BACKEND,RERANK_MODEL,RERANK_USE_FP16,RERANK_TOP_N
class Rerank:
    def __init__(self):
            self.backend = RERANK_BACKEND
            self.model = None
    def _load_model(self):
        if self.model is None:       
            from FlagEmbedding import FlagReranker 
            if self.backend == "local":
                self.model = FlagReranker(RERANK_MODEL,use_fp16=RERANK_USE_FP16)
            elif self.backend == "api":
                raise NotADirectoryError("功能未实现")

    def rerank_re(self,query,rrf_result,top_k=None):
        self._load_model()
        if top_k is None:
            top_k = RERANK_TOP_N
        if self.backend == "local":    
            result = []
            texts = [(query,doc["text"]) for doc in rrf_result]

            
            scores = self.model.compute_score(texts,normalize=True)
            for doc,score in zip(rrf_result,scores):    
                result.append({
                **doc,
                "rerank_score" : score
            }  
            )
            result.sort(
                key=lambda x:x["rerank_score"],
                reverse=True,
            )
            return result[:top_k]
        
        if self.backend == "api":
            raise NotImplementedError(
                "当前还没有实现 API Rerank"
            )
            