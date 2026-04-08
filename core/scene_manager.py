from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scenes.base_scene import BaseScene


class SceneManager:
    """Stack-based scene manager. Scenes can push, pop, or replace themselves."""

    def __init__(self):
        self._stack: list[BaseScene] = []

    @property
    def current(self) -> "BaseScene | None":
        return self._stack[-1] if self._stack else None

    def push_scene(self, scene: "BaseScene"):
        if self.current:
            self.current.on_pause()
        self._stack.append(scene)
        scene.on_enter()

    def pop_scene(self):
        if not self._stack:
            return
        self._stack.pop().on_exit()
        if self.current:
            self.current.on_resume()

    def replace_scene(self, scene: "BaseScene"):
        if self._stack:
            self._stack.pop().on_exit()
        self._stack.append(scene)
        scene.on_enter()

    @property
    def is_empty(self) -> bool:
        return len(self._stack) == 0
