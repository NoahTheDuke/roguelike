import PyBearLibTerminal as blt
from Thing import Character, Tile

window_width = 96
window_height = 54
screen_width = 64
screen_height = 36

cellsize = "12x12"
redhat = "[+][color=red][offset=0,0]^"

def make_map():
    temp = [[Tile(x, y, '.', "amber", False)
        for y in range(window_height)]
            for x in range(window_width)]
    for y in range(6):
        y += 5
        temp[5][y].invisible = True
        temp[5][y].raw_char = "#"
        temp[5][y].color = "[color=dark orange]"
        temp[5][y].update_char()
    return temp

def render_all(map_, current_flooroor_objs, offset, screen_size):
    off_x, off_y = offset
    size_w, size_h = screen_size
    for col, column in enumerate(map_):
        if off_x <= col <= off_x+size_w:
            for row, tile in enumerate(column):
                if off_y <= row <= off_y+size_h:
                    tile.update_char()
                    blt.print_(tile.x+off_x, tile.y+off_y, tile.char)
    for obj in current_flooroor_objs:
        obj.update_char()
        blt.print_(obj.x, obj.y, obj.char)

def main():
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Omni: menu';"
             "font: default".format(str(window_width), str(window_height), cellsize))
    blt.clear()
    blt.refresh()
    blt.color("white")
    p = Character(15, 15, "@", "white")

    current_floor = make_map()
    current_floor_objs = []
    current_floor_objs.append(p)

    blt.layer(1)
    render_all(current_floor, current_floor_objs, (0, 0), (screen_width, screen_height))
    proceed = True
    while proceed:
        blt.clear()
        key = 0
        while proceed and blt.has_input():
            key = blt.read()
            if key == blt.TK_CLOSE or key == blt.TK_ESCAPE:
                proceed = False
            elif key == blt.TK_K:
                p.move(0, -1)
            elif key == blt.TK_J:
                p.move(0, 1)
            elif key == blt.TK_H:
                p.move(-1, 0)
            elif key == blt.TK_L:
                p.move(1, 0)
            elif key == blt.TK_Y:
                p.move(-1, -1)
            elif key == blt.TK_U:
                p.move(1, -1)
            elif key == blt.TK_B:
                p.move(-1, 1)
            elif key == blt.TK_N:
                p.move(1, 1)
            elif key == blt.TK_A:
                p.attributes.add(redhat)
            elif key == blt.TK_S:
                p.attributes.discard(redhat)
        render_all(current_floor, current_floor_objs, (0, 0), (screen_width, screen_height))
        blt.refresh()

    blt.close()

if __name__ == '__main__':
    main()
