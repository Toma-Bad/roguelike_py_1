from dataclasses import dataclass

import heapdict
from bearlibterminal import terminal as blt
from ecs_entity import *
from scene import *
@dataclass
class BaseEvent:
    player_entity: BaseEntity

@dataclass
class MoveEvent(BaseEvent):
    destination: (int,int)

@dataclass
class AttackEvent(BaseEvent):
    destination: (int,int)
    type: str

@dataclass
class InteractEvent(BaseEvent):
    target: BaseObject|BaseEntity
    type: str


@dataclass
class BaseCommand:
    command_entity: BaseEntity


@dataclass
class MoveCommand(BaseCommand):
    destination: (int, int)
    def execute(self,scene: Scene):
        scene.move_obj(self.command_entity,self.destination)
        return True


@dataclass
class MeleeAttackCommand(BaseCommand):
    target: BaseObject | BaseEntity
    def execute(self, scene: Scene):
        if self.command_entity.to_hit(self.target,type="melee"):
            damage = self.command_entity.to_damage(self.target,type="melee")
        else:
            damage = 0
        scene.apply_damage(self.target, damage)
        return bool(damage)


@dataclass
class RangedAttackCommand(BaseCommand):
    target: BaseObject | BaseEntity
    def execute(self,scene: Scene):
        if self.command_entity.to_hit(self.target,type="ranged"):
            damage = self.command_entity.to_damage(self.target,type="ranged")
        else:
            damage = 0
        scene.apply_damage(self.target, damage)
        return bool(damage)

@dataclass
class InteractCommand(BaseCommand):
    target: BaseObject | BaseEntity
    type: str
    def execute(self,scene: Scene):
        if self.type == "grab":
            scene.add_to_container(self.command_entity,self.target)



class Game:
    def __init__(self,current_scene:Scene):
        self.current_scene = current_scene
        self.entity_que = heapdict.heapdict()
        self.state = "game"
        self.turn_marker = ("turn_marker",100)


    def generate_queue(self,entities: {BaseEntity}):
        self.entity_que.update({entity:entity.energy for entity in entities})
        self.entity_que.put(self.turn_marker[0],self.turn_marker[1])

    def pop_q(self):
        if self.entity_que.items():
            return self.entity_que.popitem()
        else:
            return None

    def peek_q(self):
        if self.entity_que.items():
            return self.entity_que.peekitem()
        else:
            return None

    def put_q(self,entity:BaseEntity):
        self.entity_que[entity] = entity.energy

    def get_controller(self,entity:BaseEntity):
        if type(IsAI).__name__ in entity.component.__dict__:
            return entity.component.IsAi.ai_style
        if type(IsPlayer).__name__ in entity.component.__dict__:
            return "player"
        else:
            return None

    def get_objs_at(self,position: (int,int)):
        if position in self.current_scene.obj_positions[position]:
            objs_at_pos = self.current_scene.obj_positions[position]
        else:
            objs_at_pos = set()
        return objs_at_pos
    def is_blocking_at(self,position: (int,int)):
        if objs_at_pos := self.get_obj_at(position):
            if objs_at_pos.intersection(self.current_scene.obj_type[BaseBlock]):
                return True
        return False

    def filter_get_obj_at(self,position: (int,int), filter:str="entity"):
        res = set()
        if objs_at_pos := self.get_obj_at(position):
            match(filter):
                case "entity":
                    res = objs_at_pos.intersection(self.current_scene.obj_type[BaseEntity])
                case "block":
                    res = objs_at_pos.intersection(self.current_scene.obj_type[BaseBlock])
                case "item":
                    res = objs_at_pos.intersection(self.current_scene.obj_type[BaseItem])
        return res

    def get_carry_capacity(self,entity:BaseEntity):
        return 10*entity.component.BasicEntityStats.value['strength']
    def can_pick_obj(self,entity:BaseEntity,item:BaseItem):
        if entity.component.Container.weight + item.component.BasicStats.value["weight"] > self.get_carry_capacity(entity):
            return False
        else:
            return True

    def event_to_command(self, event: BaseEvent|AttackEvent|MoveEvent|InteractEvent):
        match(event):
            case MoveEvent():
                if self.is_blocking_at(event.destination):
                    return None
                elif entities_at_dest:= self.filter_get_obj_at(event.destination, filter="entity"):
                    return MeleeAttackCommand(event.player_entity,entities_at_dest.pop())
                else:
                    return MoveCommand(event.player_entity,event.destination)
            case AttackEvent():
                if entities_at_dest := self.filter_get_obj_at(event.destination, filter="entity"):
                    if event.type == "melee":
                        return MeleeAttackCommand(event.player_entity,entities_at_dest.pop())
                    elif event.type == "ranged":
                        return RangedAttackCommand(event.player_entity,entities_at_dest.pop())
            case InteractEvent():
                if event.type == "grab":
                    if self.can_pick_obj(event.player_entity,event.target):
                        return InteractCommand(event.player_entity,event.target,type=event.type)
        return None

    def calculate_melee_damage(self,entity:BaseEntity):


    def command_execute(self,command:BaseCommand|MoveCommand|MeleeAttackCommand|RangedAttackCommand|InterCommand):
        match(command):
            case MoveCommand():
                return command.execute(self.current_scene)
            case MeleeAttackCommand():
                return command.execute(self.current_scene)
            case RangedAttackCommand():
                return command.execute(self.current_scene)
        return False












#inerface handles keypresses, opens closes menus, selects targets, looks at inventory
#when a valid collection of keypresses (events?) occurs, a command is generated.
#AI looks at the game and also issues a command.
# the game then executes the command


ck_dict = {blt.TK_UP: ["move",(0,1)],
           blt.TK_DOWN: ["move",(0,-1)],
           blt.TK_LEFT:  ["move",(-1,0)],
           blt.TK_RIGHT: ["move",(0,-1)],
           blt.TK_SPACE: ["attack","melee"],
           blt.TK_X: ["attack","ranged"],
           blt.TK_SHIFT: ["shift",1],
           blt.TK_CONTROL: ["ctrl",1],
           #blt.TK_CLOSE:"QUIT",
           blt.TK_Q: ["QUIT"]}



def get_event(ck_dict,nonblocking = True):
    if nonblocking and not blt.has_input():
        return None

    else:
        key = blt.read()
        if key in ck_dict:
            #print("what?")
            event = ck_dict[key]
            return event

def get_direction(ck_dict = ck_dict, nonblocking = False):
    direction = get_event(ck_dict,nonblocking=nonblocking)[1]
    if isinstance(direction, tuple):
        return direction
    return None

def event_handler(scene, event, event_target:BaseEntity = None):
    match event:
        case['wait',1]:
            return wait_event(event_target)
        case["move",direction]:
            return move_event(scene, event_target, direction)
        case["attack",a_type]:
            if a_type == "melee":
                if direction:= get_direction():
                    return melee_attack_event(scene, event_target, direction)
            if a_type == "ranged":
                ...
                # gui stuff where you select destination
                #destination = inq_destination(ck_dict)
                #return ranged_attack_event(event_target, destination)
        case["interact",i_type]: #openclose doors/switches/simple stuff
            if direction:= get_direction():
                return None#inter_event(scene, event_target, direction, i_type)
    return None


def check_able(target_obj: BaseObject|BaseEntity|BaseItem,tocheck: str):
    match(tocheck):
        case "move":
            return True
        case "attack":
            return True
        case "interact":
            return True
    return False

#these functions evaluate the event from the player and decide what
#commands to create


#def inter_event(scene, event_target, direction, i_type):
#    destination = (event_target.position[0] + direction[0],
#                   event_target.position[1] + direction[1])
#    obj_at_destination = scene.obj_positions[destination]
#    if check_able(event_target,"interact") is False:
#        command = None
#    else:
#        match(i_type):
#            case "grab":
#                items := obj_at_destination.intersection(scene.obj_type[BaseEntity]):
#        entity_at_destination = entities.pop()
#        command = InterCommand(event_target, entity_at_destination, i_type)
#    else:
#        command = None
#    return command


def move_event(scene: Scene, event_target: BaseObject|BaseEntity, direction: (int,int)):
    destination = (event_target.position[0]+direction[0],
                   event_target.position[1]+direction[1])
    obj_at_destination = scene.obj_positions[destination]
    if check_able(event_target,"move") is False:
        return None
    elif obj_at_destination.intersection(scene.obj_type[BaseBlock]):
        command = None
    elif entities := obj_at_destination.intersection(scene.obj_type[BaseEntity]):
        entity_at_destination = entities.pop()
        if entity_at_destination.aggro:
            command = [MeleeAttackCommand(event_target, entity_at_destination)]
        else:
            command = [MoveCommand(event_target, destination),
                       MoveCommand(obj_at_destination,event_target.position)]
    else:
        command = [MoveCommand(event_target, destination)]
    return command



def melee_attack_event(scene, event_target, direction):
    destination = (event_target.position[0] + direction[0],
                   event_target.position[1] + direction[1])
    obj_at_destination = scene.obj_positions[destination]
    if check_able(event_target,"attack") is False:
        command = None
    elif entities := obj_at_destination.intersection(scene.obj_type[BaseEntity]):
        entity_at_destination = entities.pop()
        command = MeleeAttackCommand(event_target, entity_at_destination)
    else:
        command = None
    return command
def command_handle(scene:Scene, command:MoveCommand|AttackCommand|InterCommand):
    if isinstance(command,AttackCommand):
        if a_type == "2":
            #do bring up the gui
            return None
        else:
            direction = inq_direction(ck_dict)
            return handle_attack_command(scene,command,direction)
    if isinstance(command,MoveCommand):
            return handle_move_command(scene,command)
    if isinstance(command,InterCommand):


            #do some gui stuff
            return handle_inter_command(scene,command,)

def attack_command(scene, command_target, a_type):
    selfpos = command_target.position
    result = None
    if a_type == "1" and check_able(command_target,"attack"):
        com = get_command(ck_dict, nonblocking=False)
        if isinstance(com,list):
            if len(com) > 1:
                direction = txt2dir(com)
                if direction:
                    destination = (selfpos[0] + direction[0], selfpos[1] + direction[1])
                    obj_at_destination = scene.obj_positions[destination]
                    if action_target := obj_at_destination.intersection(scene.obj_type[BaseEntity]):
                        action_target = action_target.pop()
                        result = AttackAction(command_target,action_target)
    if a_type == "2":
        pass
    return result

def inter_command(scene:Scene,command_target):
    selfpos = command_target.position
    result = None
    com = get_command(ck_dict, nonblocking=False)
    if isinstance(com, list):
        if len(com) > 1:
            direction = txt2dir(com)
            if direction:
                destination = (selfpos[0] + direction[0], selfpos[1] + direction[1])

                if action_target := obj_at_destination.intersection(scene.obj_type[BaseEntity]):
                    action_target = action_target.pop()
                    result = AttackAction(command_target, action_target)







@dataclass
class MoveAction:
    self: BaseObject|BaseEntity
    destination: (int,int)

@dataclass
class AttackAction:
    self: BaseObject|BaseEntity
    other: BaseObject|BaseEntity|BaseBlock

@dataclass
class InterAction:
    self: BaseObject|BaseEntity
    other: BaseObject|BaseEntity|BaseBlock|BaseItem

