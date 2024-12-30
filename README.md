# PDF Form Extraction Tool

## Overview
This Python script extracts information from PDF forms using OCR (Optical Character Recognition) and saves the extracted data into an Excel file. It is particularly designed for processing forms with checkboxes and textual fields. The script can handle variations in form structure and allows for easy customization to accommodate other PDF form types.

---

## Features
- Extracts textual data and checkbox states from PDF forms.
- Uses Tesseract OCR for text recognition.
- Detects and processes checkboxes to determine their states (checked/unchecked).
- Saves extracted information in a structured Excel format.
- Configurable field mappings to adapt to different PDF forms.

---

## Prerequisites

### Python Libraries
Install the required libraries by running:
```bash
pip install numpy opencv-python pytesseract PyMuPDF==1.20.2 pillow pandas openpyxl
```

### Tesseract OCR
Download and install Tesseract OCR from [Tesseract OCR GitHub](https://github.com/tesseract-ocr/tesseract).

Update the `pytesseract.pytesseract.tesseract_cmd` variable in the script to the path of the Tesseract executable on your system.

Example:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## Usage

1. **Place the PDF File**
   Ensure the input PDF form is located in the specified path (e.g., `input folder/Completed Dispute Form 3.pdf`).

2. **Run the Script**
   Execute the script with:
   ```bash
   python script_name.py
   ```
   Replace `script_name.py` with the actual filename of the script.

3. **Output**
   The extracted data will be saved in the specified Excel file path (e.g., `output folder/extracted_data_form3.xlsx`).

---

## Customization for Different PDF Forms

### Modify Field Mappings
To adapt the script for different forms:
- Update the `FIELDS` dictionary to include all the fields you want to extract.
- Modify the `field_mappings` dictionary to map field names in the form to keywords/phrases that identify them in the text.

Example:
```python
field_mappings = {
    "New Field Name": ["Keyword or phrase in the form"],
    ...
}
```

### Adjust Checkbox Detection
- Update the logic in the `handle_page_1_checkboxes` and `handle_page_2_checkboxes` functions to account for new checkbox labels or states.

### PDF Page Handling
If the form has additional pages or layouts:
- Extend the `update_fields_from_checkbox_results` function to handle new page numbers or checkbox patterns.

---

## Script Flow
1. **PDF Parsing**
   - Converts PDF pages to images using `PyMuPDF`.
2. **Text and Checkbox Extraction**
   - Extracts text using Tesseract OCR.
   - Detects and processes checkboxes based on contours and fills.
   ![Checkbox Extraction Example][checkbox_recognition.png]
3. **Field Matching**
   - Matches extracted data against predefined fields and mappings.
4. **Output to Excel**
   - Saves results to an Excel file using Pandas.

---

## Example Output
Extracted data is saved in an Excel file with two columns:
- **Field Name**: Name of the extracted field.
- **Extracted Value**: Corresponding value from the form.

---

## Contribution
Feel free to contribute by:
- Reporting issues.
- Adding support for new form layouts.
- Improving OCR accuracy or field mapping logic.

---

## License
This project is open-source and available under the [MIT License](LICENSE).


[def]: checkbox_extraction.png