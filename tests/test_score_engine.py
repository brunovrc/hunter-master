import pytest
from analysis.red_flags import FlagLevel, check_red_flags, has_critical_flag
from analysis.score_engine import (
    Recommendation,
    calculate_gross_margin,
    run_score_engine,
    score_f1_margin,
    score_f6_seller,
    score_f7_future_demand,
)

CLEAN_LISTING = {
    "id": "test_001",
    "title": "Camisa Zico Flamengo 1982 Autografada COA PSA",
    "description": "Camisa original do Zico com certificado PSA/DNA. Estado perfeito.",
    "price": 500.0,
    "url": "https://example.com/test_001",
    "images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
    "seller": {"id": "s1", "name": "Colecionador", "total_ratings": 60, "positive_pct": 98},
}

FAKE_LISTING = {
    "id": "test_002",
    "title": "Camisa Réplica Flamengo Tailandesa Alta Qualidade",
    "description": "Camisa tailandesa importada",
    "price": 80.0,
    "url": "https://example.com/test_002",
    "images": [],
    "seller": {"id": "s2", "name": "Loja", "total_ratings": 0, "positive_pct": 100},
}

PLAYER_LEGEND = {
    "raridade": "legend",
    "eventos_futuros": [],
    "copa_2026": False,
    "controversias_ativas": [],
}

PLAYER_ICON = {
    "raridade": "icon",
    "eventos_futuros": [],
    "copa_2026": False,
    "controversias_ativas": [],
}

CLAUDE_HIGH = {"authenticity_score": 85, "likely_fake": False, "autopen_suspected": False}
CLAUDE_LOW = {"authenticity_score": 20, "likely_fake": True, "autopen_suspected": False}


# Red flags
def test_explicit_fake_detected():
    flags = check_red_flags(FAKE_LISTING)
    assert has_critical_flag(flags)


def test_clean_listing_no_critical_flags():
    flags = check_red_flags(CLEAN_LISTING)
    assert not has_critical_flag(flags)


def test_no_images_flag():
    listing = {**CLEAN_LISTING, "images": []}
    flags = check_red_flags(listing)
    assert any(f.code == "NO_IMAGES" for f in flags)


def test_new_seller_high_value():
    listing = {
        **CLEAN_LISTING,
        "seller": {"id": "s", "name": "novo", "total_ratings": 0, "positive_pct": 100},
        "price": 600.0,
    }
    flags = check_red_flags(listing)
    assert any(f.code == "NEW_SELLER_HIGH_VALUE" for f in flags)


# Score filters
def test_f1_margin_verde():
    r = score_f1_margin(0.50)
    assert r.score == 30
    assert r.status == "VERDE"


def test_f1_margin_amarelo():
    r = score_f1_margin(0.30)
    assert r.score == 15
    assert r.status == "AMARELO"


def test_f1_margin_vermelho():
    r = score_f1_margin(0.10)
    assert r.score == 0
    assert r.status == "VERMELHO"


def test_f6_seller_good():
    r = score_f6_seller(CLEAN_LISTING)
    assert r.score == 10


def test_f6_seller_new():
    listing = {**CLEAN_LISTING, "seller": {"total_ratings": 0, "positive_pct": 100}}
    r = score_f6_seller(listing)
    assert r.score == 0


def test_gross_margin():
    assert calculate_gross_margin(500, 1000) == pytest.approx(0.50)


def test_gross_margin_zero_price():
    assert calculate_gross_margin(500, 0) == 0.0


# Full pipeline
def test_buy_recommendation():
    report = run_score_engine(CLEAN_LISTING, 1000.0, PLAYER_LEGEND, CLAUDE_HIGH)
    assert report.recommendation == Recommendation.BUY_NOW
    assert report.gross_margin == pytest.approx(0.50)
    assert report.total_score >= 60


def test_refuse_on_fake():
    report = run_score_engine(FAKE_LISTING, 200.0, PLAYER_LEGEND, CLAUDE_LOW)
    assert report.recommendation == Recommendation.REFUSE


def test_negotiate_recommendation():
    # margin = (900 - 630) / 900 = 30% — acima de 20%, abaixo de 40% → NEGOCIAR
    listing = {**CLEAN_LISTING, "price": 630.0}
    report = run_score_engine(listing, 900.0, PLAYER_LEGEND, CLAUDE_HIGH)
    assert report.recommendation in (Recommendation.NEGOTIATE, Recommendation.BUY_NOW)


def test_score_never_negative():
    listing = {**CLEAN_LISTING, "images": []}
    report = run_score_engine(listing, 600.0, PLAYER_LEGEND, CLAUDE_HIGH)
    assert report.total_score >= 0
