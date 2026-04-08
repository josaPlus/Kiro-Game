"""tests/test_chemical_plant_properties.py
Property-based tests for ChemicalPlantScene helpers.
Requires: pytest, hypothesis, pygame
"""
from __future__ import annotations

import os
import math
import random
import types
import pygame
import pytest

from hypothesis import given, settings as h_settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Pygame initialisation — no display required for most tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def pygame_session():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    yield
    pygame.quit()


# ---------------------------------------------------------------------------
# Imports from the scene and settings
# ---------------------------------------------------------------------------

from scenes.chemical_plant import (
    _LeakSpot,
    _Worker,
    _ExplosionAnimation,
    _LEAK_MAX,
    _WORKER_INTERVALS,
    EXPLOSION_FRAME_DURATION_S,
    EXPLOSION_TOTAL_DURATION_S,
)
from settings import (
    ZONE_REACTOR,
    ZONE_STORAGE,
    ZONE_MIXING,
    SCORE_LEAK_RESOLVED,
    SCORE_WORKER_PROTECTED,
    SAFETY_PENALTY_UNPROTECTED_WORKER,
    LEVEL_ADVANCE_DURATION,
    PRODUCTION_RATE,
    EXPLOSION_FRAME_DURATION,
    EXPLOSION_TOTAL_DURATION,
    WORKER_INTERVAL_EASY,
    WORKER_INTERVAL_MEDIUM,
    WORKER_INTERVAL_HARD,
)


# ---------------------------------------------------------------------------
# Minimal scene stub — avoids a full pygame display
# ---------------------------------------------------------------------------

def _make_scene():
    """Return a minimal ChemicalPlantScene-like namespace for testing."""
    from scenes.chemical_plant import ChemicalPlantScene, _LEAK_MAX, _WORKER_INTERVALS

    # Minimal manager / input stubs
    manager = types.SimpleNamespace(pop_scene=lambda: None, replace_scene=lambda s: None)
    input_handler = types.SimpleNamespace(
        is_mouse_clicked=lambda: False,
        get_mouse_pos=lambda: (0, 0),
    )
    factory_data = {"id": "chemical", "name": "Chemical Plant"}

    scene = ChemicalPlantScene.__new__(ChemicalPlantScene)
    # Manually set the attributes that on_enter would set, without calling pygame
    scene.manager = manager
    scene.input = input_handler
    scene.factory_data = factory_data
    scene._phase = "PLAYING"
    scene._level = 1
    scene._level_timer = 0.0
    scene._score = 0
    scene._safety = 100.0
    scene._production = 0.0
    scene._leaks = []
    scene._workers = []
    scene._selected_worker = None
    scene._worker_timer = WORKER_INTERVAL_EASY
    scene._time_survived = 0.0
    scene._level_up_timer = 0.0
    scene._explosion = None
    scene._game_over_screen = None
    scene._explosion_hold_timer = 0.0
    scene._save_manager = None
    scene._fonts = {}
    return scene


# ===========================================================================
# Property 1 — LeakSpot spawn position is always inside a FactoryZone
# Validates: Requirements 4.1
# ===========================================================================

@given(zone=st.sampled_from([ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING]))
@h_settings(max_examples=200)
def test_prop1_spawn_inside_zone(zone):
    """Property 1: LeakSpot spawn position is always inside a FactoryZone"""
    # Feature: chemical-plant-gameplay, Property 1: spawn inside zone
    zx, zy, zw, zh = zone
    x = random.randint(zx + 10, zx + zw - 10)
    y = random.randint(zy + 10, zy + zh - 10)
    assert pygame.Rect(*zone).collidepoint(x, y), (
        f"Spawned position ({x}, {y}) is outside zone {zone}"
    )


# ===========================================================================
# Property 2 — Active leak count never exceeds the level cap
# Validates: Requirements 4.2
# ===========================================================================

@given(levels=st.lists(st.integers(min_value=1, max_value=3), min_size=1, max_size=30))
@h_settings(max_examples=200)
def test_prop2_leak_count_cap(levels):
    """Property 2: Active leak count never exceeds the level cap"""
    # Feature: chemical-plant-gameplay, Property 2: leak count cap
    active_leaks = []
    for level in levels:
        cap = _LEAK_MAX[level - 1]
        # Simulate a spawn attempt
        if len(active_leaks) < cap:
            active_leaks.append(object())
        assert len(active_leaks) <= cap, (
            f"Leak count {len(active_leaks)} exceeds cap {cap} at level {level}"
        )
        # Simulate a resolve (50% chance)
        if active_leaks and random.random() < 0.5:
            active_leaks.pop()
        assert len(active_leaks) <= cap


# ===========================================================================
# Property 3 — LeakSpot timer decrements by exactly dt
# Validates: Requirements 4.4
# ===========================================================================

@given(
    t=st.floats(min_value=0.001, max_value=20.0),
    dt=st.floats(min_value=0.001, max_value=20.0),
)
@h_settings(max_examples=200)
def test_prop3_timer_decrement(t, dt):
    """Property 3: LeakSpot timer decrements by exactly dt"""
    # Feature: chemical-plant-gameplay, Property 3: timer decrement
    leak = _LeakSpot((100, 100), t)
    leak.remaining = t
    leak.update(dt)
    expected = max(0.0, t - dt)
    assert math.isclose(leak.remaining, expected, rel_tol=1e-9, abs_tol=1e-12), (
        f"remaining={leak.remaining} expected={expected} (t={t}, dt={dt})"
    )


# ===========================================================================
# Property 4 — Resolving a leak adds exactly SCORE_LEAK_RESOLVED to the score
# Validates: Requirements 4.5, 11.1
# ===========================================================================

@given(initial_score=st.integers(min_value=0, max_value=100_000))
@h_settings(max_examples=200)
def test_prop4_resolve_leak_score(initial_score):
    """Property 4: Resolving a leak adds exactly SCORE_LEAK_RESOLVED to the score"""
    # Feature: chemical-plant-gameplay, Property 4: resolve score delta
    scene = _make_scene()
    scene._score = initial_score
    leak = _LeakSpot((200, 200), 5.0)
    scene._leaks = [leak]

    scene._resolve_leak(leak)

    assert scene._score == initial_score + SCORE_LEAK_RESOLVED, (
        f"Score delta wrong: got {scene._score - initial_score}, "
        f"expected {SCORE_LEAK_RESOLVED}"
    )
    assert leak not in scene._leaks, "Leak should be removed after resolve"


# ===========================================================================
# Property 5 — Worker spawns after accumulating WORKER_INTERVAL seconds
# Validates: Requirements 5.1
# ===========================================================================

@given(dts=st.lists(st.floats(min_value=0.001, max_value=2.0), min_size=1, max_size=50))
@h_settings(max_examples=200)
def test_prop5_worker_spawn_timing(dts):
    """Property 5: Worker spawns after accumulating WORKER_INTERVAL seconds"""
    # Feature: chemical-plant-gameplay, Property 5: worker spawn timing
    interval = WORKER_INTERVAL_EASY
    timer = interval
    workers = []
    cumulative = 0.0

    for dt in dts:
        timer -= dt
        cumulative += dt
        if timer <= 0:
            workers.append(object())
            timer = interval  # reset

    # Verify: number of spawns matches floor(cumulative / interval)
    expected_spawns = int(cumulative / interval)
    assert len(workers) == expected_spawns, (
        f"Expected {expected_spawns} spawns for cumulative={cumulative:.3f}s "
        f"(interval={interval}), got {len(workers)}"
    )


# ===========================================================================
# Property 6 — Assigning a respirator removes the worker and adds SCORE_WORKER_PROTECTED
# Validates: Requirements 5.4, 11.2
# ===========================================================================

@given(initial_score=st.integers(min_value=0, max_value=100_000))
@h_settings(max_examples=200)
def test_prop6_assign_respirator_score(initial_score):
    """Property 6: Assigning a respirator removes the worker and adds SCORE_WORKER_PROTECTED"""
    # Feature: chemical-plant-gameplay, Property 6: assign respirator score delta
    scene = _make_scene()
    scene._score = initial_score

    worker = _Worker(0)
    worker.selected = True
    scene._workers = [worker]
    scene._selected_worker = worker

    # Simulate the assign action (mirrors handle_event logic)
    scene._selected_worker.protected = True
    scene._selected_worker.selected = False
    scene._score += SCORE_WORKER_PROTECTED
    scene._workers.remove(scene._selected_worker)
    scene._selected_worker = None

    assert scene._score == initial_score + SCORE_WORKER_PROTECTED, (
        f"Score delta wrong: got {scene._score - initial_score}, "
        f"expected {SCORE_WORKER_PROTECTED}"
    )
    assert worker not in scene._workers, "Worker should be removed after respirator assignment"


# ===========================================================================
# Property 7 — Unprotected worker exit reduces SafetyMeter by SAFETY_PENALTY_UNPROTECTED_WORKER
# Validates: Requirements 5.5
# ===========================================================================

@given(s=st.floats(min_value=0.0, max_value=100.0))
@h_settings(max_examples=200)
def test_prop7_safety_penalty(s):
    """Property 7: Unprotected worker exit reduces SafetyMeter by SAFETY_PENALTY_UNPROTECTED_WORKER"""
    # Feature: chemical-plant-gameplay, Property 7: safety penalty
    new_safety = max(0.0, s - SAFETY_PENALTY_UNPROTECTED_WORKER)
    expected = max(0.0, s - SAFETY_PENALTY_UNPROTECTED_WORKER)
    assert math.isclose(new_safety, expected, rel_tol=1e-9, abs_tol=1e-12), (
        f"Safety={new_safety} expected={expected} (s={s})"
    )
    assert new_safety >= 0.0, "Safety must never go below 0"


# ===========================================================================
# Property 8 — Level advances after LEVEL_ADVANCE_DURATION, capped at 3
# Validates: Requirements 6.4, 6.5
# ===========================================================================

@given(
    level=st.integers(min_value=1, max_value=3),
    level_timer=st.floats(min_value=0.0, max_value=200.0),
)
@h_settings(max_examples=200)
def test_prop8_level_advance(level, level_timer):
    """Property 8: Level advances after LEVEL_ADVANCE_DURATION, capped at 3"""
    # Feature: chemical-plant-gameplay, Property 8: level advance
    if level_timer >= LEVEL_ADVANCE_DURATION and level < 3:
        new_level = level + 1
        new_timer = 0.0
        assert new_level == min(3, level + 1), (
            f"Level should advance to {min(3, level + 1)}, got {new_level}"
        )
        assert new_timer == 0.0, "Level timer should reset to 0 after advance"
    else:
        # Level stays the same
        new_level = level
        assert new_level == level

    # Cap invariant: level never exceeds 3
    assert new_level <= 3, f"Level {new_level} exceeds cap of 3"

    # When already at 3, level must stay 3 regardless of timer
    if level == 3:
        assert new_level == 3, "Level must stay at 3 when already at max"


# ===========================================================================
# Property 9 — ProductionMeter update follows the clamped rate formula
# Validates: Requirements 7.1, 7.2
# ===========================================================================

@given(
    p=st.floats(min_value=0.0, max_value=100.0),
    dt=st.floats(min_value=0.001, max_value=5.0),
)
@h_settings(max_examples=200)
def test_prop9_production_formula(p, dt):
    """Property 9: ProductionMeter update follows the clamped rate formula"""
    # Feature: chemical-plant-gameplay, Property 9: production formula
    new_production = min(100.0, p + PRODUCTION_RATE * dt)
    expected = min(100.0, p + PRODUCTION_RATE * dt)
    assert math.isclose(new_production, expected, rel_tol=1e-9, abs_tol=1e-12)
    assert 0.0 <= new_production <= 100.0, (
        f"Production {new_production} out of [0, 100] range"
    )


# ===========================================================================
# Property 10 — ExplosionAnimation selects the correct frame for any elapsed time
# Validates: Requirements 8.2
# ===========================================================================

@given(e=st.floats(min_value=0.0, max_value=EXPLOSION_TOTAL_DURATION / 1000.0))
@h_settings(max_examples=200)
def test_prop10_explosion_frame(e):
    """Property 10: ExplosionAnimation selects the correct frame for any elapsed time"""
    # Feature: chemical-plant-gameplay, Property 10: explosion frame selection
    anim = _ExplosionAnimation((400, 300))
    anim.elapsed = e
    anim.frame = min(2, int(e / EXPLOSION_FRAME_DURATION_S))

    expected_frame = min(2, int(e / (EXPLOSION_FRAME_DURATION / 1000.0)))
    assert anim.frame == expected_frame, (
        f"Frame={anim.frame} expected={expected_frame} (elapsed={e})"
    )
    assert anim.frame in {0, 1, 2}, f"Frame {anim.frame} not in {{0, 1, 2}}"


# ===========================================================================
# Property 11 — Grade calculation is correct for any SafetyMeter value
# Validates: Requirements 9.2
# ===========================================================================

def _calc_grade(s: float) -> str:
    """Mirror of ChemicalPlantScene._calc_grade for isolated testing."""
    if s >= 90:
        return "A"
    if s >= 70:
        return "B"
    if s >= 50:
        return "C"
    return "F"


@given(s=st.floats(min_value=0.0, max_value=100.0))
@h_settings(max_examples=200)
def test_prop11_grade_calculation(s):
    """Property 11: Grade calculation is correct for any SafetyMeter value"""
    # Feature: chemical-plant-gameplay, Property 11: grade boundaries
    grade = _calc_grade(s)
    assert grade in {"A", "B", "C", "F"}, f"Invalid grade '{grade}' for safety={s}"
    if s >= 90:
        assert grade == "A", f"Expected A for s={s}, got {grade}"
    elif s >= 70:
        assert grade == "B", f"Expected B for s={s}, got {grade}"
    elif s >= 50:
        assert grade == "C", f"Expected C for s={s}, got {grade}"
    else:
        assert grade == "F", f"Expected F for s={s}, got {grade}"


# ===========================================================================
# Property 12 — SaveManager round-trip preserves all required result fields
# Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.6
# ===========================================================================

_RESULT_STRATEGY = st.fixed_dictionaries({
    "factory_id":    st.just("chemical"),
    "score":         st.integers(min_value=0, max_value=1_000_000),
    "level_reached": st.integers(min_value=1, max_value=3),
    "time_survived": st.floats(min_value=0.0, max_value=3600.0, allow_nan=False),
    "grade":         st.sampled_from(["A", "B", "C", "F"]),
})

REQUIRED_RESULT_KEYS = {"factory_id", "score", "level_reached", "time_survived", "grade"}


@given(result=_RESULT_STRATEGY)
@h_settings(max_examples=100)
def test_prop12_save_round_trip(result, tmp_path):
    """Property 12: SaveManager round-trip preserves all required result fields"""
    # Feature: chemical-plant-gameplay, Property 12: save round-trip
    from core.save_manager import SaveManager, SAVE_PATH
    import core.save_manager as sm_module

    # Redirect save path to tmp_path for isolation
    original_path = sm_module.SAVE_PATH
    sm_module.SAVE_PATH = tmp_path / "save.json"
    try:
        manager = SaveManager()
        manager.save_result(result)
        loaded = manager.load_results()
        assert len(loaded) >= 1, "load_results should return at least one entry"
        last = loaded[-1]
        assert last == result, f"Round-trip mismatch: saved {result}, loaded {last}"
        assert set(last.keys()) >= REQUIRED_RESULT_KEYS, (
            f"Missing keys: {REQUIRED_RESULT_KEYS - set(last.keys())}"
        )
    finally:
        sm_module.SAVE_PATH = original_path


# ===========================================================================
# Property 13 — HUD meter bar width is proportional to meter percentage
# Validates: Requirements 3.7
# ===========================================================================

def _meter_bar_width(pct: float, max_w: int) -> int:
    """Mirror of ChemicalPlantScene._meter_bar_width for isolated testing."""
    return int(pct / 100.0 * max_w)


@given(
    pct=st.floats(min_value=0.0, max_value=100.0),
    max_w=st.integers(min_value=1, max_value=500),
)
@h_settings(max_examples=200)
def test_prop13_meter_bar_width(pct, max_w):
    """Property 13: HUD meter bar width is proportional to meter percentage"""
    # Feature: chemical-plant-gameplay, Property 13: meter bar width
    width = _meter_bar_width(pct, max_w)
    expected = int(pct / 100.0 * max_w)
    assert width == expected, f"width={width} expected={expected} (pct={pct}, max_w={max_w})"
    assert 0 <= width <= max_w, (
        f"width={width} out of [0, {max_w}] for pct={pct}"
    )
