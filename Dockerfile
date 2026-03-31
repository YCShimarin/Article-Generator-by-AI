# Gunakan Python slim
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install compiler dan dependency cairo
RUN apt-get update && apt-get install -y \
    gcc \
    libcairo2-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project
COPY . .

# Environment variable
ENV FLASK_APP=app.py

# Jalankan server
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]