FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose controller port
EXPOSE 8001

# Add health check
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Command to run the application
CMD ["python", "run.py"]