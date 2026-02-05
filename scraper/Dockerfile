FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/scraper

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python del scraper
COPY scraper/requirements.txt /app/scraper/requirements.txt
RUN pip install --no-cache-dir -r /app/scraper/requirements.txt

# Copiar código del scraper
COPY scraper /app/scraper

# El scraper carga .env desde /app/.env (raíz del proyecto dentro del contenedor)
WORKDIR /app/scraper

# Comando por defecto: ejecutar el pipeline para los últimos 2 días
CMD ["python", "main.py", "2"]

