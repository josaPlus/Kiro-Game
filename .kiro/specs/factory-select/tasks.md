# Implementation Plan: Factory Selection Screen

## Overview

Replace the placeholder `scenes/factory_select.py` with a fully data-driven, lifecycle-correct scene. Work proceeds in layers: constants → data → card helper → scene lifecycle → input/transitions → property-based tests.

## Tasks

- [x] 1. Add `settings.py` constants for factory select
  - Append the card layout block (`CARD_W`, `CARD_H`, `CARD_GAP`, `CARD_TOP_OFFSET`, `WORKER_SCALE`) and the SelectButton block (`SELECT_BTN_W`, `SELECT_BTN_H`, `SELECT_BTN_MARGIN`) to `settings.py`
  - Append the three difficulty badge color constants (`COLOR_DIFFICULTY_EASY`, `COLOR_DIFFICULTY_MEDIUM`, `COLOR_DIFFICULTY_HARD`) to `settings.py`
  - Verify no magic numbers remain in the existing `factory_select.py` card layout section after this step
  - _Requirements: 7.1, 7.3_

- [x] 2. Define `FACTORIES` data and `_DIFF_COLORS` mapping
  - [x] 2.1 Replace the existing `_FACTORIES` list in `scenes/factory_select.py` with the spec-compliant `FACTORIES` list (public name, all seven required keys: `id`, `name`, `abbrev`, `color`, `difficulty`, `description`, `hazards`)
    - Chemical Plant: `difficulty="HARD"`, `id="chemical"`, three hazard strings
    - Auto Assembly: `difficulty="MEDIUM"`, `id="automotive"`, three hazard strings
    - Warehouse: `difficulty="EASY"`, `id="warehouse"`, three hazard strings
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  - [x] 2.2 Add `_DIFF_COLORS` dict in `scenes/factory_select.py` mapping `"EASY"` / `"MEDIUM"` / `"HARD"` to the three new `settings.py` constants
    - Import `COLOR_DIFFICULTY_EASY`, `COLOR_DIFFICULTY_MEDIUM`, `COLOR_DIFFICULTY_HARD` from `settings`
    - Remove the inline `diff_color` key from each factory dict (color now comes from `_DIFF_COLORS`)
    - _Requirements: 3.4, 7.3_

- [x] 3. Rewrite `_FactoryCard` to match the design spec
  - [x] 3.1 Update `_FactoryCard.__init__` to import and use all layout constants from `settings.py` (`CARD_W`, `CARD_H`, `SELECT_BTN_W`, `SELECT_BTN_H`, `SELECT_BTN_MARGIN`) — remove all inline numeric literals
    - `_btn_rect` bottom edge must be `SELECT_BTN_MARGIN` pixels above the card bottom
    - _Requirements: 2.5, 7.2_
  - [x] 3.2 Rewrite `_FactoryCard._build_surface` to render the full static card content
    - Worker sprite via `draw_worker(surf, cx, worker_cy, fac["id"], scale=WORKER_SCALE)`
    - Factory name (bold, `COLOR_TEXT`)
    - Difficulty badge coloured via `_DIFF_COLORS[fac["difficulty"]]`
    - Description text (`COLOR_MUTED`)
    - Hazard list items (each prefixed with `•`, `COLOR_MUTED`, `FONT_SIZE_SMALL`)
    - All font sizes from `settings.py`; no inline integers for sizes or colors
    - _Requirements: 3.2, 3.3, 3.4, 3.7, 7.2_
  - [x] 3.3 Implement `_FactoryCard.update`, `is_select_clicked`, and `draw`
    - `update(mouse_pos)`: set `self._hovered = self._btn_rect.collidepoint(mouse_pos)`
    - `is_select_clicked(mouse_pos, clicked)`: return `clicked and self._btn_rect.collidepoint(mouse_pos)`
    - `draw(surface)`: blit `self._surface`, draw card border (`COLOR_ACCENT` when hovered, `COLOR_BTN_BORDER` otherwise), draw SELECT button (fill `COLOR_BTN_HOVER` + dark text when hovered, `COLOR_BTN_BORDER` fill + `COLOR_TEXT` otherwise)
    - _Requirements: 3.5, 4.1, 4.2, 4.3_

- [x] 4. Rewrite `FactorySelectScene` lifecycle methods
  - [x] 4.1 Implement `on_enter`: allocate fonts via `pygame.font.SysFont`, compute card positions using `SCREEN_WIDTH`, `CARD_W`, `CARD_GAP`, `CARD_TOP_OFFSET`, build one `_FactoryCard` per `FACTORIES` entry, pre-render title surface
    - Card horizontal centring formula: `start_x = (SCREEN_WIDTH - total_w) // 2`
    - Card vertical position: `(SCREEN_HEIGHT - CARD_H) // 2 + CARD_TOP_OFFSET`
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 3.1, 3.6_
  - [x] 4.2 Implement `on_exit`: nullify `self._cards`, `self._title_surf`, and all font references
    - _Requirements: 2.2_

- [x] 5. Implement input handling and scene transitions in `FactorySelectScene.update`
  - [x] 5.1 Wire hover updates: call `card.update(mouse_pos)` for each card each frame using `self.input.get_mouse_pos()`
    - _Requirements: 4.4_
  - [x] 5.2 Wire factory selection: when `card.is_select_clicked(mouse_pos, clicked)` is `True`, import `GamePlaceholderScene` locally and call `self.manager.push_scene(GamePlaceholderScene(self.manager, self.input))`
    - Pass `factory_id` to the game scene once `GamePlaceholderScene` accepts it; for now push with current constructor signature
    - Use `self.input.is_mouse_clicked()` for the `clicked` value — no direct pygame event reads
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [x] 5.3 Wire Escape key: call `self.manager.pop_scene()` when `self.input.is_key_just_pressed(pygame.K_ESCAPE)` is `True`
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 6. Checkpoint — smoke-test the scene manually
  - Run `python main.py`, navigate to the factory select screen, verify three cards render, hover highlights work, SELECT pushes the game scene, and Escape returns to the main menu
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Write property-based tests with Hypothesis
  - [x] 7.1 Create `tests/test_factory_select_properties.py`; add `pytest` and `hypothesis` to a `requirements-dev.txt` (create the file if absent); add a `pygame.init()` / `pygame.quit()` session fixture
    - _Requirements: 1.1–1.7, 3.1, 3.4, 4.1–4.3, 5.1–5.2_
  - [ ]* 7.2 Write Property 1 — FACTORIES schema invariant
    - `@given(entry=st.sampled_from(FACTORIES))` — assert key set equals `{"id","name","abbrev","color","difficulty","description","hazards"}`, `hazards` is a non-empty list of strings, `color` is a 3-tuple with each component in [0, 255]
    - **Property 1: FACTORIES data schema invariant**
    - **Validates: Requirements 1.2, 1.6, 1.7**
  - [ ]* 7.3 Write Property 2 — card layout centring and equal spacing
    - `@given(screen_w=st.integers(min_value=800, max_value=2560))` — compute `start_x` and card rects using the same formula as `on_enter`; assert `abs(left_margin - right_margin) <= 1` and each inter-card gap equals `CARD_GAP`
    - **Property 2: Card layout centring and equal spacing**
    - **Validates: Requirements 3.1**
  - [ ]* 7.4 Write Property 3 — difficulty badge color mapping
    - `@given(entry=st.sampled_from(FACTORIES))` — assert `_DIFF_COLORS[entry["difficulty"]]` equals the expected constant for each difficulty level
    - **Property 3: Difficulty badge color mapping**
    - **Validates: Requirements 3.4**
  - [ ]* 7.5 Write Property 4 — hover state correctness
    - `@given(mx=st.integers(0,1280), my=st.integers(0,720))` — construct a `_FactoryCard` for the first factory entry, call `card.update((mx, my))`, assert `card._hovered == card._btn_rect.collidepoint((mx, my))`
    - **Property 4: Hover state correctness**
    - **Validates: Requirements 4.1, 4.2, 4.3**
  - [ ]* 7.6 Write Property 5 — factory selection pushes correct scene
    - `@given(card_index=st.integers(0, 2))` — use a stub `SceneManager` that records `push_scene` calls; call `card.is_select_clicked` with the button centre and `clicked=True`; assert the pushed scene's `factory_id` matches the card's `factory_id` once `GamePlaceholderScene` exposes that attribute
    - **Property 5: Factory selection pushes correct scene**
    - **Validates: Requirements 5.1, 5.2**

- [x] 8. Final checkpoint — full test suite
  - Run `pytest tests/ -v` and confirm all property tests pass with at least 100 examples each
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests require `pip install pytest hypothesis`; no other build tooling needed
- Scene imports inside methods (e.g. `from scenes.game_placeholder import GamePlaceholderScene`) follow the project convention to avoid circular imports
