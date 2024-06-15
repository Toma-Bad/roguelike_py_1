from map_object import *
from scene_object import *
from game_objects import *

def generate_scene(w,h):
    scene = Scene(scene_width=w,scene_height=h)
    wall_tile = make_blt_tile(walkable=False, opaque = True, dark = False, explored=False, sprite=make_blt_sprite(char="#", fg_color=[255,255,255,255], bg_color=[0,0,0,0]))
    floor_tile = make_blt_tile(walkable=True, opaque=False, dark=False, explored=False, sprite=make_blt_sprite(char=".", fg_color=[155,100,100,100], bg_color=[0,0,0,0]))
    player_tile = make_blt_tile(walkable=True, opaque=False, dark=False, explored=True, sprite=make_blt_sprite(char="@", fg_color=[255,255,255,255], bg_color=[0,0,0,0]))
    monster_tile = make_blt_tile(walkable=True, opaque=True, dark=False, explored=True, sprite=make_blt_sprite(char="&", fg_color=[255,255,25,25], bg_color=[0,0,0,0]))
    #soil_tile = make_blt_tile(walkable=True, opaque=True, dark=False, explored=False, sprite=gf_Tile3B("█", [155,100,100,100], [140,40,40,40]))
    floor_map = np.zeros((scene.scene_width, scene.scene_height),dtype=tile_dt)
    floor_map[:] = floor_tile
    scene.terrain_map = TileMap(np_array=floor_map, layer=0)
    

    for i in range(scene.scene_width):
        scene.add_object(BaseBlock(position=(i, 0),components=[{'tile': TileComponent.from_tile(wall_tile)}]))
        scene.add_object(BaseBlock(position=(i, -1),components=[{'tile': TileComponent.from_tile(wall_tile)}]))
    for i in range(scene.scene_height)[:-2]:
        scene.add_object(BaseBlock(position=(0, i+1),components=[{'tile': TileComponent.from_tile(wall_tile)}]))
        scene.add_object(BaseBlock(position=(-1, i+1),components=[{'tile': TileComponent.from_tile(wall_tile)}]))

    scene.add_object(BaseBlock(position=(20, 20), components=[{'tile': TileComponent.from_tile(wall_tile)}]))
    scene.add_object(BaseBlock(position=(21, 20), components=[{'tile': TileComponent.from_tile(wall_tile)}]))
    scene.add_object(BaseEntity(position=(10,10),components=[
        {'tile': TileComponent.from_tile(player_tile)},
        {'controller': BaseComponent(name='controller',type='player',description='this is the player')}
    ]))
    scene.add_object(BaseEntity(position=(15, 15), components=[
        {'tile': TileComponent.from_tile(monster_tile)},
        {'controller': BaseComponent(name='controller', type='ai', description='this is an ai monster')}
    ]))
    scene.update_map()

    return scene