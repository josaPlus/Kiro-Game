import sys
import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE
from core.scene_manager import SceneManager
from core.input_handler import InputHandler
from scenes.main_menu import MainMenuScene


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    input_handler = InputHandler()
    scene_manager = SceneManager()
    scene_manager.push_scene(MainMenuScene(scene_manager, input_handler))

    while not scene_manager.is_empty:
        dt = clock.tick(FPS) / 1000.0  # delta time in seconds
        events = pygame.event.get()

        # Global quit
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        input_handler.update(events)

        current = scene_manager.current
        if current:
            for event in events:
                current.handle_event(event)
            current.update(dt)
            current.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
