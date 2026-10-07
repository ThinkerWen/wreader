import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.data import data_dir, prepare_data

PREFIX = "wr_"
ISSUER = "wreader"
PH = PasswordHasher()
BEARER = HTTPBearer(auto_error=False)
_failures: dict[str, tuple[int, float]] = {}


def secret() -> str:
    value = os.getenv("WREADER_JWT_SECRET", "")
    if len(value.encode()) < 32 or len(set(value)) < 16:
        raise RuntimeError("WREADER_JWT_SECRET 必须至少 32 字节")
    return value


def credentials_path() -> Path:
    return data_dir() / "credentials.json"


def load_credentials() -> dict:
    path = credentials_path()
    if not path.is_file():
        raise RuntimeError("请先通过 python -m app.service.auth init 初始化密码")
    if path.stat().st_mode & 0o077:
        raise RuntimeError("凭据文件权限过宽，请设为 0600")
    try:
        credentials = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError("凭据文件无法读取或格式无效") from exc
    if (
        not isinstance(credentials, dict)
        or not isinstance(credentials.get("password_hash"), str)
        or not isinstance(credentials.get("token_hash"), str)
    ):
        raise RuntimeError("凭据文件格式无效")
    return credentials


def save_credentials(credentials: dict) -> None:
    path = credentials_path()
    temporary = path.with_suffix(".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        json.dump(credentials, file)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)
    os.chmod(path, 0o600)


def issue_jwt() -> str:
    now = int(time.time())
    return jwt.encode({"iss": ISSUER, "aud": ISSUER, "sub": "owner", "iat": now, "exp": now + 3600}, secret(), algorithm="HS256")


def unauthorized() -> HTTPException:
    return HTTPException(401, "身份验证失败，请重新登录", headers={"WWW-Authenticate": "Bearer"})


def verify_token(token: str) -> bool:
    credentials = load_credentials()
    if token.startswith(PREFIX):
        digest = hashlib.sha256(token.encode()).hexdigest()
        return hmac.compare_digest(digest, credentials.get("token_hash", ""))
    try:
        claims = jwt.decode(
            token, secret(), algorithms=["HS256"], audience=ISSUER, issuer=ISSUER, options={"require": ["iss", "aud", "sub", "iat", "exp"]}
        )
        return claims["sub"] == "owner" and isinstance(claims["iat"], int) and claims["iat"] <= time.time()
    except (jwt.PyJWTError, KeyError, TypeError):
        return False


def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(BEARER)) -> None:
    if not credentials or credentials.scheme.lower() != "bearer" or not verify_token(credentials.credentials):
        raise unauthorized()


def login(password: str, request: Request) -> dict:
    address = request.client.host if request.client else "unknown"
    count, until = _failures.get(address, (0, 0))
    if count >= 5 and until > time.monotonic():
        raise HTTPException(429, "登录尝试过多，请稍后重试")
    try:
        PH.verify(load_credentials()["password_hash"], password)
    except VerifyMismatchError:
        if len(_failures) > 10000:
            _failures.clear()
        _failures[address] = (count + 1 if until > time.monotonic() else 1, time.monotonic() + 60)
        raise unauthorized() from None
    except (InvalidHashError, VerificationError) as exc:
        raise RuntimeError("密码哈希无效") from exc
    _failures.pop(address, None)
    return {"access_token": issue_jwt(), "token_type": "bearer", "expires_in": 3600}


def main() -> None:
    import argparse
    import getpass

    parser = argparse.ArgumentParser(description="WReader 本地凭据管理")
    parser.add_argument("action", choices=["init", "rotate-token", "revoke-token"])
    action = parser.parse_args().action
    prepare_data()
    if action == "init":
        if credentials_path().exists():
            parser.error("已初始化；不会覆盖现有密码")
        password = getpass.getpass("设置密码: ")
        if len(password) < 12 or password != getpass.getpass("确认密码: "):
            parser.error("密码至少 12 位且两次输入必须一致")
        save_credentials({"password_hash": PH.hash(password), "token_hash": ""})
    else:
        credentials = load_credentials()
        token = PREFIX + secrets.token_urlsafe(48) if action == "rotate-token" else ""
        credentials["token_hash"] = hashlib.sha256(token.encode()).hexdigest() if token else ""
        save_credentials(credentials)
        if token:
            print(token)


if __name__ == "__main__":
    main()
