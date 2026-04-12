"""scenes/pause_scene.py
Pause overlay — pushed on top of any gameplay scene.
Provides: Resume, Settings (volume slider), Main Menu.
"""
from __future__ import annotations
import pygame
from scenes.base_scene import BaseScene
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_TEXT, COLOR_MUTED, COLOR_ACCENT,
    COLOR_BTN_BORDER, COLOR_BTN_HOVER,
    FONT_SIZE_TITLE, FONT_SIZE_BUTTON, FONT_SIZE_BODY, FONT_SIZE_SMALL,
    BTN_WIDTH, BTN_HEIGHT, BTN_BORDER_WIDTH,
    COLOR_PAUSE_OVERLAY, PAUSE_OVERLAY_ALPHA,
    COLOR_PAUSE_PANEL, COLOR_PAUSE_BORDER,
    PAUSE_PANEL_W, PAUSE_PANEL_H,
)
from core.music_manager import MusicManager


class PauseScene(BaseScene):
    """Semi-transparent pause overlay pushed over the active gameplay scene."""

    def on_enter(self) -> None:
        self._music = MusicManager.instance()
        self._music.pause()

        self._font_title = pygame.font.SysFont(None, FONT_SIZE_TITLE, bold=True)
        self._font_btn   = pygame.font.SysFont(None, FONT_SIZE_BUTTON)
        self._font_body  = pygame.font.SysFont(None, FONT_SIZE_BODY)
        self._font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)

        cx = SCREEN_WIDTH // 2
        panel_top = (SCREEN_HEIGHT - PAUSE_PANEL_H) // 2
        self._panel_rect = pygame.Rect(cx - PAUSE_PANEL_W // 2, panel_top, PAUSE_PANEL_W, PAUSE_PANEL_H)

        btn_x = cx - BTN_WIDTH // 2
        btn_y = panel_top + 90

        self._btn_resume    = pygame.Rect(btn_x, btn_y,              BTN_WIDTH, BTN_HEIGHT)
        self._btn_main_menu = pygame.Rect(btn_x, btn_y + 70,         BTN_WIDTH, BTN_HEIGHT)

        # Volume slider
        slider_y = btn_y + 160
        self._slider_track = pygame.Rect(cx - 120, slider_y, 240, 8)
        self._dragging_slider = False

        # Mute button
        self._btn_mute = pygame.Rect(cx - 60, slider_y + 28, 120, 32)

        # Overlay surface (reused each frame)
        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        r, g, b = COLOR_PAUSE_OVERLAY
        self._overlay.fill((r, g, b, PAUSE_OVERLAY_ALPHA))

    def on_exit(self) -> None:
        self._music.resume()
        self._font_title = None
        self._font_btn   = None
        self._font_body  = None
        self._font_small = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.pop_scene()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self._btn_resume.collidepoint(pos):
                self.manager.pop_scene()
            elif self._btn_main_menu.collidepoint(pos):
                # Pop pause, then pop gameplay, landing on main menu
                self.manager.pop_scene()
                self.manager.pop_scene()
            elif self._btn_mute.collidepoint(pos):
                self._music.toggle_mute()
            elif self._slider_track.collidepoint(pos):
                self._dragging_slider = True
                self._set_volume_from_x(pos[0])

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging_slider = False

        if event.type == pygame.MOUSEMOTION and self._dragging_slider:
            self._set_volume_from_x(event.pos[0])

    def _set_volume_from_x(self, x: int) -> None:
        ratio = (x - self._slider_track.left) / self._slider_track.width
        self._music.set_volume(max(0.0, min(1.0, ratio)))

    def update(self, dt: float) -> None:
        pass  # paused — nothing to update

    def draw(self, surface: pygame.Surface) -> None:
        # Guard: on_exit sets fonts to None; skip if being torn down
        if self._font_title is None:
            return

        # Semi-transparent overlay over whatever is below
        surface.blit(self._overlay, (0, 0))

        # Panel
        pygame.draw.rect(surface, COLOR_PAUSE_PANEL, self._panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PAUSE_BORDER, self._panel_rect, 2, border_radius=8)

        cx = self._panel_rect.centerx

        # Title
        title_surf = self._font_title.render("PAUSA", True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(centerx=cx, top=self._panel_rect.top + 16))

        # Buttons
        mouse_pos = self.input.get_mouse_pos()
        for rect, label in (
            (self._btn_resume,    "CONTINUAR"),
            (self._btn_main_menu, "MENÚ PRINCIPAL"),
        ):
            hovered = rect.collidepoint(mouse_pos)
            bg_color  = COLOR_ACCENT if hovered else COLOR_PAUSE_PANEL
            txt_color = COLOR_BG     if hovered else COLOR_TEXT
            pygame.draw.rect(surface, bg_color, rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_BTN_BORDER, rect, BTN_BORDER_WIDTH, border_radius=4)
            lbl = self._font_btn.render(label, True, txt_color)
            surface.blit(lbl, lbl.get_rect(center=rect.center))

        # Volume label
        vol_lbl = self._font_small.render(
            f"Volumen música: {int(self._music.volume * 100)}%",
            True, COLOR_MUTED
        )
        surface.blit(vol_lbl, vol_lbl.get_rect(centerx=cx, bottom=self._slider_track.top - 4))

        # Slider track
        pygame.draw.rect(surface, COLOR_BTN_BORDER, self._slider_track, border_radius=4)
        fill_w = int(self._slider_track.width * self._music.volume)
        if fill_w > 0:
            fill_rect = pygame.Rect(self._slider_track.left, self._slider_track.top, fill_w, self._slider_track.height)
            pygame.draw.rect(surface, COLOR_ACCENT, fill_rect, border_radius=4)
        # Knob
        knob_x = self._slider_track.left + fill_w
        pygame.draw.circle(surface, COLOR_TEXT, (knob_x, self._slider_track.centery), 8)

        # Mute button
        muted = self._music.muted
        mute_color = COLOR_ACCENT if muted else COLOR_BTN_BORDER
        mute_label = "🔇 SILENCIO" if muted else "🔊 SONIDO"
        pygame.draw.rect(surface, mute_color, self._btn_mute, border_radius=4)
        mute_surf = self._font_small.render(mute_label, True, COLOR_BG if muted else COLOR_TEXT)
        surface.blit(mute_surf, mute_surf.get_rect(center=self._btn_mute.center))

        # ESC hint
        hint = self._font_small.render("ESC — continuar", True, COLOR_MUTED)
        surface.blit(hint, hint.get_rect(centerx=cx, bottom=self._panel_rect.bottom - 10))
