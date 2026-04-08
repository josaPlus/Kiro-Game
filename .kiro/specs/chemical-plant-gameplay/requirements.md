# Requirements Document

## Introduction

Replace the `GamePlaceholderScene` for the `chemical` factory with a fully playable `ChemicalPlantScene`.
The scene implements two simultaneous gameplay mechanics — gas leak detection and PPE assignment — across
three progressive difficulty levels, with a HUD, explosion animation, game-over screen, and save-data
integration. All rendering uses `pygame.draw` only; all constants live in `settings.py`; all time-based
logic uses delta time.

---

## Glossary

- **ChemicalPlantScene**: The new `BaseScene` subclass that replaces `GamePlaceholderScene` for `factory_id = "chemical"`.
- **LeakSpot**: A clickable hazard that appears randomly inside a factory zone and has a countdown timer.
- **Worker**: A character that appears in the staging area and must be assigned a respirator before entering the plant.
- **SafetyMeter**: A 0–100% HUD bar tracking player safety performance; starts at 100%.
- **ProductionMeter**: A 0–100% HUD bar that increases over time while no explosion has occurred this level.
- **HUD**: The top bar containing SafetyMeter, ProductionMeter, level indicator, timer, and score.
- **StagingArea**: The bottom strip of the factory floor where Workers queue before entering the plant.
- **FactoryZone**: One of three fixed colored rectangles on the factory floor (REACTOR ZONE, STORAGE ZONE, MIXING ZONE) where LeakSpots may appear.
- **ExplosionAnimation**: A three-frame `pygame.draw`-only animation of expanding orange/red rings played when a LeakSpot timer reaches zero.
- **GameOverScreen**: The screen shown after an explosion, displaying final score, level reached, time survived, grade, and two navigation buttons.
- **Grade**: A letter (A/B/C/F) calculated from the final SafetyMeter percentage.
- **SaveManager**: `core/save_manager.py` — the sole module responsible for reading and writing `data/save.json`.
- **SceneManager**: `core/scene_manager.py` — manages scene stack transitions.
- **InputHandler**: `core/input_handler.py` — centralized per-frame keyboard and mouse state.
- **dt**: Delta time in seconds passed to every `update()` call.

---

## Requirements

### Requirement 1: Scene Entry and Initialization

**User Story:** As a player, I want the Chemical Plant game to launch when I select the Chemical Plant factory, so that I can play the game instead of seeing a placeholder.

#### Acceptance Criteria

1. WHEN `FactorySelectScene` selects the `"chemical"` factory, THE `SceneManager` SHALL push a `ChemicalPlantScene` instance, passing the `factory_data` dict as a constructor argument.
2. THE `ChemicalPlantScene` SHALL subclass `BaseScene` and implement `on_enter`, `on_exit`, `handle_event`, `update`, and `draw`.
3. THE `ChemicalPlantScene` SHALL initialize all gameplay state (LeakSpots, Workers, meters, timers, score) inside `on_enter`, not `__init__`.
4. THE `ChemicalPlantScene` SHALL release all resources and clear all state inside `on_exit`.
5. WHEN `pygame.K_ESCAPE` is pressed during gameplay, THE `ChemicalPlantScene` SHALL call `self.manager.pop_scene()` to return to `FactorySelectScene`.

---

### Requirement 2: Factory Floor Layout

**User Story:** As a player, I want to see a recognizable chemical plant environment, so that the game feels thematic and I can orient myself.

#### Acceptance Criteria

1. THE `ChemicalPlantScene` SHALL fill the background with a dark gray color defined in `settings.py` as `COLOR_PLANT_BG`.
2. THE `ChemicalPlantScene` SHALL draw a grid of lines over the background using a grid color defined in `settings.py` as `COLOR_PLANT_GRID`.
3. THE `ChemicalPlantScene` SHALL draw exactly three `FactoryZone` rectangles with positions and sizes defined as constants in `settings.py`: `ZONE_REACTOR`, `ZONE_STORAGE`, `ZONE_MIXING` (each a `pygame.Rect`-compatible tuple).
4. THE `ChemicalPlantScene` SHALL render each `FactoryZone` label ("REACTOR ZONE", "STORAGE ZONE", "MIXING ZONE") centered inside its rectangle using `pygame.font.SysFont`.
5. THE `ChemicalPlantScene` SHALL draw the `StagingArea` as a rectangle at the bottom of the screen with a label "STAGING AREA", with position and size defined in `settings.py` as `STAGING_AREA_RECT`.
6. THE `ChemicalPlantScene` SHALL draw all layout elements using `pygame.draw` only — no image files.

---

### Requirement 3: HUD

**User Story:** As a player, I want to see my current safety status, production level, score, and level at all times, so that I can make informed decisions.

#### Acceptance Criteria

1. THE `ChemicalPlantScene` SHALL render a HUD bar across the top of the screen with height defined in `settings.py` as `HUD_HEIGHT`.
2. THE `ChemicalPlantScene` SHALL display the `SafetyMeter` as a filled progress bar, starting at 100%, with bar color defined in `settings.py` as `COLOR_SAFETY_BAR`.
3. THE `ChemicalPlantScene` SHALL display the `ProductionMeter` as a filled progress bar, starting at 0%, with bar color defined in `settings.py` as `COLOR_PRODUCTION_BAR`.
4. THE `ChemicalPlantScene` SHALL display the current level as "LEVEL 1", "LEVEL 2", or "LEVEL 3" in the HUD.
5. THE `ChemicalPlantScene` SHALL display the elapsed time survived in the current level as whole seconds in the HUD.
6. THE `ChemicalPlantScene` SHALL display the current score as an integer in the HUD.
7. WHEN the `SafetyMeter` value changes, THE `ChemicalPlantScene` SHALL update the HUD bar width proportionally within the same frame.

---

### Requirement 4: Gas Leak Detection Mechanic

**User Story:** As a player, I want to click on gas leaks before they explode, so that I can prevent disasters and earn points.

#### Acceptance Criteria

1. THE `ChemicalPlantScene` SHALL spawn `LeakSpot` objects at random positions inside a randomly selected `FactoryZone` rectangle.
2. THE `ChemicalPlantScene` SHALL maintain at most `LEAK_MAX_SIMULTANEOUS` active `LeakSpot` objects at any time, where `LEAK_MAX_SIMULTANEOUS` is defined per level in `settings.py`.
3. WHEN a `LeakSpot` is active, THE `ChemicalPlantScene` SHALL draw it as a colored circle with a visible countdown progress bar beneath it, using colors defined in `settings.py`.
4. THE `ChemicalPlantScene` SHALL count down each `LeakSpot` timer using `dt`, starting from the duration defined in `settings.py` for the current level (`LEAK_TIMER_EASY`, `LEAK_TIMER_MEDIUM`, `LEAK_TIMER_HARD`).
5. WHEN the player clicks within the hit radius of an active `LeakSpot`, THE `ChemicalPlantScene` SHALL remove the `LeakSpot`, add `SCORE_LEAK_RESOLVED` points to the score, and spawn a replacement `LeakSpot` after a short delay.
6. WHEN a `LeakSpot` timer reaches zero, THE `ChemicalPlantScene` SHALL trigger the `ExplosionAnimation` at that `LeakSpot`'s position and transition to the game-over flow.
7. THE `ChemicalPlantScene` SHALL use `self.input.is_mouse_clicked()` and `self.input.get_mouse_pos()` for all click detection — never direct `pygame` input calls.

---

### Requirement 5: PPE Assignment Mechanic

**User Story:** As a player, I want to assign respirators to workers before they enter the plant, so that I can protect them and maintain the safety rating.

#### Acceptance Criteria

1. THE `ChemicalPlantScene` SHALL spawn a new `Worker` in the `StagingArea` at intervals defined in `settings.py` per level (`WORKER_INTERVAL_EASY`, `WORKER_INTERVAL_MEDIUM`, `WORKER_INTERVAL_HARD`), using `dt` for timing.
2. THE `ChemicalPlantScene` SHALL draw each `Worker` in the `StagingArea` queue left-to-right using `core.placeholder_sprites.draw_worker`.
3. WHEN the player clicks a `Worker` in the `StagingArea`, THE `ChemicalPlantScene` SHALL mark that `Worker` as selected and highlight it visually.
4. WHEN a `Worker` is selected and the player clicks the "Assign Respirator" button, THE `ChemicalPlantScene` SHALL mark the `Worker` as protected, add `SCORE_WORKER_PROTECTED` points to the score, and remove the `Worker` from the queue.
5. WHEN a `Worker` reaches the front of the queue without being marked as protected, THE `ChemicalPlantScene` SHALL remove the `Worker` from the queue and reduce the `SafetyMeter` by `SAFETY_PENALTY_UNPROTECTED_WORKER` percentage points, where this value is defined in `settings.py`.
6. THE `ChemicalPlantScene` SHALL draw the "Assign Respirator" button using `pygame.draw` with label rendered via `pygame.font.SysFont`, with button dimensions defined in `settings.py`.
7. IF the `SafetyMeter` reaches 0%, THEN THE `ChemicalPlantScene` SHALL trigger the game-over flow.

---

### Requirement 6: Progressive Difficulty

**User Story:** As a player, I want the game to get harder over time, so that I stay engaged and challenged.

#### Acceptance Criteria

1. THE `ChemicalPlantScene` SHALL start at Level 1 with `LEAK_MAX_SIMULTANEOUS = 1`, `LEAK_TIMER_EASY = 8.0` seconds, and `WORKER_INTERVAL_EASY = 15.0` seconds.
2. THE `ChemicalPlantScene` SHALL use Level 2 settings with `LEAK_MAX_SIMULTANEOUS = 2`, `LEAK_TIMER_MEDIUM = 5.0` seconds, and `WORKER_INTERVAL_MEDIUM = 10.0` seconds.
3. THE `ChemicalPlantScene` SHALL use Level 3 settings with `LEAK_MAX_SIMULTANEOUS = 3`, `LEAK_TIMER_HARD = 3.0` seconds, and `WORKER_INTERVAL_HARD = 6.0` seconds.
4. WHEN the player survives `LEVEL_ADVANCE_DURATION = 60.0` seconds at the current level without triggering game over, THE `ChemicalPlantScene` SHALL advance to the next level and reset the level timer.
5. WHILE at Level 3, THE `ChemicalPlantScene` SHALL not advance further and SHALL continue applying Level 3 settings.
6. WHEN the level advances, THE `ChemicalPlantScene` SHALL briefly display a "LEVEL UP!" notification on screen for `LEVEL_UP_DISPLAY_DURATION` seconds, defined in `settings.py`.
7. THE `ChemicalPlantScene` SHALL read all difficulty constants exclusively from `settings.py` — no magic numbers in scene code.

---

### Requirement 7: Production Meter

**User Story:** As a player, I want to see production increase while I work safely, so that I have a sense of progress beyond just avoiding failure.

#### Acceptance Criteria

1. WHILE no explosion has occurred in the current level session, THE `ChemicalPlantScene` SHALL increase the `ProductionMeter` at a rate of `PRODUCTION_RATE` percentage points per second, defined in `settings.py`.
2. THE `ProductionMeter` SHALL be clamped to a maximum of 100%.
3. WHEN an explosion occurs, THE `ChemicalPlantScene` SHALL freeze the `ProductionMeter` at its current value before transitioning to the game-over screen.

---

### Requirement 8: Explosion Animation

**User Story:** As a player, I want to see a clear visual explosion when a leak goes unresolved, so that the consequence feels impactful.

#### Acceptance Criteria

1. WHEN a `LeakSpot` timer reaches zero, THE `ChemicalPlantScene` SHALL play the `ExplosionAnimation` centered on that `LeakSpot`'s position before showing the game-over screen.
2. THE `ExplosionAnimation` SHALL consist of exactly 3 frames, each displayed for `EXPLOSION_FRAME_DURATION` milliseconds, with a total duration of `EXPLOSION_TOTAL_DURATION = 400` ms, both defined in `settings.py`.
3. THE `ExplosionAnimation` SHALL draw expanding concentric rings using `pygame.draw.circle` in colors `COLOR_EXPLOSION_INNER` and `COLOR_EXPLOSION_OUTER` (orange and red), defined in `settings.py`.
4. WHILE the `ExplosionAnimation` is playing, THE `ChemicalPlantScene` SHALL display "EXPLOSION!" text centered on screen using `pygame.font.SysFont`.
5. WHEN the `ExplosionAnimation` completes, THE `ChemicalPlantScene` SHALL pause for `EXPLOSION_TEXT_HOLD_DURATION = 1.0` second (defined in `settings.py`) before transitioning to the `GameOverScreen`.
6. THE `ExplosionAnimation` SHALL use `pygame.draw` only — no image files or sprite sheets.

---

### Requirement 9: Game Over Screen

**User Story:** As a player, I want to see my results after a game over, so that I can evaluate my performance and decide what to do next.

#### Acceptance Criteria

1. WHEN the game-over flow completes, THE `ChemicalPlantScene` SHALL display a `GameOverScreen` overlay showing: final score, level reached, total time survived, and grade.
2. THE `ChemicalPlantScene` SHALL calculate the `Grade` as: `"A"` if final `SafetyMeter` >= 90%, `"B"` if >= 70%, `"C"` if >= 50%, `"F"` if < 50%.
3. THE `GameOverScreen` SHALL display a "PLAY AGAIN" button that restarts `ChemicalPlantScene` via `self.manager.replace_scene`.
4. THE `GameOverScreen` SHALL display a "MAIN MENU" button that pops back to `FactorySelectScene` via `self.manager.pop_scene`.
5. THE `GameOverScreen` SHALL be rendered using `pygame.draw` and `pygame.font.SysFont` only — no image files.
6. WHEN the game-over result is ready, THE `ChemicalPlantScene` SHALL call `SaveManager` to persist the result to `data/save.json` before displaying the `GameOverScreen`.

---

### Requirement 10: Save Manager Integration

**User Story:** As a player, I want my results saved automatically, so that my progress is recorded without manual action.

#### Acceptance Criteria

1. THE `SaveManager` SHALL expose a `save_result(result: dict)` method that appends a game result entry to `data/save.json`.
2. IF the `data/` directory does not exist, THEN THE `SaveManager` SHALL create it before writing.
3. IF `data/save.json` does not exist, THEN THE `SaveManager` SHALL create it with an empty results list before appending.
4. THE `SaveManager` SHALL write valid JSON to `data/save.json` on every `save_result` call.
5. THE `ChemicalPlantScene` SHALL never read or write `data/save.json` directly — all save operations MUST go through `SaveManager`.
6. THE result dict passed to `SaveManager.save_result` SHALL contain at minimum: `factory_id`, `score`, `level_reached`, `time_survived`, and `grade`.

---

### Requirement 11: Score System

**User Story:** As a player, I want to earn points for good actions, so that I have a clear measure of my performance.

#### Acceptance Criteria

1. WHEN a `LeakSpot` is resolved by a player click, THE `ChemicalPlantScene` SHALL add `SCORE_LEAK_RESOLVED` points to the score, defined in `settings.py`.
2. WHEN a `Worker` is successfully assigned a respirator, THE `ChemicalPlantScene` SHALL add `SCORE_WORKER_PROTECTED` points to the score, defined in `settings.py`.
3. THE `ChemicalPlantScene` SHALL display the current score in the HUD, updated every frame.
4. THE score SHALL be a non-negative integer at all times.
