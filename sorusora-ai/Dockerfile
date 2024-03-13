FROM node:21.6

ENV ROOT_PATH sorusora-ai

ENV PROTO_PATH protos

RUN apt-get update \
    && apt-get install chromium -y

ENV CHROME_PATH /usr/bin/chromium

WORKDIR /app

COPY ${ROOT_PATH}/package.json .

RUN npm install

COPY ${PROTO_PATH} ${PROTO_PATH}

COPY ${ROOT_PATH}/build-protos.sh .

RUN chmod +x build-protos.sh \
    && ./build-protos.sh ${PROTO_PATH}

COPY ${ROOT_PATH} .

RUN npm run build

CMD ["npm", "start"]
