# -*- coding: utf-8 -*-
import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

# يمكن تغييره من متغير بيئة ASSETS_DB_PATH
DB_PATH = os.environ.get("ASSETS_DB_PATH", os.path.abspath("assets.db"))

def init_db() -> None:
    """تهيئة أساسية للـ SQLite (WAL لتحسين التزامن)."""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """اتصال Context Manager — يعمل commit تلقائيًا ويغلق بأمان."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    finally:
        conn.close()
