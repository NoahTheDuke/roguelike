import PyBearLibTerminal as blt

WINDOW_WIDTH = 80
WINDOW_HEIGHT = 45
CELLSIZE = "8x8"


class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Quadrant:
    size = 325
    small_size = 25
    street_width = 5

    def __init__(self):
        self.layout = [[Tile(x, y)
                       for y in range(self.small_size)]
                       for x in range(self.small_size)]

        self.make_roads()
        self.make_blocks()

    def make_roads(self):
        self.all_nodes = [[x * 2, y * 2]
                          for y in range(6)
                          for x in range(6)]

        dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        result = []
        for node in self.all_nodes:
            for dr in dirs:
                neighbor = [node[0] + dr[0], node[1] + dr[1]]
                if 0 <= neighbor[0] < 11 and 0 <= neighbor[1] < 11:
                    if neighbor not in result:
                        result.append(neighbor)
        print(result)
        for (x, y) in result:
            d, m = divmod(x, 5)
            if m > 0 and m != 4:
                print(m)
        self.roads = result

    def make_blocks(self):
        self.blocks = [[x, y]
                       for x in range(0, self.small_size, 5)
                       for y in range(0, self.small_size, 5)]
        self.make_lots()

    def make_lots(self):
        self.make_houses()

    def make_houses(self):
        pass


def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, CELLSIZE
    blt.open_()
    blt.set_("window: size={}x{}, cellsize={}, title='Grid Test';"
             "font: default".format(
                 str(WINDOW_WIDTH), str(WINDOW_HEIGHT), CELLSIZE))
    blt.clear()
    blt.refresh()
    blt.color("white")
    g = Quadrant()
    blt.clear()
    for x in range(30):
        for y in range(30):
            if [x, y] in g.all_nodes:
                blt.print_(x * 2, y * 2, ' ')
            elif [x, y] in g.roads:
                xd, xm = divmod(x, 5)
                yd, ym = divmod(y, 5)
                print(xd, xm)
                print(yd, ym)
                blt.print_(x * 2, y * 2, str(g.roads.index([x, y])))
    blt.refresh()

    proceed = True
    while proceed:
        key = 0
        while blt.has_input():
            key = blt.read()
            if key == blt.TK_CLOSE or key == blt.TK_Q:
                proceed = False
    blt.close()

if __name__ == '__main__':
    main()
