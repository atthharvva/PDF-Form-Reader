import fitz
import numpy as np
from PIL import Image
import io
import pytesseract

from checkbox_detection import detect_checkboxes_with_text_and_context

def extract_text_from_pdf(pdf_path, FIELDS):
    text_by_page = {}
    with fitz.open(pdf_path) as pdf:
        is_three_page_doc = len(pdf) == 3

        for page_num, page in enumerate(pdf):
            pix = page.get_pixmap(dpi=150)
            img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))))

            page_text = pytesseract.image_to_string(img, config='--psm 6')
            text_by_page[page_num + 1] = page_text
            detect_checkboxes_with_text_and_context(img, page_num + 1, is_three_page_doc, FIELDS)

    print(text_by_page)
    return text_by_page
