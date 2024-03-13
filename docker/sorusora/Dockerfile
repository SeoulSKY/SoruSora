FROM python:3.11.7

WORKDIR /app

ENV DOCKER 1

ENV ROOT_PATH sorusora

ENV PROTO_PATH protos

RUN apt-get update && \
    apt-get install ffmpeg -y --no-install-recommends

COPY ${ROOT_PATH}/requirements.txt .

RUN pip install -r requirements.txt \
    && pip install typing-extensions

COPY ${PROTO_PATH} ${PROTO_PATH}

COPY ${ROOT_PATH}/build-protos.sh .

RUN chmod +x build-protos.sh \
    && ./build-protos.sh ${PROTO_PATH}

COPY ${ROOT_PATH} .

CMD ["python", "main.py"]
