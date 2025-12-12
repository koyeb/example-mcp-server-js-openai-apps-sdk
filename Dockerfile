FROM python:3.12-slim

WORKDIR /app

# Copy dependency file
COPY pyproject.toml ./

# Install dependencies with pip from pyproject.toml
RUN pip install --no-cache-dir mcp>=1.23.3 uvicorn>=0.38.0

# Copy application code
COPY main.py .
COPY public/ ./public/

CMD ["python", "main.py"]
