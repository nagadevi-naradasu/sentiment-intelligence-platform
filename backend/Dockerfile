FROM python:3.9-slim

WORKDIR /app

# Copy requirements from THIS directory (build context = backend/)
COPY requirements.txt .

RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy backend source code
COPY . .

CMD ["python", "main.py"]
