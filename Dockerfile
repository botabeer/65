FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data && chmod 755 data

ENV PORT=8080
ENV DB_PATH=/app/data/botmesh.db
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
