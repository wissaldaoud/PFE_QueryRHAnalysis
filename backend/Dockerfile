FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Installer avec timeout étendu et retries
RUN pip install --no-cache-dir \
    --timeout=300 \
    --retries=5 \
    -r requirements.txt \
    --index-url https://pypi.org/simple/ || \
    pip install --no-cache-dir \
    --timeout=300 \
    --retries=5 \
    -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
