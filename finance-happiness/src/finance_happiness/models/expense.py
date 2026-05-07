from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .category import Category
from .perceived_value import PerceivedValue


@dataclass
class Expense:
    amount: Decimal
    category: Category
    description: str
    date: date
    experiential: bool
    social: bool
    planned: bool
    time_saving: bool
    id: int | None = None
    happiness_score: float | None = None
    duration_minutes: int | None = None
    perceived_value: PerceivedValue | None = None

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        if not self.description.strip():
            raise ValueError("Description cannot be empty")
        if isinstance(self.amount, (int, float)):
            self.amount = Decimal(str(self.amount))
        if self.duration_minutes is not None and self.duration_minutes <= 0:
            raise ValueError("Duration must be positive if specified")
