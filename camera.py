from math import tan, sin, cos, pi
import numpy as np
import pygame
from item import *



class Camera:
    pos = (0, 0, 0)
    angle = (0, 0, 0)

    def __init__(self, init_pos=(0, 0, 0), init_angle=(0, 0, 0)):
        self.pos = init_pos
        self.angle = init_angle

    def __str__(self):
        return "Camera object at: {}, {}, {}. Angles: {}, {}, {}".format(self.pos[0], self.pos[1], self.pos[2], self.angle[0], self.angle[1], self.angle[2])


class Renderer:
    """
    The renderer class. Takes the camera and world and outputs images.
    """

    frame = 0

    def draw_scene(self, world, camera, canvas, fov=70):
        """
        Draws the frame and updates the display
        """

        global background

        global item

        self.frame += 1

        # Reset to black
        canvas.fill(background)

        # Temp: draw rectangle
        # TODO: add transformMatrix = worldMatrix * viewMatrix * projectionMatrix and then do it

        view_matrix = self.view_matrix(camera)
        project_matrix = self.persp_proj_matrix(fov, canvas.get_width()/canvas.get_height(), 0.01, 1.0)

        transform_matrix = view_matrix * project_matrix

        for tri in item.world_points:
            for point in tri:
                #print(point)
                self.draw_point(canvas, np.dot(np.append(point, [1]), transform_matrix)[:2], (125, 0, 0))

        # for i in range(50):
        #     for j in range(50):
        #         canvas.set_at((i + self.frame, j + self.frame), (150, 0, 0))

        pygame.display.flip()

    def draw_point(self, canvas, point, color):
        #print(point)
        canvas.set_at((int(point[0]), int(point[1])), color)

    def persp_proj_matrix(self, fov, aspect, znear, zfar):
        """
        Return a projection matrix for the given parameters
        """

        # calculates the 'length' of half of the screen
        xymax = znear * tan(fov * pi / 360) # /360 because fov/2 * pi/180
        ymin = -xymax
        xmin = -xymax

        # adds the two together
        width = xymax - xmin
        height = xymax - ymin

        depth = zfar - znear
        q = -(zfar + znear) / depth
        qn = -2 * (zfar * znear) / depth

        w = (2 * znear / width) / aspect
        h = 2 * znear / height

        return np.array([[w, 0, 0, 0],
                         [0, h, 0, 0],
                         [0, 0, q, -1],
                         [0, 0, qn, 0]])


    def view_matrix(self, camera):
        sinYaw = sin(camera.angle[0])
        cosYaw = cos(camera.angle[0])
        sinPitch = sin(camera.angle[1])
        cosPitch = cos(camera.angle[1])

        # Figure out what this is doing
        xaxis = (cosYaw, 0, -sinYaw)
        yaxis = (sinYaw * sinPitch, cosPitch, cosYaw * sinPitch)
        zaxis = (sinYaw * cosPitch, -sinPitch, cosPitch * cosYaw)

        # Might need transpose. This is a RH matrix, z axis is negative
        return np.array([[xaxis[0],                     yaxis[0],                   zaxis[0],                0],
                         [xaxis[1],                     yaxis[1],                   zaxis[1],                0],
                         [xaxis[2],                     yaxis[2],                   zaxis[2],                0],
                         [-np.dot(xaxis, camera.pos),   -np.dot(yaxis, camera.pos), -np.dot(zaxis, camera.pos), 1]])

class World:
    """
    Holds all the items in the world
    """

    items = 0

    def add_item():
        """
        Adds item to the world.
        """

    def move_item():
        """
        Changes coordinates of an existing item.
        """

    def gen_world():
        """
        Generates a world.
        """

if __name__ == "__main__":
    window_size = (400, 400)
    background = (255, 255, 255)

    pygame.init()
    canvas = pygame.display.set_mode(window_size, 0, 32)
    clock = pygame.time.Clock()

    camera = Camera()
    renderer = Renderer()
    world = World()

    item = Item('Cylinder.stl', (-1, 1, 1), (90, 30, 0))

    while True:
        renderer.draw_scene(world, camera, canvas)
        clock.tick(30)
