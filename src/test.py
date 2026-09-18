from src.jiansuo import xiangsibijiao
from src.bootstrap import get_bm25

q = "接口down BGP邻居down 丢包 联合排查顺序"

print("=== 向量 top10 ===")
for i,r in enumerate(xiangsibijiao(q,top_k=10),1):
    print(f"{i}. 距离={r['distance']:.4f}  {r['source']}  {r['text'][:35]}")

print("\n=== BM25 top10 ===")
bm = get_bm25("kb1")
for i,r in enumerate(bm.query(q,10),1):
    print(f"{i}. 分数={float(r['bm25_score']):.3f}  {r['source']}  {r['text'][:35]}")