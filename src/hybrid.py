

def rrf_fusion(vector_results,bm25_results,top_k,k=60):
    scores ={}
    documents ={}
    
    #计算向量检索结果的RRF分数
    for rank, item in enumerate(vector_results, start = 1):
        doc_id  = item['chunk_id']
        
        scores[doc_id] = scores.get(doc_id,0)+1/(k+rank) 
        
        documents.setdefault(doc_id,item)
    #计算BM25检索结果的RRF分数
    for rank, item in enumerate(bm25_results, start = 1):
        doc_id  = item['chunk_id']
        scores[doc_id] = scores.get(doc_id,0)+1/(k+rank) 
        
        documents.setdefault(doc_id,item)
    #根据RRF分数对文档进行排序
    ranked_docs = sorted(scores.items(), key =lambda x : x[1], reverse = True)
    
    
    result = []
    for doc_id,score in ranked_docs[:top_k]:
        item = documents[doc_id].copy()
        #copy将document的内容复制粘贴，并创建一个新字典将内容给item
        item['rrf_score'] = score
        result.append(item)
    return result
        
 #提问的检索，与向量和bm25都对比检索内容，然后rrf进行对比       