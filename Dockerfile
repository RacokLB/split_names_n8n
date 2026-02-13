FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pandas xlsxwriter openpyxl
COPY main.py .
# We run on port 8000 inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


