from __future__ import annotations
import random
import tcod
from typing import Tuple, Iterator

import tile_types
from game_map import GameMap


class RectPrismRoom:
    def __init__(self, x: int, y: int, z: int, width: int, height: int, depth: int):
        self.x1 = x
        self.y1 = y
        self.z1 = z
        self.x2 = x + width
        self.y2 = y + height
        self.z2 = z + depth

    def intersects(self, other: RectPrismRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""

        return (
                self.x1 <= other.x2
                and self.x2 >= other.x1
                and self.y1 <= other.y2
                and self.y2 >= other.y1
                and self.z1 <= other.z2
                and self.z2 >= other.z1
        )

    @property
    def center(self) -> Tuple[int, int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        center_z = int((self.z1 + self.z2) / 2)

        return center_z, center_x, center_y

    @property
    def floor_center(self) -> Tuple[int, int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return self.z2 - 1, center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.z1 + 1, self.z2), slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)


def tunnel_between(
        start: Tuple[int, int, int], end: Tuple[int, int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points, provided these points are on the same z level"""
    z = start[0]
    x1, y1 = start[1:]
    x2, y2 = end[1:]
    if random.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield z, x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield z, x, y


def generate_dungeon(map_width, map_height, map_depth, start_depth) -> GameMap:
    dungeon = GameMap(map_width, map_height, map_depth, start_depth)

    room_1 = RectPrismRoom(x=20, y=15, z=0, width=10, height=40, depth=10)
    room_2 = RectPrismRoom(x=65, y=15, z=0, width=10, height=40, depth=10)

    dungeon.tiles[room_1.inner] = tile_types.floor
    dungeon.tiles[room_2.inner] = tile_types.floor
    for z, x, y in tunnel_between(room_2.floor_center, room_1.floor_center):
        dungeon.tiles[z, x, y] = tile_types.floor
        print(z, x, y)

    return dungeon
