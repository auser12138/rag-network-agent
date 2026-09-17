from .bootstrap import setup
from .agent import run_agent

setup()

#第一轮
answer,history = run_agent("交换机接口 Down 怎么排查")
print(answer)

#第二轮：把上一轮的历史传进去，验证记忆
answer2,history = run_agent("那如果是光模块的问题呢？",history)
print(answer2)