# Tech Stack

- Language: Python 3.10+
- Framework: Pygame 2.x
- No build system — plain Python scripts

## Dependencies

```
pip install pygame
```

No requirements.txt currently exists. Only dependency is `pygame`.

## Common Commands

```bash
# Run the game
python main.py
```

No test framework is set up yet.

## Key Conventions

- `settings.py` is the single source of truth for all constants (colors, sizes, FPS, layout values). No magic numbers elsewhere.
- Delta time (`dt`) is passed in seconds to every `update()` call. Use it for all time-based logic.
- `pygame.font.SysFont` is used throughout — no custom font files are loaded yet (assets/fonts/ is empty).
- Geometric placeholder sprites are drawn with `pygame.draw` calls in `core/placeholder_sprites.py` — no image assets required.
