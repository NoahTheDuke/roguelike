import PyBearLibTerminal as blt

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, x, y):
        if int(w_width) > self.x + x >= 0 and \
           int(w_height) > self.y + y >= 0:
            self.x += x
            self.y += y
            return True
        else:
            print("Can't move there.")
            return False

blt.open_()
w_width = "64"
w_height = "36"
cellsize = "12x12"
blt.set_("window: size={}x{}, cellsize={}, title='Omni: menu',"
              "resizeable=true;"
              "font: default".format(w_width, w_height, cellsize))
blt.clear()
blt.refresh()
blt.color("white")
p = Player(0, 0)

blt.print_(p.x, p.y, "@")

proceed = True
while proceed:
    blt.clear()
    key = 0
    while proceed and blt.has_input():
        key = blt.read()
        if key == blt.TK_CLOSE or key == blt.TK_ESCAPE:
            proceed = False
        elif key == blt.TK_UP:
            p.move(0, -1)
        elif key == blt.TK_DOWN:
            p.move(0, 1)
        elif key == blt.TK_LEFT:
            p.move(-1, 0)
        elif key == blt.TK_RIGHT:
            p.move(1, 0)
    blt.print_(p.x, p.y, "@")
    blt.refresh()

blt.close()
