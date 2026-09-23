"""PDF 提取 + 清洗验证

用法：
    python 测试/qa_test.py <pdf路径>
    python 测试/qa_test.py <pdf路径> --save      # 把提取结果存成 txt 便于对比

输出三段：
  ① 诊断：文本型还是扫描型
  ② 清洗前后对比：看 cleaner 到底去掉了什么
  ③ 前几页样本：肉眼判断提取质量
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pypdf
from src.clear import clean_text, is_toc_page, toc_line_ratio


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("--pages", type=int, default=5, help="检查前几页")
    parser.add_argument("--save", action="store_true", help="保存提取结果")
    args = parser.parse_args()
    
    path = Path(args.pdf)
    if not path.exists():
        print(f"文件不存在：{path}")
        return
    
    # ---------------- ① 基础信息 ----------------
    reader = pypdf.PdfReader(str(path))
    n = len(reader.pages)
    print(f"文件：{path.name}")
    print(f"页数：{n}")
    print()
    
    # ---------------- ② 逐步提取 + 清洗 ----------------
    content_raw = []            # 正文页的原始字数（目录页不算，否则平均字数被拉低）
    clean_all = []
    toc_pages = []
    checked = min(args.pages, n)
    
    for i, page in enumerate(reader.pages[:checked], start=1):
        raw = page.extract_text() or ""
        cleaned = clean_text(raw, merge_lines=True)      #PDF 开启断行合并
        
        print(f"===== 第 {i} 页 =====")
        #目录页整页丢弃是预期行为，不是"清洗掉了 100% 内容"
        if is_toc_page(raw):
            toc_pages.append(i)
            print(f"目录页（点线行占比 {toc_line_ratio(raw):.0%}）→ 整页跳过")
            print()
            continue
        
        content_raw.append(len(raw))
        clean_all.append(cleaned)
        print(f"原始提取：{len(raw)} 字  →  清洗后：{len(cleaned)} 字")
        if raw:
            drop = (1 - len(cleaned) / len(raw)) * 100 if raw else 0
            print(f"减少了 {drop:.0f}%（去掉页眉页脚/页码/多余空行）")
        print()
    
    # ---------------- ③ 判断类型 ----------------
    total_raw = sum(content_raw)
    content_pages = len(content_raw)
    avg = total_raw / content_pages if content_pages else 0
    print("=" * 50)
    if toc_pages:
        print(f"前 {checked} 页里有 {len(toc_pages)} 页目录（第 {toc_pages[0]}~{toc_pages[-1]} 页），已排除")
    if content_pages == 0:
        print("⚠️ 前几页全是目录，还没看到正文，请加大 --pages 再看")
    else:
        print(f"前 {checked} 页里正文页 {content_pages} 页，平均每页 {avg:.0f} 字")
        if avg < 50:
            print("⚠️ 疑似【扫描型 PDF】：提取不到文字，需要 OCR")
        elif avg < 300:
            print("🟡 文字偏少：可能图文混排，或提取质量一般")
        else:
            print("✅ 【文本型 PDF】：可以直接提取")
    print("=" * 50)
    
    # ---------------- ④ 样本 ----------------
    samples = [c for c in clean_all if c.strip()]
    if samples:
        print("\n清洗后第 1 页正文样本（前 400 字）：")
        print("-" * 50)
        print(samples[0][:400])
        print("-" * 50)
    
    # ---------------- ⑤ 保存 ----------------
    if args.save:
        out = path.with_suffix(".extracted.txt")
        out.write_text("\n\n".join(clean_all), encoding="utf-8")
        print(f"\n已保存：{out}")


if __name__ == "__main__":
    main()
