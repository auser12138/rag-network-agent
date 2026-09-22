import json
from .prompt import SYSTEM_PROMPT, ReActparser
from .my_llm import call_llm
from .tool import registry
from . import tools
from .config import OBSERVATION_MAX

def run_agent_events(question:str,history=None,max_tep:int = 5):
    """流式版本：边跑边产出事件
    事件类型：
      {"type":"status","msg":...}              进度提示（给用户看）
      {"type":"answer","text":...,"history":...} 最终答案（history 是完整对话记录）
      {"type":"error","msg":...}               出错
    """
    messages = list(history) if history else []
    
    #system 只在对话开始时加一次
    if not messages:
        messages.append({"role":"system","content":SYSTEM_PROMPT.format(tool=registry.get_tool_prompt())})
    
    messages.append({"role":"user","content":question})
    
    yield {"type":"status","msg":"正在分析问题…"}
    
    for step in range(max_tep):
        #① 调用模型
        try:
            text = call_llm(messages)
        except Exception as e:
            yield {"type":"error","msg":f"模型调用失败：{type(e).__name__}: {e}"}
            return
        
        messages.append({"role":"assistant","content":text})
        
        #② 解析模型的输出
        try:
            parse = ReActparser.parse(text)
        except ValueError as e:
            messages.append({"role":"user","content":f"Observation: 你的输出格式不合法（{e}），必须包含 Action 和 Action Input，或直接给 Final Answer，请重新输出"})
            yield {"type":"status","msg":"输出格式异常，正在重试"}
            continue
        
        #③ 有最终答案 → 结束
        if parse["type"] == "final_answer":
            yield {"type":"answer","text":parse["answer"],"history":messages}
            return
        
        #④ 要调工具
        name = parse["name"]
        func = registry.get_tool(name)
        if func is None:
            messages.append({"role":"user","content":f"Observation:没有名为{name}的工具，可以用工具为{list(registry.tools)}"})
            yield {"type":"status","msg":f"工具 {name} 不存在，正在重试"}
            continue
        
        yield {"type":"status","msg":f"正在调用工具：{name}"}
        
        try:
            observation = func(**parse["argument"])
        except Exception as e:
            messages.append({"role":"user","content":f"Observation:工具执行失败（{e}）"})
            yield {"type":"status","msg":f"工具执行失败：{type(e).__name__}"}
            continue
        
        #⑤ 回填前兜底截断
        observation = str(observation)
        if len(observation) > OBSERVATION_MAX:
            yield {"type":"status","msg":f"检索结果过长，已截断到 {OBSERVATION_MAX} 字"}
            observation = observation[:OBSERVATION_MAX] + "…(已截断)"
        messages.append({"role":"user","content":f"Observation:{observation}"})
    
    #步数用完
    yield {"type":"answer","text":"没有结果（已达到最大步数）","history":messages}


def run_agent(question:str,history=None,max_tep:int = 5):
    """非流式版本：消费事件流，返回 (答案, 历史)。原有调用方无需改动。"""
    answer = "没有结果"
    final_history = list(history) if history else []
    
    for event in run_agent_events(question,history,max_tep):
        if event["type"] == "answer":
            answer = event["text"]
            final_history = event["history"]
        elif event["type"] == "error":
            answer = event["msg"]
    
    return answer,final_history
        