import ollama
import sys
import os
import glob
import json
from pathlib import Path

# -------------------------
# Ollama Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost")
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:11434"
# -------------------------
# Ensure project root is in sys.path
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.pdf_processor import process_medical_pdf
    print("Import succeeded!")
except ModuleNotFoundError as e:
    print("Import FAILED:", e)
    sys.exit(1)

# -------------------------
# Configuration
# -------------------------
REPORTS_DIR = os.path.join(PROJECT_ROOT, "report", "reports") 
MODEL_NAME = "mistral"

# -------------------------
# Helper: Find and Process All PDFs (Recursive)
# -------------------------
def scan_and_analyze_reports(folder_path):
    search_pattern = os.path.join(folder_path, "**", "*.pdf")
    pdf_files = glob.glob(search_pattern, recursive=True)
    
    if not pdf_files:
        print(f"No PDFs found in: {folder_path}")
        return []

    print(f"\nFound {len(pdf_files)} reports. scanning headers (Fast Mode)...\n")
    
    analyzed_data = []

    for i, pdf_path in enumerate(pdf_files):
        filename = os.path.basename(pdf_path)
        rel_path = os.path.relpath(pdf_path, folder_path)
        
        # print(f"[{i+1}/{len(pdf_files)}] Scanning: {rel_path}...") # Optional: Comment out for cleaner UI
        
        try:
            # --- CRITICAL CHANGE: ENABLE FAST SCAN ---
            # We use fast_scan=True to skip the AI loop for the menu.
            # This makes scanning 84 files take ~2 mins instead of 30 mins.
            report_json = process_medical_pdf(pdf_path, fast_scan=True)
            
            # Extract basic info for the menu
            patient_name = report_json.get('report_metadata', {}).get('patient', {}).get('name') or "Unknown Patient"
            
            # Check for critical flags
            is_critical = report_json.get('summary', {}).get('critical_findings', False)
            status = "CRITICAL ⚠️" if is_critical else "Normal ✅"
            
            analyzed_data.append({
                "id": i + 1,
                "display_name": rel_path, 
                "file_path": pdf_path, # Store full path for re-processing later
                "patient": patient_name,
                "status": status,
                "full_json": report_json
            })
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    return analyzed_data

# -------------------------
# Main Application Flow
# -------------------------
def main():
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        client.list()
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        sys.exit(1)

    print("Medical Diagnostic Assistant Initialized.")

    # 1. Fast Scan (Menu Building)
    reports = scan_and_analyze_reports(REPORTS_DIR)
    
    if not reports:
        print("No valid reports available to discuss.")
        sys.exit(0)

    # 2. Main Menu Loop
    while True:
        print("\n" + "="*80)
        print(f" {'ID':<4} {'Patient Name':<25} {'Status':<12} {'File Location'}")
        print("="*80)
        
        for r in reports:
            # Truncate name if too long to keep table aligned
            p_name = (r['patient'][:22] + '..') if len(r['patient']) > 22 else r['patient']
            print(f" {r['id']:<4} {p_name:<25} {r['status']:<12} {r['display_name']}")
        
        print("="*80)
        
        selection = input("\nEnter Report # to discuss (or 'exit'): ").strip()
        
        if selection.lower() in ['exit', 'quit']:
            break
            
        selected_report = next((item for item in reports if str(item["id"]) == selection), None)
        
        if not selected_report:
            print("Invalid selection.")
            continue

        language = input(f"Language for discussion (e.g., English, Hindi): ").strip() or "English"
        
        # --- CRITICAL CHANGE: DOCTOR MODE ACTIVATION ---
        print(f" Activating Doctor AI for {selected_report['patient']}... (This takes ~20s)")
        
        # We re-process ONLY the selected file with fast_scan=False
        # This triggers the prompt you just edited (Diagnosis, Treatment, etc.)
        detailed_json = process_medical_pdf(selected_report['file_path'], fast_scan=False)
        
        # Update the report object with the new deep analysis
        selected_report['full_json'] = detailed_json
        
        # Start Chat
        start_chat_session(client, selected_report, language)

# -------------------------
# Chat Logic
# -------------------------
def start_chat_session(client, report_data, language):
    print(f"\nStarting session for: {report_data['patient']} ({language})...")
    print("(Type 'back' to return to list)\n")

    report_context = json.dumps(report_data['full_json'], indent=2)
    
    # Updated System Prompt for Doctor Persona
    system_prompt = (
        f"You are an experienced Medical Doctor and Assistant. The user prefers to speak in {language}.\n"
        f"DATA:\n```json\n{report_context}\n```\n"
        "RULES:\n"
        "1. Use the 'medical_analysis' section (Diagnosis/Treatment) from the JSON if available.\n"
        "2. If the user asks for a diagnosis, explain the findings in detail.\n"
        "3. Provide lifestyle and dietary advice based on the 'lifestyle_advice' field.\n"
        f"4. Reply in {language}."
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    
    messages.append({"role": "user", "content": f"Give me a detailed diagnosis and treatment plan in {language}."})

    try:
        response = client.chat(model=MODEL_NAME, messages=messages)
        print(f"Dr. AI: {response['message']['content']}\n")
        messages.append(response['message'])
    except Exception as e:
        print(f"AI Error: {e}")

    while True:
        user_input = input("User: ").strip()
        if user_input.lower() in ['back', 'return', 'exit']:
            break
        
        messages.append({"role": "user", "content": user_input})
        try:
            response = client.chat(model=MODEL_NAME, messages=messages)
            print(f"\nDr. AI: {response['message']['content']}\n")
            messages.append(response['message'])
        except Exception as e:
            print(f"Ollama Error: {e}")

# -------------------------
# Experiment Helper: Callable Pipeline
# -------------------------
def run_pipeline_for_experiment(pdf_path, language="English", model="mistral"):
    """
    Runs the full OCR + Doctor AI pipeline for a single file.
    Returns the parsed JSON and raw text length (to calculate tokens roughly).
    Used by external scripts (e.g., Jupyter Notebooks) for benchmarking.
    """
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
    except:
        return {"error": "Ollama connection failed"}
    
    # 1. OCR & Critical Scan (The heavy lifting)
    # Step A: Get Text & Metadata (Force deep scan to simulate full workload)
    initial_data = process_medical_pdf(pdf_path, fast_scan=False) 
    
    # Step B: Force Doctor Analysis (Inference)
    # We manually replicate the chat session logic to ensure consistent testing
    report_context = json.dumps(initial_data.get('full_json', initial_data), indent=2)
    
    system_prompt = (
        f"You are an experienced Medical Doctor. "
        f"DATA:\n```json\n{report_context}\n```\n"
        f"Reply in {language}."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Give me a detailed diagnosis and treatment plan in {language}."}
    ]
    
    # Run Inference
    response = client.chat(model=model, messages=messages)
    
    return {
        "status": "success",
        "output_length": len(response['message']['content']),
        "input_length": len(system_prompt),
        "full_response": response['message']['content']
    }

if __name__ == "__main__":
    main()