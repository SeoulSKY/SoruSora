FROM python:3.11.7 AS build

WORKDIR /app

RUN apt update && \
    apt install ffmpeg -y

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
