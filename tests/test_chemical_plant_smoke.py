"""tests/test_chemical_plant_smoke.py
Smoke test: verify ChemicalPlantScene lifecycle (on_enter → update × N → on_exit)
does not raise with a mocked pygame surface and a real InputHandler.
"""
import pygame
import pytest
from unittest.mock import MagicMock

from core.input_handler import InputHandler
from core.scene_manager import SceneManager
from scenes.chemical_plant import ChemicalPlantScene


FACTORY_DATA = {
    "id": "chemical",
    "name": "Chemical Plant",
    "abbrev": "CH",
    "color": (180, 60, 60),
    "difficulty": "HARD",
    "description": "Manage gas leaks and PPE in a chemical plant.",
    "hazards": ["gas leaks", "explosions"],
}


@pytest.fixture(scope="session", autouse=True)
def pygame_session():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    yield
    pygame.quit()


@pytest.fixture
def scene(pygame_session):
    manager = MagicMock(spec=SceneManager)
    input_handler = InputHandler()
    return ChemicalPlantScene(manager, input_handler, FACTORY_DATA)


def test_scene_lifecycle_does_not_raise(scene):
    """on_enter → several update(dt) calls → on_exit must not raise."""
    surface = pygame.Surface((1280, 720))

    scene.on_enter()

    for _ in range(5):
        scene.update(1 / 60)

    scene.draw(surface)
    scene.on_exit()


def test_on_enter_initialises_playing_phase(scene):
    """After on_enter, phase must be PLAYING and core state must be set."""
    scene.on_enter()
    assert scene._phase == "PLAYING"
    assert scene._level == 1
    assert scene._score == 0
    assert scene._safety == 100.0
    assert scene._production == 0.0
    assert isinstance(scene._leaks, list)
    assert isinstance(scene._workers, list)
    scene.on_exit()


def test_on_exit_clears_state(scene):
    """After on_exit, all state fields must be None."""
    scene.on_enter()
    scene.on_exit()
    assert scene._phase is None
    assert scene._level is None
    assert scene._leaks is None
    assert scene._workers is None
    assert scene._save_manager is None


def test_update_advances_time(scene):
    """update(dt) should increment _time_survived and _production."""
    scene.on_enter()
    dt = 0.5
    scene.update(dt)
    assert scene._time_survived == pytest.approx(dt, abs=1e-6)
    assert scene._production == pytest.approx(min(100.0, 5.0 * dt), abs=1e-6)
    scene.on_exit()


def test_handle_event_escape_calls_pop(scene):
    """K_ESCAPE during PLAYING phase must call manager.pop_scene()."""
    scene.on_enter()
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode="")
    scene.handle_event(event)
    scene.manager.pop_scene.assert_called_once()
    scene.on_exit()
