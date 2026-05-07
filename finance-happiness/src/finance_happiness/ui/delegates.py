from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QStyleOptionViewItem, QStyledItemDelegate

_CATEGORY_COLORS: dict[str, str] = {
    "Food":          "#F97316",
    "Transport":     "#0EA5E9",
    "Entertainment": "#A855F7",
    "Electronics":   "#06B6D4",
    "Health":        "#0D9488",
    "Education":     "#6366F1",
    "Clothing":      "#EC4899",
    "Other":         "#94A3B8",
}

_SCORE_HIGH   = 7.0
_SCORE_MEDIUM = 4.0
_PILL_HIGH    = QColor("#55A868")
_PILL_MEDIUM  = QColor("#C8860A")
_PILL_LOW     = QColor("#C44E52")


class ScorePillDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        QApplication.style().drawControl(
            QApplication.style().ControlElement.CE_ItemViewItem, opt, painter
        )

        if text == "–":
            painter.save()
            painter.setPen(opt.palette.text().color())
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, text)
            painter.restore()
            return

        try:
            score = float(text)
        except ValueError:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = (
            _PILL_HIGH   if score >= _SCORE_HIGH
            else _PILL_MEDIUM if score >= _SCORE_MEDIUM
            else _PILL_LOW
        )

        r = option.rect
        pill_w, pill_h = 52, 22
        pill = QRect(
            r.x() + (r.width()  - pill_w) // 2,
            r.y() + (r.height() - pill_h) // 2,
            pill_w, pill_h,
        )
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(pill, 11, 11)

        painter.setPen(QColor("white"))
        painter.drawText(pill, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(70, 34)


class CategoryChipDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        color = QColor(_CATEGORY_COLORS.get(text, "#94A3B8"))

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        QApplication.style().drawControl(
            QApplication.style().ControlElement.CE_ItemViewItem, opt, painter
        )

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = option.rect
        chip_h = 20
        chip_w = min(r.width() - 12, 110)
        chip = QRect(
            r.x() + (r.width()  - chip_w) // 2,
            r.y() + (r.height() - chip_h) // 2,
            chip_w, chip_h,
        )

        bg = QColor(color)
        bg.setAlpha(55)
        painter.setBrush(bg)
        painter.setPen(color)
        painter.drawRoundedRect(chip, 10, 10)

        fm = painter.fontMetrics()
        elided = fm.elidedText(text, Qt.TextElideMode.ElideRight, chip_w - 10)
        painter.setPen(color)
        painter.drawText(chip, Qt.AlignmentFlag.AlignCenter, elided)
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(110, 34)
