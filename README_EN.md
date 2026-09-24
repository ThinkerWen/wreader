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
uv sync --python 3.12
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open `http://127.0.0.1:8000` to search and read novels. Backend code lives in `app/`, frontend source in `web/`, and built static assets in `web/dist/`. Python dependencies are managed with `pyproject.toml` and `uv.lock`.
<br>
### 2. Docker
```bash
docker build -t wreader .
docker run -d --name wreader -p 8000:8000 wreader
```
Open `http://127.0.0.1:8000` in your browser to search and read novels

## Frontend development
The frontend uses React, HeroUI, and Vite. Node.js 22+ is required. Start the backend from the project root, then in another terminal run:
```bash
cd web
pnpm install --frozen-lockfile
pnpm dev
```
Open the Vite URL shown in the terminal. Requests to `/novel` are proxied to the local backend on port 8000. Run `pnpm build` to update `web/dist/` for the backend to serve. Docker builds the frontend automatically. Your bookshelf, reading progress, and reader preferences are stored locally in the browser.