import sqlite3

_CREATE_EXPENSES = """
CREATE TABLE IF NOT EXISTS expenses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    amount          TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    description     TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    experiential    INTEGER NOT NULL,
    social          INTEGER NOT NULL,
    planned         INTEGER NOT NULL,
    time_saving     INTEGER NOT NULL,
    happiness_score REAL,
    duration_minutes INTEGER
);
"""


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_CREATE_EXPENSES)
    _migrate(conn)
    conn.commit()


def _migrate(conn: sqlite3.Connection) -> None:
    """Add columns introduced after the initial schema."""
    for sql in [
        "ALTER TABLE expenses ADD COLUMN duration_minutes INTEGER",
        "ALTER TABLE expenses ADD COLUMN perceived_value TEXT",
    ]:
        try:
            conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # column already exists
