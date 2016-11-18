import yaml
import PyBearLibTerminal as terminal
from Thing import Actor, Map, Game_States, COLOR
from time import perf_counter
import random

# Rendering constants
WINDOW_WIDTH = 80
WINDOW_HEIGHT = 45
SCREEN_WIDTH = 58
SCREEN_HEIGHT = 36
UPDATE_INTERVAL_MS = 14
CELLSIZE = "12x12"

# Game state constants
game_states = Game_States


def layer_wrap(func):
    def func_wrapper(*args, **kwargs):
        cur_layer = terminal.state(terminal.TK_LAYER)
        func(*args, **kwargs)
        terminal.layer(cur_layer)
    return func_wrapper


def render(world, pc, offset):
    terminal.clear()
    if pc.fog_toggle:
        world.calculate_fov(pc)
    render_viewport(world, pc, offset)
    render_UI(world, pc)
    render_message_bar()
    terminal.refresh()


def find_offset(world, pc, offset):
    """
    From: http://www.roguebasin.com/index.php?title=Scrolling_map
    Get the position of the camera in a scrolling map:

     - p is the position of the player.
     - hs is half of the screen size, and s is the full screen size.
     - m is the size of the map.
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT
    offset_x, offset_y = offset
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2

    if pc.x < center_x:
        offset_x = 0
    elif pc.x > world.width - center_x:
        offset_x = world.width - SCREEN_WIDTH
    else:
        offset_x = pc.x - center_x
    if pc.y < center_y:
        offset_y = 0
    elif pc.y > world.height - center_y:
        offset_y = world.height - SCREEN_HEIGHT
    else:
        offset_y = pc.y - center_y
    return (offset_x, offset_y)


@layer_wrap
def render_viewport(world, pc, offset):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    terminal.layer(0)
    offset_x, offset_y = offset
    for col, column in enumerate(world):
        if offset_x <= col < offset_x + SCREEN_WIDTH:
            for row, tile in enumerate(column):
                if offset_y <= row < offset_y + SCREEN_HEIGHT:
                    if (tile.x, tile.y) in pc.viewed_map or not pc.fog_toggle:
                        tile.build_char(world.fov_map,
                                        pc.fog_toggle)
                        if tile.occupied:
                            terminal.print_(tile.x - offset_x,
                                       tile.y - offset_y,
                                       tile.occupied.char)
                        elif tile.item:
                            terminal.print_(tile.x - offset_x,
                                       tile.y - offset_y,
                                       tile.item.char)
                        elif tile.prop:
                            terminal.print_(tile.x - offset_x,
                                       tile.y - offset_y,
                                       tile.prop.char)
                        else:
                            terminal.print_(tile.x - offset_x,
                                       tile.y - offset_y,
                                       tile.char)


@layer_wrap
def render_UI(world, pc):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    spacing = 0
    loc = SCREEN_WIDTH + 1
    terminal.layer(10)
    terminal.print_(loc, 1 + spacing, "Name:   [color={}]{}".format(
        pc.color, pc.name))
    terminal.print_(loc, 2 + spacing, "Health: [color={}]{}".format(
        COLOR['pink'], pc.cur_health))
    terminal.print_(loc, 3 + spacing, "Mana:   [color={}]{}".format(
        COLOR['blue'], pc.cur_mana))
    terminal.print_(loc, 4 + spacing, "X:      {}".format(pc.x))
    terminal.print_(loc, 5 + spacing, "Y:      {}".format(pc.y))


@layer_wrap
def render_message_bar():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    terminal.layer(15)
    terminal.print_(2, SCREEN_HEIGHT, "Messages: ")

square = False


def move_actor(world, pc, to):
    global WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, square
    fx, fy = pc.x, pc.y
    tx, ty = to
    dx, dy = fx + tx, fy + ty
    if world.width > dx >= 0 and world.height > dy >= 0:
        pc.move(world, tx, ty)


def try_door(world, pc):
    adjacent = pc.adjacent(world)
    for (x, y) in adjacent:
        if world[x][y].check_door():
            world[x][y].toggle_door()
            pc.move(world, 0, 0)


def generate_world(name):
    w = []
    with open("data/world.yaml", 'r') as world_yaml:
        world = yaml.load_all(world_yaml)
        for x in world:
            w.append(x)
        w = w[0]
    w = w[name]
    return Map(name=w['name'], width=w['width'], height=w['height'],
               min_rooms=w['min_rooms'], max_rooms=w['max_rooms'],
               num_exits=w['num_exits'], level=w['level'], region=w['region'])


def generate_player(world, race):
    with open("data/player.yaml", 'r') as player_yaml:
        pc = yaml.load(player_yaml)
    x, y = world.start_loc
    pc = pc[race]
    return Actor(world, pc['name'], x, y, pc['char'], pc['color'],
                 pc['physical'], pc['max_health'], pc['max_mana'],
                 pc['attack'], pc['defense'])


def generate_monsters(world):
    with open('data/monsters.yaml', 'r') as monsters_yaml:
        monsters = yaml.load(monsters_yaml)
    print(monsters)


def update(world, pc, offset, time_elapsed, time_current):
    offset = find_offset(world, pc, offset)
    return world, pc, offset


def process_input(key, world, pc):
    if key == terminal.TK_K:
        move_actor(world, pc, (0, -1))
    elif key == terminal.TK_J:
        move_actor(world, pc, (0, 1))
    elif key == terminal.TK_H:
        move_actor(world, pc, (-1, 0))
    elif key == terminal.TK_L:
        move_actor(world, pc, (1, 0))
    elif key == terminal.TK_Y:
        move_actor(world, pc, (-1, -1))
    elif key == terminal.TK_U:
        move_actor(world, pc, (1, -1))
    elif key == terminal.TK_B:
        move_actor(world, pc, (-1, 1))
    elif key == terminal.TK_N:
        move_actor(world, pc, (1, 1))
    elif key == terminal.TK_PERIOD:
        move_actor(world, pc, (0, 0))
    elif key == terminal.TK_C:
        try_door(world, pc)
    elif key == terminal.TK_F:
        pc.fog_toggle = not pc.fog_toggle
    elif key == terminal.TK_S:
        pc.change_los()
    elif key == terminal.TK_R:
        world.generate_map(world.width, world.height, world.num_exits)
        pc.place(world.start_loc)
        world.register(pc)
        pc.viewed_map = set()


def initialize():
    global WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, CELLSIZE
    terminal.open()
    terminal.set("window: size={}x{}, cellsize={}, title='Roguelike';"
             "font: default".format(
                 str(WINDOW_WIDTH), str(WINDOW_HEIGHT), CELLSIZE))
    terminal.clear()
    terminal.refresh()
    terminal.color("white")
    # random.seed(2)


def main():
    initialize()

    level = 'debug'
    world = generate_world(level)
    race = 'human'
    pc = generate_player(world, race)
    offset = find_offset(world, pc, (0, 0))

    UPDATE_INTERVAL_MS = 0.033
    UPDATE_PER_FRAME_LIMIT = 10
    clock = 0
    previous_time = perf_counter()
    next_update = 0
    proceed = True

    while proceed:
        current_time = perf_counter()
        if (current_time - previous_time) > (
                UPDATE_INTERVAL_MS * UPDATE_PER_FRAME_LIMIT):
            clock += UPDATE_INTERVAL_MS * UPDATE_PER_FRAME_LIMIT
        else:
            clock += current_time - previous_time
        while clock >= next_update:
            time_elapsed = UPDATE_INTERVAL_MS
            time_current = next_update
            world, pc, offset = update(world, pc, offset,
                                       time_elapsed, time_current)
            next_update += UPDATE_INTERVAL_MS
        previous_time = perf_counter()

        render(world, pc, offset)

        key = 0
        while terminal.has_input():
            key = terminal.read()
            if key == terminal.TK_CLOSE or key == terminal.TK_Q:
                proceed = False
            else:
                process_input(key, world, pc)

    # if proceed is False, end the program
    terminal.close()

if __name__ == '__main__':
    main()
