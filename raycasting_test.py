import numpy as np
from math import cos, atan2, sin, pi, floor, hypot, ceil
import pygame as pg
import matplotlib
# Uncomment this line and change it if the default display backend doesn't work with matplotlib:
matplotlib.use('GTK3Cairo')
import matplotlib.pyplot as plt


CIRCLE = 360
DEG = pi/180
RAD = 180/pi
FOV = pi*0.4
RESOLUTION = 100


class Player():
    def __init__(self, x=0, y=0, direction=45):
        self.x_pos = x
        self.y_pos = y
        self.theta = direction

    def move(self, dx, dy):
        self.x_pos += dx;
        self.y_pos += dy;

    def rotate(self, angle):
        self.theta = (self.theta + angle) % CIRCLE


class Map():
    def __init__(self, start_x=0, start_y=0, start_dir=45):
        self.map = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
                             ])
        self.player = Player(start_x, start_y, start_dir)

    def is_wall(self, x, y):
        if 9-y < 0:
            return True
        try:
            # print("FloorX: {}, FloorY: {}".format(floor(x),9-floor(y)))
            return bool(self.map[9-floor(y)][floor(x)])
        except IndexError:
            return True

    def cast_ray(self, angle):
        dist = 0
        cur_x = self.player.x_pos
        cur_y = self.player.y_pos
        while True:
            try:
                next_x = self.step(cur_x, cur_y, angle)
                next_y = self.step(cur_x, cur_y, angle, invert=True)
                if next_x[2] < next_y[2]:
                    cur_x = next_x[0]
                    cur_y = next_x[1]
                    dist += next_x[2]
                else:
                    not self.is_wall(cur_x, cur_y)
                    cur_x = next_y[0]
                    cur_y = next_y[1]
                    dist += next_y[2]
                # print("Current pos: {}, {}".format(cur_x, cur_y))
                if self.is_wall(cur_x, cur_y):
                    break
            except IndexError:
                return None
        # print("Final pos: {}, {}".format(cur_x, cur_y))
        if cur_x == 10 or cur_y == 10:
            return 1000
        else:
            return dist

    def step(self, in_x, in_y, theta, invert=False):
        rise = sin(theta*DEG) if not invert else cos(theta*DEG)
        run = cos(theta*DEG) if not invert else sin(theta*DEG)
        x, y = (in_y, in_x) if invert else(in_x, in_y)
        dx = floor(x+1)-x if run > 0 else ceil(x-1)-x
        try:
            dy = dx*(rise/run)
        except ZeroDivisionError:
            dx = 0
            dy = floor(y+1)-y if run > 0 else ceil(y-1)-y
        next_x = y+dy if invert else x+dx
        next_y = x+dx if invert else y+dy
        # print("{}, {}".format(next_x, next_y))
        length = hypot(dx, dy)
        return [next_x, next_y, length]

    def spray_points(self):
        x = []
        y = []
        for theta in range(0,90):
            dist = self.cast_ray(theta)
            x.append(dist*cos(theta*DEG))
            y.append(dist*sin(theta*DEG))
        scatter = plt.scatter(x,y)
        plt.xlim(0,10)
        plt.ylim(0,10)
        plt.show()

    def draw_points(self):
        screen = pg.display.set_mode((500,500))
        ind = 0
        thetas = np.arange(70,0,-90/500)
        for theta in thetas:
            dist = self.cast_ray(theta)
            height = self.project(dist, theta)
            print(height)
            pg.draw.rect(screen,(255,255,255),(ind, 500-(height/2), 1, height))
            ind += 1
        while True:
            pg.display.update()


    def project(self, dist, angle):
        z = dist * cos(angle*DEG)
        if 500/float(z) > 500:
            return 500
        else:
            return 500/float(z)





if __name__ == '__main__':
    load_map = Map()
    # load_map.spray_points()
    load_map.draw_points()
