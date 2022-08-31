# SoruSora

![python](https://img.shields.io/badge/python-v3.10-blue) ![test](https://github.com/SeoulSKY/SoruSora/actions/workflows/pytest.yml/badge.svg) ![lint](https://github.com/SeoulSKY/SoruSora/actions/workflows/pylint.yml/badge.svg) ![license](https://img.shields.io/github/license/SeoulSKY/SoruSora) ![SoruSora](https://img.shields.io/badge/SoruSora-online-green?style=flat&logo=discord)

Demonstration of `/movie play` command

![movie_play](https://user-images.githubusercontent.com/48105703/186945416-728905ae-562e-463d-92de-5cde435ac44c.gif)

## How to Set up and Run

* Install [python 3.10](https://www.python.org/downloads/), [Git Large File Storage](https://git-lfs.github.com), and [FFmpeg](https://ffmpeg.org/download.html)
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

## How to Contribute

Read [CONTRIBUTING.md](https://github.com/SeoulSKY/SoruSora/blob/master/docs/CONTRIBUTING.md) for details
