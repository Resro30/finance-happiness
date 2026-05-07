from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QHeaderView,
    QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from finance_happiness.analytics.csv_importer import ImportRow
from finance_happiness.models import Expense

_OK_COLOR  = QColor("#d4edda")
_ERR_COLOR = QColor("#f8d7da")


class ImportDialog(QDialog):
    def __init__(self, rows: list[ImportRow], parent=None):
        super().__init__(parent)
        self._rows = rows
        self.setWindowTitle("Import CSV — Preview")
        self.setMinimumSize(900, 440)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        valid = sum(1 for r in self._rows if r.expense is not None)
        skipped = len(self._rows) - valid
        layout.addWidget(QLabel(
            f"<b>{len(self._rows)}</b> rows found — "
            f"<b style='color:green'>{valid} will be imported</b>, "
            f"<b style='color:#c0392b'>{skipped} will be skipped</b>."
        ))

        table = QTableWidget(len(self._rows), 6)
        table.setHorizontalHeaderLabels(
            ["#", "Date", "Description", "Category", "Amount", "Status"]
        )
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        for i, row in enumerate(self._rows):
            e = row.expense
            color = _OK_COLOR if e else _ERR_COLOR
            cells = [
                str(i + 1),
                e.date.isoformat() if e else row.raw.get("date", ""),
                (e.description if e else row.raw.get("description", ""))[:60],
                e.category.value if e else row.raw.get("category", ""),
                f"{e.amount:.2f}" if e else row.raw.get("amount", ""),
                "✓ OK" if e else f"⚠ {row.error}",
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setBackground(color)
                if col == 4:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                table.setItem(i, col, item)

        layout.addWidget(table)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        import_btn = buttons.addButton(
            f"Import {valid} expense{'s' if valid != 1 else ''}",
            QDialogButtonBox.ButtonRole.AcceptRole,
        )
        import_btn.setEnabled(valid > 0)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def valid_expenses(self) -> list[Expense]:
        return [r.expense for r in self._rows if r.expense is not None]
