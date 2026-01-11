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
