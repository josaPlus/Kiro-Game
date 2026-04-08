# Implementation Plan: chemical-plant-gameplay

## Overview

Implement `ChemicalPlantScene` — a real-time mini-game replacing `GamePlaceholderScene` for the
chemical factory. Tasks are ordered so each step builds on the previous: constants first, then
`SaveManager`, then private helper classes, then the scene lifecycle, then gameplay mechanics,
then routing, then property-based tests.

## Tasks

- [x] 1. Add Chemical Plant constants to `settings.py`
  - Append all layout, color, mechanic, scoring, and animation constants from the design's
    `settings.py Additions` block to the existing `settings.py`.
  - Include: `HUD_HEIGHT`, all `ZONE_*` rects, `STAGING_AREA_RECT`, all `COLOR_PLANT_*`,
    `COLOR_ZONE_*`, `COLOR_STAGING_*`, `COLOR_HUD_*`, `COLOR_LEAK_*`, `COLOR_WORKER_*`,
    `COLOR_ASSIGN_*`, `COLOR_EXPLOSION_*`, `COLOR_GAME_OVER_*`, `COLOR_GRADE_*`,
    `COLOR_LEVEL_UP_TEXT`, `COLOR_SAFETY_BAR`, `COLOR_PRODUCTION_BAR`, all `LEAK_*`,
    all `WORKER_*`, all `ASSIGN_BTN_*`, all `SCORE_*`, `SAFETY_PENALTY_UNPROTECTED_WORKER`,
    `LEVEL_ADVANCE_DURATION`, `LEVEL_UP_DISPLAY_DURATION`, `PRODUCTION_RATE`,
    `EXPLOSION_FRAME_DURATION`, `EXPLOSION_TOTAL_DURATION`, `EXPLOSION_TEXT_HOLD_DURATION`,
    `HUD_BAR_W`, `HUD_BAR_H`, `HUD_BAR_MARGIN`.
  - No magic numbers may appear in any scene or core file.
  - _Requirements: 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 4.2, 4.3, 4.4, 4.5, 5.1, 5.5, 5.6,
    6.1, 6.2, 6.3, 6.4, 6.6, 7.1, 8.2, 8.3, 8.5, 9.2, 11.1, 11.2_

- [x] 2. Implement `SaveManager` in `core/save_manager.py`
  - Create `core/save_manager.py` with a `SaveManager` class.
  - Implement `save_result(result: dict) -> None`: creates `data/` if absent, loads existing
    list (empty list on missing/corrupt file), appends `result`, writes back with `json.dump`.
  - Implement `load_results() -> list[dict]`: returns saved list or `[]` on any read error.
  - No pygame dependency — pure Python / stdlib only.
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 3. Implement private helper classes in `scenes/chemical_plant.py`
  - Create `scenes/chemical_plant.py` with the four private helper classes only (no scene yet).
  - [x] 3.1 Implement `_LeakSpot`
    - `__init__(pos, duration)` — stores `pos`, `remaining = duration`, `duration`, `hit_radius = LEAK_HIT_RADIUS`.
    - `update(dt) -> bool` — decrements `remaining` by `dt`, clamps to 0, returns `True` when expired.
    - `contains_point(pt) -> bool` — Euclidean distance check against `hit_radius`.
    - `draw(surface)` — draws orange circle (`LEAK_CIRCLE_RADIUS`) and countdown progress bar
      (`LEAK_TIMER_BAR_W × LEAK_TIMER_BAR_H`) using `pygame.draw` only.
    - _Requirements: 4.3, 4.4, 4.5_
  - [x] 3.2 Implement `_Worker`
    - `__init__(queue_index)` — stores `queue_index`, `protected = False`, `selected = False`.
    - `draw(surface, x, y)` — delegates to `core.placeholder_sprites.draw_worker` with
      `factory_id="chemical"`; draws a highlight ring (`COLOR_WORKER_SELECTED`) when `selected`.
    - _Requirements: 5.2, 5.3_
  - [x] 3.3 Implement `_ExplosionAnimation`
    - `__init__(pos)` — stores `pos`, `elapsed = 0.0`, `frame = 0`.
    - `update(dt) -> bool` — increments `elapsed`; sets `frame = min(2, int(elapsed / EXPLOSION_FRAME_DURATION_S))`; returns `True` when `elapsed >= EXPLOSION_TOTAL_DURATION / 1000.0`.
    - `draw(surface)` — draws expanding concentric rings via `pygame.draw.circle` using
      `COLOR_EXPLOSION_INNER` and `COLOR_EXPLOSION_OUTER`; ring radii scale with `frame`.
    - _Requirements: 8.1, 8.2, 8.3, 8.6_
  - [x] 3.4 Implement `_GameOverScreen`
    - `__init__(score, level, time_survived, grade, fonts)` — stores all display data; builds
      "PLAY AGAIN" and "MAIN MENU" button rects.
    - `handle_click(pos) -> str | None` — returns `"play_again"`, `"main_menu"`, or `None`.
    - `draw(surface)` — renders overlay background, score/level/time/grade text, grade color
      (`COLOR_GRADE_A/B/C/F`), and both buttons using `pygame.draw` + `pygame.font.SysFont`.
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 4. Implement `ChemicalPlantScene` lifecycle
  - Add `ChemicalPlantScene(BaseScene)` to `scenes/chemical_plant.py`.
  - `__init__(manager, input_handler, factory_data)` — stores args only; no pygame calls.
  - `on_enter()` — initializes all state fields (`_phase`, `_level`, `_level_timer`, `_score`,
    `_safety`, `_production`, `_leaks`, `_workers`, `_selected_worker`, `_worker_timer`,
    `_time_survived`, `_level_up_timer`, `_explosion`, `_game_over_screen`, `_save_manager`,
    `_fonts`); spawns the first leak.
  - `on_exit()` — sets all state fields to `None`.
  - Stub `handle_event`, `update`, `draw` with `pass` so the scene is importable.
  - _Requirements: 1.2, 1.3, 1.4_

- [x] 5. Implement factory floor and HUD rendering
  - [x] 5.1 Implement `_draw_floor(surface)`
    - Fill background with `COLOR_PLANT_BG`.
    - Draw grid lines using `COLOR_PLANT_GRID`.
    - Draw three zone rectangles (`ZONE_REACTOR`, `ZONE_STORAGE`, `ZONE_MIXING`) with their
      respective fill colors and centered labels via `pygame.font.SysFont`.
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6_
  - [x] 5.2 Implement `_draw_staging(surface)`
    - Draw `STAGING_AREA_RECT` filled with `COLOR_STAGING_BG` and labeled "STAGING AREA".
    - Draw each `_Worker` in `_workers` left-to-right spaced by `WORKER_SPACING`.
    - Draw the "Assign Respirator" button at `(ASSIGN_BTN_X, ASSIGN_BTN_Y)`.
    - _Requirements: 2.5, 5.2, 5.6_
  - [x] 5.3 Implement `_draw_hud(surface)`
    - Draw HUD strip (`HUD_HEIGHT`) filled with `COLOR_HUD_BG`.
    - Draw `SafetyMeter` bar (fill `COLOR_SAFETY_BAR`) and `ProductionMeter` bar
      (fill `COLOR_PRODUCTION_BAR`) using `_meter_bar_width`.
    - Render level label, elapsed time (whole seconds), and score using `pygame.font.SysFont`.
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  - [x] 5.4 Implement `draw(surface)` to wire floor, staging, leaks, workers, HUD, and overlays
    - Call `_draw_floor`, `_draw_staging`, draw each leak, draw each worker, call `_draw_hud`.
    - When `_phase == "EXPLODING"` or `"GAME_OVER"`: draw `_explosion`.
    - When `_phase == "GAME_OVER"`: draw `_game_over_screen`.
    - When `_level_up_timer > 0`: render "LEVEL UP!" centered using `COLOR_LEVEL_UP_TEXT`.
    - When `_phase == "EXPLODING"`: render "EXPLOSION!" centered using `COLOR_EXPLOSION_TEXT`.
    - _Requirements: 2.6, 3.1, 6.6, 8.4_

- [x] 6. Implement gameplay mechanics in `update` and `handle_event`
  - [x] 6.1 Implement `_spawn_leak()` and leak spawning logic
    - Pick a random zone from `[ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING]`.
    - Pick a random `(x, y)` strictly inside the chosen zone rect.
    - Append a new `_LeakSpot(pos, leak_timer_for_level)` to `_leaks`.
    - Guard: skip if `len(self._leaks) >= _LEAK_MAX[self._level - 1]`.
    - _Requirements: 4.1, 4.2_
  - [x] 6.2 Implement leak update and explosion trigger
    - Each frame (PLAYING phase): call `leak.update(dt)` for all leaks; if any returns `True`,
      call `_trigger_explosion(leak.pos)`.
    - `_trigger_explosion(pos)`: create `_ExplosionAnimation(pos)`, set `_phase = "EXPLODING"`,
      freeze `_production` (stop incrementing).
    - _Requirements: 4.4, 4.6, 8.1_
  - [x] 6.3 Implement click handling for leaks and workers in `handle_event`
    - Use `self.input.is_mouse_clicked()` and `self.input.get_mouse_pos()` exclusively.
    - If click hits a leak (`contains_point`): call `_resolve_leak(leak)`.
    - If click hits a worker in staging: set `_selected_worker`.
    - If click hits "Assign Respirator" button and a worker is selected: assign respirator,
      add `SCORE_WORKER_PROTECTED`, remove worker from `_workers`.
    - Handle `pygame.K_ESCAPE` → `self.manager.pop_scene()`.
    - _Requirements: 1.5, 4.5, 4.7, 5.3, 5.4_
  - [x] 6.4 Implement `_resolve_leak(leak)`
    - Remove `leak` from `_leaks`.
    - Add `SCORE_LEAK_RESOLVED` to `_score`.
    - Schedule a replacement spawn after a short delay (or spawn immediately if below cap).
    - _Requirements: 4.5, 11.1_
  - [x] 6.5 Implement worker spawn timer and unprotected-worker penalty
    - Decrement `_worker_timer` by `dt`; when it reaches 0, append a new `_Worker` and reset
      timer to the current level's `WORKER_INTERVAL`.
    - When a worker at the front of the queue exits unprotected: remove from `_workers`,
      apply `max(0.0, _safety - SAFETY_PENALTY_UNPROTECTED_WORKER)`.
    - If `_safety <= 0`: call `_trigger_explosion` (safety-zero explosion at screen centre).
    - _Requirements: 5.1, 5.5, 5.7_
  - [x] 6.6 Implement level progression and production meter in `update`
    - Increment `_level_timer` and `_time_survived` by `dt` each frame (PLAYING phase).
    - Call `_advance_level()` when `_level_timer >= LEVEL_ADVANCE_DURATION` and `_level < 3`.
    - `_advance_level()`: increment `_level`, reset `_level_timer = 0`, set
      `_level_up_timer = LEVEL_UP_DISPLAY_DURATION`.
    - Decrement `_level_up_timer` by `dt` (clamp to 0).
    - Increment `_production` by `PRODUCTION_RATE * dt`, clamp to 100.0 (PLAYING phase only).
    - _Requirements: 6.4, 6.5, 6.6, 6.7, 7.1, 7.2, 7.3_
  - [x] 6.7 Implement EXPLODING → GAME_OVER phase transition
    - In `update` (EXPLODING phase): call `_explosion.update(dt)`; when it returns `True`,
      decrement hold timer; when hold timer <= 0, call `_trigger_game_over()`.
    - `_trigger_game_over()`: call `_save_manager.save_result(...)` with all required fields,
      create `_GameOverScreen`, set `_phase = "GAME_OVER"`.
    - In `update` (GAME_OVER phase): call `_game_over_screen.handle_click` when mouse clicked;
      on `"play_again"` call `replace_scene(ChemicalPlantScene(...))`;
      on `"main_menu"` call `pop_scene()`.
    - _Requirements: 8.5, 9.1, 9.3, 9.4, 9.6, 10.5, 10.6_

- [x] 7. Checkpoint — smoke test scene lifecycle
  - Ensure all tests pass, ask the user if questions arise.
  - Verify `on_enter` → several `update(dt)` calls → `on_exit` does not raise with a mocked
    pygame surface and `InputHandler`.

- [x] 8. Route `"chemical"` factory to `ChemicalPlantScene` in `factory_select.py`
  - In `FactorySelectScene.update`, replace the unconditional `GamePlaceholderScene` push with
    the conditional block from the design:
    - `if card.factory_id == "chemical"`: import and push `ChemicalPlantScene` with `factory_data`.
    - `else`: import and push `GamePlaceholderScene` as before.
  - Import `ChemicalPlantScene` locally inside the `if` branch to avoid circular imports.
  - _Requirements: 1.1_

- [x] 9. Write property-based tests in `tests/test_chemical_plant_properties.py`
  - Create the test file using `pytest` + `hypothesis`. All 13 properties are required.
  - [x] 9.1 Property 1 — LeakSpot spawn position is always inside a FactoryZone
    - Strategy: `st.sampled_from([ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING])` for zone selection.
    - Assert `pygame.Rect(*zone).collidepoint(pos)` for the spawned position.
    - **Property 1: LeakSpot spawn position is always inside a FactoryZone**
    - **Validates: Requirements 4.1**
  - [x] 9.2 Property 2 — Active leak count never exceeds the level cap
    - Strategy: `st.lists(st.integers(1, 3))` for level sequence, simulate spawn/resolve events.
    - Assert `len(active_leaks) <= _LEAK_MAX[level - 1]` after every step.
    - **Property 2: Active leak count never exceeds the level cap**
    - **Validates: Requirements 4.2**
  - [x] 9.3 Property 3 — LeakSpot timer decrements by exactly dt
    - Strategy: `st.floats(min_value=0.001, max_value=20.0)` for initial `remaining` and `dt`.
    - Assert `new_remaining == max(0.0, t - dt)` after `leak.update(dt)`.
    - **Property 3: LeakSpot timer decrements by exactly dt**
    - **Validates: Requirements 4.4**
  - [x] 9.4 Property 4 — Resolving a leak adds exactly SCORE_LEAK_RESOLVED to the score
    - Strategy: `st.integers(min_value=0)` for initial score; construct a `_LeakSpot` at a
      known position and call `_resolve_leak`.
    - Assert score delta equals `SCORE_LEAK_RESOLVED` and leak is absent from `_leaks`.
    - **Property 4: Resolving a leak adds exactly SCORE_LEAK_RESOLVED to the score**
    - **Validates: Requirements 4.5, 11.1**
  - [x] 9.5 Property 5 — Worker spawns after accumulating WORKER_INTERVAL seconds
    - Strategy: `st.lists(st.floats(min_value=0.001, max_value=2.0))` for dt sequence.
    - Simulate worker timer; assert exactly one worker appended when cumulative dt >= interval.
    - **Property 5: Worker spawns after accumulating WORKER_INTERVAL seconds**
    - **Validates: Requirements 5.1**
  - [x] 9.6 Property 6 — Assigning a respirator removes the worker and adds SCORE_WORKER_PROTECTED
    - Strategy: `st.integers(min_value=0)` for initial score.
    - Assert score delta equals `SCORE_WORKER_PROTECTED` and worker absent from `_workers`.
    - **Property 6: Assigning a respirator removes the worker and adds SCORE_WORKER_PROTECTED**
    - **Validates: Requirements 5.4, 11.2**
  - [x] 9.7 Property 7 — Unprotected worker exit reduces SafetyMeter by SAFETY_PENALTY_UNPROTECTED_WORKER
    - Strategy: `st.floats(min_value=0.0, max_value=100.0)` for initial safety value.
    - Assert `new_safety == max(0.0, s - SAFETY_PENALTY_UNPROTECTED_WORKER)`.
    - **Property 7: Unprotected worker exit reduces SafetyMeter by SAFETY_PENALTY_UNPROTECTED_WORKER**
    - **Validates: Requirements 5.5**
  - [x] 9.8 Property 8 — Level advances after LEVEL_ADVANCE_DURATION, capped at 3
    - Strategy: `st.integers(min_value=1, max_value=3)` for level; `st.floats` for timer.
    - Assert level becomes `min(3, l + 1)` and timer resets when `level_timer >= LEVEL_ADVANCE_DURATION`.
    - Assert level stays 3 when already at 3.
    - **Property 8: Level advances after LEVEL_ADVANCE_DURATION, capped at 3**
    - **Validates: Requirements 6.4, 6.5**
  - [x] 9.9 Property 9 — ProductionMeter update follows the clamped rate formula
    - Strategy: `st.floats(min_value=0.0, max_value=100.0)` for `p`; `st.floats(min_value=0.001, max_value=5.0)` for `dt`.
    - Assert `new_production == min(100.0, p + PRODUCTION_RATE * dt)`.
    - **Property 9: ProductionMeter update follows the clamped rate formula**
    - **Validates: Requirements 7.1, 7.2**
  - [x] 9.10 Property 10 — ExplosionAnimation selects the correct frame for any elapsed time
    - Strategy: `st.floats(min_value=0.0, max_value=EXPLOSION_TOTAL_DURATION / 1000.0)`.
    - Assert `frame == min(2, int(e / (EXPLOSION_FRAME_DURATION / 1000.0)))` and `frame in {0, 1, 2}`.
    - **Property 10: ExplosionAnimation selects the correct frame for any elapsed time**
    - **Validates: Requirements 8.2**
  - [x] 9.11 Property 11 — Grade calculation is correct for any SafetyMeter value
    - Strategy: `st.floats(min_value=0.0, max_value=100.0)` for safety percentage.
    - Assert grade boundaries: A ≥ 90, B ≥ 70, C ≥ 50, F < 50.
    - **Property 11: Grade calculation is correct for any SafetyMeter value**
    - **Validates: Requirements 9.2**
  - [x] 9.12 Property 12 — SaveManager round-trip preserves all required result fields
    - Strategy: `st.fixed_dictionaries` with valid values for all five required keys; use
      `tmp_path` (pytest fixture) to isolate filesystem writes.
    - Assert `load_results()[-1] == result` and all five keys present.
    - **Property 12: SaveManager round-trip preserves all required result fields**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.6**
  - [x] 9.13 Property 13 — HUD meter bar width is proportional to meter percentage
    - Strategy: `st.floats(min_value=0.0, max_value=100.0)` for `pct`; `st.integers(min_value=1, max_value=500)` for `max_w`.
    - Assert `_meter_bar_width(pct, max_w) == int(pct / 100.0 * max_w)` and result in `[0, max_w]`.
    - **Property 13: HUD meter bar width is proportional to meter percentage**
    - **Validates: Requirements 3.7**

- [x] 10. Final checkpoint — Ensure all tests pass
  - Run `pytest tests/test_chemical_plant_properties.py --tb=short`.
  - Ensure all 13 property tests pass with no errors.
  - Ensure all tests pass, ask the user if questions arise.
