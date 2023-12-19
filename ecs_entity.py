import json
from types import SimpleNamespace


class Scene:
    def __init__(self):
        self.ids = dict()
        self.obj_positions = dict()
        self.obj_type = dict()
        self.obj_components = dict()

    def spawn_object(self, base_object):
        ...
#use sets instead of lists to hold all this crap

    def add_to_db(self, base_object):
        self.ids[base_object.id] = base_object
        if base_object.position in self.obj_positions:
            self.obj_positions[base_object.position].append(base_object.id)
        else:
            self.obj_positions[base_object.position] = [base_object.id]
        if type(base_object).__name__ in self.obj_type:
            self.obj_type[type(base_object.__name__)].append(base_object.id)
        else:
            self.obj_type[type(base_object.__name__)] = [base_object.id]
        for _c in base_object.component.__dict__:
            if _c in self.obj_components:
                self.obj_components[_c].append(base_object.id)
            else:
                self.obj_components[_c] = [base_object.id]

    def rem_fr_db(self, base_object):
        if base_object.id not in self.ids:
            print('object not in scene')
            return 0
        else:
            del self.ids[base_object.id]
            if base_object.position in self.obj_positions:
                if self.obj_positions[base_object.position] == [base_object.id]:
                    del self.obj_positions[base_object.position]
                elif base_object.id in self.obj_positions[base_object.position]:
                    self.obj_positions[base_object.position].remove(base_object.id)
            if type(base_object).__name__ in self.obj_type:
                if self.obj_type[type(base_object).__name__] == [base_object.id]:
                    del self.obj_positions[base_object.position]
                elif base_object.id in self.obj_type[type(base_object).__name__]:
                    self.obj_type[type(base_object).__name__].remove(base_object.id)
            for _c in base_object.component.__dict__:
                if _c in self.obj_components:
                    if self.obj_components[_c] == [base_object.id]:
                        del self.obj_components[_c]
                    elif base_object.id in self.obj_components[_c]:
                        self.obj_components[_c].remove(base_object.id)


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


class BasicProps:
    def __init__(self, **basic_properties):
        self.__dict__.update(basic_properties)
    def load_from_file(self, filename):
        with open(filename) as fin:
            self.__dict__.update(json.load(fin))
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