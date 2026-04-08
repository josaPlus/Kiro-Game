"""core/sprite_animator.py
Simple frame-cycling animator and walk-animation factory for geometric workers.
"""
import pygame
from core.placeholder_sprites import draw_worker


class SpriteAnimator:
    """Cycles through a list of pre-drawn pygame.Surface frames at a given fps."""

    def __init__(self, frame_surfaces: list[pygame.Surface], fps: int = 6):
        self._frames = frame_surfaces
        self._fps    = fps
        self._index  = 0
        self._timer  = 0.0

    def update(self, dt: float):
        """Advance the animation by dt seconds."""
        self._timer += dt
        frame_duration = 1.0 / self._fps
        while self._timer >= frame_duration:
            self._timer -= frame_duration
            self._index = (self._index + 1) % len(self._frames)

    def get_current_frame(self) -> pygame.Surface:
        return self._frames[self._index]

    def reset(self):
        self._index = 0
        self._timer = 0.0


def get_walk_animation(factory_id: str, scale: float = 1.0) -> SpriteAnimator:
    """Return a SpriteAnimator with 2 walk frames for the given factory type.

    Frame 0: left leg forward  (left -4px, right +4px)
    Frame 1: right leg forward (left +4px, right -4px)
    """
    w = int(48 * scale)
    h = int(64 * scale)
    cx = w // 2
    cy = h // 2

    leg_offsets = [(-4, 4), (4, -4)]  # (left_dy, right_dy) per frame
    frames = []
    for l_dy, r_dy in leg_offsets:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        draw_worker(surf, cx, cy, factory_id, scale=scale, leg_offset=(l_dy, r_dy))
        frames.append(surf)

    return SpriteAnimator(frames, fps=6)
