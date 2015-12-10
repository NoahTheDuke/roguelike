from uuid import uuid4
from collections.abc import Sequence
from enum import Enum
from random import randint, randrange
from math import atan2, sqrt, cos, sin

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

class Thing:
    def __init__(self, x, y, glyph, color, physical, visible=True):
        self.x = x
        self.y = y
        self.glyph = glyph
        if len(color.split()) > 1:
            self.color_modifier, self.color = color.split()
        else:
            self.color = color
            self.color_modifier = ""
        self.physical = physical
        self.visible = visible

    def __eq__(self, other):
        return ((self.glyph, self.color,
                 self.physical, self.visible) ==
                (other.glyph, other.color,
                 other.physical, other.visible))

    def build_char(self, within_fov):
        if within_fov:
            color = " ".join((self.color_modifier, self.color))
        else:
            color = "darker " + self.color
        elements = ["[color={}]".format(color), self.glyph]
        self.char = "".join(e for e in elements)

class Actor(Thing):
    def __init__(self, world, name, x, y, glyph, color, physical,
                 visible=True, max_health=None, cur_health=None,
                 max_mana=None, cur_mana=None, attack=None, defense=None,
                 apparel=None):
        # Engine Stats
        Thing.__init__(self, x, y, glyph, color, physical)
        self.name = name
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
        world.register(self)

    def build_char(self, within_fov):
        super().build_char(within_fov)
        apparel = "[+]" + [x for x in self.apparel] if self.apparel else ""
        self.char = "".join((self.char, apparel))

    def move(self, world, tx, ty):
        tick, moved = world.move_actor(self, tx, ty)
        if moved:
            self.x += tx
            self.y += ty
            world.calculate_fov(self)
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

class Item(Thing):
    def __init__(self, name, x, y, glyph, color, physical):
        Thing.__init__(self, x, y, glyph, color, physical)
        self.name = name
        self.uuid = uuid4()

class Prop(Thing):
    def __init__(self, x, y, glyph, color, physical):
        Thing.__init__(self, x, y, glyph, color, physical)
        self.is_door = False
        self.door_status = False
        self.uuid = uuid4()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Tile(Thing):
    def __init__(self, x, y, glyph, color, bkcolor, physical):
        Thing.__init__(self, x, y, glyph, color, physical)
        self.bkcolor = bkcolor
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

    def build_char(self, within_fov=False):
        if self.occupied:
            self.occupied.build_char(within_fov)
        elif self.item:
            self.item.build_char(within_fov)
        elif self.prop:
            self.prop.build_char(within_fov)
        else:
            super().build_char(within_fov)
            if within_fov:
                color = " ".join((self.color_modifier, self.color))
            else:
                color = "darker " + self.color
            color = "[color={}]".format(color)
            bkcolor = "[bkcolor={}]".format(self.bkcolor)
            elements = [color, bkcolor, self.glyph]
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
        self.fov_map = set()
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
        self.calculate_fov(actor)

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

    def calculate_fov(self, actor):
        """
        Shamelessly stolen from http://ncase.me/sight-and-light/
        """
        unique_points = []
        for room in self.rooms:
            for corner in room.corners:
                if corner not in unique_points:
                    unique_points.append(corner)

        unique_angles = []
        for point in unique_points:
            angle = atan2(point[1] - actor.y, point[0] - actor.x)
            # angle2 = atan2(point[1] - actor.y, point[0] - actor.x)
            # angle3 = atan2(point[1] - actor.y, point[0] - actor.x)
            # unique_angles.extend([angle1, angle2, angle3])
            unique_angles.append(angle)
        print('UNIQUE ANGLE', unique_angles)

        intersects = []
        for angle in unique_angles:
            # Calculate dx & dy from angle
            dx = cos(angle)
            dy = sin(angle)
            print(dx, dy)
            # Ray from actor
            ray = {'actor': {'x': actor.x, 'y': actor.y},
                   'direction': {'x': actor.x + dx, 'y': actor.y + dy}}
            # Find CLOSEST intersection
            closest_intersect = None
            for room in self.rooms:
                intersect = self.get_intersection(ray, room)
                if not intersect:
                    continue
                if not closest_intersect or intersect['param'] < closest_intersect['param']:
                    closest_intersect = intersect
            # // Add to list of intersects
            intersects.append(closest_intersect)

    def get_intersection(self, ray, room):
        # // Find intersection of RAY & SEGMENT
        # // RAY in parametric: Point + Delta*T1
        top = (room.corners[0], room.corners[1])
        right = (room.corners[1], room.corners[2])
        bottom = (room.corners[2], room.corners[3])
        left = (room.corners[3], room.corners[0])
        walls = (top, right, bottom, left)

        r_px = ray['actor']['x']
        r_py = ray['actor']['y']
        r_dx = ray['direction']['x'] - ray['actor']['x']
        r_dy = ray['direction']['y'] - ray['actor']['y']

        for wall in walls:
            print('wall', wall)
            print('rdx rdy', r_dx, r_dy)
        # // SEGMENT in parametric: Point + Delta*T2
            s_px = wall[0][0]
            s_py = wall[0][1]
            s_dx = wall[1][0] - wall[0][0]
            s_dy = wall[1][1] - wall[0][1]
        # // Are they parallel? If so, no intersect
            r_mag = sqrt(r_dx * r_dx + r_dy * r_dy)
            s_mag = sqrt(s_dx * s_dx + s_dy * s_dy)
            print('sdx, sdy', s_dx, s_dy)
            print('rmg smg', r_mag, s_mag)
            print('rdx / rmg', r_dx / r_mag)
            print('sdx / smg', s_dx / s_mag)
            print('rdy / rmg', r_dy / r_mag)
            print('sdy / smg', s_dy / s_mag)
            if (abs(r_dx / r_mag) == abs(s_dx / s_mag)) and ((r_dy / r_mag) == (s_dy / s_mag)):
                # // Unit vectors are the same.
                return None
            # // SOLVE FOR T1 & T2
            # // r_px+r_dx*T1 = s_px+s_dx*T2 && r_py+r_dy*T1 = s_py+s_dy*T2
            # // ==> T1 = (s_px+s_dx*T2-r_px)/r_dx = (s_py+s_dy*T2-r_py)/r_dy
            # // ==> s_px*r_dy + s_dx*T2*r_dy - r_px*r_dy = s_py*r_dx + s_dy*T2*r_dx - r_py*r_dx
            # // ==> T2 = (r_dx*(s_py-r_py) + r_dy*(r_px-s_px))/(s_dx*r_dy - s_dy*r_dx)
            T2 = (r_dx * (s_py - r_py) + r_dy * (r_px - s_px)) / (s_dx * r_dy - s_dy * r_dx);
            T1 = (s_px + s_dx * T2 - r_px) / r_dx
            # // Must be within parametic whatevers for RAY/SEGMENT
            if T1 < 0:
                return None
            if (T2 < 0) or (T2 > 1):
                return None
            # // Return the POINT OF INTERSECTION
            return { 'x': r_px + r_dx * T1,
                     'y': r_py + r_dy * T1,
                     'param': T1}

    def generate_map(self, width, height, num_exits):
        self.clear_map()
        self.generate_ground()
        self.carve_rooms()
        self.carve_passages()
        self.build_features()

    def clear_map(self):
        self.layout.clear()
        self.rooms.clear()
        self.passages.clear()
        self.start_loc = None

    def generate_ground(self):
        self.layout = [[Tile(x=x, y=y, glyph='.', color='light green',
                        bkcolor='black', physical=False)
                            for y in range(self.height)]
                                for x in range(self.width)]
        self.fov = [[False for y in range(self.height)] for x in range(self.width)]

    def carve_rooms(self):
        cur_max = randint(self.min_rooms, self.max_rooms)
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
        self.rooms.append(RectRoom(0, 0, self.width - 1, self.height - 1))

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
        self.corners()

    def corners(self):
        top_left = (self.x_left, self.y_top)
        top_right = (self.x_right, self.y_top)
        bottom_left = (self.x_left, self.y_bottom)
        bottom_right = (self.x_right, self.y_bottom)
        self.corners = (top_left, top_right, bottom_right, bottom_left)

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
