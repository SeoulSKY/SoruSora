# SoruSora
![python](https://img.shields.io/badge/python-v3.10-blue) ![test](https://github.com/SeoulSKY/SoruSora/actions/workflows/pytest.yml/badge.svg) ![lint](https://github.com/SeoulSKY/SoruSora/actions/workflows/pylint.yml/badge.svg) ![license](https://img.shields.io/github/license/SeoulSKY/SoruSora) ![SoruSora](https://img.shields.io/badge/SoruSora-online-green?style=flat&logo=discord)

Demonstration of `/movie play` command

https://user-images.githubusercontent.com/48105703/186544955-db959520-62d6-493c-8d87-38bd44389d64.mp4



## How to Set up and Run

* Install [python 3.10](https://www.python.org/downloads/)
* Install [Git Large File Storage](https://git-lfs.github.com) if you haven't
* Set up and activate virtual environment

```bash
pip install virtualenv
virtualenv venv

# On Windows
venv\Scripts\activate.bat

# On Linux and macOS
source venv/bin/activate
```

* Install required packages

```bash
pip install -r requirements.txt
```

* Create `.env` file, copy and paste all contents from `.env.example` file, and fill the values for your development environment
* Run `main.py`

```
python3 main.py
```

## Documents

These are the documents that will be helpful to read to understand the codebase

* [discord.py](https://discordpy.readthedocs.io/en/latest/)
* [Firestore](https://firebase.google.com/docs/firestore/)
