import curses
import itertools
import random

import settings
from utils.utils import sleep_loop


class Star:
    def __init__(self, row: int, column: int, time_sleep: int, symbol: chr):
        self.row = row
        self.column = column
        self.time_sleep = time_sleep
        self.symbol = symbol

    async def blink(self, canvas: curses.window) -> None:
        await sleep_loop(self.time_sleep)
        
        settings_for_flashing_star = [
            {'time_sleep': 20, 'brightness': curses.A_DIM},
            {'time_sleep': 3, 'brightness': None},
            {'time_sleep': 5, 'brightness': curses.A_BOLD},
            {'time_sleep': 3, 'brightness': None},
        ]
        for config in itertools.cycle(settings_for_flashing_star):
            time_sleep_of_star = config['time_sleep']
            brightness_star = config['brightness']
            
            if brightness_star:
                canvas.addstr(self.row, self.column, self.symbol, brightness_star)
            else:
                canvas.addstr(self.row, self.column, self.symbol)
            await sleep_loop(time_sleep_of_star)


class Stars:
    def __init__(self, max_row: int, max_col: int, min_row: int  = 1, 
                 min_col: int = 1):
        self.min_row = min_row
        self.max_row = max_row
        self.min_col = min_col
        self.max_col = max_col

    def fill(self, canvas: curses.window) -> list:
        for _ in range(settings.N_STARS):
            row = random.randrange(self.min_row, self.max_row)
            column = random.randrange(self.min_col, self.max_col)
            time_sleep_of_star = random.randrange(settings.MAX_TIME_SLEEP_OF_STAR)
            symbol = random.choice(settings.SYMBOLS_OF_STARS)
            
            settings.coroutines.append(
              Star(row, column, time_sleep_of_star, symbol).blink(canvas))
    