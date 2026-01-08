import easyocr
from typing import Union


class GameOCR:
    def __init__(self, 
                 languages=['en'],
                 gpu=True, 
                 exclude_amount: int = 3,
                 exclude_set: Union[set,None] = None,
        ):
        # 初始化OCR识别器
        self.languages = languages
        self.reader = easyocr.Reader(languages, gpu=gpu)
        # 维护除外文本
        self.exclude_dict = dict() # 需要排除的文本, key为文本内容，value为出现次数, 超过一定次数后加入exclude_set永久排除
        self.exclude_amount = exclude_amount # 超过该次数后加入永久排除集合
        self.exclude_set = exclude_set if exclude_set is not None else set() # 永久排除的文本


    def img_to_text(self, image_path: str) -> str:
        texts_tuple = self._img_to_tuple(image_path)
        if not texts_tuple:
            return ""
        else:
            return self._clear_tuple_to_text(texts_tuple)

    def _img_to_tuple(self, image_path) -> tuple[str]:
        result:list = self.reader.readtext(
            image_path,
            x_ths= 0.5, # 优化检测水平距离阈值，用于判断是否同一行，默认1，越小越敏感，检测游戏UI，防止多UI被识别成一句话。
            y_ths=0.3, # 优化检测垂直距离阈值，用于判断是否同一行，默认0.5，越小越敏感。
            paragraph=True)
        texts = tuple(detection[1] for detection in result)
        return texts

    def _clear_tuple_to_text(self, texts_tuple: tuple[str]) -> str:
        texts = [x.strip() for x in texts_tuple if isinstance(x,str)] # 去除前后空格，生成list
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
                # 超过n次的加入永久排除集合
                if self.exclude_dict[item] >= self.exclude_amount:
                    self.exclude_set.add(item)
            return longest_test
        else: # 少行文本，合并后翻译
            texts = "\n".join([x.strip() for x in texts])
            return texts


if __name__ == "__main__":
    import time
    start_time = time.time()

    ocr = GameOCR(languages=['en'])
    img_list = [r'test_pic\image copy.png', r'test_pic\image copy.png', r'test_pic\image copy 2.png']
    for i in img_list:
        text = ocr.img_to_text(i)
        print(text)
    end_time = time.time()
    print(f"改进方案识别时间: {end_time - start_time:.2f} 秒")
    
    