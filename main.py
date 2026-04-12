import sys
import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE, MUSIC_MENU_PATH
from core.scene_manager import SceneManager
from core.input_handler import InputHandler
from core.music_manager import MusicManager
from scenes.main_menu import MainMenuScene

# Scenes that are "gameplay" scenes — P key opens pause in these
_GAMEPLAY_SCENE_NAMES = {"ChemicalPlantScene", "GamePlaceholderScene"}


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    music = MusicManager.instance()
    music.play(MUSIC_MENU_PATH)

    input_handler = InputHandler()
    scene_manager = SceneManager()
    scene_manager.push_scene(MainMenuScene(scene_manager, input_handler))

    while not scene_manager.is_empty:
        dt = clock.tick(FPS) / 1000.0

        events = pygame.event.get()

        # Global quit
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        input_handler.update(events)

        current = scene_manager.current
        if current:
            # Global pause key — P opens pause overlay from any gameplay scene
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    scene_name = type(current).__name__
                    if scene_name in _GAMEPLAY_SCENE_NAMES:
                        from scenes.pause_scene import PauseScene
                        scene_manager.push_scene(PauseScene(scene_manager, input_handler))
                        break

            for event in events:
                current.handle_event(event)
            current.update(dt)
            current.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
