import easyocr
import time


class OCR:
    def __init__(self, languages=['en'],gpu=True):
        self.languages = languages
        self.reader = easyocr.Reader(languages, gpu=gpu)

    def ocr_image(self, image_path) -> str:
        result = self.reader.readtext(
            image_path,
            x_ths= 0.5, # 优化检测水平距离阈值，用于判断是否同一行，默认1，越小越敏感，检测游戏UI，防止多UI被识别成一句话。
            y_ths=0.3, # 优化检测垂直距离阈值，用于判断是否同一行，默认0.5，越小越敏感。
            paragraph=True)
        texts = tuple(detection[1] for detection in result)
        return texts



if __name__ == "__main__":
    start_time = time.time()

    ocr = OCR(languages=['en'])
    img_list = [r'test_pic\image copy.png', r'test_pic\image copy.png', r'test_pic\image copy 2.png']
    for i in img_list:
        text = ocr.ocr_image(i)
        print(text)
    end_time = time.time()
    print(f"改进方案识别时间: {end_time - start_time:.2f} 秒")
    
    