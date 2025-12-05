from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()
api_key = os.environ['DEEPSEEK_API_KEY']



client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")




class Translator:
    def __init__(self,size=2):
        self.queue = []
        self.size = size

    def translate(self, text: str) -> str:
        if self._judge(text):
            text = self._clear(text)
            if text == "":
                return ""
            return self._translate_text(text)
        else:
            return ""
    
    def _judge(self,item:str):
        # queue 未满时，直接添加，返回True表示可以翻译
        if len(self.queue) < self.size:
            self.queue.append(item)
            return True
        # queue 已满时，弹出最早的，添加新的，比较最后两个，相同返回False表示不翻译，不同返回True表示翻译
        elif len(self.queue) >= self.size:
            self.queue.pop(0)
            self.queue.append(item)
            return not self.queue[-2] == self.queue[-1]
        # 默认返回 False
        return True
    
    def _clear(self,text:str):
        text  = text.strip()
        if text == "":
            return ""
        if text.count("\n")>=3:
            # text = max(text.split("\n"), key=len) # 取最长的一行
            strings = text.split("\n")
            # 取最长的一行
            max_len = max(len(s) for s in strings)
            if max_len < 4:
                return ""
            longest_string = max(strings, key=len)
            remaining_strings = []
            
            # 单次遍历以保持顺序
            for s in strings:
                if len(s) < max_len:
                    remaining_strings.append(s.strip())
            
            return longest_string.strip()+"\n"+"  ".join(remaining_strings)
        else:
            return text
        
    def _translate_text(self, text: str) -> str:
        messages = [
            {"role": "system", "content": "你是一个卓越的翻译专家，需要把内容翻译成中文。只回答翻译结果。翻译结果信达雅，贴近中文表达习惯，保证流畅，贴近原文的语气和文化,有温度。如果原文有文化隐喻，用中文的文化隐喻来表达，或注释说明。保留所有特殊符号。"},
            {"role": "user", "content": text},
        ]
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False,
            temperature=1.3,
            max_tokens=128
        )
        return response.choices[0].message.content