import numpy as np  # type: ignore
from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, width: int, height: int, depth: int, start_depth: int = 0):
        self.width, self.height, self.depth = width, height, depth
        self.tiles = np.full((depth, width, height), fill_value=tile_types.wall, order="F")
        self.view_depth = start_depth
        self.rooms = []
        self.visible = np.full((depth,width, height), fill_value=False, order="F")  # Tiles the player can currently see
        self.explored = np.full((depth, width, height), fill_value=False, order="F")  # Tiles the player has seen before




    def in_bounds(self, x: int, y: int, z: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.depth

    def render(self, console: Console) -> None:
        """
                Renders the map.

                If a tile is in the "visible" array, then draw it with the "light" colors.
                If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
                Otherwise, the default is "SHROUD".
                """
        console.rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible[self.view_depth], self.explored[self.view_depth]],
            choicelist=[self.tiles["light"][self.view_depth], self.tiles["dark"][self.view_depth]],
            default=tile_types.SHROUD
        )