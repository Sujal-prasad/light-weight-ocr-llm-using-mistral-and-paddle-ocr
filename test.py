import sys
import os
# Adjust this import to match your folder structure
from src.ocr_engine import extract_text_from_pdf

# CHANGE THIS to the path of a specific file that is showing "Unknown"
failing_pdf = r"report/reports/English/English_BLOOD_abnormal_2.pdf"

if os.path.exists(failing_pdf):
    print(f"--- DEBUGGING: {failing_pdf} ---")
    raw_text = extract_text_from_pdf(failing_pdf)
    
    print("\n--- RAW TEXT START (First 600 chars) ---")
    # We print the raw string representation to see hidden \n or tabs
    print(repr(raw_text[:600])) 
    print("--- RAW TEXT END ---\n")
    
    print("--- NORMAL PRINT ---")
    print(raw_text[:600])
else:
    print("File not found! Check the path.")