from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()
api_key = os.environ['DEEPSEEK_API_KEY']



client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")




class Translator:
    def __init__(self,size=2, exclude_set=None):
        self.queue = []
        self.size = size
        self.exclude_dict = dict()
 # 需要排除的文本, key为文本内容，value为出现次数, 超过一定次数后加入exclude_set永久排除
        self.exclude_amount = 3 # 超过该次数后加入永久排除集合
        self.exclude_set = exclude_set if exclude_set is not None else set() # 永久排除的文本

    def translate(self, text) -> str:
        # 根据输入类型进行处理
        if isinstance(text, str):
            text = text.strip()
            if self._judge(text):
                return self._translate_text(text)
            else:
                return ""
        if isinstance(text, tuple):
            # 多行文本可能存在游戏UI，需要清理
            cleared_text = self._clear(text).strip()
            if self._judge(cleared_text):
                return self._translate_text(cleared_text)
            else:
                return ""
        else:
            return ""

    
    def _judge(self,item:str):
        # 按上次翻译结果判断是否翻译，如果重复则不翻译
        # 返回False表示不翻译，返回True表示翻译
        if item == "":
            return False
        # queue 未满时表示为第一次翻译，直接填满，返回True表示可以翻译
        if len(self.queue) < self.size:
            for _ in range(self.size):
                self.queue.append(item[:-1]) # 防止最后一个字符因跳动产生变化
            return True
        # queue 已满时，弹出最早的，添加新的，比较最后两个，相同返回False表示不翻译，不同返回True表示翻译
        elif len(self.queue) >= self.size:
            self.queue.pop(0)
            self.queue.append(item[:-1]) # 防止最后一个字符因跳动产生变化
            return not self.queue[-2] == self.queue[-1]
        # 默认返回 False
        print("translate._judge方法if语句未覆盖所有情况")
        return False
    
    def _clear(self, texts:tuple[str]) -> str:
        # 作用是清除多余的行（如游戏UI等内容）
        if not isinstance(texts, tuple):
            return ""
        if len(texts) == 0:
            return ""
        texts = [x.strip() for x in texts if isinstance(x,str)] # 去除前后空格，生成list
        if len(texts)>=3: # 多行文本时，很可能其中有无意义的行
            # 先删除已永久排除的行
            texts = [x for x in texts if x not in self.exclude_set]
            if len(texts) == 0:
                return ""
            # 取最长的一行，信任其有意义。下一步准备加入排除词
            longest_test = max(texts, key=lambda x:len(x))
            # 排除最长行后把其它疑似UI的行加入计数字典
            texts.remove(longest_test)
            for item in texts:
                if item in self.exclude_dict:
                    self.exclude_dict[item] += 1
                else:
                    self.exclude_dict[item] = 1
                # 超过3次的加入永久排除集合
                if self.exclude_dict[item] >= 3:
                    self.exclude_set.add(item)
            return longest_test
        else: # 少行文本，合并后翻译
            texts = "\n".join([x.strip() for x in texts])
            return texts
        
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