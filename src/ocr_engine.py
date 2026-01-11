import sys
import os
import pytesseract
from pdf2image import convert_from_path
import shutil
import platform

def configure_tesseract():
    # If user explicitly sets path (optional)
    env_path = os.environ.get("TESSERACT_CMD")
    if env_path:
        pytesseract.pytesseract.tesseract_cmd = env_path
        return

    # Windows
    if platform.system() == "Windows":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    else:
        # Linux / Docker
        tesseract_path = shutil.which("tesseract")
        if not tesseract_path:
            raise RuntimeError("Tesseract not found in PATH")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
configure_tesseract()
# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# # 1. Tesseract Path
# path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# pytesseract.pytesseract.tesseract_cmd = path_to_tesseract

# 2. Poppler Path (Your verified path)
#Sujal
#path_to_poppler = r"C:\Users\sujal\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"

#Sreenjoyee
path_to_poppler = r"C:\Users\BUTU2006\Desktop\poppler-25.12.0\Library\bin"

# 3. Languages
# Codes: 
# eng=English, fra=French, deu=German, spa=Spanish
# hin=Hindi, mar=Marathi, ben=Bengali
ACTIVE_LANGUAGES = 'eng+fra+deu+spa+hin+mar+ben'

def extract_text_from_pdf(pdf_path):
    """
    Extracts text using Tesseract with Multilingual support.
    Supports European and Indian languages.
    """
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return ""

    try:
        # Convert PDF to images
        images = convert_from_path(
            pdf_path, 
            dpi=300, 
            poppler_path=path_to_poppler
            #"/usr/bin" for Linux Docker
            #path_to_poppler for Windows
        )
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return ""

    full_text = []
    print(f"Scanning {len(images)} pages using languages: [{ACTIVE_LANGUAGES}]...")

    for i, image in enumerate(images):
        try:
            # Tesseract Magic
            # It will now look for characters from all 7 languages simultaneously
            text = pytesseract.image_to_string(image, lang=ACTIVE_LANGUAGES)
            
            # Basic cleanup
            text = text.strip()
            if text:
                full_text.append(text)

        except Exception as e:
            print(f"Error on page {i+1}: {e}")
            continue

    return "\n".join(full_text)

# ---------------------------------------------------------
# Test Block
# ---------------------------------------------------------
if __name__ == "__main__":
    test_pdf = r"report\reports\Spanish\Spanish_LIVER_normal_2.pdf"
    
    print(f"Testing OCR on: {test_pdf}")
    extracted_text = extract_text_from_pdf(test_pdf)
    
    print("\n--- Extracted Text Start ---")
    print(extracted_text)
    print("--- Extracted Text End ---")