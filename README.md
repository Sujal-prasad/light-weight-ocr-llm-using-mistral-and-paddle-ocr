To prepare an appropriate README for your project, it is important to highlight the core functionality: generating high-fidelity, multilingual medical reports (CBC, KFT, LFT) and interpreting them using a lightweight OCR-LLM pipeline.

Based on the code and workflow diagrams provided, here is a structured README for your repository.

---

# Multilingual Clinical Report Generation & Interpretation Pipeline

This project provides an automated pipeline for generating and interpreting synthetic medical reports in multiple languages (English, Spanish, German, and French). It utilizes a lightweight architecture designed for efficiency in low-compute environments, combining **Mistral-7B** for clinical reasoning and **PaddleOCR** for text extraction.

## 📑 Project Overview

The system handles three primary diagnostic categories with complete clinical parameters:

* **Complete Blood Count (CBC):** Includes Hemoglobin, WBC, Platelets, RBC, Hct, and MCV.
* **Kidney Function Test (KFT):** Includes Urea, Creatinine, BUN, Uric Acid, Calcium, Phosphorus, and Electrolytes (Na+, K+, Cl-).
* **Liver Function Test (LFT):** Includes Bilirubin (Total/Direct/Indirect), SGPT, SGOT, ALP, Total Protein, Albumin, and A/G Ratio.

## 🏗️ System Architecture

The pipeline follows a modular "Parsing-to-Interpretation" workflow:

1. **Multilingual Report Generation:** Synthetic reports are generated as PDFs with localized labels and clinical reference ranges.
2. **OCR Processing:** Uses **PaddleOCR** for high-accuracy clinical text parsing.
3. **Structured Representation:** Extracted data is mapped to a JSON schema for consistency.
4. **LLM Inference:** **Mistral-7B** interprets the structured data to provide clinical explanations.

## 🚀 Energy & Performance Optimization

A key focus of this project is sustainable deployment. The pipeline includes energy tracking to compare local execution versus cloud API calls:

* **Energy Monitoring:** Uses the Python `codecarbon` library to track GPU/CPU power consumption.
* **Hardware Evaluation:** Benchmarked against Peak RAM usage, CPU utilization, and Tokens per Second (TPS).
* **Deployment Logic:** Optimizes model size and inference energy to support energy-efficient claims.

## 🛠️ Installation & Usage

### 1. Prerequisites

* Python 3.8+
* ReportLab (for PDF generation)
* PaddleOCR & Mistral-7B access

### 2. Generate Reports

To generate the 96 standard reports (Normal and Abnormal across 4 languages), run:

```bash
python report_generation.py

```

### 3. Run Interpretation Pipeline

The pipeline will extract text from the generated PDFs and provide a structured clinical summary.

(to be updated)

## 📊 Sample Output

Generated reports follow a strict professional format including:

* **Hospital Header:** Government General Hospital branding.
* **Patient Demographics:** Name, Age/Sex, Patient ID, and Date.
* **Result Table:** Comparative view of Result vs. Reference Range with abnormal values highlighted.

---

# 🩺 Lightweight Medical OCR & Offline LLM Assistant

An offline-first desktop application designed for low-resource environments. It uses **PaddleOCR** for medical report digitisation and **Mistral-7B** for local intelligent analysis.

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

* **Python 3.10.11** (Standardized for stability)
* **Node.js** (LTS version recommended)
* **Ollama** (Running locally with `mistral` model pulled)
* **Git**

---

## 🚀 Getting Started

Follow these steps to set up the environment and run the application on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/Sujal-prasad/light-weight-ocr-llm-using-mistral-and-paddle-ocr.git
cd light-weight-ocr-llm-using-mistral-and-paddle-ocr

```

### 2. Setup Python Backend

We use a virtual environment to keep dependencies isolated.

```powershell
# Create the environment with Python 3.10
py -3.10 -m venv venv

# Activate the environment
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

```

### 3. Setup Electron Frontend

Install the desktop wrapper dependencies.

```bash
npm install

```

### 4. Run the Application

Actually, there is a small detail to clarify: **both** terminals should technically be in your project folder, but they handle different "engines."

* **Terminal 1 (Backend):** Needs the `venv` activated to run the Python/Flask server.
* **Terminal 2 (Frontend):** Does **not** strictly need the `venv` activated (because `npm` is a Node.js tool), but it must be in the project folder to find your `package.json`.

Here is exactly how to write those steps in your **README** so they are crystal clear:

---

### 🚀 Running the Application

To start the app, you need to open two separate terminals.

#### 1. Backend Server (Python + OCR)

Open **PowerShell**, navigate to the project folder, and run:

```powershell
.\venv\Scripts\activate
python app.py

```

> **Note:** Keep this window open. This terminal runs the Flask server that handles the OCR and AI logic.

#### 2. Frontend Desktop (Electron)

Open a **second terminal** (PowerShell or CMD) in the same project folder given venv is activate, run:

```powershell
npm start

```

> **Note:** This launches the actual desktop window. It will automatically connect to the backend running in the first terminal.

---
