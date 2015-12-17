import PyBearLibTerminal as blt
import random

WINDOW_WIDTH = 80
WINDOW_HEIGHT = 45
CELLSIZE = "8x8"


class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Quadrant:
    _size = 325
    _street_width = 5

    def __init__(self):
        self.layout = [[Tile(x, y)
                       for y in range(self._size)]
                       for x in range(self._size)]

    def place_streets(self):
        num_streets = 4


def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, CELLSIZE
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Roguelike';"
             "font: default".format(
                 str(WINDOW_WIDTH), str(WINDOW_HEIGHT), CELLSIZE))
    blt.clear()
    blt.refresh()
    blt.color("white")
    seed = random.randint(0, 10)
    print(seed)
    # g = Quadrant()
    # print([(b.x, b.y) for a in g.layout for b in a])

    proceed = True
    while proceed:
        key = 0
        while blt.has_input():
            key = blt.read()
            if key == blt.TK_CLOSE or key == blt.TK_Q:
                proceed = False
    # if proceed is False, end the program
    blt.close()

if __name__ == '__main__':
    main()
