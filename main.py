import pygame
from src.game_manager import GameManager, WIDTH, HEIGHT


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Kitchen Rush')
    clock = pygame.time.Clock()
    game = GameManager(screen)
    running = True
    while running:
        dt = clock.tick(60) / 1000
        game.update(dt, pygame.key.get_pressed())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
        game.draw()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
