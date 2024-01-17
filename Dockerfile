FROM python:3.11.7 AS build

WORKDIR /app

ENV DOCKER 1

RUN apt update && \
    apt install ffmpeg -y

COPY . .

RUN pip install -r requirements.txt && \
    pip install typing-extensions


CMD ["python", "main.py"]
