import pytest
from pathlib import Path
from decimal import Decimal
from datetime import date

from finance_happiness.analytics.csv_importer import parse_file
from finance_happiness.models import Category


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    f = tmp_path / "test.csv"
    f.write_text(
        "date,amount,category,description,experiential,social,planned,time_saving\n"
        "2024-01-15,45.00,FOOD,Dinner with friends,true,true,true,false\n"
        "2024-01-16,120.00,ENTERTAINMENT,Jazz concert,true,true,true,false\n",
        encoding="utf-8",
    )
    return f


def test_parses_valid_rows(sample_csv):
    rows = parse_file(sample_csv)
    assert len(rows) == 2
    assert all(r.expense is not None for r in rows)


def test_correct_values(sample_csv):
    rows = parse_file(sample_csv)
    e = rows[0].expense
    assert e.amount == Decimal("45.00")
    assert e.category == Category.FOOD
    assert e.description == "Dinner with friends"
    assert e.date == date(2024, 1, 15)
    assert e.experiential is True
    assert e.social is True
    assert e.planned is True
    assert e.time_saving is False


def test_negative_amount_becomes_positive(tmp_path):
    f = tmp_path / "bank.csv"
    f.write_text(
        "date,amount,description\n"
        "2024-02-01,-55.00,Supermarket\n",
        encoding="utf-8",
    )
    rows = parse_file(f)
    assert rows[0].expense.amount == Decimal("55.00")


def test_missing_tags_default_to_false(tmp_path):
    f = tmp_path / "minimal.csv"
    f.write_text(
        "date,amount,description\n"
        "2024-02-01,30.00,Coffee\n",
        encoding="utf-8",
    )
    rows = parse_file(f)
    e = rows[0].expense
    assert e.experiential is False
    assert e.social is False
    assert e.planned is False
    assert e.time_saving is False


def test_unknown_category_falls_back_to_other(tmp_path):
    f = tmp_path / "unknown_cat.csv"
    f.write_text(
        "date,amount,category,description\n"
        "2024-02-01,30.00,GAMING,Steam purchase\n",
        encoding="utf-8",
    )
    rows = parse_file(f)
    assert rows[0].expense.category == Category.OTHER


def test_bad_date_produces_error(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text(
        "date,amount,description\n"
        "not-a-date,30.00,Coffee\n",
        encoding="utf-8",
    )
    rows = parse_file(f)
    assert rows[0].expense is None
    assert rows[0].error is not None


def test_bad_amount_produces_error(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text(
        "date,amount,description\n"
        "2024-02-01,abc,Coffee\n",
        encoding="utf-8",
    )
    rows = parse_file(f)
    assert rows[0].expense is None


def test_mixed_valid_and_invalid_rows(tmp_path):
    f = tmp_path / "mixed.csv"
    f.write_text(
        "date,amount,description\n"
        "2024-02-01,30.00,Coffee\n"
        "bad-date,20.00,Tea\n"
        "2024-02-03,15.00,Juice\n",
        encoding="utf-8",
    )
    rows = parse_file(f)
    assert len(rows) == 3
    assert rows[0].expense is not None
    assert rows[1].expense is None
    assert rows[2].expense is not None


def test_category_by_display_value(tmp_path):
    f = tmp_path / "display.csv"
    f.write_text(
        "date,amount,category,description\n"
        "2024-02-01,50.00,Health,Gym membership\n",
        encoding="utf-8",
    )
    rows = parse_file(f)
    assert rows[0].expense.category == Category.HEALTH


def test_date_formats(tmp_path):
    f = tmp_path / "dates.csv"
    f.write_text(
        "date,amount,description\n"
        "15/01/2024,10.00,A\n"
        "2024-01-16,10.00,B\n"
        "01.17.2024,10.00,C\n",
        encoding="utf-8",
    )
    rows = parse_file(f)
    assert rows[0].expense.date == date(2024, 1, 15)
    assert rows[1].expense.date == date(2024, 1, 16)


def test_empty_file_returns_empty_list(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("date,amount,description\n", encoding="utf-8")
    assert parse_file(f) == []


def test_sample_csv_file():
    path = Path(__file__).parent.parent / "data" / "sample_expenses.csv"
    rows = parse_file(path)
    assert len(rows) == 7
    assert all(r.expense is not None for r in rows)
