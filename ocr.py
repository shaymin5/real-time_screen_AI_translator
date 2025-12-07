import easyocr
import time


class OCR:
    def __init__(self, languages=['en'],gpu=True):
        self.languages = languages
        self.reader = easyocr.Reader(languages, gpu=gpu)

    def ocr_image(self, image_path) -> str:
        result = self.reader.readtext(
            image_path,
            paragraph=True)
        texts = tuple(detection[1] for detection in result)
        return texts



if __name__ == "__main__":
    start_time = time.time()

    ocr = OCR(languages=['en'])
    text = ocr.ocr_image(r'test_pic\image copy.png')
    end_time = time.time()
    print(f"改进方案识别时间: {end_time - start_time:.2f} 秒")
    print(text)
    