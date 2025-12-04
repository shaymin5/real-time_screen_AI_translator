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
        texts = [detection[1] for detection in result]
        return '\n'.join(texts)



if __name__ == "__main__":
    start_time = time.time()

    ocr = OCR(languages=['en'])
    for i in range(10):
        text = ocr.ocr_image(r'D:\gameboy\ai_translator\temp_screenshots\temp_screenshot_20251202_214912.png')
    end_time = time.time()
    print(f"改进方案识别时间: {end_time - start_time:.2f} 秒")
    print(text)
    