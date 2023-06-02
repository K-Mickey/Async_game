import curses
import itertools
import statistics
import os

import settings
from animation.fire import fire
from objects.frame import Frame
from utils import physics
from utils.curses_tools import draw_frame, read_controls, get_frame_size
from utils.utils import sleep_loop, show_gameover, is_obstacle_collisions, show_gameover


class Rocket:

    def __init__(self, max_row: int, max_col: int):
        self.row_speed = 0
        self.col_speed = 0
        self.mod_move = settings.MOD_MOVE

        self._get_frames()
        self._initial_coordination(max_row, max_col)

    def _get_frames(self):
        self._frames = []
        for file_name in os.listdir(settings.DIR_OF_ROCKET_FRAMES):
            with open(settings.DIR_OF_ROCKET_FRAMES + file_name) as file:
                frame = file.read()
                row, column = get_frame_size(frame)
                self._frames.append(Frame(frame, row, column))

    def _initial_coordination(self, max_row: int, max_col: int):
        random_frame = self._frames[0]
        frame_row = random_frame.row
        frame_col = random_frame.column

        self.min_border_col = -1
        self.max_border_col = max_col - frame_col
        self.min_border_row = 1
        self.max_border_row = max_row - frame_row

        # middle of the hight screen
        self.row_ind = max_row // 2 - frame_row // 2
        # middle of the width screen
        self.col_ind = max_col // 2 - frame_col // 2

        self.fire_offset = frame_col // 2 + 1

    def _calculate_coordination(self, canvas: curses.window):
        rows_direction, columns_direction, space_pressed = read_controls(
            canvas)

        if space_pressed:
            settings.coroutines.append(self.open_fire(canvas))

        if rows_direction or columns_direction:
            self.row_speed, self.col_speed = physics.update_speed(
                self.row_speed, self.col_speed, rows_direction,
                columns_direction)

        self.row_ind += self.row_speed * self.mod_move
        self.col_ind += self.col_speed * self.mod_move

        row = statistics.median(
            [self.min_border_row, self.row_ind, self.max_border_row])
        if self.row_ind >= self.max_border_row:
            self.row_speed = 0

        col = statistics.median(
            [self.min_border_col, self.col_ind, self.max_border_col])
        if self.col_ind >= self.max_border_col:
            self.col_speed = 0

        return row, col

    async def run(self, canvas: curses.window):
        for frame in itertools.cycle(self._frames):
            for _ in range(2):
                row, col = self._calculate_coordination(canvas)
                draw_frame(canvas, row, col, frame())
                await sleep_loop(1)
                draw_frame(canvas, row, col, frame(), negative=True)
                if is_obstacle_collisions(row, col, self._frames[0].row,
                                          self._frames[0].column):
                    settings.coroutines.append(show_gameover(canvas))
                    return

    async def open_fire(self, canvas: curses.window):
        if settings.YEAR >= 2020:
            for _ in range(3):
                await sleep_loop(10)
                settings.coroutines.append(
                    fire(canvas, self.row_ind, self.col_ind + self.fire_offset))
