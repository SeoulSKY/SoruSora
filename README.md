<div align="center">
    <img width="250" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/08369937-4e80-4acf-b979-164f39dff5d7">
    <h1>SoruSora</h1>
</div>

<blockquote align="center">
    AI-Powered Versatile Discord Bot - AI chat, Translator and more with a user-friendly and fully localized interface!
</blockquote>

<div align="center">
    <img src="https://img.shields.io/badge/Python-v3.11-blue">
    <img src="https://img.shields.io/badge/Node.js-v21.6-84ba64">
    <img src="https://img.shields.io/github/license/SeoulSKY/SoruSora">
    <img src="https://img.shields.io/badge/SoruSora-online-green?style=flat&logo=discord">
    <br>
    <img src="https://github.com/SeoulSKY/SoruSora/actions/workflows/pytest.yml/badge.svg">
    <img src="https://github.com/SeoulSKY/SoruSora/actions/workflows/pylint.yml/badge.svg">
    <img src="https://github.com/SeoulSKY/SoruSora/actions/workflows/eslint.yml/badge.svg">
    <br>
    <a href="https://discord.gg/kQZDJJB">
        <img src="http://invidget.switchblade.xyz/kQZDJJB">
    </a>
</div>

## Feature Overview

| `/movie` |
| -------------- |
| <img style="width: 500px; height: auto" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/b20ed72f-55e0-4787-9428-c1f925ab3a0a"> |

| `/chat` |
| -------------- |
| <img style="width: 500px; height: auto" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/7f3eacda-87ac-45e0-a80a-6e6458752c82"> |

| `/translator`  |
| ------------ |
| <img style="width: 500px; height: auto" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/5f84e863-c5c8-494f-a10d-064e3d9f64c7"> |

## Table of Contents

- [Why you should use SoruSora over the others?](#why-you-should-use-sorusora-over-the-others)
- [Commands](#commands)
  - [About](#about)
  - [Arcaea](#arcaea)
    - [/arcaea linkplay](#arcaea-linkplay)
  - [Chat](#chat)
    - [/chat set\_language](#chat-set_language)
    - [/chat clear](#chat-clear)
  - [Dice](#dice)
  - [Help](#help)
  - [Ping](#ping)
  - [Translator](#translator)
    - [/translator set\_languages](#translator-set_languages)
    - [/translator set\_channel\_languages](#translator-set_channel_languages)
    - [/translator clear\_languages](#translator-clear_languages)
    - [/translator clear\_channel\_languages](#translator-clear_channel_languages)
- [How to Set up and Run](#how-to-set-up-and-run)
  - [Setting Environment Variables](#setting-environment-variables)
  - [Description of each environment variable](#description-of-each-environment-variable)
  - [Running with Docker and Docker Compose (Recommended)](#running-with-docker-and-docker-compose-recommended)
  - [Running without Docker](#running-without-docker)
- [Architecture](#architecture)
- [How to Contribute](#how-to-contribute)
- [License](#license)

## Why you should use SoruSora over the others?

* `Transparency through Open Source`: SoruSora is not only entirely free but also [open source](https://github.com/SeoulSKY/SoruSora), ensuring transparency in its operations. Users can monitor and verify that SoruSora maintains ethical practices without any hidden agendas.
* `Localized to All 29 Discord Languages`: Everything including command names, descriptions, and instructions are automatically changed based on the current Discord language setting for each user. SoruSora is especially great if your server is international.
* `Intuitive User Interface`: Designed with a focus on user experience, it features intuitive elements like slash commands, providing a more straightforward alternative to traditional message commands. Moreover, SoruSora fully utilizes widgets such as Listbox and Buttons, eliminating the need for excessive typing and adding reactions to a message.

## Commands

### About

Show the information about SoruSora

### Arcaea

#### /arcaea linkplay

Create an embed to invite people to your Link Play.

### Chat

To chat with SoruSora, either mention her or reply to her.

#### /chat set_language

Update the chat language to the current discord language.

#### /chat clear

Clear the chat history between you and SoruSora.

### Dice

Roll some dice. The result is a random number between 1 and 6 with equal probability.

### Help

Teach you how to use SoruSora.

### Ping

Check the response time of SoruSora.

### Translator

It supports 43 languages, namely `Albanian`, `Arabic`, `Azerbaijani`, `Bengali`, `Bulgarian`, `Catalan`, `Chinese (Simplified)`, `Chinese (Traditional)`, `Czech`, `Danish`, `Dutch`, `English`, `Esperanto`, `Estonian`, `Filipino`, `Finnish`, `French`, `German`, `Greek`, `Hebrew`, `Hindi`, `Hungarian`, `Indonesian`, `Irish`, `Italian`, `Japanese`, `Korean`, `Latvian`, `Lithuanian`, `Malay`, `Norwegian (Bokmal)`, `Persian`, `Polish`, `Portuguese`, `Romanian`, `Russian`, `Slovak`, `Slovenian`, `Spanish`, `Swedish`, `Thai`, `Turkish` and `Ukrainian`.

#### /translator set_languages

Set languages to be translated for your messages.

#### /translator set_channel_languages

Set languages to be translated for this channel. Only available for server admins.

#### /translator clear_languages

Clear languages to be translated for your messages.

#### /translator clear_channel_languages

Clear languages to be translated for this channel. Only available for server admins.

## How to Set up and Run

### Setting Environment Variables

Create `.env` file, copy and paste all contents from `.env.example` file, and fill the values for your development environment.

### Description of each environment variable

| Name                                 | Description                                                                                                                                                                                                    |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BOT_TOKEN                            | [Token](https://discord.com/developers/applications) for your own Discord bot                                                                                                                                  |
| TEST_GUILD_ID                        | (Optional) Find your test server id following the [guide](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-). If provided, the bot runs in development mode. |
| CAI_TOKEN                            | Token for your Character AI account. Follow the [guide](https://github.com/realcoloride/node_characterai?tab=readme-ov-file#using-an-access-token) to learn how to acquire it.                                                                               |
| CAI_CHAR_ID                          | ID for the character in the Character AI. Follow the [guide](https://github.com/realcoloride/node_characterai?tab=readme-ov-file#finding-your-characters-id) to learn how to acquire it.                                                                          |


### Running with [Docker](https://www.docker.com) and [Docker Compose](https://docs.docker.com/compose/install/) (Recommended)

Run the following command:

```bash
# For Production
docker-compose pull && docker-compose up -d

# For Development
docker-compose -f docker-compose-dev.yml up --build -d
```

### Running without [Docker](https://www.docker.com)

* Install [pyenv](https://github.com/pyenv/pyenv#installation), [nvm](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating), [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/), [FFmpeg](https://ffmpeg.org/download.html) and [protoc](https://grpc.io/docs/protoc-installation/)

* [Start MongoDB](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/#run-mongodb-community-edition)

* Install Python 3.11.7

```bash
pyenv install 3.11.7
```

* Setup and activate the virtual environment

```bash
pyenv virtualenv 3.11.7 sorusora
pyenv local sorusora
```

* Install required Python packages

```bash
pyenv exec pip install -r requirements.txt
```

* Install Node.js 21.6

```bash
nvm install 21.6
nvm use 21.6
```

* Install required node packages

```bash
npm install
```

* Build Protocol Buffer files

```bash
chmod +x ./build-protos.sh && ./build-protos.sh
```

* Run `main.py`

```bash
pyenv exec python main.py
```

* In a separate terminal, Run the node server

```bash
# For Development
npm run dev

# For Production
npm run build
npm start
```

## Architecture

SoruSora is built with a microservices architecture, consisting of a Python and a Node.js backends. The two servers
communicate with each other using gRPC, a high-performance, open-source universal RPC framework. Database is managed by MongoDB server. Each server runs in a separate Docker container, and they are orchestrated using Docker Compose.

![Architecture](https://github.com/SeoulSKY/SoruSora/assets/48105703/bc1b2042-a14c-48c0-b968-91b881d735de)

## How to Contribute

Read [CONTRIBUTING.md](https://github.com/SeoulSKY/SoruSora/blob/master/docs/CONTRIBUTING.md) for details.

## License

SoruSora is licensed under the [MIT License](https://github.com/SeoulSKY/SoruSora/blob/master/LICENSE.md).
