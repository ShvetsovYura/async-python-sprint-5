FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY src/ .

RUN pip3 install -r ./requirements.txt --no-cache-dir

