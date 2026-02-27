FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies (extend as needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command runs the MUST agent CLI
# Pass your GOOGLE_API_KEY at runtime, e.g.:
#   docker run -it --env-file .env telelink-ai
ENTRYPOINT ["python", "-m", "exec.main_must_agent"]

