# # Base image -- experiment 2
# FROM python:3.11-slim

# # Prevent Python from writing pyc files and enable unbuffered output
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# ENV DEBIAN_FRONTEND=noninteractive

# # System dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     tesseract-ocr \
#     poppler-utils \
#     build-essential \
#     libffi-dev \
#     libssl-dev \
#     pkg-config \
#     rustc \
#     cargo \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Upgrade pip
# RUN pip install --upgrade pip setuptools wheel

# # Install PyTorch CPU-only (if you want GPU, change index-url)
# RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# # Copy only requirements first (for caching)
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the code
# COPY . .

# # Expose Jupyter port
# EXPOSE 8888

# # Default command
# CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root"]


# Base image -- experiment 3
FROM python:3.10-slim

# 1. Install system dependencies + C++ Build tools
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-mar \
    tesseract-ocr-ben \
    poppler-utils \
    libgl1 \
    build-essential \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Upgrade core pip tools FIRST
# This allows pip to find pre-compiled wheels for pandas/numpy
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 3. Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy project (respects .dockerignore)
COPY . .

ENV PYTHONPATH=/app
CMD ["python", "app.py"]