"""scenes/factory_select.py
Factory selection screen — 3 cards (Chemical, Automotive, Warehouse).
Worker sprites are drawn with core.placeholder_sprites.draw_worker.
"""
import pygame
from scenes.base_scene import BaseScene
from core.placeholder_sprites import draw_worker
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_TEXT, COLOR_MUTED, COLOR_ACCENT,
    COLOR_BTN_BORDER, COLOR_BTN_HOVER,
    FONT_SIZE_TITLE, FONT_SIZE_BUTTON, FONT_SIZE_BODY, FONT_SIZE_SMALL,
    BTN_BORDER_WIDTH,
    CARD_W, CARD_H, CARD_GAP, CARD_TOP_OFFSET, WORKER_SCALE,
    SELECT_BTN_W, SELECT_BTN_H, SELECT_BTN_MARGIN,
    COLOR_DIFFICULTY_EASY, COLOR_DIFFICULTY_MEDIUM, COLOR_DIFFICULTY_HARD,
)

# ── Factory definitions ────────────────────────────────────────────────────────
FACTORIES = [
    {
        "id":          "chemical",
        "name":        "Chemical Plant",
        "abbrev":      "CH",
        "color":       (180, 60, 60),
        "difficulty":  "HARD",
        "description": "Hazardous materials, strict PPE required.",
        "hazards":     ["Chemical spills", "Toxic fumes", "PPE violations"],
    },
    {
        "id":          "automotive",
        "name":        "Auto Assembly",
        "abbrev":      "AU",
        "color":       (60, 100, 180),
        "difficulty":  "MEDIUM",
        "description": "Heavy machinery, noise & ergonomics.",
        "hazards":     ["Pinch points", "Noise exposure", "Ergonomic strain"],
    },
    {
        "id":          "warehouse",
        "name":        "Warehouse",
        "abbrev":      "WH",
        "color":       (60, 160, 80),
        "difficulty":  "EASY",
        "description": "Forklift traffic, slip & trip hazards.",
        "hazards":     ["Forklift collisions", "Wet floors", "Unsecured loads"],
    },
]

_DIFF_COLORS = {
    "EASY":   COLOR_DIFFICULTY_EASY,
    "MEDIUM": COLOR_DIFFICULTY_MEDIUM,
    "HARD":   COLOR_DIFFICULTY_HARD,
}


class FactorySelectScene(BaseScene):
    def on_enter(self):
        self._font_title = pygame.font.SysFont(None, FONT_SIZE_TITLE, bold=True)
        self._font_btn   = pygame.font.SysFont(None, FONT_SIZE_BUTTON, bold=True)
        self._font_body  = pygame.font.SysFont(None, FONT_SIZE_BODY)
        self._font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL, bold=True)

        card_top = (SCREEN_HEIGHT - CARD_H) // 2 + CARD_TOP_OFFSET
        total_w = len(FACTORIES) * CARD_W + (len(FACTORIES) - 1) * CARD_GAP
        start_x = (SCREEN_WIDTH - total_w) // 2

        self._cards = []
        for i, fac in enumerate(FACTORIES):
            card_x = start_x + i * (CARD_W + CARD_GAP)
            self._cards.append(_FactoryCard(
                fac, card_x, card_top, CARD_W, CARD_H,
                self._font_btn, self._font_body, self._font_small,
            ))

        self._title_surf = self._font_title.render("SELECT FACTORY", True, COLOR_TEXT)

    def on_exit(self):
        self._cards = None
        self._title_surf = None
        self._font_title = None
        self._font_btn = None
        self._font_body = None
        self._font_small = None

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        mouse_pos = self.input.get_mouse_pos()
        clicked   = self.input.is_mouse_clicked()

        for card in self._cards:
            card.update(mouse_pos)
            if card.is_select_clicked(mouse_pos, clicked):
                if card.factory_id == "chemical":
                    from scenes.chemical_plant import ChemicalPlantScene
                    factory_data = next(f for f in FACTORIES if f["id"] == card.factory_id)
                    self.manager.push_scene(ChemicalPlantScene(self.manager, self.input, factory_data))
                else:
                    from scenes.game_placeholder import GamePlaceholderScene
                    self.manager.push_scene(GamePlaceholderScene(self.manager, self.input, card.factory_id))
                break  # only process one click per frame

        if self.input.is_key_just_pressed(pygame.K_ESCAPE):
            self.manager.pop_scene()

    def draw(self, surface: pygame.Surface):
        surface.fill(COLOR_BG)

        # Title
        title_rect = self._title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))
        surface.blit(self._title_surf, title_rect)

        for card in self._cards:
            card.draw(surface)


# ── Card helper class ──────────────────────────────────────────────────────────

class _FactoryCard:
    _CARD_BG = (22, 27, 34)

    def __init__(self, fac: dict, x: int, y: int, w: int, h: int,
                 font_btn, font_body, font_small):
        self._fac        = fac
        self._rect       = pygame.Rect(x, y, w, h)
        self._font_btn   = font_btn
        self._font_body  = font_body
        self._font_small = font_small
        self._hovered    = False

        # Pre-render the card surface (static parts)
        self._surface = self._build_surface(w, h)

        # SELECT button rect (in screen coords) — Task 3.1
        btn_x = x + (w - SELECT_BTN_W) // 2
        btn_y = y + h - SELECT_BTN_H - SELECT_BTN_MARGIN
        self._btn_rect = pygame.Rect(btn_x, btn_y, SELECT_BTN_W, SELECT_BTN_H)

    # ── build static card surface ──────────────────────────────────────────────
    def _build_surface(self, w: int, h: int) -> pygame.Surface:
        surf = pygame.Surface((w, h))
        surf.fill(self._CARD_BG)

        fac = self._fac
        cx  = w // 2

        # Worker sprite — centred in upper ~40% of card
        worker_area_h = int(h * 0.42)
        worker_cy     = worker_area_h // 2
        draw_worker(surf, cx, worker_cy, fac["id"], scale=WORKER_SCALE)

        # Divider line
        div_y = worker_area_h + 4
        pygame.draw.line(surf, COLOR_BTN_BORDER, (16, div_y), (w - 16, div_y), 1)

        # Factory name — bold, COLOR_TEXT, FONT_SIZE_BODY
        name_font = pygame.font.SysFont(None, FONT_SIZE_BODY, bold=True)
        name_surf = name_font.render(fac["name"].upper(), True, COLOR_TEXT)
        name_rect = name_surf.get_rect(centerx=cx, top=div_y + 10)
        surf.blit(name_surf, name_rect)

        # Difficulty badge — _DIFF_COLORS, FONT_SIZE_SMALL bold
        diff_font = pygame.font.SysFont(None, FONT_SIZE_SMALL, bold=True)
        diff_surf = diff_font.render(fac["difficulty"], True, _DIFF_COLORS[fac["difficulty"]])
        diff_rect = diff_surf.get_rect(centerx=cx, top=name_rect.bottom + 6)
        surf.blit(diff_surf, diff_rect)

        # Description — COLOR_MUTED, FONT_SIZE_SMALL
        desc_font = pygame.font.SysFont(None, FONT_SIZE_SMALL)
        desc_y    = diff_rect.bottom + 10
        for line in fac["description"].split("\n"):
            line_surf = desc_font.render(line, True, COLOR_MUTED)
            line_rect = line_surf.get_rect(centerx=cx, top=desc_y)
            surf.blit(line_surf, line_rect)
            desc_y = line_rect.bottom + 4

        # Hazard list — each prefixed with •, COLOR_MUTED, FONT_SIZE_SMALL
        desc_y += 4
        for hazard in fac["hazards"]:
            h_surf = desc_font.render(f"\u2022 {hazard}", True, COLOR_MUTED)
            h_rect = h_surf.get_rect(centerx=cx, top=desc_y)
            surf.blit(h_surf, h_rect)
            desc_y = h_rect.bottom + 2

        return surf

    @property
    def factory_id(self) -> str:
        return self._fac["id"]

    def update(self, mouse_pos: tuple):
        self._hovered = self._btn_rect.collidepoint(mouse_pos)

    def is_select_clicked(self, mouse_pos: tuple, clicked: bool) -> bool:
        return clicked and self._btn_rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface):
        # Card background + static content
        surface.blit(self._surface, self._rect.topleft)

        # Card border — COLOR_ACCENT when hovered, COLOR_BTN_BORDER otherwise
        border_color = COLOR_ACCENT if self._hovered else COLOR_BTN_BORDER
        pygame.draw.rect(surface, border_color, self._rect, BTN_BORDER_WIDTH)

        # SELECT button (drawn live so hover state updates)
        btn_color = COLOR_BTN_HOVER if self._hovered else COLOR_BTN_BORDER
        txt_color = COLOR_BG        if self._hovered else COLOR_TEXT
        pygame.draw.rect(surface, btn_color, self._btn_rect)
        label = self._font_btn.render("SELECT", True, txt_color)
        label_rect = label.get_rect(center=self._btn_rect.center)
        surface.blit(label, label_rect)
