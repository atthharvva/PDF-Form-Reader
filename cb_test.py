import fitz  
import cv2
import numpy as np
from PIL import Image
import io
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def detect_checkboxes_with_text(pdf_path):
    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf):
            
            pix = page.get_pixmap(dpi=150)  
            img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))))

            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3
            )

            
            edges = cv2.Canny(binary, 100, 200)

            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            checkboxes = []  

            
            for contour in contours:
                
                x, y, w, h = cv2.boundingRect(contour)

                
                if 30 < w < 60 and 30 < h < 60:  
                    
                    checkbox_region = binary[y:y+h, x:x+w]

                    
                    non_zero_pixels = cv2.countNonZero(checkbox_region)
                    total_pixels = w * h
                    fill_ratio = non_zero_pixels / total_pixels

                    
                    state = "Checked" if fill_ratio > 0.3 else "Unchecked"

                    
                    checkboxes.append((x, y, w, h, state))

                    
                    text_region = img[y:y+h, x + w: x + w + 200] 

                    
                    extracted_text = pytesseract.image_to_string(text_region, config='--psm 6')
                    extracted_text = extracted_text.strip()

                    
                    if extracted_text:
                        print(f"Text next to checkbox at ({x}, {y}): {extracted_text}")

           
            for x, y, w, h, state in checkboxes:
                print(f"Page {page_num + 1} Checkbox at ({x}, {y}) is {state}")
                color = (0, 255, 0) if state == "Checked" else (0, 0, 255)
                cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)

            
            resized_img = cv2.resize(img, (800, 1000))  
            cv2.imshow(f"Page {page_num + 1}", resized_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


pdf_path = "input folder/Completed Dispute Form 3.pdf (2).pdf"  
detect_checkboxes_with_text(pdf_path)




# import fitz  
# import cv2
# import numpy as np
# from PIL import Image
# import io
# import pytesseract

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # Global dictionary to store results for each page
# page_results = {}

# def detect_checkboxes_with_text(pdf_path):
#     global page_results
#     with fitz.open(pdf_path) as pdf:
#         for page_num, page in enumerate(pdf):
#             pix = page.get_pixmap(dpi=150)
#             img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))))

#             gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#             binary = cv2.adaptiveThreshold(
#                 blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3
#             )
#             edges = cv2.Canny(binary, 100, 200)

#             contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#             checkboxes = []
#             results = {}

#             for contour in contours:
#                 x, y, w, h = cv2.boundingRect(contour)
#                 if 30 < w < 60 and 30 < h < 60:
#                     checkbox_region = binary[y:y+h, x:x+w]
#                     non_zero_pixels = cv2.countNonZero(checkbox_region)
#                     total_pixels = w * h
#                     fill_ratio = non_zero_pixels / total_pixels
#                     state = "checked" if fill_ratio > 0.3 else "unchecked"

#                     text_region = img[y:y+h, x + w: x + w + 200]
#                     extracted_text = pytesseract.image_to_string(
#                         text_region, config='--psm 6').strip()

#                     if extracted_text:  # Only include non-empty text
#                         key = f"{state.capitalize()}: {extracted_text}"
#                         results[key] = state
#                         print(f"Text next to checkbox at ({x}, {y}): {extracted_text}")

#             for x, y, w, h, state in checkboxes:
#                 print(f"Page {page_num + 1} Checkbox at ({x}, {y}) is {state}")
#                 color = (0, 255, 0) if state == "checked" else (0, 0, 255)
#                 cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)

#             # Save deduplicated and filtered results in the global dictionary
#             page_results[page_num + 1] = results
            
#             print(f"\nPage {page_num + 1} Results (State: [Text]):\n{results}\n")

#             resized_img = cv2.resize(img, (800, 1000))
#             cv2.imshow(f"Page {page_num + 1}", resized_img)
#             cv2.waitKey(0)
#             cv2.destroyAllWindows()

# pdf_path = "input folder/Completed Dispute Form 2.pdf (1).pdf"
# detect_checkboxes_with_text(pdf_path)

# # Access the saved page results later
# print("Page 1 Results:", page_results.get(1))
# print("Page 2 Results:", page_results.get(2))