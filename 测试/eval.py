"""检索效果评测：对比三种配置的 Top-K 命中率和 MRR

用法：
    python 测试/eval.py                    # 用默认评测集
    python 测试/eval.py --top-k 5          # 改 Top-K
    python 测试/eval.py --questions 测试/my_questions.json

评测集格式见 测试/eval_questions.json
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import COLLECTION_NAME
from src.jiansuo import xiangsibijiao,BM25_bijiao,get_rerank
from src.bootstrap import get_bm25


def hit_rank(results,expected_source):
    """返回正确答案在结果里的排名（从 1 开始）；没命中返回 None"""
    if expected_source == "NONE":
        return 1 if not results else None        #没有答案的题：返回空才算命中
    for i,item in enumerate(results,start=1):
        if item["source"] == expected_source:
            return i
    return None


def run_config(name,fn,questions,top_k):
    hits = 0
    rr_sum = 0.0
    details = []
    start = time.time()
    
    for q in questions:
        try:
            results = fn(q["question"],top_k)
        except Exception as e:
            results = []
            print(f"  [警告] {q['question'][:20]} 出错：{e}")
        
        rank = hit_rank(results,q["expected_source"])
        if rank:
            hits += 1
            rr_sum += 1.0 / rank
        details.append((q["question"],rank))
    
    cost = time.time() - start
    n = max(1,len(questions))
    return {
        "name":name,
        "hit_rate":hits / n,
        "mrr":rr_sum / n,
        "avg_ms":cost / n * 1000,
        "details":details,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions",default="测试/eval_questions.json")
    parser.add_argument("--top-k",type=int,default=4)
    parser.add_argument("--collection",default=COLLECTION_NAME)
    args = parser.parse_args()
    
    qpath = ROOT / args.questions
    if not qpath.exists():
        print(f"评测集不存在：{qpath}")
        print("格式参考：")
        print('[{"question":"...","expected_source":"xxx.md"}]')
        return
    
    questions = json.loads(qpath.read_text(encoding="utf-8"))
    print(f"评测集：{qpath.name}，共 {len(questions)} 题，Top-{args.top_k}\n")
    
    bm25 = get_bm25(args.collection)
    rerank = get_rerank()
    
    # ---------------- 三种配置 ----------------
    def vector_only(q,k):
        """配置①：只用向量检索"""
        return xiangsibijiao(quer_text=q,top_k=k)
    
    def hybrid(q,k):
        """配置②：向量 + BM25 → RRF"""
        vec = xiangsibijiao(quer_text=q,top_k=20)
        return BM25_bijiao(
            query_text=q,vector_results=vec,bm25=bm25,
            top_k=20,final_top_k=k,
        )
    
    def hybrid_rerank(q,k):
        """配置③：向量 + BM25 → RRF 20 → 精排 → k"""
        vec = xiangsibijiao(quer_text=q,top_k=20)
        rrf = BM25_bijiao(
            query_text=q,vector_results=vec,bm25=bm25,
            top_k=20,final_top_k=20,
        )
        return rerank.rerank_re(query=q,rrf_result=rrf,top_k=k)
    
    configs = [
        ("① 纯向量检索",vector_only),
        ("② 混合检索(RRF)",hybrid),
        ("③ 混合 + 精排",hybrid_rerank),
    ]
    
    results = []
    for name,fn in configs:
        print(f"跑配置 {name} …")
        results.append(run_config(name,fn,questions,args.top_k))
    
    # ---------------- 输出对比表 ----------------
    print("\n" + "=" * 56)
    print(f"{'配置':<18}{'Top-%d 命中率' % args.top_k:<16}{'MRR':<10}{'平均耗时'}")
    print("-" * 56)
    for r in results:
        print(f"{r['name']:<18}{r['hit_rate']:<16.1%}{r['mrr']:<10.3f}{r['avg_ms']:.0f} ms")
    print("=" * 56)
    
    # ---------------- 逐题明细 ----------------
    print("\n逐题明细（命中排名 / 未命中显示 ✗）：")
    for i,q in enumerate(questions,start=1):
        ranks = "  ".join(
            (f"{r['name'][:6]}={r['details'][i-1][1] or '✗'}")
            for r in results
        )
        print(f"  {i:>2}. {q['question'][:34]:<36} {ranks}")
    
    # ---------------- 保存报告 ----------------
    report = ROOT / "测试" / "eval_report.md"
    lines = [
        f"# 检索效果评测报告\n",
        f"- 评测集：{qpath.name}（{len(questions)} 题）",
        f"- Top-K：{args.top_k}",
        f"- 知识库：{args.collection}\n",
        f"| 配置 | Top-{args.top_k} 命中率 | MRR | 平均耗时 |",
        f"|---|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r['name']} | {r['hit_rate']:.1%} | {r['mrr']:.3f} | {r['avg_ms']:.0f} ms |")
    report.write_text("\n".join(lines),encoding="utf-8")
    print(f"\n报告已保存：{report}")


if __name__ == "__main__":
    main()