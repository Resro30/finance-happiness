from decimal import Decimal

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from finance_happiness.analytics import (
    avg_score_by_category,
    cost_per_hour_by_category,
    monthly_avg_score,
    score_per_ron_by_category,
    spending_by_category,
    to_dataframe,
    top_and_bottom,
)
from finance_happiness.models import Expense

_ACCENT = "#4C72B0"
_GOOD   = "#55A868"
_BAD    = "#C44E52"


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = False
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        content = QWidget()
        self._layout = QVBoxLayout(content)
        self._layout.setSpacing(16)
        self._layout.setContentsMargins(16, 16, 16, 16)

        # --- stat cards row ---
        self._stats_row = QHBoxLayout()
        self._stat_total = self._stat_card("Total Spent",                      "–", "#F97316")
        self._stat_avg   = self._stat_card("Avg Score",                        "–", "#8B5CF6")
        self._stat_best  = self._stat_card("Best Efficiency Per RON Category", "–", "#EC4899")
        self._stat_count = self._stat_card("Purchases",                        "–", "#64748B")
        for card in (self._stat_total, self._stat_avg, self._stat_best, self._stat_count):
            self._stats_row.addWidget(card)
        self._layout.addLayout(self._stats_row)

        # --- charts row 1: spending | avg score ---
        row1 = QHBoxLayout()
        self._fig_spend, self._canvas_spend = self._make_canvas((5, 3))
        self._fig_score, self._canvas_score = self._make_canvas((5, 3))
        row1.addWidget(self._canvas_spend)
        row1.addWidget(self._canvas_score)
        self._layout.addLayout(row1)

        # --- chart row 2: score over time | cost per hour ---
        row2 = QHBoxLayout()
        self._fig_time, self._canvas_time = self._make_canvas((5, 2.5))
        self._fig_cph,  self._canvas_cph  = self._make_canvas((5, 2.5))
        row2.addWidget(self._canvas_time)
        row2.addWidget(self._canvas_cph)
        self._layout.addLayout(row2)

        # --- best / worst tables ---
        row3 = QHBoxLayout()
        self._best_table  = self._make_mini_table("Best Scored")
        self._worst_table = self._make_mini_table("Worst Scored")
        row3.addWidget(self._best_table)
        row3.addWidget(self._worst_table)
        self._layout.addLayout(row3)

        self._layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh(self, expenses: list[Expense], dark: bool = False) -> None:
        self._dark = dark
        df = to_dataframe(expenses)
        self._update_stats(df, expenses)
        self._draw_spending(df)
        self._draw_avg_score(df)
        self._draw_timeline(df)
        self._draw_cost_per_hour(df)
        self._update_roi_tables(df)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def _update_stats(self, df: pd.DataFrame, expenses: list[Expense]) -> None:
        total = sum(e.amount for e in expenses) if expenses else Decimal("0")
        self._set_stat(self._stat_total, f"{total:.2f} RON")
        self._set_stat(self._stat_count, str(len(expenses)))

        scored = df.dropna(subset=["score"]) if not df.empty else pd.DataFrame()
        if not scored.empty:
            avg = scored["score"].mean()
            self._set_stat(self._stat_avg, f"{avg:.1f} / 10")
            roi = score_per_ron_by_category(df)
            if not roi.empty:
                self._set_stat(self._stat_best, roi.idxmax())
            else:
                self._set_stat(self._stat_best, "–")
        else:
            self._set_stat(self._stat_avg, "–")
            self._set_stat(self._stat_best, "–")

    # ------------------------------------------------------------------
    # Charts
    # ------------------------------------------------------------------

    def _draw_spending(self, df: pd.DataFrame) -> None:
        c = self._chart_colors()
        ax = self._reset_figure(self._fig_spend)
        self._style_ax(ax, c)
        series = spending_by_category(df)
        if series.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, color=c["fg"])
        else:
            ax.barh(series.index, series.values, color=c["bar"])
            ax.set_xlabel("RON")
            ax.set_title("Spending by Category")
            for bar, val in zip(ax.patches, series.values):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                        f"{val:.0f}", va="center", fontsize=8, color=c["fg"])
        self._canvas_spend.draw()

    def _draw_avg_score(self, df: pd.DataFrame) -> None:
        c = self._chart_colors()
        ax = self._reset_figure(self._fig_score)
        self._style_ax(ax, c)
        series = avg_score_by_category(df)
        if series.empty:
            ax.text(0.5, 0.5, "No scored data", ha="center", va="center",
                    transform=ax.transAxes, color=c["fg"])
        else:
            colors = [_GOOD if v >= 5 else _BAD for v in series.values]
            ax.barh(series.index, series.values, color=colors)
            ax.set_xlim(0, 10)
            ax.set_xlabel("Avg Score")
            ax.set_title("Avg Happiness Score by Category")
            ax.axvline(5, color="grey", linewidth=0.8, linestyle="--")
        self._canvas_score.draw()

    def _draw_cost_per_hour(self, df: pd.DataFrame) -> None:
        c = self._chart_colors()
        ax = self._reset_figure(self._fig_cph)
        self._style_ax(ax, c)
        series = cost_per_hour_by_category(df)
        if series.empty:
            ax.text(0.5, 0.5, "Add duration to purchases\nto see cost efficiency",
                    ha="center", va="center", transform=ax.transAxes,
                    color=c["fg"], fontsize=9)
        else:
            ax.barh(series.index, series.values, color=c["bar"])
            ax.set_xlabel("RON / hour  (lower = better value)")
            ax.set_title("Cost Efficiency by Category (per hour)")
            for bar, val in zip(ax.patches, series.values):
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                        f"{val:.1f}", va="center", fontsize=8, color=c["fg"])
        self._canvas_cph.draw()

    def _draw_timeline(self, df: pd.DataFrame) -> None:
        c = self._chart_colors()
        ax = self._reset_figure(self._fig_time)
        self._style_ax(ax, c)
        series = monthly_avg_score(df)
        if series.empty:
            ax.text(0.5, 0.5, "Not enough data", ha="center", va="center",
                    transform=ax.transAxes, color=c["fg"])
        else:
            ax.plot(series.index, series.values, marker="o", color=c["bar"], linewidth=2)
            ax.set_ylim(0, 10)
            ax.set_ylabel("Avg Score")
            ax.set_title("Average Happiness Score Over Time")
            ax.tick_params(axis="x", rotation=30)
            ax.grid(axis="y", linestyle="--", alpha=0.4, color=c["grid"])
        self._canvas_time.draw()

    # ------------------------------------------------------------------
    # ROI tables
    # ------------------------------------------------------------------

    def _update_roi_tables(self, df: pd.DataFrame) -> None:
        best, worst = top_and_bottom(df, n=5)
        self._fill_mini_table(self._best_table,  best,  _GOOD)
        self._fill_mini_table(self._worst_table, worst, _BAD)

    def _fill_mini_table(self, widget: QWidget, data: pd.DataFrame, color: str) -> None:
        table: QTableWidget = widget.findChild(QTableWidget)
        table.setRowCount(len(data))
        for row_idx, row in data.iterrows():
            table.setItem(row_idx, 0, QTableWidgetItem(str(row["description"])[:30]))
            table.setItem(row_idx, 1, QTableWidgetItem(str(row["category"])))
            table.setItem(row_idx, 2, QTableWidgetItem(f"{row['amount']:.2f}"))
            score_item = QTableWidgetItem(f"{row['score']:.1f}")
            score_item.setForeground(Qt.GlobalColor.white)
            score_item.setBackground(
                __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(color)
            )
            table.setItem(row_idx, 3, score_item)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_canvas(figsize: tuple) -> tuple[Figure, FigureCanvasQTAgg]:
        fig = Figure(figsize=figsize, tight_layout=True)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return fig, canvas

    def _chart_colors(self):
        if self._dark:
            return {"bg": "#242535", "fg": "#e2e8f0", "grid": "#353650", "bar": "#7aa2f7"}
        return {"bg": "#ffffff", "fg": "#1a1a2e", "grid": "#e8eaf0", "bar": _ACCENT}

    def _style_ax(self, ax, colors):
        ax.set_facecolor(colors["bg"])
        ax.figure.set_facecolor(colors["bg"])
        ax.tick_params(colors=colors["fg"], labelcolor=colors["fg"])
        ax.xaxis.label.set_color(colors["fg"])
        ax.yaxis.label.set_color(colors["fg"])
        ax.title.set_color(colors["fg"])
        for spine in ax.spines.values():
            spine.set_edgecolor(colors["grid"])

    @staticmethod
    def _reset_figure(fig: Figure):
        fig.clear()
        return fig.add_subplot(111)

    @staticmethod
    def _stat_card(title: str, initial_value: str, accent: str = "#64748B") -> QFrame:
        outer = QFrame()
        outer.setFrameStyle(QFrame.Shape.StyledPanel)
        outer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(outer)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        from PyQt6.QtWidgets import QWidget as _QWidget
        strip = _QWidget()
        strip.setFixedWidth(5)
        strip.setStyleSheet(f"background-color: {accent};")
        row.addWidget(strip)

        inner = _QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(12, 10, 12, 10)

        val_label = QLabel(initial_value)
        val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        val_label.setFont(font)
        val_label.setObjectName("stat_value")

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)

        layout.addWidget(val_label)
        layout.addWidget(title_label)
        row.addWidget(inner)
        return outer

    @staticmethod
    def _set_stat(card: QFrame, value: str) -> None:
        card.findChild(QLabel, "stat_value").setText(value)

    @staticmethod
    def _make_mini_table(title: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel(f"<b>{title}</b>"))

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Description", "Category", "RON", "Score"])
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(
            0, __import__("PyQt6.QtWidgets", fromlist=["QHeaderView"]).QHeaderView.ResizeMode.Stretch
        )
        table.setEditTriggers(
            __import__("PyQt6.QtWidgets", fromlist=["QAbstractItemView"]).QAbstractItemView.EditTrigger.NoEditTriggers
        )
        table.setSelectionMode(
            __import__("PyQt6.QtWidgets", fromlist=["QAbstractItemView"]).QAbstractItemView.SelectionMode.NoSelection
        )
        table.setMaximumHeight(180)
        layout.addWidget(table)
        return container
