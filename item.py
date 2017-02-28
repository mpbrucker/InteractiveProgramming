import numpy as np
import matplotlib
from math import sin, cos, pi
from numpy import deg2rad as rad
from mpl_toolkits.mplot3d import Axes3D
# Uncomment this line and change it if the default display backend doesn't work with matplotlib:
matplotlib.use('GTK3Cairo')
import matplotlib.pyplot as plt


class Item():

    def __init__(self, world_coords, orientation):
        """
        Initializes a new item at the coordinates (x,y,z).
        """
        # These points will probably be generated differently at some time in the future
        self.points = np.array([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0], [0, 0, 0]])

        # Get the rotation matrix using the rotations about the x, y, and z axes

        self.world_points = self.get_transformed_points(self.points, world_coords, orientation)

    def __str__(self):
        return "\n".join(["Vertex: ({}, {}, {})".format(point[0], point[1], point[2]) for point in self.points])

    def get_transformed_points(self, points, coords, orientation):
        """

        """
        translation = self.get_translation_matrix(coords)
        transform = translation.dot(self.get_rotation_matrix(orientation))
        return np.array([transform.dot(np.append(point, [1]))[0:3] for point in points])

    def get_translation_matrix(self, world_coords):
        """
        Returns a 4x4 translation matrix to transform the points.
        """
        transform = np.identity(4)  # Generate the identity matrix
        coords = np.array(world_coords)
        transform[0:3, 3] = coords  # Fill the values of the transformation matrix
        return transform

    def get_rotation_matrix(self, orient):
        """
        Returns a rotation matrix for a given theta about the x, y, and z axes
        """
        x, y, z = orient
        cosd = lambda theta: cos(theta*(pi/180))  # Lambdas will make this easier
        sind = lambda theta: sin(theta*(pi/180))
        # Returns the rotation matrix
        return np.array([[cosd(y)*cosd(z), -cosd(y)*sind(z), sind(y), 0],
                        [cosd(x)*sind(y)+sind(x)*sind(y)*cosd(z), cosd(x)*cosd(z)-sind(x)*sind(y)*sind(z), -sind(x)*cosd(y), 0],
                        [sind(x)*sind(z)-cosd(x)*sind(y)*cosd(z), sind(x)*cosd(z) + cosd(x)*sind(y)*sind(z), cosd(x)*cosd(y), 0],
                        [0, 0, 0, 1]])

    def display_model(self):
        fig = plt.figure()
        points = self.points
        ax = fig.add_subplot(111, projection='3d')
        x = points[:,0]
        y = points[:,1]
        z = points[:,2]

        x2 = self.world_points[:,0]
        y2 = self.world_points[:,1]
        z2 = self.world_points[:,2]

        ax.plot(x, y, z)
        ax.plot(x2, y2, z2)
        ax.set_xlim([0, 10])
        ax.set_ylim([0, 10])
        ax.set_zlim([0, 10])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()

    def model_to_points():
        pass


item = Item((5, 6, 7), (90, 0, 0))
item.display_model()
