import tcod

from game_map import GameMap
from actions import MovementAction, EscapeAction
from engine import Engine
from entity import Entity
from input_handlers import EventHandler
from procgen import generate_dungeon


def main() -> None:
    screen_width = 140
    screen_height = 90
    map_width = 140
    map_height = 70
    map_depth = 100
    room_max_size = 20
    room_min_size = 6
    max_rooms = 1500



    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    event_handler = EventHandler()
    player = Entity(int(screen_width / 2), int(screen_height / 2), 9, "@", (255, 255, 255))
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2),0, "@", (255, 255, 0))
    entities = {npc, player}
    game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        map_depth=map_depth,
        player=player
    )
    engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map, player=player)
    event_handler.engine = engine
    with tcod.context.new(
        rows=screen_height,
        columns=screen_width,
        tileset=tileset,
        title="Yet Another Roguelike Tutorial",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            engine.render(console=root_console, context=context)
            events = tcod.event.get()
            engine.handle_events(events)
            engine.render(console=root_console, context=context)


if __name__ == "__main__":
    main()