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

# Jalankan app dengan gunicorn di port 7860
# --bind 0.0.0.0:7860 supaya HF Spaces bisa detect
# --workers 1 cukup untuk Free tier
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]