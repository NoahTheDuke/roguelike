import PyBearLibTerminal as blt
from Thing import Actor, Map

WINDOW_WIDTH = 80
WINDOW_HEIGHT = 45
SCREEN_WIDTH = 58
SCREEN_HEIGHT = 36
UPDATE_INTERVAL_MS = 14

cellsize = "12x12"

def make_map():
    return Map(SCREEN_WIDTH, SCREEN_HEIGHT, 2)

def render_all(character, world, world_objs, offset):
    render_viewport(world, world_objs, offset)
    render_sidebar(world_objs, character)
    render_message_bar()

def render_viewport(world, world_objs, offset):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    off_x, off_y = offset
    size_w, size_h = SCREEN_WIDTH, SCREEN_HEIGHT
    for col, column in enumerate(world.layout):
        if off_x <= col <= off_x + size_w:
            for row, tile in enumerate(column):
                if off_y <= row <= off_y + size_h:
                    tile.update_char()
                    blt.print_(tile.x + off_x, tile.y + off_y, tile.char)
    for key, obj in world_objs.items():
        if obj.invisible is not True:
            blt.print_(obj.x, obj.y, obj.char)
    cur_layer = blt.state(blt.TK_LAYER)
    blt.layer(255)
    blt.layer(cur_layer)

def render_sidebar(world_objs, pc_uuid):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    spacing = 4
    loc = SCREEN_WIDTH + 1
    character = world_objs[pc_uuid]
    blt.print_(loc, 2 + spacing, "Name:   {}{}".format(character.color, character.name))
    blt.print_(loc, 3 + spacing, "Health: [color=red]{}".format(character.health))
    blt.print_(loc, 4 + spacing, "Mana:   [color=lighter blue]{}".format(character.mana))

def render_message_bar():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    loc = SCREEN_HEIGHT
    if blt.state(blt.TK_MOUSE_X) <= SCREEN_WIDTH and \
            blt.state(blt.TK_MOUSE_Y) <= SCREEN_HEIGHT:
        blt.print_(2, loc + 1, "X: {}".format(blt.TK_MOUSE_X))
        blt.print_(2, loc + 2, "Y: {}".format(blt.TK_MOUSE_Y))

def move_actor(world, actor, direction):
    global WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
    x, y = direction
    fx, fy = actor.x, actor.y
    dx, dy = fx + x, fy + y
    if SCREEN_WIDTH > dx >= 0 and SCREEN_HEIGHT > dy >= 0:
        if not world.layout[dx][dy].physical:
            if not world.layout[dx][dy].occupied:
                actor.move(world, x, y)

def generate_player(world):
    pc = Actor("Butts", 6, 6, 1, "@", "white", physical=True)
    world.register(pc)
    world_objs = {}
    world_objs[pc.uuid] = pc
    return world_objs, pc

def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
    global cellsize, world_objs, world_obj_locs
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Roguelike';"
             "font: default".format(str(WINDOW_WIDTH), str(WINDOW_HEIGHT), cellsize))
    blt.clear()
    blt.refresh()
    blt.color("white")

    offset = (0, 0)

    full_map = make_map()
    world = full_map
    world_objs, pc = generate_player(world)
    pc_uuid = pc.uuid

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
            # elif key == blt.TK_MOUSE_MOVE:
                    # if blt.check(blt.TK_MOUSE_RIGHT):
                        # selection_bounds = build_selection(selection_origin)
                    # if blt.check(blt.TK_MOUSE_RIGHT|blt.TK_KEY_RELEASED):
                        # selection = build_selection(selection_bounds)
        render_all(pc_uuid, world, world_objs, offset)
        blt.refresh()
    blt.close()

if __name__ == '__main__':
    main()
