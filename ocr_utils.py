# ocr_utils.py
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

def pdf_to_images(pdf_bytes: bytes, dpi: int = 300):
    return convert_from_bytes(pdf_bytes, dpi=dpi)

def ocr_image(img: Image.Image) -> str:
    return pytesseract.image_to_string(img)

def ocr_pdf(pdf_bytes: bytes):
    images = pdf_to_images(pdf_bytes)
    texts = [ocr_image(img) for img in images]
    return texts
