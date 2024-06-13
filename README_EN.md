# WReader
**[中文](https://github.com/ThinkerWen/wreader/blob/main/README.md)**

Online Experience：[wreader.onrender.com](https://wreader.onrender.com/)
## Introduction
Customize book-sources and set your own rules<br>
Automatically capture web page data, the rules are simple and easy to understand

## Usage
### 1. Source code
```bash
git clone https://github.com/ThinkerWen/wreader.git
cd wreader
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
Open `http://127.0.0.1:8000` in your browser to search and read novels
<br>
### 2. Docker（Not enabled yet）
```bash
docker run -d --name wreader -p 8001:8001 ThinkerWen/wreader
```
Open `http://127.0.0.1:8000` in your browser to search and read novels

## Other
Not good at front-end, thank you all for your PR contributions