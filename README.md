# SoruSora

![python](https://img.shields.io/badge/python-v3.10-blue) ![test](https://github.com/SeoulSKY/SoruSora/actions/workflows/pytest.yml/badge.svg) ![lint](https://github.com/SeoulSKY/SoruSora/actions/workflows/pylint.yml/badge.svg) ![license](https://img.shields.io/github/license/SeoulSKY/SoruSora) ![SoruSora](https://img.shields.io/badge/SoruSora-online-green?style=flat&logo=discord)

> Discord bot dedicate to SeoulSKY's Discord server

[![Discord Server Invite](https://invite.caspertheghost.me?inviteCode=kQZDJJB)](https://discord.gg/kQZDJJB)

# Feature Overview

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

* Install [python 3.10](https://www.python.org/downloads/), [Git Large File Storage](https://git-lfs.github.com), and [FFmpeg](https://ffmpeg.org/download.html)
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

* Create `.env` file, copy and paste all contents from `.env.example` file, and fill the values for your development environment
* Run `main.py`

```
python main.py
```

## How to Contribute

Read [CONTRIBUTING.md](https://github.com/SeoulSKY/SoruSora/blob/master/docs/CONTRIBUTING.md) for details
