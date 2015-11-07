import PyBearLibTerminal as blt

class Object:
    def __init__(self, x, y, char, color=None):
        self.x = x
        self.y = y
        self.char = char
        self.init_char = char
        self.color = color
        if color:
            self.char = "[color={}]{}".format(color, char)

    def move(self, dx, dy):
        if window_width > self.x + dx >= 0 and \
           window_height > self.y + dy >= 0 and \
           not dgn_layout[self.x + dx][self.y + dy].opacity:
            self.x += dx
            self.y += dy
            return True
        else:
            return False

class Tile:
    def __init__(self, x, y, char, blocked, opacity=False):
        self.x = x
        self.y = y
        self.char = char
        if not opacity:
            opacity = blocked
        self.opacity = opacity

window_width = 96
window_height = 54
screen_width = 64
screen_height = 36

cellsize = "12x12"
redhat = "[+][color=red][offset=0,0]^"
dgn_layout = []

def main():
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Omni: menu';"
             "font: default".format(str(window_width), str(window_height), cellsize))
    blt.clear()
    blt.refresh()
    blt.color("white")
    p = Object(15, 15, "@",)

    def make_map():
        temp = [[Tile(x, y, '[color=amber].', False)
            for y in range(window_height)]
                for x in range(window_width)]
        for y in range(6):
            y += 5
            temp[5][y].opacity = True
            temp[5][y].char = "[color=dark orange]#"
        return temp

    global dgn_layout
    dgn_layout = make_map()

    def render_all(map_, offset, screen_size):
        off_x, off_y = offset
        size_w, size_h = screen_size
        for col, column in enumerate(map_):
            if off_x <= col <= off_x+size_w:
                for row, tile in enumerate(column):
                    if off_y <= row <= off_y+size_h:
                        blt.print_(tile.x+off_x, tile.y+off_y, tile.char)
        blt.print_(p.x, p.y, p.char)

    blt.layer(1)
    render_all(dgn_layout, (0, 0), (screen_width, screen_height))
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
                p.char += redhat
            elif key == blt.TK_S:
                p.char = p.init_char
        render_all(dgn_layout, (0, 0), (screen_width, screen_height))
        blt.refresh()

    blt.close()

if __name__ == '__main__':
    main()
