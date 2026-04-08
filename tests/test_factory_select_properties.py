"""tests/test_factory_select_properties.py
Property-based tests for the factory selection screen.
Requires: pip install pytest hypothesis pygame
"""
import pygame
import pytest
from hypothesis import given, settings as h_settings
from hypothesis import strategies as st

from scenes.factory_select import FACTORIES, _DIFF_COLORS
from settings import (
    CARD_W, CARD_H, CARD_GAP,
    COLOR_DIFFICULTY_EASY, COLOR_DIFFICULTY_MEDIUM, COLOR_DIFFICULTY_HARD,
    SELECT_BTN_W, SELECT_BTN_H, SELECT_BTN_MARGIN,
    FONT_SIZE_BUTTON, FONT_SIZE_BODY, FONT_SIZE_SMALL,
)

REQUIRED_KEYS = {"id", "name", "abbrev", "color", "difficulty", "description", "hazards"}


@pytest.fixture(scope="session", autouse=True)
def pygame_session():
    pygame.init()
    # Need a display surface for font rendering in _build_surface
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    yield
    pygame.quit()


# ── Property 1: FACTORIES data schema invariant ────────────────────────────────
@given(entry=st.sampled_from(FACTORIES))
@h_settings(max_examples=100)
def test_factory_schema(entry):
    """For any entry in FACTORIES, the key set, hazards, and color must be valid."""
    assert set(entry.keys()) == REQUIRED_KEYS
    assert isinstance(entry["hazards"], list)
    assert len(entry["hazards"]) > 0
    assert all(isinstance(h, str) for h in entry["hazards"])
    r, g, b = entry["color"]
    assert all(0 <= c <= 255 for c in (r, g, b))


# ── Property 2: Card layout centring and equal spacing ────────────────────────
@given(screen_w=st.integers(min_value=800, max_value=2560))
@h_settings(max_examples=100)
def test_card_layout_centred(screen_w):
    """For any screen width, cards must be centred and equally spaced."""
    total_w = len(FACTORIES) * CARD_W + (len(FACTORIES) - 1) * CARD_GAP
    start_x = (screen_w - total_w) // 2
    rects = [
        pygame.Rect(start_x + i * (CARD_W + CARD_GAP), 0, CARD_W, CARD_H)
        for i in range(len(FACTORIES))
    ]
    left_margin = rects[0].left
    right_margin = screen_w - rects[-1].right
    assert abs(left_margin - right_margin) <= 1
    for i in range(len(rects) - 1):
        assert rects[i + 1].left - rects[i].right == CARD_GAP


# ── Property 3: Difficulty badge color mapping ────────────────────────────────
@given(entry=st.sampled_from(FACTORIES))
@h_settings(max_examples=100)
def test_badge_color_mapping(entry):
    """For any factory entry, the badge color must match the difficulty constant."""
    expected = {
        "EASY":   COLOR_DIFFICULTY_EASY,
        "MEDIUM": COLOR_DIFFICULTY_MEDIUM,
        "HARD":   COLOR_DIFFICULTY_HARD,
    }[entry["difficulty"]]
    assert _DIFF_COLORS[entry["difficulty"]] == expected


# ── Property 4: Hover state correctness ──────────────────────────────────────
@pytest.fixture
def first_card(pygame_session):
    """Build a _FactoryCard for the first factory entry."""
    from scenes.factory_select import _FactoryCard
    font_btn   = pygame.font.SysFont(None, FONT_SIZE_BUTTON, bold=True)
    font_body  = pygame.font.SysFont(None, FONT_SIZE_BODY)
    font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
    card = _FactoryCard(
        FACTORIES[0], x=100, y=100, w=CARD_W, h=CARD_H,
        font_btn=font_btn, font_body=font_body, font_small=font_small,
    )
    return card


@given(
    mx=st.integers(min_value=0, max_value=1280),
    my=st.integers(min_value=0, max_value=720),
)
@h_settings(max_examples=100)
def test_hover_state(mx, my):
    """For any mouse position, _hovered must equal btn_rect.collidepoint."""
    from scenes.factory_select import _FactoryCard
    font_btn   = pygame.font.SysFont(None, FONT_SIZE_BUTTON, bold=True)
    font_body  = pygame.font.SysFont(None, FONT_SIZE_BODY)
    font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
    card = _FactoryCard(
        FACTORIES[0], x=100, y=100, w=CARD_W, h=CARD_H,
        font_btn=font_btn, font_body=font_body, font_small=font_small,
    )
    card.update((mx, my))
    assert card._hovered == card._btn_rect.collidepoint((mx, my))
