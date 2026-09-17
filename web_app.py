"""网络运维故障诊断 Agent —— 网页入口
运行：venv\\Scripts\\streamlit run web_app.py
"""
import re
import streamlit as st

from src.bootstrap import setup,get_bm25
from src.agent import run_agent
from src.sync import sync
from src.config import COLLECTION_NAME
from src.xiangliangku import get_biao

st.set_page_config(
    page_title="网络运维故障诊断 Agent",
    page_icon=":material/network_check:",
    layout="wide",
)


@st.cache_resource
def init_runtime():
    """启动装配：从向量库重建 BM25 索引 + 注册工具（整个进程只跑一次）"""
    setup(COLLECTION_NAME)
    return True


init_runtime()


def extract_sources(history):
    """从 Observation 消息里提取本次引用到的资料出处"""
    sources = []
    for msg in history:
        if msg["role"] == "user" and msg["content"].startswith("Observation:"):
            for s in re.findall(r"来源：(.+)",msg["content"]):
                s = s.strip()
                if s and s not in sources:
                    sources.append(s)
    return sources


# ---------------- 侧边栏：知识库管理 ----------------
with st.sidebar:
    st.subheader("知识库")
    st.caption(f"集合：{COLLECTION_NAME}")
    st.metric("向量块数",get_biao(COLLECTION_NAME).count())
    
    if st.button("同步知识库",icon=":material/sync:"):
        with st.spinner("正在同步……"):
            result = sync(collection=COLLECTION_NAME)
            get_bm25(COLLECTION_NAME,force=True)      #重建索引，让新内容立刻能被检索
        st.success(
            f"新增 {result['added']} / 更新 {result['updated']} / "
            f"跳过 {result['skipped']} / 删除 {result['deleted']}"
        )
    
    if st.button("清空对话",icon=":material/delete:"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()


# ---------------- 主区：对话 ----------------
st.title("网络运维故障诊断 Agent")
st.caption("描述故障现象，Agent 会先检索知识库，再给出排查方案和引用出处。")

if "messages" not in st.session_state:
    st.session_state.messages = []      #给人看的问答对
if "history" not in st.session_state:
    st.session_state.history = []       #给 agent 的完整记录（含工具调用过程）

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("描述你的故障现象，例如：交换机接口 Down 怎么排查")

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("正在检索知识库并分析……"):
            answer,history = run_agent(prompt,st.session_state.history)
        st.markdown(answer)
        
        sources = extract_sources(history)
        if sources:
            with st.expander("引用的资料"):
                for s in sources:
                    st.markdown(f"- {s}")
    
    #历史裁剪：保留 system + 最近 12 条，防止越聊越慢
    if len(history) > 13:
        history = [history[0]] + history[-12:]
    st.session_state.history = history
    st.session_state.messages.append({"role":"assistant","content":answer})