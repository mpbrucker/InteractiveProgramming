from PIL import Image, ImageDraw, ImageTk
from time import sleep
import numpy as np
import pygame

pygame.init()
windowSurface = pygame.display.set_mode((400, 400), 0, 32)

im = Image.new("RGB", (400, 400), (0, 150, 0))
pixels = im.load()


frame = 0

while True:
    for i in range(50):
        for j in range(50):
            pixels[i+frame, j+frame] = (150, 0, 0)

    frame += 1

    pygame_image = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
    windowSurface.blit(pygame_image, (0,0))
    pygame.display.flip()

    sleep(.1)
