# SoruSora

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