from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from app.config.auth import login, require_auth
from app.core.configuration.settings import settings
from app.core.util.source_tool import SOURCE_ID
from app.service import library

router = APIRouter(prefix="/api")
protected = APIRouter(dependencies=[Depends(require_auth)])


class LoginInput(BaseModel):
    password: str = Field(min_length=1, max_length=1024)


class BookInput(BaseModel):
    source_id: str = Field(min_length=32, max_length=32)
    url: str = Field(min_length=1, max_length=2048)
    name: str = Field(min_length=1, max_length=256)
    author: str | None = Field(default=None, max_length=256)
    size: str | None = Field(default=None, max_length=256)
    status: str | None = Field(default=None, max_length=256)
    cover_url: str | None = Field(default=None, max_length=2048)
    classify: str | None = Field(default=None, max_length=256)
    introduce: str | None = Field(default=None, max_length=4096)
    last_update_time: str | None = Field(default=None, max_length=256)
    last_chapter_name: str | None = Field(default=None, max_length=256)


class ProgressInput(BaseModel):
    chapter_url: str = Field(min_length=1, max_length=2048)
    chapter_name: str = Field(min_length=1, max_length=256)
    chapter_index: int = Field(ge=0, le=1000000, strict=True)
    migrated_updated_at: int | None = Field(default=None, strict=True)


@router.post("/auth/login")
def auth_login(body: LoginInput, request: Request):
    return login(body.password, request)


@protected.get("/library")
def get_library():
    return {"books": library.list_books()}


@protected.post("/library/books")
def add_book(body: BookInput, response: Response):
    if not SOURCE_ID.fullmatch(body.source_id) or body.source_id not in settings.SOURCE_CONFIG:
        raise HTTPException(422, "书源不存在或已禁用")
    from app.core.net.safety import validate_url

    validate_url(body.source_id, body.url)
    book, created = library.add_book(body.model_dump())
    response.status_code = 201 if created else 200
    return book


@protected.delete("/library/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    library.delete_book(book_id)


@protected.put("/library/books/{book_id}/progress")
def update_progress(book_id: int, body: ProgressInput):
    from app.core.net.safety import validate_url

    with library.connection() as db:
        book = library.fetch_book(db, book_id)
    if not book:
        raise HTTPException(404, "书籍不存在")
    if book["source_id"] in settings.SOURCE_CONFIG:
        validate_url(book["source_id"], body.chapter_url)
    if body.migrated_updated_at is not None and not (946684800000 <= body.migrated_updated_at <= library.now_ms() + 300000):
        raise HTTPException(422, "迁移时间戳无效")
    result = library.set_progress(book_id, body.model_dump())
    if result is None:
        raise HTTPException(404, "书籍不存在")
    return result


router.include_router(protected)
