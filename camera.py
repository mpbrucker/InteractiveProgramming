from math import tan, sin, cos, pi
import numpy as np
import pygame
from item import *



class Camera:
    pos = [0, 0, 0]
    angle = [0, 0, 0]
    fov = 0

    def __init__(self, init_pos=[0, 0, 0], init_angle=[0, 0, 0], init_fov=60):
        self.pos = init_pos
        self.angle = init_angle
        self.fov = init_fov

    def __str__(self):
        return "Camera object at: {}, {}, {}. Angles: {}, {}, {}. Fov: {}".format(self.pos[0], self.pos[1], self.pos[2], self.angle[0], self.angle[1], self.angle[2], self.fov)


class Renderer:
    """
    The renderer class. Takes the camera and world and outputs images.
    """

    frame = 0

    def draw_scene(self, world, camera, canvas):
        """
        Draws the frame and updates the display
        """

        global background
        global item

        self.frame += 1

        # Reset to black
        canvas.fill(background)

        view_matrix = self.view_matrix(camera)
        project_matrix = self.persp_proj_matrix(camera.fov, canvas.get_width()/canvas.get_height(), .001, 1)

        # transform_matrix = project_matrix * view_matrix

        # print("View:")
        # print(view_matrix)
        # print("Project:")
        # print(project_matrix)
        # print("Transform:")
        # print(transform_matrix)

        # Debug: draw center point
        self.draw_point(canvas, (canvas.get_width()/2,canvas.get_height()/2, 1), (0, 200, 0), 8)
        if np.dot((0, 0, 0, 1), view_matrix)[2] > 0.01:
            self.draw_point(canvas, self.project_point((0,0,0), view_matrix, project_matrix, canvas), (125, 0, 0), 4)

        for tri in item.world_points:
            for point in tri:
                point_view = np.dot(np.append(point, [1]), view_matrix)

                if point_view[2] > 0.01:
                    print("Pt:", point)
                    print("Pt V:", point_view)
                    print("Pt Tf:", self.project_point(point, view_matrix, project_matrix, canvas))
                    input()

                    self.draw_point(canvas, self.project_point(point, view_matrix, project_matrix, canvas), (125, 0, 0), 6)

        # for i in range(50):
        #     for j in range(50):
        #         canvas.set_at((i + self.frame, j + self.frame), (150, 0, 0))

        pygame.display.flip()

    def project_point(self, point, view_matrix, project_matrix, canvas):
        xy = np.dot(np.append(point, [1]), view_matrix)
        xy = np.dot(xy, project_matrix)

        xy = xy/xy[3]

        xy[0] = xy[0] + canvas.get_width() / 2
        xy[1] = xy[1] + canvas.get_height() / 2
        # print(xy)
        return xy


    def draw_point(self, canvas, point, color, size=1):
        # print(point)
        # Basic clipping
        if point[2] > 0.01:
            for i in range(size):
                for j in range(size):
                    canvas.set_at((int(point[0] + i), canvas.get_height() - int(point[1]) + j), color)

    def persp_proj_matrix(self, fov, aspect, znear, zfar):
        """
        Return a projection matrix for the given parameters
        """

        # # This is probably 'just wrong'
        # # calculates the 'length' of half of the screen
        # xymax = znear * tan(fov * pi / 360) # /360 because fov/2 * pi/180
        # ymin = -xymax
        # xmin = -xymax
        #
        # # adds the two together
        # width = xymax - xmin
        # height = xymax - ymin
        #
        # depth = zfar - znear
        # q = -(zfar + znear) / depth
        # qn = -2 * (zfar * znear) / depth
        #
        # w = (2 * znear / width) / aspect
        # h = 2 * znear / height
        #
        # return np.array([[w, 0, 0, 0],
        #                  [0, h, 0, 0],
        #                  [0, 0, q, -1],
        #                  [0, 0, qn, 0]])

        pi180 = pi/180

        # Scale of x axis
        a = aspect * (1 / tan((fov * .5) * pi180)) # Degrees to Rad
        # Scale of y axis
        b = 1 / tan((fov * .5) * pi180) # Degrees to Rad

        # Remaps z to [0,1]
        c = zfar / (zfar - znear)
        # Remaps z to [0,1]
        d = -(znear * zfar) / (zfar - znear)
        e = 1

        # Might need transform
        return np.array([[a, 0, 0, 0],
                         [0, b, 0, 0],
                         [0, 0, c, d],
                         [0, 0, e, 0]]).T

        # deg_to_rad = pi/180
        # # Scale of horiz
        # a = znear * tan(fov * .5 * deg_to_rad)
        # # Scale of vertical
        # b = (znear * tan(fov * .5 * deg_to_rad)) / aspect
        #
        # c = 0
        # d = 1
        # e = 1
        #
        # return np.array([[a, 0, 0, 0],
        #                  [0, b, 0, 0],
        #                  [0, 0, c, d],
        #                  [0, 0, 0, 0]])


    def view_matrix(self, camera):
        pi180 = pi/180
        sinYaw = sin(camera.angle[0]*pi180)
        cosYaw = cos(camera.angle[0]*pi180)
        sinPitch = sin(camera.angle[1]*pi180)
        cosPitch = cos(camera.angle[1]*pi180)

        # Modifies the axis vectors to point in the direction of the camera
        xaxis = (cosYaw, 0, -sinYaw)
        yaxis = (sinYaw * sinPitch, cosPitch, cosYaw * sinPitch)
        zaxis = (sinYaw * cosPitch, -sinPitch, cosPitch * cosYaw)

        # print(xaxis)
        # print(yaxis)
        # print(zaxis)

        # # This is a RH matrix, z axis (camera pos) is negative
        arr =  np.array([[xaxis[0],                     yaxis[0],                   zaxis[0],                0],
                         [xaxis[1],                     yaxis[1],                   zaxis[1],                0],
                         [xaxis[2],                     yaxis[2],                   zaxis[2],                0],
                         [-np.dot(xaxis, camera.pos),   -np.dot(yaxis, camera.pos), -np.dot(zaxis, camera.pos), 1]])

        # arr = np.array([[xaxis[0], xaxis[1], xaxis[2], -np.dot(xaxis, camera.pos)],
        #                 [yaxis[0], yaxis[1], yaxis[2], -np.dot(yaxis, camera.pos)],
        #                 [zaxis[0], zaxis[1], zaxis[2], -np.dot(zaxis, camera.pos)],
        #                 [       0,        0,        0,                         1 ]])

        return arr


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

    def all_objects():
        """
        Returns all objects in the world
        """

if __name__ == "__main__":
    window_size = (1000, 1000)
    background = (255, 255, 255)

    pygame.init()
    canvas = pygame.display.set_mode(window_size, 0, 32)
    clock = pygame.time.Clock()

    camera = Camera(init_pos=[0,0,0], init_angle=[0, 0, 0], init_fov=90)
    renderer = Renderer()
    world = World()

    item = Item('cube.stl', (0, 0, 0), (0, 0, 0), 1)

    while True:
        print(camera)
        renderer.draw_scene(world, camera, canvas)
        # camera.pos[0] = camera.pos[0] + 5
        # camera.pos[1] = camera.pos[1] + 5
        camera.pos[2] = camera.pos[2] + .005
        # camera.fov = camera.fov + 1
        # camera.angle[0] = camera.angle[0] + .4


        # print()
        clock.tick(30)
