FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

ENTRYPOINT ["sh", "-c", "cd app/ && alembic upgrade head"]
