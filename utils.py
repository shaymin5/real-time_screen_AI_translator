import Levenshtein
from collections import deque
from typing import Any, Union
from pathlib import Path
import queue

class Checker:
    """
        检查OCR传过来的文本是否需要翻译和体现。
        目前方案：1、检测文本是否过长；2、检测文本是否与之前的发生明显变化。无论结果如何都存储新文本（不存储空文本）作为下一次判断的依据。
    """
    def __init__(self, queue_size: int = 2, similarity: float = 0.8) -> None:
        self.queue = deque([''],maxlen=queue_size)
        self.similarity = similarity # 文本相似度阈值，低于该阈值则认为发生明显变化。越低说明变化需要越明显才能通过。

    def check(self, new_text: str, maxlen: int = 200) -> bool:
        """
        检测文本长度是否过长。
        检测新文本是否与之前的历史文本发生明显变化。如发生明显变化则返回True。
        """
        if len(new_text) > maxlen:
            return False
        if new_text == '':
            return False
        if self.queue[-1] == '':
            self.queue.append(new_text) # 存储新文本
            return True
        else:
            self.queue.append(new_text)
            # 计算当前文本与历史文本的相似度
            similarity = Levenshtein.ratio(self.queue[-1], self.queue[-2])
            if similarity < self.similarity:
                # 如果很不相似，则通过检查
                return True
            else:
                return False
            

class FadeQueue:
    def __init__(self, maxsize: int = 0) -> None:
        self.queue = queue.Queue(maxsize=maxsize)
    def put(self, item: Any):
        try:
            self.queue.put(item)
        except queue.Full:
            while self.queue.full():
                try:
                    self.queue.get_nowait()
                    self.queue.put(item)
                except queue.Full:
                    pass
                except queue.Empty:
                    self.queue.put(item)
    def get(self) -> Any:
        return self.queue.get()
    def empty(self) -> bool:
        return self.queue.empty()
    def get_nowait(self) -> Any:
        return self.queue.get_nowait()
    def put_nowait(self, item: Any):
        return self.queue.put_nowait(item)
