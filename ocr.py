import easyocr
import json
import logging
import cv2
import numpy as np
from typing import Union
from pathlib import Path

logger = logging.getLogger(__name__)

ImageInput = Union[str, Path, bytes, np.ndarray]
RESIZE_THRESHOLD = 1920 * 1080 * 1.5 

class GameOCR:
    def __init__(
        self,
        languages=['en'],
        gpu=True,
        exclude_amount: int = 3,
        exclude_set: Union[set, None] = None,
        exclude_path: Union[str, Path, None] = "exclude_set.json",
    ):
        self.languages = languages
        self.reader = easyocr.Reader(languages, gpu=gpu)

        self.exclude_dict: dict[str, int] = {}
        self.exclude_amount = exclude_amount

        self.exclude_path = Path(exclude_path) if exclude_path else None
        self.exclude_set: set[str] = set()

        if exclude_set:
            self.exclude_set.update(exclude_set)

        if self.exclude_path:
            self._load_exclude_set()

    # ---------- public ----------

    def img_to_text(self, image: ImageInput) -> str:
        texts = self._img_to_list(image)
        if not texts:
            return ""
        return self._clear_list_to_text(texts)

    def save_exclude_set(self) -> None:
        if not self.exclude_path:
            return
        try:
            with self.exclude_path.open("w", encoding="utf-8") as f:
                json.dump(sorted(self.exclude_set), f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("Failed to save exclude_set")

    # ---------- internal ----------

    def _img_to_list(self, image: ImageInput) -> list[str]:
        try:
            img = self._load_image(image)
            img = self._preprocess_image(img)

            result: list = self.reader.readtext(
                img,
                x_ths=0.5,
                y_ths=0.3,
                paragraph=True,
            )
            return [detection[1] for detection in result]

        except Exception:
            logger.exception("OCR failed")
            return []

    def _load_image(self, image: ImageInput) -> np.ndarray:
        if isinstance(image, np.ndarray):
            return image

        if isinstance(image, (str, Path)):
            img = cv2.imread(str(image))
            if img is None:
                raise ValueError(f"Failed to load image: {image}")
            return img

        if isinstance(image, bytes):
            data = np.frombuffer(image, dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to decode image from bytes")
            return img

        raise TypeError(f"Unsupported image type: {type(image)}")

    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        游戏 OCR 专用预处理策略：
        - 默认不缩放
        - 只在极端大图时才 resize
        """
        h, w = img.shape[:2]
        pixel_count = h * w

        # 3M 像素以下：完全不动
        if pixel_count <= RESIZE_THRESHOLD:
            return img

        # 极端大图才缩
        scale = (RESIZE_THRESHOLD / pixel_count) ** 0.5
        new_w = int(w * scale)
        new_h = int(h * scale)

        logger.debug(
            "Resizing image from %dx%d to %dx%d for OCR",
            w, h, new_w, new_h
        )

        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def _clear_list_to_text(self, texts: list[str]) -> str:
        texts = [x.strip() for x in texts if isinstance(x, str)]

        if len(texts) >= 3:
            texts = [x for x in texts if x not in self.exclude_set]
            if not texts:
                return ""

            longest_text = max(texts, key=len)
            texts.remove(longest_text)

            for item in texts:
                self.exclude_dict[item] = self.exclude_dict.get(item, 0) + 1
                if self.exclude_dict[item] >= self.exclude_amount:
                    self.exclude_set.add(item)

            return longest_text
        else:
            return "\n".join(texts)

    # ---------- persistence ----------

    def _load_exclude_set(self):
        if not self.exclude_path:  # 检查是否为None
            return
        if not self.exclude_path.exists():
            return
        try:
            with self.exclude_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.exclude_set.update(data)
        except Exception:
            logger.exception("Failed to load exclude_set")



if __name__ == "__main__":
    import time
    ocr = GameOCR(languages=['en'])
    start_time = time.time()

    
    img_list = [r'test_pic\image copy.png', r'test_pic\image copy.png', r'test_pic\image copy 2.png', r'test_pic\image copy 3.png', r'test_pic\image copy 4.png']
    # for i in img_list:
    #     text = ocr.img_to_text(Path(i))
    #     print(text)
    print(ocr.img_to_text(Path(img_list[-2])))
    
    end_time = time.time()
    print(f"改进方案识别时间: {end_time - start_time:.2f} 秒")
    
    