from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

import tile_types
from game_map import GameMap
from actions import EscapeAction, MovementAction
from entity import Entity
from input_handlers import EventHandler


class Engine:
    def __init__(self, entities: Set[Entity], event_handler: EventHandler, game_map: GameMap, player: Entity):
        self.entities = entities
        self.event_handler = event_handler
        self.player = player
        self.game_map = game_map
        self.update_fov()

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)
            self.update_fov()  # Update the FOV before the players next action.

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        # Right now we only compute the fov for the level the player is on.
        # We want to also do so spherically for each level the player isn't on.
        self.compute_3d_fov()
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def compute_3d_fov(self, radius=15) -> None:
        for i in range(radius):
            self.game_map.visible[min(self.player.z + i, self.game_map.depth - 1),:] = compute_fov(
                self.game_map.tiles["transparent"][min(self.player.z + i, self.game_map.depth - 1)],
                (self.player.x, self.player.y),
                radius=radius-i,
            )
            if self.game_map.tiles[self.player.z+i,self.player.x,self.player.y] == tile_types.wall:
                break
        for i in range(radius):
            self.game_map.visible[max(self.player.z - i, 0),:] = compute_fov(
                self.game_map.tiles["transparent"][max(self.player.z - i, 0)],
                (self.player.x, self.player.y),
                radius=radius-i,
            )
            if self.game_map.tiles[self.player.z-i,self.player.x,self.player.y] == tile_types.wall:
                break
        self.game_map.visible[self.player.z,:] = compute_fov(
            self.game_map.tiles["transparent"][self.player.z],
            (self.player.x, self.player.y),
            radius=radius,
        )

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        for entity in self.entities:
            # Only print entities that are in the FOV
            if self.game_map.visible[entity.z,entity.x, entity.y] and entity.z==self.game_map.view_depth:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)

        context.present(console)

        console.clear()
