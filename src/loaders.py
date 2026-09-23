"""
  LangChain Loader  →  各格式 → 纯文本（+ 元数据）
  cleaner.clean_text →  去掉噪声
"""
from pathlib import Path

from langchain_community.document_loaders import (
    TextLoader,        #txt / md / log
    PyPDFLoader,       #pdf
    Docx2txtLoader,    #docx
    BSHTMLLoader,      #html / htm（基于 beautifulsoup4，比 unstructured 轻）
    CSVLoader,         #csv
)

from .cleaner import clean_text


LOADERS = {
    ".txt":  TextLoader,
    ".md":   TextLoader,
    ".log":  TextLoader,
    ".pdf":  PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".html": BSHTMLLoader,
    ".htm":  BSHTMLLoader,
    ".csv":  CSVLoader,
}

MERGE_LINE_SUFFIXES = {".pdf"}


def load_text(path: Path) -> str:
    """用对应 Loader 加载 → 拼成文本 → 用我们的规则清洗"""
    ext = path.suffix.lower()
    loader_cls = LOADERS.get(ext)
    if loader_cls is None:
        raise ValueError(f"不支持的格式：{ext}")
    
    if loader_cls is TextLoader:
        loader = TextLoader(str(path),encoding="utf-8",autodetect_encoding=True)
    else:
        loader = loader_cls(str(path))
    
    docs = loader.load()                    
    if not docs:
        raise ValueError("没有加载到内容")
    
    text = "\n\n".join(d.page_content for d in docs)
    if not text.strip():
        raise ValueError("内容为空（PDF 可能是扫描件，需要 OCR）")
    
    return clean_text(text,merge_lines=(ext in MERGE_LINE_SUFFIXES))


def load_metadata(path: Path):
    """取 Loader 附带的元数据（source / page 等）
    
    用途：PDF 可以知道当前内容是第几页，用于更精细的出处展示
    """
    ext = path.suffix.lower()
    loader_cls = LOADERS.get(ext)
    if loader_cls is None:
        return []
    try:
        return [d.metadata for d in loader_cls(str(path)).load()]
    except Exception:
        return []