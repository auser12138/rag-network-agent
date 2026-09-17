"""问答效果测试脚本

链路：向量检索 + BM25 -> RRF 融合 -> （可选）重排 -> 大模型生成回答
用法：python 测试/qa_test.py            # 跑默认题目
      python 测试/qa_test.py "你的问题"  # 跑指定问题

结果同时打印到屏幕，并写入 测试/qa_report.md（UTF-8），方便在编辑器里看中文。
"""

import sys
import time
import hashlib
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.jiaoyan import make_chunk_hash
from src.bm_25 import BM25
from src.config import (
    RERANK_API_KEY,
    RERANK_BACKEND,
    RERANK_TOP_N,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    top_k,
)
from src.jiansuo import BM25_bijiao, rerank_results, xiangsibijiao
from src.my_llm import answer
from src.xiangliangku import get_biao

DEFAULT_QUESTIONS = [
    "交换机接口显示 down，应该怎么排查？",
    "Linux 服务器怎么查看网卡状态和默认路由？",
    "接口出现大量 CRC 错误，需要检查哪些方面？",
    "公司年假有多少天？",
]

RETRIEVE_TOP_K = 20   # 向量/BM25 各自召回多少
RRF_TOP_K = 20        # RRF 融合后留多少


class Chunk:
    """BM25 只需要 .content / .source，用轻量对象承接向量库里的块。"""

    def __init__(self, content: str, source: str):
        self.content = content
        self.source = source

    def __repr__(self):
        return f"Chunk({self.source}, {len(self.content)}字)"


def load_chunks():
    """从向量库里读出所有块，供 BM25 使用。"""
    res = get_biao().get(include=["documents", "metadatas"])
    return [
        Chunk(text, meta["source"])
        for text, meta in zip(res["documents"], res["metadatas"])
    ]


def rerank_enabled() -> bool:
    """重排是否可用：none 表示关闭；api 需要 Key；local 需要本地模型。"""
    if RERANK_BACKEND == "none":
        return False
    if RERANK_BACKEND == "api" and not RERANK_API_KEY:
        return False
    return True


def rrf_by_chunk(vec, bm_results, top_k=20, k=60):
    """块级 RRF 融合（对照用）。

    与 src/hybrid.py 的区别：
    1. 按“块”去重，而不是按 source（文件名）去重；
    2. 同一个块多次出现时保留排名更靠前（分数更高）的那条，不覆盖。
    """
    scores, docs = {}, {}
    for results in (vec, bm_results):
        for rank, item in enumerate(results, 1):
            key = make_chunk_hash(
                item["source"],
                item["text"]
                                )
            scores[key] = scores.get(key, 0) + 1 / (k + rank)
            docs.setdefault(key, item)          # 先到先得 = 保留最好名次的那条

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    result = []
    for key, score in ranked:
        item = dict(docs[key])
        item["rrf_score"] = score
        result.append(item)
    return result


def retrieve(question: str, bm25: BM25, final_top_k: int, mode: str = "current"):
    """返回 (最终资料, 诊断信息)。"""
    vec = xiangsibijiao(question, top_k=RETRIEVE_TOP_K)
    if mode == "fixed":
        bm_results = bm25.query(question, RETRIEVE_TOP_K)
        rrf = rrf_by_chunk(vec, bm_results, top_k=RRF_TOP_K)
    else:
        rrf = BM25_bijiao(
            query_text=question,
            vector_results=vec,
            bm25=bm25,
            top_k=RETRIEVE_TOP_K,
            final_top_k=RRF_TOP_K,
        )
    if rerank_enabled():
        items = rerank_results(question, rrf, top_k=final_top_k)
        used_rerank = True
    else:
        items = rrf[:final_top_k]
        used_rerank = False

    diag = f"向量 {len(vec)} 条 -> RRF {len(rrf)} 条 -> 最终 {len(items)} 条"
    return items, {"used_rerank": used_rerank, "diag": diag, "vec": vec, "rrf": rrf}


def run(questions, mode="current"):
    chunks = load_chunks()
    print(f"[准备] 向量库共 {len(chunks)} 个块，来自 "
          f"{sorted({c.source for c in chunks})}")
    print(f"[准备] 切分参数 chunk_size={CHUNK_SIZE} overlap={CHUNK_OVERLAP}；"
          f"生成用 top_k={top_k}；重排={'开' if rerank_enabled() else '关'}；"
          f"融合方式={mode}")

    bm25 = BM25(chunks)
    lines = [f"# 问答效果测试报告（{mode}）", ""]
    lines.append(f"- 知识库块数：{len(chunks)}")
    lines.append(f"- 检索：向量 top{RETRIEVE_TOP_K} + BM25 top{RETRIEVE_TOP_K} -> RRF top{RRF_TOP_K}")
    lines.append(f"- 重排：{'启用' if rerank_enabled() else '未启用（RERANK_BACKEND=' + RERANK_BACKEND + '）'}")
    lines.append(f"- 生成：RAG 提示词 + 大模型，资料取前 {top_k} 条")
    lines.append("")

    for i, q in enumerate(questions, 1):
        print(f"\n===== 第 {i} 题：{q} =====")
        t0 = time.time()
        items, info = retrieve(q, bm25, final_top_k=top_k, mode=mode)
        t1 = time.time()
        result = answer(q, items)
        t2 = time.time()

        print(f"[检索] {info['diag']}  耗时 {t1 - t0:.2f}s")
        for j, it in enumerate(items, 1):
            print(f"  ({j}) {it['source']} | {it['text'][:60]!r}")
        print(f"[回答] 耗时 {t2 - t1:.2f}s")
        print(result["answer"])

        lines.append(f"## {i}. {q}")
        lines.append("")
        lines.append(f"检索：{info['diag']}；检索耗时 {t1 - t0:.2f}s，生成耗时 {t2 - t1:.2f}s")
        lines.append("")
        lines.append("检索过程诊断：")
        lines.append("")
        lines.append("向量检索 top3：")
        for j, it in enumerate(info["vec"][:3], 1):
            lines.append(f"  {j}. `{it['source']}`（距离 {it['distance']:.4f}）：{' '.join(it['text'].split())[:60]}")
        lines.append("")
        lines.append("BM25 检索 top3：")
        for j, it in enumerate(bm25.query(q, 3), 1):
            lines.append(f"  {j}. `{it['source']}`（分数 {it['bm25_score']:.4f}）：{' '.join(it['text'].split())[:60]}")
        lines.append("")
        lines.append("命中的资料：")
        lines.append("")
        for j, it in enumerate(items, 1):
            score = it.get("rerank_score", it.get("rrf_score"))
            text = " ".join(it["text"].split())
            lines.append(f"{j}. `{it['source']}`（分数 {score:.4f}）：{text[:160]}")
        lines.append("")
        lines.append("回答：")
        lines.append("")
        lines.append(result["answer"] or "（空回答）")
        lines.append("")

    out = ROOT / "测试" / f"qa_report_{mode}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[报告] 已写入 {out}")


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = "fixed" if "--fixed" in args else "current"
    questions = [a for a in args if not a.startswith("--")]
    run(questions if questions else DEFAULT_QUESTIONS, mode=mode)
