import pytest
from datetime import date
from decimal import Decimal

from finance_happiness.models import Expense, Category
from finance_happiness.database import open_connection, create_schema, ExpenseDAO


@pytest.fixture
def dao():
    conn = open_connection(":memory:")
    create_schema(conn)
    return ExpenseDAO(conn)


def make_expense(**kwargs) -> Expense:
    defaults = dict(
        amount=Decimal("75.50"),
        category=Category.ENTERTAINMENT,
        description="Jazz concert",
        date=date(2024, 3, 10),
        experiential=True,
        social=True,
        planned=True,
        time_saving=False,
    )
    return Expense(**{**defaults, **kwargs})


def test_add_returns_expense_with_id(dao):
    saved = dao.add(make_expense())
    assert saved.id == 1
    assert saved.amount == Decimal("75.50")


def test_get_all_returns_saved_expenses(dao):
    dao.add(make_expense(description="Concert"))
    dao.add(make_expense(description="Movie"))
    results = dao.get_all()
    assert len(results) == 2


def test_get_by_id(dao):
    saved = dao.add(make_expense())
    found = dao.get_by_id(saved.id)
    assert found.description == "Jazz concert"
    assert found.category == Category.ENTERTAINMENT


def test_get_by_id_missing_returns_none(dao):
    assert dao.get_by_id(999) is None


def test_update(dao):
    saved = dao.add(make_expense())
    updated = Expense(
        id=saved.id,
        amount=Decimal("80.00"),
        category=Category.ENTERTAINMENT,
        description="Updated concert",
        date=saved.date,
        experiential=True,
        social=True,
        planned=True,
        time_saving=False,
    )
    dao.update(updated)
    found = dao.get_by_id(saved.id)
    assert found.description == "Updated concert"
    assert found.amount == Decimal("80.00")


def test_delete(dao):
    saved = dao.add(make_expense())
    dao.delete(saved.id)
    assert dao.get_by_id(saved.id) is None
    assert dao.get_all() == []


def test_decimal_precision_preserved(dao):
    saved = dao.add(make_expense(amount=Decimal("123.45")))
    found = dao.get_by_id(saved.id)
    assert found.amount == Decimal("123.45")


def test_category_roundtrip(dao):
    saved = dao.add(make_expense(category=Category.HEALTH))
    found = dao.get_by_id(saved.id)
    assert found.category == Category.HEALTH


def test_update_without_id_raises(dao):
    with pytest.raises(ValueError):
        dao.update(make_expense())
