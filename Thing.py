from uuid import uuid4
from collections.abc import Sequence
from enum import Enum
from random import randint, randrange

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
    def __init__(self, world, name, x, y, glyph, color, physical,
                 visible=True, max_health=None, cur_health=None,
                 max_mana=None, cur_mana=None, attack=None, defense=None,
                 apparel=None):
        # Engine Stats
        self.name = name
        self.x = x
        self.y = y
        self.glyph = glyph
        self.color = color
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
        self.build_char()
        world.register(self)

    def __eq__(self, other):
        return ((self.glyph, self.color,
                 self.physical, self.visible) ==
                (other.glyph, other.color,
                 other.physical, other.visible))

    def build_char(self):
        apparel = "[+]" + [x for x in self.apparel] if self.apparel else ""
        elements = "[color={}]".format(self.color) + self.glyph + apparel
        self.char = "".join(e for e in elements)

    def move(self, world, tx, ty):
        tick, moved = world.move_actor(self, tx, ty)
        if moved:
            self.x += tx
            self.y += ty
        return tick

    def place(self, start_loc):
        self.x, self.y = start_loc

    def adjacent(self, world):
        adjacent = []
        for x in range(self.x - 1, self.x + 2):
            for y in range(self.y - 1, self.y + 2):
                if x == self.x and y == self.y:
                    continue
                else:
                    adjacent.append((x, y))
        return adjacent

class Item:
    def __init__(self, name, x, y, glyph, color, physical):
        self.x = x
        self.y = y
        self.glyph = glyph
        self.color = color
        self.physical = physical
        self.uuid = uuid4()

    def __eq__(self, other):
        return ((self.glyph, self.color, self.physical) ==
                (other.glyph, other.color, other.physical))

    def build_char(self):
        elements = ["[color={}]".format(self.color) + self.glyph]
        self.char = "".join(e for e in elements)

class Prop:
    def __init__(self, x, y, glyph, color, physical):
        self.x = x
        self.y = y
        self.glyph = glyph
        self.color = color
        self.physical = physical
        self.is_door = False
        self.door_status = False
        self.uuid = uuid4()

    def __eq__(self, other):
        return ((self.glyph, self.color, self.physical) ==
                (other.glyph, other.color, other.physical))

    def build_char(self):
        elements = ["[color={}]".format(self.color) + self.glyph]
        self.char = "".join(e for e in elements)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Tile:
    def __init__(self, x, y, glyph, color, bgcolor, physical):
        self.x = x
        self.y = y
        self.glyph = glyph
        self.color = color
        self.bgcolor = bgcolor
        self.physical = physical
        self.occupied = None
        self.prop = None
        self.item = None
        self.uuid = uuid4()

    def __eq__(self, other):
        return ((self.glyph, self.color, self.physical, self.door[0]) ==
                (other.glyph, other.color, other.physical, other.door[0]))

    def __str__(self):
        return "x: {}, y: {}, glyph: {}, char: {}, color: {}, physical: {}, occupied: {}, prop: {}, item: {}, uuid: {}".format(self.x, self.y, self.glyph, self.char, self.color, self.physical, self.occupied, self.prop, self.item, self.uuid)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def build_door(self):
        self.update(glyph='.', physical=False)
        self.prop = Prop(x=self.x, y=self.y, glyph='+', color='white', physical=True)
        self.prop.update(is_door=True, door_status=True)

    def check_door(self):
        if self.prop and self.prop.is_door:
            return True

    def toggle_door(self):
        self.prop.door_status = not self.prop.door_status
        self.prop.glyph = ["-", "+"][self.prop.door_status]
        self.prop.physical = not self.prop.physical

    def build_char(self):
        if self.occupied:
            self.occupied.build_char()
        elif self.prop:
            self.prop.build_char()
        elif self.item:
            self.item.build_char()
        color = "[color={}]".format(self.color)
        bgcolor = "[bgcolor={}]".format(self.bgcolor)
        elements = [color, bgcolor, self.glyph]
        self.char = "".join(e for e in elements)

class Map(Sequence):
    def __init__(self, name, width, height,
                 min_rooms, max_rightooms, num_exits, level, region):
        self.name = name
        self.width = width
        self.height = height
        self.min_rooms = min_rooms
        self.max_rightooms = max_rightooms
        self.num_exits = num_exits
        self.level = level
        self.layout = []
        self.rooms = []
        self.passages = []
        self.region = region
        self.start_loc = None
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

    def register(self, actor):
        self[actor.x][actor.y].occupied = actor

    def move_actor(self, actor, tx, ty):
        dx, dy = actor.x + tx, actor.y + ty
        if not (dx >= self.width) or (dy >= self.height):
            if not self[dx][dy].physical:
                if self[dx][dy].check_door() and self[dx][dy].prop.door_status:
                    self[dx][dy].toggle_door()
                    return (True, False)
                elif not self[dx][dy].occupied:
                    self[actor.x][actor.y].occupied = None
                    self[dx][dy].occupied = actor
                    return (True, True)
        return (False, False)

    def generate_map(self, width, height, num_exits):
        self.clear_map()
        self.generate_ground(width, height)
        self.carve_rooms()
        self.carve_passages()
        self.build_features()

    def clear_map(self):
        self.layout.clear()
        self.rooms.clear()
        self.passages.clear()
        self.start_loc = None

    def generate_ground(self, width, height):
        self.layout = [[Tile(x=x, y=y, glyph='.', color='black',
                        bgcolor='red', physical=False)
                            for y in range(height)]
                                for x in range(width)]

    def carve_rooms(self):
        cur_max = randint(self.min_rooms, self.max_rightooms)
        while len(self.rooms) <= cur_max:
            w, h = randint(4, 10), randint(4, 10)
            x, y = randint(0, self.width - w), randint(0, self.height - h)
            new_room = RectRoom(x, y, w, h)
            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break
            if (new_room.x_right >= self.width) or (new_room.y_bottom >= self.height):
                failed = True
            if not failed:
                self.rooms.append(new_room)
                if not self.start_loc:
                    self.start_loc = new_room.center()
                for x in range(new_room.x_left, new_room.x_right + 1):
                    for y in range(new_room.y_top, new_room.y_bottom + 1):
                        if ((x == new_room.x_left) or
                           (x == new_room.x_right) or
                           (y == new_room.y_top) or
                           (y == new_room.y_bottom)):
                            self[x][y].update(glyph='#', color='grey', physical=True)
                        else:
                            self[x][y].update(glyph='.', color='amber')
                x, y = new_room.x_right, new_room.y_bottom
                self[x][y].glyph = str(chr(64 + len(self.rooms)))

    def carve_passages(self):
        pass

    def build_features(self):
        for room in self.rooms:
            side = randint(0, 3)
            if side is 0:
                x, y = (randrange(room.x_left + 1, room.x_right), room.y_top)
            elif side is 1:
                x, y = (room.x_left, randrange(room.y_top + 1, room.y_bottom))
            elif side is 2:
                x, y = (randrange(room.x_left + 1, room.x_right), room.y_bottom)
            elif side is 3:
                x, y = (room.x_right, randrange(room.y_top + 1, room.y_bottom))
            self[x][y].build_door()

class RectRoom:
    def __init__(self, x, y, w, h):
        self.x_left = x
        self.y_top = y
        self.x_right = x + w
        self.y_bottom = y + h

    def center(self):
        x = (self.x_left + self.x_right) // 2
        y = (self.y_top + self.y_bottom) // 2
        return (x, y)

    def intersect(self, other):
        return (self.x_left <= other.x_right and self.x_right >= other.x_left and
                self.y_top <= other.y_bottom and self.y_bottom >= other.y_top)

class RightAnglePassage:
    def __init__(self, start_loc, end_loc, width):
        self.x1, self.y1 = start_loc
        self.x2, self.y2 = end_loc
        self.width = width

    def length(self):
        return (abs(self.x2 - self.x1) + abs(self.y2 - self.y1))
