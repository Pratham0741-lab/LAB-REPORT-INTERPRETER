# ocr_layer.py
from typing import Dict, List

import cv2
import numpy as np
from pdf2image import convert_from_bytes
import pytesseract


def _preprocess_image(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 3)
    th = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        31,
        10
    )
    return th


def _images_from_bytes(file_bytes: bytes, file_type: str) -> List[np.ndarray]:
    if file_type == "image":
        arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image bytes.")
        return [img]

    if file_type == "pdf":
        pil_pages = convert_from_bytes(file_bytes)
        images = [cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR) for p in pil_pages]
        if not images:
            raise ValueError("No pages extracted from PDF.")
        return images

    raise ValueError(f"Unsupported file_type: {file_type}")


def ocr_image_bytes(file_bytes: bytes, file_type: str = "pdf") -> Dict:

    images = _images_from_bytes(file_bytes, file_type)
    pages = []
    full_text_parts = []

    for idx, img in enumerate(images, start=1):
        processed = _preprocess_image(img)
        text = pytesseract.image_to_string(processed)
        pages.append({"page_number": idx, "text": text})
        full_text_parts.append(text)

    return {"pages": pages, "full_text": "\n".join(full_text_parts)}
