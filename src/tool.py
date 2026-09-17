#工具注册，装饰器

class Toolregistry:
    def __init__(self):
        self.tools = {}
        
    def regist(self,name:str,description:str,func:callable):
        self.tools[name] ={
            "name": name,
            "description":description,
            "func":func,
        }
    
    def get_tool(self,name:str):
        tool = self.tools.get(name)
        return tool["func"] if tool else None
    def get_tool_prompt(self):
        prompt = []
        for tool in self.tools.values():
            prompt.append(f"{tool['name']}: {tool['description']}")
        return "\n".join(prompt)

registry = Toolregistry()

def tool(name:str,description:str):
    def decorator(func:callable):
        registry.regist(name,description,func)
        return func
    return decorator