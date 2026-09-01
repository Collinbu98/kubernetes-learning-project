FROM python:3.12-slim

RUN pip install psycopg[binary]

WORKDIR /app

COPY worker.py .

CMD ["python", "worker.py"]
