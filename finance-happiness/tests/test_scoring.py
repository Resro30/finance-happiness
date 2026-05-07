import pytest
from datetime import date
from decimal import Decimal

from finance_happiness.models import Expense, Category, PerceivedValue
from finance_happiness.scoring import calculate_score


def make_expense(**kwargs) -> Expense:
    defaults = dict(
        amount=Decimal("100.00"),
        category=Category.ENTERTAINMENT,
        description="Jazz concert",
        date=date(2024, 3, 10),
        experiential=True,
        social=True,
        planned=True,
        time_saving=False,
    )
    return Expense(**{**defaults, **kwargs})


# --- Score range ---

def test_score_is_between_0_and_10():
    score = calculate_score(make_expense(), Decimal("0"), 0)
    assert 0.0 <= score <= 10.0


def test_perfect_expense_scores_near_10():
    # All boosts active, no history
    e = make_expense(experiential=True, social=True, planned=True, time_saving=True)
    score = calculate_score(e, Decimal("0"), 0)
    assert score == 10.0


def test_worst_expense_scores_above_0():
    # No boosts, impulse penalty, heavy history
    e = make_expense(experiential=False, social=False, planned=False, time_saving=False)
    score = calculate_score(e, Decimal("5000"), 10)
    assert score > 0.0


# --- Tag multipliers ---

def test_experiential_scores_higher_than_material():
    base = dict(social=False, planned=True, time_saving=False)
    experiential = calculate_score(make_expense(experiential=True,  **base), Decimal("0"), 0)
    material     = calculate_score(make_expense(experiential=False, **base), Decimal("0"), 0)
    assert experiential > material


def test_social_scores_higher_than_solo():
    base = dict(experiential=False, planned=True, time_saving=False)
    social = calculate_score(make_expense(social=True,  **base), Decimal("0"), 0)
    solo   = calculate_score(make_expense(social=False, **base), Decimal("0"), 0)
    assert social > solo


def test_planned_scores_higher_than_impulse():
    base = dict(experiential=False, social=False, time_saving=False)
    planned = calculate_score(make_expense(planned=True,  **base), Decimal("0"), 0)
    impulse = calculate_score(make_expense(planned=False, **base), Decimal("0"), 0)
    assert planned > impulse


def test_time_saving_scores_higher():
    base = dict(experiential=False, social=False, planned=True)
    saving  = calculate_score(make_expense(time_saving=True,  **base), Decimal("0"), 0)
    no_save = calculate_score(make_expense(time_saving=False, **base), Decimal("0"), 0)
    assert saving > no_save


# --- Diminishing returns ---

def test_higher_cumulative_spend_lowers_score():
    e = make_expense()
    low_history  = calculate_score(e, Decimal("0"),    0)
    high_history = calculate_score(e, Decimal("2000"), 0)
    assert low_history > high_history


def test_zero_cumulative_spend_gives_no_penalty():
    e = make_expense(experiential=True, social=True, planned=True, time_saving=True)
    score = calculate_score(e, Decimal("0"), 0)
    assert score == 10.0


# --- Hedonic adaptation ---

def test_more_recent_purchases_lowers_score():
    e = make_expense()
    first_purchase    = calculate_score(e, Decimal("0"), 0)
    repeated_purchase = calculate_score(e, Decimal("0"), 5)
    assert first_purchase > repeated_purchase


def test_adaptation_has_a_floor():
    e = make_expense(experiential=True, social=True, planned=True, time_saving=True)
    # Extreme repetition — adaptation should not drive score to zero
    score = calculate_score(e, Decimal("0"), 100)
    assert score > 0.0


# --- Concrete expected values (regression tests) ---

def test_known_score_concert():
    # tag_mult = 1.30 * 1.20 * 1.15 * 1.00 = 1.794, no history, no duration
    # score = (1.794 / 2.1528) * 10 ≈ 8.33
    e = make_expense(experiential=True, social=True, planned=True, time_saving=False)
    score = calculate_score(e, Decimal("0"), 0)
    assert score == pytest.approx(8.33, abs=0.01)


def test_known_score_impulse_material_purchase():
    e = make_expense(experiential=False, social=False, planned=False, time_saving=False)
    score = calculate_score(e, Decimal("500"), 3)
    assert score == pytest.approx(1.73, abs=0.05)


# --- Duration does NOT affect the happiness score ---

def test_duration_does_not_change_score():
    """Duration belongs in RON/hr, not in the happiness score."""
    film = make_expense(duration_minutes=90)
    game = make_expense(duration_minutes=6000)
    none = make_expense(duration_minutes=None)
    s_film = calculate_score(film, Decimal("0"), 0)
    s_game = calculate_score(game, Decimal("0"), 0)
    s_none = calculate_score(none, Decimal("0"), 0)
    assert s_film == s_game == s_none


def test_coffee_scores_well_when_tags_are_good():
    """A 20-min social planned coffee should outscore a solo impulse game."""
    coffee = make_expense(experiential=True, social=True,
                          planned=True, time_saving=False, duration_minutes=20)
    game   = make_expense(experiential=True, social=False,
                          planned=False, time_saving=False, duration_minutes=6000)
    s_coffee = calculate_score(coffee, Decimal("0"), 0)
    s_game   = calculate_score(game,   Decimal("0"), 0)
    assert s_coffee > s_game


# --- Perceived value (transaction utility) ---

def test_great_deal_scores_higher_than_no_value():
    """A bargain should lift the score above the neutral baseline."""
    base = make_expense()
    deal = make_expense(perceived_value=PerceivedValue.GREAT_DEAL)
    assert calculate_score(deal, Decimal("0"), 0) > calculate_score(base, Decimal("0"), 0)


def test_splurge_scores_lower_than_no_value():
    """A luxury purchase should lower the score compared to the neutral baseline."""
    base   = make_expense()
    splurge = make_expense(perceived_value=PerceivedValue.SPLURGE)
    assert calculate_score(splurge, Decimal("0"), 0) < calculate_score(base, Decimal("0"), 0)


def test_expensive_treat_impulse_worse_than_planned():
    """An unplanned expensive treat carries a guilt penalty; a planned one does not."""
    planned  = make_expense(planned=True,  perceived_value=PerceivedValue.EXPENSIVE_TREAT)
    impulse  = make_expense(planned=False, perceived_value=PerceivedValue.EXPENSIVE_TREAT)
    assert calculate_score(planned, Decimal("0"), 0) > calculate_score(impulse, Decimal("0"), 0)


def test_splurge_impulse_penalty_larger_than_treat_impulse_penalty():
    """SPLURGE has a bigger guilt hit than EXPENSIVE_TREAT when unplanned."""
    treat   = make_expense(planned=False, perceived_value=PerceivedValue.EXPENSIVE_TREAT)
    splurge = make_expense(planned=False, perceived_value=PerceivedValue.SPLURGE)
    assert calculate_score(treat, Decimal("0"), 0) > calculate_score(splurge, Decimal("0"), 0)


def test_great_deal_impulse_no_penalty():
    """A bargain on impulse should not be penalised — there is no guilt in a great find."""
    planned = make_expense(planned=True,  perceived_value=PerceivedValue.GREAT_DEAL)
    impulse = make_expense(planned=False, perceived_value=PerceivedValue.GREAT_DEAL)
    assert calculate_score(planned, Decimal("0"), 0) != calculate_score(impulse, Decimal("0"), 0)
    # The difference comes from the PLANNED_BOOST / IMPULSE_PENALTY, not the value factor.
    # Both should score above the neutral baseline (no perceived_value).
    neutral = make_expense(planned=False)
    assert calculate_score(impulse, Decimal("0"), 0) > calculate_score(neutral, Decimal("0"), 0)


def test_none_perceived_value_is_neutral():
    """Omitting perceived_value must not change the score."""
    e_none = make_expense(perceived_value=None)
    e_norm = make_expense(perceived_value=PerceivedValue.NORMAL)
    assert calculate_score(e_none, Decimal("0"), 0) == calculate_score(e_norm, Decimal("0"), 0)
