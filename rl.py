import PyBearLibTerminal as blt
from Thing import Actor, Tile

window_width = 80
window_height = 45
screen_width = 58
screen_height = 36
current_floor_objs = {}
current_floor_obj_locs = []
selection = []
selector_objs = set()
mouse_x = 0
mouse_y = 0

cellsize = "12x12"
redhat = "[+][color=red][offset=0,0]^"

def make_map():
    layout = [[Tile(x, y, 1, '.', 'amber', False)
        for y in range(window_height)]
            for x in range(window_width)]
    locations = [[None
        for y in range(window_height)]
            for x in range(window_width)]
    return layout, locations

def render_all(current_floor, current_floor_objs, offset):
    global selection
    render_viewport(current_floor, current_floor_objs, offset)
    render_sidebar(selection)
    render_message_bar()

def render_viewport(current_floor, current_floor_objs, offset):
    global screen_width, screen_height, selector_objs
    off_x, off_y = offset
    size_w, size_h = screen_width, screen_height
    for col, column in enumerate(current_floor):
        if off_x <= col <= off_x + size_w:
            for row, tile in enumerate(column):
                if off_y <= row <= off_y + size_h:
                    tile.update_char()
                    blt.print_(tile.x + off_x, tile.y + off_y, tile.char)
    for key, obj in current_floor_objs.items():
        if obj.invisible is not True:
            blt.print_(obj.x, obj.y, obj.char)
    cur_layer = blt.state(blt.TK_LAYER)
    blt.layer(255)
    for x, y in selector_objs:
        blt.print_(x, y, "[color=yellow]X")
    blt.layer(cur_layer)

def render_sidebar(selection):
    global screen_width, screen_height
    spacing = 4
    loc = screen_width + 1
    for idx, character in enumerate(selection):
        if character:
            blt.print_(loc, 2 + spacing * idx, "Name:   {}{}".format(character.color, character.name))
            blt.print_(loc, 3 + spacing * idx, "Health: [color=red]{}".format(character.health))
            blt.print_(loc, 4 + spacing * idx, "Mana:   [color=lighter blue]{}".format(character.mana))
        else:
            blt.print_(loc, 2, "Nothing selected.")

def render_message_bar():
    global screen_width, screen_height, window_width, window_height
    global mouse_x, mouse_y
    loc = screen_height
    blt.print_(2, loc + 1, "X: {}".format(mouse_x))
    blt.print_(2, loc + 2, "Y: {}".format(mouse_y))

def move_character(current_floor, direction):
    global window_width, window_height, screen_width, screen_height
    global selection, current_floor_objs, current_floor_obj_locs
    for idx, character in enumerate(selection):
        x, y = direction
        fx, fy = character.x, character.y
        dx, dy = fx + x, fy + y
        if screen_width >= dx >= 0 and screen_height >= dy >= 0:
            if not current_floor[dx][dy].physical:
                if current_floor_obj_locs[dx][dy]:
                    if not current_floor_objs[current_floor_obj_locs[dx][dy]].physical:
                        current_floor_obj_locs[fx][fy] = None
                        character.move(x, y)
                        current_floor_obj_locs[dx][dy] = character.uuid
                else:
                    current_floor_obj_locs[fx][fy] = None
                    character.move(x, y)
                    current_floor_obj_locs[dx][dy] = character.uuid

def build_selection(origin):
    global window_width, window_height, screen_width, screen_height
    global selection, current_floor_objs, current_floor_obj_locs
    global mouse_x, mouse_y, selector_objs
    selector_objs.clear()
    x, y = origin[0], origin[1]
    width = abs(x - mouse_x)
    height = abs(y - mouse_y)
    for idx in range(width + 1):
        if mouse_x >= x:
            selector_objs.add((idx + x, y))
            selector_objs.add((idx + x, mouse_y))
        else:
            selector_objs.add((x - idx, y))
            selector_objs.add((x - idx, mouse_y))
    for idx in range(height + 1):
        if mouse_y >= y:
            selector_objs.add((x, idx + y))
            selector_objs.add((mouse_x, idx + y))
        else:
            selector_objs.add((x, y - idx))
            selector_objs.add((mouse_x, y - idx))

def generate_characters():
    global current_floor_obj_locs
    pc = Actor(6, 6, 1, "Butts", "@", "white", physical=True, invisible=False)
    pc2 = Actor(7, 7, 1, "Ass", "@", "green", physical=True, invisible=False)
    current_floor_objs = {}
    current_floor_objs[pc.uuid] = pc
    current_floor_obj_locs[pc.x][pc.y] = pc.uuid
    current_floor_objs[pc2.uuid] = pc2
    current_floor_obj_locs[pc2.x][pc2.y] = pc2.uuid
    return current_floor_objs

def main():
    global window_width, window_height, screen_width, screen_height
    global cellsize, selection, mouse_x, mouse_y, selector_objs
    global current_floor_objs, current_floor_obj_locs
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Roguelike';"
             "font: default".format(str(window_width), str(window_height), cellsize))
    blt.clear()
    blt.refresh()
    blt.color("white")

    offset = (0, 0)

    full_map, full_map_obj_locs = make_map()
    current_floor, current_floor_obj_locs = full_map, full_map_obj_locs
    current_floor_objs = generate_characters()

    render_all(current_floor, current_floor_objs, offset)
    proceed = True
    selection_bool = False
    selection_origin = (0, 0)
    while proceed:
        blt.clear()
        key = 0
        while blt.has_input():
            key = blt.read()
            if key == blt.TK_CLOSE or key == blt.TK_Q:
                proceed = False
            elif key == blt.TK_ESCAPE:
                del selection[:]
            elif key == blt.TK_K:
                move_character(current_floor, (0, -1))
            elif key == blt.TK_J:
                move_character(current_floor, (0, 1))
            elif key == blt.TK_H:
                move_character(current_floor, (-1, 0))
            elif key == blt.TK_L:
                move_character(current_floor, (1, 0))
            elif key == blt.TK_Y:
                move_character(current_floor, (-1, -1))
            elif key == blt.TK_U:
                move_character(current_floor, (1, -1))
            elif key == blt.TK_B:
                move_character(current_floor, (-1, 1))
            elif key == blt.TK_N:
                move_character(current_floor, (1, 1))
            elif key == (blt.TK_MOUSE_LEFT | blt.TK_KEY_RELEASED):
                if not blt.check(blt.TK_SHIFT):
                    del selection[:]
                if current_floor_obj_locs[mouse_x][mouse_y]:
                    selection.append(current_floor_objs[current_floor_obj_locs[mouse_x][mouse_y]])
            elif key == (blt.TK_MOUSE_RIGHT):
                if not selection_bool:
                    selection_bool = True
                    selection_origin = (mouse_x, mouse_y)
            elif key == (blt.TK_MOUSE_RIGHT | blt.TK_KEY_RELEASED):
                selector_objs.clear()
                selection_bool = False
            elif key == blt.TK_A:
                for character in selection:
                    character.apparel.add(redhat)
                    character.update_char()
            elif key == blt.TK_S:
                for character in selection:
                    character.apparel.discard(redhat)
                    character.update_char()
            elif key == blt.TK_MOUSE_MOVE:
                if blt.state(blt.TK_MOUSE_X) <= screen_width and \
                        blt.state(blt.TK_MOUSE_Y) <= screen_height:
                    mouse_x = blt.state(blt.TK_MOUSE_X)
                    mouse_y = blt.state(blt.TK_MOUSE_Y)
                    if blt.check(blt.TK_MOUSE_RIGHT):
                        build_selection(selection_origin)
        render_all(current_floor, current_floor_objs, offset)
        blt.refresh()
    blt.close()

if __name__ == '__main__':
    main()
