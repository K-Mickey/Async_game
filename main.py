import curses
import time

import settings
from objects.space import Stars
from objects.garbage import GarbageManagement
from objects.rocket import Rocket
from utils.game_scenario import draw_info_text
from utils.utils import sleep_loop


def draw(canvas: curses.window):
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas.refresh()

    max_row, max_column = get_size_screen(canvas)
    fill_the_event_loop(canvas, max_row, max_column)
    start_event_loop(canvas)


def fill_the_event_loop(canvas: curses.window, max_row: int, max_column: int):
    settings.coroutines.append(Rocket(max_row, max_column).run(canvas))
    settings.coroutines.append(GarbageManagement(max_column).fill(canvas))
    
    start_coord_sub_window = (max_row - 1, 2)
    sub_window = canvas.derwin(*start_coord_sub_window)
    settings.coroutines.append(draw_info_text(sub_window))
    settings.coroutines.append(is_next_year())

    Stars(max_row, max_column).fill(canvas)


def get_size_screen(canvas: curses.window):
    #get the screen size
    max_border_row, max_border_column = canvas.getmaxyx()
    #get the space height
    max_row = max_border_row - 1
    #get the space width
    max_column = max_border_column - 1
    return max_row, max_column


def start_event_loop(canvas: curses.window):
    while True:
        for coroutine in settings.coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                settings.coroutines.remove(coroutine)

        canvas.refresh()
        canvas.border()
        time.sleep(settings.TIC_TIMEOUT)


async def is_next_year():
    while True:
        settings.YEAR += 1
        await sleep_loop(15)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
