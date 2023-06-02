import curses
import random
import os
from statistics import median

import settings
from animation.explosion import explode
from utils.curses_tools import draw_frame, get_frame_size
from utils.game_scenario import get_garbage_delay_tics
from utils.utils import sleep_loop
from .frame import Frame
from .obstacles import Obstacle


class Garbage:

    def __init__(self, column: int, frame: str, speed: float = 0.5):
        self.column = column
        self.row = 0
        self.frame = frame
        self.speed = speed

    async def fly(self, canvas: curses.window):
        """Animate garbage, flying from top to bottom. Сolumn position will stay 
        same, as specified on start."""
        rows_number, columns_number = canvas.getmaxyx()
        self.column = median([0, self.column, columns_number - 1])
        obstacle = Obstacle(self.row,
                            self.column,
                            self.frame.row,
                            self.frame.column,
                            uid=self)
        settings.obstacles.append(obstacle)

        while self.row < rows_number:
            obstacle.row = self.row
            draw_frame(canvas, self.row, self.column, self.frame.frame)
            await sleep_loop(5)
            draw_frame(canvas,
                       self.row,
                       self.column,
                       self.frame.frame,
                       negative=True)
            self.row += self.speed
            if obstacle in settings.obstacles_in_last_collisions:
                settings.coroutines.append(
                    explode(canvas, self.row, self.column))
                break

        settings.obstacles.remove(obstacle)


class GarbageManagement:

    def __init__(self, max_col: int, min_col: int = 1):
        self.max_col = max_col
        self.min_col = min_col
        self.garbages_frames = []

        for file_name in os.listdir(settings.DIR_OF_GARBAGE_FRAMES):
            with open(settings.DIR_OF_GARBAGE_FRAMES + file_name) as file:
                frame = file.read()
                row, column = get_frame_size(frame)
                self.garbages_frames.append(Frame(frame, row, column))

    async def fill(self, canvas: curses.window):
        while True:
            garbage_delay = get_garbage_delay_tics(settings.YEAR)
            if not garbage_delay:
                await sleep_loop(1)
            else:
                random_frame = random.choice(self.garbages_frames)
                random_col = random.randint(self.min_col,
                                            self.max_col - random_frame.column)
                garbage = Garbage(random_col, random_frame)
                settings.coroutines.append(garbage.fly(canvas))
                await sleep_loop(garbage_delay)
