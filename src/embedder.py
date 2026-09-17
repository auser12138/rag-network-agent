#向量化，调用分块好的文本内容从xiangliangku文件中调用
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 从 .env 读 Key，别写死在代码里

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-v4")
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
EMBED_API_KEY = os.getenv("EMBED_API_KEY", "")

_client = None


def get_client():
    """获取并缓存客户端，避免每次调用都重新创建。"""
    global _client
    if _client is None:
        _client = OpenAI(api_key=EMBED_API_KEY, base_url=EMBED_BASE_URL)
    return _client


def embed_texts(texts, batch_size=10):
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"正在向量化 {i + len(batch)}/{len(texts)} ...")
        resp = get_client().embeddings.create(model=EMBED_MODEL, input=batch)
        all_vectors.extend(item.embedding for item in resp.data)
    return all_vectors

def embed_text(text):
    """把单条文本转成向量。提问时用。"""
    return embed_texts([text])[0]

