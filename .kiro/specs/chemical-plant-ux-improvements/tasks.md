# Plan de Implementación: chemical-plant-ux-improvements

## Visión general

Añadir tres capas de UX a `ChemicalPlantScene`: diálogos contextuales en español,
asignación por arrastre drag-and-drop, y animación de personajes con estados.
El orden de implementación va de menor a mayor dependencia: constantes → clases helper
→ integración en la escena → tests de propiedades.

## Tareas

- [x] 1. Añadir constantes de UX en `settings.py`
  - Agregar bloque `# ── Chemical Plant — UX Improvements` con todas las constantes nuevas:
    `DIALOG_DISPLAY_DURATION`, `DIALOG_VERTICAL_OFFSET`, `DIALOG_BG_ALPHA`,
    `DIALOG_PADDING`, `DIALOG_BORDER_RADIUS`, `COLOR_DIALOG_BG`, `COLOR_DIALOG_TEXT`,
    `COLOR_ZONE_DROP_HIGHLIGHT`, `COLOR_DRAG_LINE`, `DRAG_LINE_SEGMENT_LEN`,
    `DRAG_LINE_GAP_LEN`, `WORKER_WALK_SPEED`, `WORKER_ARRIVE_THRESHOLD`,
    `WORKER_ALERT_RADIUS`, `COLOR_WORKER_ALERT`, `WORKER_ALERT_RING_RADIUS`,
    `WORKER_ALERT_RING_WIDTH`
  - Usar los valores por defecto del documento de diseño
  - Sin números mágicos: todos los valores deben quedar en este bloque
  - _Requisitos: 1.10, 1.11, 2.3, 2.7, 3.10, 4.6_

- [x] 2. Implementar `_DialogoBurbuja` en `scenes/chemical_plant.py`
  - [x] 2.1 Crear la clase `_DialogoBurbuja` con campos `text`, `pos`, `remaining`
    - Método `update(dt) -> bool`: decrementa `remaining`, retorna `True` al expirar
    - Método `draw(surface, font)`: texto sobre rectángulo semi-transparente redondeado
      usando `DIALOG_BG_ALPHA`, `DIALOG_PADDING`, `DIALOG_BORDER_RADIUS`,
      `COLOR_DIALOG_BG`, `COLOR_DIALOG_TEXT`
    - _Requisitos: 1.1, 1.8, 1.9_

  - [ ]* 2.2 Escribir test de propiedad P2 — timer decrementa y expira correctamente
    - **Propiedad 2: Timer de diálogo decrementa por dt y expira correctamente**
    - Estrategia: `st.floats(0.001, 10.0)` para `t` y `dt`
    - Verificar `remaining == max(0.0, t - dt)` tras `update(dt)`
    - Verificar que `_update_dialogs` elimina diálogos con `remaining <= 0`
    - **Valida: Requisito 1.8**

- [x] 3. Implementar `_DragState` en `scenes/chemical_plant.py`
  - Crear la clase `_DragState` con campos `worker`, `origin_pos`, `cursor_pos`
  - Sin lógica adicional: es un contenedor de estado puro
  - _Requisitos: 2.1, 2.2_

- [x] 4. Extender `_Worker` con campos de animación y estado
  - Añadir imports de `SpriteAnimator` y `get_walk_animation` desde `core/sprite_animator.py`
  - Añadir campos: `state: str = "IDLE"`, `pos: tuple[int, int]`, `target: tuple[int, int] | None`,
    `animator: SpriteAnimator` (inicializado con `get_walk_animation("chemical")`)
  - Actualizar `draw(surface, x, y)`: renderizar frame actual del animator;
    dibujar anillo pulsante `COLOR_WORKER_ALERT` / `WORKER_ALERT_RING_RADIUS` /
    `WORKER_ALERT_RING_WIDTH` cuando `state == "ALERTA"`
  - _Requisitos: 3.1, 3.2, 3.6, 3.7_

  - [ ]* 4.1 Escribir test de propiedad P6 — todo Worker creado tiene un SpriteAnimator
    - **Propiedad 6: Todo Worker creado tiene un SpriteAnimator**
    - Estrategia: `st.integers(0, 10)` para `queue_index`
    - Verificar `isinstance(worker.animator, SpriteAnimator)`
    - **Valida: Requisito 3.1**

- [x] 5. Implementar sistema de diálogos en `ChemicalPlantScene`
  - Añadir imports de las nuevas constantes de diálogos desde `settings.py`
  - Inicializar `self._dialogs: list[_DialogoBurbuja] = []` en `on_enter`; limpiar en `on_exit`
  - Implementar `_create_dialog(text, pos)`: crea `_DialogoBurbuja`; aplica offset vertical
    `DIALOG_VERTICAL_OFFSET` si ya existe un diálogo en la misma posición
  - Implementar `_update_dialogs(dt)`: decrementa timers, elimina expirados con `remaining <= 0`
  - Implementar `_draw_dialogs(surface)`: itera `_dialogs` y llama `draw` en cada uno
  - Integrar `_update_dialogs(dt)` en `update()` (fase `PLAYING`)
  - Integrar `_draw_dialogs(surface)` al final de `draw()` (sobre todo lo demás)
  - _Requisitos: 1.1, 1.8, 1.9, 1.11_

  - [ ]* 5.1 Escribir test de propiedad P1 — diálogo creado en posición del evento
    - **Propiedad 1: Diálogo creado en posición del evento**
    - Estrategia: `st.tuples(st.integers(0,1280), st.integers(0,720))` para pos;
      `st.sampled_from` para tipo de evento
    - Verificar que `_dialogs` contiene al menos un diálogo con `pos` igual al evento
    - **Valida: Requisitos 1.2, 1.3, 1.4, 1.5, 1.6, 1.7**

  - [ ]* 5.2 Escribir test de propiedad P3 — offset vertical evita solapamiento
    - **Propiedad 3: Offset vertical evita solapamiento de diálogos**
    - Estrategia: `st.tuples(...)` para pos; crear diálogo existente en misma pos
    - Verificar que el nuevo diálogo tiene `pos.y` desplazado ≥ `DIALOG_VERTICAL_OFFSET`
    - **Valida: Requisito 1.11**

- [x] 6. Disparar diálogos desde los eventos de juego existentes
  - En `_resolve_leak`: llamar `_create_dialog("¡Fuga sellada!", leak.pos)`
  - En `update` al hacer spawn de worker: llamar `_create_dialog("¡Nuevo trabajador!", spawn_pos)`
  - En asignación por botón: llamar `_create_dialog("¡Respirador asignado!", worker_pos)`
  - En worker sin protección que sale: llamar `_create_dialog("¡Trabajador sin protección!", worker_pos)`
  - En `_trigger_explosion`: llamar `_create_dialog("¡EXPLOSIÓN! ¡Evacúen!", pos)`
  - En `_advance_level`: llamar `_create_dialog(f"¡Nivel {self._level} iniciado!", screen_center)`
  - _Requisitos: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 7. Implementar sistema de animación de workers en `ChemicalPlantScene`
  - Añadir imports de las nuevas constantes de animación desde `settings.py`
  - Implementar `_update_worker_animation(worker, dt)`:
    - Si `IDLE` o `EN_ZONA`: llamar `worker.animator.update(dt)`
    - Si `CAMINANDO`: mover `worker.pos` hacia `worker.target` a `WORKER_WALK_SPEED` px/s;
      llamar `worker.animator.update(dt)`; si distancia ≤ `WORKER_ARRIVE_THRESHOLD`,
      transicionar a `EN_ZONA`
    - Guard: si `CAMINANDO` y `target is None`, revertir a `IDLE`
  - Implementar `_update_worker_alert(worker)`:
    - Si `EN_ZONA`: si alguna leak activa está a < `WORKER_ALERT_RADIUS` px, → `ALERTA`
    - Si `ALERTA`: si ninguna leak activa está a < `WORKER_ALERT_RADIUS` px, → `EN_ZONA`
  - Integrar ambos métodos en `update()` iterando `self._workers`
  - _Requisitos: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.11_

  - [ ]* 7.1 Escribir test de propiedad P7 — CAMINANDO mueve a velocidad correcta
    - **Propiedad 7: Worker CAMINANDO se mueve hacia su destino a la velocidad correcta**
    - Estrategia: `st.floats(0.001, 2.0)` para dt; `st.tuples` para pos y target
    - Verificar que la nueva distancia ≤ distancia original − `WORKER_WALK_SPEED * dt` (o 0)
    - **Valida: Requisito 3.4**

  - [ ]* 7.2 Escribir test de propiedad P8 — llegada transiciona a EN_ZONA
    - **Propiedad 8: Worker llega a destino y transiciona a EN_ZONA**
    - Estrategia: posición dentro de `WORKER_ARRIVE_THRESHOLD` del target
    - Verificar `worker.state == "EN_ZONA"` tras `_update_worker_animation`
    - **Valida: Requisito 3.5**

  - [ ]* 7.3 Escribir test de propiedad P9 — proximidad activa/desactiva ALERTA
    - **Propiedad 9: Proximidad a fuga activa el estado ALERTA**
    - Estrategia: `st.floats` para distancia worker-leak respecto a `WORKER_ALERT_RADIUS`
    - Verificar transición `EN_ZONA → ALERTA` cuando distancia < radio
    - Verificar transición `ALERTA → EN_ZONA` cuando no hay leaks dentro del radio
    - **Valida: Requisitos 3.7, 3.8**

- [x] 8. Actualizar `_trigger_explosion` para poner todos los workers en ALERTA
  - En `_trigger_explosion(pos)`: iterar `self._workers` y asignar `worker.state = "ALERTA"`
  - _Requisitos: 3.9_

  - [ ]* 8.1 Escribir test de propiedad P10 — explosión pone todos los workers en ALERTA
    - **Propiedad 10: Explosión pone todos los workers en ALERTA**
    - Estrategia: `st.lists(st.sampled_from(["IDLE","CAMINANDO","EN_ZONA","ALERTA"]))` para estados
    - Verificar que todos los workers tienen `state == "ALERTA"` tras `_trigger_explosion`
    - **Valida: Requisito 3.9**

- [x] 9. Implementar drag-and-drop en `ChemicalPlantScene`
  - Añadir imports de las nuevas constantes de drag desde `settings.py`
  - Inicializar `self._drag: _DragState | None = None` en `on_enter`; limpiar en `on_exit`
  - Implementar `_start_drag(worker, origin_pos)`: crea `_DragState`, marca worker como seleccionado
  - Implementar `_end_drag(drop_pos)`:
    - Guard: `if self._drag is None: return`
    - Si `drop_pos` está dentro de alguna `FactoryZone`: asignar worker, sumar `SCORE_WORKER_PROTECTED`,
      crear diálogo `"¡Respirador asignado!"`, remover worker de `_workers`, `_drag = None`
    - Si no: devolver worker a staging (restaurar `queue_index`), `_drag = None`
  - Implementar `_cancel_drag()`: restaura worker a staging, `_drag = None`
  - Implementar `_draw_drag(surface)`:
    - Dibujar worker arrastrado en `cursor_pos`
    - Dibujar línea punteada desde `origin_pos` a `cursor_pos` con `COLOR_DRAG_LINE`,
      `DRAG_LINE_SEGMENT_LEN`, `DRAG_LINE_GAP_LEN`
    - Highlight de zona bajo cursor con `COLOR_ZONE_DROP_HIGHLIGHT`
  - Integrar `_draw_drag` en `draw()` (antes de `_draw_dialogs`)
  - _Requisitos: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.9_

- [x] 10. Integrar eventos de ratón para drag-and-drop en `handle_event`
  - En `MOUSEBUTTONDOWN` (botón 1, fase `PLAYING`): detectar si el click cae sobre un worker
    en staging (radio 20 px); si hay drag activo ignorar click en leaks/botón; llamar `_start_drag`
  - En `MOUSEMOTION` con drag activo: actualizar `self._drag.cursor_pos = event.pos`
  - En `MOUSEBUTTONUP` (botón 1) con drag activo: llamar `_end_drag(event.pos)`
  - En `KEYDOWN K_ESCAPE` con drag activo: llamar `_cancel_drag()` antes del `pop_scene`
  - Todo input exclusivamente a través de `handle_event` — sin polling directo
  - _Requisitos: 2.1, 2.8, 2.9_

  - [ ]* 10.1 Escribir test de propiedad P4 — arrastre sobre zona asigna worker y suma puntuación
    - **Propiedad 4: Arrastre sobre zona asigna worker y suma puntuación**
    - Estrategia: `st.sampled_from([ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING])` + `st.integers` para score
    - Verificar `score == initial + SCORE_WORKER_PROTECTED` y `_drag is None`
    - **Valida: Requisito 2.4**

  - [ ]* 10.2 Escribir test de propiedad P5 — arrastre fuera de zona devuelve worker a staging
    - **Propiedad 5: Arrastre fuera de zona devuelve worker a staging**
    - Estrategia: posiciones generadas fuera de los tres rectángulos de zona
    - Verificar que el worker regresa a staging y `_drag is None`
    - **Valida: Requisito 2.5**

- [x] 11. Actualizar `_draw_staging` para renderizar workers con su animator
  - Reemplazar llamada directa a `worker.draw(surface, wx, wy)` por lógica que usa
    el frame actual del `worker.animator` para workers en estado `IDLE`
  - Workers en estado `CAMINANDO`, `EN_ZONA` o `ALERTA` se dibujan en `worker.pos`
    (fuera del staging strip), no en la posición de cola
  - Asegurar que el worker arrastrado (`_drag.worker`) no se dibuja en la cola durante el arrastre
  - _Requisitos: 3.2, 3.3, 3.6, 4.5_

- [x] 12. Checkpoint — Verificar integración completa
  - Asegurar que todos los tests existentes en `test_chemical_plant_properties.py` y
    `test_chemical_plant_smoke.py` siguen pasando sin modificación
  - Asegurar que todos los tests nuevos en `test_chemical_plant_ux_properties.py` pasan
  - Verificar que no hay números mágicos fuera de `settings.py`
  - Verificar que todo input pasa por `handle_event` o `self.input`
  - Asegurar que todos los tests pasan, consultar al usuario si surgen dudas.
  - _Requisitos: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- El orden de las tareas respeta las dependencias: constantes → helpers → integración → tests
- Todos los tests de propiedades van en `tests/test_chemical_plant_ux_properties.py`
- Los tests de propiedades usan Hypothesis con mínimo 100 ejemplos por propiedad
- Cada test de propiedad incluye la etiqueta `# Feature: chemical-plant-ux-improvements, Property N`
- Los tests existentes en `test_chemical_plant_properties.py` y `test_chemical_plant_smoke.py`
  no deben modificarse
