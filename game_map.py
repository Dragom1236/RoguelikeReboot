from __future__ import annotations

from typing import Iterable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from entity import Entity

import numpy as np  # type: ignore
from tcod.console import Console

import tile_types



class GameMap:
    def __init__(self, width: int, height: int, depth: int, entities: Iterable[Entity] = (), start_depth: int = 0):
        self.width, self.height, self.depth = width, height, depth
        self.tiles = np.full((depth, width, height), fill_value=tile_types.wall, order="F")
        self.view_depth = start_depth
        self.rooms = []
        self.entities = set(entities)
        self.visible = np.full((depth,width, height), fill_value=False, order="F")  # Tiles the player can currently see
        self.explored = np.full((depth, width, height), fill_value=False, order="F")  # Tiles the player has seen before

    def get_blocking_entity_at_location(self, location_x: int, location_y: int, location_z: int) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y and entity.z == location_z:
                return entity

        return None



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

        for entity in self.entities:
            # Only print entities that are in the FOV
            if self.visible[entity.z,entity.x, entity.y] and entity.z==self.view_depth:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)