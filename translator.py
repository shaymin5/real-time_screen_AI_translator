from dotenv import load_dotenv
from openai import OpenAI
import os
from abc import ABC, abstractmethod
from checker import Checker
from voxcpm_tts.tts.ttsplayer import TTSplayer
from typing import Union


load_dotenv()


class Provider(ABC):

    translator_prompt = "模拟卓越的翻译专家，把内容翻译成中文。只回答翻译结果。如果原文有文化隐喻，用中文的文化隐喻来表达。"

    def __init__(self):
        pass

    @abstractmethod
    def translate(self, text: str) -> str:
        pass


class Deepseek(Provider):

    def __init__(self, env_api_key: str = 'DEEPSEEK_API_KEY', max_tokens: int = 256):
        super().__init__()
        self.api_key = os.environ[env_api_key]
        self.maxtokens = max_tokens
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com")
        
    def translate(self, text: str) -> str:
        messages: list = [
            {"role": "system", "content": self.translator_prompt},
            {"role": "user", "content": text},
        ]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False,
            temperature=1.3,
            max_tokens=self.maxtokens
        )
        response_content = response.choices[0].message.content
        if response_content:
            return response_content.strip()
        else:
            return ""


class Translator:
    
    def __init__(self, ai_engine: str = 'deepseek', need_tts: bool = False):
        if ai_engine == 'deepseek':
            self.ai_engine: Provider = Deepseek()
        else:
            raise ValueError("Unsupported AI engine")
        self.checker: Checker = Checker()
        self.tts_player: Union[TTSplayer, None] = None
        if need_tts:
            self.tts_player = TTSplayer()
            

    def translate(self, text: str) -> str:
        if self.checker.check(text):
            return self.ai_engine.translate(text)
        else:
            return ""
        
    def translate_and_tts(self, text: str):
        if self.tts_player is None:
            raise RuntimeError('tts_player模块未正常加载。')
        else:
            text_translate = self.translate(text)
            if text_translate:
                self.tts_player.generate_and_play_streaming(text_translate) # 减少步数以追求稳定输出速度
            else:
                pass
