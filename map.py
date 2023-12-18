
gf_tile_dt = np.dtype([("ch", np.uint32),
                       ("fg", np.uint32),
                       ("bg", np.uint32)]
                      )

gf_tile_dt_3B =  np.dtype([("ch", np.uint32),
                       ("fg", '4B'),
                       ("bg", '4B')]
                      )


def gf_Tile(char, fgcolor, bgcolor):
    return np.array((ord(char), blt.color_from_name(fgcolor), blt.color_from_name(bgcolor)), dtype=gf_tile_dt)

def gf_Tile3B(char,fgcolor,bgcolor):
    return np.array((ord(char), blt.color_from_argb(*fgcolor), blt.color_from_argb(*bgcolor)), dtype=gf_tile_dt)

tile_dt = np.dtype([("walkable", bool), ("transparent", bool), ("dark", bool), ("explored", bool), ("gf_tile", gf_tile_dt)])

tile_dt_3B = np.dtype([("walkable", bool), ("transparent", bool), ("dark", bool), ("explored", bool), ("gf_tile", gf_tile_dt)])

def Tile(walkable=True, transparent=True, dark=False, explored = True, gf_tile=None):
    return np.array((walkable, transparent, dark, explored, gf_tile), dtype=tile_dt)

def Tile3B(walkable=True, transparent=True, dark=False, explored = True, gf_tile=None):
    return np.array((walkable, transparent, dark, explored, gf_tile), dtype=tile_dt_3B)
