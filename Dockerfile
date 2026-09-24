FROM node:22-bookworm-slim AS frontend

WORKDIR /web
RUN corepack enable
COPY web/package.json web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY web/ ./
RUN pnpm run build

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY app ./app
COPY --from=frontend /web/dist ./web/dist

ENV WREADER_DATA_DIR=/data/wreader
RUN useradd --system --uid 10001 --create-home wreader && mkdir -p /data/wreader && chown -R wreader:wreader /data/wreader /app
USER wreader
VOLUME ["/data/wreader"]

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
