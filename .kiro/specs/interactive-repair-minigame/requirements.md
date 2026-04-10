# Documento de Requisitos — interactive-repair-minigame

## Introducción

Esta mejora transforma el mecanismo de reparación de fugas en `ChemicalPlantScene` de un simple click en un círculo a un **minijuego interactivo** estilo "Among Us". Al hacer click en una fuga, se abre un panel overlay con una tarea interactiva que el jugador debe completar antes de que el timer expire. Los trabajadores asignados a zonas reducen el tiempo requerido para completar el minijuego, dando sentido estratégico a la asignación previa. La dificultad escala con el nivel: más pasos, menos tiempo. El juego está diseñado para durar varios minutos si el jugador juega bien.

Todo el renderizado usa `pygame.draw`. Todas las constantes viven en `settings.py`. La lógica usa delta time.

---

## Glosario

- **ChemicalPlantScene**: Escena de juego principal para la fábrica química, definida en `scenes/chemical_plant.py`.
- **LeakSpot**: Hazard de fuga de gas activo en una zona del mapa, con timer de cuenta regresiva.
- **RepairMinigame**: Panel overlay interactivo que se abre al hacer click en un `LeakSpot`. El jugador debe completar una secuencia de pasos para sellar la fuga.
- **RepairStep**: Un paso individual dentro de un `RepairMinigame`. Cada paso tiene un tipo (`VALVE`, `BUTTON`, `CABLE`) y un estado de completado.
- **StepType**: Tipo de interacción requerida en un `RepairStep`: `VALVE` (girar válvula con clicks en secuencia), `BUTTON` (presionar botones en orden), `CABLE` (conectar cables).
- **MinigamePanel**: El rectángulo overlay dibujado sobre la escena principal que contiene los controles del `RepairMinigame`.
- **MinigameTimer**: Timer interno del `RepairMinigame` que cuenta el tiempo disponible para completar todos los pasos. Distinto del timer de la `LeakSpot`.
- **WorkerBonus**: Reducción del `MinigameTimer` base otorgada por trabajadores asignados a la zona de la fuga activa.
- **ZoneWorkerCount**: Número de trabajadores asignados a la `FactoryZone` donde está la fuga activa.
- **FactoryZone**: Uno de los tres rectángulos de zona (`ZONE_REACTOR`, `ZONE_STORAGE`, `ZONE_MIXING`).
- **Worker**: Personaje asignado a una zona mediante drag-and-drop.
- **dt**: Delta time en segundos, pasado a cada llamada `update()`.
- **settings.py**: Fuente única de verdad para todas las constantes del juego.

---

## Requisitos

### Requisito 1: Apertura del minijuego al hacer click en una fuga

**User Story:** Como jugador, quiero que al hacer click en una fuga se abra un panel interactivo, para que reparar fugas sea una tarea activa y no un simple click.

#### Criterios de Aceptación

1. WHEN the player clicks within the hit radius of an active `LeakSpot`, THE `ChemicalPlantScene` SHALL open a `RepairMinigame` panel overlay and transition to the `MINIGAME` sub-phase, instead of immediately resolving the leak.
2. WHILE a `RepairMinigame` is open, THE `ChemicalPlantScene` SHALL pause the `LeakSpot` countdown timer for that specific leak.
3. WHILE a `RepairMinigame` is open, THE `ChemicalPlantScene` SHALL continue updating all other active `LeakSpot` timers, worker animations, and HUD elements.
4. THE `RepairMinigame` panel SHALL be drawn as a centered overlay rectangle on top of the main scene, using `pygame.draw` only, with dimensions defined in `settings.py` as `MINIGAME_PANEL_W` and `MINIGAME_PANEL_H`.
5. THE `MinigamePanel` SHALL display the name of the active step type, the step progress (e.g. "Paso 1 de 2"), and the remaining `MinigameTimer` as a visible countdown bar.
6. IF the player presses `K_ESCAPE` while a `RepairMinigame` is open, THEN THE `ChemicalPlantScene` SHALL close the panel, resume the `LeakSpot` timer, and return to the `PLAYING` phase without resolving the leak.
7. THE `ChemicalPlantScene` SHALL allow at most one `RepairMinigame` open at a time — clicking a second leak while one is open SHALL have no effect.

---

### Requisito 2: Pasos del minijuego — tipos de interacción

**User Story:** Como jugador, quiero completar tareas interactivas variadas para reparar fugas, para que el juego sea más entretenido que hacer click en un punto.

#### Acceptance Criteria

1. THE `RepairMinigame` SHALL consist of one or more `RepairStep` objects, each with a `StepType` of `VALVE`, `BUTTON`, or `CABLE`.
2. WHEN the active `RepairStep` has type `VALVE`, THE `MinigamePanel` SHALL display a circular valve graphic and require the player to click a sequence of `N` positions around the valve in clockwise order, where `N` is defined per level in `settings.py` as `VALVE_CLICKS_PER_LEVEL`.
3. WHEN the active `RepairStep` has type `BUTTON`, THE `MinigamePanel` SHALL display a row of numbered buttons and require the player to click them in ascending numerical order.
4. WHEN the active `RepairStep` has type `CABLE`, THE `MinigamePanel` SHALL display two columns of colored endpoints and require the player to click a left endpoint then the matching right endpoint to connect each cable pair.
5. WHEN the player completes all interactions required by the active `RepairStep`, THE `ChemicalPlantScene` SHALL advance to the next `RepairStep` in the sequence.
6. WHEN the player makes an incorrect interaction (wrong order, wrong cable match), THE `ChemicalPlantScene` SHALL reset the current `RepairStep` progress to zero without closing the panel.
7. THE `MinigamePanel` SHALL provide clear visual feedback for each interaction: correct clicks turn green, incorrect clicks flash red, using colors defined in `settings.py` as `COLOR_MINIGAME_CORRECT` and `COLOR_MINIGAME_ERROR`.

---

### Requisito 3: Completar y fallar el minijuego

**User Story:** Como jugador, quiero que completar el minijuego selle la fuga y que agotar el tiempo cause una explosión, para que las consecuencias sean claras.

#### Acceptance Criteria

1. WHEN the player completes all `RepairStep` objects in the `RepairMinigame`, THE `ChemicalPlantScene` SHALL close the panel, remove the `LeakSpot`, add `SCORE_LEAK_RESOLVED` points to the score, and return to the `PLAYING` phase.
2. WHEN the `MinigameTimer` reaches zero before all steps are completed, THE `ChemicalPlantScene` SHALL close the panel and trigger the `ExplosionAnimation` at the `LeakSpot` position, as if the leak timer had expired naturally.
3. WHEN the `RepairMinigame` is completed successfully, THE `ChemicalPlantScene` SHALL spawn a replacement `LeakSpot` if the active leak count is below the level cap, consistent with the existing `_resolve_leak` behavior.
4. THE `MinigameTimer` SHALL be a separate countdown from the `LeakSpot` timer — the `LeakSpot` timer is paused while the minigame is open; the `MinigameTimer` runs independently during the minigame.

---

### Requisito 4: Efecto de los trabajadores asignados sobre el minijuego

**User Story:** Como jugador, quiero que asignar trabajadores a una zona antes de que aparezca una fuga reduzca la dificultad del minijuego en esa zona, para que la asignación estratégica tenga un efecto mecánico claro.

#### Acceptance Criteria

1. WHEN a `RepairMinigame` is created for a `LeakSpot` in a `FactoryZone`, THE `ChemicalPlantScene` SHALL count the number of `Worker` objects assigned to that zone as `ZoneWorkerCount`.
2. THE `MinigameTimer` base duration SHALL be defined in `settings.py` per level as `MINIGAME_TIMER_EASY`, `MINIGAME_TIMER_MEDIUM`, and `MINIGAME_TIMER_HARD`.
3. THE effective `MinigameTimer` duration SHALL be calculated as: `base_duration + ZoneWorkerCount * MINIGAME_WORKER_BONUS_SECONDS`, where `MINIGAME_WORKER_BONUS_SECONDS` is defined in `settings.py` as a positive number of seconds added per worker.
4. THE effective `MinigameTimer` duration SHALL be capped at a maximum of `MINIGAME_TIMER_MAX` seconds, defined in `settings.py`, to prevent trivially easy minigames with many workers.
5. WHILE a `RepairMinigame` is open, THE `ChemicalPlantScene` SHALL display the `ZoneWorkerCount` bonus visually in the panel (e.g. "+Ns bonus" label), using a color defined in `settings.py` as `COLOR_MINIGAME_BONUS`.
6. THE `ChemicalPlantScene` SHALL determine which zone a `LeakSpot` belongs to by checking which `FactoryZone` rectangle contains the leak's position.

---

### Requisito 5: Dificultad progresiva del minijuego

**User Story:** Como jugador, quiero que el minijuego sea simple al inicio y se complique con el nivel, para que pueda aprender las mecánicas antes de enfrentar desafíos mayores.

#### Acceptance Criteria

1. WHILE at Level 1, THE `ChemicalPlantScene` SHALL generate `RepairMinigame` instances with exactly 1 `RepairStep` of type `VALVE` with `VALVE_CLICKS_L1 = 3` required clicks, defined in `settings.py`.
2. WHILE at Level 2, THE `ChemicalPlantScene` SHALL generate `RepairMinigame` instances with exactly 2 `RepairStep` objects: one `VALVE` step and one `BUTTON` step, with `VALVE_CLICKS_L2 = 4` clicks for the valve, defined in `settings.py`.
3. WHILE at Level 3, THE `ChemicalPlantScene` SHALL generate `RepairMinigame` instances with exactly 3 `RepairStep` objects: one `VALVE`, one `BUTTON`, and one `CABLE` step, with `VALVE_CLICKS_L3 = 5` clicks for the valve, defined in `settings.py`.
4. THE `MinigameTimer` base durations SHALL follow: `MINIGAME_TIMER_EASY = 12.0` seconds (Level 1), `MINIGAME_TIMER_MEDIUM = 9.0` seconds (Level 2), `MINIGAME_TIMER_HARD = 6.0` seconds (Level 3), all defined in `settings.py`.
5. THE number of `RepairStep` objects per level SHALL be non-decreasing: Level 1 ≤ Level 2 ≤ Level 3.
6. THE `MinigameTimer` base duration per level SHALL be non-increasing: Level 1 ≥ Level 2 ≥ Level 3.
7. THE `ChemicalPlantScene` SHALL read all minigame difficulty constants exclusively from `settings.py` — no magic numbers in scene code.

---

### Requisito 6: Duración del juego y curva de dificultad

**User Story:** Como jugador, quiero que el juego pueda durar varios minutos si juego bien, para que valga la pena aprender las mecánicas.

#### Acceptance Criteria

1. THE `ChemicalPlantScene` SHALL keep `LEAK_TIMER_EASY = 8.0` seconds for Level 1 leaks, giving the player time to open and complete the minigame before the leak timer would have expired.
2. THE `MINIGAME_TIMER_EASY` SHALL be set to a value that allows a player to complete 1 `VALVE` step with `VALVE_CLICKS_L1` clicks within the time limit under normal conditions.
3. WHEN the player successfully completes minigames without triggering explosions, THE `ChemicalPlantScene` SHALL continue advancing through levels and increasing difficulty, allowing gameplay to extend beyond 3 minutes.
4. THE `ChemicalPlantScene` SHALL NOT reduce the `LEVEL_ADVANCE_DURATION` — levels still advance after 60 seconds of survival, preserving the existing progression pacing.
5. IF the player completes a minigame faster than the `MinigameTimer` allows, THEN THE `ChemicalPlantScene` SHALL immediately close the panel and resolve the leak without waiting for the timer to expire.

---

### Requisito 7: Integración y compatibilidad con sistemas existentes

**User Story:** Como desarrollador, quiero que el minijuego se integre sin romper la lógica existente de fugas, trabajadores, puntuación y guardado.

#### Acceptance Criteria

1. THE `ChemicalPlantScene` SHALL preserve all existing `LeakSpot` spawning logic — the minigame replaces the click-to-resolve action, not the spawn or timer mechanics.
2. THE `ChemicalPlantScene` SHALL preserve all existing scoring: `SCORE_LEAK_RESOLVED` is awarded upon successful minigame completion, `SCORE_WORKER_PROTECTED` upon worker assignment.
3. THE `ChemicalPlantScene` SHALL preserve all existing phase transitions: `PLAYING` → `EXPLODING` → `GAME_OVER`, with the new `MINIGAME` sub-phase nested within `PLAYING`.
4. THE `ChemicalPlantScene` SHALL preserve all existing `SaveManager` integration: `save_result` called exactly once before `_GameOverScreen` is shown.
5. THE `ChemicalPlantScene` SHALL preserve all existing drag-and-drop worker assignment — workers assigned to zones still boost production rate and now also provide `MinigameTimer` bonuses.
6. ALL new constants introduced by this feature SHALL be defined in `settings.py` — no magic numbers in scene code.
7. THE `ChemicalPlantScene` SHALL continue to use `pygame.draw` and `pygame.font.SysFont` exclusively — no image files.
8. THE `RepairMinigame` panel SHALL be implemented as a private helper class `_RepairMinigame` in `scenes/chemical_plant.py`, following the existing pattern of `_LeakSpot`, `_Worker`, and `_GameOverScreen`.
