FROM python:3.11.7

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DOCKER 1

RUN apt-get update && \
    apt-get install ffmpeg -y --no-install-recommends

COPY . .

CMD ["uv", "run", "src/main.py"]
