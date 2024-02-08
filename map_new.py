import numpy as np



class TileMap:
    def __init__(self, width=128, height=128, layer=0):

        self.np_array = np.zeros((width, height), dtype=tile_dt)
        self.layer = layer

    def add_set(self, obj_set: set[BaseObject]):
        for obj in obj_set:
            self.add_obj(obj)

    def set_set(self, obj_set: set[BaseObject]):
        self.np_array[:] = 0
        self.add_set(obj_set)

    def rem_set(self, obj_set: set[BaseObject]):
        for obj in obj_set:
            self.rem_obj(obj)

    def add_obj(self, obj: BaseObject):
        self.np_array[obj.position]['gf_tile'] = obj.component.SpriteComponent.sprite

    def rem_obj(self, obj: BaseObject):
        self.np_array[obj.position] = 0


class MapRenderer:
    def __init__(self, *tilemaps: TileMap):
        #the current maps update as the game runs
        #the render tilemaps update when seen
        #by the player only
        self.current_tilemaps = tilemaps
        self.render_tilemaps = copy.deepcopy(tilemaps)
        self.render_layers = {_rt.layer: _rt for _rt in self.render_tilemaps}
        self._trans_map = np.zeros_like(tilemaps[0])
        self._fov_map = None

    @property
    def trans_map(self):
        self._trans_map = np.any([_tilemap.np_array['transparent'] for _tilemap in self.current_tilemaps],
                                 axis=0)
        return self._trans_map

    @property
    def fov_map(self):
        return self._fov_map

    @fov_map.setter
    def fov_map(self, fovmap):
        self._fov_map = fovmap
        for _current_tilemap, _render_tilemap in zip(self.current_tilemaps, self.render_tilemaps):
            not_fovmap = np.logical_not(fovmap)
            _current_tilemap.np_array['dark'] = not_fovmap
            _render_tilemap.np_array[not_fovmap] = _current_tilemap.np_array[not_fovmap]
            _current_tilemap.np_array['explored'] = np.logical_or(fovmap,
                                                                  _current_tilemap.np_array['explored'])
            _render_tilemap.np_array['explored'] = np.logical_or(fovmap,
                                                                 _render_tilemap.np_array['explored'])

    def render(self):
        for key in sorted(self.render_layers.keys()):
            map_to_render = self.render_layers[key].np_array['gf_tile']
            darkmap = np.where(map_to_render['dark'] == True)
            map_to_render['fg'][darkmap] = (map_to_render['gf_tile']['fg'][darkmap]
                                            // np.array([2, 1, 1, 1]))
            map_to_render['bg'][darkmap] = (map_to_render['gf_tile']['bg'][darkmap]
                                            // np.array([2, 1, 1, 1]))
            unexmap = np.where(map_to_render['explored'] == False)
            map_to_render['fg'][unexmap] = (map_to_render['gf_tile']['fg'][unexmap]
                                            * np.array([1, 0, 0, 0]))
            map_to_render['bg'][unexmap] = (map_to_render['gf_tile']['bg'][unexmap]
                                            * np.array([1, 0, 0, 0]))
            blt.layer(key)
            blt.put_np_array(0,
                             0,
                             self.render_layers[key].np_array['gf_tile'],
                             'ch',
                             'fg',
                             'bg')


