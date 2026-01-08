import Levenshtein
from collections import deque

class Checker:
    """
        检查OCR传过来的文本是否需要翻译和体现。
        目前方案：检测文本是否与之前的发生明显变化。无论结果如何都存储新文本（不存储空文本）作为下一次判断的依据。
    """
    def __init__(self, queue_size: int = 2, similarity: float = 0.9) -> None:
        self.queue = deque([''],maxlen=queue_size)
        self.similarity = similarity # 文本相似度阈值，低于该阈值则认为发生明显变化。

    def check(self, new_text: str) -> bool:
        """
            检测新文本是否与之前的历史文本发生明显变化。如发生明显变化则返回True。
        """
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
                return True
            else:
                return False


