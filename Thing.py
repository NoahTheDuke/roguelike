from uuid import uuid4
from collections.abc import Sequence
from enum import Enum
from random import randint

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
        self.color = "[color={}]".format(self.raw_color)
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

    def __str__(self):
        return "x: {}, y: {}, raw_char: {}, char: {}, raw_color: {}, color: {}, physical: {}, occupied: {}, prop: {}, item: {}, uuid: {}".format(self.x, self.y, self.raw_char, self.char, self.raw_color, self.color, self.physical, self.occupied, self.prop, self.item, self.uuid)

    def update_char(self):
        self.color = "[color={}]".format(self.raw_color)
        elements = [self.color + self.raw_char]
        self.char = "".join(e for e in elements)

class Map(Sequence):
    def __init__(self, name, width, height,
                 min_rooms, max_rooms, num_exits, level, region):
        self.name = name
        self.width = width
        self.height = height
        self.min_rooms = min_rooms
        self.max_rooms = max_rooms
        self.num_exits = num_exits
        self.level = level
        self.layout = []
        self.rooms = []
        self.passages = []
        self.region = region
        self.generate_map(width, height, num_exits)

    def __getitem__(self, key):
        return self.layout[key]

    def __len__(self):
        return self.width * self.height

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
        self.generate_ground(width, height)
        self.carve_rooms()
        self.carve_passages()
        self.build_features()

    def generate_ground(self, width, height):
        self.layout = [[Tile(x, y, '#', 'black', True)
                            for y in range(height)]
                                for x in range(width)]

    def carve_rooms(self):
        cur_max = randint(self.min_rooms, self.max_rooms)
        while len(self.rooms) <= cur_max:
            w, h = randint(3, 10), randint(3, 10)
            print("w, h", w, h)
            x, y = randint(0, self.width - w), randint(0, self.height - h)
            new_room = RectRoom(x, y, w, h)
            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break
            if not failed:
                self.rooms.append(new_room)
                if len(self.rooms) is 1:
                    self.start_loc = new_room.center()
                print(str(len(self.rooms)), new_room.x1, new_room.y1, new_room.x2, new_room.y2)
                for x in range(new_room.x1, new_room.x2):
                    for y in range(new_room.y1, new_room.y2):
                        if ((x == new_room.x1) or
                           (x == new_room.x2 - 1) or
                           (y == new_room.y1) or
                           (y == new_room.y2 - 1)):
                            self.layout[x][y].raw_char = '#'
                            self.layout[x][y].raw_color = 'amber'
                            self.layout[x][y].update_char()
                            # print(self.layout[x][y])
                        else:
                            self.layout[x][y].raw_char = '.'
                            self.layout[x][y].raw_color = 'amber'
                            self.layout[x][y].physical = False
                            self.layout[x][y].update_char()
                            # print(self.layout[x][y])
                x, y = new_room.center()
                self.layout[x][y].raw_char = str(len(self.rooms))

    def carve_passages(self):
        pass

    def build_features(self):
        pass

    def register(self, actor):
        self.layout[actor.x][actor.y].occupied = actor
        return

    def move_actor(self, actor, dx, dy):
        self.layout[actor.x][actor.y].occupied = None
        self.layout[actor.x + dx][actor.y + dy].occupied = actor

class RectRoom:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        x = (self.x1 + self.x2) // 2
        y = (self.y1 + self.y2) // 2
        return (x, y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
