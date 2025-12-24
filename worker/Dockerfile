FROM python:3.9-slim

WORKDIR /app

# 1️⃣ Copy only requirements (rarely changes)
COPY requirements.txt .

# 2️⃣ Install deps (cached forever unless requirements.txt changes)
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# 3️⃣ Now copy the actual code (changes often)
COPY . .

CMD ["python", "worker.py"]
