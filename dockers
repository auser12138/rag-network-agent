FROM python:3.12-slim

# 时区 + Python 运行参数
ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 先装依赖：requirements 不变时这层会被缓存，不重复安装
COPY requirements.txt .
RUN pip install --no-cache-dir \
      -i https://mirrors.aliyun.com/pypi/simple/ \
      -r requirements.txt

# 再复制代码（代码改动不会导致依赖重装）
COPY src/ ./src/
COPY static/ ./static/
COPY api.py .

EXPOSE 8000

CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8000"]