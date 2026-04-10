"""scenes/chemical_plant.py
ChemicalPlantScene and private helper classes.
"""
from __future__ import annotations

import math
import random
import pygame

from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    # Interactive Repair Minigame
    MINIGAME_PANEL_W, MINIGAME_PANEL_H,
    MINIGAME_TIMER_EASY, MINIGAME_TIMER_MEDIUM, MINIGAME_TIMER_HARD, MINIGAME_TIMER_MAX,
    MINIGAME_WORKER_BONUS_SECONDS,
    VALVE_CLICKS_L1, VALVE_CLICKS_L2, VALVE_CLICKS_L3, VALVE_RADIUS, VALVE_TARGET_RADIUS,
    BUTTON_COUNT_L2, BUTTON_COUNT_L3, MINIGAME_BTN_W, MINIGAME_BTN_H, MINIGAME_BTN_GAP,
    CABLE_PAIRS_L3, CABLE_ENDPOINT_RADIUS, CABLE_ENDPOINT_GAP,
    MINIGAME_FEEDBACK_DURATION,
    COLOR_MINIGAME_BG, COLOR_MINIGAME_BORDER, COLOR_MINIGAME_CORRECT, COLOR_MINIGAME_ERROR,
    COLOR_MINIGAME_BONUS, COLOR_MINIGAME_TIMER_BAR, COLOR_MINIGAME_TIMER_BG,
    COLOR_MINIGAME_STEP_ACTIVE, COLOR_MINIGAME_STEP_DONE,
    COLOR_MINIGAME_VALVE_POINT, COLOR_MINIGAME_CABLE,
    # UX Improvements — dialogs
    DIALOG_DISPLAY_DURATION,
    DIALOG_VERTICAL_OFFSET,
    DIALOG_BG_ALPHA,
    DIALOG_PADDING,
    DIALOG_BORDER_RADIUS,
    COLOR_DIALOG_BG,
    COLOR_DIALOG_TEXT,
    # UX Improvements — drag-and-drop
    COLOR_ZONE_DROP_HIGHLIGHT,
    COLOR_DRAG_LINE,
    DRAG_LINE_SEGMENT_LEN,
    DRAG_LINE_GAP_LEN,
    # UX Improvements — worker animation
    WORKER_WALK_SPEED,
    WORKER_ARRIVE_THRESHOLD,
    WORKER_ALERT_RADIUS,
    # UX Improvements — worker alert
    COLOR_WORKER_ALERT,
    WORKER_ALERT_RING_RADIUS,
    WORKER_ALERT_RING_WIDTH,
    # Floor / zones
    COLOR_PLANT_BG,
    COLOR_PLANT_GRID,
    ZONE_REACTOR,
    ZONE_STORAGE,
    ZONE_MIXING,
    COLOR_ZONE_REACTOR,
    COLOR_ZONE_STORAGE,
    COLOR_ZONE_MIXING,
    COLOR_ZONE_LABEL,
    # Staging
    STAGING_AREA_RECT,
    COLOR_STAGING_BG,
    COLOR_STAGING_LABEL,
    WORKER_SPACING,
    WORKER_STAGING_Y,
    ASSIGN_BTN_X,
    ASSIGN_BTN_Y,
    ASSIGN_BTN_W,
    ASSIGN_BTN_H,
    COLOR_ASSIGN_BTN,
    COLOR_ASSIGN_BTN_TEXT,
    # HUD
    HUD_HEIGHT,
    HUD_BAR_W,
    HUD_BAR_H,
    HUD_BAR_MARGIN,
    COLOR_HUD_BG,
    COLOR_HUD_TEXT,
    COLOR_SAFETY_BAR,
    COLOR_PRODUCTION_BAR,
    # Overlays
    COLOR_LEVEL_UP_TEXT,
    COLOR_EXPLOSION_TEXT,
    # Leak
    LEAK_HIT_RADIUS,
    LEAK_CIRCLE_RADIUS,
    LEAK_TIMER_BAR_W,
    LEAK_TIMER_BAR_H,
    LEAK_TIMER_EASY,
    LEAK_TIMER_MEDIUM,
    LEAK_TIMER_HARD,
    COLOR_LEAK_CIRCLE,
    COLOR_LEAK_TIMER_BAR,
    COLOR_LEAK_TIMER_BG,
    # Worker
    COLOR_WORKER_SELECTED,
    WORKER_INTERVAL_EASY,
    WORKER_INTERVAL_MEDIUM,
    WORKER_INTERVAL_HARD,
    SCORE_WORKER_PROTECTED,
    # Scoring / progression
    SCORE_LEAK_RESOLVED,
    SAFETY_PENALTY_UNPROTECTED_WORKER,
    LEVEL_ADVANCE_DURATION,
    LEVEL_UP_DISPLAY_DURATION,
    PRODUCTION_RATE,
    # Explosion
    EXPLOSION_FRAME_DURATION,
    EXPLOSION_TOTAL_DURATION,
    EXPLOSION_TEXT_HOLD_DURATION,
    COLOR_EXPLOSION_INNER,
    COLOR_EXPLOSION_OUTER,
    # Game over
    COLOR_GAME_OVER_BG,
    COLOR_GRADE_A,
    COLOR_GRADE_B,
    COLOR_GRADE_C,
    COLOR_GRADE_F,
    COLOR_TEXT,
    COLOR_ACCENT,
    COLOR_BTN_BORDER,
    BTN_WIDTH,
    BTN_HEIGHT,
    FONT_SIZE_TITLE,
    FONT_SIZE_BUTTON,
    FONT_SIZE_BODY,
)
import core.placeholder_sprites as placeholder_sprites
from core.save_manager import SaveManager
from core.sprite_animator import SpriteAnimator, get_walk_animation
from scenes.base_scene import BaseScene


# ---------------------------------------------------------------------------
# Derived constants
# ---------------------------------------------------------------------------
EXPLOSION_FRAME_DURATION_S = EXPLOSION_FRAME_DURATION / 1000.0
EXPLOSION_TOTAL_DURATION_S = EXPLOSION_TOTAL_DURATION / 1000.0

# Level-indexed lookup lists (index = level - 1)
_LEAK_TIMERS      = [LEAK_TIMER_EASY, LEAK_TIMER_MEDIUM, LEAK_TIMER_HARD]
_WORKER_INTERVALS = [WORKER_INTERVAL_EASY, WORKER_INTERVAL_MEDIUM, WORKER_INTERVAL_HARD]
_LEAK_MAX         = [1, 2, 3]


# ---------------------------------------------------------------------------
# _LeakSpot
# ---------------------------------------------------------------------------

class _LeakSpot:
    """A clickable gas-leak hazard with a countdown timer."""

    def __init__(self, pos: tuple[int, int], duration: float) -> None:
        self.pos = pos
        self.duration = duration
        self.remaining = duration
        self.hit_radius: int = LEAK_HIT_RADIUS

    def update(self, dt: float) -> bool:
        """Decrement timer by dt. Returns True when the timer has expired."""
        self.remaining = max(0.0, self.remaining - dt)
        return self.remaining == 0.0

    def contains_point(self, pt: tuple[int, int]) -> bool:
        """Return True if pt is within hit_radius of this leak's centre."""
        dx = pt[0] - self.pos[0]
        dy = pt[1] - self.pos[1]
        return math.sqrt(dx * dx + dy * dy) <= self.hit_radius

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the leak circle and countdown progress bar."""
        x, y = self.pos

        # Orange leak circle
        pygame.draw.circle(surface, COLOR_LEAK_CIRCLE, (x, y), LEAK_CIRCLE_RADIUS)

        # Countdown bar — centred below the circle
        bar_x = x - LEAK_TIMER_BAR_W // 2
        bar_y = y + LEAK_CIRCLE_RADIUS + 4

        # Background bar
        bg_rect = pygame.Rect(bar_x, bar_y, LEAK_TIMER_BAR_W, LEAK_TIMER_BAR_H)
        pygame.draw.rect(surface, COLOR_LEAK_TIMER_BG, bg_rect)

        # Fill bar (proportional to remaining/duration)
        ratio = self.remaining / self.duration if self.duration > 0 else 0.0
        fill_w = int(LEAK_TIMER_BAR_W * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_w, LEAK_TIMER_BAR_H)
            pygame.draw.rect(surface, COLOR_LEAK_TIMER_BAR, fill_rect)


# ---------------------------------------------------------------------------
# _DialogoBurbuja
# ---------------------------------------------------------------------------

class _DialogoBurbuja:
    def __init__(self, text: str, pos: tuple, duration: float) -> None:
        self.text = text
        self.pos = pos          # (x, y) centro del diálogo
        self.remaining = duration

    def update(self, dt: float) -> bool:
        """Decrementa timer. Retorna True cuando expira."""
        self.remaining = max(0.0, self.remaining - dt)
        return self.remaining <= 0.0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Dibuja texto sobre rectángulo semi-transparente redondeado."""
        text_surf = font.render(self.text, True, COLOR_DIALOG_TEXT)
        tw, th = text_surf.get_size()
        rect = pygame.Rect(
            self.pos[0] - tw // 2 - DIALOG_PADDING,
            self.pos[1] - th // 2 - DIALOG_PADDING,
            tw + DIALOG_PADDING * 2,
            th + DIALOG_PADDING * 2,
        )
        bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        r, g, b = COLOR_DIALOG_BG
        bg.fill((r, g, b, DIALOG_BG_ALPHA))
        surface.blit(bg, rect.topleft)
        pygame.draw.rect(surface, COLOR_DIALOG_TEXT, rect, 1, border_radius=DIALOG_BORDER_RADIUS)
        surface.blit(text_surf, text_surf.get_rect(center=self.pos))


# ---------------------------------------------------------------------------
# _DragState
# ---------------------------------------------------------------------------

class _DragState:
    def __init__(self, worker: "_Worker", origin_pos: tuple) -> None:
        self.worker = worker
        self.origin_pos = origin_pos
        self.cursor_pos: tuple = origin_pos


# ---------------------------------------------------------------------------
# _Worker
# ---------------------------------------------------------------------------

class _Worker:
    """A staging-area worker that must be assigned a respirator."""

    def __init__(self, queue_index: int) -> None:
        self.queue_index = queue_index
        self.protected: bool = False
        self.selected: bool = False
        self.state: str = "IDLE"
        self.pos: tuple = (0, 0)
        self.target = None
        self.animator: SpriteAnimator = get_walk_animation("chemical")

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw the worker sprite; highlight ring when selected; alert ring when ALERTA."""
        if self.selected:
            pygame.draw.circle(surface, COLOR_WORKER_SELECTED, (x, y), 20, 2)
        if self.state == "ALERTA":
            pygame.draw.circle(surface, COLOR_WORKER_ALERT, (x, y), WORKER_ALERT_RING_RADIUS, WORKER_ALERT_RING_WIDTH)
        frame = self.animator.get_current_frame()
        surface.blit(frame, frame.get_rect(center=(x, y)))


# ---------------------------------------------------------------------------
# Minigame step classes
# ---------------------------------------------------------------------------

class _ValveStep:
    step_type = "VALVE"

    def __init__(self, n_clicks: int) -> None:
        self.n_clicks = n_clicks
        self.progress = 0
        self.completed = False
        self.feedback = ""          # "correct" | "error" | ""
        self.feedback_timer = 0.0
        self._angles = [2 * math.pi * i / n_clicks for i in range(n_clicks)]

    def handle_event(self, event: pygame.event.Event, panel_rect: pygame.Rect) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        cx = panel_rect.centerx
        cy = panel_rect.centery - 20
        pos = event.pos
        expected_angle = self._angles[self.progress]
        tx = int(cx + VALVE_RADIUS * math.cos(expected_angle))
        ty = int(cy + VALVE_RADIUS * math.sin(expected_angle))
        dist = math.sqrt((pos[0] - tx)**2 + (pos[1] - ty)**2)
        if dist <= VALVE_TARGET_RADIUS:
            self.progress += 1
            self.feedback = "correct"
            self.feedback_timer = MINIGAME_FEEDBACK_DURATION
            if self.progress >= self.n_clicks:
                self.completed = True
        else:
            for i, angle in enumerate(self._angles):
                ox = int(cx + VALVE_RADIUS * math.cos(angle))
                oy = int(cy + VALVE_RADIUS * math.sin(angle))
                if math.sqrt((pos[0] - ox)**2 + (pos[1] - oy)**2) <= VALVE_TARGET_RADIUS:
                    self.progress = 0
                    self.feedback = "error"
                    self.feedback_timer = MINIGAME_FEEDBACK_DURATION
                    return

    def update(self, dt: float) -> None:
        if self.feedback_timer > 0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)
            if self.feedback_timer == 0.0:
                self.feedback = ""

    def reset(self) -> None:
        self.progress = 0
        self.completed = False
        self.feedback = ""
        self.feedback_timer = 0.0

    def draw(self, surface: pygame.Surface, panel_rect: pygame.Rect, font) -> None:
        cx = panel_rect.centerx
        cy = panel_rect.centery - 20
        pygame.draw.circle(surface, COLOR_MINIGAME_VALVE_POINT, (cx, cy), VALVE_RADIUS, 2)
        for i, angle in enumerate(self._angles):
            tx = int(cx + VALVE_RADIUS * math.cos(angle))
            ty = int(cy + VALVE_RADIUS * math.sin(angle))
            if i < self.progress:
                color = COLOR_MINIGAME_CORRECT
            elif i == self.progress:
                color = COLOR_MINIGAME_ERROR if self.feedback == "error" else COLOR_MINIGAME_STEP_ACTIVE
            else:
                color = COLOR_MINIGAME_VALVE_POINT
            pygame.draw.circle(surface, color, (tx, ty), VALVE_TARGET_RADIUS)
            lbl = font.render(str(i + 1), True, (13, 17, 23))
            surface.blit(lbl, lbl.get_rect(center=(tx, ty)))
        pygame.draw.circle(surface, COLOR_MINIGAME_BORDER, (cx, cy), 12)
        instr = font.render(f"Gira la válvula: {self.progress}/{self.n_clicks}", True, COLOR_MINIGAME_STEP_ACTIVE)
        surface.blit(instr, instr.get_rect(centerx=cx, top=panel_rect.bottom - 50))


class _ButtonStep:
    step_type = "BUTTON"

    def __init__(self, n_buttons: int) -> None:
        self.n_buttons = n_buttons
        self.next_expected = 1
        self.completed = False
        self.feedback = ""
        self.feedback_timer = 0.0
        self._button_rects: list = []

    def handle_event(self, event: pygame.event.Event, panel_rect: pygame.Rect) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        self._build_rects(panel_rect)
        for i, rect in enumerate(self._button_rects):
            if rect.collidepoint(event.pos):
                num = i + 1
                if num == self.next_expected:
                    self.next_expected += 1
                    self.feedback = "correct"
                    self.feedback_timer = MINIGAME_FEEDBACK_DURATION
                    if self.next_expected > self.n_buttons:
                        self.completed = True
                else:
                    self.next_expected = 1
                    self.feedback = "error"
                    self.feedback_timer = MINIGAME_FEEDBACK_DURATION
                return

    def update(self, dt: float) -> None:
        if self.feedback_timer > 0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)
            if self.feedback_timer == 0.0:
                self.feedback = ""

    def reset(self) -> None:
        self.next_expected = 1
        self.completed = False
        self.feedback = ""
        self.feedback_timer = 0.0

    def _build_rects(self, panel_rect: pygame.Rect) -> None:
        total_w = self.n_buttons * MINIGAME_BTN_W + (self.n_buttons - 1) * MINIGAME_BTN_GAP
        start_x = panel_rect.centerx - total_w // 2
        cy = panel_rect.centery - 10
        self._button_rects = [
            pygame.Rect(start_x + i * (MINIGAME_BTN_W + MINIGAME_BTN_GAP),
                        cy - MINIGAME_BTN_H // 2,
                        MINIGAME_BTN_W, MINIGAME_BTN_H)
            for i in range(self.n_buttons)
        ]

    def draw(self, surface: pygame.Surface, panel_rect: pygame.Rect, font) -> None:
        self._build_rects(panel_rect)
        for i, rect in enumerate(self._button_rects):
            num = i + 1
            if num < self.next_expected:
                color = COLOR_MINIGAME_CORRECT
            elif num == self.next_expected:
                color = COLOR_MINIGAME_ERROR if self.feedback == "error" else COLOR_MINIGAME_STEP_ACTIVE
            else:
                color = COLOR_MINIGAME_VALVE_POINT
            pygame.draw.rect(surface, color, rect, border_radius=6)
            lbl = font.render(str(num), True, (13, 17, 23))
            surface.blit(lbl, lbl.get_rect(center=rect.center))
        instr = font.render(f"Presiona en orden: siguiente → {self.next_expected}", True, COLOR_MINIGAME_STEP_ACTIVE)
        surface.blit(instr, instr.get_rect(centerx=panel_rect.centerx, top=panel_rect.bottom - 50))


_CABLE_COLORS = [
    (220, 60, 60),
    (60, 200, 100),
    (64, 128, 240),
    (240, 192, 64),
]


class _CableStep:
    step_type = "CABLE"

    def __init__(self, n_pairs: int) -> None:
        self.n_pairs = n_pairs
        self.connected = [False] * n_pairs
        self.selected_left: int | None = None
        self.completed = False
        self.feedback = ""
        self.feedback_timer = 0.0
        self._colors = [_CABLE_COLORS[i % len(_CABLE_COLORS)] for i in range(n_pairs)]
        self._left_rects: list = []
        self._right_rects: list = []
        import random as _random
        self._right_order = list(range(n_pairs))
        _random.shuffle(self._right_order)

    def handle_event(self, event: pygame.event.Event, panel_rect: pygame.Rect) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        self._build_rects(panel_rect)
        for i, rect in enumerate(self._left_rects):
            if rect.collidepoint(event.pos) and not self.connected[i]:
                self.selected_left = i
                return
        for j, rect in enumerate(self._right_rects):
            if rect.collidepoint(event.pos):
                actual_pair = self._right_order[j]
                if self.selected_left is not None:
                    if actual_pair == self.selected_left:
                        self.connected[self.selected_left] = True
                        self.feedback = "correct"
                        self.feedback_timer = MINIGAME_FEEDBACK_DURATION
                        self.selected_left = None
                        if all(self.connected):
                            self.completed = True
                    else:
                        self.feedback = "error"
                        self.feedback_timer = MINIGAME_FEEDBACK_DURATION
                        self.selected_left = None
                return

    def update(self, dt: float) -> None:
        if self.feedback_timer > 0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)
            if self.feedback_timer == 0.0:
                self.feedback = ""

    def reset(self) -> None:
        self.connected = [False] * self.n_pairs
        self.selected_left = None
        self.completed = False
        self.feedback = ""
        self.feedback_timer = 0.0

    def _build_rects(self, panel_rect: pygame.Rect) -> None:
        total_h = self.n_pairs * CABLE_ENDPOINT_RADIUS * 2 + (self.n_pairs - 1) * CABLE_ENDPOINT_GAP
        start_y = panel_rect.centery - total_h // 2 - 20
        lx = panel_rect.left + 80
        rx = panel_rect.right - 80
        self._left_rects = [
            pygame.Rect(lx - CABLE_ENDPOINT_RADIUS,
                        start_y + i * (CABLE_ENDPOINT_RADIUS * 2 + CABLE_ENDPOINT_GAP) - CABLE_ENDPOINT_RADIUS,
                        CABLE_ENDPOINT_RADIUS * 2, CABLE_ENDPOINT_RADIUS * 2)
            for i in range(self.n_pairs)
        ]
        self._right_rects = [
            pygame.Rect(rx - CABLE_ENDPOINT_RADIUS,
                        start_y + i * (CABLE_ENDPOINT_RADIUS * 2 + CABLE_ENDPOINT_GAP) - CABLE_ENDPOINT_RADIUS,
                        CABLE_ENDPOINT_RADIUS * 2, CABLE_ENDPOINT_RADIUS * 2)
            for i in range(self.n_pairs)
        ]

    def draw(self, surface: pygame.Surface, panel_rect: pygame.Rect, font) -> None:
        self._build_rects(panel_rect)
        lx = panel_rect.left + 80
        rx = panel_rect.right - 80
        total_h = self.n_pairs * CABLE_ENDPOINT_RADIUS * 2 + (self.n_pairs - 1) * CABLE_ENDPOINT_GAP
        start_y = panel_rect.centery - total_h // 2 - 20

        for i in range(self.n_pairs):
            ly = start_y + i * (CABLE_ENDPOINT_RADIUS * 2 + CABLE_ENDPOINT_GAP)
            color = self._colors[i]
            ep_color = COLOR_MINIGAME_CORRECT if self.connected[i] else (
                COLOR_MINIGAME_ERROR if self.selected_left == i else color)
            pygame.draw.circle(surface, ep_color, (lx, ly), CABLE_ENDPOINT_RADIUS)
            if self.selected_left == i:
                pygame.draw.circle(surface, COLOR_MINIGAME_STEP_ACTIVE, (lx, ly), CABLE_ENDPOINT_RADIUS + 3, 2)

        for j in range(self.n_pairs):
            ry = start_y + j * (CABLE_ENDPOINT_RADIUS * 2 + CABLE_ENDPOINT_GAP)
            actual_pair = self._right_order[j]
            color = self._colors[actual_pair]
            ep_color = COLOR_MINIGAME_CORRECT if self.connected[actual_pair] else color
            pygame.draw.circle(surface, ep_color, (rx, ry), CABLE_ENDPOINT_RADIUS)

        for i in range(self.n_pairs):
            if self.connected[i]:
                ly = start_y + i * (CABLE_ENDPOINT_RADIUS * 2 + CABLE_ENDPOINT_GAP)
                j = self._right_order.index(i)
                ry = start_y + j * (CABLE_ENDPOINT_RADIUS * 2 + CABLE_ENDPOINT_GAP)
                pygame.draw.line(surface, self._colors[i],
                                 (lx + CABLE_ENDPOINT_RADIUS, ly),
                                 (rx - CABLE_ENDPOINT_RADIUS, ry), 3)

        connected_count = sum(self.connected)
        instr = font.render(f"Conecta los cables: {connected_count}/{self.n_pairs}", True, COLOR_MINIGAME_STEP_ACTIVE)
        surface.blit(instr, instr.get_rect(centerx=panel_rect.centerx, top=panel_rect.bottom - 50))


# ---------------------------------------------------------------------------
# _RepairMinigame
# ---------------------------------------------------------------------------

class _RepairMinigame:
    """Panel overlay interactivo para reparar una fuga."""

    def __init__(self, leak, steps: list, timer_duration: float, zone_worker_count: int) -> None:
        self.leak = leak
        self.steps = steps
        self.current_step_index = 0
        self.timer = timer_duration
        self.max_timer = timer_duration
        self.zone_worker_count = zone_worker_count
        self.completed = False
        self.failed = False
        self.panel_rect = pygame.Rect(
            (SCREEN_WIDTH - MINIGAME_PANEL_W) // 2,
            (SCREEN_HEIGHT - MINIGAME_PANEL_H) // 2,
            MINIGAME_PANEL_W,
            MINIGAME_PANEL_H,
        )

    @property
    def current_step(self):
        return self.steps[self.current_step_index]

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.completed or self.failed:
            return
        self.current_step.handle_event(event, self.panel_rect)
        if self.current_step.completed:
            self.current_step_index += 1
            if self.current_step_index >= len(self.steps):
                self.completed = True

    def update(self, dt: float) -> None:
        if self.completed or self.failed:
            return
        self.current_step.update(dt)
        self.timer = max(0.0, self.timer - dt)
        if self.timer <= 0.0 and not self.completed:
            self.failed = True

    def draw(self, surface: pygame.Surface, font) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, COLOR_MINIGAME_BG, self.panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_MINIGAME_BORDER, self.panel_rect, 2, border_radius=8)

        total = len(self.steps)
        current_num = min(self.current_step_index + 1, total)
        step_label = font.render(
            f"Paso {current_num} de {total}  —  {self.current_step.step_type}",
            True, COLOR_MINIGAME_STEP_ACTIVE
        )
        surface.blit(step_label, step_label.get_rect(centerx=self.panel_rect.centerx, top=self.panel_rect.top + 12))

        dot_y = self.panel_rect.top + 38
        dot_spacing = 20
        total_dots_w = total * 12 + (total - 1) * dot_spacing
        dot_x = self.panel_rect.centerx - total_dots_w // 2
        for i in range(total):
            color = COLOR_MINIGAME_STEP_DONE if i < self.current_step_index else (
                COLOR_MINIGAME_STEP_ACTIVE if i == self.current_step_index else COLOR_MINIGAME_VALVE_POINT
            )
            pygame.draw.circle(surface, color, (dot_x + i * (12 + dot_spacing), dot_y), 6)

        bar_w = self.panel_rect.width - 40
        bar_x = self.panel_rect.left + 20
        bar_y = self.panel_rect.top + 54
        bar_h = 10
        pygame.draw.rect(surface, COLOR_MINIGAME_TIMER_BG, pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=4)
        timer_color = COLOR_MINIGAME_TIMER_BAR if self.timer > 3.0 else COLOR_MINIGAME_ERROR
        fill_w = int(bar_w * min(1.0, self.timer / self.max_timer))
        if fill_w > 0:
            pygame.draw.rect(surface, timer_color, pygame.Rect(bar_x, bar_y, fill_w, bar_h), border_radius=4)
        timer_lbl = font.render(f"{self.timer:.1f}s", True, COLOR_MINIGAME_STEP_ACTIVE)
        surface.blit(timer_lbl, timer_lbl.get_rect(right=self.panel_rect.right - 20, top=bar_y - 2))

        if self.zone_worker_count > 0:
            bonus_secs = self.zone_worker_count * MINIGAME_WORKER_BONUS_SECONDS
            bonus_lbl = font.render(f"+{bonus_secs:.0f}s bonus de trabajadores", True, COLOR_MINIGAME_BONUS)
            surface.blit(bonus_lbl, bonus_lbl.get_rect(left=self.panel_rect.left + 20, top=bar_y - 2))

        self.current_step.draw(surface, self.panel_rect, font)


# ---------------------------------------------------------------------------
# _ExplosionAnimation
# ---------------------------------------------------------------------------

class _ExplosionAnimation:
    """Three-frame expanding-ring explosion animation."""

    def __init__(self, pos: tuple[int, int]) -> None:
        self.pos = pos
        self.elapsed: float = 0.0
        self.frame: int = 0

    def update(self, dt: float) -> bool:
        """Advance animation. Returns True when the animation is complete."""
        self.elapsed += dt
        self.frame = min(2, int(self.elapsed / EXPLOSION_FRAME_DURATION_S))
        return self.elapsed >= EXPLOSION_TOTAL_DURATION_S

    def draw(self, surface: pygame.Surface) -> None:
        """Draw expanding concentric rings scaled to the current frame."""
        x, y = self.pos
        f = self.frame

        inner_r = 20 + f * 20
        outer_r = 35 + f * 25

        pygame.draw.circle(surface, COLOR_EXPLOSION_OUTER, (x, y), outer_r)
        pygame.draw.circle(surface, COLOR_EXPLOSION_INNER, (x, y), inner_r)


# ---------------------------------------------------------------------------
# _GameOverScreen
# ---------------------------------------------------------------------------

_GRADE_COLORS = {
    "A": COLOR_GRADE_A,
    "B": COLOR_GRADE_B,
    "C": COLOR_GRADE_C,
    "F": COLOR_GRADE_F,
}

_BTN_GAP = 20  # vertical gap between the two buttons


class _GameOverScreen:
    """Semi-transparent game-over overlay with results and navigation buttons."""

    def __init__(
        self,
        score: int,
        level: int,
        time_survived: float,
        grade: str,
        fonts: dict,
    ) -> None:
        self.score = score
        self.level = level
        self.time_survived = time_survived
        self.grade = grade
        self.fonts = fonts

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # "PLAY AGAIN" button — above centre
        self.play_again_rect = pygame.Rect(
            cx - BTN_WIDTH // 2,
            cy + 60,
            BTN_WIDTH,
            BTN_HEIGHT,
        )
        # "MAIN MENU" button — below "PLAY AGAIN"
        self.main_menu_rect = pygame.Rect(
            cx - BTN_WIDTH // 2,
            cy + 60 + BTN_HEIGHT + _BTN_GAP,
            BTN_WIDTH,
            BTN_HEIGHT,
        )

    def handle_click(self, pos: tuple[int, int]) -> str | None:
        """Return 'play_again', 'main_menu', or None."""
        if self.play_again_rect.collidepoint(pos):
            return "play_again"
        if self.main_menu_rect.collidepoint(pos):
            return "main_menu"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Render the game-over overlay."""
        # Semi-transparent dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        r, g, b = COLOR_GAME_OVER_BG
        overlay.fill((r, g, b, 210))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2

        # Title
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        title_surf = title_font.render("GAME OVER", True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(centerx=cx, centery=SCREEN_HEIGHT // 2 - 140))

        # Stats
        body_font = pygame.font.SysFont(None, FONT_SIZE_BODY + 4)
        stats = [
            f"Score: {self.score}",
            f"Level Reached: {self.level}",
            f"Time Survived: {int(self.time_survived)}s",
        ]
        for i, text in enumerate(stats):
            surf = body_font.render(text, True, COLOR_TEXT)
            surface.blit(surf, surf.get_rect(centerx=cx, centery=SCREEN_HEIGHT // 2 - 70 + i * 28))

        # Grade
        grade_color = _GRADE_COLORS.get(self.grade, COLOR_TEXT)
        grade_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        grade_surf = grade_font.render(f"Grade: {self.grade}", True, grade_color)
        surface.blit(grade_surf, grade_surf.get_rect(centerx=cx, centery=SCREEN_HEIGHT // 2 + 20))

        # Buttons
        btn_font = pygame.font.SysFont(None, FONT_SIZE_BUTTON)

        for rect, label in (
            (self.play_again_rect, "PLAY AGAIN"),
            (self.main_menu_rect, "MAIN MENU"),
        ):
            pygame.draw.rect(surface, COLOR_ACCENT, rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_BTN_BORDER, rect, 2, border_radius=4)
            lbl_surf = btn_font.render(label, True, (13, 17, 23))
            surface.blit(lbl_surf, lbl_surf.get_rect(center=rect.center))


# ---------------------------------------------------------------------------
# ChemicalPlantScene
# ---------------------------------------------------------------------------

class ChemicalPlantScene(BaseScene):
    """Main gameplay scene for the Chemical Plant factory."""

    def __init__(self, manager, input_handler, factory_data: dict) -> None:
        super().__init__(manager, input_handler)
        self.factory_data = factory_data

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self._phase = "PLAYING"
        self._level = 1
        self._level_timer = 0.0
        self._score = 0
        self._safety = 100.0
        self._production = 0.0
        self._leaks = []
        self._workers = []
        self._selected_worker = None
        self._worker_timer = WORKER_INTERVAL_EASY
        self._time_survived = 0.0
        self._level_up_timer = 0.0
        self._explosion = None
        self._game_over_screen = None
        self._explosion_hold_timer = 0.0
        self._save_manager = SaveManager()
        self._fonts = {}
        self._dialogs = []
        self._dialog_font = pygame.font.SysFont(None, FONT_SIZE_BODY)
        self._drag = None
        self._zone_workers = []  # workers assigned to factory zones
        self._minigame = None
        self._spawn_leak()

    def on_exit(self) -> None:
        self._phase = None
        self._level = None
        self._level_timer = None
        self._score = None
        self._safety = None
        self._production = None
        self._leaks = None
        self._workers = None
        self._selected_worker = None
        self._worker_timer = None
        self._time_survived = None
        self._level_up_timer = None
        self._explosion = None
        self._game_over_screen = None
        self._explosion_hold_timer = None
        self._save_manager = None
        self._fonts = None
        self._dialogs = None
        self._dialog_font = None
        self._drag = None
        self._zone_workers = None
        self._minigame = None

    # ------------------------------------------------------------------
    # Frame loop
    # ------------------------------------------------------------------

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self._drag is not None:
                self._cancel_drag()
                return
            if self._minigame is not None:
                self._close_minigame()
                return
            self.manager.pop_scene()
            return

        if event.type == pygame.MOUSEMOTION:
            if self._minigame is not None:
                return  # no procesar movimiento de drag durante minijuego
            if self._drag is not None:
                self._drag.cursor_pos = event.pos
            return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self._drag is not None:
            self._end_drag(event.pos)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self._phase == "GAME_OVER" and self._game_over_screen:
                action = self._game_over_screen.handle_click(pos)
                if action == "play_again":
                    from scenes.chemical_plant import ChemicalPlantScene
                    self.manager.replace_scene(ChemicalPlantScene(self.manager, self.input, self.factory_data))
                elif action == "main_menu":
                    self.manager.pop_scene()
                return

            if self._phase != "PLAYING":
                return

            # Si hay minijuego activo, delegar todos los eventos a él
            if self._minigame is not None:
                self._minigame.handle_event(event)
                return

            # Detect click on worker in staging — start drag
            for i, worker in enumerate(self._workers):
                wx = STAGING_AREA_RECT[0] + 60 + i * WORKER_SPACING
                wy = WORKER_STAGING_Y
                dist_sq = (pos[0] - wx) ** 2 + (pos[1] - wy) ** 2
                if dist_sq <= 20 ** 2:
                    self._start_drag(worker, (wx, wy))
                    return

            # Check leaks
            for leak in list(self._leaks):
                if leak.contains_point(pos):
                    self._open_minigame(leak)
                    return

            # Check workers in staging (select for button assignment)
            for i, worker in enumerate(self._workers):
                wx = STAGING_AREA_RECT[0] + 60 + i * WORKER_SPACING
                wy = WORKER_STAGING_Y
                dist_sq = (pos[0] - wx) ** 2 + (pos[1] - wy) ** 2
                if dist_sq <= 20 ** 2:
                    # Deselect previous
                    if self._selected_worker:
                        self._selected_worker.selected = False
                    worker.selected = True
                    self._selected_worker = worker
                    return

            # Check "Assign Respirator" button
            btn_rect = pygame.Rect(ASSIGN_BTN_X, ASSIGN_BTN_Y, ASSIGN_BTN_W, ASSIGN_BTN_H)
            if btn_rect.collidepoint(pos) and self._selected_worker is not None:
                wx, wy = self._selected_worker.pos
                self._selected_worker.protected = True
                self._selected_worker.selected = False
                self._score += SCORE_WORKER_PROTECTED
                self._workers.remove(self._selected_worker)
                self._zone_workers.append(self._selected_worker)
                self._create_dialog("¡Respirador asignado!", (wx, wy))
                self._selected_worker = None

    def update(self, dt: float) -> None:
        if self._phase == "PLAYING":
            # Tick leaks — check for expiry
            for leak in list(self._leaks):
                if self._minigame is not None and leak is self._minigame.leak:
                    continue  # timer pausado mientras el minijuego está abierto
                if leak.update(dt):
                    self._trigger_explosion(leak.pos)
                    return  # stop further updates this frame

            # Actualizar minijuego activo
            if self._minigame is not None:
                self._minigame.update(dt)
                if self._minigame is not None and self._minigame.completed:
                    self._complete_minigame()
                    return
                if self._minigame is not None and self._minigame.failed:
                    self._fail_minigame()
                    return

            # Worker spawn timer
            self._worker_timer -= dt
            if self._worker_timer <= 0:
                spawn_x = STAGING_AREA_RECT[0] + 60 + len(self._workers) * WORKER_SPACING
                self._create_dialog("¡Nuevo trabajador!", (spawn_x, WORKER_STAGING_Y - 30))
                self._workers.append(_Worker(len(self._workers)))
                self._worker_timer = _WORKER_INTERVALS[self._level - 1]

            # Unprotected worker exit: if queue > 3, front exits
            if len(self._workers) > 3:
                front = self._workers[0]
                if not front.protected:
                    self._safety = max(0.0, self._safety - SAFETY_PENALTY_UNPROTECTED_WORKER)
                    front_wx = STAGING_AREA_RECT[0] + 60
                    self._create_dialog("¡Trabajador sin protección!", (front_wx, WORKER_STAGING_Y))
                self._workers.pop(0)
                # Re-index remaining workers
                for i, w in enumerate(self._workers):
                    w.queue_index = i
                if self._safety <= 0:
                    self._trigger_explosion((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    return

            # Level progression
            self._level_timer += dt
            self._time_survived += dt
            if self._level < 3 and self._level_timer >= LEVEL_ADVANCE_DURATION:
                self._advance_level()

            # Level-up display timer
            if self._level_up_timer > 0:
                self._level_up_timer = max(0.0, self._level_up_timer - dt)

            # Production meter — zone workers boost production rate
            zone_bonus = 1.0 + 0.2 * len(self._zone_workers)
            self._production = min(100.0, self._production + PRODUCTION_RATE * zone_bonus * dt)

            # Update zone workers animation/alert
            for worker in self._zone_workers:
                self._update_worker_animation(worker, dt)
                self._update_worker_alert(worker)

            # Worker animation and alert
            for worker in self._workers:
                self._update_worker_animation(worker, dt)
                self._update_worker_alert(worker)

            # Update dialogs
            self._update_dialogs(dt)

        elif self._phase == "EXPLODING":
            if self._explosion and self._explosion.update(dt):
                self._explosion_hold_timer -= dt
                if self._explosion_hold_timer <= 0:
                    self._trigger_game_over()

        elif self._phase == "GAME_OVER":
            pass  # input handled in handle_event

    def draw(self, surface) -> None:
        # Guard: on_exit sets these to None; skip drawing if scene is being torn down
        if self._workers is None or self._leaks is None:
            return
        self._draw_floor(surface)
        self._draw_staging(surface)
        # Draw workers that are outside staging (EN_ZONA, ALERTA, CAMINANDO)
        for worker in self._workers:
            if worker.state in ("EN_ZONA", "ALERTA", "CAMINANDO"):
                worker.draw(surface, int(worker.pos[0]), int(worker.pos[1]))
        # Draw zone-assigned workers
        for worker in self._zone_workers:
            worker.draw(surface, int(worker.pos[0]), int(worker.pos[1]))
        for leak in self._leaks:
            leak.draw(surface)
        self._draw_hud(surface)
        if self._phase in ("EXPLODING", "GAME_OVER") and self._explosion:
            self._explosion.draw(surface)
        if self._phase == "GAME_OVER" and self._game_over_screen:
            self._game_over_screen.draw(surface)
        if self._level_up_timer and self._level_up_timer > 0:
            font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
            surf = font.render("LEVEL UP!", True, COLOR_LEVEL_UP_TEXT)
            surface.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        if self._phase == "EXPLODING":
            font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
            surf = font.render("EXPLOSION!", True, COLOR_EXPLOSION_TEXT)
            surface.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
        if self._minigame is not None:
            self._minigame.draw(surface, self._dialog_font)
        self._draw_drag(surface)
        self._draw_dialogs(surface)

    # ------------------------------------------------------------------
    # Private helpers — stubs
    # ------------------------------------------------------------------

    def _get_zone_for_pos(self, pos: tuple):
        """Retorna la zona (tuple) que contiene pos, o None."""
        for zone in [ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING]:
            if pygame.Rect(*zone).collidepoint(pos):
                return zone
        return None

    def _count_zone_workers(self, leak_pos: tuple) -> int:
        """Cuenta workers asignados a la zona que contiene leak_pos."""
        zone = self._get_zone_for_pos(leak_pos)
        if zone is None:
            return 0
        zone_center = (zone[0] + zone[2] // 2, zone[1] + zone[3] // 2)
        return sum(1 for w in self._zone_workers if w.target == zone_center)

    def _build_steps(self, level: int) -> list:
        """Retorna la lista de pasos para el nivel dado."""
        level = max(1, min(3, level))
        if level == 1:
            return [_ValveStep(VALVE_CLICKS_L1)]
        elif level == 2:
            return [_ValveStep(VALVE_CLICKS_L2), _ButtonStep(BUTTON_COUNT_L2)]
        else:
            return [_ValveStep(VALVE_CLICKS_L3), _ButtonStep(BUTTON_COUNT_L3), _CableStep(CABLE_PAIRS_L3)]

    def _calc_minigame_timer(self, level: int, zone_worker_count: int) -> float:
        """Calcula la duración efectiva del MinigameTimer con bonus y cap."""
        base = [MINIGAME_TIMER_EASY, MINIGAME_TIMER_MEDIUM, MINIGAME_TIMER_HARD]
        level = max(1, min(3, level))
        duration = base[level - 1] + zone_worker_count * MINIGAME_WORKER_BONUS_SECONDS
        return min(duration, MINIGAME_TIMER_MAX)

    def _open_minigame(self, leak) -> None:
        if self._minigame is not None:
            return  # solo un minijuego a la vez
        zone_worker_count = self._count_zone_workers(leak.pos)
        timer_duration = self._calc_minigame_timer(self._level, zone_worker_count)
        steps = self._build_steps(self._level)
        self._minigame = _RepairMinigame(leak, steps, timer_duration, zone_worker_count)

    def _complete_minigame(self) -> None:
        if self._minigame is None:
            return
        leak = self._minigame.leak
        self._close_minigame()
        if leak in self._leaks:
            self._leaks.remove(leak)
        self._score += SCORE_LEAK_RESOLVED
        self._create_dialog("¡Fuga sellada!", leak.pos)
        if len(self._leaks) < _LEAK_MAX[self._level - 1]:
            self._spawn_leak()

    def _fail_minigame(self) -> None:
        if self._minigame is None:
            return
        pos = self._minigame.leak.pos
        self._close_minigame()
        self._trigger_explosion(pos)

    def _close_minigame(self) -> None:
        self._minigame = None

    def _spawn_leak(self) -> None:
        if len(self._leaks) >= _LEAK_MAX[self._level - 1]:
            return
        zone = random.choice([ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING])
        zx, zy, zw, zh = zone
        x = random.randint(zx + 10, zx + zw - 10)
        y = random.randint(zy + 10, zy + zh - 10)
        duration = _LEAK_TIMERS[self._level - 1]
        self._leaks.append(_LeakSpot((x, y), duration))

    def _resolve_leak(self, leak) -> None:
        if leak in self._leaks:
            self._leaks.remove(leak)
        self._create_dialog("¡Fuga sellada!", leak.pos)
        self._score += SCORE_LEAK_RESOLVED
        # Spawn a replacement if below cap
        if len(self._leaks) < _LEAK_MAX[self._level - 1]:
            self._spawn_leak()

    def _advance_level(self) -> None:
        self._level += 1
        self._level_timer = 0.0
        self._level_up_timer = LEVEL_UP_DISPLAY_DURATION
        self._worker_timer = _WORKER_INTERVALS[self._level - 1]
        self._create_dialog(f"¡Nivel {self._level} iniciado!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))

    def _trigger_explosion(self, pos) -> None:
        for worker in self._workers:
            worker.state = "ALERTA"
        for worker in self._zone_workers:
            worker.state = "ALERTA"
        self._create_dialog("¡EXPLOSIÓN! ¡Evacúen!", pos)
        self._explosion = _ExplosionAnimation(pos)
        self._phase = "EXPLODING"
        self._explosion_hold_timer = EXPLOSION_TEXT_HOLD_DURATION

    def _trigger_game_over(self) -> None:
        grade = self._calc_grade()
        self._save_manager.save_result({
            "factory_id": "chemical",
            "score": self._score,
            "level_reached": self._level,
            "time_survived": self._time_survived,
            "grade": grade,
        })
        self._game_over_screen = _GameOverScreen(
            self._score, self._level, self._time_survived, grade, self._fonts
        )
        self._phase = "GAME_OVER"

    def _draw_hud(self, surface) -> None:
        # HUD strip background
        pygame.draw.rect(surface, COLOR_HUD_BG, pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT))

        font = pygame.font.SysFont(None, FONT_SIZE_BODY)

        # Safety bar
        safety_bar_x = 10
        pygame.draw.rect(surface, (40, 40, 40),
                         pygame.Rect(safety_bar_x, HUD_BAR_MARGIN, HUD_BAR_W, HUD_BAR_H))
        safety_fill_w = self._meter_bar_width(self._safety, HUD_BAR_W)
        if safety_fill_w > 0:
            pygame.draw.rect(surface, COLOR_SAFETY_BAR,
                             pygame.Rect(safety_bar_x, HUD_BAR_MARGIN, safety_fill_w, HUD_BAR_H))
        safety_lbl = font.render("Safety", True, COLOR_HUD_TEXT)
        surface.blit(safety_lbl, (safety_bar_x, HUD_BAR_MARGIN + HUD_BAR_H + 2))

        # Production bar
        prod_bar_x = 230
        pygame.draw.rect(surface, (40, 40, 40),
                         pygame.Rect(prod_bar_x, HUD_BAR_MARGIN, HUD_BAR_W, HUD_BAR_H))
        prod_fill_w = self._meter_bar_width(self._production, HUD_BAR_W)
        if prod_fill_w > 0:
            pygame.draw.rect(surface, COLOR_PRODUCTION_BAR,
                             pygame.Rect(prod_bar_x, HUD_BAR_MARGIN, prod_fill_w, HUD_BAR_H))
        prod_lbl = font.render("Production", True, COLOR_HUD_TEXT)
        surface.blit(prod_lbl, (prod_bar_x, HUD_BAR_MARGIN + HUD_BAR_H + 2))

        # Level / time / score text
        level_surf = font.render(f"Level {self._level}", True, COLOR_HUD_TEXT)
        surface.blit(level_surf, level_surf.get_rect(centerx=SCREEN_WIDTH // 2, centery=HUD_HEIGHT // 2 - 8))

        time_surf = font.render(f"Time: {int(self._time_survived)}s", True, COLOR_HUD_TEXT)
        surface.blit(time_surf, time_surf.get_rect(centerx=SCREEN_WIDTH // 2, centery=HUD_HEIGHT // 2 + 10))

        score_surf = font.render(f"Score: {self._score}", True, COLOR_HUD_TEXT)
        surface.blit(score_surf, score_surf.get_rect(right=SCREEN_WIDTH - 10, centery=HUD_HEIGHT // 2))

    def _draw_floor(self, surface) -> None:
        # Background fill
        surface.fill(COLOR_PLANT_BG)

        # Grid lines
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(surface, COLOR_PLANT_GRID, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(surface, COLOR_PLANT_GRID, (0, y), (SCREEN_WIDTH, y))

        font = pygame.font.SysFont(None, FONT_SIZE_BODY)

        # Zone rectangles with labels
        zones = [
            (ZONE_REACTOR, COLOR_ZONE_REACTOR, "REACTOR"),
            (ZONE_STORAGE, COLOR_ZONE_STORAGE, "STORAGE"),
            (ZONE_MIXING,  COLOR_ZONE_MIXING,  "MIXING"),
        ]
        for zone_rect, color, label in zones:
            rect = pygame.Rect(*zone_rect)
            pygame.draw.rect(surface, color, rect)
            lbl_surf = font.render(label, True, COLOR_ZONE_LABEL)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=rect.center))

    def _draw_staging(self, surface) -> None:
        # Staging area background
        staging_rect = pygame.Rect(*STAGING_AREA_RECT)
        pygame.draw.rect(surface, COLOR_STAGING_BG, staging_rect)

        font = pygame.font.SysFont(None, FONT_SIZE_BODY)

        # "STAGING AREA" label
        lbl_surf = font.render("STAGING AREA", True, COLOR_STAGING_LABEL)
        surface.blit(lbl_surf, lbl_surf.get_rect(center=staging_rect.center))

        # Workers
        for i, worker in enumerate(self._workers):
            if self._drag and worker is self._drag.worker:
                continue  # se dibuja en _draw_drag
            if worker.state in ("EN_ZONA", "ALERTA", "CAMINANDO"):
                continue  # se dibuja en draw() en su posición de zona
            wx = STAGING_AREA_RECT[0] + 60 + i * WORKER_SPACING
            wy = WORKER_STAGING_Y
            worker.pos = (wx, wy)
            worker.draw(surface, wx, wy)

        # "Assign Respirator" button
        btn_rect = pygame.Rect(ASSIGN_BTN_X, ASSIGN_BTN_Y, ASSIGN_BTN_W, ASSIGN_BTN_H)
        pygame.draw.rect(surface, COLOR_ASSIGN_BTN, btn_rect)
        btn_lbl = font.render("Assign Respirator", True, COLOR_ASSIGN_BTN_TEXT)
        surface.blit(btn_lbl, btn_lbl.get_rect(center=btn_rect.center))

    # ------------------------------------------------------------------
    # Dialog system (Task 5)
    # ------------------------------------------------------------------

    def _create_dialog(self, text: str, pos: tuple) -> None:
        adjusted_pos = pos
        for d in self._dialogs:
            if d.pos == adjusted_pos:
                adjusted_pos = (adjusted_pos[0], adjusted_pos[1] - DIALOG_VERTICAL_OFFSET)
        self._dialogs.append(_DialogoBurbuja(text, adjusted_pos, DIALOG_DISPLAY_DURATION))

    def _update_dialogs(self, dt: float) -> None:
        self._dialogs = [d for d in self._dialogs if not d.update(dt)]

    def _draw_dialogs(self, surface: pygame.Surface) -> None:
        for d in self._dialogs:
            d.draw(surface, self._dialog_font)

    # ------------------------------------------------------------------
    # Worker animation (Task 7)
    # ------------------------------------------------------------------

    def _update_worker_animation(self, worker: _Worker, dt: float) -> None:
        worker.animator.update(dt)
        if worker.state == "CAMINANDO":
            if worker.target is None:
                worker.state = "IDLE"
                return
            tx, ty = worker.target
            px, py = worker.pos
            dx, dy = tx - px, ty - py
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= WORKER_ARRIVE_THRESHOLD:
                worker.pos = worker.target
                worker.state = "EN_ZONA"
            else:
                step = WORKER_WALK_SPEED * dt
                ratio = step / dist
                worker.pos = (px + dx * ratio, py + dy * ratio)

    def _update_worker_alert(self, worker: _Worker) -> None:
        if worker.state not in ("EN_ZONA", "ALERTA"):
            return
        in_range = any(
            math.sqrt((leak.pos[0] - worker.pos[0])**2 + (leak.pos[1] - worker.pos[1])**2) < WORKER_ALERT_RADIUS
            for leak in self._leaks
        )
        if in_range:
            worker.state = "ALERTA"
        else:
            worker.state = "EN_ZONA"

    # ------------------------------------------------------------------
    # Drag-and-drop (Task 9)
    # ------------------------------------------------------------------

    def _start_drag(self, worker: _Worker, origin_pos: tuple) -> None:
        worker.selected = True
        self._drag = _DragState(worker, origin_pos)

    def _end_drag(self, drop_pos: tuple) -> None:
        if self._drag is None:
            return
        worker = self._drag.worker
        zones = [ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING]
        for zone in zones:
            if pygame.Rect(*zone).collidepoint(drop_pos):
                worker.protected = True
                worker.selected = False
                worker.state = "CAMINANDO"
                worker.target = (zone[0] + zone[2] // 2, zone[1] + zone[3] // 2)
                self._score += SCORE_WORKER_PROTECTED
                if worker in self._workers:
                    self._workers.remove(worker)
                # Workers in zones boost production and extend leak timers
                self._zone_workers.append(worker)
                self._create_dialog("¡Respirador asignado!", drop_pos)
                self._drag = None
                return
        # No zone found — return worker to staging
        worker.selected = False
        self._drag = None

    def _cancel_drag(self) -> None:
        if self._drag is None:
            return
        self._drag.worker.selected = False
        self._drag = None

    def _draw_drag(self, surface: pygame.Surface) -> None:
        if self._drag is None:
            return
        # Highlight hovered zone
        zones = [ZONE_REACTOR, ZONE_STORAGE, ZONE_MIXING]
        for zone in zones:
            if pygame.Rect(*zone).collidepoint(self._drag.cursor_pos):
                pygame.draw.rect(surface, COLOR_ZONE_DROP_HIGHLIGHT, pygame.Rect(*zone), 3)
        # Dashed line from origin to cursor
        ox, oy = self._drag.origin_pos
        cx, cy = self._drag.cursor_pos
        dx, dy = cx - ox, cy - oy
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            seg_total = DRAG_LINE_SEGMENT_LEN + DRAG_LINE_GAP_LEN
            steps = int(length / seg_total)
            for i in range(steps):
                t0 = i * seg_total / length
                t1 = (i * seg_total + DRAG_LINE_SEGMENT_LEN) / length
                t1 = min(t1, 1.0)
                p0 = (int(ox + dx * t0), int(oy + dy * t0))
                p1 = (int(ox + dx * t1), int(oy + dy * t1))
                pygame.draw.line(surface, COLOR_DRAG_LINE, p0, p1, 2)
        # Draw worker at cursor
        self._drag.worker.draw(surface, int(self._drag.cursor_pos[0]), int(self._drag.cursor_pos[1]))

    def _calc_grade(self) -> str:
        # Grade is based on a weighted combination of safety, score, and time survived.
        # Safety alone is not enough — a player who does nothing and dies in 3s
        # with safety=100 should not get an A.
        #
        # Formula:
        #   safety_score  = self._safety            (0–100)
        #   score_score   = min(100, self._score / 20)  (100 pts per resolved leak/worker ≈ 5 events = 100)
        #   time_score    = min(100, self._time_survived / 1.8)  (180s max = 100)
        #   weighted      = safety * 0.5 + score_score * 0.3 + time_score * 0.2
        safety_score = self._safety
        score_score  = min(100.0, self._score / 20.0)
        time_score   = min(100.0, self._time_survived / 1.8)
        weighted = safety_score * 0.5 + score_score * 0.3 + time_score * 0.2
        if weighted >= 85:
            return "A"
        if weighted >= 65:
            return "B"
        if weighted >= 45:
            return "C"
        return "F"

    def _meter_bar_width(self, pct: float, max_w: int) -> int:
        return int(pct / 100.0 * max_w)
