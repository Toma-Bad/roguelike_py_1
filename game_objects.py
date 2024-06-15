import json
from utils import *
class BaseObject:
    def __init__(self,position: (int,int) = None, components = [dict()], contained_by = None,):
        self.id = id(self)
        self.position = position
        self.components = dict()
        for _c in components:
            self.components.update(_c)
        self.contained_by = contained_by


    def _iter_contained_by(self):
        if self.contained_by is not None:
            yield self.contained_by
            yield from self.contained_by._iter_contained_by()

    def contained_by_all(self):
        return [_ for _ in self._iter_contained_by()]+[None]

class BaseBlock(BaseObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class BaseItem(BaseObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class BaseEntity(BaseObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.components['move_points'] = BaseComponent(
            name = "move_points",
            value=100
        )



class BaseComponent(dict):
    def __init__(
            self,
            name: str = '',
            type: str = '',
            description: str = '',
            **kwargs
    ):
        self['name'] = name
        self['description'] = description
        self['type'] = type
        self.update(kwargs)

    @classmethod
    def loadf(cls,filename: str = None):
        with open(filename,'r') as fin:
            data = json.load(fin)
            return cls(**data)

    @classmethod
    def loads(cls,json_string: str = None):
        data = json.loads(json_string)
        return cls(**data)


class TileComponent(BaseComponent):
    def __init__(
            self,
            char: str= "X",
            fg_color = (0,0,0,0),
            bg_color = (0,0,0,0),
            walkable = True,
            dark = False,
            explored = True,
            opaque = True,
            **kwargs
    ):
        super().__init__(
            name="tile",
            type="tile_dt"
        )
        self['walkable'] = walkable
        self['dark'] =  dark
        self['explored'] = explored
        self['opaque'] = opaque
        self['char'] = char
        self['fg_color'] = fg_color
        self['bg_color'] = bg_color
        self._sprite = make_blt_sprite(
            char=char,
            fg_color=fg_color,
            bg_color=bg_color
        )
        self.tile = make_blt_tile(
            walkable = walkable,
            dark = dark,
            explored = explored,
            opaque = opaque,
            sprite=self.sprite
        )

    @classmethod
    def from_tile(cls,tile):
        return cls(
            walkable = tile['walkable'],
            dark = tile['dark'],
            explored = tile['explored'],
            opaque = tile['opaque'],
            char=tile['sprite']['ch'],
            fg_color=tile['sprite']['fg'],
            bg_color=tile['sprite']['bg'],
        )

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key in self.keys() and all([_k in self.keys() for _k in ['char','bg_color','fg_color','walkable','opaque','explored','dark']]):
            self.sprite = make_blt_sprite(
                char=self['char'],
                fg_color=self['fg_color'],
                bg_color=self['bg_color']
            )
        if key in self.keys() and all([_k in self.keys() for _k in ['char','bg_color','fg_color','walkable','opaque','explored','dark']]):
            self.tile = make_blt_tile(
                walkable=self['walkable'],
                dark=self['dark'],
                explored=self['explored'],
                opaque=self['opaque'],
                sprite=self.sprite
            )

    @property
    def sprite(self):
        return self._sprite
    @sprite.setter
    def sprite(self,value):
        self._sprite = value
        self.tile = make_blt_tile(
            walkable=self['walkable'],
            dark=self['dark'],
            explored=['explored'],
            opaque=['opaque'],
            sprite=value
        )
