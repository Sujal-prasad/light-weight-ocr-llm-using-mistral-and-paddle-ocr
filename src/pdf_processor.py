import json
import re
import sys
import os
import time
from langchain_community.llms import Ollama
from src.ocr_engine import extract_text_from_pdf

def clean_json_output(text):
    try:
        start_index = text.find('{')
        end_index = text.rfind('}')
        if start_index != -1 and end_index != -1:
            return text[start_index : end_index + 1]
        else:
            return text.strip()
    except Exception:
        return text.strip()

def detect_language_statistically(text):
    """
    Detects language based on Unicode character ranges.
    Returns: 'Bengali', 'Hindi', 'Marathi', 'English', etc.
    """
    counts = {
        'Bengali': 0,
        'Devanagari': 0, # Hindi/Marathi
        'English': 0
    }
    
    for char in text:
        code = ord(char)
        if 0x0980 <= code <= 0x09FF:
            counts['Bengali'] += 1
        elif 0x0900 <= code <= 0x097F:
            counts['Devanagari'] += 1
        elif 0x0041 <= code <= 0x005A or 0x0061 <= code <= 0x007A:
            counts['English'] += 1

    # Heuristic: If > 10% of chars are a specific script, assume that language
    total = sum(counts.values()) or 1
    
    if counts['Bengali'] / total > 0.1:
        return "Bengali"
    if counts['Devanagari'] / total > 0.1:
        # Simple heuristic to distinguish Hindi vs Marathi could go here
        # For now, default to Hindi/Marathi generic or assume Hindi if unsure
        return "Hindi" 
    
    return "English"

def extract_name_with_regex(text):
    header_text = text[:1000]
    header_text = re.sub(r'([A-Za-z\u0900-\u097F\u0980-\u09FF])\s([A-Za-z\u0900-\u097F\u0980-\u09FF])\s([A-Za-z\u0900-\u097F\u0980-\u09FF])', r'\1\2\3', header_text)
    
    patterns = [
        r"(?:Patient Name|Patient|Paciente|Name|Nom|Nombre)\s*[:\-\.]+\s*([^\n\r]+)",
        r"(?:Patient Name|Patient|Paciente|Name|Nom|Nombre)\s*\n\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"(?:नाव|रुग्ण|रुग्णाचे नाव|नांव|नाम|मरीज|रोगी)\s*[:\-\.]+\s*([^\n\r]+)",
        r"(?:নাম|রোগী|রোগীর নাম)\s*[:\-\.]+\s*([^\n\r]+)"
    ]

    STOP_WORDS = ["Age", "Date", "Gender", "Sex", "Dob", "Yrs", "Years", "वय", "लिंग", "বয়স", "লিঙ্গ"]
    BLOCK_LIST = ["HOSPITAL", "GENERAL", "CLINIC", "LABORATORY", "CENTRE", "DEPARTMENT"]

    for pattern in patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            raw_name = match.group(1).strip()
            for stop in STOP_WORDS:
                split_match = re.split(r'\s+' + stop, raw_name, flags=re.IGNORECASE)
                if len(split_match) > 1:
                    raw_name = split_match[0].strip()
            
            raw_name = re.sub(r'[|:,\._\n\r]+$', '', raw_name).strip()
            upper_name = raw_name.upper()
            if any(bad_word in upper_name for bad_word in BLOCK_LIST):
                continue 
            
            if 2 < len(raw_name) < 50 and not any(char.isdigit() for char in raw_name):
                return raw_name
    return None

def process_medical_pdf(pdf_path, fast_scan=False):
    # 1. OCR Extraction
    raw_text = extract_text_from_pdf(pdf_path)
    
    if not raw_text:
        return {
            "report_metadata": {"patient": {"name": "Unreadable File"}},
            "summary": {"critical_findings": False}
        }

    # 2. Extract Metadata (Regex + Statistical Language Detection)
    regex_name = extract_name_with_regex(raw_text)
    detected_lang = detect_language_statistically(raw_text) # <--- NEW FUNCTION
    
    # 3. Critical Check
    danger_keywords = ["HIGH", "LOW", "CRITICAL", "ABNORMAL", "POSITIVE"]
    upper_text = raw_text.upper()
    is_critical_regex = False
    for word in danger_keywords:
        if re.search(r'\b' + re.escape(word) + r'\b', upper_text):
            if word == "HIGH" and "HIGH DENSITY" in upper_text: continue 
            is_critical_regex = True
            break

    # --- SMART FALLBACK (Fast Mode) ---
    if fast_scan:
        return {
            "report_metadata": { 
                "patient": {"name": regex_name or "Unknown"}, 
                "language": detected_lang 
            },
            "summary": { "critical_findings": is_critical_regex },
            "medical_analysis": None, 
            "full_text": raw_text
        }

    # --- DOCTOR MODE (LLM) ---
    llm = Ollama(model="mistral")
    name_hint = f"(Hint: I detected the name '{regex_name}')" if regex_name else ""

    # We inject the detected language explicitly into the prompt
    prompt = f"""
    You are an experienced Medical Doctor.
    The document language is detected as: {detected_lang}.
    
    Your task is to analyze this report, extract facts AND provide professional medical advice.
    
    TEXT:
    {raw_text[:4000]}
    
    INSTRUCTIONS:
    1. **FIND THE PATIENT NAME**: {name_hint}.
    2. **DETECT CRITICAL VALUES**: Look for "High"/"Low".
    3. **DIAGNOSIS**: Provide a diagnosis in {detected_lang}.
    
    RETURN ONLY JSON:
    {{
        "report_metadata": {{
            "patient": {{ "name": "Extracted Name" }},
            "language": "{detected_lang}" 
        }},
        "summary": {{
            "critical_findings": true/false
        }},
        "medical_analysis": {{
            "diagnosis": "Detailed diagnosis in {detected_lang}",
            "treatment_plan": "Treatment plan in {detected_lang}",
            "lifestyle_advice": "Advice in {detected_lang}"
        }}
    }}
    """
    
    # --- RETRY LOGIC ---
    max_retries = 3
    ai_data = None

    for attempt in range(max_retries):
        try:
            print(f"LLM Attempt {attempt+1}...")
            response_text = llm.invoke(prompt)
            cleaned_json_text = clean_json_output(response_text)
            ai_data = json.loads(cleaned_json_text)
            break
        except Exception as e:
            print(f"Attempt {attempt+1} Failed: {e}")

    if not ai_data:
        ai_data = {
            "report_metadata": {"patient": {"name": regex_name or "Unknown"}},
            "summary": {"critical_findings": is_critical_regex},
            "medical_analysis": {"diagnosis": "Analysis Failed"}
        }
        
    # Ensure language is preserved in final output
    if "report_metadata" not in ai_data: ai_data["report_metadata"] = {}
    ai_data["report_metadata"]["language"] = detected_lang

    return {
        "report_metadata": ai_data.get("report_metadata", {}),
        "summary": ai_data.get("summary", {}),
        "medical_analysis": ai_data.get("medical_analysis", {}),
        "full_text": raw_text 
    }