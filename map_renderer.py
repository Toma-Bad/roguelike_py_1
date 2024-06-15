from scene_object import Scene
from  bearlibterminal import terminal as blt
import copy
from tcod import map as tcodmap
import tcod.constants
import numpy as np
class MapRenderer:
    def __init__(self, current_scene: Scene):
        #the current maps update as the game runs
        #the render tilemaps update when seen
        #by the player only
        self.current_scene = current_scene
        self.tilemaps = [self.current_scene.terrain_map,
                         self.current_scene.block_map,
                         self.current_scene.item_map,
                         self.current_scene.entity_map]
        self.render_tilemaps = copy.deepcopy(self.tilemaps)
        self.render_layers = {_rt.layer: _rt for _rt in self.render_tilemaps}
        self._trans_map = np.zeros_like(self.tilemaps[0])
        self._fov_map = None

    def compute_fov(self,position,radius = 9):
        self.fov_map = tcodmap.compute_fov(self.trans_map, pov=tuple(position), radius=radius,algorithm=tcod.constants.FOV_DIAMOND)

    @property
    def trans_map(self):
        self._trans_map = np.logical_not(np.any([_tilemap.np_array['opaque'] for _tilemap in self.tilemaps],
                                 axis=0))
        return self._trans_map

    @property
    def fov_map(self):
        return self._fov_map

    @fov_map.setter
    def fov_map(self, fovmap):
        self._fov_map = fovmap
        for _i,(_current_tilemap, _render_tilemap) in enumerate(zip(self.tilemaps, self.render_tilemaps)):
            not_fovmap = np.logical_not(fovmap)
            _render_tilemap.np_array['dark'] = not_fovmap
            _current_tilemap.np_array['dark'] = not_fovmap
            _render_tilemap.np_array[fovmap] = _current_tilemap.np_array[fovmap]

            _current_tilemap.np_array['explored'] = np.logical_or(fovmap,
                                                                  _current_tilemap.np_array['explored'])
            _render_tilemap.np_array['explored'] = np.logical_or(fovmap,
                                                                 _render_tilemap.np_array['explored'])
            self.tilemaps[_i] = _current_tilemap
            self.render_tilemaps[_i] = _render_tilemap
            self.render_layers[_render_tilemap.layer]= _render_tilemap

    def render(self):
        for key in sorted(self.render_layers.keys()):
            map_to_render = copy.deepcopy(self.render_layers[key].np_array)
            darkmap = np.where(map_to_render['dark'] == True)
            map_to_render['sprite']['fg'][darkmap] = map_to_render['sprite']['fg'][darkmap]//2
            map_to_render['sprite']['bg'][darkmap] = (map_to_render['sprite']['bg'][darkmap]//2)
            if key > 1:
                unexmap = darkmap
            else:
                unexmap = np.where(map_to_render['explored'] == False)
            map_to_render['sprite']['fg'][unexmap] = (map_to_render['sprite']['fg'][unexmap]*0)
            map_to_render['sprite']['bg'][unexmap] = (map_to_render['sprite']['bg'][unexmap]*0)
            blt.layer(key)

            blt.put_np_array(0,
                             0,
                             map_to_render['sprite'],
                             'ch',
                             'fg',
                             'bg')
