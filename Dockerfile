FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8080

CMD uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8080}
