import pygame
from scenes.base_scene import BaseScene
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_TEXT, COLOR_MUTED, COLOR_ACCENT,
    COLOR_BTN_BORDER, COLOR_BTN_HOVER,
    FONT_SIZE_TITLE, FONT_SIZE_BODY, FONT_SIZE_BUTTON, FONT_SIZE_TABLE,
    BTN_WIDTH, BTN_HEIGHT, BTN_BORDER_WIDTH,
)

# Control table data
KEYBOARD_CONTROLS = [
    ("WASD / Arrow keys", "Move camera / pan view"),
    ("I",                 "Toggle Inspection Mode"),
    ("E",                 "Interact / confirm action"),
    ("ESC",               "Pause / back to menu"),
    ("SPACE",             "Activate alarm (emergency)"),
]

MOUSE_CONTROLS = [
    ("Left click",      "Select worker / hazard / machine"),
    ("Right click",     "Deselect / cancel action"),
    ("Scroll wheel",    "Zoom in / out"),
    ("Click + drag",    "Assign PPE to worker"),
]

ROW_HEIGHT = 34
COL_HEADER_H = 30
TABLE_TOP_OFFSET = 160   # px below title
COLUMN_WIDTH = 280
KEY_COL_W = 160
DIVIDER_X_OFFSET = 60   # gap between the two tables


class ControlsScene(BaseScene):
    def on_enter(self):
        self._font_title = pygame.font.SysFont(None, FONT_SIZE_TITLE, bold=True)
        self._font_header = pygame.font.SysFont(None, FONT_SIZE_BODY, bold=True)
        self._font_table = pygame.font.SysFont(None, FONT_SIZE_TABLE)
        self._font_btn = pygame.font.SysFont(None, FONT_SIZE_BUTTON)

        cx = SCREEN_WIDTH // 2
        # Back button near bottom
        self._back_rect = pygame.Rect(0, 0, BTN_WIDTH, BTN_HEIGHT)
        self._back_rect.center = (cx, SCREEN_HEIGHT - 70)
        self._back_hovered = False

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        mouse_pos = self.input.get_mouse_pos()
        self._back_hovered = self._back_rect.collidepoint(mouse_pos)

        if self.input.is_key_just_pressed(pygame.K_ESCAPE):
            self.manager.pop_scene()

        if self.input.is_mouse_clicked() and self._back_hovered:
            self.manager.pop_scene()

    def draw(self, surface: pygame.Surface):
        surface.fill(COLOR_BG)

        cx = SCREEN_WIDTH // 2
        title_surf = self._font_title.render("CONTROLS", True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(center=(cx, 70)))

        # Divider line under title
        pygame.draw.line(surface, COLOR_BTN_BORDER, (80, 110), (SCREEN_WIDTH - 80, 110), 1)

        # Two-column layout
        left_x = cx - COLUMN_WIDTH - DIVIDER_X_OFFSET
        right_x = cx + DIVIDER_X_OFFSET

        self._draw_table(
            surface, "Keyboard", KEYBOARD_CONTROLS,
            left_x, TABLE_TOP_OFFSET, KEY_COL_W, COLUMN_WIDTH
        )
        self._draw_table(
            surface, "Mouse", MOUSE_CONTROLS,
            right_x, TABLE_TOP_OFFSET, KEY_COL_W, COLUMN_WIDTH
        )

        # Vertical divider between columns
        div_x = cx
        pygame.draw.line(
            surface, COLOR_BTN_BORDER,
            (div_x, TABLE_TOP_OFFSET - 10),
            (div_x, TABLE_TOP_OFFSET + max(len(KEYBOARD_CONTROLS), len(MOUSE_CONTROLS)) * ROW_HEIGHT + COL_HEADER_H + 10),
            1
        )

        # Back button
        border_color = COLOR_BTN_HOVER if self._back_hovered else COLOR_BTN_BORDER
        text_color = COLOR_ACCENT if self._back_hovered else COLOR_TEXT
        pygame.draw.rect(surface, border_color, self._back_rect, BTN_BORDER_WIDTH)
        back_surf = self._font_btn.render("BACK", True, text_color)
        surface.blit(back_surf, back_surf.get_rect(center=self._back_rect.center))

    def _draw_table(
        self, surface: pygame.Surface, heading: str,
        rows: list[tuple[str, str]], x: int, y: int,
        key_col_w: int, total_w: int
    ):
        # Section heading
        head_surf = self._font_header.render(heading, True, COLOR_ACCENT)
        surface.blit(head_surf, (x, y))
        y += COL_HEADER_H

        # Column headers
        key_h = self._font_table.render("Key / Action", True, COLOR_MUTED)
        val_h = self._font_table.render("Result", True, COLOR_MUTED)
        surface.blit(key_h, (x, y))
        surface.blit(val_h, (x + key_col_w + 16, y))
        y += ROW_HEIGHT - 6

        # Thin header underline
        pygame.draw.line(surface, COLOR_BTN_BORDER, (x, y), (x + total_w, y), 1)
        y += 8

        for key_label, action_label in rows:
            key_surf = self._font_table.render(key_label, True, COLOR_TEXT)
            act_surf = self._font_table.render(action_label, True, COLOR_MUTED)
            surface.blit(key_surf, (x, y))
            surface.blit(act_surf, (x + key_col_w + 16, y))
            y += ROW_HEIGHT
