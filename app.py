from flask import Flask, request, jsonify, render_template
import os
import ollama

# Ensure this import matches your actual file structure
from src.pdf_processor import process_medical_pdf

# -----------------------
# App setup
# -----------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost")
MODEL_NAME = "mistral"

# -----------------------
# Home (UI)
# -----------------------
@app.route("/")
def index():
    return render_template("index.html")

# -----------------------
# Upload PDF & Analyze
# -----------------------
@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    try:
        # Run OCR + analysis pipeline
        report_data = process_medical_pdf(pdf_path, fast_scan=False)
        return jsonify(report_data)
    except Exception as e:
        print(f"PDF PROCESSING ERROR: {e}")
        return jsonify({"error": "Failed to process PDF"}), 500

# -----------------------
# Chat Endpoint
# -----------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        messages = data.get("messages", [])

        if not messages:
            return jsonify({"error": "No messages provided"}), 400

        client = ollama.Client(host=f"http://{OLLAMA_HOST}:11434")

        # Call the model
        response = client.chat(
            model=MODEL_NAME,
            messages=messages
        )

        # ---------------- FIX APPLIED HERE ----------------
        # The Ollama Python library returns an object, not always a dict.
        # We check both dictionary access and object attribute access.
        
        reply_content = ""

        # Case 1: Response is a dictionary (common in some versions)
        if isinstance(response, dict):
            reply_content = response.get("message", {}).get("content", "")
        
        # Case 2: Response is an Object (The issue seen in your screenshot)
        # We access attributes directly using dot notation.
        else:
            try:
                reply_content = response.message.content
            except AttributeError:
                # Fallback if structure is unexpected
                reply_content = str(response)

        # Return clean JSON structure matching what frontend expects
        return jsonify({"message": {"content": reply_content}})

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------
# Run app
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)