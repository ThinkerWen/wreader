from fastapi import HTTPException

from app.config.settings import settings
from app.config.sources import SOURCE_ID
from app.core.processer.safety import validate_url
from app.repository import library as repository


def list_books() -> list[dict]:
    return repository.list_books()


def add_book(values: dict) -> tuple[dict, bool]:
    source_id = values["source_id"]
    if not SOURCE_ID.fullmatch(source_id) or source_id not in settings.SOURCE_CONFIG:
        raise HTTPException(422, "书源不存在或已禁用")
    validate_url(source_id, values["url"])
    return repository.add_book(values)


def delete_book(book_id: int) -> None:
    repository.delete_book(book_id)


def set_progress(book_id: int, values: dict) -> dict:
    with repository.connection() as db:
        book = repository.fetch_book(db, book_id)
    if not book:
        raise HTTPException(404, "书籍不存在")
    if book["source_id"] in settings.SOURCE_CONFIG:
        validate_url(book["source_id"], values["chapter_url"])
    migrated = values.get("migrated_updated_at")
    if migrated is not None and not (946684800000 <= migrated <= repository.now_ms() + 300000):
        raise HTTPException(422, "迁移时间戳无效")
    result = repository.set_progress(book_id, values)
    if result is None:
        raise HTTPException(404, "书籍不存在")
    return result
