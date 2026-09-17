# 文本切分：把长文档切成小块，相邻块有重叠
from .lodaer import Dacome


class RecursiveTextSplitter:
    """递归切块器：先按分隔符从大到小切，切不动就按字符硬切。"""

    def __init__(self, chunk_size=500, chunk_overlap=50, separators=None):
        """三个参数：
        - chunk_size：每块最多多少字
        - chunk_overlap：相邻两块重叠多少字（避免一句话被切断）
        - separators：优先按什么切，从大到小排列（先段落、再句号、最后空格）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "！", "？", ".", "?", "!", " "]

    def splitter_text(self, text):
        """把一段长文本切成小块，返回块列表。"""
        text = text.strip()
        # 情况 1：文本本身就够短，直接当一整块
        if len(text) <= self.chunk_size:
            return [text]

        # 情况 2：按分隔符从大到小逐个试
        for sep in self.separators:
            if sep not in text:            # 文本里没有这个分隔符，换下一个
                continue
            parts = text.split(sep)        # 用这个分隔符切开
            if len(parts) <= 1:            # 没切开，换下一个
                continue

            chunks, current = [], ""       # chunks：最终结果；current：正在拼的块
            for part in parts:
                if not part:               # 跳过空片段（比如结尾的分隔符）
                    continue
                # 把当前片段拼进 current 还不超长，就继续拼
                if len(current) + len(part) + len(sep) <= self.chunk_size:
                    current += part + sep
                else:
                    # 拼进去就超长了：先把拼好的 current 存成一块
                    if current:
                        chunks.append(current.strip())
                    # 关键修复：片段本身就超长时，按字符硬切，绝不递归
                    if len(part) > self.chunk_size:
                        chunks.extend(self._hard_split(part))
                        current = ""
                    else:
                        current = part + sep   # 否则用它开一个新块
            if current:                      # 循环结束，存下最后一块
                chunks.append(current.strip())
            return chunks

        # 情况 3：所有分隔符都不起作用，按字符硬切
        return self._hard_split(text)

    def _hard_split(self, text):
        """按固定字符数硬切，步长 = 块长 - 重叠，实现重叠。"""
        step = max(1, self.chunk_size - self.chunk_overlap)
        return [text[i:i + self.chunk_size] for i in range(0, len(text), step)]

    def split_Dacome(self, documents):
        """把多个文档（Dacome 列表）都切成块，每块保留出处 source。"""
        resul = []
        for doc in documents:
            for i, chunk in enumerate(self.splitter_text(doc.content)):
                resul.append(Dacome(content=chunk, source=doc.source,file_hash=doc.file_hash,))
        return resul