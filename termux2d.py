import math
import os
from sys import version_info
from collections import defaultdict
from time import sleep
from copy import deepcopy
import curses


IS_PY3 = version_info[0] == 3

if IS_PY3:
    unichr = chr

"""

http://www.alanwood.net/unicode/braille_patterns.html

quadrants:
   ,___,
   |1 2|
   |3 4|
   `````
"""

pixel_map = ((0x01, 0x02),
             (0x04, 0x08))

full_block = 0x0F

block_map = {0x01: 0x2598,
             0x02: 0x259D,
             0x03: 0x2580,
             0x04: 0x2596,
             0x05: 0x258C,
             0x06: 0x259E,
             0x07: 0x259B,
             0x08: 0x2597,
             0x09: 0x259A,
             0x0A: 0x2590,
             0x0B: 0x259C,
             0x0C: 0x2584,
             0x0D: 0x2599,
             0x0E: 0x259F,
             0x0F: 0x2588}


COLOR_BLACK     = curses.COLOR_BLACK
COLOR_RED       = curses.COLOR_RED
COLOR_GREEN     = curses.COLOR_GREEN
COLOR_BLUE      = curses.COLOR_BLUE
COLOR_YELLOW    = curses.COLOR_YELLOW
COLOR_CYAN      = curses.COLOR_CYAN
COLOR_MAGENTA   = curses.COLOR_MAGENTA
COLOR_WHITE     = curses.COLOR_WHITE

KEY_UP      = curses.KEY_UP
KEY_DOWN    = curses.KEY_DOWN
KEY_LEFT    = curses.KEY_LEFT
KEY_RIGHT   = curses.KEY_RIGHT


DEFAULT_COLORS = {COLOR_WHITE:0,
                  COLOR_RED:1,
                  COLOR_GREEN:2,
                  COLOR_BLUE:3,
                  COLOR_YELLOW:4}

# http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
def get_terminal_size():
    """Returns terminal width, height
    """
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)

    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass

    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[1]), int(cr[0])

def get_terminal_size_in_pixels():
    tw, th = get_terminal_size()
    return 2*tw, 4*th



def normalize(coord):
    coord_type = type(coord)

    if coord_type == int:
        return coord
    elif coord_type == float:
        return int(round(coord))
    else:
        raise TypeError("Unsupported coordinate type <{0}>".format(type(coord)))


def intdefaultdict():
    return defaultdict(int)


def get_pos(x, y):
    """Convert x, y to cols, rows"""
    return normalize(x) // 2, normalize(y) // 4


class Canvas(object):
    """This class implements the pixel surface."""

    def __init__(self, line_ending=os.linesep):
        super(Canvas, self).__init__()
        self.line_ending = line_ending
        self.static_chars = defaultdict(intdefaultdict)
        self.static_colors = defaultdict(intdefaultdict)
        self.clear()

    def set_static(self, frame):
        for x,y,c in frame:
            self.set(x,y)
            self.set_color(x,y,c)
        self.static_chars = deepcopy(self.chars)
        self.static_colors = deepcopy(self.colors)

    def draw(self,stdscr):
        pass


    def clear(self):
        """Remove all pixels from the :class:`Canvas` object."""
        self.chars = deepcopy(self.static_chars)
        self.colors = deepcopy(self.static_colors)

    def reset(self, x,y):
        x = normalize(x)
        y = normalize(y)
        col,row = get_pos(x,y)

        if type(self.chars[row][col]) != int:
            return

        self.chars[row][col] = self.static_chars[row][col]

    def reset_color(self,x,y):

        x = normalize(x)
        y = normalize(y)
        col, row = get_pos(x, y)

        if type(self.chars[row][col]) != int:
            return

        self.colors[row][col] = self.static_colors[row][col]


    def set(self, x, y):
        """Set a pixel of the :class:`Canvas` object.

        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        """
        x = normalize(x)
        y = normalize(y)
        col, row = get_pos(x, y)

        if type(self.chars[row][col]) != int:
            return

        self.chars[row][col] |= pixel_map[(y % 4) // 2][x % 2]



    def unset(self, x, y):
        """Unset a pixel of the :class:`Canvas` object.

        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        """
        x = normalize(x)
        y = normalize(y)
        col, row = get_pos(x, y)

        if type(self.chars[row][col]) == int:
            self.chars[row][col] &= ~pixel_map[(y % 4) // 2][x % 2]

        if type(self.chars[row][col]) != int or self.chars[row][col] == 0:
            del(self.chars[row][col])

        if not self.chars.get(row):
            del(self.chars[row])


    def toggle(self, x, y):
        """Toggle a pixel of the :class:`Canvas` object.

        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        """
        x = normalize(x)
        y = normalize(y)
        col, row = get_pos(x, y)

        if type(self.chars[row][col]) != int or self.chars[row][col] & pixel_map[(y % 4) // 2][x % 2]:
            self.unset(x, y)
        else:
            self.set(x, y)


    def set_text(self, x, y, text):
        """Set text to the given coords.

        :param x: x coordinate of the text start position
        :param y: y coordinate of the text start position
        """
        col, row = get_pos(x, y)

        for i,c in enumerate(text):
            self.chars[row][col+i] = c

    def set_color(self,x,y,color):
        """Set color to the given coords.

        :param x: x coordinate of the char to be colored
        :param y: y coordinate of the char to be colored
        """
        col,row = get_pos(x,y)
        self.colors[row][col] = color


    def get(self, x, y):
        """Get the state of a pixel. Returns bool.

        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        """
        x = normalize(x)
        y = normalize(y)
        dot_index = pixel_map[(y % 4) // 2][x % 2]
        col, row = get_pos(x, y)
        char = self.chars.get(row, {}).get(col)

        if not char:
            return False

        if type(char) != int:
            return True

        return bool(char & dot_index)


    def rows(self, min_x=None, min_y=None, max_x=None, max_y=None):
        """Returns a list of the current :class:`Canvas` object lines.
        :param min_x: (optional) minimum x coordinate of the canvas
        :param min_y: (optional) minimum y coordinate of the canvas
        :param max_x: (optional) maximum x coordinate of the canvas
        :param max_y: (optional) maximum y coordinate of the canvas
        """

        if not self.chars.keys():
            return []

        minrow = min_y // 4 if min_y != None else min(self.chars.keys())
        maxrow = (max_y - 1) // 4 if max_y != None else max(self.chars.keys())
        mincol = min_x // 2 if min_x != None else min(min(x.keys()) for x in self.chars.values())
        maxcol = (max_x - 1) // 2 if max_x != None else max(max(x.keys()) for x in self.chars.values())
        ret = []

        for rownum in range(minrow, maxrow+1):
            if not rownum in self.chars:
                ret.append('')
                continue

            maxcol = (max_x - 1) // 2 if max_x != None else max(self.chars[rownum].keys())
            row = []

            for x in range(mincol, maxcol+1):
                char = self.chars[rownum].get(x)

                if not char:
                    row.append(' ')
                elif type(char) != int:
                    row.append(char)
                else:
                    row.append(unichr(block_map[char]))

            ret.append(''.join(row))

        return ret


    def frame(self, min_x=None, min_y=None, max_x=None, max_y=None):
        """String representation of the current :class:`Canvas` object pixels.
        :param min_x: (optional) minimum x coordinate of the canvas
        :param min_y: (optional) minimum y coordinate of the canvas
        :param max_x: (optional) maximum x coordinate of the canvas
        :param max_y: (optional) maximum y coordinate of the canvas
        """
        ret = self.line_ending.join(self.rows(min_x, min_y, max_x, max_y))

        if IS_PY3:
            return ret

        return ret.encode('utf-8')


def line(x1, y1, x2, y2):
    """Returns the coords of the line between (x1, y1), (x2, y2)

    :param x1: x coordinate of the startpoint
    :param y1: y coordinate of the startpoint
    :param x2: x coordinate of the endpoint
    :param y2: y coordinate of the endpoint
    """

    x1 = normalize(x1)
    y1 = normalize(y1)
    x2 = normalize(x2)
    y2 = normalize(y2)

    xdiff = max(x1, x2) - min(x1, x2)
    ydiff = max(y1, y2) - min(y1, y2)
    xdir = 1 if x1 <= x2 else -1
    ydir = 1 if y1 <= y2 else -1

    r = max(xdiff, ydiff)

    for i in range(r+1):
        x = x1
        y = y1

        if ydiff:
            y += (float(i) * ydiff) / r * ydir
        if xdiff:
            x += (float(i) * xdiff) / r * xdir

        yield (x, y)


def polygon(center_x=0, center_y=0, sides=4, radius=4):
    degree = float(360) / sides

    for n in range(sides):
        a = n * degree
        b = (n + 1) * degree
        x1 = (center_x + math.cos(math.radians(a))) * (radius + 1) / 2
        y1 = (center_y + math.sin(math.radians(a))) * (radius + 1) / 2
        x2 = (center_x + math.cos(math.radians(b))) * (radius + 1) / 2
        y2 = (center_y + math.sin(math.radians(b))) * (radius + 1) / 2

        for x, y in line(x1, y1, x2, y2):
            yield x, y


class Palette(object):
    def __init__(self):
        #each color has an (r,g,b) value as key, mapped to its (color_idx,pair_idx) tuple.
        self.colors = dict(DEFAULT_COLORS)
        self.pair_index = len(DEFAULT_COLORS)

    def start_colors(self):
        if not curses.can_change_color():
            return

        curses.start_color()
        for color_index in self.colors.keys():
            pair_index = self.colors[color_index]
            if pair_index != 0:
                curses.init_pair(pair_index, color_index, curses.COLOR_BLACK)
            curses.init_pair(pair_index+10,color_index,color_index)

    def add_color(self,color_index):
        if color_index not in self.colors:
            self.colors[color_index] = self.pair_index
            self.pair_index += 1


global stdscr

def handle_input():
    global stdscr
    return stdscr.getch()


def animate(canvas, palette, fn, delay=1./24, *args, **kwargs):
    """Animation automatition function

    :param canvas: :class:`Canvas` object
    :param fn: Callable. Frame coord generator
    :param delay: Float. Delay between frames.
    :param *args, **kwargs: optional fn parameters
    """

    # python2 unicode curses fix
    if not IS_PY3:
        import locale
        locale.setlocale(locale.LC_ALL, "")

    def animation(stdscr):
        seen = defaultdict(bool)

        #Draw static frame.
        sf = canvas.frame()
        stdscr.addstr(0,0,sf)

        for frame in fn(*args, **kwargs):
            #Reset abandoned pixels.
            for x,y,c in frame:
                if seen[(x,y,c)]:
                    seen.pop((x,y,c))

            for x,y,c in seen:
                canvas.reset(x,y)
                canvas.reset_color(x,y)

                col,row = get_pos(x,y)
                color = canvas.colors[row][col]

                color_pair = curses.color_pair(0)
                if color in palette.colors:
                    color_pair = curses.color_pair(palette.colors[color])

                char = canvas.chars[row][col]
                if char:
                    stdscr.addstr(row, col, unichr(block_map[char]).encode('utf-8'), color_pair)
                else:
                    stdscr.addstr(row, col, " ", color_pair)


            #Update dynamic frame.
            seen.clear()
            for x,y,c in frame:
                seen[(x,y,c)] = True
                # Bug when a static is present here.
                if canvas.get(x,y):
                    continue

                canvas.set(x,y)
                canvas.set_color(x,y,c)

                col,row = get_pos(x,y)
                color = canvas.colors[row][col]

                color_pair = curses.color_pair(0)
                if color in palette.colors:
                    color_pair = curses.color_pair(palette.colors[color])

                char = canvas.chars[row][col]
                stdscr.addstr(row, col, unichr(block_map[char]).encode('utf-8'), color_pair)

            #Refresh window.
            stdscr.refresh()

            #Wait for fps delay.
            if delay:
                sleep(delay)

    animation_wrapper(animation, palette)


def animation_wrapper(func, palette, *args, **kwds):
    global stdscr
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.keypad(1)
        stdscr.nodelay(True)

        palette.start_colors()

        return func(stdscr, *args, **kwds)
    finally:
        # Set everything back to normal
        if 'stdscr' in locals() or globals():
            stdscr.keypad(0)
            stdscr.nodelay(False)
            curses.echo()
            curses.curs_set(1)
            curses.nocbreak()
            curses.endwin()



