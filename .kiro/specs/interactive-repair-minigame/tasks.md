# Plan de Implementación: interactive-repair-minigame

## Visión general

Reemplazar el click-to-resolve de fugas por un minijuego interactivo en `ChemicalPlantScene`.
El orden de implementación es: constantes → clases de paso → `_RepairMinigame` → integración en escena → tests.
Todo el input pasa por `handle_event`. Sin números mágicos fuera de `settings.py`.

---

## Tareas

- [x] 1. Agregar constantes del minijuego a `settings.py`
  - Añadir el bloque `# ── Interactive Repair Minigame` con todas las constantes del diseño:
    `MINIGAME_PANEL_W`, `MINIGAME_PANEL_H`, `MINIGAME_TIMER_EASY/MEDIUM/HARD`, `MINIGAME_TIMER_MAX`,
    `MINIGAME_WORKER_BONUS_SECONDS`, `VALVE_CLICKS_L1/L2/L3`, `VALVE_RADIUS`, `VALVE_TARGET_RADIUS`,
    `BUTTON_COUNT_L2/L3`, `MINIGAME_BTN_W/H/GAP`, `CABLE_PAIRS_L3`, `CABLE_ENDPOINT_RADIUS/GAP`,
    `MINIGAME_FEEDBACK_DURATION`, y todos los `COLOR_MINIGAME_*`.
  - No modificar ninguna constante existente (en especial `LEAK_TIMER_EASY` y `LEVEL_ADVANCE_DURATION`).
  - _Requisitos: 1.4, 2.2, 2.3, 2.4, 4.2, 4.3, 4.4, 5.1–5.4, 5.6, 5.7, 6.1, 6.4, 7.6_

- [x] 2. Implementar las clases de paso del minijuego en `scenes/chemical_plant.py`
  - [x] 2.1 Implementar `_ValveStep`
    - Clase con `step_type = "VALVE"`, `n_clicks`, `progress`, `completed`, `feedback`, `feedback_timer`.
    - Calcular `_click_targets` como N puntos equidistantes en círculo de radio `VALVE_RADIUS` en `__init__`.
    - `handle_event`: click dentro de `VALVE_TARGET_RADIUS` del target correcto avanza `progress`; cualquier otro click resetea a 0.
    - `update(dt)`: decrementar `feedback_timer`; limpiar `feedback` cuando llega a 0.
    - `draw`: dibujar círculo de válvula, puntos target (verde si ya pasados, color normal si pendientes), feedback flash.
    - Marcar `completed = True` cuando `progress == n_clicks`.
    - _Requisitos: 2.2, 2.6, 2.7_

  - [ ]* 2.2 Escribir test de propiedad para `_ValveStep` — Propiedad 9 (parcial)
    - **Propiedad 9: Interacción incorrecta resetea el progreso del paso actual a cero**
    - **Valida: Requisito 2.6**

  - [x] 2.3 Implementar `_ButtonStep`
    - Clase con `step_type = "BUTTON"`, `n_buttons`, `next_expected`, `completed`, `feedback`, `feedback_timer`, `_button_rects`.
    - `handle_event`: click en botón con número == `next_expected` avanza; click en botón incorrecto resetea `next_expected = 1`.
    - `update(dt)`: decrementar `feedback_timer`.
    - `draw`: dibujar fila de botones numerados; botones ya pulsados en verde, activo en blanco, pendientes en gris.
    - Marcar `completed = True` cuando `next_expected > n_buttons`.
    - _Requisitos: 2.3, 2.6, 2.7_

  - [ ]* 2.4 Escribir test de propiedad para `_ButtonStep` — Propiedad 9 (parcial)
    - **Propiedad 9: Interacción incorrecta resetea el progreso del paso actual a cero**
    - **Valida: Requisito 2.6**

  - [x] 2.5 Implementar `_CableStep`
    - Clase con `step_type = "CABLE"`, `n_pairs`, `connected`, `selected_left`, `completed`, `feedback`, `feedback_timer`, `_left_rects`, `_right_rects`, `_colors`.
    - `handle_event`: click en endpoint izquierdo selecciona `selected_left`; click en endpoint derecho del mismo índice conecta el par; click en endpoint derecho de índice distinto resetea `selected_left = None` y flashea error.
    - `update(dt)`: decrementar `feedback_timer`.
    - `draw`: dibujar dos columnas de endpoints coloreados; pares conectados en verde; línea entre endpoints conectados.
    - Marcar `completed = True` cuando `all(connected)`.
    - _Requisitos: 2.4, 2.6, 2.7_

  - [ ]* 2.6 Escribir test de propiedad para `_CableStep` — Propiedad 9 (parcial)
    - **Propiedad 9: Interacción incorrecta resetea el progreso del paso actual a cero**
    - **Valida: Requisito 2.6**

- [x] 3. Implementar `_RepairMinigame` en `scenes/chemical_plant.py`
  - [x] 3.1 Implementar constructor y propiedades básicas
    - `__init__(self, leak, steps, timer_duration, zone_worker_count)`: inicializar todos los campos del modelo de datos del diseño.
    - Calcular `panel_rect` centrado en pantalla usando `MINIGAME_PANEL_W/H` y `SCREEN_WIDTH/HEIGHT`.
    - Propiedad `current_step` que retorna `steps[current_step_index]`.
    - _Requisitos: 1.4, 1.5, 4.1_

  - [x] 3.2 Implementar `_RepairMinigame.handle_event`
    - Delegar el evento al `current_step`.
    - Si `current_step.completed` después del evento, avanzar `current_step_index`.
    - Si `current_step_index >= len(steps)`, marcar `self.completed = True`.
    - _Requisitos: 2.5, 3.1_

  - [ ]* 3.3 Escribir test de propiedad para avance de paso — Propiedad 10
    - **Propiedad 10: Completar un paso avanza al siguiente en la secuencia**
    - **Valida: Requisito 2.5**

  - [x] 3.4 Implementar `_RepairMinigame.update`
    - Decrementar `self.timer` por `dt`.
    - Si `timer <= 0` y no `completed`, marcar `self.failed = True`.
    - Verificar `current_step.completed` antes de decrementar (completar tiene prioridad sobre expiración).
    - _Requisitos: 3.2, 3.4_

  - [ ]* 3.5 Escribir test de propiedad para timer expirado — Propiedad 8
    - **Propiedad 8: MinigameTimer expirado dispara explosión**
    - **Valida: Requisito 3.2**

  - [x] 3.6 Implementar `_RepairMinigame.draw`
    - Dibujar panel overlay con fondo `COLOR_MINIGAME_BG` y borde `COLOR_MINIGAME_BORDER`.
    - Mostrar nombre del tipo de paso activo y progreso ("Paso N de M") con `pygame.font.SysFont`.
    - Dibujar barra de timer (`COLOR_MINIGAME_TIMER_BAR` / `COLOR_MINIGAME_TIMER_BG`).
    - Mostrar label de bonus de workers ("+Ns bonus") en `COLOR_MINIGAME_BONUS` cuando `zone_worker_count > 0`.
    - Delegar el dibujo del contenido al `current_step.draw(surface, panel_rect, fonts)`.
    - _Requisitos: 1.4, 1.5, 4.5_

- [x] 4. Implementar métodos auxiliares en `ChemicalPlantScene`
  - [x] 4.1 Implementar `_get_zone_for_pos` y `_count_zone_workers`
    - `_get_zone_for_pos(pos)`: iterar `[ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING]`; retornar la zona cuyo `pygame.Rect` contiene `pos`, o `None`.
    - `_count_zone_workers(leak_pos)`: llamar `_get_zone_for_pos`; contar workers en `_zone_workers` cuyo `target` coincide con esa zona; retornar 0 si zona es `None`.
    - _Requisitos: 4.1, 4.6_

  - [ ]* 4.2 Escribir test de propiedad para detección de zona — Propiedad 5
    - **Propiedad 5: Detección de zona por posición**
    - **Valida: Requisito 4.6**

  - [x] 4.3 Implementar `_build_steps`
    - `_build_steps(level)`: clamp `level = max(1, min(3, level))`.
    - Nivel 1: `[_ValveStep(VALVE_CLICKS_L1)]`.
    - Nivel 2: `[_ValveStep(VALVE_CLICKS_L2), _ButtonStep(BUTTON_COUNT_L2)]`.
    - Nivel 3: `[_ValveStep(VALVE_CLICKS_L3), _ButtonStep(BUTTON_COUNT_L3), _CableStep(CABLE_PAIRS_L3)]`.
    - _Requisitos: 2.1, 5.1, 5.2, 5.3, 5.7_

  - [ ]* 4.4 Escribir test de propiedad para configuración de pasos — Propiedad 6
    - **Propiedad 6: Configuración de pasos por nivel es correcta y monótona**
    - **Valida: Requisitos 2.1, 5.1, 5.2, 5.3, 5.5**

  - [x] 4.5 Implementar `_calc_minigame_timer`
    - `_calc_minigame_timer(level, zone_worker_count)`: aplicar fórmula `min(base[level-1] + zone_worker_count * MINIGAME_WORKER_BONUS_SECONDS, MINIGAME_TIMER_MAX)`.
    - Usar `[MINIGAME_TIMER_EASY, MINIGAME_TIMER_MEDIUM, MINIGAME_TIMER_HARD]` como lista base.
    - _Requisitos: 4.2, 4.3, 4.4_

  - [ ]* 4.6 Escribir test de propiedad para fórmula del timer — Propiedad 4
    - **Propiedad 4: Fórmula del MinigameTimer efectivo con cap**
    - **Valida: Requisitos 4.3, 4.4**

- [x] 5. Integrar el minijuego en `ChemicalPlantScene`
  - [x] 5.1 Añadir campo `_minigame` e importar nuevas constantes
    - En `on_enter`: inicializar `self._minigame = None`.
    - En `on_exit`: limpiar `self._minigame = None`.
    - Añadir al bloque de imports desde `settings` todas las constantes nuevas del minijuego.
    - _Requisitos: 7.3, 7.6_

  - [x] 5.2 Implementar `_open_minigame`, `_complete_minigame`, `_fail_minigame`, `_close_minigame`
    - `_open_minigame(leak)`: guard `if self._minigame is not None: return`; calcular `zone_worker_count`; calcular timer con `_calc_minigame_timer`; construir steps con `_build_steps`; crear `_RepairMinigame`; asignar a `self._minigame`.
    - `_complete_minigame()`: guard `if self._minigame is None: return`; remover fuga con `if leak in self._leaks`; sumar `SCORE_LEAK_RESOLVED`; mostrar diálogo "¡Fuga sellada!"; llamar `_close_minigame()`; llamar `_spawn_leak()` si bajo el cap.
    - `_fail_minigame()`: guard `if self._minigame is None: return`; guardar `pos = self._minigame.leak.pos`; llamar `_close_minigame()`; llamar `_trigger_explosion(pos)`.
    - `_close_minigame()`: `self._minigame = None`.
    - _Requisitos: 1.1, 1.2, 3.1, 3.2, 3.3, 7.2_

  - [ ]* 5.3 Escribir test de propiedad para completar minijuego — Propiedad 7
    - **Propiedad 7: Completar todos los pasos resuelve la fuga y suma score**
    - **Valida: Requisitos 3.1, 7.2**

  - [x] 5.4 Modificar `handle_event` para enrutar eventos al minijuego
    - Al inicio del bloque `MOUSEBUTTONDOWN` en fase `PLAYING`: si `_minigame is not None`, delegar a `_minigame.handle_event(event)` y retornar (bloquea clicks en otras fugas).
    - Reemplazar `self._resolve_leak(leak)` por `self._open_minigame(leak)` en el loop de detección de fugas.
    - Añadir handler para `K_ESCAPE`: si `_minigame is not None`, reanudar timer de la fuga (`_minigame.leak` no se actualiza mientras `_minigame` está activo) y llamar `_close_minigame()`.
    - _Requisitos: 1.1, 1.6, 1.7_

  - [ ]* 5.5 Escribir test de propiedad para exclusividad del minijuego — Propiedad 3
    - **Propiedad 3: Solo un minijuego puede estar abierto a la vez**
    - **Valida: Requisito 1.7**

  - [x] 5.6 Modificar `update` para gestionar el minijuego activo
    - En el bloque `PLAYING`: si `_minigame is not None`, llamar `_minigame.update(dt)` y NO llamar `leak.update(dt)` sobre `_minigame.leak`; las demás fugas siguen actualizándose normalmente.
    - Después de `_minigame.update(dt)`: si `_minigame.completed`, llamar `_complete_minigame()`; si `_minigame.failed`, llamar `_fail_minigame()`.
    - _Requisitos: 1.2, 1.3, 3.2_

  - [ ]* 5.7 Escribir test de propiedad para pausa de timer — Propiedad 1 y Propiedad 2
    - **Propiedad 1: Click en fuga abre minijuego y pausa su timer**
    - **Propiedad 2: Otras fugas siguen corriendo mientras el minijuego está abierto**
    - **Valida: Requisitos 1.1, 1.2, 1.3**

  - [x] 5.8 Modificar `draw` para renderizar el panel overlay
    - Al final de `draw`, después de todos los elementos de juego y antes de `_draw_drag`/`_draw_dialogs`: si `_minigame is not None`, llamar `_minigame.draw(surface, self._fonts)`.
    - El panel se dibuja encima de todo usando solo `pygame.draw` y `pygame.font.SysFont`.
    - _Requisitos: 1.4, 7.7_

- [x] 6. Checkpoint — Verificar integración completa
  - Asegurar que todos los tests existentes en `test_chemical_plant_properties.py` y `test_chemical_plant_smoke.py` siguen pasando sin modificación.
  - Asegurar que todos los tests nuevos de propiedades pasan.
  - Preguntar al usuario si hay dudas antes de continuar.

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido.
- Cada tarea referencia requisitos específicos para trazabilidad.
- Los tests de propiedad usan Hypothesis (ya instalado). Seguir el patrón de `test_chemical_plant_properties.py`.
- Los tests nuevos van en `tests/test_chemical_plant_properties.py` (archivo existente) o en un nuevo `tests/test_repair_minigame_properties.py`.
- `_minigame.leak` nunca se pasa a `leak.update(dt)` mientras el minijuego está activo — esa es la única modificación al loop de fugas.
