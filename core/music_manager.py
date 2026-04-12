"""core/music_manager.py
Centralised background music controller.
Uses pygame.mixer.music — only one track plays at a time.
"""
from __future__ import annotations
import pygame
from settings import MUSIC_VOLUME


class MusicManager:
    """Singleton-style music controller. Call MusicManager.instance() to get it."""

    _inst: "MusicManager | None" = None

    @classmethod
    def instance(cls) -> "MusicManager":
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    def __init__(self) -> None:
        self._current_path: str | None = None
        self._volume: float = MUSIC_VOLUME
        self._muted: bool = False

    # ------------------------------------------------------------------
    def play(self, path: str, loops: int = -1) -> None:
        """Load and play a music file. No-op if already playing the same file."""
        if self._current_path == path and pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.0 if self._muted else self._volume)
            pygame.mixer.music.play(loops)
            self._current_path = path
        except Exception:
            pass  # missing file or mixer not initialised — fail silently

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self._current_path = None

    def pause(self) -> None:
        pygame.mixer.music.pause()

    def resume(self) -> None:
        pygame.mixer.music.unpause()

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        if not self._muted:
            pygame.mixer.music.set_volume(self._volume)

    def toggle_mute(self) -> bool:
        self._muted = not self._muted
        pygame.mixer.music.set_volume(0.0 if self._muted else self._volume)
        return self._muted

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def muted(self) -> bool:
        return self._muted
