import cv2
from text_extraction import extract_text_with_context

FIELDS = {
    "Name": None,
    "Account number": None,
    "Last four digits of card": None,
    "Transaction date": None,
    "Amount": None,
    "Merchant name": None,
    "Transaction was not authorized": None,
    "My card was": None,
    "Date you lost your card": None,
    "Time you lost your card": None,
    "Date you realised card was stolen": None,
    "Time you realised card was stolen": None,
    "Do you know who made the transaction": None,
    "Have you given permission to anyone to use your card": None,
    "When was the last time you used your card": None,
    "Last transaction amount": None,
    "Where do you normally store your card": None,
    "Where do you normally store your PIN": None,
    "Other items that were stolen": None,
    "Have you filed police report": None,
    "Officer name": None,
    "Report number": None,
    "Suspect name": None,
    "Date": None,
    "Contact number": None,
    "Reason for dispute": None
}

def detect_checkboxes_with_text_and_context(img, page_num, is_three_page_doc, FIELDS):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3)
    edges = cv2.Canny(binary, 100, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    results = {}

    if is_three_page_doc:
        min_size, max_size, min_fill_ratio = 27, 63, 0.39
    else:
        min_size, max_size, min_fill_ratio = 30, 60, 0.3

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if min_size < w < max_size and min_size < h < max_size:
            checkbox_region = binary[y:y + h, x:x + w]
            non_zero_pixels = cv2.countNonZero(checkbox_region)
            total_pixels = w * h
            fill_ratio = non_zero_pixels / total_pixels
            state = "checked" if fill_ratio > min_fill_ratio else "unchecked"

            extracted_text = extract_text_with_context(img, x, y, w, h)

            if extracted_text:
                key = f"{state.capitalize()}: {extracted_text}"
                results[key] = state
                print(f"Text around checkbox at ({x}, {y}): {extracted_text}")

    update_fields_from_checkbox_results(results, page_num, FIELDS)
    return results

def update_fields_from_checkbox_results(results, page_num, FIELDS):
    for key, state in results.items():
        if state == "checked":
            key_text = key.split(": ")[1].upper()

            if page_num == 1:
                handle_page_1_checkboxes(key_text, FIELDS)
            elif page_num == 2:
                handle_page_2_checkboxes(key_text, FIELDS)

    print(f"\nPage {page_num} Checkbox Results (State: [Text]):\n{results}\n")

def handle_page_1_checkboxes(key_text, FIELDS):
    if "SECTION" or "SECTION 1" in key_text:
        FIELDS["Transaction was not authorized"] = "Yes"
    else:
        FIELDS["Transaction was not authorized"] = "No"

    if "IN MY POSSESS" in key_text:
        FIELDS["My card was"] = "In My Possession"
    elif "NOT RECEIVED" in key_text:
        FIELDS["My card was"] = "Not Received"
    elif "STOLEN" in key_text:
        FIELDS["My card was"] = "Stolen"
    elif "LOST" in key_text:
        FIELDS["My card was"] = "Lost"

def handle_page_2_checkboxes(key_text, FIELDS):
    if "NO" in key_text:
        FIELDS["Have you filed police report"] = "No"
    else:
        FIELDS["Have you filed police report"] = "Yes"
    
    if "DO YOU" or "NO YES" in key_text:
        FIELDS["Do you know who made the transaction"] = "No"
    elif "WHO" in key_text:
        FIELDS["Do you know who made the transaction"] = "Yes"
    
    if "HAVE YOU" in key_text:
        FIELDS["Have you given permission to anyone to use your card"] = "No"
    else:
        FIELDS["Have you given permission to anyone to use your card"] = "Yes"
