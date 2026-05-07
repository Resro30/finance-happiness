import sqlite3
from pathlib import Path


def default_db_path() -> Path:
    data_dir = Path.home() / ".local" / "share" / "finance-happiness"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "finance.db"


def open_connection(path: str | Path = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
