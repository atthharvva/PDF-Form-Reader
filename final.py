import fitz
import cv2
import numpy as np
from PIL import Image
import io
import pytesseract
import pandas as pd


class FormExtractor:
    def __init__(self, tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.fields = {
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
        self.field_mappings = {
            "Name": ["Your Name", "Yourname —", "Yourname _ ", "Yourname "],
            "Account number": ["Account # —", "Account #", "Account##  ", "Account#"],
            "Last four digits of card": ["Last 4 digits of the card#", "Last 4 digits of thecard#"],
            "Transaction date": ["Transaction date", "Transactiondate"],
            "Amount": ["Amount $", "Amount$"],
            "Merchant name": ["Merchantname", "Merchant name ", "Merchant name"],
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
            "Reason for dispute": ["Reason for Dispute", "Renson renee:\nDate"]
        }

    def extract_text_with_context(self, img, x, y, w, h):
        """
        Extract text from regions around a given bounding box in the image.

        Parameters:
            img (ndarray): Image from which text is to be extracted.
            x (int): X-coordinate of the bounding box.
            y (int): Y-coordinate of the bounding box.
            w (int): Width of the bounding box.
            h (int): Height of the bounding box.

        Returns:
            str: Extracted text from regions above and next to the bounding box.
        """
        above_region = img[max(0, y - h):y, x:x + w + 50]  # Region above the checkbox
        next_to_region = img[y:y + h, x + w:x + w + 200]  # Region next to the checkbox

        # Handle cases where regions may go out of bounds
        if above_region.shape[1] != next_to_region.shape[1]:
            max_width = max(above_region.shape[1], next_to_region.shape[1])
            above_region = cv2.copyMakeBorder(
                above_region, 0, 0, 0, max_width - above_region.shape[1], cv2.BORDER_CONSTANT, value=255
            )
            next_to_region = cv2.copyMakeBorder(
                next_to_region, 0, 0, 0, max_width - next_to_region.shape[1], cv2.BORDER_CONSTANT, value=255
            )

        # Combine the two regions vertically
        combined_region = cv2.vconcat([above_region, next_to_region])

        # Preprocess the combined region for better OCR performance
        # Convert to grayscale and apply thresholding for better text extraction
        gray_region = cv2.cvtColor(combined_region, cv2.COLOR_BGR2GRAY)
        _, thresholded_region = cv2.threshold(gray_region, 150, 255, cv2.THRESH_BINARY)

        # Extract text using pytesseract with configured OCR settings
        extracted_text = pytesseract.image_to_string(
            thresholded_region, config='--psm 6').strip()

        # Return the extracted text (check if extraction is empty)
        return extracted_text if extracted_text else "No text detected"

    def detect_checkboxes_with_text_and_context(self, img, page_num, is_three_page_doc):
        """
        Detect checkboxes in the image, analyze their state (checked/unchecked), and extract surrounding text.

        Parameters:
            img (ndarray): Image in which checkboxes are to be detected.
            page_num (int): Current page number.
            is_three_page_doc (bool): Flag to indicate if the document has three pages.

        Returns:
            dict: Mapping of checkbox text to their states (checked/unchecked).
        """
        global FIELDS

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3
        )
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

        update_fields_from_checkbox_results(results, page_num)
        return results

    def update_fields_from_checkbox_results(self, results, page_num):
        """
        Update global fields based on detected checkbox results for a specific page.

        Parameters:
            results (dict): Checkbox text-to-state mappings.
            page_num (int): Page number where the checkboxes were detected.
        """
        global FIELDS

        for key, state in results.items():
            if state == "checked":
                key_text = key.split(": ")[1].upper()

                if page_num == 1:
                    handle_page_1_checkboxes(key_text)
                elif page_num == 2:
                    handle_page_2_checkboxes(key_text)

        print(f"\nPage {page_num} Checkbox Results (State: [Text]):\n{results}\n")

    def handle_page_1_checkboxes(self, key_text):
        """
        Process and update fields for page 1 checkboxes.

        Parameters:
            key_text (str): Text associated with a checkbox.
        """
        global FIELDS
        if "SECTION" or "SECTION 1"in key_text:
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

    def handle_page_2_checkboxes(self, key_text):
        """
        Process and update fields for page 2 checkboxes.

        Parameters:
            key_text (str): Text associated with a checkbox.
        """
        global FIELDS
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


    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from a PDF file and processes checkboxes and context.

        Args:
            pdf_path (str): The path to the input PDF file.

        Returns:
            dict: A dictionary with page numbers as keys and extracted text as values.
        """
        text_by_page = {}
        with fitz.open(pdf_path) as pdf:
            is_three_page_doc = len(pdf) == 3

            for page_num, page in enumerate(pdf):
                pix = page.get_pixmap(dpi=150)
                img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))))

                page_text = pytesseract.image_to_string(img, config='--psm 6')
                text_by_page[page_num + 1] = page_text

                # Correct method call using self
                self.detect_checkboxes_with_text_and_context(img, page_num + 1, is_three_page_doc)

        print(text_by_page)
        return text_by_page

    def find_field_values(self, text_by_page):
        """
        Extracts field values from the text of each page in the PDF.

        Args:
            text_by_page (dict): A dictionary where keys are page numbers and values are the text extracted from each page.

        Modifies:
            Updates the global FIELDS dictionary with values extracted from the text.
        """
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

        # Additional processing for specific fields
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

    def save_to_excel(self, filename):
        """
        Saves extracted field data to an Excel file.

        Args:
            data (dict): A dictionary containing field names and their extracted values.
            filename (str): The path to the output Excel file.

        Saves:
            Writes the data to the specified Excel file.
        """
        data = {
            "Field Name": list(data.keys()), 
            "Extracted Value": list(data.values())
        }
        df = pd.DataFrame(data)
        df = df.T
        df.to_excel(filename, index=False, header=False)
        print(f"Data saved to {filename}")


if __name__ == "__main__":
    pdf_path = "PDF_Form_Reader\input folder\Completed Dispute Form 3.pdf (2).pdf"
    excel_filename = "D:\atharva\Internship\task_20_Dec_24\PDF_Form_Reader\output folder\extracted_data_form311.xlsx"
    tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    extractor = FormExtractor(tesseract_cmd)
    text_by_page = extractor.extract_text_from_pdf(pdf_path)
    extractor.find_field_values(text_by_page)
    extractor.save_to_excel(excel_filename)
    print("Extraction complete!")
