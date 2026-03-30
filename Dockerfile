# Gunakan Python slim
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file repo
COPY . .

# Set environment variable (opsional)
ENV FLASK_APP=app.py

# Jalankan Flask di port 8080 (HF Spaces detect port ini)
CMD ["python", "app.py"]