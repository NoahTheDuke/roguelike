from uuid import uuid4

class Thing:
    def __init__(self, x, y, z, char, color, physical, invisible=False):
        self.x = x
        self.y = y
        self.z = z
        self.raw_char = char
        self.color = "[color={}]".format(color)
        self.apparel = set()
        self.physical = physical
        self.invisible = invisible
        self.update_char()

    def update_char(self):
        elements = [self.color + self.raw_char] + [x for x in self.apparel]
        self.char = "".join(e for e in elements)

class Actor(Thing):
    def __init__(self, x, y, z, name, char, color, physical, invisible=False):
        super().__init__(x, y, z, char, color, physical, invisible)
        self.name = name
        self.health = 20
        self.mana = 10
        self.attack = 2
        self.uuid = uuid4()

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Tile(Thing):
    def __init__(self, x, y, z, char, color, physical, invisible=False):
        super().__init__(x, y, z, char, color, physical, invisible)
        if not invisible:
            invisible = physical
