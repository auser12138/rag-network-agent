import jieba
from rank_bm25 import BM25Okapi
from .chunk_id import make_chunk_hash

def tokenize(text):
    return  [
        word.strip() for word in jieba.lcut(text) if word.strip()
        #jieba.lcut()是分词的函数，返回一个列表，列表中是分词后的词语
    ]
    
class BM25:
    def __init__(self,chunks):
        self.documents = chunks
        
        tokenize_docunments = [
            tokenize(doc.content) for doc in chunks
            #对每个文档的内容进行分词，返回一个列表，documents中是分词后的词语
        ]
        self.BM25 = BM25Okapi(tokenize_docunments)
        #建立索引，对分词内容进行高频统计等
        
#对用户提问进行分词
    def query(self,query_text:str,top_k:int):
        query_tokens = tokenize(query_text)
        scores = self.BM25.get_scores(query_tokens)
#对每个文档的分词内容进行评分，返回一个列表，列表中是每个文档的索引       
        ranked_indices = sorted (range(len(scores)), key =lambda i: scores[i], reverse=True)[:top_k]
 #doc的内容为排序后的索引从document中拿出对应的原始文本内容       
        result = []
        for index in ranked_indices:
            doc =self.documents[index]
            
            result.append(
            {
                "text": doc.content,
                "source": doc.source,
                "bm25_score": scores[index],
                "chunk_id":make_chunk_hash(doc.source,doc.content)
            }
        )
        return result