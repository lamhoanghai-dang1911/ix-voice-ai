FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for audio decoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY ai-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy ai-service source code
COPY ai-service/app /app/app
# Copy shared contracts for fallback mock schemas
COPY contracts /app/contracts

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV STORAGE_LOCAL_DIR=/app/data/storage
ENV MODELS_CACHE_DIR=/app/data/models

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
