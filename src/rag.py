#用户进行提问处，将检索结果返回到my_llm中，再返回my_llm获得的回答
from .jiansuo import xiangsibijiao,rerank_results,BM25_bijiao   
from .my_llm import answer
from .bm_25 import BM25

def create_chunks(chunks):
    return BM25(chunks)

def ask(query_text,bm25,
        retrieve_top_k=20,
        rrf_top_k=20,
        final_top_k=4,
        ):
    vector_results = xiangsibijiao(query_text,top_k = retrieve_top_k)
    
    # 2. BM25 + RRF Top 20
    rrf_results = BM25_bijiao(
        query_text=query_text,
        vector_results=vector_results,
        bm25=bm25,
        top_k=retrieve_top_k,
        final_top_k=rrf_top_k,
    )

    print(f"RRF 返回：{len(rrf_results)}")

    # 3. BGE Reranker Top 4
    final_results = rerank_results(
        query_text=query_text,
        results=rrf_results,
        top_k=final_top_k,
    )
    


    return answer(question=query_text,items = final_results)

    
    

