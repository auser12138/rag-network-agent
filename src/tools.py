#工具库
from .jiansuo import xiangsibijiao,BM25_bijiao
from .tool import registry
from .config import TOOL_TOP_K,TOOP_CHUNK_CHARS

def create_knowledge(bm25):
    def knowledge(query):
        vector_results = xiangsibijiao(quer_text=query,top_k = 20)
        results = BM25_bijiao(
            query_text=query,
            vector_results=vector_results,
            bm25=bm25,
            top_k =20,
            final_top_k=TOOL_TOP_K,
        )
    
        if not results:
            return {"found":False,
                    "message":"知识库中未找到相关资料"
                    }  
        
        know = []
        for i,item in enumerate(results,start=1):
            text = item["text"]
            if len(text) >TOOP_CHUNK_CHARS:
                text = text[:TOOP_CHUNK_CHARS]
            
            know.append(                
                f"[资料{i}]\n"
                f"来源：{item['source']}\n"
                f"内容：{text}"
                )
        return "\n".join(know)
    
    registry.regist(
        name="knowledge",
        description="查询企业知识库内容文档，运维手册",
        func=knowledge
    )
    return  knowledge