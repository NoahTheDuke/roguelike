import PyBearLibTerminal as blt
from Thing import Actor, Tile

window_width = 80
window_height = 45
screen_width = 58
screen_height = 36
current_floor_obj_locs = []
selection = []

cellsize = "12x12"
redhat = "[+][color=red][offset=0,0]^"

def make_map():
    layout = [[Tile(x, y, 1, '', 'transparent', False)
        for y in range(window_height * 2)]
            for x in range(window_width * 2)]
    locations = [[None
        for y in range(window_height * 2)]
            for x in range(window_width * 2)]
    return layout, locations

def render_all(current_floor, current_floor_objs, offset):
    global selection
    render_viewport(current_floor, current_floor_objs, offset)
    render_sidebar(selection)
    render_message_bar()

def render_viewport(current_floor, current_floor_objs, offset):
    global screen_width, screen_height
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

def render_sidebar(selection):
    global screen_width, screen_height
    if selection:
        spacing = 4
        loc = screen_width + 1
        for idx, character in enumerate(selection):
            if character:
                c = character.color
                blt.print_(loc, 2 + spacing * idx, "Name:   [color={}]{}".format(c, character.name))
                blt.print_(loc, 3 + spacing * idx, "Health: [color=red]{}".format(character.health))
                blt.print_(loc, 4 + spacing * idx, "Mana:   [color=lighter blue]{}".format(character.mana))
            else:
                blt.print_(loc, 2, "Nothing selected.")

def render_message_bar():
    global screen_width, screen_height
    loc = screen_height
    blt.print_(2, loc + 1, "X: {}".format(blt.state(blt.TK_MOUSE_X)))
    blt.print_(2, loc + 2, "Y: {}".format(blt.state(blt.TK_MOUSE_Y)))
    return

def move_character(current_floor, direction):
    global window_width, window_height, screen_width, screen_height
    global selection
    for character in selection:
        print(character)
        dx, dy = character.x + direction[0], character.y + direction[1]
        x, y = direction
        if not current_floor[dx][dy].invisible and \
                screen_width >= dx >= 0 and screen_height >= dy >= 0:
            global current_floor_obj_locs
            current_floor_obj_locs[character.y][character.x] = None
            character.move(x, y)
            current_floor_obj_locs[character.y][character.x] = character.uuid
            return True
        else:
            return False

def look():
    return

def generate_characters():
    global current_floor_obj_locs
    pc = Actor(6, 6, 1, "Butts", "@", "white", True, False)
    pc2 = Actor(7, 7, 1, "Ass", "@", "green", True, False)
    current_floor_objs = {}
    current_floor_objs[pc.uuid] = pc
    current_floor_obj_locs[pc.y][pc.x] = pc.uuid
    current_floor_objs[pc2.uuid] = pc2
    current_floor_obj_locs[pc2.y][pc2.x] = pc2.uuid
    return current_floor_objs

def main():
    global window_width, window_height, screen_width, screen_height
    global cellsize, selection, current_floor_obj_locs
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
                x, y = blt.state(blt.TK_MOUSE_X), blt.state(blt.TK_MOUSE_Y)
                if current_floor_obj_locs[y][x]:
                    selection.append(current_floor_objs[current_floor_obj_locs[y][x]])
            elif key == blt.TK_A:
                for character in selection:
                    character.apparel.add(redhat)
                    character.update_char()
            elif key == blt.TK_S:
                for character in selection:
                    character.apparel.discard(redhat)
                    character.update_char()
            elif key == blt.TK_X:
                look()
        render_all(current_floor, current_floor_objs, offset)
        blt.refresh()

    blt.close()

if __name__ == '__main__':
    main()
