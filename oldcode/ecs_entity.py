import json
from types import SimpleNamespace
import numpy as np
import copy
from bearlibterminal import terminal as blt
def tile(*args):
    return np.array(*args, dtype=tile_dt)


def sprite(*args):
    return np.array(*args, dtype=gf_tile_dt)

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

    def get_base_to_hit(self,mode: str):
        dexmod = (self.component.EntityProps.value["dexterity"] - 12) // 2
        if mode == "ranged":
            wepmod = (self.component.Equipped.value["ranged"].tohit_mod)
        elif mode == "melee":
            wepmod = (self.component.Equipped.value["melee"].tohit_mod)
        return dexmod + wepmod
    def get_base_to_dodge(self):
        dexmod = (self.component.EntityProps.value["dexterity"] - 12) // 2
        if mode == "ranged":
            armmod = (self.component.Equipped.value["armor"].tododge_mod)
        elif mode == "melee":
            armmod = (self.component.Equipped.value["armor"].tododge_mod)
        return dexmod + wepmod
    def to_hit(self, other: 'BaseObject|BaseEntity',mode: str):
        self_base_to_hit = self.get_base_to_hit(mode)
        other_base_to_dodge = other.get_base_to_dodge(mode)
        if self_base_to_hit >= other_base_to_dodge:
            return True
        else:
            return False



    def _iter_contained_by(self):
        if self.contained_by is not None:
            yield self.contained_by
            yield from self.contained_by._iter_contained_by()

    def contained_by_all(self):
        return [_ for _ in self._iter_contained_by()]+[None]

    def add_component(self, *components):
        self.component.__dict__.update({_c.name if hasattr(_c,'name') else type(_c).__name__: _c for _c in components})

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
        self.value = basic_properties

class IsPlayer(BaseComponent):
    def __init__(self):
        super.__init__()

class IsAI(BaseComponent):
    def __init__(self,ai_style:str = "default"):
        super.init()
        self.ai_style = ai_style
class BasicStats(BasicProps):
    def __init__(self, hp=10, weight=100):
        super().__init__(hp=hp, weight=weight)

class BasicEntityStats(BasicProps):
    def __init__(self, hp=10, weight=100, energy=100):
        super().__init__(hp=hp,
                         weight=weight,
                         energy=energy)
class BasicItemStats(BasicProps):
    def __init__(self,hp=10, weight=10, value=10, status="ok"):
        super().__init__(hp=hp,
                         weight=weight,
                         value=value,
                         status=status)
class EntityProps(BasicProps):
    def __init__(self, strength=10, dexterity=10, intelligence=10, charisma=10, constitution=10):
        super().__init__(strength=strength,
                         dexterity=dexterity,
                         intelligence=intelligence,
                         charisma=charisma,
                         constitution=constitution)
class WeaponProps(BasicProps):
    def __init__(self,damage = (1,5), damage_type = "", ranged_damage = None):
        super().__init__(damage=damage,
                         damage_type=damage_type,
                         ranged_damage=ranged_damage)

class BlockProps(BasicProps):
    def __init__(self,material = ""):
        super().__init__(material=material)

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

class BaseModifier(BaseComponent):
    def __init__(self,name: str, target_component: BasicProps, target_properties: dict):
        super().__init__(name=name, target_component=target_component)
        self.target_properties = target_properties

class MultiModifier(BaseComponent):
    def __init__(self, name: str, *modifiers: BaseModifier):
        super().__init__(name=name, modifiers=modifiers)

class BodyPart(BaseComponent):
    def __init__(self, name: str,
                 attached_from: BaseComponent = None,
                 attached_to: BaseComponent = None,
                 can_equip: set = None,
                 equipped_item : BaseItem = None):
        self.name = name
        self.attached_from = attached_from
        self.attached_to = attached_to
        self.can_equip = can_equip
        self.equipped_item = equipped_item






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
    ...
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

    #sc = Scene(100, 100)
