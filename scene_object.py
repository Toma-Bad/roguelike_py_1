from utils import *
from game_objects import BaseObject, BaseComponent, BaseBlock, BaseEntity, BaseItem
from map_object import *

class Scene:
    def __init__(self, scene_width, scene_height):
        self.ids = dict()
        self.obj_positions = SetDict()
        self.obj_type = SetDict()
        self.obj_components = SetDict()
        self.comp_timers = SetDict()
        # self.obj_loc_arr = np.empty((scene_width, scene_height), dtype=object)
        self.obj_in_container = SetDict()
        self.terrain_map = TileMap(scene_width, scene_height, layer=0)
        self.block_map = TileMap(scene_width, scene_height, layer=1)
        self.item_map = TileMap(scene_width, scene_height, layer=2)
        self.entity_map = TileMap(scene_width, scene_height, layer=3)
        self.map_renderer = MapRenderer(self.terrain_map,
                                        self.block_map,
                                        self.item_map,
                                        self.entity_map)
    def update_block_map(self):
        self.block_map.set_set(self.obj_type['BaseBlock'])
    def update_item_map(self):
        self.item_map.set_set(self.obj_type['BaseItem'])
    def update_entity_map(self):
        self.entity_map.set_set(self.obj_type['BaseEntity'])
    def update_map(self):
        self.update_entity_map()
        self.update_item_map()
        self.update_block_map()
    def move_object(self, base_object: BaseObject, new_position):
        old_position = base_object.position
        self.obj_positions.move(old_position, new_position, base_object)
        base_object.position = new_position
        if "inventory" in base_object.components:
            for _obj in base_object.component['inventory']['contents']:
                self.move_object(_obj, new_position)

    def add_object(self, base_object: BaseObject, at_position=None):
        if at_position:
            base_object.position = at_position
        self.ids[base_object.id] = base_object
        self.obj_positions.add(base_object.position, base_object)
        self.obj_type.add(type(base_object).__name__, base_object)
        if base_object.contained_by:
            self.obj_in_container.add(base_object.id, base_object.contained_by)

        for _c in base_object.components:
            self.obj_components.add(_c, base_object)
    def remove_object(self, base_object: BaseObject):
        if base_object.id not in self.ids:
            print('object not in scene')
            return 0
        else:
            del self.ids[base_object.id]
        self.obj_positions.remove(base_object.position, base_object)
        self.obj_type.remove(type(base_object).__name__, base_object)
        if base_object.contained_by:
            self.obj_in_container.remove(base_object.id, base_object.contained_by)
        if "inventory" in base_object.components:
            for _obj in base_object.component["inventory"]["storage"]:
                _obj.contained_by = _obj.contained_by_all()[1]
        for _c in base_object.components:
            self.obj_components.remove(_c, base_object)
            del base_object.components[_c]['parent']
        del base_object
    def add_component(self, base_object: BaseObject, base_component: BaseComponent, component_id=None):
        if component_id is None:
            component_id = base_component['name']
        base_component['parent'] = base_object
        base_object.components[component_id] = base_component
        self.obj_components.add(component_id ,base_object)
    def remove_component(self, base_object: BaseObject, component_id: str):
        del base_object.components[component_id]
        self.obj_components.remove(component_id, base_object)
    def add_to_container(self, base_object_c: BaseObject, *base_objects: BaseObject):
        if "inventory" not in base_object_c.components:
            raise Exception(f"object {base_object_c} does not have an inventory comp")
        base_object_c.components['inventory']['contents'].update(base_objects)
        for base_object in base_objects:
            base_object.contained_by = base_object_c
            self.obj_in_container.add(base_object.id, base_object_c)
    def remove_from_container(self,
                              base_object_c: BaseObject,
                              *base_objects: BaseObject,
                              oneup_only=False):
        if "inventory" not in base_object_c.components:
            raise Exception(f"object {base_object_c} does not have an inventory comp")
        base_object_c.components['inventory']['contents'].difference_update(base_objects)
        for base_object in base_objects:
            self.obj_in_container.remove(base_object.id, base_object_c)
            if oneup_only:
                base_object.contained_by = base_object.contained_by_all()[1]
                self.obj_in_container.add(base_object.id, base_object.contained_by)
            else:
                base_object.contained_by = None
    def make_turn_order(self, turn_duration = None):
        if turn_duration == None:
            turn_duration == 100
        init_obj = np.array([(_o.components["move_points"]["value"],_o.id) for _o in self.obj_type['BaseEntity']],
                            dtype=[('move_points',np.int32),('obj_id',np.int64)])
        to_move = init_obj[init_obj['move_points'] <= turn_duration].sort(order='move_points')
        has_moved = init_obj[init_obj['move_points'] > turn_duration].sort(order='move_points')
        return to_move, has_moved
