import pygame


class InputHandler:
    """Centralized input state. Call update() once per frame before scenes process input."""

    def __init__(self):
        self._keys_prev = {}
        self._keys_curr = {}
        self._mouse_clicked = False
        self._mouse_pos = (0, 0)

    def update(self, events: list):
        """Must be called once per frame with the event list from pygame.event.get()."""
        self._keys_prev = dict(self._keys_curr)
        self._keys_curr = dict(enumerate(pygame.key.get_pressed()))
        self._mouse_pos = pygame.mouse.get_pos()
        self._mouse_clicked = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._mouse_clicked = True

    def is_key_pressed(self, key: int) -> bool:
        """True while the key is held down."""
        return bool(self._keys_curr.get(key, False))

    def is_key_just_pressed(self, key: int) -> bool:
        """True only on the first frame the key is pressed."""
        return bool(self._keys_curr.get(key, False)) and not bool(self._keys_prev.get(key, False))

    def get_mouse_pos(self) -> tuple[int, int]:
        return self._mouse_pos

    def is_mouse_clicked(self) -> bool:
        """True for one frame when left mouse button is released."""
        return self._mouse_clicked
