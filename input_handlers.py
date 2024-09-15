from __future__ import annotations
from typing import Optional,TYPE_CHECKING

import tcod.event

from actions import Action, EscapeAction, MovementAction
if TYPE_CHECKING:
    from engine import Engine


class EventHandler(tcod.event.EventDispatch[Action]):
    engine:Engine


    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym
        if key == tcod.event.KeySym.PERIOD:
            self.engine.game_map.view_depth +=1
        if key == tcod.event.KeySym.COMMA:
            self.engine.game_map.view_depth -= 1

        if key == tcod.event.KeySym.UP:
            action = MovementAction(dx=0, dy=-1, dz=0)
        elif key == tcod.event.KeySym.DOWN:
            action = MovementAction(dx=0, dy=1,dz=0)
        elif key == tcod.event.KeySym.LEFT:
            action = MovementAction(dx=-1, dy=0,dz=0)
        elif key == tcod.event.KeySym.RIGHT:
            action = MovementAction(dx=1, dy=0,dz=0)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction()

        # No valid key was pressed
        return action