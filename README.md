# 网络运维故障诊断 Agent

基于 RAG 与 ReAct Agent 的网络运维知识库问答系统。输入故障现象，系统检索运维手册并给出排查方案，支持多轮追问、流式输出与答案出处追溯

## 项目简介

网络排障的痛点在于：排查经验散落在设备手册、故障案例和个人笔记里，新人定位一个接口 Down 的问题可能要翻半小时文档。本项目把这些资料统一入库，做成一个能对话的排障助手——**输入现象，返回带出处的排查步骤**。

与"把文档丢给大模型"的做法不同，这个项目重点解决三件事：

1. **检索要准**——单一向量检索对"接口 Down""CRC errors"这类专有名词召回不准，因此引入 BM25 关键词召回并用 RRF 融合
2. **回答要可信**——所有结论必须能追溯到具体资料，资料没有的内容直接拒答，不允许模型用预训练知识补充
3. **入库要幂等**——文档会反复修改，重复入库会产生脏数据，因此用文件哈希做增量更新与删除清理

---

## 架构

```
                    ┌─────────────────────────────────────────┐
   浏览器  ────────► │  FastAPI                                │
   (HTTPS/HTTP)     │   /chat/stream  SSE 事件流               │
                    │   /verify 口令校验                       │
                    └───────────────┬─────────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────────┐
                    │  ReAct Agent（手写，无框架）             │
                    │   Thought → Action → Observation 循环    │
                    │   多轮记忆 / 容错 / 输出截断             │
                    └───────────────┬─────────────────────────┘
                                    │ 工具调用
                    ┌───────────────▼─────────────────────────┐
                    │  knowledge 工具                         │
                    │   向量检索 ─┐                           │
                    │            ├─► RRF 融合 ─► 取 Top-K     │
                    │   BM25   ──┘                            │
                    └───────────────┬─────────────────────────┘
                                    │
              ┌─────────────────────┴─────────────────────┐
              │                                           │
      ┌───────▼────────┐                        ┌─────────▼────────┐
      │  ChromaDB      │                        │  MySQL           │
      │  块 + 向量      │                        │  文件登记簿       │
      └───────▲────────┘                        └─────────▲────────┘
              │                                           │
              └───────────────┬───────────────────────────┘
                              │
                    ┌─────────▼─────────────────────────────┐
                    │  同步管道 sync()                       │
                    │   扫描 → 文件哈希 → 判定 → 增量写入     │
                    │   新增 / 跳过 / 更新 / 删除             │
                    └───────────────────────────────────────┘
```

---

## 技术栈

| 层次 | 技术 |
|---|---|
| 大模型 | DeepSeek API（OpenAI 兼容接口） |
| 向量化 | 通义千问 text-embedding-v4（批量调用） |
| 向量库 | ChromaDB（本地持久化） |
| 关键词检索 | BM25（rank_bm25）+ jieba 中文分词 |
| 融合排序 | RRF（Reciprocal Rank Fusion，k=60） |
| 精排 | BGE Reranker v2-m3（cross-encoder，支持本地/API 切换） |
| Agent | 手写 ReAct（工具注册表 + 解析器 + 执行循环，不依赖框架） |
| 服务 | FastAPI + SSE + Pydantic |
| 数据库 | MySQL 8（文件登记簿） / SQLite（可选） |
| 前端 | 原生 HTML + JS（fetch 读取 SSE 流） |
| 部署 | 阿里云 ECS + systemd + Nginx（规划中） |

---

## 核心实现

### 1. 混合检索与 RRF 融合

单一向量检索对专有名词和精确关键词不敏感（"CRC errors" 的语义向量可能被大量无关内容淹没）。因此采用双路召回：

- 向量检索（语义）：召回 20 条
- BM25（关键词）：召回 20 条
- RRF 融合：不依赖两路分数的量纲，只用排名计算 `score = Σ 1/(k + rank)`，融合后取 Top-K

### 2. 精排（Reranker）

双塔向量模型（bi-encoder）对 query 和 doc 分别编码，缺少交互；cross-encoder 把 query 和 doc 拼在一起编码，精度高但只能对少量候选计算。因此对 RRF 的 Top-20 做交叉编码精排，取 Top-4 送生成。

精排后端做成可切换：

```ini
RERANK_BACKEND=local   # FlagEmbedding 本地推理（需 2.3GB 模型）
RERANK_BACKEND=api     # 云端接口（同一模型，零显存占用）
RERANK_BACKEND=none    # 关闭精排
```

本地模式实现了懒加载单例（避免每次调用重新加载 2.3GB 权重）和 GPU/CPU 自适应 fp16。

### 3. 手写 ReAct Agent

不依赖 LangChain，从零实现：

- **工具注册表**：用装饰器把函数注册到 `{名称: {描述, 函数}}` 的表里，工具描述渲染进系统提示
- **输出解析器**：正则提取 `Action` / `Action Input`，JSON 解析参数
- **执行循环**：Thought → Action → Observation 回填 → 再决策，最多 5 步
- **多层容错**：格式错误 / 工具不存在 / 参数错误 / 工具执行异常，均回填为 Observation 让模型自我纠正

**防伪造机制**（实践中发现模型会伪造成完整的 ReAct 剧本）：

1. `stop=["\nObservation:"]` —— 从协议层禁止模型写出观测结果
2. 解析器"动作优先"——若同时出现 Action 和 Final Answer，以动作为准
3. 提示词明确"每次只输出一个步骤"

### 4. 幂等入库（文件哈希 + 登记簿）

用 MySQL 记录每个文件的 SHA256，同步时比对：

| 情况 | 动作 |
|---|---|
| 库里无记录 | 新增：切分 → 向量化 → 写 Chroma → 登记 |
| 哈希一致 | 跳过（不读文本、不切分、不调 embedding） |
| 哈希变化 | 更新：删旧块 → 写新块 → 更新登记 |
| 磁盘已删除 | 清理：删 Chroma 块 → 标记 `deleted` |

**块级 ID 由"来源 + 内容哈希"决定**（`source#hash16`），保证同一文件内重复段落只存一份，而不同文件的相同内容各存一份（出处不丢失、删除不误伤）。

### 5. 服务化与流式输出

FastAPI 提供 `/chat`（同步）和 `/chat/stream`（SSE）两个接口。**Agent 的流式采用"事件流"而非"token 流"**：ReAct 循环中一轮输出是 Action 还是 Final Answer 事先不确定，无法逐 token 推送，因此按阶段推送：

```
event: status   {"msg": "正在调用工具：knowledge"}
event: answer   {"text": "交换机接口 Down 时，先检查..."}
event: done
```

### 6. 输出长度控制

三层截断，防止 Observation 撑爆上下文：

- `TOOL_TOP_K`：工具返回几条资料（默认 6）
- `TOOL_CHUNK_CHARS`：每条资料最多多少字（默认 800）
- `OBSERVATION_MAX`：单次 Observation 总长上限（默认 4000 字，agent 层兜底）

---

## 快速开始

### 1. 环境准备

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置 `.env`

```ini
llm_Api_Key=你的DeepSeek密钥
EMBED_API_KEY=你的通义密钥
MYSQL_HOST=127.0.0.1
MYSQL_USER=myuser
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=mydb
RERANK_BACKEND=none             # 云上不装 torch
ACCESS_CODE=你的访问口令
```

### 3. 建表（首次）

```sql
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(512) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    chunk_count INT NOT NULL DEFAULT 0,
    collection VARCHAR(64) NOT NULL DEFAULT 'kb1',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_source_collection (source, collection)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4. 同步知识库

```bash
python -c "from src.sync import sync; print(sync())"
```

### 5. 启动服务

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/`。

**服务器部署**（systemd 常驻）：

```bash
systemctl restart rag-agent      # 重启
journalctl -u rag-agent -f       # 看日志
```

---

## 设计取舍

### 为什么手写 ReAct 而不用 LangChain？

先手写一遍才能理解 Agent 的本质：模型只输出"意图文本"，真正执行的是代码，循环的关键是**把工具结果回填**。框架会把这些细节封装掉——用框架能跑通，但被问到"你的 Observation 怎么回填的"就答不上来。手写完成后，再用框架是权衡，而不是依赖。

### 为什么 RRF 而不是加权求和？

向量距离和 BM25 分数**量纲不可比**（一个是余弦距离，一个是词频统计），加权求和需要归一化，而归一化的方式本身又引入超参。RRF 只用排名，天然规避了这个问题，代价是丢掉了分数差异的绝对信息。

### 为什么 MySQL + Chroma 双存储，而不是只用 Chroma metadata？

文件级问题（"库里有哪些文件""这个文件什么时候更新的"）用 SQL 是一句话，用 Chroma 要遍历所有块的 metadata。而且**唯一性约束**是关键——Chroma 的 metadata 没有唯一键，无法从数据结构上阻止重复登记。

### 为什么 `db/` 不进 git？

向量库是**从语料派生出来的产物**，不是源码。把它提交进 git 会带来三个问题：二进制文件导致仓库膨胀、每次入库产生巨大 diff、换机器后还必须重新对齐。现在只要 `git clone` + 一次同步就能重建全部数据。

### 为什么 Agent 的流式用事件流而不是 token 流？

ReAct 循环里，模型一轮的输出可能是 Action（内部推理，不该给用户看），也可能是 Final Answer。**在模型吐完之前无法判断**，所以逐 token 推送会暴露内部推理过程。改用阶段事件流后，用户能立刻看到"正在检索"，首字感知延迟从十几秒降到 1 秒内。

### 为什么用文件哈希而不是修改时间做增量判定？

修改时间不可靠：`git checkout`、文件复制、解压都会更新时间但不改变内容。哈希反映的是**内容是否真的变了**，这才是去重的正确依据。代价是每次同步都要读一遍文件字节（但远快于切分和 embedding）。

### 为什么精排做成可切换后端？

本地部署 BGE Reranker 要 2.3GB 权重 + 2~3GB 内存，而目标部署环境的免费实例只有 4GB 内存。做成可切换后，同一份代码可以本地跑模型（面试演示"我部署过"），也可以走 API（线上零显存）。**同一模型、同样口径，只改一个配置。**

---

## 已知限制

- **尚未做量化评测**：目前没有标准测试集和命中率数据，"检索质量提升"缺少可验证的数字支撑（规划中）
- **Agent 路径未接入精排**：精排已实现并在纯 RAG 路径中生效，Agent 的工具路径当前直接使用 RRF 结果（云环境未装 torch）
- **会话存储在进程内存**：服务重启后历史丢失，且不支持多进程部署（规划迁移到 Redis）
- **无接口限流**：当前只有访问口令，没有按 IP 的频率限制
- **语料规模较小**：目前约 80 个知识块，检索策略的优势在更大规模语料上更明显
- **未容器化**：暂无 Dockerfile，部署依赖手动配置环境
- **无 HTTPS 与域名**：当前通过 IP + 端口访问（国内服务器使用域名需备案）

## 后续计划

- [ ] 构建 30 题评测集，量化混合检索与精排的命中率提升
- [ ] 将精排接入 Agent 工具路径（走 API 后端）
- [ ] 会话迁移到 Redis，支持多进程与持久化
- [ ] 加入接口限流与调用日志
- [ ] 扩充语料规模至数千块
- [ ] 接入诊断工具（ping / DNS / 端口探测 / 日志读取），从"查文档"走向"现场取证"
- [ ] Docker 化 + Nginx 反代 + HTTPS
```

---
