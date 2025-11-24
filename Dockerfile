# ------------------------------
# Stage 1 — Builder
# ------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1
ENV GEN_API_KEY=$GEN_API_KEY

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ------------------------------
# Stage 2 — Runtime
# ------------------------------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PATH=/usr/local/bin:$PATH

# Add PYTHONPATH so orchestrator.py & agents/ can be imported
ENV PYTHONPATH="/app:${PYTHONPATH:-}"

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . /app

ENV PORT=8080
EXPOSE 8080

USER appuser

CMD ["sh", "-c", "streamlit run ui/app.py --server.port=${PORT:-8080} --server.address=0.0.0.0"]
