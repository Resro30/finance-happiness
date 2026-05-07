import csv
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from finance_happiness.models import Category, Expense, PerceivedValue


@dataclass
class ImportRow:
    expense: Expense | None
    error: str | None
    raw: dict


def parse_file(path: str | Path) -> list[ImportRow]:
    results: list[ImportRow] = []
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return []
            for line_no, row in enumerate(reader, start=2):
                results.append(_parse_row(row, line_no))
    except OSError as e:
        results.append(ImportRow(expense=None, error=str(e), raw={}))
    return results


def _parse_row(row: dict, line_no: int) -> ImportRow:
    raw = dict(row)
    try:
        raw_amount = row.get("amount", "").strip().replace(",", ".")
        # Banks export debits as negative — take the absolute value
        amount = Decimal(raw_amount.lstrip("-"))
        raw_dur = row.get("duration_minutes", "").strip()
        duration = int(raw_dur) if raw_dur.isdigit() and int(raw_dur) > 0 else None
        expense = Expense(
            amount=amount,
            category=_parse_category(row.get("category", "OTHER")),
            description=row.get("description", "").strip() or f"Row {line_no}",
            date=_parse_date(row.get("date", "")),
            experiential=_parse_bool(row.get("experiential", "false")),
            social=_parse_bool(row.get("social", "false")),
            planned=_parse_bool(row.get("planned", "false")),
            time_saving=_parse_bool(row.get("time_saving", "false")),
            duration_minutes=duration,
            perceived_value=_parse_perceived_value(row.get("perceived_value", "")),
        )
        return ImportRow(expense=expense, error=None, raw=raw)
    except Exception as e:
        return ImportRow(expense=None, error=str(e), raw=raw)


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes", "y")


def _parse_date(value: str) -> date:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: {value!r}")


def _parse_perceived_value(value: str) -> PerceivedValue | None:
    v = value.strip()
    if not v:
        return None
    try:
        return PerceivedValue[v.upper()]
    except KeyError:
        pass
    for pv in PerceivedValue:
        if pv.value.lower() == v.lower():
            return pv
    return None


def _parse_category(value: str) -> Category:
    v = value.strip().upper()
    try:
        return Category[v]
    except KeyError:
        pass
    for cat in Category:
        if cat.value.upper() == v:
            return cat
    return Category.OTHER
