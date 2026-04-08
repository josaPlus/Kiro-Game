import pygame
import sys
from scenes.base_scene import BaseScene
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_TEXT, COLOR_MUTED, COLOR_ACCENT,
    COLOR_BTN_BORDER, COLOR_BTN_HOVER,
    FONT_SIZE_TITLE, FONT_SIZE_SUBTITLE, FONT_SIZE_BUTTON, FONT_SIZE_SMALL,
    BTN_WIDTH, BTN_HEIGHT, BTN_BORDER_WIDTH, BUTTON_GAP,
    TITLE_Y_RATIO, SUBTITLE_OFFSET, BUTTON_START_OFFSET,
    VERSION_LABEL,
)


class Button:
    def __init__(self, label: str, cx: int, cy: int, font: pygame.font.Font):
        self.label = label
        self.rect = pygame.Rect(0, 0, BTN_WIDTH, BTN_HEIGHT)
        self.rect.center = (cx, cy)
        self.font = font
        self.hovered = False

    def update(self, mouse_pos: tuple[int, int]):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface):
        border_color = COLOR_BTN_HOVER if self.hovered else COLOR_BTN_BORDER
        text_color = COLOR_ACCENT if self.hovered else COLOR_TEXT
        pygame.draw.rect(surface, border_color, self.rect, BTN_BORDER_WIDTH)
        text_surf = self.font.render(self.label, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos: tuple[int, int], clicked: bool) -> bool:
        return clicked and self.rect.collidepoint(mouse_pos)


class MainMenuScene(BaseScene):
    def on_enter(self):
        self._font_title = pygame.font.SysFont(None, FONT_SIZE_TITLE, bold=True)
        self._font_subtitle = pygame.font.SysFont(None, FONT_SIZE_SUBTITLE)
        self._font_btn = pygame.font.SysFont(None, FONT_SIZE_BUTTON)
        self._font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)

        cx = SCREEN_WIDTH // 2
        title_y = int(SCREEN_HEIGHT * TITLE_Y_RATIO)
        btn_y = title_y + BUTTON_START_OFFSET

        self._buttons = [
            Button("START GAME", cx, btn_y, self._font_btn),
            Button("CONTROLS",   cx, btn_y + BUTTON_GAP, self._font_btn),
            Button("QUIT",       cx, btn_y + BUTTON_GAP * 2, self._font_btn),
        ]

        self._title_surf = self._font_title.render("FACTORY SAFETY INSPECTOR", True, COLOR_TEXT)
        self._subtitle_surf = self._font_subtitle.render(
            "Safety & Hygiene Coordinator Simulator", True, COLOR_MUTED
        )
        self._version_surf = self._font_small.render(VERSION_LABEL, True, COLOR_MUTED)

    def handle_event(self, event: pygame.event.Event):
        pass  # Input handled via InputHandler in update()

    def update(self, dt: float):
        mouse_pos = self.input.get_mouse_pos()
        clicked = self.input.is_mouse_clicked()

        for btn in self._buttons:
            btn.update(mouse_pos)

        if self._buttons[0].is_clicked(mouse_pos, clicked):
            from scenes.factory_select import FactorySelectScene
            self.manager.push_scene(FactorySelectScene(self.manager, self.input))

        elif self._buttons[1].is_clicked(mouse_pos, clicked):
            from scenes.controls_scene import ControlsScene
            self.manager.push_scene(ControlsScene(self.manager, self.input))

        elif self._buttons[2].is_clicked(mouse_pos, clicked):
            pygame.quit()
            sys.exit()

    def draw(self, surface: pygame.Surface):
        surface.fill(COLOR_BG)

        cx = SCREEN_WIDTH // 2
        title_y = int(SCREEN_HEIGHT * TITLE_Y_RATIO)

        # Title
        title_rect = self._title_surf.get_rect(center=(cx, title_y))
        surface.blit(self._title_surf, title_rect)

        # Subtitle
        sub_rect = self._subtitle_surf.get_rect(center=(cx, title_y + SUBTITLE_OFFSET))
        surface.blit(self._subtitle_surf, sub_rect)

        # Buttons
        for btn in self._buttons:
            btn.draw(surface)

        # Version label — bottom right
        ver_rect = self._version_surf.get_rect(
            bottomright=(SCREEN_WIDTH - 12, SCREEN_HEIGHT - 10)
        )
        surface.blit(self._version_surf, ver_rect)
