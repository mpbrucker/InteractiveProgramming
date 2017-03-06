from math import tan, sin, cos, pi, sqrt
import math
import numpy as np
import pygame
from item import *

sign = lambda x: math.copysign(1, x)
class Camera:
    # Position coordinates
    pos = [0, 0, 0]
    # Camera orientation. In rad
    angle = [0, 0, 0]
    fov = 0

    def __init__(self, init_pos=[0, 0, 0], init_angle=[0, 0, 0], init_fov=.5*pi):
        self.pos = init_pos
        self.angle = init_angle
        self.fov = init_fov

    def __str__(self):
        return "Camera object at: {}, {}, {}. Angles: {}, {}, {}. Fov: {}".format(self.pos[0], self.pos[1], self.pos[2], self.angle[0], self.angle[1], self.angle[2], self.fov)

    def move(self, movement, speed=0.0001):
        self.pos[0] += (movement[0]*speed*cos(self.angle[0]))+(movement[2]*speed*sin(self.angle[0]))
        self.pos[2] += (movement[0]*speed*sin(-self.angle[0]))+(movement[2]*speed*cos(self.angle[0]))

    def rotate(self, yaw, pitch, roll, sensitivity=.1):
        self.angle[0] += yaw*sensitivity
        self.angle[1] += pitch*sensitivity
        self.angle[2] += roll*sensitivity


class Renderer:
    """
    The renderer class. Takes the camera, world, and canvas and draws the scene.
    """
    def __init__(self, camera):
        self.project_matrix = self.persp_proj_matrix(camera.fov, canvas.get_width()/canvas.get_height(), 1, 30)

    def draw_scene(self, world, camera, canvas):
        """
        Draws the frame and updates the display.
        """


        # TODO: Use world items
        item = Item('cube2.stl', (0, 0, 0), (0, 0, 0), 1)

        # Reset to white
        background = (255, 255, 255)
        canvas.fill(background)

        view_matrix = self.view_matrix(camera)


        # Draw center point
        self.draw_point(canvas, (canvas.get_width()/2,canvas.get_height()/2, 1), (0, 200, 0), 6)

        test_lines = (((0,1,0,1),(1,0,0,1)),) #, ((0,0,1,1),(10,10,10,1)))
        for line in test_lines:
            self.project_line(canvas, line[0], line[1], view_matrix, self.project_matrix, (125, 0, 0), 3)

        # for tri in item.world_points:
        #     print(tri)
        #     self.project_line(canvas, tri[0], tri[1], view_matrix, project_matrix, (125, 0, 0), 3)
        #     self.project_line(canvas, tri[1], tri[2], view_matrix, project_matrix, (125, 0, 0), 3)

        # for tri in item.world_points:
        #     for point in tri:
        #         point_view = np.dot(np.append(point, [1]), view_matrix)
        #
        #         # Cull points behind camera
        #         if point_view[2] > 0.01:
        #             self.draw_point(canvas, self.project_point(point, view_matrix, project_matrix, canvas), (125, 0, 0), 6, point)


        pygame.display.flip()


    def project_point(self, point, view_matrix, project_matrix, canvas):
        # R3 points need an w value for perspective. Turn an [x, y, z] to [x, y, z, 1]
        if len(point) == 3:
            point = np.append(point, [1])

        # Project the points to the camera view and then a projection view
        print(view_matrix)
        print("point:", point)
        #xy = view_matrix * point
        xy = np.dot(point, view_matrix)

        print("xyV:", xy)
        xy = np.dot(xy, project_matrix)
        print("xyP:", xy)


        # Makes the perspective happen. w is based on z, and adjusts x and y properly
        # The magic number makes the stretch in z smaller. Tweak to perfection. Can also be fixed in the projection matrix
        # TODO: removed magic number (xy[3] * .02), might need to put it back
        if not xy[3] == 0:
            xy = xy/(xy[3])

        # if (xy[0] > 1 or xy[0] < -1) or (xy[1] > 1 or xy[1] < -1) or (xy[2] > 1 or xy[2] < -1):
        #     # TODO: Clip here if -w < (x, y, z) < w
        #     return (0,0,0,1)

        # xy[0] = xy[0] + canvas.get_width() / 2
        # xy[1] = xy[1] + canvas.get_height() / 2

        # print(xy)
        return xy

    def project_line(self, canvas, point0, point1, view_matrix, project_matrix, color, size=1):
        """
        Projects and draws a line given world coordinates.
        """

        try:
            if len(point0) == 3:
                point0 = np.append(point0, [1])
            if len(point1) == 3:
                point1 = np.append(point1, [1])
        except:
            print("Bad points given ({}, {})".format(point0, point1))
            return

        point0_p = self.project_point(point0, view_matrix, project_matrix, canvas)
        point1_p = self.project_point(point1, view_matrix, project_matrix, canvas)

        print(point0_p, point1_p)

        self.draw_line(canvas, point0_p, point1_p, (125, 0, 0), 3)

    def draw_point(self, canvas, point, color, size=1, orig_coordinates=""):
        # print(point)
        if point[2] > .01:
            for i in range(size):
                for j in range(size):
                    canvas.set_at((int(point[0]) + i, canvas.get_height() - int(point[1]) + j), color)


    def draw_line(self, canvas, point0, point1, color, size=1):
        """
        Draw line between two points.
        """
        x = point0[0]
        y = point0[1]
        z = point0[2]

        if int(point0[0]) == int(point1[0]) and int(point0[1]) == int(point1[1]):
            print("Single point at {} {} {}".format(x, y, z))
            self.draw_point(canvas, (int(x), int(y), int(z)), color, 100)
            return

        # Vertical line
        if int(point0[0]) == int(point1[0]):
            dz = (point1[2] - point0[2]) / (point1[1] - point0[1])

            for y in range(int(point0[1]), int(point1[1])):
                if z > .01:
                    self.draw_point(canvas, (int(x), int(y), int(z)), color, size)
                z += dz
            return

        # Horizontal line
        if int(point0[1]) == int(point1[1]):
            dz = (point1[2] - point0[2]) / (point1[0] - point0[0])

            for x in range(int(point0[0]), int(point1[0])):
                if z > .01:
                    self.draw_point(canvas, (int(x), int(y), int(z)), color, size)
                z += dz
            return

        dx = (point1[0] - point0[0]) / (point1[1] - point0[1])
        dy = (point1[1] - point0[1]) / (point1[0] - point0[0])


        if dx > dy:
            # dz depends on x
            dz = (point1[2] - point0[2]) / (point1[0] - point0[0])

            for x in range(int(point0[0]), int(point1[0])):
                print(x, y, z)
                self.draw_point(canvas, (int(x), int(y), int(z)), color, size)
                y += dy
                z += dz

        else:
            # dz depends on y
            dz = dz = (point1[2] - point0[2]) / (point1[1] - point0[1])

            for y in range(int(point0[1]), int(point1[1])):
                print(x, y, z)
                self.draw_point(canvas, (int(x), int(y), int(z)), color, size)
                x += dx
                z += dz


    def persp_proj_matrix(self, fov, aspect, znear, zfar):
        """
        Return a projection matrix for the given parameters
        """

        # Scale of x axis
        a = aspect * (1 / tan(fov * .5))

        # Scale of y axis
        b = 1 / tan(fov * .5)

        # Remaps z to [0,1], for z-index
            # Possible: c = -(zfar + znear) / (zfar - znear)
        c = zfar / (zfar - znear)

        d = 1

        # Maps w to z *
            # TODO: Figure out why this is wrong.
            # Possible: e = -2 * (zfar * znear) / (zfar - znear)
        e = -(znear * zfar) / (zfar - znear)


        return np.array([[a, 0, 0, 0],
                         [0, b, 0, 0],
                         [0, 0, c, d],
                         [0, 0, e, 0]])


    def view_matrix(self, camera):
        sinYaw = sin(camera.angle[0])
        cosYaw = cos(camera.angle[0])
        sinPitch = sin(camera.angle[1])
        cosPitch = cos(camera.angle[1])

        # Modifies the axis vectors to point in the direction of the camera
        xaxis = (cosYaw, 0, -sinYaw)
        yaxis = (sinYaw * sinPitch, cosPitch, cosYaw * sinPitch)
        zaxis = (sinYaw * cosPitch, -sinPitch, cosPitch * cosYaw)

        # print(xaxis)
        # print(yaxis)
        # print(zaxis)

        # Might be a RH matrix
        arr =  np.array([[xaxis[0],                     yaxis[0],                   zaxis[0],                0],
                         [xaxis[1],                     yaxis[1],                   zaxis[1],                0],
                         [xaxis[2],                     yaxis[2],                   zaxis[2],                0],
                         [-np.dot(xaxis, camera.pos),   -np.dot(yaxis, camera.pos), -np.dot(zaxis, camera.pos), 1]])

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

    camera = Camera(init_pos=[0,0,-1], init_angle=[0, 0, 0])
    renderer = Renderer()
    world = World()

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
