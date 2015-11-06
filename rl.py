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
        if w_width > self.x + dx >= 0 and \
           w_height > self.y + dy >= 0 and \
           not dgn_layout[self.x + dx][self.y + dy].opacity:
            self.x += dx
            self.y += dy
            return True
        else:
            return False

class Tile:
    def __init__(self, blocked, opacity=False):
        if not opacity:
            opacity = blocked
        self.opacity = opacity

w_width = 64
w_height = 36
cellsize = "12x12"
redhat = "[+][color=red][offset=0,0]^"
dgn_layout = []

def main():
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Omni: menu';"
             "font: default".format(str(w_width), str(w_height), cellsize))
    blt.clear()
    blt.refresh()
    blt.color("white")
    p = Object(0, 0, "@",)

    def make_map():
        temp = [[Tile(False)
            for y in range(w_height)]
                for x in range(w_width)]
        for y in range(10):
            y += 10
            temp[10][y].opacity = True
        return temp
    global dgn_layout
    dgn_layout = make_map()

    def render_all():
        for y in range(w_height):
            for x in range(w_width):
                wall = dgn_layout[x][y].opacity
                if wall:
                    blt.print_(x, y, "[color=dark orange]#")
                else:
                    blt.layer(0)
                    blt.print_(x, y, "[color=light amber][offset=0, -3].")
                    blt.layer(1)
        blt.print_(p.x, p.y, p.char)

    blt.layer(1)
    render_all()
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
            elif key == blt.TK_B:
                print(blt.state(blt.TK_LAYER))
                p.char = p.init_char
        render_all()
        blt.refresh()

    blt.close()

if __name__ == '__main__':
    main()
