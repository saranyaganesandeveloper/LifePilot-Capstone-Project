# ------------------------------
# Stage 1 — Builder
# ------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ------------------------------
# Stage 2 — Runtime
# ------------------------------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Run as safer non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . /app

# Optional: no PYTHONPATH needed
ENV PYTHONPATH="/app"

EXPOSE 8080

USER appuser

CMD ["sh", "-c", "streamlit run ui/app.py --server.port=${PORT:-8080} --server.address=0.0.0.0"]
