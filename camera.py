from math import sin, cos, pi


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
