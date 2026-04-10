# Documento de Requisitos — chemical-plant-ux-improvements

## Introducción

Esta mejora añade tres capas de experiencia de usuario a `ChemicalPlantScene`:

1. **Diálogos contextuales en español** — mensajes flotantes que informan al jugador sobre eventos del juego (fugas, trabajadores, asignaciones, explosiones) en español.
2. **Asignación interactiva de trabajadores por arrastre** — el jugador puede arrastrar un trabajador desde el área de staging hasta una zona del mapa para asignarlo, en lugar de depender únicamente del botón "Asignar Respirador".
3. **Animación de personajes** — los trabajadores caminan hacia su posición asignada, tienen animación idle en staging y reaccionan visualmente a eventos cercanos (fugas, explosiones).

Toda la lógica nueva se integra en `scenes/chemical_plant.py` y `settings.py`. Las animaciones reutilizan `core/sprite_animator.py` y `core/placeholder_sprites.py`. No se usan archivos de imagen.

---

## Glosario

- **ChemicalPlantScene**: Escena de juego principal para la fábrica química, definida en `scenes/chemical_plant.py`.
- **DialogoBurbuja**: Mensaje de texto flotante que aparece en pantalla durante un tiempo limitado y luego desaparece.
- **EventoJuego**: Acción o cambio de estado que dispara un `DialogoBurbuja` (fuga detectada, trabajador llegó, respirador asignado, explosión).
- **Worker**: Personaje en el área de staging que debe recibir un respirador antes de entrar a la planta.
- **StagingArea**: Franja inferior de la pantalla donde los `Worker` esperan en cola.
- **FactoryZone**: Uno de los tres rectángulos de zona en el piso de la fábrica (`ZONE_REACTOR`, `ZONE_STORAGE`, `ZONE_MIXING`).
- **DragState**: Estado interno que registra si el jugador está arrastrando un `Worker`, cuál es, y la posición actual del cursor.
- **ZonaDestino**: La `FactoryZone` sobre la que el jugador suelta un `Worker` durante un arrastre.
- **SpriteAnimator**: Clase en `core/sprite_animator.py` que cicla frames de animación a una velocidad en fps.
- **EstadoWorker**: Uno de los estados de animación de un `Worker`: `IDLE` (en staging), `CAMINANDO` (moviéndose hacia destino), `EN_ZONA` (en su zona asignada), `ALERTA` (fuga cercana).
- **UmbralAlerta**: Distancia en píxeles entre un `Worker` y una `LeakSpot` activa que activa el estado `ALERTA`.
- **dt**: Delta time en segundos, pasado a cada llamada `update()`.
- **settings.py**: Fuente única de verdad para todas las constantes del juego.
- **InputHandler**: `core/input_handler.py` — estado centralizado de teclado y ratón por frame.

---

## Requisitos

### Requisito 1: Diálogos contextuales en español

**User Story:** Como jugador, quiero ver mensajes en español que expliquen qué está pasando en el juego, para entender los eventos sin necesidad de leer documentación externa.

#### Criterios de Aceptación

1. THE `ChemicalPlantScene` SHALL maintain a list of active `DialogoBurbuja` objects, each with a text string, a screen position, and a remaining display duration.
2. WHEN a `LeakSpot` is resolved by a player click, THE `ChemicalPlantScene` SHALL create a `DialogoBurbuja` with the text `"¡Fuga sellada!"` centered on the resolved leak's position.
3. WHEN a new `Worker` spawns in the `StagingArea`, THE `ChemicalPlantScene` SHALL create a `DialogoBurbuja` with the text `"¡Nuevo trabajador!"` at the worker's spawn position.
4. WHEN a `Worker` is successfully assigned a respirator (via drag or button), THE `ChemicalPlantScene` SHALL create a `DialogoBurbuja` with the text `"¡Respirador asignado!"` at the worker's current position.
5. WHEN a `Worker` exits the queue without protection, THE `ChemicalPlantScene` SHALL create a `DialogoBurbuja` with the text `"¡Trabajador sin protección!"` at the worker's last position.
6. WHEN the `ExplosionAnimation` begins, THE `ChemicalPlantScene` SHALL create a `DialogoBurbuja` with the text `"¡EXPLOSIÓN! ¡Evacúen!"` centered on the explosion position.
7. WHEN the level advances, THE `ChemicalPlantScene` SHALL create a `DialogoBurbuja` with the text `"¡Nivel {N} iniciado!"` (where N is the new level number) centered on screen.
8. THE `ChemicalPlantScene` SHALL update each `DialogoBurbuja` timer using `dt`, removing dialogs whose remaining duration reaches zero.
9. THE `ChemicalPlantScene` SHALL render each active `DialogoBurbuja` as text drawn with `pygame.font.SysFont` over a semi-transparent rounded rectangle background, using colors defined in `settings.py`.
10. THE `DialogoBurbuja` display duration SHALL be defined in `settings.py` as `DIALOG_DISPLAY_DURATION` (default: 2.0 seconds).
11. IF a new `DialogoBurbuja` is created at the same position as an existing one, THEN THE `ChemicalPlantScene` SHALL offset the new dialog vertically by `DIALOG_VERTICAL_OFFSET` pixels (defined in `settings.py`) to avoid overlap.

---

### Requisito 2: Asignación interactiva de trabajadores por arrastre

**User Story:** Como jugador, quiero arrastrar a un trabajador desde el área de staging hasta una zona del mapa para asignarlo, para que la interacción sea más física e intuitiva.

#### Criterios de Aceptación

1. WHEN the player presses the mouse button down on a `Worker` in the `StagingArea`, THE `ChemicalPlantScene` SHALL enter drag mode, storing the dragged `Worker` in `DragState` and marking it as selected.
2. WHILE in drag mode, THE `ChemicalPlantScene` SHALL render the dragged `Worker` sprite at the current cursor position, offset from the staging queue.
3. WHILE in drag mode, THE `ChemicalPlantScene` SHALL highlight any `FactoryZone` rectangle that the cursor is currently hovering over, using a highlight color defined in `settings.py` as `COLOR_ZONE_DROP_HIGHLIGHT`.
4. WHEN the player releases the mouse button while in drag mode and the cursor is inside a `FactoryZone`, THE `ChemicalPlantScene` SHALL assign the `Worker` to that zone, add `SCORE_WORKER_PROTECTED` points to the score, and exit drag mode.
5. WHEN the player releases the mouse button while in drag mode and the cursor is NOT inside any `FactoryZone`, THE `ChemicalPlantScene` SHALL return the `Worker` to its original position in the staging queue and exit drag mode.
6. THE `ChemicalPlantScene` SHALL support the existing "Assign Respirator" button as an alternative assignment method alongside drag-and-drop.
7. WHEN drag mode is active, THE `ChemicalPlantScene` SHALL draw a dashed line from the worker's original staging position to the current cursor position as a visual guide, using a color defined in `settings.py` as `COLOR_DRAG_LINE`.
8. THE `ChemicalPlantScene` SHALL use `pygame.MOUSEBUTTONDOWN`, `pygame.MOUSEMOTION`, and `pygame.MOUSEBUTTONUP` events for drag detection — never polling input directly outside of `handle_event`.
9. IF the player presses `K_ESCAPE` while in drag mode, THEN THE `ChemicalPlantScene` SHALL cancel the drag and return the `Worker` to the staging queue without assigning it.

---

### Requisito 3: Animación de personajes

**User Story:** Como jugador, quiero ver a los trabajadores moverse y reaccionar visualmente, para que el juego se sienta vivo y los eventos sean más claros.

#### Criterios de Aceptación

1. THE `ChemicalPlantScene` SHALL assign each `Worker` a `SpriteAnimator` instance (from `core/sprite_animator.py`) using `get_walk_animation("chemical")` upon creation.
2. WHILE a `Worker` is in the `StagingArea` with state `IDLE`, THE `ChemicalPlantScene` SHALL update the worker's `SpriteAnimator` each frame with `dt` and render the current animation frame.
3. WHEN a `Worker` is assigned to a `FactoryZone` (via drag or button), THE `ChemicalPlantScene` SHALL set the worker's state to `CAMINANDO` and record the target position as the center of the assigned `FactoryZone`.
4. WHILE a `Worker` has state `CAMINANDO`, THE `ChemicalPlantScene` SHALL move the worker's position toward the target at a speed defined in `settings.py` as `WORKER_WALK_SPEED` pixels per second, updating the `SpriteAnimator` each frame.
5. WHEN a `Worker` with state `CAMINANDO` reaches its target position (within `WORKER_ARRIVE_THRESHOLD` pixels, defined in `settings.py`), THE `ChemicalPlantScene` SHALL set the worker's state to `EN_ZONA` and stop the walk animation.
6. WHILE a `Worker` has state `EN_ZONA`, THE `ChemicalPlantScene` SHALL render the worker as a static sprite at its assigned zone position.
7. WHEN an active `LeakSpot` is within `WORKER_ALERT_RADIUS` pixels of a `Worker` with state `EN_ZONA`, THE `ChemicalPlantScene` SHALL set that worker's state to `ALERTA` and render a visual indicator (a pulsing colored ring) around the worker, using `COLOR_WORKER_ALERT` defined in `settings.py`.
8. WHEN no active `LeakSpot` is within `WORKER_ALERT_RADIUS` pixels of a `Worker` in state `ALERTA`, THE `ChemicalPlantScene` SHALL revert the worker's state to `EN_ZONA`.
9. WHEN the `ExplosionAnimation` begins, THE `ChemicalPlantScene` SHALL set all `Worker` objects to state `ALERTA` regardless of their current position.
10. THE `ChemicalPlantScene` SHALL define `WORKER_WALK_SPEED`, `WORKER_ARRIVE_THRESHOLD`, `WORKER_ALERT_RADIUS`, and `COLOR_WORKER_ALERT` in `settings.py`.
11. THE `ChemicalPlantScene` SHALL use `core/sprite_animator.py` for all worker animation — no custom frame cycling logic in the scene.

---

### Requisito 4: Integración y compatibilidad

**User Story:** Como desarrollador, quiero que las mejoras de UX se integren sin romper la lógica de juego existente, para que el sistema de puntuación, seguridad y guardado sigan funcionando correctamente.

#### Criterios de Aceptación

1. THE `ChemicalPlantScene` SHALL preserve all existing scoring logic: `SCORE_LEAK_RESOLVED` for leaks, `SCORE_WORKER_PROTECTED` for worker assignment (whether via drag or button).
2. THE `ChemicalPlantScene` SHALL preserve all existing `SafetyMeter` penalty logic: `SAFETY_PENALTY_UNPROTECTED_WORKER` applied when a worker exits without protection.
3. THE `ChemicalPlantScene` SHALL preserve all existing phase transitions: `PLAYING` → `EXPLODING` → `GAME_OVER`.
4. THE `ChemicalPlantScene` SHALL preserve all existing `SaveManager` integration: `save_result` called exactly once before `_GameOverScreen` is shown.
5. THE `ChemicalPlantScene` SHALL preserve all existing HUD rendering: `SafetyMeter`, `ProductionMeter`, level, time, and score bars.
6. ALL new constants introduced by this feature SHALL be defined in `settings.py` — no magic numbers in scene code.
7. THE `ChemicalPlantScene` SHALL continue to use `pygame.draw` and `pygame.font.SysFont` exclusively — no image files.
