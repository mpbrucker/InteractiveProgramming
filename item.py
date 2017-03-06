import numpy as np
from math import sin, cos, pi
from stl import mesh
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
# Uncomment this line and change it if the default display backend doesn't work with matplotlib:
# matplotlib.use('GTK3Cairo')
import matplotlib.pyplot as plt


class Item():

    def __init__(self, file_name, world_coords, orientation, scale, color=(255, 0, 0)):
        """
        Initializes a new item at the coordinates (x,y,z).
        """
        # Imports an STL file and extracts the points from it
        self.vecs = self.model_to_points(file_name)

        # Get the rotation matrix using the rotations about the x, y, and z axes
        self.world_points = self.get_transformed_points(self.vecs, world_coords, orientation, scale)
        self.color = color  # Set the color of the object
        self.location = world_coords  # The canonical location of the object

    def __str__(self):
        return "Position in world: ({}, {}, {})".format(self.location[0], self.location[1], self.location[2])

    def model_to_points(self, file_name):
        """
        Returns a list of triangles, each of which is composed of 3D points, based on a file_name
        """
        obj_mesh = mesh.Mesh.from_file(file_name)
        return obj_mesh.vectors

    def get_transformed_points(self, points, coords, orientation, scale):
        """
        Returns the points of the object as translated by coords and rotated by orientation
        """
        # Combines the translation and rotation matrices
        transform = self.get_translation_matrix(coords).dot(self.get_rotation_matrix(orientation).dot(self.get_scale_matrix(scale)))
        new_points = np.zeros(points.shape)  # The matrix of transformed points
        new_points = [np.array([transform.dot(np.append(point, [1])) for point in triangle]) for triangle in points]
        return new_points

    def get_scale_matrix(self, scale):
        ident = np.identity(4)
        for x in range(3):
            ident[x, x] = scale
        return ident

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
        """
        Displays the object using matplotlib. Useful for debugging.
        """
        fig = plt.figure()
        vectors = self.vecs
        ax = fig.add_subplot(111, projection='3d')
        for points in vectors:
            x = points[:, 0]
            y = points[:, 1]
            z = points[:, 2]
            ax.plot(x, y, z)

        world_vectors = self.world_points
        for points in world_vectors:
            x2 = points[:, 0]
            y2 = points[:, 1]
            z2 = points[:, 2]
            ax.plot(x2, y2, z2)

        ax.set_xlim([0, 10])
        ax.set_ylim([0, 10])
        ax.set_zlim([0, 10])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()

# if __name__ == "__main__":
    # item = Item('Cylinder.stl', (5, 1, 7), (90, 30, 0), 4)
    # item.display_model()
