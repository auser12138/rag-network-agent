from fastapi.responses import FileResponse, StreamingResponse
from contextlib import asynccontextmanager

from fastapi import FastAPI,HTTPException,Depends, Header
from pydantic import BaseModel

import json
from fastapi.responses import StreamingResponse
from src.agent import run_agent,run_agent_events
from src.bootstrap import setup
from src.agent import run_agent
from src.config import COLLECTION_NAME,ACCESS_CODE

_sessions = {}          # {session_id: history}，进程内存储


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动装配：重建 BM25 索引 + 注册工具（整个进程只跑一次）"""
    setup(COLLECTION_NAME)
    yield


app = FastAPI(title="网络运维故障诊断 Agent",lifespan=lifespan)

def check_access(x_access_code: str = Header(default="")):
    """校验访问口令：ACCESS_CODE 为空时不校验；不匹配返回 401"""
    if ACCESS_CODE and x_access_code != ACCESS_CODE:
        raise HTTPException(status_code=401,detail="访问口令不正确")


class VerifyRequest(BaseModel):
    code: str


@app.post("/verify")
def verify(req: VerifyRequest):
    """只校验口令，供前端登录使用"""
    if ACCESS_CODE and req.code != ACCESS_CODE:
        raise HTTPException(status_code=401,detail="访问口令不正确")
    return {"ok":True}


class ChatRequest(BaseModel):
    question: str                        #用户问题
    session_id: str = "default"          #会话标识，不传就是默认会话


class ChatResponse(BaseModel):
    answer: str
    session_id: str


@app.get("/health")
def health():
    
    return {"status":"ok","collection":COLLECTION_NAME}

@app.get("/")
def index():
    """返回聊天页面（静态 HTML）"""
    return FileResponse("static/index.html")


@app.post("/chat",response_model=ChatResponse,dependencies=[Depends(check_access)])
def chat(req: ChatRequest):
    """问答接口（同步版，写完这一版再考虑流式）"""
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400,detail="question 不能为空")
    
    history = _sessions.get(req.session_id,[])
    
    try:
        answer,history = run_agent(question,history)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{type(e).__name__}: {e}")
    
    _sessions[req.session_id] = history
    return ChatResponse(answer=answer,session_id=req.session_id)

@app.post("/chat/stream",dependencies=[Depends(check_access)])
def chat_stream(req: ChatRequest):
    """SSE 流式问答：边跑边把进度和答案推给客户端"""
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400,detail="question 不能为空")
    
    history = _sessions.get(req.session_id,[])
    
    def event_stream():
        """产出 SSE 格式的文本块，每条以空行结尾"""
        try:
            for event in run_agent_events(question,history):
                #答案事件带着完整历史，这时才写回会话
                if event["type"] == "answer":
                    _sessions[req.session_id] = event["history"]
                    payload = {"type":"answer","text":event["text"]}
                else:
                    payload = event
                
                yield f"data: {json.dumps(payload,ensure_ascii=False)}\n\n"
            
            yield "data: {\"type\":\"done\"}\n\n"      #正常结束标记
        except Exception as e:
            err = {"type":"error","msg":f"{type(e).__name__}: {e}"}
            yield f"data: {json.dumps(err,ensure_ascii=False)}\n\n"
    
    return StreamingResponse(event_stream(),media_type="text/event-stream")

@app.delete("/session/{session_id}",dependencies=[Depends(check_access)])
def clear_session(session_id: str):
    """清空某个会话的历史"""
    _sessions.pop(session_id,None)
    return {"cleared":session_id}