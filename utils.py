import Levenshtein
from collections import deque
import threading


class Checker:
    """
    线程安全
    检查OCR传过来的文本是否需要翻译和体现。
    目前方案：1、过长文本不通过检查；2、当前文本与上上次不相似，与上次相似，则通过检查。无论结果如何都存储新文本（不存储空文本）作为下一次判断的依据。
    """
    def __init__(self, queue_size: int = 3, similarity: float = 0.95) -> None:
        # 关键：用空文本填充整个队列
        self.queue = deque([''] * queue_size, maxlen=queue_size)
        self.similarity = similarity
        self.lock = threading.Lock()

    def check(self, new_text: str, maxlen: int = 200) -> bool:
        """
        检测文本是否已经稳定地变化到新内容。
        需要同时满足：
        1. 当前文本和上次文本高度相似（稳定）
        2. 当前文本和上上次文本高度不相似（确实变化了）
        """
        with self.lock:
            if len(new_text) > maxlen or new_text == '':
                return False
            
            # 存储新文本
            self.queue.append(new_text)
            
            # 获取最近三次的文本
            current = self.queue[-1]  # 当前文本
            last = self.queue[-2]     # 上一次文本
            last_last = self.queue[-3] # 上上次文本
            
            # 条件1：当前和上次高度相似（文本稳定）
            similarity_current_last = Levenshtein.ratio(current, last)
            is_stable = similarity_current_last >= self.similarity
            
            # 条件2：当前和上上次高度不相似（确实发生了变化）
            similarity_current_last_last = Levenshtein.ratio(current, last_last)
            has_changed = similarity_current_last_last < self.similarity
            # 同时满足两个条件才通过检查
            return is_stable and has_changed

if __name__ == "__main__":
    c = Checker(queue_size=3, similarity=0.8)
    
    print("测试文本稳定过程:")
    # print("1. 第一次识别 'Hello':", c.check("Hello"))  # False（等待稳定）
    # print("2. 第二次识别 'Hello':", c.check("Hello"))  # True（已稳定）
    # print("3. 第三次识别 'Hello':", c.check("Hello"))  # False（没有变化）
    
    # print("\n测试切换到新文本:")
    # print("4. 第一次识别 '你好':", c.check("你好"))    # False（等待稳定）
    # print("5. 第二次识别 '你好':", c.check("你好"))    # True（新文本已稳定）
    
    # print("\n测试文本抖动:")
    # c2 = Checker(queue_size=3, similarity=0.8)
    # print("识别 'A':", c2.check("A"))      # False
    # print("识别 'B':", c2.check("B"))      # False（A不稳定）
    # print("识别 'A':", c2.check("A"))      # False（B不稳定）
    # print("识别 'A':", c2.check("A"))      # True（A终于稳定）
    a = "one day, War broke out between the two race"
    b = "one day, War broke out between the two races."
    # print("one day, War broke out between ", c.check("one day, War broke out between"))
    # print("one day, War broke out between the two races.", c.check("one day, War broke out between the two races."))
    print(Levenshtein.ratio(a,b))


    

