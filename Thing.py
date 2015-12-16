from uuid import uuid4
from collections.abc import Sequence
from enum import IntEnum
from random import randint, randrange
from math import atan2, sqrt, pi


class Game_States(IntEnum):
    MAIN_MENU = 0
    NEW_GAME = 1
    IN_GAME = 2
    OPTIONS = 3
    HISTORY = 4


class LOS_Shape(IntEnum):
    EUCLID = 0
    SQUARE = 1


COLOR = {
    'blue': '#89CCEE',
    'purple': '#332288',
    'turqoise': '#44AA99',
    'green': '#117733',
    'brown': '#999933',
    'yellow': '#DDCC77',
    'orange': '#CC6677',
    'red': '#882255',
    'pink': '#AA4499',
    'white': '#EEEEEE',
    'black': '#000000',
    'grey': '#191919',
    }


class Thing:
    def __init__(self, x, y, glyph, color, physical, visible=True):
        self.x = x
        self.y = y
        self.glyph = glyph
        if type(color) is 'str':
            self.color = COLOR[color]
        else:
            self.color = color
        self.physical = physical
        self.visible = visible

    def __eq__(self, other):
        return ((self.glyph, self.color,
                 self.physical, self.visible) ==
                (other.glyph, other.color,
                 other.physical, other.visible))

    def build_char(self, within_fov):
        if within_fov:
            bkcolor = ""
        else:
            bkcolor = "[bkcolor={}]".format(COLOR['grey'])
        elements = [bkcolor, "[color={}]".format(self.color), self.glyph]
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
        self.base_radius = 8
        self.radius = self.base_radius
        self.los_shape = LOS_Shape.SQUARE
        self.fov_toggle = True
        self.viewed_map = set()
        self.apparel = set()
        # Finalization Methods
        world.register(self)

    def change_los(self):
        if self.los_shape < len(LOS_Shape) - 1:
            self.los_shape = LOS_Shape(self.los_shape + 1)
        else:
            self.los_shape = LOS_Shape(0)
        if self.los_shape == LOS_Shape.EUCLID:
            self.radius = sqrt(((self.base_radius * 2) ** 2) / pi)
        else:
            self.radius = self.base_radius

    def build_char(self, within_fov):
        super().build_char(within_fov)
        apparel = "[+]" + [x for x in self.apparel] if self.apparel else ""
        self.char = "".join((self.char, apparel))

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
        return "x: {}, "
        "y: {}, "
        "glyph: {}, "
        "char: {}, "
        "color: {}, "
        "physical: {}, "
        "occupied: {}, "
        "prop: {}, "
        "item: {}, "
        "uuid: {}".format(self.x, self.y, self.glyph, self.char, self.color,
                          self.physical, self.occupied, self.prop, self.item,
                          self.uuid)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def build_door(self):
        self.update(glyph='.', physical=False)
        self.prop = Prop(x=self.x, y=self.y, glyph='+',
                         color=COLOR['white'], physical=True)
        self.prop.update(is_door=True, door_status=True)

    def check_door(self):
        if self.prop and self.prop.is_door:
            return True

    def toggle_door(self):
        self.prop.door_status = not self.prop.door_status
        self.prop.glyph = ["-", "+"][self.prop.door_status]
        self.prop.physical = not self.prop.physical

    def build_char(self, fov_map, fov_toggle=True):
        # Only for debugging purposes. In production, this won't be accessible.
        if fov_toggle:
            if (self.x, self.y) in fov_map:
                within_fov = True
            else:
                within_fov = False
        else:
            within_fov = True

        if self.occupied:
            self.occupied.build_char(within_fov)
        elif self.item:
            self.item.build_char(within_fov)
        elif self.prop:
            self.prop.build_char(within_fov)
        else:
            super().build_char(within_fov)
            if within_fov:
                bkcolor = "[bkcolor={}]".format(self.bkcolor)
            else:
                bkcolor = "[bkcolor={}]".format(COLOR['grey'])
            color = "[color={}]".format(self.color)
            elements = [bkcolor, color, self.glyph]
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

    def line(self, x0, y0, x1, y1, halt=False):
        """Bresenham's line algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        plot = []
        if dx > dy:
            err = dx / 2.0
            if halt:
                while x != x1:
                    plot.append((x, y))
                    err -= dy
                    if err < 0:
                        y += sy
                        err += dx
                    x += sx
            else:
                while 0 <= x < self.width:
                    plot.append((x, y))
                    err -= dy
                    if err < 0:
                        y += sy
                        err += dx
                    x += sx
        else:
            err = dy / 2.0
            if halt:
                while y != y1:
                    plot.append((x, y))
                    err -= dx
                    if err < 0:
                        x += sx
                        err += dy
                    y += sy
            else:
                while 0 <= y < self.height:
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
        Adapted from http://ncase.me/sight-and-light/
        Notable changes: Instead of building a polygon from all possible
        corners, instead build from intersecting elements at the edge of
        the radius of line-of-sight.
        Unchanged is the construction of a polygon for the boundary and
        filling it in using point-in-polygon.
        """
        """
        Below is the previous version of the code. I have it in git, but I
        want it available if I decide to reuse it for some reason.

        corners = []
        wall_points = []
        for room in self.rooms:
            wall_points.extend(room.wall_points)
            for corner in room.corners:
                if corner not in corners:
                    corners.append(corner)

        lines = []
        for corner in corners:
            lines.append(self.line(actor.x, actor.y
                                   corner[0], corner[1], True))
            # if more x than y, it's to the left and right
            # add one above and below
            if abs(corner[0] - actor.x) > abs(corner[1] - actor.y):
                lines.append(self.line(actor.x, actor.y,
                                       corner[0], corner[1] - 1))
                lines.append(self.line(actor.x, actor.y,
                                       corner[0], corner[1] + 1))
            # otherwise, it's more y than x, so add one left and right
            else:
                lines.append(self.line(actor.x, actor.y
                                       corner[0] - 1, corner[1]))
                lines.append(self.line(actor.x, actor.y
                                       corner[0] + 1, corner[1]))
        # check orthogonal directions
        lines.append(self.line(actor.x, actor.y, actor.x - 1, actor.y))
        lines.append(self.line(actor.x, actor.y, actor.x + 1, actor.y))
        lines.append(self.line(actor.x, actor.y, actor.x, actor.y - 1))
        lines.append(self.line(actor.x, actor.y, actor.x, actor.y + 1))
        # check diagonal directions
        lines.append(self.line(actor.x, actor.y, actor.x - 1, actor.y - 1))
        lines.append(self.line(actor.x, actor.y, actor.x + 1, actor.y - 1))
        lines.append(self.line(actor.x, actor.y, actor.x - 1, actor.y + 1))
        lines.append(self.line(actor.x, actor.y, actor.x + 1, actor.y + 1))
        """

        wall_points = []
        for room in self.rooms:
            wall_points.extend(room.wall_points)

        vision_boundary = RectRoom(actor.x - actor.radius,
                                   actor.y - actor.radius,
                                   actor.x + actor.radius,
                                   actor.y + actor.radius)
        lines = []
        line = vision_boundary.wall_points
        for point in line:
            lines.append(self.line(actor.x, actor.y, point[0], point[1]))

        polygon = []
        for line in lines:
            for step in line:
                intersection = None
                # No friggin need to repeatedly check the origin.
                if (actor.x, actor.y) == step:
                    continue
                # Only for debugging purposes. Will probably just be square
                # in the final game. Who knows, though? yolo
                # Also, these math bits are weird. I don't know that I need
                # them.
                if actor.los_shape == LOS_Shape.EUCLID:
                    distance = sqrt((step[0] - actor.x) ** 2
                                    + (step[1] - actor.y) ** 2)
                else:
                    distance = max(abs(step[0] - actor.x),
                                   abs(step[1] - actor.y))
                if distance < actor.radius:
                    if step in wall_points:
                        if not self[step[0]][step[1]].check_door():
                            intersection = step
                        else:
                            if self[step[0]][step[1]].prop.door_status:
                                intersection = step
                elif distance >= actor.radius:
                    intersection = step
                if not intersection:
                    continue
                break
            if intersection:
                if intersection not in polygon:
                    polygon.append(intersection)

        def algo(point):
            nonlocal actor
            return (atan2(point[1] - actor.y,
                          point[0] - actor.x)
                    + 2 * pi) % (2 * pi)

        polygon.sort(key=algo)
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
            line = self.line(v1[0], v1[1], v2[0], v2[1], True)
            for tile in line:
                if tile not in poly_walls:
                    poly_walls.extend(line)

        # bounding box: it's the enclosing box of possible tiles that need
        # to be checked for point-in-polygon. Probably a faster method,
        # but yolo.
        bb = (min(poly_walls)[0], min(poly_walls, key=lambda x: x[1])[1],
              max(poly_walls)[0], max(poly_walls, key=lambda x: x[1])[1])
        fov = []
        vertx, verty = zip(*poly_walls)
        for y in range(bb[1], bb[3] + 1):
            for x in range(bb[0], bb[2] + 1):
                # Sanity check: Obviously the walls are visible.
                if (x, y) in poly_walls:
                    fov.append((x, y))
                elif self.point_in_poly(x, y, vertx, verty):
                    fov.append((x, y))
        actor.viewed_map.update(fov)
        self.fov_map = fov

    def point_in_poly(self, x, y, vertx, verty):
        """
        Adapted from:
        https://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
        I could have changed it to use a bounding box, but I think the
        zip(*poly_walls) method is the fastest way to do it. Works well enough
        for me right now.
        """
        c = False
        j = len(vertx) - 1
        for i in range(len(vertx)):
            if ((verty[i] > y) != (verty[j] > y)):
                if (x < (vertx[j] - vertx[i])
                        * (y - verty[i])
                        / (verty[j] - verty[i])
                        + vertx[i]):
                    c = not c
            j = i
        return c

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
        self.layout = [[Tile(x=x, y=y, glyph='.', color=COLOR['green'],
                       bkcolor=COLOR['black'], physical=False)
                       for y in range(self.height)]
                       for x in range(self.width)]
        self.fov = [[False for y in range(self.height)]
                    for x in range(self.width)]

    def carve_rooms(self):
        # cur_max = self.max_rooms + 5
        cur_max = randint(self.min_rooms, self.max_rooms)
        while len(self.rooms) < cur_max:
            w, h = randint(2, 10), randint(2, 10)
            x, y = randint(0, self.width - w), randint(0, self.height - h)
            new_room = RectRoom(x, y, w, h)
            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break
            if (new_room.x_right >= self.width) or (new_room.y_bottom >=
                                                    self.height):
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
                            self[x][y].update(glyph='#',
                                              color='grey',
                                              physical=True)
                        else:
                            self[x][y].update(glyph='.', color='amber')
        new_room = RectRoom(0, 0, self.width - 1, self.height - 1)
        for x in range(new_room.x_left, new_room.x_right + 1):
            for y in range(new_room.y_top, new_room.y_bottom + 1):
                if ((x == new_room.x_left) or
                   (x == new_room.x_right) or
                   (y == new_room.y_top) or
                   (y == new_room.y_bottom)):
                    self[x][y].update(glyph='#', color='grey', physical=True)
        self.rooms.append(new_room)

    def carve_passages(self):
        pass

    def build_features(self):
        for room in self.rooms:
            side = randint(0, 3)
            if side is 0:
                x, y = (randrange(room.x_left + 1, room.x_right),
                        room.y_top)
            elif side is 1:
                x, y = (room.x_left,
                        randrange(room.y_top + 1, room.y_bottom))
            elif side is 2:
                x, y = (randrange(room.x_left + 1, room.x_right),
                        room.y_bottom)
            elif side is 3:
                x, y = (room.x_right,
                        randrange(room.y_top + 1, room.y_bottom))
            self[x][y].build_door()


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
        self.corner_points.extend((top_left,
                                  top_right,
                                  bottom_right,
                                  bottom_left))

    def walls(self):
        top = self.line(self.x_left,
                        self.y_top,
                        self.x_right,
                        self.y_top)
        right = self.line(self.x_right,
                          self.y_top,
                          self.x_right,
                          self.y_bottom)
        bottom = self.line(self.x_left,
                           self.y_bottom,
                           self.x_right,
                           self.y_bottom)
        left = self.line(self.x_left,
                         self.y_top,
                         self.x_left,
                         self.y_bottom)
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
        return (self.x_left <= other.x_right
                and self.x_right >= other.x_left
                and self.y_top <= other.y_bottom
                and self.y_bottom >= other.y_top)


class RightAnglePassage:
    def __init__(self, start_loc, end_loc, width):
        self.x1, self.y1 = start_loc
        self.x2, self.y2 = end_loc
        self.width = width

    def length(self):
        return (abs(self.x2 - self.x1) + abs(self.y2 - self.y1))
