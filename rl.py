import PyBearLibTerminal as blt
from Thing import Character, Tile

window_width = 64
window_height = 36
screen_width = 40
screen_height = 27

cellsize = "16x16"
redhat = "[+][color=red][offset=0,0]^"

def make_map():
    temp = [[Tile(x, y, '.', "amber", False)
        for y in range(window_height)]
            for x in range(window_width)]
    return temp

def render_all(character, current_floor, current_floor_objs, offset):
    render_main_window(current_floor, current_floor_objs, offset)
    display_character_info(character)

def render_main_window(current_floor, current_floor_objs, offset):
    global screen_width, screen_height
    off_x, off_y = offset
    size_w, size_h = screen_width, screen_height
    for col, column in enumerate(current_floor):
        if off_x <= col <= off_x+size_w:
            for row, tile in enumerate(column):
                if off_y <= row <= off_y+size_h:
                    tile.update_char()
                    blt.print_(tile.x+off_x, tile.y+off_y, tile.char)
    for obj in current_floor_objs["Player"]:
        if obj.invisible is not True:
            blt.print_(obj.x, obj.y, obj.char)

def display_character_info(character):
    global screen_width, screen_height
    loc = screen_width+1
    blt.print_(loc, 2, "Name:   {}".format(character.name))
    blt.print_(loc, 3, "Health: [color=red]{}".format(character.health))
    blt.print_(loc, 4, "Mana:   [color=light blue]{}".format(character.mana))

def move_character(current_floor, character, direction):
    global window_width, window_height, screen_width, screen_height
    dx, dy = character.x+direction[0], character.y+direction[1]
    x, y = direction
    if not current_floor[dx][dy].invisible and \
            screen_width >= dx >= 0 and screen_height >= dy >= 0:
        character.move(x, y)
        return True
    else:
        return False

def look():
    return

def main():
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Omni: menu';"
             "font: default".format(str(window_width), str(window_height), cellsize))
    blt.clear()
    blt.refresh()
    blt.color("white")
    pc = Character(6, 6, "Butts", "@", "white", True, False)
    look_char = Character(6, 6, "Look", "X", "purple", True, True)

    current_floor = make_map()
    current_floor_objs = {}
    current_floor_objs["Player"] = []
    current_floor_objs["Player"].append(pc)
    current_floor_objs["Player"].append(look_char)

    render_all(pc, current_floor, current_floor_objs, (0, 0))
    proceed = True
    while proceed:
        blt.clear()
        key = 0
        while blt.has_input():
            key = blt.read()
            if key == blt.TK_CLOSE or key == blt.TK_ESCAPE:
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
        render_all(pc, current_floor, current_floor_objs, (0, 0))
        blt.refresh()

    blt.close()

if __name__ == '__main__':
    main()
