import numpy as np
import pygame

window_size = (400, 400)
background = (255, 255, 255)

class Camera:
    def __init__(self):
        pass

    def drawScene(self, surface):
        surface.fill((0, 150, 0))

        for i in range(50):
            for j in range(50):
                surface.set_at((i, j), (150, 0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    surface = pygame.display.set_mode(window_size, 0, 32)
    clock = pygame.time.Clock()

    camera = Camera()

    while True:
        camera.drawScene(surface)
        clock.tick(30)
