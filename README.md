<div align="center">
    <img width="250" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/08369937-4e80-4acf-b979-164f39dff5d7">
    <h1>SoruSora</h1>
</div>

<blockquote align="center">
    AI-Powered Versatile Discord Bot - AI chat, Translator and more with a user-friendly and fully localized interface!
</blockquote>

<div align="center">
    <img src="https://img.shields.io/badge/Python-v3.11-blue">
    <img src="https://img.shields.io/github/license/SeoulSKY/SoruSora">
    <img src="https://img.shields.io/badge/SoruSora-online-green?style=flat&logo=discord">
    <br>
    <img src="https://github.com/SeoulSKY/SoruSora/actions/workflows/pytest.yml/badge.svg">
    <img src="https://github.com/SeoulSKY/SoruSora/actions/workflows/ruff.yml/badge.svg">
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
  - [Channel](#channel)
    - [/channel language](#channel-language)
    - [/channel translator](#channel-translator)
  - [Chat](#chat)
    - [/chat clear](#chat-clear)
    - [/chat token](#chat-token)
    - [/chat tutorial](#chat-tutorial)
  - [Dashboard](#dashboard)
  - [Dice](#dice)
  - [Help](#help)
  - [Ping](#ping)
  - [Translator](#translator)
- [How to Set up and Run](#how-to-set-up-and-run)
  - [Setting Environment Variables](#setting-environment-variables)
  - [Description of each environment variable](#description-of-each-environment-variable)
  - [Running with Docker (Recommended)](#running-with-docker-recommended)
  - [Running without Docker](#running-without-docker)
- [Architecture](#architecture)
- [How to Contribute](#how-to-contribute)
- [License](#license)

## Why you should use SoruSora over the others?

* `Transparency through Open Source`: SoruSora is not only entirely free but also [open source](https://github.com/SeoulSKY/SoruSora), ensuring transparency in its operations. Users can monitor and verify that SoruSora maintains ethical practices without any hidden agendas.
* `Privacy-first Design`: SoruSora is designed with privacy in mind. Any sensitive information is encrypted and stored securely, ensuring that user data is protected from unauthorized access.
* `Localized to All 29 Discord Languages`: Everything including command names, descriptions, and instructions are automatically changed based on the current Discord language setting for each user. SoruSora is especially great if your server is international.
* `Intuitive User Interface`: Designed with a focus on user experience, it features intuitive elements like slash commands, providing a more straightforward alternative to traditional message commands. Moreover, SoruSora fully utilizes widgets such as Listbox and Buttons, eliminating the need for excessive typing and adding reactions to a message.

## Commands

### About

Show the information about SoruSora

### Arcaea

#### /arcaea linkplay

Create an embed to invite people to your Link Play.

### Channel

#### /channel language

Set or remove the main language of the channels.

The translator will use the main language as the source language for all messages in the channels.

#### /channel translator

Set or remove a translator for channels.

For every message sent in the selected channels, SoruSora will translate the message into the selected languages and reply with the translations.

If the main language of the channels is not selected using `/channel language`, the language used in the message will be detected automatically.

It supports 43 languages, namely `Albanian`, `Arabic`, `Azerbaijani`, `Bengali`, `Bulgarian`, `Catalan`, `Chinese (Simplified)`, `Chinese (Traditional)`, `Czech`, `Danish`, `Dutch`, `English`, `Esperanto`, `Estonian`, `Filipino`, `Finnish`, `French`, `German`, `Greek`, `Hebrew`, `Hindi`, `Hungarian`, `Indonesian`, `Irish`, `Italian`, `Japanese`, `Korean`, `Latvian`, `Lithuanian`, `Malay`, `Norwegian (Bokmal)`, `Persian`, `Polish`, `Portuguese`, `Romanian`, `Russian`, `Slovak`, `Slovenian`, `Spanish`, `Swedish`, `Thai`, `Turkish` and `Ukrainian`.

### Chat

To chat with SoruSora, either mention her or reply to her.

#### /chat clear

Clear the chat history between you and SoruSora.

#### /chat token

Set the token that will be used to chat with SoruSora.

#### /chat tutorial

Teach you how to chat with SoruSora.

### Dashboard

Display the dashboard that contains configurations and statistics.

### Dice

Roll some dice. The result is a random number between 1 and 6 with equal probability.

### Help

Teach you how to use SoruSora.

### Ping

Check the response time of SoruSora.

### Translator

Set or remove a translator that translates all of your messages to other languages.

It supports 45 languages, namely `Albanian`, `Arabic`, `Azerbaijani`, `Basque`, `Bengali`, `Bulgarian`, `Catalan`, `Chinese (Simplified)`, `Chinese (Traditional)`, `Czech`, `Danish`, `Dutch`, `English`, `Esperanto`, `Estonian`, `Filipino`, `Finnish`, `French`, `Galician`, `German`, `Greek`, `Hebrew`, `Hindi`, `Hungarian`, `Indonesian`, `Irish`, `Italian`, `Japanese`, `Korean`, `Latvian`, `Lithuanian`, `Malay`, `Norwegian (Bokmal)`, `Persian`, `Polish`, `Portuguese`, `Romanian`, `Russian`, `Slovak`, `Slovenian`, `Spanish`, `Swedish`, `Thai`, `Turkish` and `Ukrainian`.


## How to Set up and Run

### Setting Environment Variables

Create `.env` file, copy and paste all contents from `.env.example` file, and fill the values for your development environment.

### Description of each environment variable

| Name                                 | Description                                                                                                                                                                                                    |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BOT_TOKEN                            | [Token](https://discord.com/developers/applications) for your own Discord bot                                                                                                                                  |
| TEST_GUILD_ID                        | (Optional) Find your test server id following the [guide](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-). If provided, the bot runs in development mode. |
| AI_TOKEN                           | Token for Gemini API. You can create one [here](https://makersuite.google.com/app/apikey) for free |
| ENCRYPTION_KEY                       | Key for encrypting and decrypting the user token |


### Running with [Docker](https://www.docker.com) (Recommended)

Run the following command:

```bash
# For Production
docker compose pull && docker compose up -d

# For Development
docker compose -f docker-compose-dev.yml up --build -d
```

### Running without [Docker](https://www.docker.com)

* Install [pyenv](https://github.com/pyenv/pyenv#installation), [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/) and [FFmpeg](https://ffmpeg.org/download.html)

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

* Run `main.py`

```bash
pyenv exec python src/main.py
```

## Architecture

![Architecture](https://github.com/user-attachments/assets/f1c80e87-1476-493b-bd59-195d33ec2a0b)

## How to Contribute

Read [CONTRIBUTING.md](https://github.com/SeoulSKY/SoruSora/blob/master/docs/CONTRIBUTING.md) for details.

## License

SoruSora is licensed under the [MIT License](https://github.com/SeoulSKY/SoruSora/blob/master/LICENSE.md).
