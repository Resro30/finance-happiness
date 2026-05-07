LIGHT = """
QMainWindow, QDialog, QWidget {
    background-color: #f0f2f5;
    color: #1a1a2e;
    font-size: 13px;
}

QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #dde1e7;
    padding: 2px 6px;
    spacing: 4px;
}
QToolButton {
    padding: 5px 14px;
    border-radius: 4px;
    color: #1a1a2e;
    background: transparent;
}
QToolButton:hover   { background-color: #e4e8f0; }
QToolButton:pressed { background-color: #d0d6e2; }

QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #dde1e7;
}
QMenuBar::item:selected { background-color: #e4e8f0; }
QMenu { background-color: #ffffff; border: 1px solid #dde1e7; }
QMenu::item { padding: 4px 24px; }
QMenu::item:selected { background-color: #dbe5f1; }

QTabWidget::pane {
    border: 1px solid #dde1e7;
    background-color: #ffffff;
    top: -1px;
}
QTabBar::tab {
    background-color: #e4e8f0;
    color: #555577;
    padding: 7px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected { background-color: #ffffff; color: #4C72B0; font-weight: bold; }
QTabBar::tab:hover:!selected { background-color: #d8dcea; }

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f6f8fc;
    gridline-color: #e8eaf0;
    border: 1px solid #dde1e7;
}
QTableWidget::item { padding: 3px 8px; }
QTableWidget::item:selected { background-color: #dbe5f1; color: #1a1a2e; }
QHeaderView::section {
    background-color: #eef0f7;
    color: #444466;
    padding: 6px 8px;
    border: none;
    border-right: 1px solid #dde1e7;
    border-bottom: 2px solid #c8cede;
    font-weight: bold;
}

QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #ccd0dc;
    border-radius: 4px;
    padding: 5px 8px;
    color: #1a1a2e;
}
QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
    border-color: #4C72B0;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1a1a2e;
    selection-background-color: #dbe5f1;
    border: 1px solid #ccd0dc;
}

QGroupBox {
    color: #1a1a2e;
    border: 1px solid #ccd0dc;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #4C72B0;
    font-weight: bold;
}

QRadioButton { spacing: 6px; color: #1a1a2e; }
QRadioButton::indicator { width: 15px; height: 15px; }
QRadioButton::indicator:checked { background-color: #4C72B0; border: 3px solid #ffffff; border-radius: 7px; outline: 1px solid #4C72B0; }

QCheckBox { spacing: 6px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 1px solid #aab0c0; background: #ffffff; }
QCheckBox::indicator:checked { background-color: #4C72B0; border-color: #4C72B0; }

QPushButton {
    background-color: #4C72B0;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 6px 18px;
    font-weight: bold;
}
QPushButton:hover   { background-color: #3a60a0; }
QPushButton:pressed { background-color: #2a5090; }
QPushButton:disabled { background-color: #b8c0d0; color: #888899; }

QStatusBar { background-color: #ffffff; border-top: 1px solid #dde1e7; color: #555577; }

QScrollBar:vertical { background: #f0f2f5; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #c0c8d8; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #a8b4c8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

DARK = """
QMainWindow, QDialog, QWidget {
    background-color: #1a1b2e;
    color: #e2e8f0;
    font-size: 13px;
}

QToolBar {
    background-color: #242535;
    border-bottom: 1px solid #353650;
    padding: 2px 6px;
    spacing: 4px;
}
QToolButton {
    padding: 5px 14px;
    border-radius: 4px;
    color: #e2e8f0;
    background: transparent;
}
QToolButton:hover   { background-color: #353650; }
QToolButton:pressed { background-color: #454668; }

QMenuBar {
    background-color: #242535;
    color: #e2e8f0;
    border-bottom: 1px solid #353650;
}
QMenuBar::item { color: #e2e8f0; background: transparent; padding: 4px 10px; }
QMenuBar::item:selected { background-color: #353650; }
QMenu { background-color: #242535; color: #e2e8f0; border: 1px solid #454660; }
QMenu::item { padding: 4px 24px; color: #e2e8f0; }
QMenu::item:selected { background-color: #3a4a6a; }

QTabWidget::pane { border: 1px solid #353650; background-color: #242535; top: -1px; }
QTabBar::tab {
    background-color: #1a1b2e;
    color: #8890a8;
    padding: 7px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected { background-color: #242535; color: #7aa2f7; font-weight: bold; }
QTabBar::tab:hover:!selected { background-color: #252640; }

QTableWidget {
    background-color: #242535;
    alternate-background-color: #2a2b42;
    gridline-color: #353650;
    border: 1px solid #353650;
    color: #e2e8f0;
}
QTableWidget::item { padding: 3px 8px; color: #e2e8f0; }
QTableWidget::item:selected { background-color: #3a4a6a; color: #e2e8f0; }
QHeaderView::section {
    background-color: #1a1b2e;
    color: #8890a8;
    padding: 6px 8px;
    border: none;
    border-right: 1px solid #353650;
    border-bottom: 2px solid #454660;
    font-weight: bold;
}

QAbstractScrollArea { background-color: #1a1b2e; color: #e2e8f0; }
QScrollArea > QWidget > QWidget { background-color: #1a1b2e; }

QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox {
    background-color: #2a2b3e;
    border: 1px solid #454660;
    border-radius: 4px;
    padding: 5px 8px;
    color: #e2e8f0;
}
QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
    border-color: #7aa2f7;
}
QComboBox QAbstractItemView {
    background-color: #2a2b3e;
    color: #e2e8f0;
    selection-background-color: #3a4a6a;
    selection-color: #e2e8f0;
    border: 1px solid #454660;
}
QComboBox::drop-down { border: none; }

QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QDateEdit::up-button, QDateEdit::down-button {
    background-color: #353650;
    border: none;
    width: 16px;
}

QCalendarWidget QWidget { background-color: #242535; color: #e2e8f0; }
QCalendarWidget QToolButton { background-color: #353650; color: #e2e8f0; border-radius: 3px; }
QCalendarWidget QAbstractItemView { background-color: #242535; color: #e2e8f0; selection-background-color: #3a4a6a; }
QCalendarWidget QMenu { background-color: #242535; color: #e2e8f0; }
QCalendarWidget QSpinBox { background-color: #2a2b3e; color: #e2e8f0; border: 1px solid #454660; }

QGroupBox {
    color: #e2e8f0;
    border: 1px solid #454660;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #7aa2f7;
    font-weight: bold;
}

QRadioButton { spacing: 6px; color: #e2e8f0; }
QRadioButton::indicator { width: 15px; height: 15px; }
QRadioButton::indicator:checked { background-color: #7aa2f7; border: 3px solid #1a1b2e; border-radius: 7px; outline: 1px solid #7aa2f7; }

QCheckBox { spacing: 6px; color: #e2e8f0; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 1px solid #555680; background: #2a2b3e; }
QCheckBox::indicator:checked { background-color: #7aa2f7; border-color: #7aa2f7; }

QPushButton {
    background-color: #7aa2f7;
    color: #1a1b2e;
    border: none;
    border-radius: 4px;
    padding: 6px 18px;
    font-weight: bold;
}
QPushButton:hover   { background-color: #6a92e7; }
QPushButton:pressed { background-color: #5a82d7; }
QPushButton:disabled { background-color: #353650; color: #606080; }

QLabel { color: #e2e8f0; }
QStatusBar { background-color: #242535; border-top: 1px solid #353650; color: #8890a8; }
QMessageBox { background-color: #242535; }
QMessageBox QLabel { color: #e2e8f0; }

QScrollBar:vertical { background: #1a1b2e; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #454660; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #555680; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #1a1b2e; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: #454660; border-radius: 5px; min-width: 24px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""
