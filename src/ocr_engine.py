import sys
import os
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
import shutil
import platform

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

# 1. Languages
# Codes: eng=English, fra=French, deu=German, spa=Spanish
# hin=Hindi, mar=Marathi, ben=Bengali
ACTIVE_LANGUAGES = 'eng+fra+deu+spa+hin+mar+ben'

def configure_environment():
    """
    Automatically configures Tesseract and Poppler paths based on the OS.
    """
    poppler_path = None
    
    # --- WINDOWS CONFIGURATION ---
    if platform.system() == "Windows":
        # 1. Tesseract Path (Update this if installed elsewhere)
        tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            print("Warning: Tesseract not found at default Windows path.")

        # 2. Poppler Path (Update this to YOUR specific path)
        # Try specific user paths first, then fall back to None (PATH)
        possible_poppler_paths = [
            r"C:\Users\sujal\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin",
            r"C:\Users\BUTU2006\Desktop\poppler-25.12.0\Library\bin",
            r"C:\Program Files\poppler-24.02.0\Library\bin" # Common install location
        ]
        
        for p in possible_poppler_paths:
            if os.path.exists(p):
                poppler_path = p
                print(f"✅ Poppler found at: {p}")
                break
        
        if not poppler_path:
            print("⚠️ Warning: Poppler path not found. Ensure it is in your System PATH.")

    # --- LINUX / DOCKER CONFIGURATION ---
    else:
        # In Docker, we installed these via apt-get, so they are in the system PATH.
        # We generally do NOT need to set paths manually.
        pass

    return poppler_path

# Initialize configuration once
POPPLER_PATH = configure_environment()

def extract_text_from_pdf(pdf_path):
    """
    Extracts text using Tesseract with Multilingual support.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found at {pdf_path}")
        return ""

    try:
        # Debug: Check if PDF is valid before converting
        info = pdfinfo_from_path(pdf_path, poppler_path=POPPLER_PATH)
        print(f"📄 Processing PDF: {pdf_path} ({info['Pages']} pages)")

        # Convert PDF to images
        images = convert_from_path(
            pdf_path, 
            dpi=300, 
            poppler_path=POPPLER_PATH
        )
    except Exception as e:
        print(f"❌ CRITICAL OCR ERROR: {e}")
        print("Tip: If on Windows, check 'ocr_engine.py' Poppler path.")
        print("Tip: If on Docker, ensure 'poppler-utils' is installed.")
        return ""

    full_text = []
    print(f"🔍 Scanning {len(images)} pages...")

    for i, image in enumerate(images):
        try:
            # Tesseract Magic
            text = pytesseract.image_to_string(image, lang=ACTIVE_LANGUAGES)
            
            # Basic cleanup
            text = text.strip()
            if text:
                full_text.append(text)

        except Exception as e:
            print(f"⚠️ Error reading page {i+1}: {e}")
            continue

    return "\n".join(full_text)

# ---------------------------------------------------------
# Test Block
# ---------------------------------------------------------
if __name__ == "__main__":
    # Test with a dummy file if run directly
    print("Running OCR Engine Test...")
    # You can add a specific test file path here to debug locally