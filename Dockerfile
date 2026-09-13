# Multi-stage / lightweight Python container for Zero-Trust AI Flight Recorder
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed (e.g. gcc, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source, tests, and configuration
COPY src/ src/
COPY tests/ tests/
COPY receipt.json .

# Set environment variables
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED="1"

# Expose Lending API HTTP port
EXPOSE 8000

# Healthcheck to verify service operational readiness
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: launch the Lending API server
CMD ["uvicorn", "lending_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
