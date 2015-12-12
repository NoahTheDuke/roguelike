from uuid import uuid4
from collections.abc import Sequence
from enum import Enum
from random import randint, randrange
from math import atan2, sqrt, pi
from collections import deque

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
        if tick:
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

    def build_char(self, fov_map, fov_toggle):
        if fov_toggle:
            if (self.x, self.y) in fov_map:
                within_fov = True
            else:
                within_fov = False
        else:
            within_fov = False
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
        if tx == 0 and ty == 0:
            return (True, False)
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

    def line(self, x0, y0, x1, y1):
        """Bresenham's line algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        plot = []
        if dx > dy:
            err = dx / 2.0
            while x != x1:
            # while 0 <= x < self.width:
                plot.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            # while 0 <= y < self.height:
            while y != y1:
                plot.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        plot.append((x, y))
        return plot

    def calculate_fov(self, actor):
        """
        Shamelessly adapted from http://ncase.me/sight-and-light/
        """
        corners = []
        wall_points = []
        for room in self.rooms:
            wall_points.extend(room.wall_points)
            for corner in room.corners:
                if corner not in corners:
                    corners.append(corner)

        lines = []
        for corner in corners:
            lines.append(self.line(actor.x, actor.y, corner[0], corner[1]))
            # if more x than y, it's to the left and right
            # add one above and below
            if abs(corner[0] - actor.x) > abs(corner[1] - actor.y):
                lines.append(self.line(actor.x, actor.y, corner[0], corner[1] - 1))
                lines.append(self.line(actor.x, actor.y, corner[0], corner[1] + 1))
            # otherwise, it's more y than x, so add one left and right
            else:
                lines.append(self.line(actor.x, actor.y, corner[0] - 1, corner[1]))
                lines.append(self.line(actor.x, actor.y, corner[0] + 1, corner[1]))

        intersections = []
        for line in lines:
            closest_intersect = None
            for step in line:
                intersect = []
                if step in wall_points:
                    if not self[step[0]][step[1]].check_door():
                        distance = sqrt((step[0] - actor.x) ** 2 + (step[1] - actor.y) ** 2)
                        intersect.append((distance, step))
                    else:
                        if self[step[0]][step[1]].prop.door_status:
                            distance = sqrt((step[0] - actor.x) ** 2 + (step[1] - actor.y) ** 2)
                            intersect.append((distance, step))
                if not intersect:
                    continue
                if not closest_intersect:
                    closest_intersect = min(intersect)
                elif min(intersect)[0] < closest_intersect[0]:
                    closest_intersect = min(intersect)
            if closest_intersect:
                intersections.append(closest_intersect[1])
        polygon = []
        for intersect in intersections:
            if intersect not in polygon:
                polygon.append(intersect)

        def algo(point):
            nonlocal actor
            return (atan2(point[1] - actor.y, point[0] - actor.x) + 2 * pi) % (2 * pi)

        print('presort', polygon)
        polygon.sort(key=algo)
        print('postsort', polygon)
        poly_walls = []
        for i in range(len(polygon) + 1):
            if i == 0:
                continue
            elif i == len(polygon):
                v1 = polygon[-1]
                v2 = polygon[0]
            else:
                v1 = polygon[i - 1]
                v2 = polygon[i]
            print('v1 v2', v1, v2)
            line = self.line(v1[0], v1[1], v2[0], v2[1])
            print('line', line)
            poly_walls.extend(line)
        poly_walls = list(set(poly_walls))
        print(poly_walls)

        # bb = (min(polygon)[0], min(polygon, key=lambda x: x[1])[1],
        # max(polygon)[0], max(polygon, key=lambda x: x[1])[1])
        # for y in range(bb[1], bb[3] + 1):
            # for x in range(bb[0], bb[2] + 1):
                # if self.point_in_poly(x, y, polygon):
                    # fov.append((x, y))
        fov = self.iter_flood_fill(actor.x, actor.y, poly_walls)
        self.fov_map = fov

    def iter_flood_fill(self, x, y, bounds):
        fov = []
        q = deque()
        q.append((x, y))
        # print(q)
        while q:
            x, y = q.popleft()
            # print(x, y)
            fov.append((x, y))
            if 0 < x - 1 <= self.width:
                if (x - 1, y) not in bounds:
                    if (x - 1, y) not in fov:
                        # print('x - 1', (x - 1, y), (x - 1, y) in bounds)
                        q.append((x - 1, y))
                if (x + 1, y) not in bounds:
                    if (x + 1, y) not in fov:
                        # print('x + 1', q)
                        q.append((x + 1, y))
            if 0 < y - 1 <= self.height:
                if ((x, y - 1) not in bounds) and ((x, y - 1) not in fov):
                    # print('y - 1', q)
                    q.append((x, y - 1))
                if ((x, y + 1) not in bounds) and ((x, y + 1) not in fov):
                    # print('y + 1', q)
                    q.append((x, y + 1))
        return fov

    def point_in_poly(self, x, y, poly_original):
        # Improved point in polygon test which includes edge
        # and vertex points

        # check if point is a vertex
        if (x, y) in poly_original:
            # print('shortcut')
            return True

        # check if point is on a boundary
        # print('new', x, y)
        poly = poly_original + [poly_original[0]]
        # print(poly)
        for i in range(len(poly)):
            p1 = None
            p2 = None
            if i == 0:
                p1 = poly[0]
                p2 = poly[1]
            else:
                p1 = poly[i - 1]
                p2 = poly[i]
            if p1[1] == p2[1]:
                if p1[1] == y:
                    if x >= min(p1[0], p2[0]):
                        if x <= max(p1[0], p2[0]):
                            return True
            # elif p1[0] == p2[0]:
                # print('p1 p2 x', p1, p2)
                # if p1[0] == x:
                    # if y >= min(p1[1], p2[1]):
                        # if y <= max(p1[1], p2[1]):
                            # return True

        inside = False

        p1x, p1y = poly[0]
        for i in range(len(poly) + 1):
            p2x, p2y = poly[i % len(poly)]
            if y > min(p1y, p2y):
                # print('p1x, p1y', p1x, p1y)
                # print('p2x, p2y', p2x, p2y)
                # print('y min', y, min(p1y, p2y))
                if y <= max(p1y, p2y):
                    # print('y max', y, max(p1y, p2y))
                    if x <= max(p1x, p2x):
                        # print('x max', x, max(p1x, p2x))
                        if p1y != p2y:
                            # print('ne')
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
                            # print('not', inside)
            p1x, p1y = p2x, p2y

        # print('inside?', inside)
        return inside

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
        cur_max = 1
        # cur_max = randint(self.min_rooms, self.max_rooms)
        while len(self.rooms) < cur_max:
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
            # room.wall_points.remove((x, y))

class RectRoom:
    def __init__(self, x, y, w, h):
        self.x_left = x
        self.y_top = y
        self.x_right = x + w
        self.y_bottom = y + h
        self.corners()
        self.walls()

    def corners(self):
        top_left = (self.x_left, self.y_top)
        top_right = (self.x_right, self.y_top)
        bottom_right = (self.x_right, self.y_bottom)
        bottom_left = (self.x_left, self.y_bottom)
        self.corners = (top_left, top_right, bottom_right, bottom_left)
        self.corner_points = []
        self.corner_points.extend((top_left, top_right, bottom_right, bottom_left))

    def walls(self):
        top = self.line(self.x_left, self.y_top, self.x_right, self.y_top)
        right = self.line(self.x_right, self.y_top, self.x_right, self.y_bottom)
        bottom = self.line(self.x_left, self.y_bottom, self.x_right, self.y_bottom)
        left = self.line(self.x_left, self.y_top, self.x_left, self.y_bottom)
        self.walls = (top, right, bottom, left)
        self.wall_points = []
        for wall in self.walls:
            self.wall_points.extend(wall)

    def line(self, x0, y0, x1, y1):
        """Bresenham's line algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        plot = []
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                plot.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                plot.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        plot.append((x, y))
        return plot

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
