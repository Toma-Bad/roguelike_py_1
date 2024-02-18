from map_new import *
class Scene:
    def __init__(self, scene_width, scene_height):
        self.ids = dict()
        self.obj_positions = SetDict()
        self.obj_type = SetDict()
        self.obj_components = SetDict()
        self.comp_timers = SetDict()
        #self.obj_loc_arr = np.empty((scene_width, scene_height), dtype=object)
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

    def move_obj(self, base_object: BaseObject, new_position):
        old_position = base_object.position
        self.obj_positions.move(old_position, new_position, base_object)
        if "Container" in base_object.component.__dict__:
            for _obj in base_object.component.Container.storage:
                self.move_obj(_obj, new_position)
                _obj.position = new_position
        base_object.position = new_position

    def add_obj(self, base_object: BaseObject, at_position=None):
        if at_position:
            base_object.position = at_position
        self.ids[base_object.id] = base_object
        self.obj_positions.add(base_object.position, base_object)
        self.obj_type.add(type(base_object).__name__, base_object)
        if base_object.contained_by:
            self.obj_in_container.add(base_object.id, base_object.contained_by)

        for _c in base_object.component.__dict__:
            self.obj_components.add(_c, base_object)

    def rem_obj(self, base_object: BaseObject):
        if base_object.id not in self.ids:
            print('object not in scene')
            return 0
        else:
            del self.ids[base_object.id]
        self.obj_positions.remove(base_object.position, base_object)
        self.obj_type.remove(type(base_object).__name__, base_object)
        if base_object.contained_by:
            self.obj_in_container.remove(base_object.id, base_object.contained_by)
        if "Container" in base_object.component.__dict__:
            for _obj in base_object.component.Container.storage:
                _obj.contained_by = _obj.contained_by_all()[1]
        for _c in base_object.component.__dict__:
            self.obj_components.remove(_c, base_object)

    def add_component(self, base_object: BaseObject, *components: BaseComponent, **kcomponents: BaseComponent):
        if base_object.id not in self.ids:
            raise Exception(f"object not in scene!{base_object.id}")
        base_object.component.__dict__.update({type(_c).__name__: _c for _c in components})
        base_object.component.__dict__.update(kcomponents)
        for _c in components:
            self.obj_components.add(type(_c).__name__, base_object)
            if hasattr(_c, 'timer'):
                self.comp_timers.add('timer', _c)
        for _c in kcomponents:
            self.obj_components.add(_c, kcomponents[_c])
            if hasattr(_c, 'timer'):
                self.comp_timers.add('timer', kcomponents[_c])

    def remove_component(self, base_object: BaseObject, *components, **kcomponents):
        if base_object.id not in self.ids:
            raise Exception(f"object not in scene!{base_object.id}")

        base_object.component.__dict__.update(kcomponents)
        for _c in components:
            base_object.component.__delattr__(type(_c).__name__)
            self.obj_components.remove(type(_c).__name__, base_object)
            if hasattr(_c, 'timer'):
                self.comp_timers.remove('timer', _c)
        for _c in kcomponents:
            base_object.component.__delattr__(_c)
            self.obj_components.remove(_c, kcomponents[_c])
            if hasattr(_c, 'timer'):
                self.comp_timers.remove('timer', kcomponents[_c])

    def add_to_container(self, base_object_c: BaseObject, *base_objects: BaseObject):
        if "Container" not in base_object_c.component.__dict__:
            raise Exception(f"object {base_object_c} does not have a Container comp")
        base_object_c.component.Container.storage.update(base_objects)
        for base_object in base_objects:
            base_object.contained_by = base_object_c
            self.obj_in_container.add(base_object.id, base_object_c)

    def remove_from_container(self,
                              base_object_c: BaseObject,
                              *base_objects: BaseObject,
                              oneup_only=False):
        if "Container" not in base_object_c.component.__dict__:
            raise Exception(f"object {base_object_c} does not have a Container comp")
        base_object_c.component.Container.storage.difference_update(base_objects)
        for base_object in base_objects:
            if oneup_only:
                base_object.contained_by = base_object.contained_by_all()[1]
            else:
                base_object.contained_by = None
            self.obj_in_container.remove(base_object.id, base_object_c)
