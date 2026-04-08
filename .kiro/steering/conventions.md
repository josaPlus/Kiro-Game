# Coding Conventions

## Constants & Settings
- All colors, sizes, font sizes, layout values, and FPS live in `settings.py`. No magic numbers anywhere else.
- Import only the specific constants you need from `settings.py`.

## Scene System
- All screens must subclass `BaseScene`.
- Initialize resources in `on_enter`, not `__init__`. Clean up in `on_exit`.
- Use `on_pause`/`on_resume` for stack-based suspend/restore.
- Never read pygame input directly in scenes — always use `self.input` (the `InputHandler` instance).
- Import other scene classes locally inside methods (not at the top of the file) to avoid circular imports.

## Scene Transitions
- All scene transitions must go through `SceneManager` (`push_scene`, `pop_scene`, `replace_scene`).
- Never instantiate or swap scenes directly outside of `SceneManager`.

## Helper Classes
- UI components scoped to a single scene (e.g. `Button`, `_FactoryCard`) are defined in the same file as the scene.
- Prefix private helpers with `_`.

## Factory Data
- All factory definitions must be a `dict` with exactly these keys:
  - `id` — unique string identifier (e.g. `"chemical"`)
  - `name` — display name (e.g. `"Chemical Plant"`)
  - `abbrev` — short code (e.g. `"CH"`)
  - `color` — RGB tuple
  - `difficulty` — string: `"EASY"`, `"MEDIUM"`, or `"HARD"`
  - `description` — short string describing the environment
  - `hazards` — list of hazard strings

## Sprites
- Worker sprites are drawn with `pygame.draw` via `core/placeholder_sprites.py`. No image files required.
- Animations use `core/sprite_animator.py` (`SpriteAnimator` class).

## Time
- `dt` (delta time in seconds) is passed to every `update()` call. Use it for all time-based logic — never use raw frame counts.

## Fonts
- Use `pygame.font.SysFont` throughout. No custom font loading until assets/fonts/ is populated.

## Save Data
- Player scores and progress are saved to `data/save.json` via `core/save_manager.py`.
- Never read or write save data outside of `save_manager.py`.

## Where Things Go
- New gameplay systems (entities, maps, game logic) → `core/`
- New screens → `scenes/`
- Save data → `data/save.json` (managed exclusively by `core/save_manager.py`)
