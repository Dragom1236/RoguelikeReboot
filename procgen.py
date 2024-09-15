from __future__ import annotations
import random
import tcod
from typing import Tuple, Iterator, List

import tile_types
from entity import Entity
from game_map import GameMap


class RectPrismRoom:
    def __init__(self, x: int, y: int, z: int, width: int, height: int, depth: int):
        self.x1 = x
        self.y1 = y
        self.z1 = z
        self.x2 = x + width
        self.y2 = y + height
        self.z2 = z + depth
        self.connections: List[RectPrismRoom] = []

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

    @property
    def air_inner(self) -> Tuple[slice, slice, slice]:
        """Return the inner area of this room that represents air as a 2D array index."""
        return slice(self.z1 + 2, self.z2), slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)


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


def join_rooms(dungeon: GameMap, room1: RectPrismRoom, room2: RectPrismRoom) -> None:
    for z, x, y in tunnel_between(room1.floor_center, room2.floor_center):
        dungeon.tiles[z, x, y] = tile_types.floor


def generate_dungeon(
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        map_depth: int,
        player: Entity,
        chunk_depth: int = 15,
        chunk_bisection_ratio: float = 0,
        number_of_layers: int = 0,
        chunk_offset: int = 0) -> GameMap:
    """Generate a new dungeon map.
    Max rooms is the upper bound of rooms in the dungeon.
    room_min_size and room_max_size determine the minimum and maximum dimensions for a room respectively.

    chunk_depth represent the height of 'chunks' or partitions of the map space in the game map.
    Rooms sit at the bottom of the chunks, and are created in order and layer of their chunk from top to bottom.
    chunk_bisection_ratio is an alternate way to set your chunk_depth based on how deep you want chunks to be.
    Multiplying the chunk_bisection_ratio by the map_depth gives you the chunk_depth.
    number_of_layers allows you to explicitly set the number of layers in the dungeon.
    It is divided by the map_depth to give the chunk_bisection_ratio, which gives the chunk_depth.
    chunk_depth is automatically set to the room_max_size if it is less than it.

    As rooms sit at the bottom of a chunk, their z value and depth must add up to the chunk_depth.
    For simplicity, the depth of a room is generated randomly first, then its z value is calculated based on its depth.

    chunk_offset creates a mini-layer in between layers that will not be filled with rooms.
    This can be used in cases where you may not want rooms to be immediately layered untop of each other.
    A similar effect can be achieved by setting chunk_depth higher than the room_max_size.
    chunk_offset will be taken as a positive value, and cannot be negative  as that would create overlapping chunks.

    This function distributes rooms evenly among chunks.
    If max rooms is 50, and there are 5 chunks, it will attempt to generate 10 rooms in each chunk.

     """
    if number_of_layers > 0:
        chunk_bisection_ratio = number_of_layers / map_depth
    if chunk_bisection_ratio > 0:
        chunk_depth = int(map_depth * chunk_bisection_ratio)
    if chunk_depth < room_max_size:
        chunk_depth = room_max_size
    dungeon: GameMap = GameMap(map_width, map_height, map_depth)
    rooms: List[RectPrismRoom] = []
    chunk_offset = abs(chunk_offset)
    if chunk_offset == 0:
        chunks: list[tuple[int, int]] = [(i, min(i + chunk_depth - 1, map_depth)) for i in
                                         range(0, map_depth, chunk_depth)]
    else:
        chunks: list[tuple[int, int]] = [(i, min(i + chunk_depth - 1, map_depth - chunk_offset)) for i in
                                         range(chunk_offset, map_depth - chunk_offset, chunk_depth + chunk_offset)]
    print("chunks:", chunks)
    for chunk in chunks:
        if chunk[1]-chunk[0]<chunk_depth-1:
            continue
        for r in range(max_rooms // (map_depth // chunk_depth)):
            room_width = random.randint(room_min_size, room_max_size)
            room_height = random.randint(room_min_size, room_max_size)
            room_depth = min(random.randint(room_min_size, room_max_size), chunk[1]-chunk[0])

            x = random.randint(0, dungeon.width - room_width - 1)
            y = random.randint(0, dungeon.height - room_height - 1)
            z = max(0, chunk[1] - room_depth)

            # "RectPrismRoom" class makes rectangular prisms easier to work with
            new_room = RectPrismRoom(x, y, z, room_width, room_height, room_depth)

            # Run through the other rooms and see if they intersect with this one.
            if any(new_room.intersects(other_room) for other_room in rooms):
                continue  # This room intersects, so go to the next attempt.
            # If there are no intersections then the room is valid.

            # Dig out this rooms inner area.
            dungeon.tiles[new_room.inner] = tile_types.floor

            if len(rooms) == 0:
                # The first room, where the player starts.
                player.z, player.x, player.y = new_room.floor_center
            else:  # All rooms after the first.
                # Dig out a tunnel between this room and the previous one.
                join_rooms(dungeon, rooms[-1], new_room)
            # Finally, append the new room to the list.
            rooms.append(new_room)
            print("x", x, "y", y, "z", z)
            print("width", room_width, "height", room_height, "depth", room_depth)
    dungeon.view_depth = player.z
    print("We got this many rooms:", len(rooms))
    return dungeon
