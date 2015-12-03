from uuid import uuid4
from collections.abc import Sequence
from enum import Enum

class AutoEnum(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class Game_States(AutoEnum):
    MAIN_MENU = ()
    NEW_GAME = ()
    IN_GAME = ()
    OPTIONS = ()
    HISTORY = ()


class Actor:
    def __init__(self, world, name, x, y, char, color, physical,
                 visible=True, max_health=None, cur_health=None,
                 max_mana=None, cur_mana=None, attack=None, defense=None,
                 apparel=None):
        # Engine Stats
        self.name = name
        self.x = x
        self.y = y
        self.raw_char = char
        self.raw_color = color
        self.color = "[color={}]".format(color)
        self.physical = physical
        self.visible = visible
        self.inventory = []
        self.uuid = uuid4()
        # Generic Stats
        self.max_health = max_health
        self.cur_health = cur_health or max_health
        self.max_mana = max_mana
        self.cur_mana = cur_mana or max_mana
        self.attack = attack
        self.defense = defense
        self.apparel = set()
        # Finalization Methods
        self.update_char()
        world.register(self)

    def __eq__(self, other):
        return ((self.raw_char, self.raw_color,
                 self.physical, self.visible) ==
                (other.raw_char, other.raw_color,
                 other.physical, other.visible))

    def update_char(self):
        elements = [self.color + self.raw_char] + [x for x in self.apparel]
        self.char = "".join(e for e in elements)

    def move(self, world, dx, dy):
        world.move_actor(self, dx, dy)
        self.x += dx
        self.y += dy
        return self.x, self.y


class Item:
    def __init__(self, name, x, y, char, color, physical):
        self.x = x
        self.y = y
        self.raw_char = char
        self.raw_color = color
        self.color = "[color={}]".format(color)
        self.physical = physical
        self.uuid = uuid4()

    def __eq__(self, other):
        return ((self.raw_char, self.raw_color, self.physical) ==
                (other.raw_char, other.raw_color, other.physical))


class Prop:
    def __init__(self, name, x, y, char, color, physical):
        self.x = x
        self.y = y
        self.raw_char = char
        self.raw_color = color
        self.color = "[color={}]".format(color)
        self.physical = physical
        self.uuid = uuid4()

    def __eq__(self, other):
        return ((self.raw_char, self.raw_color, self.physical) ==
                (other.raw_char, other.raw_color, other.physical))


class Tile:
    def __init__(self, x, y, char, color, physical):
        self.x = x
        self.y = y
        self.raw_char = char
        self.raw_color = color
        self.color = "[color={}]".format(color)
        self.physical = physical
        self.occupied = None
        self.prop = None
        self.item = None
        self.uuid = uuid4()

    def __eq__(self, other):
        return ((self.raw_char, self.raw_color, self.physical) ==
                (other.raw_char, other.raw_color, other.physical))

    def update_char(self):
        elements = [self.color + self.raw_char]
        self.char = "".join(e for e in elements)


class Map(Sequence):
    def __init__(self, width, height, num_exits=0, level=0, region=None):
        self.width = width
        self.height = height
        self.num_exits = num_exits
        self.level = level
        self.layout = []
        self.region = region
        self.generate_map(width, height, num_exits)

    def __getitem__(self, key):
        return self.layout[key]

    def __len__(self):
        return len([y for x in self.layout for y in x])

    def __contains__(self, item):
        for tiles in self.layout:
            for tile in tiles:
                if isinstance(item, Tile):
                    if item == tile:
                        return True
                elif isinstance(item, Actor):
                    if item == tile.occupied:
                        return True
                elif isinstance(item, Item):
                    if item == tile.item:
                        return True
                elif isinstance(item, Prop):
                    if item == tile.prop:
                        return True
        return False

    def generate_map(self, width, height, num_exits):
        self.layout = [[Tile(x, y, '.', 'amber', False)
            for y in range(height)]
                for x in range(width)]

    def register(self, actor):
        self.layout[actor.x][actor.y].occupied = actor
        return

    def move_actor(self, actor, dx, dy):
        self.layout[actor.x][actor.y].occupied = None
        self.layout[actor.x + dx][actor.y + dy].occupied = actor
