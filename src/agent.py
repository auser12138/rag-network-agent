import json
from .prompt import SYSTEM_PROMPT, ReActparser
from .my_llm import call_llm
from .tool import registry
from . import tools
from .config import OBSERVATION_MAX

def run_agent(question:str,history = None,max_tep:int = 5) ->str:
    #有历史保存一次历史
    messages = list(history) if history else []
    
    if not messages :
        messages.append({"role":"system","content":SYSTEM_PROMPT.format(tool =registry.get_tool_prompt())})
    messages.append({"role":"user","content":question})
        
    for step in range(max_tep):
        text = call_llm(messages)
        
        print(f"--- 第{step + 1}轮 ---\n{text}")
        
        messages.append({"role":"assistant","content" : text})
        try: 
            parse = ReActparser.parse(text)
        except  ValueError as e:
            messages.append({"role":"user","content":f"Observation: 你的输出格式不合法（{e}），必须包含 Action 和 Action Input，或直接给 Final Answer，请重新输出"})
            continue
        
        if parse["type"] == "final_answer":
            return parse["answer"],messages
        
        name = parse["name"]
        arguments = parse["argument"]
        
        func = registry.get_tool(name)
        if func is None:
            messages.append({"role":"user","content":f"Observation:没有名为{name}的工具，可以用工具为{list(registry.tools)}"})
            continue
       
        
        try:
            observation = func(**arguments)  
        except Exception as e:
            messages.append({"role":"user","content":f"Observation:工具执行失败（{e}），请重新输出"})
            continue
        
        observation = str(observation)
        if len(observation) > OBSERVATION_MAX:
            print(f"警告 observation 被截断:{len(observation)} -> {OBSERVATION_MAX}")
            observation = observation[:OBSERVATION_MAX] + "…(已截断)"
        messages.append({"role":"user","content":f"Observation:{observation}"})

    return "没有结果",messages
        