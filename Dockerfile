FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 user
USER user

EXPOSE 7860

ENV FLASK_APP=app.py

CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]