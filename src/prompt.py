import re 
import json
from typing import Dict,Any
from .tool import registry

SYSTEM_PROMPT = """
你是一个企业知识问答助手，你可以使用以下工具获取知识库内容，
每一步只能选择下面两种输出格式之一。

如果需要调用工具：
Thought: 说明你为什么要用这个工具
Action: 工具名称
Action Input: JSON参数 

执行工具之后，系统会返回：
Observation:工具执行结果

然后你继续推理。

如果已经可以直接回答:
Thought : 我已经得到最终答案
Final Answer:最终答案

可使用工具：
{tool}

重要：
1. 每次回复只能输出一种格式：要么只输出 Action，要么只输出 Final Answer，不能同时出现
2. Observation 只能由系统提供，你绝对不能自己写 Observation
3. Action Input 必须是单行合法 JSON
4. Action 必须是已注册的工具名称
5. 不得使用你自身的预训练知识补充答案，不得猜测、不得编造
6. 如果知识库检索结果为空，直接回答：资料中未找到相关信息，无法根据现有知识库回答。
"""

class ReActparser:
    
    @staticmethod
    def parse(respone:str) -> Dict[str,Any]:
        
        #先看有没有工具调用：有动作就执行动作，不能因为出现 Final Answer 就跳过工具
        action = re.search(r"Action:(.*)",respone)
        Action_input = re.search(r"Action Input:(.*)",respone,re.DOTALL)
        
        if action and Action_input:
            tool_name = action.group(1).strip()
            #只取 JSON 本体：遇到空行或 Observation 就截断
            input_text = re.split(r"\n\s*\n|\nObservation:",Action_input.group(1))[0].strip()
            
            try:
                argument = json.loads(input_text)
            except json.JSONDecodeError:
                raise ValueError("input_text不是合法json")
            return {
            "type":"tool",
            "name":tool_name,
            "argument":argument,
            }
        
        #没有动作，再看是不是最终答案
        final_answer = re.search(r"Final Answer:(.*)",respone,re.DOTALL)
        
        if final_answer:
            return{
                "type":"final_answer",
                "answer": final_answer.group(1).strip(),
            }
        
        raise ValueError("无法解析大模型输出")
    


