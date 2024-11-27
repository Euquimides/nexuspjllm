FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PYTHONPATH=/app

# Expose the API port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "api.base_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]