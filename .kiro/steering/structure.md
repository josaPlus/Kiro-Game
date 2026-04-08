# Project Structure

```
factory_safety_inspector/
├── main.py               # Entry point: pygame init, game loop, wires up SceneManager + InputHandler
├── settings.py           # All constants — colors, font sizes, layout values, FPS
├── assets/
│   └── fonts/            # Reserved for font files (unused, SysFont used currently)
├── core/
│   ├── scene_manager.py  # Stack-based scene transitions (push/pop/replace)
│   ├── input_handler.py  # Centralized per-frame input state (keyboard + mouse)
│   ├── placeholder_sprites.py  # Geometric worker sprites via pygame.draw (no image files)
│   └── sprite_animator.py      # Frame-cycling animator + walk animation factory
└── scenes/
    ├── base_scene.py     # Abstract base: on_enter/exit/pause/resume, handle_event, update, draw
    ├── main_menu.py      # Main menu with Button helper class
    ├── controls_scene.py # Controls reference screen
    ├── factory_select.py # Factory selection with _FactoryCard helper class
    └── game_placeholder.py  # Placeholder for the main game scene
```

## Architecture Patterns

- Scene system: all screens are `BaseScene` subclasses. Scenes are managed on a stack via `SceneManager`. Use `push_scene` to go deeper, `pop_scene` to go back, `replace_scene` for hard transitions.
- Input: never read `pygame` input directly in scenes. Always use `self.input` (the `InputHandler` instance) for key/mouse state.
- Lifecycle: initialize resources in `on_enter`, not `__init__`. Clean up in `on_exit`. Use `on_pause`/`on_resume` for stack-based suspend/restore.
- Scene navigation: scenes import other scene classes locally (inside methods) to avoid circular imports.
- Helper classes: UI components local to a scene (e.g. `Button`, `_FactoryCard`) are defined in the same file as the scene that uses them. Prefix private helpers with `_`.
- Constants: all layout, color, and sizing values must live in `settings.py`. Import only what you need from it.
- New gameplay systems (entities, maps, game logic) should go in `core/`. New screens go in `scenes/`.
