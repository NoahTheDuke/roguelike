import yaml
import PyBearLibTerminal as blt
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

def render_all(character, world, offset):
    render_viewport(world, offset)
    render_sidebar(character, world)
    render_message_bar()

def render_viewport(world, offset):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    offset_x, offset_y = offset
    screen_w, screen_h = SCREEN_WIDTH, SCREEN_HEIGHT
    print_ = blt.print_
    for col, column in enumerate(world):
        if offset_x <= col <= offset_x + screen_w:
            for row, tile in enumerate(column):
                if offset_y <= row <= offset_y + screen_h:
                    tile.update_char()
                    if tile.occupied:
                        print_(tile.x + offset_x,
                               tile.y + offset_y,
                               tile.occupied.char)
                    elif tile.prop:
                        print_(tile.x + offset_x,
                               tile.y + offset_y,
                               tile.prop.char)
                    elif tile.item:
                        print_(tile.x + offset_x,
                               tile.y + offset_y,
                               tile.item.char)
                    else:
                        print_(tile.x + offset_x,
                               tile.y + offset_y,
                               tile.char)

def render_sidebar(character, world):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    spacing = 4
    loc = SCREEN_WIDTH + 1
    blt.print_(loc, 2 + spacing, "Name:   {}{}".format(character.color, character.name))
    blt.print_(loc, 3 + spacing, "Health: [color=red]{}".format(character.cur_health))
    blt.print_(loc, 4 + spacing, "Mana:   [color=lighter blue]{}".format(character.cur_mana))

def render_message_bar():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    blt.print_(2, SCREEN_HEIGHT, "Messages: ")

def move_actor(world, actor, direction):
    global WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
    x, y = direction
    fx, fy = actor.x, actor.y
    dx, dy = fx + x, fy + y
    if SCREEN_WIDTH > dx >= 0 and SCREEN_HEIGHT > dy >= 0:
        if not world[dx][dy].physical:
            if not world[dx][dy].occupied:
                actor.move(world, x, y)

def generate_world(level):
    w = []
    with open("data/world.yaml", 'r') as world_yaml:
        world = yaml.load_all(world_yaml)
        for x in world:
            w.append(x)
        w = w[0]
    return Map(SCREEN_WIDTH, SCREEN_HEIGHT, num_exits=2)

def generate_player(world, race):
    with open("data/player.yaml", 'r') as player_yaml:
        pc = yaml.load(player_yaml)
    x, y = 6, 6
    pc = pc[race]
    return Actor(world, pc['name'], x, y, pc['char'], pc['color'], pc['physical'],
                 pc['max_health'], pc['max_mana'], pc['attack'], pc['defense'])

def generate_monsters(world):
    return True

def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
    global CELLSIZE
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Roguelike';"
             "font: default".format(str(WINDOW_WIDTH), str(WINDOW_HEIGHT), CELLSIZE))
    blt.clear()
    blt.refresh()
    blt.color("white")
    offset = (0, 0)

    level = "town"
    world = generate_world(level)
    race = "human"
    pc = generate_player(world, race)

    proceed = True
    while proceed:
        blt.clear()
        key = 0
        while blt.has_input():
            key = blt.read()
            if key == blt.TK_CLOSE or key == blt.TK_Q:
                proceed = False
            elif key == blt.TK_K:
                move_actor(world, pc, (0, -1))
            elif key == blt.TK_J:
                move_actor(world, pc, (0, 1))
            elif key == blt.TK_H:
                move_actor(world, pc, (-1, 0))
            elif key == blt.TK_L:
                move_actor(world, pc, (1, 0))
            elif key == blt.TK_Y:
                move_actor(world, pc, (-1, -1))
            elif key == blt.TK_U:
                move_actor(world, pc, (1, -1))
            elif key == blt.TK_B:
                move_actor(world, pc, (-1, 1))
            elif key == blt.TK_N:
                move_actor(world, pc, (1, 1))
            elif key == (blt.TK_MOUSE_RIGHT):
                blt.print_(blt.TK_MOUSE_X, blt.TK_MOUSE_Y, "[color=yellow]X")
            elif key == (blt.TK_MOUSE_RIGHT | blt.TK_KEY_RELEASED):
                move_actor(world, pc, (1, 1))
        render_all(pc, world, offset)
        blt.refresh()
    blt.close()

if __name__ == '__main__':
    main()
