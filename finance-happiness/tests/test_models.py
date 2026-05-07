import pytest
from datetime import date
from decimal import Decimal

from finance_happiness.models import Expense, Category


def make_expense(**kwargs):
    defaults = dict(
        amount=Decimal("50.00"),
        category=Category.FOOD,
        description="Dinner at restaurant",
        date=date(2024, 1, 15),
        experiential=True,
        social=True,
        planned=True,
        time_saving=False,
    )
    return Expense(**{**defaults, **kwargs})


def test_basic_creation():
    e = make_expense()
    assert e.amount == Decimal("50.00")
    assert e.category == Category.FOOD
    assert e.id is None
    assert e.happiness_score is None


def test_float_amount_is_converted_to_decimal():
    e = make_expense(amount=49.99)
    assert isinstance(e.amount, Decimal)
    assert e.amount == Decimal("49.99")


def test_negative_amount_raises():
    with pytest.raises(ValueError):
        make_expense(amount=Decimal("-10"))


def test_zero_amount_raises():
    with pytest.raises(ValueError):
        make_expense(amount=Decimal("0"))


def test_empty_description_raises():
    with pytest.raises(ValueError):
        make_expense(description="   ")


def test_category_display_name():
    assert Category.FOOD.value == "Food"
    assert Category.HEALTH.value == "Health"
