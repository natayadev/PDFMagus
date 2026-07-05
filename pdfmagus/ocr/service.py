import os

try:
    import pytesseract
except ImportError:
    pytesseract = None

COMMON_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
]


def is_available():
    return pytesseract is not None


def ensure_tesseract_found():
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        for path in COMMON_TESSERACT_PATHS:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True
    return False


def run_ocr(image, lang="spa+eng"):
    return pytesseract.image_to_string(image, lang=lang)
