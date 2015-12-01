from uuid import uuid4

class Actor:
    def __init__(self, name, x, y, z, char, color, physical):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.raw_char = char
        self.raw_color = color
        self.color = "[color={}]".format(color)
        self.physical = physical
        self.invisible = False
        self.health = 0
        self.mana = 0
        self.attack = 0
        self.uuid = uuid4()
        self.apparel = set()
        self.update_char()

    def update_char(self):
        elements = [self.color + self.raw_char] + [x for x in self.apparel]
        self.char = "".join(e for e in elements)

    def move(self, world, dx, dy):
        world.move_actor(self, dx, dy)
        self.x += dx
        self.y += dy
        return self.x, self.y


class Tile:
    def __init__(self, x, y, z, char, color, physical):
        self.x = x
        self.y = y
        self.z = z
        self.raw_char = char
        self.raw_color = color
        self.color = "[color={}]".format(color)
        self.physical = physical
        self.item = None
        self.occupied = None

    def update_char(self):
        elements = [self.color + self.raw_char]
        self.char = "".join(e for e in elements)


class Map:
    def __init__(self, width, height, num_exits=0, level=0, region=None):
        self.width = width
        self.height = height
        self.num_exits = num_exits
        self.level = level
        self.region = region
        self.generate_map(width, height, num_exits)

    def generate_map(self, width, height, num_exits):
        self.layout = [[Tile(x, y, 1, '.', 'amber', False)
            for y in range(height)]
                for x in range(width)]

    def register(self, actor):
        self.layout[actor.x][actor.y].occupied = actor
        return

    def move_actor(self, actor, dx, dy):
        self.layout[actor.x][actor.y].occupied = None
        self.layout[actor.x + dx][actor.y + dy].occupied = actor
