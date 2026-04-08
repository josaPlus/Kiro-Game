"""core/placeholder_sprites.py
Geometric worker sprites drawn entirely with pygame.draw — no image files needed.
"""
import pygame

# Color schemes per factory_id
_FACTORY_COLORS = {
    "chemical":   {"body": (180, 60,  60),  "hat": (255, 220, 0)},
    "automotive": {"body": (60,  100, 180), "hat": (255, 255, 255)},
    "warehouse":  {"body": (60,  160, 80),  "hat": (255, 140, 0)},
}

_SKIN = (255, 200, 160)
_STRIPE = (230, 230, 230)  # vest stripe highlight


def draw_worker(
    surface: pygame.Surface,
    x: int,
    y: int,
    factory_id: str,
    scale: float = 1.0,
    leg_offset: tuple[int, int] = (0, 0),
):
    """Draw a geometric worker figure centred at (x, y).

    The figure fits inside a 48×64 bounding box at scale=1.0.
    leg_offset = (left_dy, right_dy) shifts each leg rect vertically for walk frames.
    """
    colors = _FACTORY_COLORS.get(factory_id, _FACTORY_COLORS["warehouse"])
    body_color = colors["body"]
    hat_color  = colors["hat"]

    def s(v: float) -> int:
        return max(1, int(v * scale))

    # --- dimensions (base px) ---
    head_r   = s(9)
    hat_w, hat_h = s(20), s(6)
    body_w, body_h = s(20), s(22)
    arm_w, arm_h = s(6), s(14)
    leg_w, leg_h = s(8), s(16)
    stripe_w, stripe_h = s(4), s(10)

    # --- vertical layout anchors (relative to centre x, top of bounding box) ---
    top = y - s(32)          # top of 64px box

    hat_top  = top
    head_cy  = hat_top + hat_h + head_r
    body_top = head_cy + head_r
    arm_top  = body_top + s(2)
    leg_top  = body_top + body_h

    # --- hard hat ---
    hat_rect = pygame.Rect(x - hat_w // 2, hat_top, hat_w, hat_h)
    pygame.draw.rect(surface, hat_color, hat_rect)

    # --- head ---
    pygame.draw.circle(surface, _SKIN, (x, head_cy), head_r)

    # --- body ---
    body_rect = pygame.Rect(x - body_w // 2, body_top, body_w, body_h)
    pygame.draw.rect(surface, body_color, body_rect)

    # vest stripe
    stripe_rect = pygame.Rect(x - stripe_w // 2, body_top + s(4), stripe_w, stripe_h)
    pygame.draw.rect(surface, _STRIPE, stripe_rect)

    # --- arms ---
    left_arm  = pygame.Rect(x - body_w // 2 - arm_w, arm_top, arm_w, arm_h)
    right_arm = pygame.Rect(x + body_w // 2,          arm_top, arm_w, arm_h)
    pygame.draw.rect(surface, body_color, left_arm)
    pygame.draw.rect(surface, body_color, right_arm)

    # --- legs ---
    l_dy, r_dy = leg_offset
    left_leg  = pygame.Rect(x - body_w // 2,              leg_top + s(l_dy), leg_w, leg_h)
    right_leg = pygame.Rect(x + body_w // 2 - leg_w,      leg_top + s(r_dy), leg_w, leg_h)
    pygame.draw.rect(surface, body_color, left_leg)
    pygame.draw.rect(surface, body_color, right_leg)
