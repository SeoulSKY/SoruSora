FROM ghcr.io/puppeteer/puppeteer:22.4.1

USER root

SHELL ["/bin/bash", "-c"]

ENV NODE_VERSION=21.6

RUN wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash \
    && export NVM_DIR="$HOME/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] \
    && \. "$NVM_DIR/nvm.sh" \
    && [ -s "$NVM_DIR/bash_completion" ] \
    && \. "$NVM_DIR/bash_completion" \
    && nvm install $NODE_VERSION \
    && source $HOME/.bashrc \
    && nvm use $NODE_VERSION

WORKDIR /app

COPY package.json .

RUN npm install

COPY . .

RUN npm run build

CMD ["npm", "start"]
