from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this action is being performed in.

        `entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()


class ActionWithDirection(Action):
    def __init__(self, dx: int, dy: int, dz: int):
        super().__init__()

        self.dx = dx
        self.dy = dy
        self.dz = dz

    def perform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()


class MovementAction(ActionWithDirection):

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        dest_z = entity.z + self.dz

        if not engine.game_map.in_bounds(dest_x, dest_y, dest_z):
            return  # Destination is out of bounds.
        if not engine.game_map.tiles["walkable"][dest_z, dest_x, dest_y]:
            return  # Destination is blocked by a tile.
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y,dest_z):
            return  # Destination is blocked by an entity.

        entity.move(self.dx, self.dy, self.dz)


class MeleeAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        dest_z = entity.z + self.dz
        target = engine.game_map.get_blocking_entity_at_location(dest_x, dest_y,dest_z)
        if not target:
            return  # No entity to attack.

        print(f"You kick the {target.name}, much to its annoyance!")


class BumpAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        dest_z = entity.z + self.dz

        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y, dest_z):
            return MeleeAction(self.dx, self.dy,self.dz).perform(engine, entity)

        else:
            return MovementAction(self.dx, self.dy, self.dz).perform(engine, entity)