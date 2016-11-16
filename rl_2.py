from time import perf_counter
from collections import namedtuple
from enum import IntEnum
from collections.abc import Sequence
import PyBearLibTerminal as terminal
import random
import yaml

class Game_States(IntEnum):
    MAIN_MENU = 0
    NEW_GAME = 1
    IN_GAME = 2
    OPTIONS = 3
    HISTORY = 4

class Thing:
    def __init__(self, glyph, x, y):
        self.glyph = glyph
        self.x = x
        self.y = y

    def __str__(self):
        return 'Thing: glyph={}, x={}, y={}'.format(self.glyph, self.x, self.y)

class Map(Sequence):
    def __init__(self, name, width, height, min_rooms, max_rooms):
        self.name = name
        self.width = width
        self.height = height
        self.min_rooms = min_rooms
        self.max_rooms = max_rooms
        self.layout = [[None for y in range(height)] for x in range(width)]

    def __getitem__(self, key):
        return self.layout[key]

    def __len__(self):
        return self.width * self.height

    def __str__(self):
        info = 'Map: name={}, width={}, height={}\n'.format(self.name, self.width, self.height)
        pic = '\n'.join([str([' . ' * len(y)]) for y in self.layout])
        return info + pic

class Viewport:
    def __init__(self, left_edge, top_edge):
        self.left_edge = left_edge
        self.top_edge = top_edge

class GameEngine:
    def __init__(self):
        self.window_width = 80
        self.window_height = 45
        self.screen_width = 58
        self.screen_height = 36
        self.cellsize = "12x12"
        self.update_interval_ms = 0.033
        self.update_per_frame_limit = 10
        self.offset = Viewport(0, 0)
        self.actors = []
        self.state = Game_States.IN_GAME

    def initialize_blt(self):
        terminal.open()
        terminal.set(
            "window: size={}x{}, cellsize={}, title='Roguelike';"
            "font: default;"
            "input: filter=[keyboard+];"
            "".format(
                str(self.window_width),
                str(self.window_height),
                self.cellsize))
        terminal.clear()
        terminal.refresh()
        terminal.color("white")

    def load_world_data(self):
        with open('data/world.yaml', 'r') as world_yaml:
            self.world_data = yaml.load(world_yaml)

    def generate_level(self, name):
        current_level_data = self.world_data[name]
        try:
            self.current_world = Map(
                name=current_level_data['name'],
                width=current_level_data['width'],
                height=current_level_data['height'],
                min_rooms=current_level_data['min_rooms'],
                max_rooms=current_level_data['max_rooms'],)
        except Exception as ex:
            print('you fucked up:', ex)
            return None
        self.generate_player('human')

    def generate_player(self, race):
        with open('data/player.yaml', 'r') as player_yaml:
            race_options = yaml.load(player_yaml)
            self.races = race_options
        chosen_race = race_options[race]
        try:
            self.pc = Thing(chosen_race['char'], 10, 10)
        except Exception as ex:
            print('you fucked up:', ex)
            return None

    def run(self):
        UPDATE_INTERVAL_MS = self.update_interval_ms
        UPDATE_PER_FRAME_LIMIT = self.update_per_frame_limit
        clock = 0
        previous_time = perf_counter()
        next_update = 0
        proceed = True

        while proceed:
            current_time = perf_counter()
            if current_time - previous_time > (UPDATE_INTERVAL_MS * UPDATE_PER_FRAME_LIMIT):
                clock += UPDATE_INTERVAL_MS * UPDATE_PER_FRAME_LIMIT
            else:
                clock += current_time - previous_time
            while clock >= next_update:
                time_elapsed = UPDATE_INTERVAL_MS
                time_current = next_update
                self.update(time_elapsed, time_current)
                next_update += UPDATE_INTERVAL_MS
            previous_time = perf_counter()
            self.render()
            if terminal.has_input():
                key = terminal.read()
                if key is terminal.TK_CLOSE:
                    proceed = False
                else:
                    proceed = self.process_input(key)

    def update(self, time_elapsed, time_current):
        for actor in self.actors:
            actor.take_turn()

    def render(self):
        terminal.clear()
        self.render_viewport()
        self.render_UI()
        self.render_message_bar()
        terminal.refresh()

    def render_viewport(self):
        self.set_offset()
        for row in range(self.offset.top_edge, self.screen_height):
            for col in range(self.offset.left_edge, self.screen_width):
                terminal.print_(col, row, '.')
        terminal.print_(self.pc.x, self.pc.y, self.pc.glyph)

    def render_UI(self):
        pass

    def render_message_bar(self):
        pass

    def set_offset(self):
        """
        From: http://www.roguebasin.com/index.php?title=Scrolling_map
        """
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        if self.pc.x < center_x:
            self.offset.left_edge = 0
        elif self.pc.x > self.current_world.width - center_x:
            self.offset.left_edge = self.current_world.width - self.screen_width
        else:
            self.offset.left_edge = self.pc.x - center_x

        if self.pc.y < center_y:
            self.offset.top_edge = 0
        elif self.pc.y > self.current_world.height - center_y:
            self.offset.top_edge = self.current_world.height - self.screen_height
        else:
            self.offset.top_edge = self.pc.y - center_y

    def process_input(self, key):
        if key == terminal.TK_Q and terminal.check(terminal.TK_SHIFT):
            return False
        elif key == terminal.TK_ESCAPE:
            return False
        if self.state == Game_States.MAIN_MENU:
            self.menu_input(key)
        elif self.state == Game_States.IN_GAME:
            self.in_game_input(key)
        return True

    def menu_input(self, key):
        pass

    def in_game_input(self, key):
        key_released = (terminal.TK_KEY_RELEASED, 0)[terminal.check(terminal.TK_SHIFT)]
        if key == terminal.TK_L | key_released:
            self.move_pc(1, 0)
        elif key == terminal.TK_N | key_released:
            self.move_pc(1, 1)
        elif key == terminal.TK_J | key_released:
            self.move_pc(0, 1)
        elif key == terminal.TK_B | key_released:
            self.move_pc(-1, 1)
        elif key == terminal.TK_H | key_released:
            self.move_pc(-1, 0)
        elif key == terminal.TK_Y | key_released:
            self.move_pc(-1, -1)
        elif key == terminal.TK_K | key_released:
            self.move_pc(0, -1)
        elif key == terminal.TK_U | key_released:
            self.move_pc(1, -1)

    def move_pc(self, tx, ty):
        dx, dy = self.pc.x + tx, self.pc.y + ty
        if self.current_world.width > dx >= 0 and self.current_world.height > dy >= 0:
            self.pc.x = dx
            self.pc.y = dy

    def cleanup(self):
        terminal.close()

if __name__ == "__main__":
    game = GameEngine()
    game.initialize_blt()
    game.load_world_data()
    game.generate_level('debug')
    game.run()
    game.cleanup()
