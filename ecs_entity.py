import json
from types import SimpleNamespace
import numpy as np


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


class BaseObject:
    def __init__(self, position, *components):
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


class Scene:
    def __init__(self, scene_width, scene_height):
        self.ids = dict()
        self.obj_positions = SetDict()
        self.obj_type = SetDict()
        self.obj_components = SetDict()
        self.obj_loc_arr = np.empty((scene_width, scene_height), dtype=object)
        self.obj_in_container = SetDict()

    def update_obj_position(self, base_object: BaseObject, new_position):
        old_position = base_object.position
        self.obj_positions.move(old_position, new_position, base_object)
        if "Container" in base_object.component.__dict__:
            for _obj in base_object.component.Container.storage:
                self.update_obj_position(_obj, new_position)
                _obj.position = new_position
        base_object.position = new_position

    def add_obj(self, base_object: BaseObject):
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
        for _c in kcomponents:
            self.obj_components.add(_c, kcomponents[_c])

    def remove_component(self, base_object: BaseObject, *components, **kcomponents):
        if base_object.id not in self.ids:
            raise Exception(f"object not in scene!{base_object.id}")

        base_object.component.__dict__.update(kcomponents)
        for _c in components:
            base_object.component.__delattr__(type(_c).__name__)
            self.obj_components.remove(type(_c).__name__, base_object)
        for _c in kcomponents:
            base_object.component.__delattr__(_c)
            self.obj_components.remove(_c, kcomponents[_c])
    
    def add_to_container(self, base_object_c: BaseObject, *base_objects: BaseObject):
        if "Container" not in base_object_c.component.__dict__:
            raise Exception(f"object {base_object_c} does not have a Container comp")
        base_object_c.component.Container.storage.update(base_objects)
        for base_object in base_objects:
            base_object.contained_by = base_object_c
            self.obj_in_container.add(base_object.id, base_object_c)

    def remove_from_container(self, base_object_c: BaseObject, *base_objects: BaseObject,oneup_only = False):
        if "Container" not in base_object_c.component.__dict__:
            raise Exception(f"object {base_object_c} does not have a Container comp")
        base_object_c.component.Container.storage.difference_update(base_objects)
        for base_object in base_objects:
            if oneup_only:
                base_object.contained_by = base_object.contained_by_all()[1]
            else:
                base_object.contained_by = None
            self.obj_in_container.remove(base_object.id, base_object_c)
            
        



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
    #ee1 = Entities("bob", (1, 1), BasicProps(), Orc())
    #ee2 = Entities("jim", (2, 1), BasicProps(strength=12), Orc())
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
