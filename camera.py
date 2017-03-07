from math import tan, sin, cos, pi, sqrt
from world import World
import math
import numpy as np
import pygame
from item import Item

sign = lambda x: math.copysign(1, x)

class Camera:
    def __init__(self, init_pos=[0, 0, 0], init_angle=[0, 0, 0], init_fov=.5*pi):
        self.pos = init_pos
        self.angle = init_angle
        self.fov = init_fov

    def __str__(self):
        return "Camera object at: {}, {}, {}. Angles: {}, {}, {}. Fov: {}".format(self.pos[0], self.pos[1], self.pos[2], self.angle[0], self.angle[1], self.angle[2], self.fov)

    def move(self, movement, speed=0.0001):
        """
        Moves the position of the camera object along the x and z axes
        """
        self.pos[0] += (movement[0]*speed*cos(self.angle[0]))+(movement[2]*speed*sin(self.angle[0]))
        self.pos[2] += (movement[0]*speed*sin(-self.angle[0]))+(movement[2]*speed*cos(self.angle[0]))

    def rotate(self, yaw, pitch, roll, sensitivity=.1):
        """
        Rotates the orientation matrix of the camera
        """
        self.angle[0] += yaw*sensitivity
        self.angle[1] += pitch*sensitivity
        self.angle[2] += roll*sensitivity
        if self.angle[1] < -pi/2:
            self.angle[1] = -pi/2
        if self.angle[1] > pi/2:
            self.angle[1] = pi/2


class Renderer:
    """
    The renderer class. Takes the camera, world, and canvas and draws the scene.

    Note: point variables are named after the coordinate system they are defined in.
    point_w:    world
    point_c:    camera
    point_p:    projection
    point_can:  canvas

    """

    def __init__(self, camera, window_size=(1000,1000)):
        self.project_matrix = self.persp_proj_matrix(camera.fov, window_size[0]/window_size[1], 0.01, 100)

    def draw_scene(self, world, camera, canvas):
        """
        Draws the frame and updates the display.
        """

        # Reset to white
        background = (255, 255, 255)
        canvas.fill(background)

        view_matrix = self.view_matrix(camera)

        self.draw_ground(canvas, camera)


        for item in world.get_objects():
            for tri in item.world_points:
                self.project_line(canvas, tri[0], tri[1], view_matrix, self.project_matrix, (125, 0, 0))
                self.project_line(canvas, tri[1], tri[2], view_matrix, self.project_matrix, (125, 0, 0))
                self.project_line(canvas, tri[2], tri[0], view_matrix, self.project_matrix, (125, 0, 0))

        # Draw center point
        self.draw_point(canvas, (0,0, .01), (0, 200, 0), 6)
        pygame.display.flip()

    def draw_ground(self, canvas, camera):
        """
        Draws the ground. A rectangle based on camera angle
        """

        fov = camera.fov
        cur_angle = (camera.angle[1]+(fov/2))/fov
        # print(camera.angle)
        if cur_angle < 0:
            cur_angle = 0
        if cur_angle > 1:
            cur_angle = 1
        height = cur_angle*canvas.get_height()
        pygame.draw.rect(canvas, (120,120,120), (0,canvas.get_height()-height,canvas.get_width(),canvas.get_height()), 0)


    def project_point(self, point_w, view_matrix, project_matrix, canvas):
        """
        Projects a point from world coordinates to the projected coordinates.
        """

        # R3 points need an w value for perspective. Turn an [x, y, z] to [x, y, z, 1]
        if len(point_w) == 3:
            point_w = np.append(point_w, [1])

        point_v = np.dot(point_w, view_matrix)
        point_p = np.dot(point_v, project_matrix)

        # Makes the perspective happen. w is based on z, and adjusts x and y properly
        if point_p[3] != 0:
            point_p = point_p/(point_p[3])

        return point_p

    def clip_point(self, point_p):
        """
        Clips a point to the inside of the projection box.
        """

        if -1 < point_p[0] < 1 and -1 < point_p[1] < 1 and -1 < point_p[2] < 1:
            return point_p
        else:
            return None

    def clip_line(self, point0_p, point1_p):
        """
        Clips a line to the inside of the projection box.
        Note: incomplete
        """

        point0_clip = self.clip_point(point0_p)
        point1_clip = self.clip_point(point1_p)

        # If both points are inside
        if (point0_clip is not None) and (point1_clip is not None):
            return point0_p, point1_p

        # If line is vertical
        if point0_p[0] == point1_p[0]:
            if -1 < point0_p[0] < 1:
                if point0_clip is None:
                    point0_p[2] = sign(point0_p[2])
                return point0_p, point1_p


        # Make point 0 leftmost
        if point0_p[0] > point1_p[0]:
            point_hold = point0_p
            point0_p = point1_p
            point1_p = point_hold

        # Find intercept
        slope = (point1_p[1] - point0_p[1]) / (point1_p[0] - point0_p[0])
        offset = point0_p[1] - slope*point0_p[0]
        line = lambda x: slope*x + offset

        # Todo: Fix Z
        if self.clip_point((-1, line(-1), 0),) is not None:
            point0_p = (-1, line(-1), point0_p[2])

        return point0_p, point1_p

    def project_line(self, canvas, point0_w, point1_w, view_matrix, project_matrix, color, size=1):
        """
        Projects and draws a line given world coordinates.
        """

        try:
            if len(point0_w) == 3:
                point0_w = np.append(point0_w, [1])
            if len(point1_w) == 3:
                point1_w = np.append(point1_w, [1])
        except:
            print("Bad points given ({}, {})".format(point0_w, point1_w))
            return

        point0_p = self.project_point(point0_w, view_matrix, project_matrix, canvas)
        point1_p = self.project_point(point1_w, view_matrix, project_matrix, canvas)

        point0_clip, point1_clip = self.clip_line(point0_p, point1_p)

        point0_can = self.norm_to_canvas_coord(canvas, point0_clip)
        point1_can = self.norm_to_canvas_coord(canvas, point1_clip)

        print(point0_can, point1_can)
        self.draw_line(canvas, point0_can, point1_can, (125, 0, 0), 1)

    def norm_to_canvas_coord(self, canvas, point_p):
        return((point_p[0] * canvas.get_width()) + canvas.get_width()/2, (point_p[1] * canvas.get_height()) + canvas.get_height()/2, point_p[2])

    def draw_point(self, canvas, point_p, color, size=1):
        """
        Draw a point given projected coordinates.
        """

        if (-1 <= point_p[0] <= 1) and (-1 <= point_p[1] <= 1) and (.01 <= point_p[2] <= 1):
            point_can = self.norm_to_canvas_coord(canvas, point_p)

            if size == 1:
                canvas.set_at((int(point_can[0]), canvas.get_height() - int(point_can[1])), color)

            else:
                # TODO center point
                for i in range(size):
                    for j in range(size):
                        canvas.set_at((int(point_can[0]) + i, canvas.get_height() - int(point_can[1]) + j), color)

    def draw_point_canvas(self, canvas, point_can, color, size=1):
        """
        Draw a point given canvas coordinates.
        """

        for i in range(size):
            for j in range(size):
                canvas.set_at((int(point_can[0]) + i, canvas.get_height() - int(point_can[1]) + j), color)


    def draw_line(self, canvas, point0_can, point1_can, color, size=3):
        """
        Draw line between two points.
        """

        if point0_can is None or point1_can is None:
            return

        x = point0_can[0]
        y = point0_can[1]
        z = point0_can[2]

        if int(point0_can[0]) == int(point1_can[0]) and int(point0_can[1]) == int(point1_can[1]):
            print("Single point at {} {} {}".format(x, y, z))
            self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, 1)
            return

        # Vertical line
        if int(point0_can[0]) == int(point1_can[0]):
            # print("Vertical Line", x, int(point0_can[1]) - int(point0_can[1]))
            dz = (point1_can[2] - point0_can[2]) / (point1_can[1] - point0_can[1])

            for y in range(int(point0_can[1]), int(point1_can[1])):
                if z > .01:
                    self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, size)
                z += dz
            return

        # Horizontal line
        if int(point0_can[1]) == int(point1_can[1]):
            # print("Horizontal Line")
            dz = (point1_can[2] - point0_can[2]) / (point1_can[0] - point0_can[0])

            for x in range(int(point0_can[0]), int(point1_can[0])):
                if z > .01:
                    self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, size)
                z += dz
            return

        dx = (point1_can[0] - point0_can[0]) / (point1_can[1] - point0_can[1])
        dy = (point1_can[1] - point0_can[1]) / (point1_can[0] - point0_can[0])


        if dx > dy:
            # dz depends on x
            dz = (point1_can[2] - point0_can[2]) / (point1_can[0] - point0_can[0])

            for x in range(int(point0_can[0]), int(point1_can[0])):
                #print(x, y, z)
                self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, size)
                y += dy
                z += dz

        else:
            # dz depends on y
            dz = dz = (point1_can[2] - point0_can[2]) / (point1_can[1] - point0_can[1])

            for y in range(int(point0_can[1]), int(point1_can[1])):
                #print(x, y, z)
                self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, size)
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
        c = zfar / (zfar - znear)

        d = 1

        # Maps w to proper z value
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

        arr =  np.array([[xaxis[0],                     yaxis[0],                   zaxis[0],                0],
                         [xaxis[1],                     yaxis[1],                   zaxis[1],                0],
                         [xaxis[2],                     yaxis[2],                   zaxis[2],                0],
                         [-np.dot(xaxis, camera.pos),   -np.dot(yaxis, camera.pos), -np.dot(zaxis, camera.pos), 1]])

        return arr


if __name__ == "__main__":
    window_size = (1000, 1000)
    background = (255, 255, 255)

    pygame.init()
    canvas = pygame.display.set_mode(window_size, 0, 32)
    clock = pygame.time.Clock()

    camera = Camera(init_pos=[0,0,-10], init_angle=[0, 0, 0])
    renderer = Renderer(camera, window_size=window_size)
    world = World([Item('Cylinder.stl', (0, .5, 0), (0, 0, 0), 1)])


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
