# ocr_utils.py
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

def pdf_to_images(pdf_bytes: bytes, dpi: int = 300):
    """Convert PDF bytes to a list of PIL images."""
    return convert_from_bytes(pdf_bytes, dpi=dpi)

def ocr_image(img: Image.Image) -> str:
    """OCR a single page image."""
    return pytesseract.image_to_string(img)

def ocr_pdf(pdf_bytes: bytes):
    """OCR all pages of a PDF -> list of page texts."""
    images = pdf_to_images(pdf_bytes)
    texts = [ocr_image(img) for img in images]
    return texts
