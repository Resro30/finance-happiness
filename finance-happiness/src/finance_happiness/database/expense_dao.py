import sqlite3
from datetime import date
from decimal import Decimal

from finance_happiness.models import Expense, Category, PerceivedValue


class ExpenseDAO:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, expense: Expense) -> Expense:
        cursor = self._conn.execute(
            """
            INSERT INTO expenses
                (amount, category, description, date,
                 experiential, social, planned, time_saving,
                 happiness_score, duration_minutes, perceived_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._to_row(expense),
        )
        self._conn.commit()
        return Expense(
            id=cursor.lastrowid,
            amount=expense.amount,
            category=expense.category,
            description=expense.description,
            date=expense.date,
            experiential=expense.experiential,
            social=expense.social,
            planned=expense.planned,
            time_saving=expense.time_saving,
            happiness_score=expense.happiness_score,
            duration_minutes=expense.duration_minutes,
            perceived_value=expense.perceived_value,
        )

    def get_all(self) -> list[Expense]:
        rows = self._conn.execute(
            "SELECT * FROM expenses ORDER BY date DESC"
        ).fetchall()
        return [self._from_row(r) for r in rows]

    def get_by_id(self, expense_id: int) -> Expense | None:
        row = self._conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def update(self, expense: Expense) -> None:
        if expense.id is None:
            raise ValueError("Cannot update an expense without an id")
        self._conn.execute(
            """
            UPDATE expenses SET
                amount=?, category=?, description=?, date=?,
                experiential=?, social=?, planned=?, time_saving=?,
                happiness_score=?, duration_minutes=?, perceived_value=?
            WHERE id=?
            """,
            (*self._to_row(expense), expense.id),
        )
        self._conn.commit()

    def delete(self, expense_id: int) -> None:
        self._conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self._conn.commit()

    def cumulative_spend(self, category: Category, before_date: date) -> Decimal:
        rows = self._conn.execute(
            "SELECT amount FROM expenses WHERE category=? AND date<?",
            (category.name, before_date.isoformat()),
        ).fetchall()
        return sum((Decimal(r[0]) for r in rows), Decimal("0"))

    def recent_count(
        self,
        category: Category,
        since_date: date,
        exclude_id: int | None = None,
    ) -> int:
        if exclude_id is not None:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM expenses WHERE category=? AND date>=? AND id!=?",
                (category.name, since_date.isoformat(), exclude_id),
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM expenses WHERE category=? AND date>=?",
                (category.name, since_date.isoformat()),
            ).fetchone()
        return row[0]

    @staticmethod
    def _to_row(e: Expense) -> tuple:
        return (
            str(e.amount),
            e.category.name,
            e.description,
            e.date.isoformat(),
            int(e.experiential),
            int(e.social),
            int(e.planned),
            int(e.time_saving),
            e.happiness_score,
            e.duration_minutes,
            e.perceived_value.name if e.perceived_value else None,
        )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Expense:
        return Expense(
            id=row["id"],
            amount=Decimal(row["amount"]),
            category=Category[row["category"]],
            description=row["description"],
            date=date.fromisoformat(row["date"]),
            experiential=bool(row["experiential"]),
            social=bool(row["social"]),
            planned=bool(row["planned"]),
            time_saving=bool(row["time_saving"]),
            happiness_score=row["happiness_score"],
            duration_minutes=row["duration_minutes"],
            perceived_value=PerceivedValue[row["perceived_value"]] if row["perceived_value"] else None,
        )
