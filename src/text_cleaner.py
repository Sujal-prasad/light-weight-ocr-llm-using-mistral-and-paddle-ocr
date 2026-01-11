import re

def normalize_text(text):
    text = text.replace(",", ".")
    text = text.replace(" :", ":")
    
    # NEW: Remove excessive newlines to treat the document as a stream of text
    # This helps if "Hemoglobin" is on line 1 and "12.5" is on line 2
    text = text.replace("\n", "  ") 
    
    text = re.sub(r"\s+", " ", text) # Collapse multiple spaces
    return text.strip()