from math import tan, sin, cos, pi, sqrt
import numpy as np
import pygame
from item import Item


class Camera:
    # Position coordinates
    pos = [0, 0, 0]
    # Camera orientation. In rad
    angle = [0, 0, 0]
    fov = 0

    def __init__(self, init_pos=[0, 0, 0], init_angle=[0, 0, 0], init_fov=.5):
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


class Renderer:
    """
    The renderer class. Takes the camera, world, and canvas and draws the scene.
    """

    def draw_scene(self, world, camera, canvas):
        """
        Draws the frame and updates the display.
        """

        # Reset to white
        background = (255, 255, 255)
        canvas.fill(background)

        view_matrix = self.view_matrix(camera)
        project_matrix = self.persp_proj_matrix(camera.fov, canvas.get_width()/canvas.get_height(), .1, 1)

        # Draw center point
        self.draw_point(canvas, (canvas.get_width()/2,canvas.get_height()/2, 1), (0, 200, 0), 6)

        # test_lines = (((0,0,1,1),(1,10,10,1)), ((0,0,1,1),(10,10,10,1)))
        # for line in test_lines:
        #     self.draw_line(canvas, self.project_point(line[0], view_matrix, project_matrix, canvas), self.project_point(line[1], view_matrix, project_matrix, canvas), (0, 255, 0), 3)

        for item in world.get_objects():
            for tri in item.world_points:
                for point in tri:
                    transformed_point = self.project_point(point, view_matrix, project_matrix, canvas)
                    self.draw_point(canvas, transformed_point, (125, 0, 0), 6, point)


        # for item in world.get_objects():
        #     for idx, tri in enumerate(item.world_points):
        #         print("{}/{}".format(idx+1,len(item.world_points)))
        #         for idx, point in enumerate(tri):
        #             point2 = tri[(idx+1)%2]
        #             print(self.project_point(point, view_matrix, project_matrix, canvas))
        #             print(self.project_point(point2, view_matrix, project_matrix, canvas))
        #             self.draw_line(canvas, self.project_point(point, view_matrix, project_matrix, canvas), self.project_point(point2, view_matrix, project_matrix, canvas), (0, 255, 0), 3)

        pygame.display.flip()


    def project_point(self, point, view_matrix, project_matrix, canvas):
        # R3 points need an w value for perspective. Turn an [x, y, z] to [x, y, z, 1]
        if len(point) == 3:
            point = np.append(point, [1])

        # Project the points to the camera view and then a projection view

        # print("point:", point)
        xy = np.dot(point, view_matrix)
        # print("xyV:", xy)
        xy = np.dot(xy, project_matrix)

        # Makes the perspective happen. w is based on z, and adjusts x and y properly
        # The magic number makes the stretch in z smaller. Tweak to perfection. Can also be fixed in the projection matrix
        xy = xy/(xy[3]*.02)
        xy[0] = xy[0] + canvas.get_width() / 2
        xy[1] = xy[1] + canvas.get_height() / 2
        # print(xy)
        return xy

    # def draw_

    def draw_point(self, canvas, point, color, size=1, orig_coordinates=""):
        # # Label each point with world coordinates and current coordinates
        # basicfont = pygame.font.SysFont(None, 12)
        # text = basicfont.render(str(point) + "\n" + str(orig_coordinates), True, (0, 0, 0), (255, 255, 255))
        # textrect = text.get_rect()
        # textrect.centerx = point[0]
        # textrect.centery = canvas.get_height() - int(point[1]) + 5
        # canvas.blit(text, textrect)

        if point[2] > .01 and 0 <= point[0] <= canvas.get_height() and 0 <= point[1] <= canvas.get_width():
            # print(point)
            for i in range(size):
                for j in range(size):
                    canvas.set_at((int(point[0]) + i, canvas.get_height() - int(point[1]) + j), color)


    def dist(self, point0, point1):
        return sqrt((point0[0]-point1[0])**2 + (point0[1] - point1[1])**2)

    def middle(self, point0, point1):
        return [(point1[0] + (point0[0] - point1[0])/2), (point1[1] + (point0[1] - point1[1])/2), (point1[2] + (point0[2] - point1[2])/2), 1]

    def draw_line(self, canvas, point0, point1, color, size=1):
        """
        Draw line between two points.
        """

        dist = self.dist(point0, point1)
        if dist < 2:
            return

        middle_point = self.middle(point0, point1)
        if middle_point[2] > 0.01:
            self.draw_point(canvas, middle_point, color, size)

        try:
            self.draw_line(canvas, point0, middle_point, color, size)
            self.draw_line(canvas, middle_point, point1, color, size)
        except RuntimeError:
            return




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

        # Scale of x axis
        a = aspect * (1 / tan(fov * .5)) # Degrees to Rad

        # Scale of y axis
        b = 1 / tan(fov * .5) # Degrees to Rad

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

        # arr = np.array([[xaxis[0], xaxis[1], xaxis[2], -np.dot(xaxis, camera.pos)],
        #                 [yaxis[0], yaxis[1], yaxis[2], -np.dot(yaxis, camera.pos)],
        #                 [zaxis[0], zaxis[1], zaxis[2], -np.dot(zaxis, camera.pos)],
        #                 [       0,        0,        0,                         1 ]])

        return arr


class World:
    """
    Holds all objects in the world.
    """

    def __init__(self, items=[]):
        self.items = items

    def add_item(self, item):
        """
        Adds item to the world.
        """
        if item.__class__.__name__ == "Item":
            self.items.append(item)

    def get_objects(self):
        """
        Returns all objects in the world
        """
        return self.items

# if __name__ == "__main__":
#     window_size = (1000, 1000)
#     background = (255, 255, 255)
#
#     pygame.init()
#     canvas = pygame.display.set_mode(window_size, 0, 32)
#     clock = pygame.time.Clock()
#
#     camera = Camera(init_pos=[0,0,-1], init_angle=[0, 0, 0])
#     renderer = Renderer()
#     world = World()
#
#     while True:
#         print(camera)
#         renderer.draw_scene(world, camera, canvas)
#
#         # camera.pos[0] = camera.pos[0] + 5
#         # camera.pos[1] = camera.pos[1] + 5
#         camera.pos[2] = camera.pos[2] + .005
#         # camera.fov = camera.fov + 1
#         # camera.angle[0] = camera.angle[0] + .4
#
#
#         # print()
#         clock.tick(30)
