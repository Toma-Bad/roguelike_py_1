import tcod.constants
from bearlibterminal import terminal as blt
import numpy as np
from tcod import map as tcodmap


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
def QuitGame(event):
    if event == "QUIT":
        raise SystemExit("Quit")


class PlayerMoveEvent:
    def __init__(self, command=None, *args, **kwargs):
        self.command = command
        self.dx = 0
        self.dy = 0
        if self.command == "MUP":
            self.dy = -1
        if self.command == "MDO":
            self.dy = +1
        if self.command == "MLE":
            self.dx = -1
        if self.command == "MRI":
            self.dx = +1
        self.dir = (self.dx,self.dy)

class PlayerAttackEvent:
    def __init__(self, command=None):
        self.command = command
        self.attack_1 = 0
        self.attack_2 = 0
        if self.command == "AT1":
            self.attack_1 = 1
        if self.command == "AT2":
            self.attack_2 = 1


class EventHandler:
    def __init__(self,ck_dict):
        self.ck_dict = ck_dict
    def get_event(self):
        if blt.has_input():
            key = blt.read()
            #print(key)
            if key in self.ck_dict:
                #print("what?")
                event = self.ck_dict[key]
                return event
    def register_event(self,ck_dict,key,event_type):
        ck_dict[key] = event_type

class EntityAction: #need to make an action  factory too...
    def __init__(self,entity):
        self.entity = entity
        self.actiontype = None


    @classmethod
    def create_move_action(cls,entity,dir):
        cl = cls(entity)
        cl.actiontype = "move"
        cl.dir = dir
        return cl
    def apply_action(self):
        if self.actiontype == "move":
            self.entity.position[0] += self.dir[0]
            self.entity.position[1] += self.dir[1]
            return True


class MoveCommand:
    def __init__(self,event):
        self.event = event
    def to_action(self,entity,scenemap):
        dest_floortile,dest_walltile,dest_entity = scenemap.check_position(entity,self.event.dir)
        if dest_walltile["walkable"]:
            return EntityAction.create_move_action(entity,self.event.dir)
        else:
            print("ow!")
            return None

        
        #if destination is hostile creature return attack action on target
        #if it's NPC, return talk or move action to target
        #if it's wall, return None
        #if it's walkable place return move action to target
        #if it's interactible barrier open action to target



        #if _map[self.position[0] + event.dx, self.position[1] + event.dy]['walkable']:
        #    self.position = self.position + np.array([event.dx, event.dy])
        #    return True
        #else:
        #    print("ow!")
        #    return False


class EntityCommander:
    def __call__(self,entity,map,commandfactory,event):
        command = commandfactory.get_command_from(event)
        action = command.to_action(entity,map)
        return action



class CommandFactory:
    def get_command_from(self,event):
        if isinstance(event,PlayerMoveEvent):
            return MoveCommand(event)
        if isinstance(event,PlayerAttackEvent):
            return False
            #return AttackCommand(event)
        if isinstance(event,str):
            if event == "QUIT":
                QuitGame(event)







class Entity:
    def __init__(self, position, gf_tile=None, name="", isplayer=True):
        self.position = np.array(position)
        self.gf_tile = np.array([[gf_tile, ], ], dtype=gf_tile_dt)
        self.name = name
        self.isplayer = isplayer
    def __call__(self, *args, **kwargs):
        if self.isplayer is True:
            event = args[0]
            _map = args[1]
            if isinstance(event,PlayerMoveEvent):
                return self._move(event,_map)
            if isinstance(event, PlayerAttackEvent):
                print("attack!")
                return True
            return False
        if self.isplayer is False:
            return self._ai_do(*args)
    def _move(self,event,_map):
        if _map[self.position[0] + event.dx, self.position[1] + event.dy]['walkable']:
            self.position = self.position + np.array([event.dx, event.dy])
            return True
        else:
            print("ow!")
            return False

    def _ai_do(self,_fov_map):
        return True


ck_dict = {blt.TK_UP: PlayerMoveEvent("MUP"),
           blt.TK_DOWN: PlayerMoveEvent("MDO"),
           blt.TK_LEFT:  PlayerMoveEvent("MLE"),
           blt.TK_RIGHT: PlayerMoveEvent("MRI"),
           blt.TK_SPACE: PlayerAttackEvent("ATT1"),
           blt.TK_X: PlayerAttackEvent("ATT2"),
           #blt.TK_CLOSE:"QUIT",
           blt.TK_Q: "QUIT"}


class GameEngine:
    def __init__(self, SceneMap, ev_handler):
        self.event_handler = ev_handler
        self.SceneMap = SceneMap
        self.Renderer = Render(self.SceneMap,self.SceneMap.object_list,self.SceneMap.entity_list)
        self.commandfactory = CommandFactory()
        #self._playerobject = entity_list[0]


    def render_scene(self,map,entity_list):
        blt.put_np_array(0,0,map['gf_tile'],'ch','fg','bg')
        for entity in entity_list:
            blt.put_np_array(entity.position[0],entity.position[1],entity.gf_tile,'ch','fg','bg')
    def main_loop(self):

        print(blt.TK_WIDTH, blt.TK_HEIGHT, blt.TK_CELL_WIDTH, blt.TK_CELL_HEIGHT)

        advance_turn = True
        turn_number = 0
        while True:
            #print("A")
            event = self.event_handler.get_event()
            #print(event)
            QuitGame(event)
            if self.SceneMap._playerobject(event,self.SceneMap.WallMap.np_map):
                advance_turn = True
            else:
                advance_turn = False

            if advance_turn is True:
                turn_number += 1
                #print(Render.)
                print(turn_number)
            #else:
            #   print(turn_number)

            #self.render_scene(self.local_map,self.entity_list)
            blt.clear()
            self.Renderer.compute_fov(self.SceneMap._playerobject.position)
            self.Renderer.render_scene()
            blt.refresh()

class SceneMap:
    def __init__(self,FloorMap = None, WallMap=None,entity_list = None,object_list = None):
        self.FloorMap = FloorMap
        self.WallMap = WallMap
        self.entity_list = entity_list
        self.object_list = object_list

    @property
    def entity_list(self):
        return self._entity_list

    @entity_list.setter
    def entity_list(self, e_list):
        self._entity_list = e_list
        for _entity in e_list:
            if _entity.isplayer is True:
                self._playerobject = _entity
    def check_position(self,position : tuple([int,int])):
        x,y = position
        entity_at_pos = [_e for _e in self.entity_list if _e.x == x and _e.y == y]
        return self.FloorMap.get_xy(x,y),self.WallMap.get_xy(x,y),entity_at_pos

class Map:
    def __init__(self,np_map = None, layer = 0):
        self.np_map = np_map
        self.layer = layer
    def get_xy(self,*args):
        if isinstance(args,tuple):
            x = args[0][1]
            y = args[0][1]
        else:
            x = args[0]
            y = args[1]
        return self.np_map[x,y]



class Render:
    def __init__(self,SceneMap,obj_list,entity_list):
        self.SceneMap = SceneMap
        self.obj_list = obj_list
        self.entity_list = entity_list
    def compute_fov(self,position,radius = 9):
        self.fov_map = tcodmap.compute_fov(self.SceneMap.WallMap.np_map["transparent"], pov=tuple(position), radius=radius,algorithm=tcod.constants.FOV_DIAMOND)
    @property
    def fov_map(self):
        return self._fov_map

    @fov_map.setter
    def fov_map(self,fovmap):
        self._fov_map = fovmap
        self.SceneMap.FloorMap.np_map['dark'] = np.logical_not(fovmap)
        self.SceneMap.WallMap.np_map['dark'] = np.logical_not(fovmap)
        self.SceneMap.FloorMap.np_map['explored'] = np.logical_or(fovmap,self.SceneMap.FloorMap.np_map['explored'])
        self.SceneMap.WallMap.np_map['explored'] = np.logical_or(fovmap,self.SceneMap.WallMap.np_map['explored'])
        self.obj_to_render = [obj for obj in self.obj_list if fovmap[obj.position[0],obj.position[1]] == True]
        self.ent_to_render = [ent for ent in self.entity_list if fovmap[ent.position[0],ent.position[1]] == True]
    #def fov_obj(self):
    #   self.obj_to_render = [obj for obj in self.obj_list if self.fov_map[*obj.position] == True]
    #def fov_ent(self):
    #    self.ent_to_render = [ent for ent in self.entity_list if self.fov_map[*ent.position] == True]
    def render_scene(self):
        floormap_to_render = np.copy(self.SceneMap.FloorMap.np_map)
        wallmap_to_render = np.copy(self.SceneMap.WallMap.np_map)
        floormap_to_render['gf_tile']['fg'][np.where(floormap_to_render['dark'] == True)] = self.SceneMap.FloorMap.np_map['gf_tile']['fg'][np.where(floormap_to_render['dark'] == True)] //2
        floormap_to_render['gf_tile']['bg'][np.where(floormap_to_render['dark'] == True)] = self.SceneMap.FloorMap.np_map['gf_tile']['bg'][np.where(floormap_to_render['dark'] == True)] // 2
        wallmap_to_render['gf_tile']['fg'][np.where(wallmap_to_render['dark'] == True)] = self.SceneMap.WallMap.np_map['gf_tile']['fg'][np.where(floormap_to_render['dark'] == True)] // 2
        wallmap_to_render['gf_tile']['bg'][np.where(wallmap_to_render['dark'] == True)] = self.SceneMap.WallMap.np_map['gf_tile']['bg'][np.where(floormap_to_render['dark'] == True)] // 2
        floormap_to_render['gf_tile']['fg'][np.where(floormap_to_render['explored'] == False)] = blt.color_from_argb(255, 0, 0, 0)
        floormap_to_render['gf_tile']['bg'][np.where(floormap_to_render['explored'] == False)] = blt.color_from_argb(255, 0, 0, 0)
        wallmap_to_render['gf_tile']['fg'][np.where(wallmap_to_render['explored'] == False)] = blt.color_from_argb(255, 0, 0, 0)
        wallmap_to_render['gf_tile']['bg'][np.where(wallmap_to_render['explored'] == False)] = blt.color_from_argb(255, 0, 0, 0)
        blt.layer(self.SceneMap.FloorMap.layer)
        blt.put_np_array(0,0,wallmap_to_render['gf_tile'],'ch','fg','bg')
        blt.layer(self.SceneMap.WallMap.layer)
        blt.put_np_array(0, 0, floormap_to_render['gf_tile'], 'ch', 'fg', 'bg')
        blt.layer(3)
        for object in self.obj_to_render:
            blt.put_np_array(object.position[0], object.position[1], object.gf_tile, 'ch', 'fg', 'bg')
        for entity in self.ent_to_render:
            blt.put_np_array(entity.position[0],entity.position[1],entity.gf_tile,'ch','fg','bg')











if __name__ == "__main__":
    blt.open()
    wall_tile = Tile3B(False, False, False, explored=False, gf_tile=gf_Tile3B("#", [255,255,255,255], [0,0,0,0]))
    floor_tile = Tile3B(True, True, False, explored=False, gf_tile=gf_Tile3B(".", [155,100,100,100], [0,0,0,0]))
    soil_tile = Tile3B(True, True, False, explored=False, gf_tile=gf_Tile3B("█", [155,100,100,100], [140,40,40,40]))
    map = np.zeros((128, 71), dtype=tile_dt_3B)
    soilmap = np.zeros((128, 71), dtype=tile_dt_3B)
    soilmap[:] = soil_tile
    map[:] = floor_tile
    map[0, :] = wall_tile
    map[-1, :] = wall_tile
    map[:, 0] = wall_tile
    map[:, -1] = wall_tile
    map[20:22, 20] = wall_tile


    blt.set("window: cellsize=10x10, title='Omni: menu', fullscreen=true, size=128x72; font: default")


    blt.set("window.title='Rouge Rogue Rage'")
    blt.color("white")
    blt.clear()
    print(blt.color_from_name("red"),blt.color_from_name("white"))
    entity_list = [Entity((5,5),name="Player",gf_tile=gf_Tile("@","white",bgcolor="black"),isplayer=True),
                   Entity((7,9),name="Monster 1",gf_tile=gf_Tile("H","blue",bgcolor="black"),isplayer=False),
                   Entity((15,12),name="Monster 2",gf_tile=gf_Tile("J","green",bgcolor="black"),isplayer=False)]
    object_list = [Entity((17, 9), name="Monster 1", gf_tile=gf_Tile("^", "blue", bgcolor="black"), isplayer=False),
                   Entity((10, 12), name="Monster 2", gf_tile=gf_Tile("$", "green", bgcolor="black"), isplayer=False)]
    scn_map = SceneMap(FloorMap=Map(np_map=soilmap, layer=0), WallMap=Map(np_map=map, layer=1),entity_list=entity_list,object_list=object_list)
    event_handler = EventHandler(ck_dict = ck_dict)
    game_engine = GameEngine(scn_map,event_handler)
    game_engine.main_loop()
