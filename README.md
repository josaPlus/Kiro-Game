# Factory Safety Inspector

A top-down factory safety simulation game built with Python and Pygame. You play as a Safety & Hygiene Coordinator inspecting a chemical plant, managing workers, sealing gas leaks, and enforcing PPE compliance.

## Requirements

- Python 3.10+
- Pygame 2.x

## Install

```bash
pip install pygame
```

## Run

```bash
python main.py
```

## How to Play

1. Select the **Chemical Plant** from the factory selection screen
2. **Leaks** appear in the reactor, storage, and mixing zones — click one to open the repair minigame
3. Complete the interactive repair task (valve, buttons, or cables) before the timer runs out
4. **Drag workers** from the staging area to a factory zone to assign them respirators
5. Workers in zones boost production rate and extend your repair timer
6. Survive as long as possible across 3 escalating difficulty levels

## Controls

| Key / Action         | Result                                      |
|----------------------|---------------------------------------------|
| Left click (leak)    | Open repair minigame                        |
| Click + drag worker  | Assign worker to a factory zone             |
| Click worker         | Select worker for button assignment         |
| Assign Respirator btn| Assign selected worker via button           |
| ESC (in minigame)    | Cancel repair, resume leak timer            |
| ESC (in game)        | Return to main menu                         |

## Repair Minigame

Clicking a leak opens an interactive panel. Complete all steps before the timer expires:

| Level | Steps | Types |
|-------|-------|-------|
| 1 | 1 | Valve (3 clicks) |
| 2 | 2 | Valve (4 clicks) + Buttons |
| 3 | 3 | Valve (5 clicks) + Buttons + Cables |

Workers assigned to the leak's zone add bonus seconds to the repair timer.

## Grading

Final grade is based on a weighted score: 50% safety meter + 30% score + 20% time survived.

| Grade | Weighted Score |
|-------|---------------|
| A     | ≥ 85          |
| B     | ≥ 65          |
| C     | ≥ 45          |
| F     | < 45          |

## Project Structure

```
factory_safety_inspector/
├── main.py                      # Entry point and game loop
├── settings.py                  # All constants (colors, sizes, FPS, gameplay values)
├── assets/fonts/                # Reserved for font files (SysFont used currently)
├── core/
│   ├── scene_manager.py         # Stack-based scene transitions
│   ├── input_handler.py         # Centralized per-frame input state
│   ├── placeholder_sprites.py   # Geometric worker sprites via pygame.draw
│   ├── sprite_animator.py       # Frame-cycling animator + walk animation factory
│   └── save_manager.py          # Persists game results to data/save.json
├── scenes/
│   ├── base_scene.py            # Abstract base class for all screens
│   ├── main_menu.py             # Main menu screen
│   ├── controls_scene.py        # Controls reference screen
│   ├── factory_select.py        # Factory selection with 3 cards
│   ├── chemical_plant.py        # Chemical Plant gameplay scene (fully implemented)
│   └── game_placeholder.py      # Placeholder for Auto Assembly and Warehouse
└── tests/
    ├── test_chemical_plant_properties.py   # 13 Hypothesis property tests
    └── test_factory_select_properties.py   # Factory select property tests
```

## Completed Features

- **Main menu & scene navigation** — stack-based scene system with main menu, controls screen, and factory selection. (2026-04-07)
- **Factory selection screen** — 3 factory cards (Chemical Plant, Auto Assembly, Warehouse) with difficulty badges and worker sprites. (2026-04-07)
- **SaveManager** — persists game results to `data/save.json` with full round-trip integrity. (2026-04-07)
- **Chemical Plant gameplay** — real-time leak management, safety/production meters, 3-level progression, explosion animation, game-over screen with grade. (2026-04-07)
- **Property-based test suite** — 13 Hypothesis properties covering spawn logic, scoring, timers, level progression, grade calculation, and save round-trips. (2026-04-07)
- **Spanish contextual dialogs** — floating speech bubbles in Spanish for all game events (leak sealed, new worker, explosion, level up, etc.). (2026-04-09)
- **Drag-and-drop worker assignment** — drag workers from staging to factory zones with dashed guide line and zone highlight. (2026-04-09)
- **Worker character animation** — workers have IDLE, CAMINANDO, EN_ZONA, and ALERTA states with walk animation and alert rings. (2026-04-09)
- **Interactive repair minigame** — clicking a leak opens an Among Us-style overlay with valve rotation, button sequence, and cable matching steps that scale per level. (2026-04-09)
- **Worker zone bonuses** — workers assigned to a zone boost production rate (+20% each) and extend the repair minigame timer (+3s each). (2026-04-09)
- **Weighted grade formula** — final grade uses safety (50%), score (30%), and time survived (20%) so idle play results in a poor grade. (2026-04-09)

## Planned

- Auto Assembly scene (medium difficulty)
- Warehouse scene (easy difficulty)
- Sound effects and background music
- High score leaderboard
