from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from app.service import library
from app.service.auth import login, require_auth

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
    book, created = library.add_book(body.model_dump())
    response.status_code = 201 if created else 200
    return book


@protected.delete("/library/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    library.delete_book(book_id)


@protected.put("/library/books/{book_id}/progress")
def update_progress(book_id: int, body: ProgressInput):
    return library.set_progress(book_id, body.model_dump())


router.include_router(protected)
