import os
from  pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent #创建根目录，——file——指当前文件地址，parent取上一级目录
load_dotenv(BASE_DIR / ".env")#加载env环境变量

#大模型
llm_Api_Key = os.getenv("llm_Api_Key","")
llm_Api_URL = os.getenv("llm_Api_URL","https://api.deepseek.com")
llm_Api_mode = os.getenv("llm_Api_mode","deepseek-chat")

#向量化模型
EMBED_MODEL=  os.getenv("EMBED_MODEL","text-embedding-v4")
EMBED_BASE_URL= os.getenv("EMBED_BASE_URL","https://dashscope.aliyuncs.com/compatible-mode/v1")
EMBED_API_KEY= os.getenv("EMBED_API_KEY","")

#切分
CHUNK_SIZE= int(os.getenv("CHUNK_SIZE","400"))
CHUNK_OVERLAP=int(os.getenv("CHUNK_OVERLAP","50"))

#检索
top_k = int(os.getenv("TOP_K", "4"))

#重排
RERANK_BACKEND = os.getenv("RERANK_BACKEND", "local")   # local=本地模型 / api=云端接口 / none=关闭重排
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")  # 本地填HF模型名或本地目录；API填服务商模型名
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "4"))
RERANK_API_URL = os.getenv("RERANK_API_URL", "https://api.siliconflow.cn/v1/rerank")
RERANK_API_KEY = os.getenv("RERANK_API_KEY", "")
RERANK_USE_FP16 = os.getenv("RERANK_USE_FP16", "false").lower() == "true"
RERANK_API_STYLE = os.getenv("RERANK_API_STYLE", "cohere")  # cohere=SiliconFlow/Jina/TEI，dashscope=阿里百炼

#数据库

MYSQL_HOST = os.getenv("MYSQL_HOST", "192.168.1.4")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "myuser")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "ubuntu")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "mydb")
MYSQL_CHARSET = "utf8mb4"

#工具输出
TOOL_TOP_K = int(os.getenv("TOOL_TOP_K","6"))
TOOP_CHUNK_CHARS = int(os.getenv("TOOP_CHUNK_CHARS","800"))
OBSERVATION_MAX = int(os.getenv("OBSERVATION_MAX", "4000"))

#路径
data_dir = BASE_DIR / "data"
db_dir = BASE_DIR /"db"
COLLECTION_NAME = "kb1"
