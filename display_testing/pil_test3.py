import numpy as np
import pygame

pygame.init()
windowSurface = pygame.display.set_mode((400, 400), 0, 32)

clock = pygame.time.Clock()
frame = 0

while True:
    windowSurface.fill((0, 150, 0))
    for i in range(50):
        for j in range(50):
            windowSurface.set_at((i+frame, j+frame), (150, 0, 0))

    frame += 1

    pygame.display.flip()

    clock.tick(30)
