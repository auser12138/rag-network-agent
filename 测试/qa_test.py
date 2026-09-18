from src.xiangliangku import get_biao
from src.repos_sql import list_file
from collections import Counter

biao = get_biao("kb1")
print("Chroma 总块数：", biao.count())

res = biao.get(include=["metadatas"])
for s,n in Counter(m["source"] for m in res["metadatas"]).items():
    print(f"  {s}: {n} 块")

print("MySQL active：", [r["source"] for r in list_file("kb1")])