import math
from decimal import Decimal

from finance_happiness.models import Expense, PerceivedValue

# --- Tag multipliers ---
_EXPERIENTIAL_BOOST  = 1.30   # Van Boven & Gilovich (2003)
_SOCIAL_BOOST        = 1.20   # Dunn, Aknin & Norton (2008)
_PLANNED_BOOST       = 1.15   # behavioural economics consensus
_IMPULSE_PENALTY     = 0.90
_TIME_SAVING_BOOST   = 1.20   # Whillans et al. (2017)

# Theoretical maximum raw score (all four boosts, no history penalties)
_MAX_RAW = _EXPERIENTIAL_BOOST * _SOCIAL_BOOST * _PLANNED_BOOST * _TIME_SAVING_BOOST

# --- Diminishing returns (cumulative category spend) ---
_SATURATION_POINT = Decimal("500")   # RON — spend level where factor ≈ 0.5

# --- Hedonic adaptation (purchase repetition in 30-day window) ---
_ADAPTATION_STEP  = 0.10
_ADAPTATION_FLOOR = 0.60

# --- Perceived value / transaction utility (Thaler, 1985) ---
# Base modifier: how much psychological value the buyer felt they received.
_VALUE_BASE: dict[PerceivedValue, float] = {
    PerceivedValue.GREAT_DEAL:      1.20,
    PerceivedValue.FAIR:            1.08,
    PerceivedValue.NORMAL:          1.00,
    PerceivedValue.EXPENSIVE_TREAT: 0.92,
    PerceivedValue.SPLURGE:         0.80,
}
# Additional guilt penalty that only applies when the purchase was unplanned.
# A splurge you carefully planned for feels different from a splurge on impulse.
_VALUE_IMPULSE_PENALTY: dict[PerceivedValue, float] = {
    PerceivedValue.GREAT_DEAL:      0.00,
    PerceivedValue.FAIR:            0.00,
    PerceivedValue.NORMAL:          0.00,
    PerceivedValue.EXPENSIVE_TREAT: 0.12,
    PerceivedValue.SPLURGE:         0.20,
}


def calculate_score(
    expense: Expense,
    cumulative_category_spend: Decimal,
    recent_category_count: int,
) -> float:
    """
    Return a happiness score in [0, 10] for a single expense.

    Duration is intentionally excluded from this score.  It belongs in the
    separate RON/hr cost-efficiency metric, not here — conflating the two
    would reward volume of hours over quality of experience, which is not
    what the behavioural-economics literature measures.

    Parameters
    ----------
    expense:
        The expense to evaluate.
    cumulative_category_spend:
        Total amount already spent in the same category *before* this
        purchase.  Used to model diminishing returns.
    recent_category_count:
        Number of purchases in the same category in the last 30 days,
        *not* counting this expense.  Used to model hedonic adaptation.
    """
    # 1. Tag multipliers
    tag_multiplier = (
        (_EXPERIENTIAL_BOOST if expense.experiential else 1.0)
        * (_SOCIAL_BOOST      if expense.social       else 1.0)
        * (_PLANNED_BOOST     if expense.planned       else _IMPULSE_PENALTY)
        * (_TIME_SAVING_BOOST if expense.time_saving   else 1.0)
    )

    # 2. Diminishing returns — logarithmic decay over cumulative category spend
    diminishing = 1.0 / (
        1.0 + math.log1p(float(cumulative_category_spend) / float(_SATURATION_POINT))
    )

    # 3. Hedonic adaptation — repeated purchases in the same category
    adaptation = max(
        _ADAPTATION_FLOOR,
        1.0 - recent_category_count * _ADAPTATION_STEP,
    )

    # 4. Transaction utility (perceived value / guilt factor) — Thaler (1985)
    #    Omitting this field leaves the factor neutral at 1.0.
    if expense.perceived_value is not None:
        base = _VALUE_BASE[expense.perceived_value]
        guilt = (
            _VALUE_IMPULSE_PENALTY[expense.perceived_value]
            if not expense.planned
            else 0.0
        )
        value_factor = base - guilt
    else:
        value_factor = 1.0

    # 5. Scale to [0, 10]
    raw = tag_multiplier * diminishing * adaptation * value_factor
    score = (raw / _MAX_RAW) * 10.0

    return round(min(10.0, max(0.0, score)), 2)
