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

    # def gen_random_scene(self, min_val, max_val):
    #     objects = ['Cylinder.stl']
    #     for x in range(min_val, max_val):
    #         self.add_item(Item(choice(objects), (uniform(0,10), uniform(0,10), uniform(0,1)), (0,0,0), uniform(0.5, 5), color=(randint(0,255),randint(0,255), randint(0,255)))
