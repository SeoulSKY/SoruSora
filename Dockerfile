FROM python:3.10.12 AS build

WORKDIR /app

RUN apt update && \
    apt install ffmpeg -y

COPY . .

RUN pip install -r requirements.txt

RUN playwright install &&  \
    playwright install-deps

CMD ["python3", "main.py"]
