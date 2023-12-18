class BasicProps:
    def __init__(self,hp=100,strength=10,dexterity=10):
        self.hp = hp
        self.strength = strength
        self.dexterity = dexterity

class Modifiers:
    def __init__(self,**modifiers):
        self.__dict__.update(modifiers)
class BasicRace:
    def __init__(self,racetype,**modifiers):
        self.racetype = racetype
        self.modifiers = Modifiers(**modifiers)

class Orc(BasicRace):
    def __init__(self):
        super().__init__("orcish",hp=2,strength=5)


class Entities:
    ids = dict()
    components = dict()
    positions = dict()
    def __init__(self,name,pos,*component_args):
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