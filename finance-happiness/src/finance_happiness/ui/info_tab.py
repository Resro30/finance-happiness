from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)


def _section(title: str, body: str) -> QFrame:
    frame = QFrame()
    frame.setFrameStyle(QFrame.Shape.StyledPanel)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    layout = QVBoxLayout(frame)
    layout.setSpacing(8)

    heading = QLabel(f"<b style='font-size:13px'>{title}</b>")
    heading.setWordWrap(True)
    layout.addWidget(heading)

    text = QLabel(body)
    text.setWordWrap(True)
    text.setTextFormat(Qt.TextFormat.RichText)
    text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    layout.addWidget(text)

    return frame


class InfoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        intro = QLabel(
            "<h2 style='margin-bottom:4px'>How Finance Happiness works</h2>"
            "<p style='color:grey'>Each purchase is scored 0–10 using findings from "
            "behavioural economics. This tab explains every factor so you know exactly "
            "what the numbers mean.</p>"
        )
        intro.setWordWrap(True)
        intro.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(intro)

        layout.addWidget(_section(
            "The Happiness Score  (0 – 10)",
            "The score is calculated in four stages that are multiplied together, "
            "then scaled to a 0–10 range:<br><br>"
            "<b>1. Tag multipliers</b> — four yes/no questions at the time of purchase "
            "(see Tags section below).<br>"
            "<b>2. Diminishing returns</b> — the more you have already spent in the "
            "same category, the smaller the boost from the next purchase. "
            "Modelled as a logarithmic curve; the factor halves around 860 RON of "
            "all-time cumulative spending in that category.<br>"
            "<b>3. Hedonic adaptation</b> — buying the same category repeatedly within "
            "30 days reduces novelty. Each additional recent purchase subtracts 10 % "
            "from the score, down to a floor of 60 %.<br>"
            "<b>4. Perceived value</b> (optional) — how the purchase felt price-wise "
            "at the moment of buying (see Perceived Value section below).<br><br>"
            "The four stages are combined as:<br>"
            "<code>score = (tag_mult × diminishing × adaptation × value_factor) "
            "/ max_possible × 10</code>",
        ))

        layout.addWidget(_section(
            "Happiness Tags — what to pick",
            "<b>Type — Material vs Experience</b><br>"
            "Experiential purchases (concerts, meals out, travel, activities) "
            "deliver longer-lasting satisfaction than material goods. "
            "This gives a <b>+30 %</b> boost. "
            "<i>Research: Van Boven &amp; Gilovich (2003)</i><br><br>"

            "<b>Context — Solo vs Social</b><br>"
            "Spending on or with other people consistently produces higher wellbeing "
            "than spending on yourself alone. <b>+20 %</b>. "
            "<i>Dunn, Aknin &amp; Norton (2008)</i><br><br>"

            "<b>Intent — Spontaneous vs Anticipated</b><br>"
            "Planned and routine purchases have clearer expected value; "
            "impulse buys often produce post-purchase regret. "
            "Anticipated: <b>+15 %</b>. Spontaneous: <b>−10 %</b>. "
            "<i>Behavioural economics consensus</i><br><br>"

            "<b>Time — No time saved vs Saves me time</b><br>"
            "Buying back time (delivery, cleaning, transport) reliably lifts "
            "day-to-day happiness more than buying things. <b>+20 %</b>. "
            "<i>Whillans et al. (2017)</i>",
        ))

        layout.addWidget(_section(
            "Perceived Value (optional tag)",
            "This field captures how the price <i>felt</i> at the moment of buying — "
            "independent of the actual amount. It applies Thaler's "
            "<i>Transaction Utility Theory (1985)</i>: the psychological gain or loss "
            "from getting a deal (or not).<br><br>"
            "<b>Great deal / bargain</b> — felt cheaper than expected. <b>+20 %</b><br>"
            "<b>Fair price / worth it</b> — felt just right. <b>+8 %</b><br>"
            "<b>Normal price</b> — neutral, identical to leaving the field blank.<br>"
            "<b>Expensive treat</b> — felt pricey. <b>−8 %</b>, "
            "plus an extra <b>−12 %</b> guilt penalty if the purchase was unplanned.<br>"
            "<b>Luxury / splurge</b> — felt very expensive. <b>−20 %</b>, "
            "plus <b>−20 %</b> extra if unplanned.<br><br>"
            "The guilt penalty only applies when Intent is set to Spontaneous. "
            "A planned splurge you saved up for feels different from an impulse one.",
        ))

        layout.addWidget(_section(
            "Diminishing Returns — all-time cumulative category spend",
            "The diminishing-returns factor looks at how much you have spent in the "
            "same category <b>before</b> the current purchase, across all time — "
            "not just 30 days. It uses a logarithmic curve:<br><br>"
            "<code>factor = 1 / (1 + ln(1 + cumulative / 500))</code><br><br>"
            "At 0 RON prior spending the factor is 1.0 (no penalty). "
            "At 500 RON it is approximately 0.59. "
            "The factor halves (reaches 0.5) at around 860 RON of cumulative spending. "
            "At 2 000 RON it is approximately 0.38. "
            "The score never reaches zero — even heavily repeated spending "
            "still gets some credit.",
        ))

        layout.addWidget(_section(
            "Hedonic Adaptation — 30-day repeat window",
            "Buying in the same category multiple times within a 30-day window "
            "reduces novelty, which is modelled as a step-down penalty:<br><br>"
            "<code>adaptation = max(0.60,  1.0 − recent_count × 0.10)</code><br><br>"
            "0 recent purchases → no penalty (factor 1.0).<br>"
            "3 recent purchases → factor 0.70.<br>"
            "4+ recent purchases → floor of 0.60.<br><br>"
            "The 30-day window is counted backwards from the date of <i>this</i> "
            "purchase, not from today. Editing or re-dating a purchase recalculates "
            "its score against the historical window that was correct at that time.",
        ))

        layout.addWidget(_section(
            "RON / hr — Cost Efficiency (per hour)",
            "Separate from the happiness score, the app tracks how much each "
            "purchase costs per hour of use:<br><br>"
            "<code>RON/hr = amount ÷ (duration_minutes ÷ 60)</code><br><br>"
            "Lower is better — a 45 RON movie (2 h) costs 22.5 RON/hr, "
            "while a 300 RON game (100 h) costs only 3.0 RON/hr.<br><br>"
            "This metric is intentionally kept separate from the happiness score. "
            "A 20-minute coffee with friends can score higher than a 100-hour "
            "solo game because the score measures <i>psychological quality</i>, "
            "not volume of hours. Duration is optional — only fill it in when "
            "it makes sense to compare cost-per-use.",
        ))

        layout.addWidget(_section(
            "Dashboard — what each metric means",
            "<b>Total Spent</b> — sum of all recorded expenses.<br>"
            "<b>Avg Score</b> — mean happiness score across all scored purchases.<br>"
            "<b>Best Efficiency Per RON Category</b> — the category with the "
            "highest ratio of average happiness score to average amount spent "
            "(score ÷ RON × 100). Where your money converts most efficiently "
            "into wellbeing.<br>"
            "<b>Purchases</b> — total number of recorded expenses.<br><br>"
            "<b>Spending by Category</b> — total RON spent per category.<br>"
            "<b>Avg Happiness Score by Category</b> — mean score per category; "
            "green bars are above 5, red below.<br>"
            "<b>Average Happiness Score Over Time</b> — monthly average score trend.<br>"
            "<b>Cost Efficiency by Category (per hour)</b> — average RON/hr per "
            "category, for purchases that have a duration. Lower = better value per "
            "hour of use.<br><br>"
            "<b>Best Scored / Worst Scored</b> — your top 5 and bottom 5 individual "
            "purchases ranked by happiness score.",
        ))

        layout.addWidget(_section(
            "CSV Import — supported columns",
            "The importer accepts a CSV file with these column names "
            "(all are optional except <i>amount</i>, <i>description</i>, and <i>date</i>):<br><br>"
            "<code>amount, description, date, category, experiential, social, "
            "planned, time_saving, duration_minutes, perceived_value</code><br><br>"
            "<b>date</b> — accepted formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, DD.MM.YYYY<br>"
            "<b>category</b> — FOOD, TRANSPORT, ENTERTAINMENT, ELECTRONICS, HEALTH, "
            "EDUCATION, CLOTHING, OTHER (defaults to OTHER if missing or unrecognised)<br>"
            "<b>experiential / social / planned / time_saving</b> — "
            "true / false, 1 / 0, yes / no<br>"
            "<b>duration_minutes</b> — positive integer; leave empty to omit<br>"
            "<b>perceived_value</b> — GREAT_DEAL, FAIR, NORMAL, EXPENSIVE_TREAT, "
            "SPLURGE (or the full display text); leave empty to omit<br><br>"
            "Negative amounts (bank debits) are converted to positive automatically. "
            "Rows with invalid data are shown in the import preview so you can "
            "review them before confirming.",
        ))

        layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
