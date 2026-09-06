FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# on n'execute pas l'application en root
RUN useradd --create-home --uid 10001 todo && chown -R todo:todo /app
USER todo

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s \
  CMD curl -fs http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:create_app()"]
