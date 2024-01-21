import json
from types import SimpleNamespace
import numpy as np
import copy
from bearlibterminal import terminal as blt

gf_tile_dt = np.dtype([("ch", np.uint32),
                       ("fg", '4B'),
                       ("bg", '4B')])

tile_dt = np.dtype([("walkable", bool),
                    ("transparent", bool),
                    ("dark", bool),
                    ("explored", bool),
                    ("gf_tile", gf_tile_dt)])


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


def tile(*args):
    return np.array(*args, dtype=tile_dt)


def sprite(*args):
    return np.array(*args, dtype=gf_tile_dt)


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


class BaseComponent:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


    @classmethod
    def load_from_file(cls, filename):
        with open(filename) as fin:
            data_dict = json.load(fin)
        return cls(**data_dict)


class BaseObject:
    def __init__(self, position, *components: BaseComponent):
        self.id = id(self)
        self.position = position
        self.component = SimpleNamespace(**{type(_c).__name__: _c for _c in components})
        self.contained_by = None

    def _iter_contained_by(self):
        if self.contained_by is not None:
            yield self.contained_by
            yield from self.contained_by._iter_contained_by()

    def contained_by_all(self):
        return [_ for _ in self._iter_contained_by()]+[None]

    def add_component(self, *components):
        self.component.__dict__.update({type(_c).__name__: _c for _c in components})

    def remove_component(self, component_name):
        try:
            self.component.__delattr__(component_name)
        except Exception as e:
            print(e)


class BaseBlock(BaseObject):
    def __init__(self, position, *components: BaseComponent):
        super().__init__(position, *components)


class BaseEntity(BaseObject):
    def __init__(self, position, *components: BaseComponent):
        super().__init__(position, *components)
        self.energy = 100


class BaseItem(BaseObject):
    def __init__(self, position, *components: BaseComponent):
        super().__init__(position, *components)


class SpriteComponent(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)
        self._keys = kwargs.keys()
        self.sprite = sprite(*[kwargs[_name] for _name in gf_tile_dt.names])

    def __setattr__(self, key, value):
        if key == '_keys':
            super().__setattr__(key, value)
        elif key in self._keys:
            super().__setattr__(key, value)
            self.sprite = sprite(*[self.__dict__[_name] for _name in gf_tile_dt.names])
        else:
            super().__setattr__(key, value)


class TileComponent(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)
        self._keys = kwargs.keys()
        self.tile = tile(*[kwargs[_name] for _name in tile_dt.names])

    def __setattr__(self, key, value):
        if key == '_keys':
            super().__setattr__(key, value)
        elif key in self._keys:
            super().__setattr__(key, value)
            self.tile = tile(*[self.__dict__[_name] for _name in tile_dt.names])
        else:
            super().__setattr__(key, value)


class BasicProps(BaseComponent):
    def __init__(self, **basic_properties):
        super().__init__()
        self.__dict__.update(basic_properties)

class Movement(BaseComponent):
    def __init__(self, base_cost=100, **basic_properties):
        super().__init__()
        self.base_cost = base_cost
        self.__dict__.update(basic_properties)
class Container(BaseComponent):
    def __init__(self, *items: BaseObject):
        super().__init__()
        self.storage = set(items)

    @property
    def weight(self):
        return sum([_i.component.BasicProps.weight for _i in self.storage])


class TileMap:
    def __init__(self, width=128, height=128, layer=0):

        self.np_array = np.zeros((width, height), dtype=tile_dt)
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
        self.np_array[obj.position]['gf_tile'] = obj.component.SpriteComponent.sprite

    def rem_obj(self, obj: BaseObject):
        self.np_array[obj.position] = 0


class MapRenderer:
    def __init__(self, *tilemaps: TileMap):
        #the current maps update as the game runs
        #the render tilemaps update when seen
        #by the player only
        self.current_tilemaps = tilemaps
        self.render_tilemaps = copy.deepcopy(tilemaps)
        self.render_layers = {_rt.layer: _rt for _rt in self.render_tilemaps}
        self._trans_map = np.zeros_like(tilemaps[0])
        self._fov_map = None

    @property
    def trans_map(self):
        self._trans_map = np.any([_tilemap.np_array['transparent'] for _tilemap in self.current_tilemaps],
                                 axis=0)
        return self._trans_map

    @property
    def fov_map(self):
        return self._fov_map

    @fov_map.setter
    def fov_map(self, fovmap):
        self._fov_map = fovmap
        for _current_tilemap, _render_tilemap in zip(self.current_tilemaps, self.render_tilemaps):
            not_fovmap = np.logical_not(fovmap)
            _current_tilemap.np_array['dark'] = not_fovmap
            _render_tilemap.np_array[not_fovmap] = _current_tilemap.np_array[not_fovmap]
            _current_tilemap.np_array['explored'] = np.logical_or(fovmap,
                                                                  _current_tilemap.np_array['explored'])
            _render_tilemap.np_array['explored'] = np.logical_or(fovmap,
                                                                 _render_tilemap.np_array['explored'])

    def render(self):
        for key in sorted(self.render_layers.keys()):
            map_to_render = self.render_layers[key].np_array['gf_tile']
            darkmap = np.where(map_to_render['dark'] == True)
            map_to_render['fg'][darkmap] = (map_to_render['gf_tile']['fg'][darkmap]
                                            // np.array([2, 1, 1, 1]))
            map_to_render['bg'][darkmap] = (map_to_render['gf_tile']['bg'][darkmap]
                                            // np.array([2, 1, 1, 1]))
            unexmap = np.where(map_to_render['explored'] == False)
            map_to_render['fg'][unexmap] = (map_to_render['gf_tile']['fg'][unexmap]
                                            * np.array([1, 0, 0, 0]))
            map_to_render['bg'][unexmap] = (map_to_render['gf_tile']['bg'][unexmap]
                                            * np.array([1, 0, 0, 0]))
            blt.layer(key)
            blt.put_np_array(0,
                             0,
                             self.render_layers[key].np_array['gf_tile'],
                             'ch',
                             'fg',
                             'bg')


class Scene:
    def __init__(self, scene_width, scene_height):
        self.ids = dict()
        self.obj_positions = SetDict()
        self.obj_type = SetDict()
        self.obj_components = SetDict()
        self.comp_timers = SetDict()
        self.obj_loc_arr = np.empty((scene_width, scene_height), dtype=object)
        self.obj_in_container = SetDict()
        self.terrain_map = TileMap(scene_width, scene_height, layer=0)
        self.block_map = TileMap(scene_width, scene_height, layer=1)
        self.item_map = TileMap(scene_width, scene_height, layer=2)
        self.entity_map = TileMap(scene_width, scene_height, layer=3)
        self.map_renderer = MapRenderer(self.terrain_map,
                                        self.block_map,
                                        self.item_map,
                                        self.entity_map)

    def update_block_map(self):
        self.block_map.set_set(self.obj_type['BaseBlock'])

    def update_item_map(self):
        self.item_map.set_set(self.obj_type['BaseItem'])

    def update_entity_map(self):
        self.entity_map.set_set(self.obj_type['BaseEntity'])

    def update_map(self):
        self.update_entity_map()
        self.update_item_map()
        self.update_block_map()

    def move_obj(self, base_object: BaseObject, new_position):
        old_position = base_object.position
        self.obj_positions.move(old_position, new_position, base_object)
        if "Container" in base_object.component.__dict__:
            for _obj in base_object.component.Container.storage:
                self.move_obj(_obj, new_position)
                _obj.position = new_position
        base_object.position = new_position

    def add_obj(self, base_object: BaseObject, at_position=None):
        if at_position:
            base_object.position = at_position
        self.ids[base_object.id] = base_object
        self.obj_positions.add(base_object.position, base_object)
        self.obj_type.add(type(base_object).__name__, base_object)
        if base_object.contained_by:
            self.obj_in_container.add(base_object.id, base_object.contained_by)

        for _c in base_object.component.__dict__:
            self.obj_components.add(_c, base_object)

    def rem_obj(self, base_object: BaseObject):
        if base_object.id not in self.ids:
            print('object not in scene')
            return 0
        else:
            del self.ids[base_object.id]
        self.obj_positions.remove(base_object.position, base_object)
        self.obj_type.remove(type(base_object).__name__, base_object)
        if base_object.contained_by:
            self.obj_in_container.remove(base_object.id, base_object.contained_by)
        if "Container" in base_object.component.__dict__:
            for _obj in base_object.component.Container.storage:
                _obj.contained_by = _obj.contained_by_all()[1]
        for _c in base_object.component.__dict__:
            self.obj_components.remove(_c, base_object)

    def add_component(self, base_object: BaseObject, *components: BaseComponent, **kcomponents: BaseComponent):
        if base_object.id not in self.ids:
            raise Exception(f"object not in scene!{base_object.id}")
        base_object.component.__dict__.update({type(_c).__name__: _c for _c in components})
        base_object.component.__dict__.update(kcomponents)
        for _c in components:
            self.obj_components.add(type(_c).__name__, base_object)
            if hasattr(_c,'timer'):
                self.comp_timers.add('timer',_c)
        for _c in kcomponents:
            self.obj_components.add(_c, kcomponents[_c])
            if hasattr(_c,'timer'):
                self.comp_timers.add('timer',kcomponents[_c])
    def remove_component(self, base_object: BaseObject, *components, **kcomponents):
        if base_object.id not in self.ids:
            raise Exception(f"object not in scene!{base_object.id}")

        base_object.component.__dict__.update(kcomponents)
        for _c in components:
            base_object.component.__delattr__(type(_c).__name__)
            self.obj_components.remove(type(_c).__name__, base_object)
            if hasattr(_c,'timer'):
                self.comp_timers.remove('timer',_c)
        for _c in kcomponents:
            base_object.component.__delattr__(_c)
            self.obj_components.remove(_c, kcomponents[_c])
            if hasattr(_c,'timer'):
                self.comp_timers.remove('timer',kcomponents[_c])
    
    def add_to_container(self, base_object_c: BaseObject, *base_objects: BaseObject):
        if "Container" not in base_object_c.component.__dict__:
            raise Exception(f"object {base_object_c} does not have a Container comp")
        base_object_c.component.Container.storage.update(base_objects)
        for base_object in base_objects:
            base_object.contained_by = base_object_c
            self.obj_in_container.add(base_object.id, base_object_c)

    def remove_from_container(self,
                              base_object_c: BaseObject,
                              *base_objects: BaseObject,
                              oneup_only=False):
        if "Container" not in base_object_c.component.__dict__:
            raise Exception(f"object {base_object_c} does not have a Container comp")
        base_object_c.component.Container.storage.difference_update(base_objects)
        for base_object in base_objects:
            if oneup_only:
                base_object.contained_by = base_object.contained_by_all()[1]
            else:
                base_object.contained_by = None
            self.obj_in_container.remove(base_object.id, base_object_c)


class BaseModifier(BaseComponent):
    def __init__(self,name: str, target_component: BaseComponent, **target_properties: tuple[str,int|bool]):
        super().__init__(name=name, target_component=target_component, target_properties=target_properties)



class MultiComponent(BaseComponent):
    def __init__(self, name: str, *components: BaseComponent):
        super().__init__(name=name, components=set(components))



class BasicTime:
    def __init__(self, turn=0):
        self.turn = turn
    def advance_time(self):
        self.turn += 1

class Timer(BaseComponent):
    def __init__(self, duration = 3,
                 basic_time: BasicTime = None):
        super().__init__()
        self.basic_time = basic_time
        self.start_turn = basic_time.turn
        self.end_turn = self.start_turn + duration

    @property
    def counter(self):
        return self.end_turn - self.basic_time.turn

    def isdone(self):
        return self.counter > 0
















class Entities:
    ids = dict()
    components = dict()
    positions = dict()

    def __init__(self, name, pos, *component_args):
        self.name = name
        self.pos = pos
        self.id = id(self)
        t_comp_dict = {type(_c).__name__: _c for _c in component_args}
        self.__dict__.update(t_comp_dict)
        Entities.ids[self.id] = self
        if pos in Entities.positions:
            Entities.positions[pos].append(self.id)
        else:
            Entities.positions[pos] = self.id


if __name__ == "__main__":
    #ee1 = Entities("bob", (1, 1), BasicProps(), Orc())
    #ee2 = Entities("jim", (2, 1), BasicProps(strength=12), Orc())
    #ob1 = BaseObject((4, 5),
    #                 BasicProps(weight=40, height=100, strength=15, dexterity=20, constitution=10),
    #                 Orc())
    #ob2 = BaseObject((4, 6),
    #                 BasicProps(weight=40, height=100, strength=17, dexterity=10, constitution=14),
    #                 Orc())
    #axe = BaseObject((4, 5),
    #                 BasicProps(weight=40, damage_min=1, damage_max=7))

    sc = Scene(100, 100)
