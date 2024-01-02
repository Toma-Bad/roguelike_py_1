import json
from types import SimpleNamespace
import numpy as np


class BaseObject:
    def __init__(self, position, *components):
        self.id = id(self)
        self.position = position
        self.component = SimpleNamespace(**{type(_c).__name__: _c for _c in components})
        self.contained_by = None

    @property
    def _iter_contained_by(self):
        if self.contained_by is not None:
            yield self.contained_by
            yield from self.contained_by._iter_contained_by()

    @property
    def contained_by_all(self):
        return [_ for _ in self._iter_contained_by]

    def add_component(self, *components):
        self.component.__dict__.update({type(_c).__name__: _c for _c in components})

    def remove_component(self, component_name):
        try:
            self.component.__delattr__(component_name)
        except Exception as e:
            print(e)


class Scene:
    def __init__(self, scene_width, scene_height):
        self.ids = dict()
        self.obj_positions = dict()
        self.obj_type = dict()
        self.obj_components = dict()
        self.obj_loc_arr = np.empty((scene_width, scene_height), dtype=object)

    def spawn_object(self, base_object):
        ...
#use sets instead of lists to hold all this crap

    def rem_obj_position(self, base_object: BaseObject):
        if base_object.id not in self.ids:
            raise Exception("object not in scene!")
        if base_object.position in self.obj_positions:
            if self.obj_positions[base_object.position] == {base_object}:
                del self.obj_positions[base_object.position]
            elif base_object in self.obj_positions[base_object.position]:
                self.obj_positions[base_object.position].remove(base_object)

    def add_obj_position(self, base_object: BaseObject, new_position):
        if base_object.id not in self.ids:
            raise Exception("object not in scene!")
        if base_object.position != new_position:
            base_object.position = new_position
            if base_object.position in self.obj_positions:
                self.obj_positions[base_object.position].add(base_object)
            else:
                self.obj_positions[base_object.position] = {base_object}

    def update_obj_position(self, base_object: BaseObject, new_position):
        self.rem_obj_position(base_object)
        self.add_obj_position(base_object, new_position)

        if "Container" in base_object.component.__dict__:
            for _obj in base_object.component.Container.storage:
                self.update_obj_position(_obj, new_position)

    def add_to_db(self, base_object):
        self.ids[base_object.id] = base_object
        if base_object.position in self.obj_positions:
            self.obj_positions[base_object.position].add(base_object)
        else:
            self.obj_positions[base_object.position] = {base_object}
        if type(base_object).__name__ in self.obj_type:
            self.obj_type[type(base_object).__name__].add(base_object)
        else:
            self.obj_type[type(base_object).__name__] = {base_object}
        for _c in base_object.component.__dict__:
            if _c in self.obj_components:
                self.obj_components[_c].add(base_object)
            else:
                self.obj_components[_c] = {base_object}

    def rem_fr_db(self, base_object):
        if base_object.id not in self.ids:
            print('object not in scene')
            return 0
        else:
            del self.ids[base_object.id]
            if base_object.position in self.obj_positions:
                if self.obj_positions[base_object.position] == {base_object}:
                    del self.obj_positions[base_object.position]
                elif base_object in self.obj_positions[base_object.position]:
                    self.obj_positions[base_object.position].remove(base_object)
            if type(base_object).__name__ in self.obj_type:
                if self.obj_type[type(base_object).__name__] == {base_object}:
                    del self.obj_positions[base_object.position]
                elif base_object in self.obj_type[type(base_object).__name__]:
                    self.obj_type[type(base_object).__name__].remove(base_object)
            for _c in base_object.component.__dict__:
                if _c in self.obj_components:
                    if self.obj_components[_c] == {base_object}:
                        del self.obj_components[_c]
                    elif base_object.id in self.obj_components[_c]:
                        self.obj_components[_c].remove(base_object)

    def rm_comp_from_obj(self, base_object: BaseObject, component_name: str):
        if component_name in base_object.component.__dict__:
            base_object.remove_component(component_name)
            if component_name in self.obj_components:
                if self.obj_components[component_name] == {base_object}:
                    del self.obj_components[component_name]
                elif base_object.id in self.obj_components[component_name]:
                    self.obj_components[component_name].remove(base_object)

    def add_comp_to_obj(self, base_object: BaseObject, component_instance):
        base_object.add_component(component_instance)
        component_name = type(component_instance).__name__
        if component_name in self.obj_components:
            self.obj_components[component_name].add(base_object)
        else:
            self.obj_components[component_name] = {base_object}


class BaseComponent:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def load_from_file(cls, filename):
        with open(filename) as fin:
            data_dict = json.load(fin)
        return cls(**data_dict)


class BasicProps(BaseComponent):
    def __init__(self, **basic_properties):
        self.__dict__.update(basic_properties)


class Container(BaseComponent):

    def __init__(self, *items: BaseObject):
        self.storage = set(items)

    @property
    def weight(self):
        return sum([_i.component.BasicProps.weight for _i in self.storage])


class Modifiers:
    def __init__(self, **modifiers):
        self.__dict__.update(modifiers)


class BasicRace:
    def __init__(self, racetype, **modifiers):
        self.racetype = racetype
        self.modifiers = Modifiers(**modifiers)


class Orc(BasicRace):
    def __init__(self):
        super().__init__("orcish", hp=2, strength=5)


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
    #ee1 = Entities("bob",(1,1),BasicProps(),Orc())
    #ee2 = Entities("jim",(2,1),BasicProps(strength=12),Orc())
    ob1 = BaseObject((4, 5),
                     BasicProps(weight=40, height=100, strength=15, dexterity=20, constitution=10),
                     Orc())
    ob2 = BaseObject((4, 6),
                     BasicProps(weight=40, height=100, strength=17, dexterity=10, constitution=14),
                     Orc())
    axe = BaseObject((4, 5),
                     BasicProps(weight=40, damage_min=1, damage_max=7))

    sc = Scene(100, 100)
    sc.add_to_db(ob1)
    sc.add_to_db(ob2)
    sc.add_to_db(axe)
    sc.add_comp_to_obj(ob1, Container(axe))
