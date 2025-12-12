FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies globally (no venv)
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY main.py .
COPY public/ ./public/

CMD ["python", "main.py"]
