import pytesseract
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_with_context(img, x, y, w, h):
    above_region = img[max(0, y - h):y, x:x + w + 50]
    next_to_region = img[y:y + h, x + w:x + w + 200]

    if above_region.shape[1] != next_to_region.shape[1]:
        max_width = max(above_region.shape[1], next_to_region.shape[1])
        above_region = cv2.copyMakeBorder(above_region, 0, 0, 0, max_width - above_region.shape[1], cv2.BORDER_CONSTANT, value=255)
        next_to_region = cv2.copyMakeBorder(next_to_region, 0, 0, 0, max_width - next_to_region.shape[1], cv2.BORDER_CONSTANT, value=255)

    combined_region = cv2.vconcat([above_region, next_to_region])
    extracted_text = pytesseract.image_to_string(combined_region, config='--psm 6').strip()
    
    return extracted_text
