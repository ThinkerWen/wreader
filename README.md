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
浏览器打开 `http://127.0.0.1:8000` 即可搜索阅读小说。后端代码与配置在 `app/`，`web/` 是前端构建后的静态文件；前端源码见下方链接。依赖由 `pyproject.toml` 与 `uv.lock` 管理。
<br>
### 二、Docker
```bash
docker build -t wreader .
docker run -d --name wreader -p 8000:8000 wreader
```
浏览器打开 `http://127.0.0.1:8000`即可搜索阅读小说

## 前端
前端100%使用[Cursor](https://www.cursor.com/)制作：[wreader-web](https://github.com/ThinkerWen/wreader-web)

不擅前端，感谢大家多多贡献PR