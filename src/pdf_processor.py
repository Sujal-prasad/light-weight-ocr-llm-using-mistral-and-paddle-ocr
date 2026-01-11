import json
import re
import sys
import os
from langchain_community.llms import Ollama
from src.ocr_engine import extract_text_from_pdf

def clean_json_output(text):
    """Removes markdown formatting from LLM response."""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

def extract_name_with_regex(text):
    """
    SMART NAME EXTRACTOR (Updated for Marathi & Bengali + Fixes Squashed Names)
    """
    # 1. Clean OCR artifacts
    header_text = text[:1000]
    
    # FIX: Require 3 characters to trigger "un-spacing" (e.g., "N a m e" -> "Name")
    # This prevents "Sarah Miller" from becoming "SarahMiller"
    header_text = re.sub(r'([A-Za-z\u0900-\u097F\u0980-\u09FF])\s([A-Za-z\u0900-\u097F\u0980-\u09FF])\s([A-Za-z\u0900-\u097F\u0980-\u09FF])', r'\1\2\3', header_text)
    
    # 2. Define Patterns
    patterns = [
        # English / European (Name, Patient, Nom, Nombre)
        r"(?:Patient Name|Patient|Paciente|Name|Nom|Nombre)\s*[:\-\.]+\s*([^\n\r]+)",
        r"(?:Patient Name|Patient|Paciente|Name|Nom|Nombre)\s*\n\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
        
        # --- MARATHI & HINDI ---
        r"(?:नाव|रुग्ण|रुग्णाचे नाव|नांव|नाम|मरीज|रोगी)\s*[:\-\.]+\s*([^\n\r]+)",
        
        # --- BENGALI ---
        r"(?:নাম|রোগী|রোগীর নাম)\s*[:\-\.]+\s*([^\n\r]+)"
    ]

    # 3. Stopwords
    STOP_WORDS = [
        "Age", "Date", "Gender", "Sex", "Dob", "Yrs", "Years", 
        "Alter", "Datum", "Geschlecht", "Sexe", "Edad", "Fecha", "Sexo",
        "वय", "लिंग", "दिनांक", "तारीख",
        "বয়স", "লিঙ্গ", "তারিখ"
    ]
    
    # 4. Blocklist
    BLOCK_LIST = [
        "HOSPITAL", "GENERAL", "CLINIC", "LABORATORY", "CENTRE", "DEPARTMENT", 
        "HOPITAL", "KRANKENHAUS", "GOBIERNO", "GOVERNMENT", "INFORME", "MEDICO", 
        "DAVAKHANA", "RUGNALAYA", "ASPATAAL"
    ]

    for pattern in patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            raw_name = match.group(1).strip()
            
            # --- CLEANING LOGIC ---
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

    # 2. Python Extraction (Fast)
    regex_name = extract_name_with_regex(raw_text)
    
    # 3. Critical Check (Python Safety Net)
    danger_keywords = ["HIGH", "LOW", "CRITICAL", "ABNORMAL", "POSITIVE", 
                       "HAUT", "BAS", "ANORMAL", "POSITIF", 
                       "HOCH", "NIEDRIG", "KRITISCH", "POSITIV", 
                       "ALTO", "BAJO", "ANORMAL", "POSITIVO"]
    
    upper_text = raw_text.upper()
    is_critical_regex = False
    
    for word in danger_keywords:
        if re.search(r'\b' + re.escape(word) + r'\b', upper_text):
            if word == "HIGH" and "HIGH DENSITY" in upper_text: continue 
            is_critical_regex = True
            break

    # --- SMART FALLBACK LOGIC ---
    # If fast_scan is ON, we usually return immediately.
    # BUT if regex_name is None (Unknown), we force the AI to run to find it.
    if fast_scan:
        if regex_name: 
            # Success! Return data instantly without touching the AI
            folder_name = os.path.basename(os.path.dirname(pdf_path))
            return {
                "report_metadata": { 
                    "patient": {"name": regex_name}, 
                    "language": folder_name 
                },
                "summary": { "critical_findings": is_critical_regex },
                "medical_analysis": None, 
                "full_text": raw_text
            }
        else:
            # Fallback: Regex failed. We MUST run AI even in fast mode to find the name.
            # (Pass through to the AI block below)
            pass 

    # --- DOCTOR MODE / FALLBACK MODE ---
    llm = Ollama(model="mistral")
    name_hint = f"(Hint: I detected the name '{regex_name}')" if regex_name else ""

    # UPDATED PROMPT: Request Advice AND provide JSON fields for it
    prompt = f"""
    You are an experienced Medical Doctor.
    
    Your task is to analyze this report, extract facts AND provide professional medical advice and answer subsequent questions from the user , analysing individual queries and doubts and provide insightful answers
    
    TEXT:
    {raw_text[:4000]}
    
    INSTRUCTIONS:
    1. **FIND THE PATIENT NAME**: {name_hint}.
    2. **DETECT CRITICAL VALUES**: Look for "High"/"Low".
    3. **DIAGNOSIS & PLAN**: 
       - Based on the values, provide a potential diagnosis.
       - Suggest a basic treatment plan (medication types, further tests).
       - Recommend lifestyle changes (diet, exercise).
    
    RETURN ONLY JSON:
    {{
        "report_metadata": {{
            "patient": {{ "name": "Extracted Name" }},
            "language": "Detected Language"
        }},
        "summary": {{
            "critical_findings": true/false
        }},
        "medical_analysis": {{
            "diagnosis": "Detailed diagnosis here",
            "treatment_plan": "Suggested medications or next steps",
            "lifestyle_advice": "Diet and exercise recommendations",
            "suppliments_advice": "Any recommended supplements",
            "follow_up_tests": "Any suggested follow-up tests",
            "additional_info": "Any additional relevant information"
            
        }}
    }}
    """
    
    try:
        response_text = llm.invoke(prompt)
        ai_data = json.loads(clean_json_output(response_text))
        
        # Merge Regex Logic
        ai_name = ai_data.get("report_metadata", {}).get("patient", {}).get("name")
        if (not ai_name or "Unknown" in ai_name) and regex_name:
            ai_data["report_metadata"]["patient"]["name"] = regex_name
            
        if is_critical_regex:
            ai_data["summary"]["critical_findings"] = True

    except Exception:
        ai_data = {
            "report_metadata": {"patient": {"name": regex_name if regex_name else "Unknown"}},
            "summary": {"critical_findings": is_critical_regex},
            "medical_analysis": {"diagnosis": "AI Analysis Failed", "treatment_plan": "N/A"}
        }

    return {
        "report_metadata": ai_data.get("report_metadata", {}),
        "summary": ai_data.get("summary", {}),
        "medical_analysis": ai_data.get("medical_analysis", {}),
        "full_text": raw_text 
    }