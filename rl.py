import PyBearLibTerminal as blt
from Thing import Actor, Tile

window_width = 80
window_height = 45
screen_width = 58
screen_height = 36

cellsize = "12x12"
redhat = "[+][color=red][offset=0,0]^"

def make_map():
    temp = [[Tile(x, y, 1, '.', 'amber', False)
        for y in range(window_height * 2)]
            for x in range(window_width * 2)]
    return temp

def render_all(current_floor, current_floor_objs, selection, offset):
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

def render_sidebar(character):
    global screen_width, screen_height
    loc = screen_width + 1
    if character:
        blt.print_(loc, 2, "Name:   {}".format(character.name))
        blt.print_(loc, 3, "Health: [color=red]{}".format(character.health))
        blt.print_(loc, 4, "Mana:   [color=lighter blue]{}".format(character.mana))
    else:
        blt.print_(loc, 2, "Nothing selected.")

def render_message_bar():
    global screen_width, screen_height
    return

def move_character(current_floor, character, direction):
    global window_width, window_height, screen_width, screen_height
    dx, dy = character.x + direction[0], character.y + direction[1]
    x, y = direction
    if not current_floor[dx][dy].invisible and \
            screen_width >= dx >= 0 and screen_height >= dy >= 0:
        character.move(x, y)
        return True
    else:
        return False

def look():
    return

def generate_characters():
    return

def main():
    global window_width, window_height, screen_width, screen_height, cellsize
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Roguelike';"
             "font: default".format(str(window_width), str(window_height), cellsize))
    blt.clear()
    blt.refresh()
    blt.color("white")

    pc = Actor(6, 6, 1, "Butts", "@", "white", True, False)
    offset = (0, 0)

    current_floor = make_map()
    current_floor_objs = {}
    current_floor_objs[pc.uuid] = pc

    render_all(current_floor, current_floor_objs, None, offset)
    proceed = True
    while proceed:
        blt.clear()
        key = 0
        while blt.has_input():
            key = blt.read()
            if key == blt.TK_CLOSE or key == blt.TK_Q:
                proceed = False
            elif key == blt.TK_K:
                move_character(current_floor, pc, (0, -1))
            elif key == blt.TK_J:
                move_character(current_floor, pc, (0, 1))
            elif key == blt.TK_H:
                move_character(current_floor, pc, (-1, 0))
            elif key == blt.TK_L:
                move_character(current_floor, pc, (1, 0))
            elif key == blt.TK_Y:
                move_character(current_floor, pc, (-1, -1))
            elif key == blt.TK_U:
                move_character(current_floor, pc, (1, -1))
            elif key == blt.TK_B:
                move_character(current_floor, pc, (-1, 1))
            elif key == blt.TK_N:
                move_character(current_floor, pc, (1, 1))
            elif key == blt.TK_A:
                pc.apparel.add(redhat)
                pc.update_char()
            elif key == blt.TK_S:
                pc.apparel.discard(redhat)
                pc.update_char()
            elif key == blt.TK_X:
                look()
        render_all(current_floor, current_floor_objs, None, offset)
        blt.refresh()

    blt.close()

if __name__ == '__main__':
    main()
