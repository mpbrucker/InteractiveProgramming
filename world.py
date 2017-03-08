from item import Item
from random import choice, uniform, randint

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

    def gen_random_scene(self, min_val, max_val):
        """
        Places objects into the world. Number of objects generated is between min_val and max_val.
        """
        objects = ['teapot.stl']
        num_obj = randint(min_val, max_val)
        for x in range(num_obj):
            self.add_item(Item(choice(objects), (randint(30,50), randint(30,50), randint(30,50)), (-90,0,0), 1, color=(randint(0,255), randint(0,255), randint(0,255))))
