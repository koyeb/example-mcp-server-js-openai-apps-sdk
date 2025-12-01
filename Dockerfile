FROM python:3.12-slim

WORKDIR /app

# Install required dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port Koyeb will use
EXPOSE 8000

# Koyeb sets PORT automatically — FastMCP must bind to it
ENV PORT=8000

CMD ["python", "main.py"]
