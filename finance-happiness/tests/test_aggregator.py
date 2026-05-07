import pytest
from datetime import date
from decimal import Decimal

from finance_happiness.analytics.aggregator import (
    avg_score_by_category,
    cost_per_hour_by_category,
    monthly_avg_score,
    score_per_ron_by_category,
    spending_by_category,
    to_dataframe,
    top_and_bottom,
)
from finance_happiness.models import Category, Expense


def make_expense(**kwargs) -> Expense:
    defaults = dict(
        amount=Decimal("100.00"),
        category=Category.ENTERTAINMENT,
        description="Test",
        date=date(2024, 3, 10),
        experiential=True,
        social=False,
        planned=True,
        time_saving=False,
        happiness_score=7.0,
    )
    return Expense(**{**defaults, **kwargs})


# --- to_dataframe ---

def test_to_dataframe_empty():
    df = to_dataframe([])
    assert df.empty
    assert "amount" in df.columns
    assert "score" in df.columns


def test_to_dataframe_basic_columns():
    df = to_dataframe([make_expense()])
    assert list(df.columns) == [
        "date", "description", "category", "amount",
        "score", "duration_minutes", "hours", "cost_per_hour",
    ]


def test_to_dataframe_amount_is_float():
    df = to_dataframe([make_expense(amount=Decimal("42.50"))])
    assert df["amount"].iloc[0] == pytest.approx(42.50)


def test_to_dataframe_duration_computes_hours_and_cph():
    e = make_expense(amount=Decimal("90.00"), duration_minutes=180)
    df = to_dataframe([e])
    assert df["hours"].iloc[0] == pytest.approx(3.0)
    assert df["cost_per_hour"].iloc[0] == pytest.approx(30.0)


def test_to_dataframe_no_duration_gives_none():
    df = to_dataframe([make_expense(duration_minutes=None)])
    assert df["hours"].iloc[0] is None
    assert df["cost_per_hour"].iloc[0] is None


def test_to_dataframe_category_is_display_value():
    df = to_dataframe([make_expense(category=Category.FOOD)])
    assert df["category"].iloc[0] == "Food"


# --- spending_by_category ---

def test_spending_by_category_sums_correctly():
    expenses = [
        make_expense(category=Category.FOOD, amount=Decimal("50")),
        make_expense(category=Category.FOOD, amount=Decimal("30")),
        make_expense(category=Category.ENTERTAINMENT, amount=Decimal("100")),
    ]
    df = to_dataframe(expenses)
    series = spending_by_category(df)
    assert series["Food"] == pytest.approx(80.0)
    assert series["Entertainment"] == pytest.approx(100.0)


def test_spending_by_category_empty():
    assert spending_by_category(to_dataframe([])).empty


# --- avg_score_by_category ---

def test_avg_score_by_category_ignores_unscored():
    expenses = [
        make_expense(category=Category.FOOD, happiness_score=8.0),
        make_expense(category=Category.FOOD, happiness_score=None),
    ]
    df = to_dataframe(expenses)
    series = avg_score_by_category(df)
    assert series["Food"] == pytest.approx(8.0)


def test_avg_score_by_category_averages_correctly():
    expenses = [
        make_expense(category=Category.FOOD, happiness_score=6.0),
        make_expense(category=Category.FOOD, happiness_score=8.0),
    ]
    df = to_dataframe(expenses)
    series = avg_score_by_category(df)
    assert series["Food"] == pytest.approx(7.0)


def test_avg_score_by_category_empty_when_no_scores():
    expenses = [make_expense(happiness_score=None)]
    assert avg_score_by_category(to_dataframe(expenses)).empty


# --- score_per_ron_by_category ---

def test_score_per_ron_formula():
    # avg_score=8.0, avg_amount=100.0 → (8/100)*100 = 8.0
    expenses = [make_expense(happiness_score=8.0, amount=Decimal("100"))]
    df = to_dataframe(expenses)
    series = score_per_ron_by_category(df)
    assert series["Entertainment"] == pytest.approx(8.0)


def test_score_per_ron_higher_score_per_ron_ranks_higher():
    expenses = [
        make_expense(category=Category.FOOD, happiness_score=8.0, amount=Decimal("50")),
        make_expense(category=Category.ENTERTAINMENT, happiness_score=8.0, amount=Decimal("200")),
    ]
    df = to_dataframe(expenses)
    series = score_per_ron_by_category(df)
    assert series["Food"] > series["Entertainment"]


# --- cost_per_hour_by_category ---

def test_cost_per_hour_only_includes_timed_purchases():
    expenses = [
        make_expense(amount=Decimal("60"), duration_minutes=120),
        make_expense(amount=Decimal("999"), duration_minutes=None),
    ]
    df = to_dataframe(expenses)
    series = cost_per_hour_by_category(df)
    assert len(series) == 1
    assert series["Entertainment"] == pytest.approx(30.0)


def test_cost_per_hour_empty_when_no_durations():
    assert cost_per_hour_by_category(to_dataframe([make_expense()])).empty


# --- monthly_avg_score ---

def test_monthly_avg_score_groups_by_month():
    expenses = [
        make_expense(date=date(2024, 3, 1),  happiness_score=6.0),
        make_expense(date=date(2024, 3, 15), happiness_score=8.0),
        make_expense(date=date(2024, 4, 1),  happiness_score=5.0),
    ]
    df = to_dataframe(expenses)
    series = monthly_avg_score(df)
    assert series["2024-03"] == pytest.approx(7.0)
    assert series["2024-04"] == pytest.approx(5.0)


def test_monthly_avg_score_empty_when_no_scores():
    assert monthly_avg_score(to_dataframe([make_expense(happiness_score=None)])).empty


# --- top_and_bottom ---

def test_top_and_bottom_ordering():
    expenses = [
        make_expense(description="A", happiness_score=9.0),
        make_expense(description="B", happiness_score=3.0),
        make_expense(description="C", happiness_score=6.0),
    ]
    df = to_dataframe(expenses)
    best, worst = top_and_bottom(df, n=1)
    assert best.iloc[0]["description"] == "A"
    assert worst.iloc[0]["description"] == "B"


def test_top_and_bottom_empty():
    best, worst = top_and_bottom(to_dataframe([]), n=5)
    assert best.empty
    assert worst.empty


def test_top_and_bottom_ignores_unscored():
    expenses = [
        make_expense(description="scored", happiness_score=7.0),
        make_expense(description="unscored", happiness_score=None),
    ]
    df = to_dataframe(expenses)
    best, worst = top_and_bottom(df, n=5)
    assert len(best) == 1
    assert best.iloc[0]["description"] == "scored"
