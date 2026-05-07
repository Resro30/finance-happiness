import sys

from PyQt6.QtWidgets import QApplication

from finance_happiness.database import ExpenseDAO, create_schema, default_db_path, open_connection
from finance_happiness.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    conn = open_connection(default_db_path())
    create_schema(conn)
    dao = ExpenseDAO(conn)

    window = MainWindow(dao)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
