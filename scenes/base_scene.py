from __future__ import annotations
import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.scene_manager import SceneManager
    from core.input_handler import InputHandler


class BaseScene(ABC):
    """Abstract base for all scenes. Every scene gets a reference to the manager and input handler."""

    def __init__(self, manager: "SceneManager", input_handler: "InputHandler"):
        self.manager = manager
        self.input = input_handler

    # Lifecycle hooks — override as needed
    def on_enter(self): pass
    def on_exit(self): pass
    def on_pause(self): pass
    def on_resume(self): pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event): ...

    @abstractmethod
    def update(self, dt: float): ...

    @abstractmethod
    def draw(self, surface: pygame.Surface): ...
