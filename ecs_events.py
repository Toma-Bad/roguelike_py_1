from dataclasses import dataclass
from bearlibterminal import terminal as blt
from ecs_entity import *
from scene import *




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
            if 100 <= target_obj.component.base_stats["energy"]:
                return True
        case "attack":
            if 100 <= target_obj.component.base_stats["energy"]:
                return True
        case "interact":
            if 100 <= target_obj.component.base_stats["energy"]:
                return True
    return False

#these functions evaluate the event from the player and decide what
#commands to create
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
            command = MeleeAttackCommand(event_target, entity_at_destination)
        else:
            command = MoveCommand(event_target, destination, flip=entity_at_destination)
    else:
        command = MoveCommand(event_target, destination)
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

@dataclass
class MoveCommand:
    command_target: BaseObject|BaseEntity
    destination: (int,int)
    flip: BaseEntity = None
    def execute(self,scene:Scene):
        scene.move_obj(self.command_target,self.destination)

@dataclass
class MeleeAttackCommand:
    command_target: BaseObject|BaseEntity
    attack_target: BaseObject|BaseEntity
    def execute(self):



@dataclass
class InterCommand:
    command_target: BaseObject|BaseEntity
    direction: (int,int)
    i_type: str


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

