import numpy as np
from bearlibterminal import terminal as blt

sprite_dt = np.dtype(
    [
        ("ch", np.uint32),
        ("fg", np.uint32),
        ("bg", np.uint32)
    ]
)

tile_dt = np.dtype(
    [
        ("walkable", bool),
        ('opaque', bool),
        ("dark", bool),
        ("explored", bool),
        ("sprite", sprite_dt)
    ]
)

def make_blt_sprite(**kwargs):
    char = kwargs.setdefault('char','X')
    fg_color = kwargs.setdefault('fg_color',[255,255,255,255])
    bg_color = kwargs.setdefault('bg_color', [255, 255, 255, 255])
    if isinstance(char, str):
        char = ord(char)
    if isinstance(fg_color, np.uint32):
        pass
    elif isinstance(fg_color, str):
        fg_color = blt.color_from_name(fg_color)
    else:
        fg_color = blt.color_from_argb(*fg_color)
    if isinstance(bg_color, np.uint32):
        pass
    elif isinstance(bg_color, str):
        bg_color = blt.color_from_name(bg_color)
    else:
        bg_color = blt.color_from_argb(*bg_color)
    return np.array(
        [(char,
          fg_color,
          bg_color), ],
        dtype=sprite_dt
    )[0]

def make_blt_tile(**kwargs):
    walkable = kwargs.setdefault('walkable',True)
    dark = kwargs.setdefault('dark', True)
    opaque = kwargs.setdefault('opaque', True)
    explored = kwargs.setdefault('explored', True)
    sprite = kwargs.setdefault('sprite',make_blt_sprite())
    return np.array(
        [(walkable, opaque, dark, explored,sprite),],
        dtype=tile_dt
    )[0]



def multi_union(*args: set):
    if args:
        if len(args) > 1:
            result = args[0].union(args[1:])
        else:
            result = args[0]
    else:
        result = None
    return result


def multi_intersect(*args: set):
    if args:
        if len(args) > 1:
            result = args[0].intersection(args[1:])
        else:
            result = args[0]
    else:
        result = None
    return result



class SetDict(dict):
    def add(self, key, value):
        if key in self:
            if value in self[key]:
                return False
            else:
                self[key].add(value)
                return 2
        else:
            self[key] = {value}
            return 1

    def remove(self, key, value):
        if key in self:
            if {value} == self[key]:
                del self[key]
                return 1
            elif value in self[key]:
                self[key].remove(value)
                return 2
            else:
                return False

    def move(self, old_key, new_key, value):
        if old_key == new_key:
            return 0
        if self.remove(old_key, value) and self.add(new_key, value):
            return 1
        else:
            raise Exception("Not able to move value in set_dict!")

