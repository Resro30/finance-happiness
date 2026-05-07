from datetime import timedelta
from decimal import Decimal

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QGuiApplication, QKeySequence
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QDialog, QFileDialog, QHeaderView,
    QMainWindow, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QToolBar, QToolButton, QVBoxLayout, QWidget,
)

from finance_happiness.analytics.csv_importer import parse_file
from finance_happiness.database import ExpenseDAO
from finance_happiness.models import Expense
from finance_happiness.resources.styles import DARK, LIGHT
from finance_happiness.scoring import calculate_score
from .dashboard import DashboardWidget
from .delegates import CategoryChipDelegate, ScorePillDelegate
from .expense_form import ExpenseForm
from .import_dialog import ImportDialog
from .info_tab import InfoTab

_EXPENSES_TAB  = 0
_DASHBOARD_TAB = 1



class MainWindow(QMainWindow):
    def __init__(self, dao: ExpenseDAO):
        super().__init__()
        self._dao = dao
        self._expenses: list[Expense] = []
        self._dark = self._load_theme_preference()
        self.setWindowTitle("Finance Happiness")
        self.setMinimumSize(900, 650)
        self.resize(1150, 940)
        self._build_ui()      # menu (incl. _dark_action) built here
        self._apply_theme()   # now safe to sync checkbox
        self._refresh()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        self._build_menu()

        self._tabs = QTabWidget()
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._tabs.addTab(self._build_expenses_tab(), "Expenses")
        self._dashboard = DashboardWidget()
        self._tabs.addTab(self._dashboard, "Dashboard")

        info_btn = QToolButton()
        info_btn.setText("How it works")
        info_btn.clicked.connect(self._on_how_it_works)
        self._tabs.setCornerWidget(info_btn, Qt.Corner.TopRightCorner)

        self.setCentralWidget(self._tabs)
        self.statusBar()

    def _build_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("View")
        self._dark_action = QAction("Dark Theme", self, checkable=True)
        self._dark_action.setShortcut(QKeySequence("Ctrl+Shift+D"))
        self._dark_action.toggled.connect(self._on_theme_toggle)
        view_menu.addAction(self._dark_action)

        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _build_expenses_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QToolBar("Expenses")
        actions = [
            ("+ Add",      "Ctrl+N",    self._on_add),
            ("Edit",       "F2",        self._on_edit),
            ("Delete",     "Del",       self._on_delete),
            ("Import CSV", "Ctrl+I",    self._on_import),
        ]
        for label, shortcut, slot in actions:
            action = QAction(label, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(slot)
            toolbar.addAction(action)
        layout.addWidget(toolbar)

        self._table = QTableWidget()
        self._table.setColumnCount(10)
        self._table.setHorizontalHeaderLabels([
            "Date", "Description", "Category", "Amount (RON)",
            "Exp", "Social", "Planned", "Time-saving", "RON/hr", "Score /10",
        ])
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setDefaultSectionSize(34)
        self._table.setItemDelegateForColumn(2, CategoryChipDelegate(self._table))
        self._table.setItemDelegateForColumn(9, ScorePillDelegate(self._table))
        self._table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self._table)

        return widget

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    @staticmethod
    def _load_theme_preference() -> bool:
        settings = QSettings("FinanceHappiness", "FinanceHappiness")
        if settings.contains("dark_mode"):
            return settings.value("dark_mode", False, type=bool)
        # First launch — follow the system colour scheme
        try:
            from PyQt6.QtCore import Qt as _Qt
            scheme = QGuiApplication.styleHints().colorScheme()
            return scheme == _Qt.ColorScheme.Dark
        except Exception:
            return False

    @staticmethod
    def _save_theme_preference(dark: bool) -> None:
        QSettings("FinanceHappiness", "FinanceHappiness").setValue("dark_mode", dark)

    def _apply_theme(self):
        QApplication.instance().setStyleSheet(DARK if self._dark else LIGHT)
        # Keep the menu checkbox in sync (needed when preference is loaded at startup)
        self._dark_action.setChecked(self._dark)

    def _on_theme_toggle(self, checked: bool):
        self._dark = checked
        self._save_theme_preference(checked)
        self._apply_theme()
        self._refresh()
        if self._tabs.currentIndex() == _DASHBOARD_TAB:
            self._dashboard.refresh(self._expenses, dark=self._dark)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def _refresh(self):
        # Disable sorting while populating to avoid index scrambling
        self._table.setSortingEnabled(False)
        self._expenses = self._dao.get_all()
        self._table.setRowCount(len(self._expenses))
        total = Decimal("0")
        scores = []
        for row, e in enumerate(self._expenses):
            self._populate_row(row, e)
            total += e.amount
            if e.happiness_score is not None:
                scores.append(e.happiness_score)
        self._table.setSortingEnabled(True)

        n = len(self._expenses)
        avg = f"{sum(scores)/len(scores):.1f}" if scores else "–"
        self.statusBar().showMessage(
            f"{n} expense{'s' if n != 1 else ''}  |  "
            f"Total: {total:.2f} RON  |  Avg score: {avg}"
        )

    def _populate_row(self, row: int, e: Expense):
        def item(text, center=False):
            it = QTableWidgetItem(str(text))
            flag = Qt.AlignmentFlag.AlignCenter if center else Qt.AlignmentFlag.AlignLeft
            it.setTextAlignment(flag | Qt.AlignmentFlag.AlignVCenter)
            return it

        self._table.setItem(row, 0, item(e.date.isoformat()))
        self._table.setItem(row, 1, item(e.description))
        self._table.setItem(row, 2, item(e.category.value))
        self._table.setItem(row, 3, item(f"{e.amount:.2f}", center=True))
        self._table.setItem(row, 4, item("✓" if e.experiential else "–", center=True))
        self._table.setItem(row, 5, item("✓" if e.social      else "–", center=True))
        self._table.setItem(row, 6, item("✓" if e.planned     else "–", center=True))
        self._table.setItem(row, 7, item("✓" if e.time_saving else "–", center=True))

        if e.duration_minutes:
            cph = float(e.amount) / (e.duration_minutes / 60.0)
            self._table.setItem(row, 8, item(f"{cph:.1f}", center=True))
        else:
            self._table.setItem(row, 8, item("–", center=True))

        score_text = f"{e.happiness_score:.1f}" if e.happiness_score is not None else "–"
        self._table.setItem(row, 9, item(score_text, center=True))

    def _compute_score(self, expense: Expense) -> float:
        cumulative = self._dao.cumulative_spend(expense.category, expense.date)
        recent = self._dao.recent_count(
            expense.category,
            expense.date - timedelta(days=30),
            exclude_id=expense.id,
        )
        return calculate_score(expense, cumulative, recent)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_tab_changed(self, index: int):
        if index == _DASHBOARD_TAB:
            self._dashboard.refresh(self._expenses, dark=self._dark)

    def _on_add(self):
        form = ExpenseForm(self)
        form.exec()
        expense = form.get_expense()
        if expense is None:
            return
        saved = self._dao.add(expense)
        saved.happiness_score = self._compute_score(saved)
        self._dao.update(saved)
        self._refresh()

    def _on_edit(self):
        expense = self._selected_expense()
        if expense is None:
            QMessageBox.information(self, "No selection", "Select an expense to edit.")
            return
        form = ExpenseForm(self, expense=expense)
        form.exec()
        updated = form.get_expense(existing_id=expense.id)
        if updated is None:
            return
        updated.happiness_score = self._compute_score(updated)
        self._dao.update(updated)
        self._refresh()

    def _on_delete(self):
        expense = self._selected_expense()
        if expense is None:
            QMessageBox.information(self, "No selection", "Select an expense to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete \"{expense.description}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._dao.delete(expense.id)
            self._refresh()

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        rows = parse_file(path)
        if not rows:
            QMessageBox.information(self, "Empty File", "No data rows found in the file.")
            return
        dialog = ImportDialog(rows, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        expenses = dialog.valid_expenses()
        for expense in expenses:
            saved = self._dao.add(expense)
            saved.happiness_score = self._compute_score(saved)
            self._dao.update(saved)
        self._refresh()
        QMessageBox.information(
            self, "Import Complete",
            f"Imported {len(expenses)} expense{'s' if len(expenses) != 1 else ''}."
        )

    def _on_how_it_works(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("How it works")
        dlg.resize(720, 640)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(InfoTab())
        dlg.exec()

    def _on_about(self):
        QMessageBox.about(
            self,
            "About Finance Happiness",
            "<b>Finance Happiness</b> v0.1.0<br><br>"
            "A personal finance manager that scores each purchase<br>"
            "against evidence from behavioural economics research.<br><br>"
            "<b>Scientific basis:</b><br>"
            "Van Boven &amp; Gilovich (2003) · Kahneman &amp; Deaton (2010)<br>"
            "Dunn, Aknin &amp; Norton (2008) · Whillans et al. (2017)<br><br>"
            "Built with Python 3.11, PyQt6, pandas, matplotlib.",
        )

    def _selected_expense(self) -> Expense | None:
        row = self._table.currentRow()
        if row < 0 or row >= len(self._expenses):
            return None
        return self._expenses[row]
