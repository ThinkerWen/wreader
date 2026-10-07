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
export WREADER_DATA_DIR="$HOME/wreader-data"
export WREADER_JWT_SECRET="$(openssl rand -hex 32)" # Store securely and reuse after restarts
uv run python -m app.service.auth init # Set a password of at least 12 characters
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000` to search and read novels. Backend code lives in `app/`, frontend source in `web/`, and built static assets in `web/dist/`. Python dependencies are managed with `pyproject.toml` and `uv.lock`.
<br>
### 2. Docker
```bash
docker build -t wreader .
docker volume create wreader-data
export WREADER_JWT_SECRET="$(openssl rand -hex 32)" # Save securely and reuse on restart
docker run --rm -it -v wreader-data:/data/wreader wreader python -m app.service.auth init
docker run -d --name wreader -p 127.0.0.1:8000:8000 \
  -v wreader-data:/data/wreader -e WREADER_JWT_SECRET wreader
```
Log in at `http://127.0.0.1:8000`. The container runs as UID 10001; ensure this user can write to bind-mounted directories. Reuse the same volume and JWT secret for upgrades.

Generate a long-lived CLI token (shown once) with `docker exec -it wreader python -m app.service.auth rotate-token`; send it as a Bearer authorization header. Rotating invalidates the old token; `docker exec -it wreader python -m app.service.auth revoke-token` revokes it.

For public deployments, enforce HTTPS via a reverse proxy, avoid logging authorization headers, and set `WREADER_CORS_ORIGIN` to the frontend origin. Back up `sources/`, `credentials.json`, and a consistent SQLite snapshot: stop the server and copy the whole directory, or use the SQLite backup API. Do not copy only the live WAL-mode database file. Store the JWT secret separately. To restore, stop the server, back up the current directory, restore into an empty directory, verify YAML/JSON sources and SQLite integrity, then restart with the original secret.

## Frontend development
The frontend uses React, HeroUI, and Vite. Node.js 22+ is required. Start the backend from the project root, then in another terminal run:
```bash
cd web
pnpm install --frozen-lockfile
pnpm dev
```
Open the Vite URL shown in the terminal. Requests to `/novel` and `/api` are proxied to the local backend on port 8000. Initialize a password and configure the JWT secret before starting the backend. Run `pnpm build` to update `web/dist/`; Docker builds the frontend automatically. The bookshelf and reading progress live in the server data directory. After logging in, you may confirm an import of legacy browser data, which is never automatically deleted. Theme and font size remain in the browser.