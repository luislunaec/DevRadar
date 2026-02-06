FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/scraper

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cron \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Instalar crontab (ejecuta main.py cada día a las 23:59)
RUN crontab /app/scraper/crontab

# .env se monta en runtime en /app/.env (ver docker-compose)
# crond -f: cron en foreground para que el contenedor siga activo
CMD ["crond", "-f"]
