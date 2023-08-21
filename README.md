<img width="250" src="https://github.com/SeoulSKY/SoruSora/assets/48105703/08369937-4e80-4acf-b979-164f39dff5d7">

# SoruSora

![python](https://img.shields.io/badge/python-v3.10-blue) ![test](https://github.com/SeoulSKY/SoruSora/actions/workflows/pytest.yml/badge.svg) ![lint](https://github.com/SeoulSKY/SoruSora/actions/workflows/pylint.yml/badge.svg) ![license](https://img.shields.io/github/license/SeoulSKY/SoruSora) ![SoruSora](https://img.shields.io/badge/SoruSora-online-green?style=flat&logo=discord)

> AI-Powered Multi-Functional Discord Bot Dedicated to SeoulSKY's Discord Server

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

Create `.env` file, copy and paste all contents from `.env.example` file, and fill the values for your development
environment.

Following is the description of each environment variable:

| Name                                 | Description                                                                                                                                                                                                                                             |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BOT_TOKEN                            | [Token](https://discord.com/developers/applications) for your own Discord bot                                                                                                                                                                           |
| TEST_GUILD_ID                        | (Optional) Find your test server id following the [guide](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-). In the test server, the slash commands immediately get updated when you run the program |
| FIREBASE_TYPE                        | One of the value in the private key in your Firebase project. Go to `Project Settings` →  `Service accounts` → `Firebase Admin SDK` → `Generate new private key`                                                                                        |
| FIREBASE_PROJECT_ID                  | Same as above                                                                                                                                                                                                                                           |
| FIREBASE_PRIVATE_KEY_ID              | Same as above                                                                                                                                                                                                                                           |
| FIREBASE_PRIVATE_KEY                 | Same as above                                                                                                                                                                                                                                           |
| FIREBASE_CLIENT_EMAIL                | Same as above                                                                                                                                                                                                                                           |
| FIREBASE_CLIENT_ID                   | Same as above                                                                                                                                                                                                                                           |
| FIREBASE_AUTH_URI                    | Same as above                                                                                                                                                                                                                                           |
| FIREBASE_TOKEN_URI                   | Same as above                                                                                                                                                                                                                                           |
| FIREBASE_AUTH_PROVIDER_X509_CERT_URL | Same as above                                                                                                                                                                                                                                           |
| FIREBASE_CLIENT_X509_CERT_URL        | Same as above                                                                                                                                                                                                                                           |
| CAI_TOKEN                            | Token for your Character AI account. Follow the [guide](https://pycai.gitbook.io/welcome/api/values) to learn how to acquire it.                                                                                                                        |
| CAI_CHAR_ID                          | ID for the character in the Character AI. Follow the [guide](https://pycai.gitbook.io/welcome/api/values) to learn how to acquire it.                                                                                                                   |


### Running With [Docker](https://www.docker.com) (Recommended)

Run the following commands:

```
docker build -t sorusora .
docker run --rm -v ./logs:/app/logs --name sorusora sorusora
```

### Running Without [Docker](https://www.docker.com)

* Install [python 3.10](https://www.python.org/downloads/) and [FFmpeg](https://ffmpeg.org/download.html)
* Find the path to the Python executable


```bash
# On Windows
where python3.10

# On Linux or macOS
which python3.10
```

* Set up and activate virtual environment

```bash
/path/to/python3.10 -m venv venv

# On Windows
venv\Scripts\activate.bat

# On Linux or macOS
source venv/bin/activate
```

* Install required packages

```bash
pip install -r requirements.txt
```

* Setup playwright

```bash
playwright install
playwright install-dev
```

* Run `main.py`

```
python main.py
```

## How to Contribute

Read [CONTRIBUTING.md](https://github.com/SeoulSKY/SoruSora/blob/master/docs/CONTRIBUTING.md) for details
