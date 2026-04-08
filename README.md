# Factory Safety Inspector

A top-down factory safety simulation game built with Python and Pygame.

## Requirements

- Python 3.10+
- Pygame 2.x

## Install

```bash
pip install pygame
```

## Run

```bash
cd factory_safety_inspector
python main.py
```

## Controls

| Key / Action       | Result                          |
|--------------------|---------------------------------|
| WASD / Arrow keys  | Move camera / pan view          |
| I                  | Toggle Inspection Mode          |
| E                  | Interact / confirm action       |
| ESC                | Pause / back to menu            |
| SPACE              | Activate alarm (emergency)      |
| Left click         | Select worker / hazard / machine|
| Right click        | Deselect / cancel action        |
| Scroll wheel       | Zoom in / out                   |
| Click + drag       | Assign PPE to worker            |

## Completed Features

- **Chemical Plant mini-game** (`ChemicalPlantScene`) — real-time leak management, worker PPE assignment, safety/production meters, level progression, explosion animation, game-over screen, and save system. (2026-04-07)
- **Factory routing** — `FactorySelectScene` now routes the Chemical Plant card to `ChemicalPlantScene` instead of the placeholder. (2026-04-07)
- **SaveManager** (`core/save_manager.py`) — persists game results to `data/save.json` with full round-trip integrity. (2026-04-07)
- **Property-based test suite** (`tests/test_chemical_plant_properties.py`) — 13 hypothesis properties covering spawn logic, scoring, timers, level progression, grade calculation, and save round-trips. (2026-04-07)

## Project Structure

```
factory_safety_inspector/
├── main.py               # Entry point and game loop
├── settings.py           # All constants (colors, sizes, FPS)
├── assets/fonts/         # Font assets (uses system fonts currently)
├── scenes/
│   ├── base_scene.py     # Abstract base class
│   ├── main_menu.py      # Main menu screen
│   ├── controls_scene.py # Controls reference screen
│   └── game_placeholder.py
└── core/
    ├── scene_manager.py  # Stack-based scene transitions
    └── input_handler.py  # Centralized input state
```
