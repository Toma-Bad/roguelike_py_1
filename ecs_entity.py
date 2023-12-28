import json
from types import SimpleNamespace
import numpy as np
class BaseObject:
    def __init__(self, *components):
        self.id = id(self)
        self.component = SimpleNamespace(**{type(_c).__name__:_c for _c in components})
    def add_component(self, *components):
        self.component.__dict__.update({type(_c).__name__:_c for _c in components})
    def remove_component(self, component_name):
        try:
            self.component.__delattr__(component_name)
        except Exception as e:
            print(e)


class Scene:
    def __init__(self,scene_width, scene_height):
        self.ids = dict()
        self.obj_positions = dict()
        self.obj_type = dict()
        self.obj_components = dict()
        self.obj_loc_arr = np.empty((scene_width,scene_height),dtype=object)
    def spawn_object(self, base_object):
        ...
#use sets instead of lists to hold all this crap

    def add_to_db(self, base_object):
        self.ids[base_object.id] = base_object
        if base_object.position in self.obj_positions:
            self.obj_positions[base_object.position].add(base_object.id)
        else:
            self.obj_positions[base_object.position] = {base_object.id}
        if type(base_object).__name__ in self.obj_type:
            self.obj_type[type(base_object.__name__)].add(base_object.id)
        else:
            self.obj_type[type(base_object.__name__)] = {base_object.id}
        for _c in base_object.component.__dict__:
            if _c in self.obj_components:
                self.obj_components[_c].add(base_object.id)
            else:
                self.obj_components[_c] = {base_object.id}

    def rem_fr_db(self, base_object):
        if base_object.id not in self.ids:
            print('object not in scene')
            return 0
        else:
            del self.ids[base_object.id]
            if base_object.position in self.obj_positions:
                if self.obj_positions[base_object.position] == {base_object.id}:
                    del self.obj_positions[base_object.position]
                elif base_object.id in self.obj_positions[base_object.position]:
                    self.obj_positions[base_object.position].remove(base_object.id)
            if type(base_object).__name__ in self.obj_type:
                if self.obj_type[type(base_object).__name__] == {base_object.id}:
                    del self.obj_positions[base_object.position]
                elif base_object.id in self.obj_type[type(base_object).__name__]:
                    self.obj_type[type(base_object).__name__].remove(base_object.id)
            for _c in base_object.component.__dict__:
                if _c in self.obj_components:
                    if self.obj_components[_c] == {base_object.id}:
                        del self.obj_components[_c]
                    elif base_object.id in self.obj_components[_c]:
                        self.obj_components[_c].remove(base_object.id)

    def rm_comp_from_obj(self,base_object : BaseObject,component_name : str):
        if component_name in base_object.component.__dict__:
            base_object.remove_component(component_name)
            if component_name in self.obj_components:
                if self.obj_components[component_name] == {base_object.id}:
                    del self.obj_components[component_name]
                elif base_object.id in self.obj_components[component_name]:
                    self.obj_components[component_name].remove(base_object.id)
    def add_comp_to_obj(self,base_object : BaseObject,component_instance):
        base_object.add_component(component_instance)
        component_name = type(component_instance).__name__
        if component_name in self.obj_components:
            self.obj_components[component_name].add(base_object.id)
        else:
            self.obj_components[component_name] = {base_object.id}



class BaseComponent:
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
    @classmethod
    def load_from_file(cls, filename):
        with open(filename) as fin:
            data_dict = json.load(fin)
        return cls(**data_dict)

class BasicProps(BaseComponent):
    def __init__(self, **basic_properties):
        self.__dict__.update(basic_properties)

class Inventory(BaseComponent):
    #to do: add str representation for the items in dict
    def __init__(self,**items):
        self.storage = dict()
        self.storage.update(items)
        self.equipped = dict()
        self.weight = sum([_i.weight for _i in self.storage.values()])
    def set_equip_from_storage(self,item_name):
        if item_name in self.storage and item_name not in self.equipped:
            self.equipped[item_name] = self.storage[item_name]
    def set_unequip(self,item_name):
        if item_name in self.storage and item_name in self.equipped:
            del self.equipped[item_name]
    def add_items(self,**items):
        self.storage.update(items)
        self.weight += sum([_i.weight for _i in items.values()])
    def remove_items(self,equipped = False,**items):
        for _it_name in items:
            if _it_name in self.storage:
                del self.storage[_it_name]
            if equipped:
                if _it_name in self.equipped:
                    del self.equipped[_it_name]
        self.weight -= sum([_i.weight for _i in items.values()])



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
    ee1 = Entities("bob",(1,1),BasicProps(),Orc())
    ee2 = Entities("jim",(2,1),BasicProps(strength=12),Orc())