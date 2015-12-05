import yaml
from PyBearLibTerminal import *
from Thing import Actor, Map, Game_States

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
        cur_layer = terminal_state(TK_LAYER)
        func(*args, **kwargs)
        terminal_layer(cur_layer)
    return func_wrapper

def render_all(character, world, offset):
    render_viewport(world, offset)
    render_UI(character, world)
    render_message_bar()

@layer_wrap
def render_viewport(world, offset):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    terminal_layer(5)
    offset_x, offset_y = offset
    screen_w, screen_h = SCREEN_WIDTH, SCREEN_HEIGHT
    for col, column in enumerate(world):
        if offset_x <= col <= offset_x + screen_w:
            for row, tile in enumerate(column):
                if offset_y <= row <= offset_y + screen_h:
                    tile.build_char()
                    if tile.occupied:
                        terminal_print(tile.x + offset_x,
                                       tile.y + offset_y,
                                       tile.occupied.char)
                    elif tile.prop:
                        terminal_print(tile.x + offset_x,
                                       tile.y + offset_y,
                                       tile.prop.char)
                    elif tile.item:
                        terminal_print(tile.x + offset_x,
                                       tile.y + offset_y,
                                       tile.item.char)
                    else:
                        terminal_print(tile.x + offset_x,
                                       tile.y + offset_y,
                                       tile.char)

@layer_wrap
def render_UI(character, world):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    spacing = 4
    loc = SCREEN_WIDTH + 1
    terminal_layer(10)
    terminal_print(loc, 2 + spacing, "Name:   [color={}]{}".format(character.color, character.name))
    terminal_print(loc, 3 + spacing, "Health: [color=red]{}".format(character.cur_health))
    terminal_print(loc, 4 + spacing, "Mana:   [color=lighter blue]{}".format(character.cur_mana))

@layer_wrap
def render_message_bar():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    terminal_layer(15)
    terminal_print(2, SCREEN_HEIGHT, "Messages: ")

def move_actor(world, actor, to):
    global WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
    fx, fy = actor.x, actor.y
    tx, ty = to
    dx, dy = fx + tx, fy + ty
    if SCREEN_WIDTH > dx >= 0 and SCREEN_HEIGHT > dy >= 0:
        if not world[dx][dy].physical:
            if not world[dx][dy].occupied:
                actor.move(world, tx, ty)

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
    return Actor(world, pc['name'], x, y, pc['char'], pc['color'], pc['physical'],
                 pc['max_health'], pc['max_mana'], pc['attack'], pc['defense'])

def generate_monsters(world):
    return True

def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, CELLSIZE
    terminal_open()
    terminal_set("window: size={}x{}, cellsize={}, title='Roguelike';"
                 "font: default".format(str(WINDOW_WIDTH), str(WINDOW_HEIGHT), CELLSIZE))
    terminal_clear()
    terminal_refresh()
    terminal_color("white")
    offset = (0, 0)

    level = "town"
    world = generate_world(level)
    race = "human"
    pc = generate_player(world, race)

    proceed = True
    while proceed:
        terminal_clear()
        key = 0
        while terminal_has_input():
            key = terminal_read()
            if key == TK_CLOSE or key == TK_Q:
                proceed = False
            elif key == TK_K:
                move_actor(world, pc, (0, -1))
            elif key == TK_J:
                move_actor(world, pc, (0, 1))
            elif key == TK_H:
                move_actor(world, pc, (-1, 0))
            elif key == TK_L:
                move_actor(world, pc, (1, 0))
            elif key == TK_Y:
                move_actor(world, pc, (-1, -1))
            elif key == TK_U:
                move_actor(world, pc, (1, -1))
            elif key == TK_B:
                move_actor(world, pc, (-1, 1))
            elif key == TK_N:
                move_actor(world, pc, (1, 1))
            elif key == (TK_MOUSE_RIGHT):
                terminal_print(TK_MOUSE_X, TK_MOUSE_Y, "[color=yellow]X")
            elif key == (TK_MOUSE_RIGHT | TK_KEY_RELEASED):
                move_actor(world, pc, (1, 1))
        render_all(pc, world, offset)
        terminal_refresh()
    terminal_close()

if __name__ == '__main__':
    main()
