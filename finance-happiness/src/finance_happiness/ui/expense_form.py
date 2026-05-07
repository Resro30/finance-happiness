from datetime import date
from decimal import Decimal

from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import (
    QButtonGroup, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QRadioButton, QSpinBox, QVBoxLayout,
)

from finance_happiness.models import Category, Expense, PerceivedValue


class _AmountSpinBox(QDoubleSpinBox):
    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)


class _MinutesSpinBox(QSpinBox):
    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)


class _RadioPair:
    def __init__(self, false_label: str, true_label: str):
        self._group = QButtonGroup()
        self.false_btn = QRadioButton(false_label)
        self.true_btn  = QRadioButton(true_label)
        self._group.addButton(self.false_btn, 0)
        self._group.addButton(self.true_btn,  1)
        self.false_btn.setChecked(True)

    def widget(self):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.false_btn)
        row.addWidget(self.true_btn)
        row.addStretch()
        return row

    @property
    def value(self) -> bool:
        return self._group.checkedId() == 1

    def set_value(self, v: bool):
        (self.true_btn if v else self.false_btn).setChecked(True)


class ExpenseForm(QDialog):
    def __init__(self, parent=None, expense: Expense | None = None):
        super().__init__(parent)
        self.setWindowTitle("Add Expense" if expense is None else "Edit Expense")
        self.setMinimumWidth(480)
        self._build_ui()
        if expense:
            self._fill(expense)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setVerticalSpacing(10)

        self._amount = _AmountSpinBox()
        self._amount.setRange(0.00, 999_999.99)
        self._amount.setDecimals(2)
        self._amount.setSuffix(" RON")
        self._amount.setSpecialValueText("Amount…")
        self._amount.setValue(0.00)
        form.addRow("Amount:", self._amount)

        self._category = QComboBox()
        for cat in Category:
            self._category.addItem(cat.value, userData=cat)
        form.addRow("Category:", self._category)

        self._description = QLineEdit()
        self._description.setPlaceholderText("What did you buy?")
        form.addRow("Description:", self._description)

        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setDate(QDate.currentDate())
        form.addRow("Date:", self._date)

        # Duration row: spinbox + live hours label
        dur_row = QHBoxLayout()
        dur_row.setContentsMargins(0, 0, 0, 0)
        self._duration = _MinutesSpinBox()
        self._duration.setRange(0, 99999)
        self._duration.setSpecialValueText("N/A (optional)")
        self._duration.setSuffix(" min")
        self._duration.setValue(0)
        self._duration_label = QLabel("")
        self._duration.valueChanged.connect(self._on_duration_changed)
        dur_row.addWidget(self._duration)
        dur_row.addWidget(self._duration_label)
        dur_row.addStretch()
        form.addRow("Duration:", dur_row)

        layout.addLayout(form)

        # Happiness tags
        tags_box = QGroupBox("Happiness Tags")
        tags_layout = QFormLayout(tags_box)
        tags_layout.setVerticalSpacing(10)

        self._type   = _RadioPair("Material good",        "Experience / activity")
        self._social = _RadioPair("Just for me",           "Social / with others")
        self._intent = _RadioPair("Spontaneous / impulse", "Anticipated / routine")
        self._time   = _RadioPair("No time saved",         "Saves me time")

        tags_layout.addRow("Type:",    self._type.widget())
        tags_layout.addRow("Context:", self._social.widget())
        tags_layout.addRow("Intent:",  self._intent.widget())
        tags_layout.addRow("Time:",    self._time.widget())

        # Perceived value — Thaler's transaction utility
        self._perceived_value = QComboBox()
        self._perceived_value.addItem("— not specified —", userData=None)
        for pv in PerceivedValue:
            self._perceived_value.addItem(pv.value, userData=pv)
        tags_layout.addRow("Value felt:", self._perceived_value)

        layout.addWidget(tags_box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_duration_changed(self, minutes: int):
        if minutes > 0:
            hours = minutes / 60
            self._duration_label.setText(f"≈ {hours:.1f} h")
        else:
            self._duration_label.setText("")

    def _fill(self, expense: Expense):
        self._amount.setValue(float(expense.amount))
        self._category.setCurrentIndex(self._category.findData(expense.category))
        self._description.setText(expense.description)
        d = expense.date
        self._date.setDate(QDate(d.year, d.month, d.day))
        self._type.set_value(expense.experiential)
        self._social.set_value(expense.social)
        self._intent.set_value(expense.planned)
        self._time.set_value(expense.time_saving)
        self._duration.setValue(expense.duration_minutes or 0)
        idx = self._perceived_value.findData(expense.perceived_value)
        if idx >= 0:
            self._perceived_value.setCurrentIndex(idx)

    def accept(self):
        if self._amount.value() <= 0:
            QMessageBox.warning(self, "Validation", "Please enter an amount.")
            return
        if not self._description.text().strip():
            QMessageBox.warning(self, "Validation", "Description cannot be empty.")
            return
        super().accept()

    def get_expense(self, existing_id: int | None = None) -> Expense | None:
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        qd = self._date.date()
        raw_duration = self._duration.value()
        return Expense(
            id=existing_id,
            amount=Decimal(str(round(self._amount.value(), 2))),
            category=self._category.currentData(),
            description=self._description.text().strip(),
            date=date(qd.year(), qd.month(), qd.day()),
            experiential=self._type.value,
            social=self._social.value,
            planned=self._intent.value,
            time_saving=self._time.value,
            duration_minutes=raw_duration if raw_duration > 0 else None,
            perceived_value=self._perceived_value.currentData(),
        )
