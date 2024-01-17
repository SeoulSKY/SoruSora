<img width="250" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/08369937-4e80-4acf-b979-164f39dff5d7">

# SoruSora

![python](https://img.shields.io/badge/python-v3.11-blue) ![test](https://github.com/SeoulSKY/SoruSora/actions/workflows/pytest.yml/badge.svg) ![lint](https://github.com/SeoulSKY/SoruSora/actions/workflows/pylint.yml/badge.svg) ![license](https://img.shields.io/github/license/SeoulSKY/SoruSora) ![SoruSora](https://img.shields.io/badge/SoruSora-online-green?style=flat&logo=discord)

> AI-Powered Versatile Discord Bot

[![Discord Server Invite](http://invidget.switchblade.xyz/kQZDJJB)](https://discord.gg/kQZDJJB)


## Feature Overview

| `/movie` |
|--------------|
| <img style="width: 500px; height: auto" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/b20ed72f-55e0-4787-9428-c1f925ab3a0a"> |

| `/chat` |
|--------------|
| <img style="width: 500px; height: auto" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/7f3eacda-87ac-45e0-a80a-6e6458752c82"> |

| `/translator`  |
| ------------ |
| <img style="width: 500px; height: auto" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/5f84e863-c5c8-494f-a10d-064e3d9f64c7"> |

## How to Set up and Run

### Setting Environment Variables

Create `.env` file, copy and paste all contents from `.env.example` file, and fill the values for your development environment.

### Description of each environment variable

| Name                                 | Description                                                                                                                                                                                                    |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BOT_TOKEN                            | [Token](https://discord.com/developers/applications) for your own Discord bot                                                                                                                                  |
| TEST_GUILD_ID                        | (Optional) Find your test server id following the [guide](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-). If provided, the bot runs in development mode. |
| CAI_TOKEN                            | Token for your Character AI account. Follow the [guide](https://pycai.gitbook.io/welcome/api/values) to learn how to acquire it.                                                                               |
| CAI_CHAR_ID                          | ID for the character in the Character AI. Follow the [guide](https://pycai.gitbook.io/welcome/api/values) to learn how to acquire it.                                                                          |
| CAI_TGT                              | ID for the target in the Character AI. Its value starts with `internal_id:`. Run `scripts/cai_tgt.py` to get it.                                                                                               |


### Running with [Docker](https://www.docker.com) and [Docker Compose](https://docs.docker.com/compose/install/) (Recommended)

Run the following command:

```
docker-compose pull && docker-compose up
```

Optionally, you can add `-d` flag to run the docker container in detached mode.


If you want to build the docker image by yourself and run it, use the following commands:

```
docker-compose -f docker-compose-dev.yml up --build
```

### Running without [Docker](https://www.docker.com)

* Install [pyenv](https://github.com/pyenv/pyenv#installation), [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/) and [FFmpeg](https://ffmpeg.org/download.html)

* [Start MongoDB](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/#run-mongodb-community-edition)

* Install python 3.11.7

```bash
pyenv install 3.11.7
```

* Setup and activate virtual environment

```bash
pyenv virtualenv 3.11.7 sorusora
pyenv local sorusora
```

* Install required packages

```bash
pyenv exec pip install -r requirements.txt
```

* Run `main.py`

```bash
pyenv exec python main.py
```

## How to Contribute

Read [CONTRIBUTING.md](https://github.com/SeoulSKY/SoruSora/blob/master/docs/CONTRIBUTING.md) for details.
