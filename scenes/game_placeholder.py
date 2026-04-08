import pygame
from scenes.base_scene import BaseScene
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG_GAME, COLOR_TEXT, COLOR_MUTED,
    FONT_SIZE_TITLE, FONT_SIZE_SUBTITLE,
)

_FACTORY_NAMES = {
    "chemical":   "Chemical Plant",
    "automotive": "Auto Assembly",
    "warehouse":  "Warehouse",
}

# Factories that are not yet playable
_COMING_SOON = {"automotive", "warehouse"}


class GamePlaceholderScene(BaseScene):
    def __init__(self, manager, input_handler, factory_id: str = "chemical"):
        super().__init__(manager, input_handler)
        self._factory_id = factory_id

    def on_enter(self):
        font_title = pygame.font.SysFont(None, FONT_SIZE_TITLE, bold=True)
        font_sub   = pygame.font.SysFont(None, FONT_SIZE_SUBTITLE)

        name = _FACTORY_NAMES.get(self._factory_id, self._factory_id.title())
        cx   = SCREEN_WIDTH // 2
        cy   = SCREEN_HEIGHT // 2

        self._surfs = []

        if self._factory_id in _COMING_SOON:
            self._surfs.append((
                font_title.render(name, True, COLOR_TEXT),
                (cx, cy - 40),
            ))
            self._surfs.append((
                font_sub.render("Coming Soon", True, COLOR_MUTED),
                (cx, cy + 20),
            ))
        else:
            self._surfs.append((
                font_title.render(name, True, COLOR_TEXT),
                (cx, cy - 20),
            ))
            self._surfs.append((
                font_sub.render("GAME SCENE — Work in Progress", True, COLOR_MUTED),
                (cx, cy + 40),
            ))

    def on_exit(self):
        self._surfs = None

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        if self.input.is_key_just_pressed(pygame.K_ESCAPE):
            self.manager.pop_scene()

    def draw(self, surface: pygame.Surface):
        surface.fill(COLOR_BG_GAME)
        for surf, (cx, cy) in self._surfs:
            rect = surf.get_rect(center=(cx, cy))
            surface.blit(surf, rect)
