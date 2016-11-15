from time import perf_counter
from collections import namedtuple
import PyBearLibTerminal as terminal
import random
import yaml
from Thing_2 import *

class GameEngine:
    def __init__(self):
        self.window_width = 80
        self.window_height = 45
        self.screen_width = 58
        self.screen_height = 36
        self.cellsize = "12x12"
        self.update_interval_ms = 0.033
        self.update_per_frame_limit = 10
        self.offset = namedtuple('offset', 'x, y')
        self.pc = None
        self.actors = []

    def initialize_blt(self):
        terminal.open()
        terminal.set("window: size={}x{}, cellsize={}, title='Roguelike';"
                "font: default".format(
                    str(self.window_width),
                    str(self.window_height),
                    self.cellsize))
        terminal.clear()
        terminal.refresh()
        terminal.color("white")

    def generate_world(self):
        with open('data/world.yaml', 'r') as world_yaml:
            self.world = [w for w in yaml.load_all(world_yaml)][0]

    def generate_level(self, name):
        try:
            current_world = self.world[name]
        except Exception as ex:
            print('you fucked up:', ex)
            return None
        # self.current_world = Map(
        #     name=current_world['name'],
        #     width=current_world['width'],
        #     height=current_world['height'],
        #     min_rooms=current_world['min_rooms'],
        #     max_rooms=current_world['max_rooms'],
        #     num_exits=current_world['num_exits'],)

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
                if key is terminal.TK_CLOSE or key is terminal.TK_Q:
                    break
                else:
                    self.process_input(key)

    def update(self, time_elapsed, time_current):
        for actor in self.actors:
            # actor.take_turn()
            pass

    def render(self):
        terminal.clear()
        self.render_viewport()
        self.render_UI()
        self.render_message_bar()
        terminal.refresh()

    def render_viewport(self):
        self.find_offset()

    def render_UI(self):
        pass

    def render_message_bar(self):
        pass

    def find_offset(self):
        """
        From: http://www.roguebasin.com/index.php?title=Scrolling_map
        """
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        if self.pc.x < center_x:
            self.offset.x = 0
        elif self.pc.x > world.width - center_x:
            self.offset.x = world.width - SCREEN_WIDTH
        else:
            self.offset.x = self.pc.x - center_x

        if self.pc.y < center_y:
            self.offset.y = 0
        elif self.pc.y > world.height - center_y:
            self.offset.y = world.height - SCREEN_HEIGHT
        else:
            self.offset.y = self.pc.y - center_y

    def process_input(self, key):
        print(key)

    def cleanup(self):
        terminal.close()

if __name__ == "__main__":
    game = GameEngine()
    game.initialize_blt()
    game.generate_world()
    game.generate_level('debug')
    game.run()
    game.cleanup()
