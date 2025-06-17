FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

WORKDIR /app

RUN mkdir -p logs

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY src .
COPY entrypoint.sh .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
