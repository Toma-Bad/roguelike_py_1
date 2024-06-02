import numpy as np


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
        ("transparent", bool),
        ("dark", bool),
        ("explored", bool),
        ("sprite", sprite_dt)
    ]
)

def make_blt_sprite(**kwargs):
    char = kwargs.setdefault('char','X')
    fg_color = kwargs.setdefault('fg_color',[255,255,255,255])
    bg_color = kwargs.setdefault('bg_color', [255, 255, 255, 255])

    try:
        return np.array(
            [(ord(char),
            blt.color_from_argb(*fg_color),
            blt.color_from_argb(*bg_color)),],
            dtype=sprite_dt
        )
    except:
        return np.array(
            [(ord(char),
            blt.color_from_name(fg_color),
            blt.color_from_name(bg_color)),],
            dtype=sprite_dt
        )

def make_blt_tile(**kwargs):
    walkable = kwargs.setdefault('walkable',True)
    dark = kwargs.setdefault('dark', True)
    transparent = kwargs.setdefault('transparent', True)
    explored = kwargs.setdefault('explored', True)
    sprite = kwargs.setdefault('sprite',make_blt_sprite())
    return np.array(
        [(walkable, transparent, dark, explored,sprite),],
        dtype=tile_dt
    )



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

