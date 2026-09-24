# WReader
**[English](https://github.com/ThinkerWen/wreader/blob/main/README_EN.md)**

在线体验：[wreader.onrender.com](https://wreader.onrender.com/)
## 介绍
自定义书源，自己设置规则<br>
自动抓取网页数据，规则简单易懂

## 使用
### 一、下载源代码
```bash
git clone https://github.com/ThinkerWen/wreader.git
cd wreader
uv sync --python 3.12
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
浏览器打开 `http://127.0.0.1:8000` 即可搜索阅读小说。后端代码与配置位于 `app/`，前端源码位于 `web/`，`web/dist/` 是构建产物。Python 依赖由 `pyproject.toml` 与 `uv.lock` 管理。
<br>
### 二、Docker
```bash
docker build -t wreader .
docker run -d --name wreader -p 8000:8000 wreader
```
浏览器打开 `http://127.0.0.1:8000`即可搜索阅读小说

## 前端开发
前端使用 React、HeroUI 与 Vite。需要 Node.js 22 及以上版本。在项目根目录启动后端，再在另一个终端运行：
```bash
cd web
pnpm install --frozen-lockfile
pnpm dev
```
打开终端提示的 Vite 地址进行开发；`/novel` 请求会代理至本地 8000 端口。要更新后端托管的静态资源，运行 `pnpm build`，构建结果会写入 `web/dist/`。Docker 构建会自动编译前端，无需预先执行构建。书架、阅读进度和阅读设置保存在浏览器本地。