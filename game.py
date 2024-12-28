from map_renderer import MapRenderer
import event_handler
import json
import jsonschema
from event_handler import EventHandler
from scene_object import Scene
from map_object import *
from dataclasses import dataclass
from game_objects import BaseEntity

move_dict = {
    "up":(0,-1),
    "down":(0,1),
    "left":(-1,0),
    "right":(1,0)
}
from scene_loader import generate_scene

class Command(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CommandFactory:
    def __init__(self, schema_file: str = None):
        with open(schema_file,'r') as fin:
            schema_data = json.load(fin)

    def create_command(self, event):
        match (event):
            case "up" | "down" | "left" | "right":
                return
            case _:
                return None






@dataclass
class Command:
    entity: BaseEntity

#@dataclass
#class MoveCommand(Command):
#    direction: (int,int)

class AttackCommand(Command):
    def __init__(self, entity, other):
        super().__init__(entity)
        self.other = other



@dataclass
class Action:
    entity: BaseEntity

@dataclass
class MoveAction(Action):
    destination: (int,int)


class Game:
    def __init__(self,current_scene: Scene, event_handler: EventHandler):
        self.current_scene = current_scene
        self.event_handler = event_handler
        self.state = "game"
        self.map_renderer = MapRenderer(self.current_scene)
    def issue_command(self, entity, event):
        match (event):
            case "up" | "down" | "left" | "right":
                return MoveCommand(entity, move_dict[event])
            case _:
                return None
    def action_from_command(self, command):
        if isinstance(command, MoveCommand):
            destination = (command.entity.position[0] + command.direction[0],
                     command.entity.position[1] + command.direction[1])
            if self.current_scene.is_blocking_at(destination):
                return None
            else:
                return MoveAction(command.entity, destination)
        return None
    def action_from_ai(self, entity, some_ai_stuff = "move_random"):
        if some_ai_stuff == "move_random":
            direction = np.random.default_rng().choice(np.array([(0, 1), (0, -1), (1, 0), (-1, 0)]),4,replace=True)
            print(f"{direction=}")
            i_dir = iter(direction)
            while  (n_dir := next(i_dir)).size:
                destination = (entity.position[0] + n_dir[0],
                               entity.position[1] + n_dir[1])
                if not self.current_scene.is_blocking_at(destination):
                    print(f"{MoveAction(entity, destination)=}")
                    return MoveAction(entity, destination)
            return None
        return None




    def apply_action(self, action):
        if isinstance(action, MoveAction):
            self.current_scene.move_object(action.entity, action.destination)
            action.entity.components['move_points']['value'] += 100



    def main_loop(self):
        while True:
            event = self.event_handler.get_event()
            if event == "QUIT":
                raise SystemExit("Quit")
            match(self.state):
                case "game":
                    current_entity, to_move, has_moved = self.current_scene.get_turn()
                    print(to_move, has_moved)
                    if current_entity is None:
                        self.current_scene.pass_turn()
                        current_entity, to_move, has_moved = self.current_scene.get_turn()
                    if current_entity.components['controller']['type'] == "player":
                        current_command = self.issue_command(current_entity,event)
                        current_action = self.action_from_command(current_command)
                    elif current_entity.components['controller']['type'] == "ai":
                        current_action = self.action_from_ai(current_entity)
                        print(current_action)
                    if current_action:
                        self.apply_action(current_action)
                        self.current_scene.update_map()

                    blt.clear()
                    if current_entity.components['controller']['type'] == "player":
                        self.map_renderer.compute_fov(current_entity.position)

                    self.map_renderer.render()
                    blt.refresh()










if __name__ == "__main__":
    blt.open()
    blt.set("window: cellsize=10x10, title='Omni: menu', fullscreen=true, size=128x72; font: default")
    blt.set("window.title='Rouge Rogue Rage'")
    blt.color("white")
    blt.clear()
    game = Game(current_scene = generate_scene(128,71),event_handler=EventHandler(ck_dict=event_handler.ck_dict))
    game.main_loop()



#    floormap = np.zeros((128, 71), dtype=tile_dt)
#
#    wallmap = np.zeros((128, 71), dtype=tile_dt)
#
#    floormap[:] = soil_tile
#
#    scene = Scene(128,71)
#    for i in range(scene.scene_width):
#        scene.add_object(
#            BaseBlock(
#                (i,0),
#                components=[
#                    {'tile':TileComponent.from_tile(wall_tile)}
#                ]
#            )
#        )
#        scene.add_object(
#            BaseBlock(
#                (i,-1),
#                components=[
#                    {'tile': TileComponent.from_tile(wall_tile)}
#                ]
#            )
#        )
#    for i in range(scene.scene_height):
#        scene.add_object(
#            BaseBlock(
#                (0,i),
#                components=[
#                    {'tile':TileComponent.from_tile(wall_tile)}
#                ]
#            )
#        )
#        scene.add_object(
#            BaseBlock(
#                (-1,i),
#                components=[
#                    {'tile': TileComponent.from_tile(wall_tile)}
#                ]
#            )
#        )
#