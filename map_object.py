
from game_objects import BaseObject


from utils import *
class TileMap:
    def __init__(self, width=128, height=128, np_array = None, layer=0):

        self.width = width
        self.height = height
        if np_array is None:
            self.np_array = np.zeros((width, height), dtype=tile_dt)
        else:
            self.np_array = np_array
            self.width, self.height = np_array.shape
        self.layer = layer

    def add_set(self, obj_set: set[BaseObject]):
        for obj in obj_set:
            self.add_obj(obj)

    def set_set(self, obj_set: set[BaseObject]):
        self.np_array[:] = 0
        self.add_set(obj_set)

    def rem_set(self, obj_set: set[BaseObject]):
        for obj in obj_set:
            self.rem_obj(obj)

    def add_obj(self, obj: BaseObject):
        self.np_array[obj.position] = obj.components['tile'].tile

    def rem_obj(self, obj: BaseObject):
        self.np_array[obj.position] = 0




