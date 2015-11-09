class Thing:
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.raw_char = char
        self.color = "[color={}]".format(color)
        self.attributes = set()
        self.update_char()

    def update_char(self):
        ups = [self.color + self.raw_char] + [x for x in self.attributes]
        self.char = "".join(x for x in ups)

class Character(Thing):

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Tile(Thing):
    def __init__(self, x, y, char, color, physical, invisible=False):
        super().__init__(x, y, char, color)
        if not invisible:
            invisible = physical
        self.invisible = invisible

