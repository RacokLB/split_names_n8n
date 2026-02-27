FROM python:3.10-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install dependencies from pinned requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py validators.py ./

# Drop privileges — never run as root in production
USER appuser

# Health check — verify the API is responding
HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Run on port 8000 inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
