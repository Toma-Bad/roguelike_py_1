class BasicProps:
    def __init__(self,hp,str,dex):
        self.hp = hp
        self.str = str
        self.dex = dex

class BasicRace:
    def __init__(self,racetype,modifiers):
        self.racetype = racetype
        self.modifiers = modifiers

class Entities:
    ids = dict()
    components = dict()
    positions = dict()
    def __init__(self,pos,*comps):
        self.pos = pos
        self.comp_list

