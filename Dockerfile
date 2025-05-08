FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/forest_app

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    graphviz && \
    rm -rf /var/lib/apt/lists/*

RUN curl -o /usr/local/bin/cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.15.3/cloud-sql-proxy.linux.amd64 && \
    chmod +x /usr/local/bin/cloud-sql-proxy

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY forest_app/ /app/forest_app/
COPY alembic.ini /app/alembic.ini
COPY alembic/ /app/alembic/
COPY entrypoint.sh /app/entrypoint.sh
COPY flexible_entrypoint.sh /app/flexible_entrypoint.sh

RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/flexible_entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]