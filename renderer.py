from math import tan, sin, cos, atan
from world import World
import math
import numpy as np
import pygame
from item import Item
from camera import Camera

sign = lambda x: math.copysign(1, x)


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
        self.camera = camera
        self.project_matrix = self.persp_proj_matrix(self.camera.fov, window_size[0]/window_size[1], 1, 300)

    def draw_scene(self, world, canvas):
        """
        Draws the frame and updates the display.
        """

        # Reset canvas to white
        background = (255, 255, 255)
        canvas.fill(background)

        view_matrix = self.view_matrix()

        self.draw_ground(canvas)

        # Draw all lines in the world
        for item in world.items:
            for line in item.lines:
                self.project_line(canvas, line[0], line[1], view_matrix, self.project_matrix, item.color)

        # Draw center point
        self.draw_point(canvas, (0,0, .01), (0, 200, 0))
        pygame.display.flip()



    def draw_ground(self, canvas):
        """
        Draws the ground. A rectangle based on camera angle
        """

        fov = self.camera.fov
        cur_angle = (self.camera.angle[1]+(fov/2))/fov
        if cur_angle < 0:
            cur_angle = 0
        if cur_angle > 1:
            cur_angle = 1
        height = cur_angle*canvas.get_height()
        pygame.draw.rect(canvas, (120,120,120), (0,canvas.get_height()-height,canvas.get_width(),canvas.get_height()), 0)


    def project_point(self, point_w, view_matrix, project_matrix, canvas):
        """
        Projects a point from world coordinates to projected coordinates.
        """

        # R3 points need an w value for perspective. Turn an [x, y, z] to [x, y, z, 1]
        if len(point_w) == 3:
            point_w = np.append(point_w, [1])

        # Project the points to the camera view and then a projection view
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
        Note: Intersections are incomplete, resulting in lines with one or both
        points off the canvas being displayed wrong. (Especially if one is
        behind the camera)
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
                    point0_p[1] = sign(point0_p[1])
                if point1_clip is None:
                    point1_p[1] = sign(point1_p[1])
                return point0_p, point1_p

        # If line is Horizontal
        if point0_p[1] == point1_p[1]:
            if -1 < point0_p[1] < 1:
                if point0_clip is None:
                    point0_p[0] = sign(point0_p[0])
                if point1_clip is None:
                    point1_p[0] = sign(point1_p[0])
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


    def project_line(self, canvas, point0_w, point1_w, view_matrix, project_matrix, color):
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

        self.draw_line(canvas, point0_can, point1_can, color)


    def norm_to_canvas_coord(self, canvas, point_p):
        return((point_p[0] * canvas.get_width()) + canvas.get_width()/2, (point_p[1] * canvas.get_height()) + canvas.get_height()/2, point_p[2])


    def draw_point(self, canvas, point_p, color):
        """
        Draw a point given projected coordinates.
        """

        if clip_point(point_p) is not None:
            point_can = self.norm_to_canvas_coord(canvas, point_p)
            canvas.set_at((int(point_can[0]), canvas.get_height() - int(point_can[1])), color)


    def draw_point_canvas(self, canvas, point_can, color, size=1):
        """
        Draw a point given canvas coordinates.
        """

        for i in range(size):
            for j in range(size):
                canvas.set_at((int(point_can[0]) + i, canvas.get_height() - int(point_can[1]) + j), color)


    def draw_line(self, canvas, point0_can, point1_can, color):
        """
        Draw line between two points, given in canvas coordinates.
        """

        if point0_can is None or point1_can is None:
            return

        x = point0_can[0]
        y = point0_can[1]
        z = point0_can[2]

        # Single Point
        if int(point0_can[0]) == int(point1_can[0]) and int(point0_can[1]) == int(point1_can[1]):
            # print("Single point at {} {} {}".format(x, y, z))
            self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color)
            return

        # Vertical line
        if abs(point0_can[0]-point1_can[0]) < 2.5:
            # print("Vertical Line", x, int(point0[1]) - int(point1[1]))
            dz = (point1_can[2] - point0_can[2]) / (point1_can[1] - point0_can[1])

            for y in range(int(point0_can[1]), int(point1_can[1])):
                if z > .01:
                    self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color)
                z += dz
            return

        # Horizontal line
        if abs(point0_can[1] - point1_can[1]) < 2.5:
            # print("Horizontal Line")
            dz = (point1_can[2] - point0_can[2]) / (point1_can[0] - point0_can[0])

            for x in range(int(point0_can[0]), int(point1_can[0])):
                if z > .01:
                    self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color)
                z += dz
            return

        dx = (point1_can[0] - point0_can[0]) / (point1_can[1] - point0_can[1])
        dy = (point1_can[1] - point0_can[1]) / (point1_can[0] - point0_can[0])

        # Slope between Pi/4 and -Pi/4
        if abs(dx) > abs(dy):
            # dz depends on x
            dz = (point1_can[2] - point0_can[2]) / (point1_can[0] - point0_can[0])

            for x in range(int(point0_can[0]), int(point1_can[0])):
                self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color)

                y += dy
                z += dz

        # Slope more up or down
        else:
            # dz depends on y
            dz = (point1_can[2] - point0_can[2]) / (point1_can[1] - point0_can[1])

            for y in range(int(point0_can[1]), int(point1_can[1])):
                self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color)
                x += dx
                z += dz


    def persp_proj_matrix(self, fov, aspect, znear, zfar):
        """
        Returns a perspective projection matrix from the given parameters.
        This is a rectangular frustum, which remaps world coordinates into a cube between -1 and 1
        """
        # Scale of x axis
        a = aspect * (1 / tan(fov * .5))

        # Scale of y axis
        b = 1 / tan(fov * .5)

        # Remaps z to [0,1], for z-index
        c = zfar / (zfar - znear)

        # Sets w to z
        d = 1

        # Moves z up to fit in znear
        e = -(znear * zfar) / (zfar - znear)

        return np.array([[a, 0, 0, 0],
                         [0, b, 0, 0],
                         [0, 0, c, d],
                         [0, 0, e, 0]])


    def view_matrix(self):
        """
        Returns a view matrix.
        Transforms view coordinates to make the camera located at (0,0,0) and pointed in the positive z direction.
        """
        sinYaw = sin(self.camera.angle[0])
        cosYaw = cos(self.camera.angle[0])
        sinPitch = sin(self.camera.angle[1])
        cosPitch = cos(self.camera.angle[1])

        # The axis vectors to point in the direction of the camera
        xaxis = (cosYaw, 0, -sinYaw)
        yaxis = (sinYaw * sinPitch, cosPitch, cosYaw * sinPitch)
        zaxis = (sinYaw * cosPitch, -sinPitch, cosPitch * cosYaw)

        # First 3 rows do rotation, the 4th row (which gets multiplied by 1) does translation
        arr =  np.array([[xaxis[0],                     yaxis[0],                   zaxis[0],                0],
                         [xaxis[1],                     yaxis[1],                   zaxis[1],                0],
                         [xaxis[2],                     yaxis[2],                   zaxis[2],                0],
                         [-np.dot(xaxis, self.camera.pos),   -np.dot(yaxis, self.camera.pos), -np.dot(zaxis, self.camera.pos), 1]])

        return arr
