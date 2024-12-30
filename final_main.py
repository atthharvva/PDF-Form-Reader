import fitz
import cv2
import numpy as np
from PIL import Image
import io
import pytesseract
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

FIELDS = {
    "Name": None, "Account number": None, "Last four digits of card": None, "Transaction date": None, 
    "Amount": None, "Merchant name": None, "Transaction was not authorized": None,  
    "My card was": None, "Date you lost your card": None, "Time you lost your card": None,
    "Date you realised card was stolen": None, "Time you realised card was stolen": None,
    "Do you know who made the transaction": None, "Have you given permission to anyone to use your card": None,
    "When was the last time you used your card": None, "Last transaction amount": None,
    "Where do you normally store your card": None, "Where do you normally store your PIN": None,
    "Other items that were stolen": None, "Have you filed police report": None, "Officer name": None,
    "Report number": None, "Suspect name": None, "Date": None, "Contact number": None, "Reason for dispute": None
}

field_mappings = {
    "Name": ["Yourname —", "Yourname _ ", "Yourname "],
    "Account number": ["Account # —", "Account #", "Account##  "],
    "Last four digits of card": ["Last 4 digits of the card#", "Last 4 digits of thecard#"],
    "Transaction date": ["Transaction date", "Transactiondate"],
    "Amount": ["Amount $"],
    "Merchant name": ["Merchantname", "Merchant name "],
    "Transaction was not authorized": None,
    "My card was": None,
    "Date you lost your card": ["your card? card was missing?"],
    "Time you lost your card": ["your card? card was missing?"],
    "Date you realised card was stolen": ["your card? card was missing?"],
    "Time you realised card was stolen": ["your card? card was missing?"],
    "Do you know who made the transaction": None,
    "Have you given permission to anyone to use your card": None,
    "When was the last time you used your card": ["Date/Time:"],
    "Last transaction amount": ["Amount: $"],
    "Where do you normally store your card": ["Where do you normally store your card? _", "Where do you normally store your card?"],
    "Where do you normally store your PIN": ["Where do you normally store your PIN?"],
    "Other items that were stolen": ["additional cards (if applicable):"],
    "Have you filed police report": None,
    "Officer name": ["District/Officer name:"],
    "Report number": ["Report number:", "Report Number"],
    "Suspect name": ["Suspect name:", "Suspect Name"],
    "Date": ["Date: =", "Date:"],
    "Contact number": ["Contact number (during the hours of 8am-5pm PST): —", "Contact number (during the hours of 8am-5pm PST):", "Contact number (during the hours of 8am-5pm PST);"],
    "Reason for dispute": ["Reason for Dispute"]
}

def extract_text_with_context(img, x, y, w, h):
    
    above_region = img[max(0, y - h):y, x:x + w + 200]
    next_to_region = img[y:y + h, x + w:x + w + 200]

    if above_region.shape[1] != next_to_region.shape[1]:
        max_width = max(above_region.shape[1], next_to_region.shape[1])
        above_region = cv2.copyMakeBorder(
            above_region, 0, 0, 0, max_width - above_region.shape[1], cv2.BORDER_CONSTANT, value=255
        )
        next_to_region = cv2.copyMakeBorder(
            next_to_region, 0, 0, 0, max_width - next_to_region.shape[1], cv2.BORDER_CONSTANT, value=255
        )

    combined_region = cv2.vconcat([above_region, next_to_region])
    extracted_text = pytesseract.image_to_string(
        combined_region, config='--psm 6').strip()

    return extracted_text


def detect_checkboxes_with_text_and_context(img, page_num):
    
    global FIELDS

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3
    )
    edges = cv2.Canny(binary, 100, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    results = {}

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 30 < w < 60 and 30 < h < 60:  
            checkbox_region = binary[y:y + h, x:x + w]
            non_zero_pixels = cv2.countNonZero(checkbox_region)
            total_pixels = w * h
            fill_ratio = non_zero_pixels / total_pixels
            state = "checked" if fill_ratio > 0.3 else "unchecked"

            extracted_text = extract_text_with_context(img, x, y, w, h)

            if extracted_text:  
                key = f"{state.capitalize()}: {extracted_text}"
                results[key] = state
                print(f"Text around checkbox at ({x}, {y}): {extracted_text}")

    update_fields_from_checkbox_results(results, page_num)
    return results


def update_fields_from_checkbox_results(results, page_num):
    
    global FIELDS

    for key, state in results.items():
        if state == "checked":
            key_text = key.split(": ")[1].upper()

            if page_num == 1:
                handle_page_1_checkboxes(key_text)
            elif page_num == 2:
                handle_page_2_checkboxes(key_text)

    print(f"\nPage {page_num} Checkbox Results (State: [Text]):\n{results}\n")


def handle_page_1_checkboxes(key_text):
    
    global FIELDS
    if "SECTION" in key_text:
        FIELDS["Transaction was not authorized"] = "Yes"
    else:
        FIELDS["Transaction was not authorized"] = "No"

    if "IN MY" in key_text:
        FIELDS["My card was"] = "In My Possession"
    elif "NOT" in key_text:
        FIELDS["My card was"] = "Not Received"
    elif "STOLEN" in key_text:
        FIELDS["My card was"] = "Stolen"
    elif "LOST" in key_text:
        FIELDS["My card was"] = "Lost"

    if "DO YOU" in key_text:
        FIELDS["Do you know who made the transaction"] = "No"
    elif "WHO MADE" in key_text:
        FIELDS["Do you know who made the transaction"] = "Yes"
    
    if "HAVE YOU" in key_text:
        FIELDS["Have you given permission to anyone to use your card"] = "No"
    elif "PERMISSION TO" in key_text:
        FIELDS["Have you given permission to anyone to use your card"] = "Yes"


def handle_page_2_checkboxes(key_text):
    
    global FIELDS
    if "NO" in key_text:
        FIELDS["Have you filed police report"] = "No"
    else:
        FIELDS["Have you filed police report"] = "Yes"


def extract_text_from_pdf(pdf_path):
    
    text_by_page = {}
    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf):
            pix = page.get_pixmap(dpi=150)
            img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))))
            
            
            page_text = pytesseract.image_to_string(img, config='--psm 6')
            text_by_page[page_num + 1] = page_text

            
            detect_checkboxes_with_text_and_context(img, page_num + 1)

    print(text_by_page)           
    return text_by_page


def find_field_values(text_by_page):
    
    for page_num, page_text in text_by_page.items():
        print(f"Processing Page {page_num}")
        
        for field, variations in field_mappings.items():
            if variations:  
                for variation in variations:
                    if variation.lower() in page_text.lower():
                        field_index = page_text.lower().find(variation.lower())
                        
                        right_text = page_text[field_index + len(variation):].strip().split("\n")[0]
                        
                        if right_text:
                            if FIELDS[field] is None:
                                FIELDS[field] = right_text.strip()
                                print(f"Found value for '{field}': {FIELDS[field]}")
    print(f"\nFinal Extracted FIELDS:\n{FIELDS}")
    if "Date you lost your card" in FIELDS and FIELDS["Date you lost your card"]:
        FIELDS["Date you lost your card"] = FIELDS["Date you lost your card"].split()[0]

    if "Time you lost your card" in FIELDS and FIELDS["Time you lost your card"]:
        FIELDS["Time you lost your card"] = FIELDS["Time you lost your card"].split()[1]

    if "Date you realised card was stolen" in FIELDS and FIELDS["Date you realised card was stolen"]:
        FIELDS["Date you realised card was stolen"] = FIELDS["Date you realised card was stolen"].split()[2]

    if "Time you realised card was stolen" in FIELDS and FIELDS["Time you realised card was stolen"]:
        FIELDS["Time you realised card was stolen"] = FIELDS["Time you realised card was stolen"].split()[3]

    if "Reason for dispute" in FIELDS and FIELDS["Reason for dispute"]:
        if FIELDS["Merchant name"] and FIELDS["Merchant name"].lower() in FIELDS["Reason for dispute"].lower():
            x = FIELDS["Merchant name"]
            index_after_x = FIELDS["Reason for dispute"].lower().find(x.lower()) + len(x)
            FIELDS["Reason for dispute"] = FIELDS["Reason for dispute"][index_after_x:].strip()

    if "When was the last time you used your card" in FIELDS and FIELDS["When was the last time you used your card"]:
        parts = FIELDS["When was the last time you used your card"].split()
        if len(parts) >= 3:
            FIELDS["When was the last time you used your card"] = ' '.join(parts[:3])



def save_to_excel(data, filename):
    data = {
        "Field Name": list(data.keys()), 
        "Extracted Value": list(data.values())
    }
    
    df = pd.DataFrame(data)
    df = df.T
    
    df.to_excel(filename, index=False, header=False)
    print(f"Data saved to {filename}")


def main(pdf_path, excel_filename):
    
    text_by_page = extract_text_from_pdf(pdf_path)
    find_field_values(text_by_page)
    save_to_excel(FIELDS, excel_filename)
    return FIELDS

if __name__ == "__main__":
    
    pdf_path = "input folder/Completed Dispute Form 3.pdf (2).pdf"  
    excel_filename = "output folder/extracted_data_form3.xlsx"  
    extracted_data = main(pdf_path, excel_filename)
    print(f"Extracted Data:\n{extracted_data}")