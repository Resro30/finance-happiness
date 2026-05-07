import pandas as pd

from finance_happiness.models import Expense


def to_dataframe(expenses: list[Expense]) -> pd.DataFrame:
    if not expenses:
        return pd.DataFrame(columns=[
            "date", "description", "category", "amount",
            "score", "duration_minutes", "hours", "cost_per_hour",
        ])
    rows = []
    for e in expenses:
        hours = e.duration_minutes / 60.0 if e.duration_minutes else None
        cph   = float(e.amount) / hours    if hours else None
        rows.append({
            "date":             e.date,
            "description":      e.description,
            "category":         e.category.value,
            "amount":           float(e.amount),
            "score":            e.happiness_score,
            "duration_minutes": e.duration_minutes,
            "hours":            hours,
            "cost_per_hour":    cph,
        })
    return pd.DataFrame(rows)


def spending_by_category(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby("category")["amount"].sum().sort_values()


def avg_score_by_category(df: pd.DataFrame) -> pd.Series:
    scored = df.dropna(subset=["score"])
    if scored.empty:
        return pd.Series(dtype=float)
    return scored.groupby("category")["score"].mean().sort_values()


def score_per_ron_by_category(df: pd.DataFrame) -> pd.Series:
    scored = df.dropna(subset=["score"])
    if scored.empty:
        return pd.Series(dtype=float)
    result = scored.groupby("category").apply(
        lambda g: (g["score"].mean() / g["amount"].mean()) * 100,
        include_groups=False,
    )
    return result.sort_values()


def cost_per_hour_by_category(df: pd.DataFrame) -> pd.Series:
    """Average RON/hour by category (only for purchases with duration). Lower = better value."""
    timed = df.dropna(subset=["cost_per_hour"])
    if timed.empty:
        return pd.Series(dtype=float)
    return timed.groupby("category")["cost_per_hour"].mean().sort_values(ascending=False)


def monthly_avg_score(df: pd.DataFrame) -> pd.Series:
    scored = df.dropna(subset=["score"])
    if scored.empty:
        return pd.Series(dtype=float)
    scored = scored.copy()
    scored["month"] = pd.to_datetime(scored["date"]).dt.to_period("M").astype(str)
    return scored.groupby("month")["score"].mean().sort_index()


def top_and_bottom(df: pd.DataFrame, n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    scored = df.dropna(subset=["score"]).copy()
    if scored.empty:
        empty = pd.DataFrame(columns=["description", "category", "amount", "score"])
        return empty, empty
    scored = scored.sort_values("score", ascending=False).reset_index(drop=True)
    return scored.head(n), scored.tail(n).iloc[::-1].reset_index(drop=True)
