from pdf_processing import extract_text_from_pdf
from field_extraction import find_field_values, save_to_excel
from checkbox_detection import FIELDS

def main(pdf_path, excel_filename):
    field_mappings = {
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

    text_by_page = extract_text_from_pdf(pdf_path, FIELDS)
    find_field_values(text_by_page, FIELDS, field_mappings)
    save_to_excel(FIELDS, excel_filename)
    return FIELDS

if __name__ == "__main__":
    pdf_path = "PDF_Form_Reader\input folder\Completed Dispute Form 3.pdf (2).pdf"
    excel_filename = "PDF_Form_Reader\output folder\extracted_data_form311.xlsx"
    extracted_data = main(pdf_path, excel_filename)
    print(f"Extracted Data:\n{extracted_data}")
