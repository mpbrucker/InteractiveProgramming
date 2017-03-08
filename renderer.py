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
    """

    def __init__(self, camera, window_size=(1000,1000)):
        self.camera = camera
        self.project_matrix = self.persp_proj_matrix(self.camera.fov, window_size[0]/window_size[1], 0.01, 100)

    def draw_scene(self, world, canvas):
        """
        Draws the frame and updates the display.
        """

        # print(camera.angle)
        # Reset to white
        background = (255, 255, 255)
        canvas.fill(background)

        view_matrix = self.view_matrix()

        self.draw_ground(canvas)

        # Draw center point

        for item in world.items:
            for line in item.lines:
                self.project_line(canvas, line[0], line[1], view_matrix, self.project_matrix, item.color)


            # for tri in item.world_points:
            #     # print("Tri:", tri)
            #     print(tri[0])
            #     self.project_line(canvas, tri[0], tri[1], view_matrix, self.project_matrix, (125, 0, 0))
            #     self.project_line(canvas, tri[1], tri[2], view_matrix, self.project_matrix, (125, 0, 0))
            #     self.project_line(canvas, tri[2], tri[0], view_matrix, self.project_matrix, (125, 0, 0))

                # for point in tri:
                #     transformed_point = self.project_point(point, view_matrix, self.project_matrix, canvas)
                #     self.draw_point(canvas, transformed_point, (125, 0, 0), 6)

        # test_lines = (((0,1,0,1),(1,0,0,1)),) #, ((0,0,1,1),(10,10,10,1)))
        # for line in test_lines:
        #     self.project_line(canvas, line[0], line[1], view_matrix, self.project_matrix, (125, 0, 0), 3)
        self.draw_point(canvas, (0,0, .01), (0, 200, 0), 6)
        pygame.display.flip()



    def draw_ground(self, canvas):
        fov = self.camera.fov
        cur_angle = (self.camera.angle[1]+(fov/2))/fov
        if cur_angle < 0:
            cur_angle = 0
        if cur_angle > 1:
            cur_angle = 1
        height = cur_angle*canvas.get_height()
        pygame.draw.rect(canvas, (120,120,120), (0,canvas.get_height()-height,canvas.get_width(),canvas.get_height()), 0)


    def project_point(self, point, view_matrix, project_matrix, canvas):
        # R3 points need an w value for perspective. Turn an [x, y, z] to [x, y, z, 1]
        if len(point) == 3:
            point = np.append(point, [1])

        # Project the points to the camera view and then a projection view
        # print(view_matrix)
        # print(project_matrix)

        # print("point:", point)
        xy = np.dot(point, view_matrix)
        # print("xyV:", xy)
        xy = np.dot(xy, project_matrix)
        # print("xyP:", xy)


        # Makes the perspective happen. w is based on z, and adjusts x and y properly
        if not xy[3] == 0:
            xy = xy/(xy[3])

        # print("xyN:", xy)

        return xy

    def cull_point(self, point):
        if -1 < point[0] < 1 and -1 < point[1] < 1 and -1 < point[2] < 1:
            return point
        else:
            return None

    def cull_line(self, point0, point1):
        point0_c = self.cull_point(point0)
        point1_c = self.cull_point(point1)

        if point0_c != None and point1_c != None:
            return point0, point1

        # If vertical
        if point0[0] == point1[0]:
            if -1 < point0[0] < 1:
                if point0_c == None:
                    point0[2] = sign(point0[2])
                return point0, point1


        if point0[0] > point1[0]:
            point_hold = point0
            point0 = point1
            point1 = point_hold

        # Find intercept
        slope = (point1[1] - point0[1]) / (point1[0] - point0[0])
        offset = point0[1] - slope*point0[0]
        line = lambda x: slope*x + offset

        # Todo: Fix Z
        if self.cull_point((-1, line(-1), 0),):
            point0 = (-1, line(-1), point0[2])

        return point0, point1


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

        point0_cull, point1_cull = self.cull_line(point0_p, point1_p)

        point0_can = self.norm_to_canvas_coord(canvas, point0_cull)
        point1_can = self.norm_to_canvas_coord(canvas, point1_cull)

        self.draw_line(canvas, point0_can, point1_can, color, 1)

    def norm_to_canvas_coord(self, canvas, point):
        return((point[0] * canvas.get_width()) + canvas.get_width()/2, (point[1] * canvas.get_height()) + canvas.get_height()/2, point[2])

    def draw_point(self, canvas, point, color, size=1):
        # print(point)
        if (-1 <= point[0] <= 1) and (-1 <= point[1] <= 1) and (.01 <= point[2] <= 1):
            point_canvas = self.norm_to_canvas_coord(canvas, point)
            # print("Draw:", point_canvas, "Size:", size)
            for i in range(size):
                for j in range(size):
                    canvas.set_at((int(point_canvas[0]) + i, canvas.get_height() - int(point_canvas[1]) + j), color)

    def draw_point_canvas(self, canvas, point, color, size=1):
        if 0 <= point[0] <= canvas.get_width() and 0 <= point[1] <= canvas.get_height():
            for i in range(size):
                for j in range(size):
                    canvas.set_at((int(point[0]) + i, canvas.get_height() - int(point[1]) + j), color)


    def draw_line(self, canvas, point0, point1, color, size=1):
        """
        Draw line between two points.
        """
        # print("Draw:", point0, point1)

        if point0 == None or point1 == None:
            # print("Draw_line, point is None")
            return

        x = point0[0]
        y = point0[1]
        z = point0[2]

        if int(point0[0]) == int(point1[0]) and int(point0[1]) == int(point1[1]):
            # print("Single point at {} {} {}".format(x, y, z))
            self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, 100)
            return

        # Vertical line
        if abs(point0[0]-point1[0]) < 2.5:
            # print("Vertical Line", x, int(point0[1]) - int(point1[1]))
            dz = (point1[2] - point0[2]) / (point1[1] - point0[1])

            for y in range(int(point0[1]), int(point1[1])):
                if z > .01:
                    self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, size)
                z += dz
            return

        # Horizontal line
        if abs(point0[1]-point1[1]) < 2.5:
            # print("Horizontal Line")
            dz = (point1[2] - point0[2]) / (point1[0] - point0[0])

            for x in range(int(point0[0]), int(point1[0])):
                if z > .01:
                    self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, size)
                z += dz
            return

        dx = (point1[0] - point0[0]) / (point1[1] - point0[1])
        dy = (point1[1] - point0[1]) / (point1[0] - point0[0])


        if dx < dy:
            # dz depends on x
            dz = (point1[2] - point0[2]) / (point1[0] - point0[0])

            # print("dy:", dy)
            for x in range(int(point0[0]), int(point1[0])):
                #print(x, y, z)
                y_draw = y
                if dy > 1:
                    while y_draw-y < int(dy) and y_draw < point1[1]:
                        self.draw_point_canvas(canvas, (int(x), int(y_draw), int(z)), color, size)
                        y_draw += 1
                else:
                    self.draw_point_canvas(canvas, (int(x), int(y), int(z)), color, size)

                y += dy
                z += dz

        else:
            # dz depends on y
            dz = (point1[2] - point0[2]) / (point1[1] - point0[1])

            for y in range(int(point0[1]), int(point1[1])):
                #print(x, y, z)
                x_draw = x
                if dx > 1:
                    while x_draw-x < int(dx) and x_draw < point1[0]:
                        self.draw_point_canvas(canvas, (int(x_draw), int(y), int(z)), color, size)
                        x_draw += 1
                else:
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


    def view_matrix(self):
        sinYaw = sin(self.camera.angle[0])
        cosYaw = cos(self.camera.angle[0])
        sinPitch = sin(self.camera.angle[1])
        cosPitch = cos(self.camera.angle[1])

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
                         [-np.dot(xaxis, self.camera.pos),   -np.dot(yaxis, self.camera.pos), -np.dot(zaxis, self.camera.pos), 1]])

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
        renderer.draw_scene(world, canvas)

        # camera.pos[0] = camera.pos[0] + 5
        # camera.pos[1] = camera.pos[1] + 5
        camera.pos[2] = camera.pos[2] + .005
        # camera.fov = camera.fov + 1
        # camera.angle[0] = camera.angle[0] + .4


        # print()
        clock.tick(30)
