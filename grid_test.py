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
    net_0 = [1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, ]

    net_1 = [1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, ]

    net_2 = [1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, ]

    net_3 = [1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, ]

    net_4 = [1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, ]

    net_5 = [1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, ]

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

        result = []
        below = []
        for node in self.all_nodes:
            right = [node[0] + 1, node[1]]
            down = [node[0], node[1] + 1]
            if right not in result:
                if 0 <= right[0] < 11 and 0 <= right[1] < 11:
                    result.append(right)
            if down not in below:
                if 0 <= down[0] < 11 and 0 <= down[1] < 11:
                    below.append(down)
        print(result, below)

        # result = [val for pair in zip(result, below) for val in pair]
        self.roads = [x for idx, x in enumerate(result)
                      if self.net_0[idx] is 1]
        print(result)

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
                blt.print_(x * 2, y * 2, 'O')
            elif [x, y] in g.roads:
                # if x != 0 and x != 10 and y != 0 and y != 10:
                    # blt.layer(1)
                # blt.print_(x * 2, y * 2, str(g.roads.index([x, y])))
                    # blt.layer(0)
                # else:
                blt.print_(x * 2, y * 2, '+')
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
