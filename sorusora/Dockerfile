FROM python:3.11.7 AS build

WORKDIR /app

ENV DOCKER 1

RUN apt-get update && \
    apt-get install ffmpeg -y --no-install-recommends

COPY requirements.txt .

RUN pip install -r requirements.txt \
    && pip install typing-extensions

COPY . .

CMD ["python", "main.py"]
