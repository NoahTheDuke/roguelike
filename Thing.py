class Thing:
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.raw_char = char
        self.color = "[color={}]".format(color)
        self.apparel = set()
        self.update_char()

    def update_char(self):
        elements = [self.color + self.raw_char] + [x for x in self.apparel]
        self.char = "".join(e for e in elements)

class Character(Thing):
    def __init__(self, x, y, name, char, color):
        super().__init__(x, y, char, color)
        self.name = name
        self.health = 20
        self.mana = 10
        self.attack = 2

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Tile(Thing):
    def __init__(self, x, y, char, color, physical, invisible=False):
        super().__init__(x, y, char, color)
        if not invisible:
            invisible = physical
        self.physical = physical
        self.invisible = invisible
