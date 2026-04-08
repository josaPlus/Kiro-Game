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
# _Worker
# ---------------------------------------------------------------------------

class _Worker:
    """A staging-area worker that must be assigned a respirator."""

    def __init__(self, queue_index: int) -> None:
        self.queue_index = queue_index
        self.protected: bool = False
        self.selected: bool = False

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw the worker sprite; highlight ring when selected."""
        if self.selected:
            pygame.draw.circle(surface, COLOR_WORKER_SELECTED, (x, y), 20, 2)
        placeholder_sprites.draw_worker(surface, x, y, factory_id="chemical")


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

    # ------------------------------------------------------------------
    # Frame loop
    # ------------------------------------------------------------------

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.pop_scene()
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

            # Check leaks
            for leak in list(self._leaks):
                if leak.contains_point(pos):
                    self._resolve_leak(leak)
                    return

            # Check workers in staging
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
                self._selected_worker.protected = True
                self._selected_worker.selected = False
                self._score += SCORE_WORKER_PROTECTED
                self._workers.remove(self._selected_worker)
                self._selected_worker = None

    def update(self, dt: float) -> None:
        if self._phase == "PLAYING":
            # Tick leaks — check for expiry
            for leak in list(self._leaks):
                if leak.update(dt):
                    self._trigger_explosion(leak.pos)
                    return  # stop further updates this frame

            # Worker spawn timer
            self._worker_timer -= dt
            if self._worker_timer <= 0:
                self._workers.append(_Worker(len(self._workers)))
                self._worker_timer = _WORKER_INTERVALS[self._level - 1]

            # Unprotected worker exit: if queue > 3, front exits
            if len(self._workers) > 3:
                front = self._workers[0]
                if not front.protected:
                    self._safety = max(0.0, self._safety - SAFETY_PENALTY_UNPROTECTED_WORKER)
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

            # Production meter
            self._production = min(100.0, self._production + PRODUCTION_RATE * dt)

        elif self._phase == "EXPLODING":
            if self._explosion and self._explosion.update(dt):
                self._explosion_hold_timer -= dt
                if self._explosion_hold_timer <= 0:
                    self._trigger_game_over()

        elif self._phase == "GAME_OVER":
            pass  # input handled in handle_event

    def draw(self, surface) -> None:
        self._draw_floor(surface)
        self._draw_staging(surface)
        for leak in self._leaks:
            leak.draw(surface)
        # draw workers (handled inside _draw_staging)
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

    # ------------------------------------------------------------------
    # Private helpers — stubs
    # ------------------------------------------------------------------

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
        self._score += SCORE_LEAK_RESOLVED
        # Spawn a replacement if below cap
        if len(self._leaks) < _LEAK_MAX[self._level - 1]:
            self._spawn_leak()

    def _advance_level(self) -> None:
        self._level += 1
        self._level_timer = 0.0
        self._level_up_timer = LEVEL_UP_DISPLAY_DURATION
        self._worker_timer = _WORKER_INTERVALS[self._level - 1]

    def _trigger_explosion(self, pos) -> None:
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
            wx = STAGING_AREA_RECT[0] + 60 + i * WORKER_SPACING
            wy = WORKER_STAGING_Y
            worker.draw(surface, wx, wy)

        # "Assign Respirator" button
        btn_rect = pygame.Rect(ASSIGN_BTN_X, ASSIGN_BTN_Y, ASSIGN_BTN_W, ASSIGN_BTN_H)
        pygame.draw.rect(surface, COLOR_ASSIGN_BTN, btn_rect)
        btn_lbl = font.render("Assign Respirator", True, COLOR_ASSIGN_BTN_TEXT)
        surface.blit(btn_lbl, btn_lbl.get_rect(center=btn_rect.center))

    def _calc_grade(self) -> str:
        s = self._safety
        if s >= 90:
            return "A"
        if s >= 70:
            return "B"
        if s >= 50:
            return "C"
        return "F"

    def _meter_bar_width(self, pct: float, max_w: int) -> int:
        return int(pct / 100.0 * max_w)
