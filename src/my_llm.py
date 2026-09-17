from .config import llm_Api_Key,llm_Api_URL,llm_Api_mode
from  openai import OpenAI

#提示词
SYSTEM_PROMPT = (
    "你是严谨的知识库问答助手。"
    "只能根据下面提供的资料回答，禁止编造资料中没有的内容。"
    "如果资料不足以回答，请直接说明：资料中未找到相关信息。"
)
#items 是检索返回的 [{text, source, distance}]，内容、来源、相似值
def bulid_prompt(question:str, items) ->list :
    contexts = "\n".join(f"[资料{i}] {it ['text']}" for i ,it in enumerate(items,1))
    #拼接资料
    return[
        {"role" : "system", "content":SYSTEM_PROMPT},
        {"role" : "user", "content": f"相关资料:\n{contexts}\n\n 问题:{question}"},
    ]
    
#调用大模型
def call_llm(messages):
    client = OpenAI(api_key=llm_Api_Key,base_url=llm_Api_URL)
    resp = client.chat.completions.create(
        model= llm_Api_mode,
        messages= messages,
        temperature=0.3,
        stop=["\nObservation:"],
    )
    return resp.choices[0].message.content#resp.choices：列表，通常只有一个元素（除非你要求生成多个候选）。[0]：取第一个生成的回答。
                                          #.message.content：提取模型生成的文本内容（即回答本身）。

#大模型结果
def answer(question,items):
    if not items:
        return {"answer": "没有找到相关内容", "source": []}
    messages = bulid_prompt(question,items)
    answer = call_llm(messages)
    sources = [{"source": it["source"],"text": it["text"]} for it in items ]
    return {"answer": answer,"source": sources}
    
    