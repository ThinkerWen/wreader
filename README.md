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
export WREADER_DATA_DIR="$HOME/wreader-data"
export WREADER_JWT_SECRET="$(openssl rand -hex 32)" # 请在密钥管理器中持久保存，重启时使用同一密钥
uv run python -m app.service.auth init # 首次运行交互设置至少 12 位密码
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```
浏览器打开 `http://127.0.0.1:8000` 即可搜索阅读小说。后端代码与配置位于 `app/`，前端源码位于 `web/`，`web/dist/` 是构建产物。Python 依赖由 `pyproject.toml` 与 `uv.lock` 管理。
<br>
### 二、Docker
```bash
docker build -t wreader .
docker volume create wreader-data
export WREADER_JWT_SECRET="$(openssl rand -hex 32)" # 安全保存，重启时使用同一密钥
docker run --rm -it -v wreader-data:/data/wreader wreader python -m app.service.auth init
docker run -d --name wreader -p 127.0.0.1:8000:8000 \
  -v wreader-data:/data/wreader -e WREADER_JWT_SECRET wreader
```
浏览器打开 `http://127.0.0.1:8000` 登录。容器使用 UID 10001，挂载宿主机目录时须确保该用户可读写。重启和升级时复用数据卷及同一 JWT 密钥。

CLI 长期令牌：`docker exec -it wreader python -m app.service.auth rotate-token` 生成并只显示一次，使用 `Authorization: Bearer 令牌`；再次轮换旧令牌即失效，`docker exec -it wreader python -m app.service.auth revoke-token` 可撤销。请勿将令牌写入仓库或日志。

公网部署须经反向代理强制 HTTPS，不记录授权头，并用 `WREADER_CORS_ORIGIN` 限制跨域来源。定期备份数据卷中的 `sources/`、`credentials.json` 和 SQLite 一致快照：停机复制整个目录或使用 SQLite backup API，不能只在线复制 WAL 数据库主文件。JWT 密钥单独安全保存。恢复时停止服务，备份当前目录，再还原至空目录，验证书源 YAML/JSON 与 SQLite 完整性，最后用原密钥启动。

## 前端开发
前端使用 React、HeroUI 与 Vite。需要 Node.js 22 及以上版本。在项目根目录启动后端，再在另一个终端运行：
```bash
cd web
pnpm install --frozen-lockfile
pnpm dev
```
打开终端提示的 Vite 地址进行开发；`/novel` 与 `/api` 请求会代理至本地 8000 端口。启动后端前须初始化密码并设置 JWT 密钥。运行 `pnpm build` 可更新后端托管的 `web/dist/`；Docker 构建会自动编译前端。书架与阅读进度保存在服务端数据目录；首次登录后可确认导入旧浏览器数据，旧数据不会自动删除。主题和字号仍保存在浏览器本地。