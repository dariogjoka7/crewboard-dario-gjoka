FROM python:3.12-slim

WORKDIR /app

# Install PostgreSQL client for pg_isready / psql
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
RUN chmod +x start.sh

ENV PYTHONPATH=/app

CMD ["./start.sh"]