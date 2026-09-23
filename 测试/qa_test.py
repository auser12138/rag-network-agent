"""PDF 提取 + 清洗验证

用法：
    python 测试/check_pdf.py <pdf路径>
    python 测试/check_pdf.py <pdf路径> --save      # 把提取结果存成 txt 便于对比

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
from src.cleaner import clean_text


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
    raw_all = []
    clean_all = []
    checked = min(args.pages, n)
    
    for i, page in enumerate(reader.pages[:checked], start=1):
        raw = page.extract_text() or ""
        cleaned = clean_text(raw, merge_lines=True)      #PDF 开启断行合并
        raw_all.append(raw)
        clean_all.append(cleaned)
        
        print(f"===== 第 {i} 页 =====")
        print(f"原始提取：{len(raw)} 字  →  清洗后：{len(cleaned)} 字")
        if raw:
            drop = (1 - len(cleaned) / len(raw)) * 100 if raw else 0
            print(f"减少了 {drop:.0f}%（去掉页眉页脚/页码/多余空行）")
        print()
    
    # ---------------- ③ 判断类型 ----------------
    total_raw = sum(len(t) for t in raw_all)
    avg = total_raw / checked if checked else 0
    print("=" * 50)
    print(f"前 {checked} 页平均每页 {avg:.0f} 字")
    if avg < 50:
        print("⚠️ 疑似【扫描型 PDF】：提取不到文字，需要 OCR")
    elif avg < 300:
        print("🟡 文字偏少：可能图文混排，或提取质量一般")
    else:
        print("✅ 【文本型 PDF】：可以直接提取")
    print("=" * 50)
    
    # ---------------- ④ 样本 ----------------
    if clean_all and clean_all[0]:
        print("\n清洗后第 1 页样本（前 400 字）：")
        print("-" * 50)
        print(clean_all[0][:400])
        print("-" * 50)
    
    # ---------------- ⑤ 保存 ----------------
    if args.save:
        out = path.with_suffix(".extracted.txt")
        out.write_text("\n\n".join(clean_all), encoding="utf-8")
        print(f"\n已保存：{out}")


if __name__ == "__main__":
    main()