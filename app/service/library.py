import sqlite3
import time
from contextlib import contextmanager

from app.config.data import data_dir

FIELDS = (
    "source_id",
    "url",
    "name",
    "author",
    "size",
    "status",
    "cover_url",
    "classify",
    "introduce",
    "last_update_time",
    "last_chapter_name",
)


def now_ms() -> int:
    return time.time_ns() // 1_000_000


@contextmanager
def connection():
    db = sqlite3.connect(data_dir() / "wreader.db", timeout=5)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=5000")
    try:
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def initialize() -> None:
    with connection() as db:
        db.execute("PRAGMA journal_mode=WAL")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            raise RuntimeError(f"不支持的数据库版本: {version}")
        db.execute(
            "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, source_id TEXT NOT NULL, url TEXT NOT NULL, "
            "name TEXT NOT NULL, author TEXT, size TEXT, status TEXT, cover_url TEXT, classify TEXT, "
            "introduce TEXT, last_update_time TEXT, last_chapter_name TEXT, added_at INTEGER NOT NULL, "
            "updated_at INTEGER NOT NULL, UNIQUE(source_id,url))"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS reading_progress (book_id INTEGER PRIMARY KEY REFERENCES books(id) ON DELETE CASCADE, "
            "chapter_url TEXT NOT NULL, chapter_name TEXT NOT NULL, chapter_index INTEGER NOT NULL "
            "CHECK(chapter_index >= 0), updated_at INTEGER NOT NULL)"
        )
        db.execute("PRAGMA user_version=1")
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("数据库完整性检查失败")


def fetch_book(db: sqlite3.Connection, book_id: int) -> dict | None:
    row = db.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    if not row:
        return None
    book = dict(row)
    book["book_id"] = book.pop("id")
    progress = db.execute(
        "SELECT chapter_url, chapter_name, chapter_index, updated_at FROM reading_progress WHERE book_id=?", (book_id,)
    ).fetchone()
    book["progress"] = dict(progress) if progress else None
    return book


def list_books() -> list[dict]:
    with connection() as db:
        return [fetch_book(db, row[0]) for row in db.execute("SELECT id FROM books ORDER BY added_at DESC, id DESC").fetchall()]


def add_book(values: dict) -> tuple[dict, bool]:
    with connection() as db:
        stamp = now_ms()
        values = {key: values.get(key) for key in FIELDS}
        columns = ", ".join(FIELDS)
        placeholders = ", ".join("?" for _ in FIELDS)
        cursor = db.execute(
            f"INSERT INTO books ({columns}, added_at, updated_at) VALUES ({placeholders}, ?, ?) ON CONFLICT(source_id,url) DO NOTHING",
            (*values.values(), stamp, stamp),
        )
        book_id = (
            cursor.lastrowid
            if cursor.rowcount
            else db.execute("SELECT id FROM books WHERE source_id=? AND url=?", (values["source_id"], values["url"])).fetchone()[0]
        )
        return fetch_book(db, book_id), bool(cursor.rowcount)


def delete_book(book_id: int) -> None:
    with connection() as db:
        db.execute("DELETE FROM books WHERE id=?", (book_id,))


def set_progress(book_id: int, values: dict) -> dict | None:
    with connection() as db:
        if not db.execute("SELECT 1 FROM books WHERE id=?", (book_id,)).fetchone():
            return None
        migrated = values.get("migrated_updated_at")
        stamp = migrated if migrated is not None else now_ms()
        sql = (
            "INSERT INTO reading_progress (book_id,chapter_url,chapter_name,chapter_index,updated_at) VALUES (?,?,?,?,?) "
            "ON CONFLICT(book_id) DO UPDATE SET chapter_url=excluded.chapter_url, chapter_name=excluded.chapter_name, "
            "chapter_index=excluded.chapter_index, updated_at=excluded.updated_at"
        )
        if migrated is not None:
            sql += " WHERE excluded.updated_at > reading_progress.updated_at"
        cursor = db.execute(sql, (book_id, values["chapter_url"], values["chapter_name"], values["chapter_index"], stamp))
        if cursor.rowcount:
            db.execute("UPDATE books SET updated_at=? WHERE id=?", (now_ms(), book_id))
        return dict(
            db.execute(
                "SELECT chapter_url, chapter_name, chapter_index, updated_at FROM reading_progress WHERE book_id=?", (book_id,)
            ).fetchone()
        )
