# Requirements Document

## Introduction

The Factory Selection Screen is the entry point between the Main Menu and active gameplay. It presents the player with three factory environments — Chemical Plant (HARD), Auto Assembly (MEDIUM), and Warehouse (EASY) — as interactive cards. The player reviews each factory's difficulty, description, and hazard list, then selects one to begin an inspection session. The screen replaces the existing placeholder implementation in `scenes/factory_select.py` with a fully functional scene.

## Glossary

- **FactorySelectScene**: The `BaseScene` subclass that owns and orchestrates the factory selection screen.
- **FactoryCard**: The `_FactoryCard` helper class (private, defined in the same file) that encapsulates rendering and hit-testing for a single factory option.
- **Factory**: A `dict` with keys `id`, `name`, `abbrev`, `color`, `difficulty`, `description`, and `hazards` describing one inspectable environment.
- **FACTORIES**: The module-level list of three Factory dicts defined in `scenes/factory_select.py`.
- **Worker Sprite**: A geometric figure drawn by `core.placeholder_sprites.draw_worker`, used as a visual preview on each card.
- **Difficulty Badge**: A coloured text label (`EASY`, `MEDIUM`, or `HARD`) rendered on each card.
- **Hazard List**: The list of hazard strings from a Factory dict, displayed on the card below the description.
- **SceneManager**: The stack-based scene controller in `core/scene_manager.py`.
- **InputHandler**: The centralised per-frame input state object accessed via `self.input` inside scenes.
- **SelectButton**: The interactive button on each card that triggers factory selection.
- **settings.py**: The single source of truth for all constants — colors, font sizes, layout values.

---

## Requirements

### Requirement 1: Factory Data Definitions

**User Story:** As a developer, I want all three factory environments defined as structured data in one place, so that the UI can be driven entirely from that data without hardcoded per-factory logic.

#### Acceptance Criteria

1. THE `FACTORIES` list SHALL contain exactly three Factory dicts: Chemical Plant, Auto Assembly, and Warehouse.
2. THE `FACTORIES` list SHALL define each Factory dict with exactly the keys `id`, `name`, `abbrev`, `color`, `difficulty`, `description`, and `hazards`.
3. THE Chemical Plant entry SHALL have `difficulty` set to `"HARD"` and `id` set to `"chemical"`.
4. THE Auto Assembly entry SHALL have `difficulty` set to `"MEDIUM"` and `id` set to `"automotive"`.
5. THE Warehouse entry SHALL have `difficulty` set to `"EASY"` and `id` set to `"warehouse"`.
6. THE `hazards` field of each Factory dict SHALL be a non-empty list of strings describing environment-specific hazards.
7. THE `color` field of each Factory dict SHALL be an RGB tuple used for card accent and worker sprite tinting.

---

### Requirement 2: Scene Lifecycle and Resource Management

**User Story:** As a developer, I want the scene to follow the established lifecycle contract, so that resources are allocated and freed correctly when the scene is pushed or popped.

#### Acceptance Criteria

1. THE `FactorySelectScene` SHALL initialise all fonts, card objects, and pre-rendered surfaces in `on_enter`, not in `__init__`.
2. THE `FactorySelectScene` SHALL release or nullify all surface and font references in `on_exit`.
3. WHEN `FactorySelectScene.on_enter` is called, THE `FactorySelectScene` SHALL create one `_FactoryCard` instance per entry in `FACTORIES`.
4. THE `FactorySelectScene` SHALL use `pygame.font.SysFont` for all font creation and SHALL NOT load font files from disk.
5. THE `FactorySelectScene` SHALL read all layout constants (card dimensions, gaps, offsets) from `settings.py` and SHALL NOT use magic numbers.

---

### Requirement 3: Card Layout and Rendering

**User Story:** As a player, I want to see all three factory options displayed as visually distinct cards, so that I can compare them at a glance before choosing.

#### Acceptance Criteria

1. THE `FactorySelectScene` SHALL render three `_FactoryCard` instances horizontally centred on the screen with equal spacing between them.
2. THE `_FactoryCard` SHALL display the factory name, Difficulty Badge, description, and Hazard List for its associated Factory.
3. THE `_FactoryCard` SHALL render a Worker Sprite in the upper portion of the card using `core.placeholder_sprites.draw_worker` with the card's `factory_id`.
4. THE Difficulty Badge SHALL be coloured green for `"EASY"`, yellow for `"MEDIUM"`, and red for `"HARD"`.
5. THE `_FactoryCard` SHALL render a SelectButton labelled `"SELECT"` in the lower portion of the card.
6. THE `FactorySelectScene` SHALL render a screen title (`"SELECT FACTORY"`) centred horizontally near the top of the screen.
7. THE `_FactoryCard` SHALL pre-render all static card content onto an off-screen `pygame.Surface` in its constructor, and SHALL blit that surface each frame rather than re-drawing static elements every frame.

---

### Requirement 4: Hover Feedback

**User Story:** As a player, I want visual feedback when I hover over a factory card, so that I know which card is interactive and which one I am about to select.

#### Acceptance Criteria

1. WHEN the mouse cursor is positioned over a SelectButton, THE `_FactoryCard` SHALL change the SelectButton's fill color to the hover color defined in `settings.py`.
2. WHEN the mouse cursor is positioned over a SelectButton, THE `_FactoryCard` SHALL change the card border color to the accent color defined in `settings.py`.
3. WHEN the mouse cursor is not positioned over a SelectButton, THE `_FactoryCard` SHALL render the SelectButton and card border in their default colors defined in `settings.py`.
4. THE `_FactoryCard` SHALL update hover state each frame using the mouse position provided by `self.input.get_mouse_pos()` via the parent scene, and SHALL NOT call `pygame.mouse.get_pos()` directly.

---

### Requirement 5: Factory Selection

**User Story:** As a player, I want to click a factory card's SELECT button to start an inspection session in that factory, so that I can begin gameplay.

#### Acceptance Criteria

1. WHEN the player clicks a SelectButton, THE `FactorySelectScene` SHALL push a game scene onto the `SceneManager` stack, passing the selected Factory's `id` to the game scene.
2. WHEN the player clicks a SelectButton, THE `FactorySelectScene` SHALL use `self.manager.push_scene` for the transition and SHALL NOT call `replace_scene` or manipulate the scene stack directly.
3. THE `FactorySelectScene` SHALL detect mouse clicks using `self.input.is_mouse_clicked()` and SHALL NOT read `pygame.MOUSEBUTTONDOWN` events directly in the scene.
4. WHEN a game scene for the selected factory is pushed, THE `FactorySelectScene` SHALL remain on the scene stack beneath it so the player can return to it.

---

### Requirement 6: Keyboard Navigation and Back Action

**User Story:** As a player, I want to press Escape to return to the Main Menu from the factory selection screen, so that I can change my mind without using the mouse.

#### Acceptance Criteria

1. WHEN the player presses the `Escape` key, THE `FactorySelectScene` SHALL call `self.manager.pop_scene` to return to the previous scene.
2. THE `FactorySelectScene` SHALL detect the Escape key using `self.input.is_key_just_pressed(pygame.K_ESCAPE)` and SHALL NOT read keyboard state directly via `pygame.key.get_pressed()`.
3. IF no scene exists beneath `FactorySelectScene` on the stack, THEN THE `SceneManager` SHALL handle the empty-stack condition gracefully without raising an exception.

---

### Requirement 7: Settings Constants

**User Story:** As a developer, I want all layout and visual constants for the factory selection screen defined in `settings.py`, so that values are easy to tune without hunting through scene code.

#### Acceptance Criteria

1. THE `settings.py` file SHALL define constants for card width, card height, card gap, card top offset, worker sprite scale, and SelectButton dimensions used by `FactorySelectScene`.
2. THE `FactorySelectScene` and `_FactoryCard` SHALL import layout constants exclusively from `settings.py` and SHALL NOT define numeric literals for sizes, colors, or font sizes inline.
3. THE difficulty badge colors (green, yellow, red) SHALL be defined as named constants in `settings.py`.
