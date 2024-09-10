import numpy as np  # type: ignore
from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, width: int, height: int, depth: int, start_depth: int = 0):
        self.width, self.height, self.depth = width, height, depth
        self.tiles = np.full((depth, width, height), fill_value=tile_types.wall, order="F")
        self.view_depth = start_depth



    def in_bounds(self, x: int, y: int, z: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.depth

    def render(self, console: Console) -> None:
        console.rgb[0:self.width, 0:self.height] = self.tiles[self.view_depth]["dark"]