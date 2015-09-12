import curses
from termux2d import full_block
from sys import version_info
from termux2d import block_map

__author__ = 'ericmuxagata'

# python2 unicode curses fix
if not version_info[0] == 3:
    import locale
    locale.setlocale(locale.LC_ALL, "")

try:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)

    curses.start_color()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)

    stdscr.clear()

    stdscr.addstr(0,0, unichr(block_map[0x0F]).encode('utf-8'), curses.color_pair(0))
    stdscr.addstr(0,1, unichr(block_map[0x0F]).encode('utf-8'), curses.color_pair(1))

    stdscr.refresh()
    stdscr.getch()


finally:
    # Set everything back to normal
    if 'stdscr' in locals() or globals():
        stdscr.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.nocbreak()
        curses.endwin()