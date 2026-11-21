#!/usr/bin/env python3
"""news-image-20261121: draw Saturday 21 November 2026's world news as one
1024x1024 front page, pure Python 3 stdlib (no PIL in the grader container).

Reads stories.json beside this file, renders with a built-in 5x7 bitmap font
and a hand-rolled PNG encoder, writes entry.png to $MAKEFUN_OUTPUT_DIR
(default /output). Deterministic: two runs write identical bytes.
"""

import json
import os
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = ink. Plain ASCII 32..126 only.
FONT = {
    ' ': ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    '!': ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    '#': (" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "),
    '$': ("  #  ", " ####", "# # #", " ### ", "  # #", "#### ", "  #  "),
    '%': ("##  #", "## # ", "    #", "   # ", "  #  ", " # ##", "#  ##"),
    '&': (" ### ", "#   #", "#   #", " # # ", "# # #", "#  # ", " ## #"),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    '(': ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ')': (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    '*': ("     ", "  #  ", "# # #", " ### ", "# # #", "  #  ", "     "),
    '+': ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    ',': ("     ", "     ", "     ", "     ", " ##  ", "  #  ", " #   "),
    '-': ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    '.': ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    '/': ("    #", "   # ", "   # ", "  #  ", " #   ", " #   ", "#    "),
    '0': (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    '1': ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    '2': (" ### ", "#   #", "    #", "  ## ", " #   ", "#    ", "#####"),
    '3': ("#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "),
    '4': ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    '5': ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    '6': ("  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "),
    '7': ("#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "),
    '8': (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    '9': (" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "),
    ':': ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ';': ("     ", " ##  ", " ##  ", "     ", " ##  ", "  #  ", " #   "),
    '<': ("   # ", "  #  ", " #   ", "#    ", " #   ", "  #  ", "   # "),
    '=': ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    '>': (" #   ", "  #  ", "   # ", "    #", "   # ", "  #  ", " #   "),
    '?': (" ### ", "#   #", "    #", "  ## ", "  #  ", "     ", "  #  "),
    '@': (" ### ", "#   #", "# ###", "# # #", "# ## ", "#    ", " ### "),
    'A': (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    'B': ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    'C': (" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "),
    'D': ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    'E': ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    'F': ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    'G': (" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ####"),
    'H': ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    'I': (" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    'J': ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    'K': ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    'L': ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    'M': ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    'N': ("#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"),
    'O': (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    'P': ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    'Q': (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    'R': ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    'S': (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    'T': ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    'U': ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    'V': ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    'W': ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    'X': ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    'Y': ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    'Z': ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    '[': (" ### ", " #   ", " #   ", " #   ", " #   ", " #   ", " ### "),
    '\\': ("#    ", " #   ", " #   ", "  #  ", "   # ", "   # ", "    #"),
    ']': (" ### ", "   # ", "   # ", "   # ", "   # ", "   # ", " ### "),
    '^': ("  #  ", " # # ", "#   #", "     ", "     ", "     ", "     "),
    '_': ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
    '`': (" #   ", "  #  ", "   # ", "     ", "     ", "     ", "     "),
    'a': ("     ", "     ", " ### ", "    #", " ####", "#   #", " ####"),
    'b': ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "),
    'c': ("     ", "     ", " ### ", "#   #", "#    ", "#   #", " ### "),
    'd': ("    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"),
    'e': ("     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "),
    'f': ("  ## ", " #  #", " #   ", "#### ", " #   ", " #   ", " #   "),
    'g': ("     ", " ####", "#   #", "#   #", " ####", "    #", " ### "),
    'h': ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    'i': ("  #  ", "     ", " ##  ", "  #  ", "  #  ", "  #  ", " ### "),
    'j': ("   # ", "     ", "  ## ", "   # ", "   # ", "#  # ", " ##  "),
    'k': ("#    ", "#    ", "#  # ", "# #  ", "##   ", "# #  ", "#  # "),
    'l': (" ##  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    'm': ("     ", "     ", "## # ", "# # #", "# # #", "# # #", "# # #"),
    'n': ("     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    'o': ("     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "),
    'p': ("     ", "     ", "#### ", "#   #", "#   #", "#### ", "#    "),
    'q': ("     ", "     ", " ####", "#   #", "#   #", " ####", "    #"),
    'r': ("     ", "     ", "# ## ", "##  #", "#    ", "#    ", "#    "),
    's': ("     ", "     ", " ####", "#    ", " ### ", "    #", "#### "),
    't': (" #   ", " #   ", "#### ", " #   ", " #   ", " #  #", "  ## "),
    'u': ("     ", "     ", "#   #", "#   #", "#   #", "#  ##", " ## #"),
    'v': ("     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "),
    'w': ("     ", "     ", "#   #", "# # #", "# # #", "# # #", " # # "),
    'x': ("     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"),
    'y': ("     ", "     ", "#   #", "#   #", " ####", "    #", " ### "),
    'z': ("     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"),
    '{': ("  ## ", " #   ", " #   ", "###  ", " #   ", " #   ", "  ## "),
    '|': ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    '}': ("##   ", "  #  ", "  #  ", "  ###", "  #  ", "  #  ", "##   "),
    '~': ("     ", "     ", " ## #", "# ## ", "     ", "     ", "     "),
}

# ---------------------------------------------------------------- PNG writer
def _chunk(kind, data):
    c = struct.pack(">I", len(data)) + kind + data
    return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += rgb[y * stride:(y + 1) * stride]
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )
    Path(path).write_bytes(png)
    return len(png)


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def _set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:(x1 - x0) * 3 + i] = bytes(c) * (x1 - x0)

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            self._set(x, y, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), 1, c)

    def text(self, x, y, s, scale, c, spacing=1):
        """Draw s at (x, y); returns width in px. Unknown chars -> '?'."""
        cx = x
        adv = 5 * scale + spacing
        for ch in s:
            g = FONT.get(ch, FONT['?'])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '#':
                        self.rect(cx + col * scale, y + r * scale, scale, scale, c)
            cx += adv
        return cx - x - spacing

    def text_w(self, s, scale, spacing=1):
        return len(s) * (5 * scale + spacing) - spacing

    def wrap(self, s, max_w, scale, spacing=1):
        """Greedy word wrap to lines of <= max_w px; raises if a word is too wide."""
        adv = 5 * scale + spacing
        lines, cur = [], ""
        for word in s.split(" "):
            trial = (cur + " " + word) if cur else word
            if len(trial) * adv - spacing <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                if len(word) * adv - spacing > max_w:
                    raise ValueError(f"word too wide: {word!r}")
                cur = word
        if cur:
            lines.append(cur)
        return lines

# ------------------------------------------------------------------ palette
PAPER = (246, 241, 227)
CARD = (255, 255, 255)
INK = (22, 35, 63)
GREY = (90, 100, 114)
RED = (179, 38, 30)
LINE = (203, 192, 170)
SEA = (211, 226, 233)
LAND = (233, 222, 182)
PINWHITE = (255, 255, 255)

COLORS = {
    "blue": (31, 78, 121),
    "teal": (14, 124, 107),
    "red": (179, 38, 30),
    "gold": (176, 124, 20),
    "green": (46, 125, 50),
    "purple": (106, 76, 147),
}

W = H = 1024
MARGIN = 24

# Simplified continent outlines (lon, lat) for a flat strip map.
CONTINENTS = [
    [(-168, 66), (-145, 70), (-130, 71), (-115, 73), (-100, 73), (-90, 74),
     (-82, 72), (-76, 69), (-70, 62), (-65, 60), (-60, 52), (-55, 47),
     (-65, 44), (-70, 42), (-74, 39), (-76, 35), (-80, 32), (-81, 26),
     (-84, 24), (-87, 21), (-90, 21), (-94, 17), (-97, 16), (-92, 15),
     (-86, 13), (-83, 10), (-80, 8), (-79, 9), (-83, 15), (-87, 13),
     (-90, 14), (-92, 15), (-95, 17), (-97, 19), (-101, 18), (-105, 20),
     (-109, 23), (-112, 28), (-117, 32), (-122, 37), (-124, 42), (-124, 48),
     (-128, 50), (-135, 58), (-145, 60), (-155, 58), (-162, 55), (-168, 60)],
    [(-79, 9), (-77, 7), (-75, 10), (-72, 12), (-68, 11), (-64, 10),
     (-60, 8), (-55, 6), (-52, 4), (-50, 0), (-44, -3), (-40, -5),
     (-35, -8), (-37, -13), (-39, -17), (-41, -23), (-46, -26), (-50, -30),
     (-54, -34), (-58, -38), (-62, -41), (-65, -45), (-68, -50), (-70, -53),
     (-73, -50), (-73, -44), (-72, -37), (-71, -30), (-70, -23), (-75, -15),
     (-79, -8), (-81, -4), (-80, 1)],
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (-4, 48), (-1, 49),
     (-3, 50), (0, 50), (2, 51), (5, 53), (8, 54), (8, 57), (10, 58),
     (12, 56), (18, 56), (21, 55), (24, 58), (24, 60), (28, 61), (30, 62),
     (30, 66), (25, 70), (20, 70), (15, 68), (12, 64), (8, 62), (5, 60),
     (5, 58), (0, 57), (-3, 55), (-5, 53), (-5, 50), (-8, 48), (-10, 45),
     (-10, 40), (-9, 37)],
    [(-5, 50), (-3, 53), (-5, 55), (-3, 58), (-1, 57), (0, 54), (1, 51),
     (-2, 50)],
    [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-6, 33), (-1, 35),
     (5, 37), (10, 37), (15, 32), (20, 32), (25, 32), (30, 31), (32, 31),
     (34, 28), (36, 23), (38, 18), (40, 15), (43, 12), (48, 11), (51, 12),
     (51, 10), (48, 5), (46, 0), (42, -3), (40, -8), (38, -12), (36, -18),
     (33, -22), (30, -27), (27, -33), (22, -35), (19, -35), (17, -32),
     (15, -27), (13, -20), (12, -17), (12, -12), (10, -8), (9, -4),
     (9, 0), (9, 4), (6, 4), (0, 6), (-5, 5), (-8, 4), (-12, 8),
     (-15, 11)],
    [(30, 36), (36, 36), (40, 38), (44, 39), (48, 38), (48, 33), (50, 30),
     (54, 26), (58, 25), (62, 25), (66, 25), (70, 22), (73, 20), (77, 12),
     (80, 8), (83, 17), (87, 21), (91, 21), (94, 17), (97, 15), (100, 9),
     (103, 4), (105, 8), (108, 12), (110, 20), (114, 23), (118, 25),
     (121, 28), (124, 33), (127, 36), (130, 40), (134, 43), (138, 46),
     (141, 50), (141, 56), (138, 60), (134, 62), (130, 66), (126, 69),
     (122, 72), (117, 73), (112, 74), (107, 75), (102, 77), (97, 76),
     (92, 75), (87, 74), (82, 73), (77, 72), (72, 72), (67, 70),
     (62, 69), (57, 68), (52, 68), (47, 68), (42, 68), (37, 67), (32, 65),
     (30, 60), (30, 54), (28, 50), (26, 46), (24, 42), (22, 40), (20, 38),
     (16, 37), (12, 38), (8, 36), (4, 36), (0, 36)],
    [(113, -22), (114, -28), (115, -33), (118, -35), (122, -34), (126, -32),
     (129, -32), (132, -32), (135, -35), (137, -35), (138, -37), (140, -38),
     (142, -39), (145, -38), (147, -39), (150, -37), (152, -34), (153, -30),
     (153, -27), (151, -24), (148, -20), (146, -19), (143, -15), (142, -11),
     (140, -17), (137, -12), (135, -12), (132, -12), (130, -13), (127, -14),
     (124, -15), (121, -17), (118, -20), (115, -21)],
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 77),
     (-35, 79), (-45, 78), (-55, 76), (-58, 72), (-55, 68), (-50, 64)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (175, -40),
     (172, -42), (168, -46)],
]


def draw_icon(cv, kind, x, y, s, c):
    """Small flat pictogram inside an s x s box at (x, y)."""
    if kind == "target":
        cv.circle(x + s // 2, y + s // 2, s // 2 - 1, c)
        cv.circle(x + s // 2, y + s // 2, s // 2 - 4, PAPER)
        cv.circle(x + s // 2, y + s // 2, 2, c)
    elif kind == "missile":
        cv.poly([(x + s - 2, y + 1), (x + s - 2, y + 9), (x + s - 9, y + 1)], c)
        cv.rect(x + 3, y + s - 8, 8, 5, c)
        cv.line(x + 5, y + 6, x + 11, y + s - 8, c)
    elif kind == "deal":
        cv.rect(x + 2, y + 1, s - 4, s - 2, c)
        cv.rect(x + 4, y + 3, s - 8, s - 6, PAPER)
        cv.line(x + 5, y + 9, x + 8, y + 13, RED)
        cv.line(x + 8, y + 13, x + 15, y + 5, RED)
    elif kind == "quake":
        cv.line(x + 1, y + 3, x + 6, y + 10, c)
        cv.line(x + 6, y + 10, x + 10, y + 4, c)
        cv.line(x + 10, y + 4, x + 15, y + 12, c)
        cv.line(x + 3, y + 16, x + 8, y + 9, c)
        cv.line(x + 12, y + 17, x + 16, y + 10, c)
    elif kind == "gavel":
        cv.rect(x + 2, y + 2, 12, 5, c)
        cv.line(x + 8, y + 7, x + 15, y + 16, c)
        cv.rect(x + 1, y + 16, 16, 2, c)
    elif kind == "leaf":
        cv.circle(x + s // 2, y + s // 2 - 1, 7, c)
        cv.line(x + s // 2, y + s - 2, x + s // 2, y + s // 2 + 5, (46, 125, 50))
    elif kind == "mic":
        cv.circle(x + s // 2, y + 6, 5, c)
        cv.rect(x + s // 2 - 1, y + 10, 2, 6, c)
        cv.rect(x + 3, y + 16, s - 6, 2, c)
    elif kind == "capitol":
        cv.poly([(x + 1, y + 8), (x + s // 2, y + 1), (x + s - 1, y + 8)], c)
        for cx in (x + 3, x + 8, x + 13):
            cv.rect(cx, y + 9, 3, 7, c)
        cv.rect(x + 1, y + 16, s - 2, 2, c)
    elif kind == "shield":
        cv.poly([(x + 2, y + 1), (x + s - 2, y + 1), (x + s - 2, y + 9),
                 (x + s // 2, y + s - 1), (x + 2, y + 9)], c)
        cv.line(x + 6, y + 9, x + 9, y + 13, PAPER)
        cv.line(x + 9, y + 13, x + 15, y + 5, PAPER)
    elif kind == "flame":
        cv.poly([(x + s // 2, y + 1), (x + s - 2, y + 11), (x + s // 2, y + 9),
                 (x + 2, y + 11)], c)
        cv.rect(x + 4, y + 13, s - 8, 4, c)
    elif kind == "chart":
        for i, hh in enumerate((6, 10, 15)):
            cv.rect(x + 2 + i * 6, y + s - 2 - hh, 4, hh, c)
    elif kind == "bat":
        cv.line(x + 3, y + s - 3, x + s - 4, y + 4, c)
        cv.rect(x + s - 7, y + 2, 5, 5, c)
        cv.circle(x + 4, y + 5, 3, RED)
    else:
        cv.rect(x + 2, y + 2, s - 4, s - 4, c)


def draw(data):
    cv = Canvas(W, H, PAPER)
    total = data["total_stories"]
    featured = data["featured"]
    also = data["also"]

    # ---------------------------------------------------------- masthead
    mast = "THE WORLD IN ONE DAY"
    cv.text((W - cv.text_w(mast, 2)) // 2, 14, mast, 2, INK)
    date = data["date"]
    cv.text((W - cv.text_w(date, 5)) // 2, 38, date, 5, INK)
    sub = f"{total} STORIES | {data['regions']} REGIONS | EVERY ONE FROM THIS SATURDAY"
    cv.text((W - cv.text_w(sub, 2)) // 2, 82, sub, 2, RED)
    cv.rect(MARGIN, 100, W - 2 * MARGIN, 4, RED)

    # --------------------------------------------------- featured stories
    cw, chh, gap = 320, 98, 6
    for i, st in enumerate(featured):
        col, row = i % 3, i // 3
        x = MARGIN + col * (cw + gap)
        y = 110 + row * (chh + gap)
        color = COLORS[st["color"]]
        cv.rect(x, y, cw, chh, CARD)
        cv.rect(x, y, cw, 4, color)
        draw_icon(cv, st["icon"], x + 8, y + 8, 20, color)
        cv.text(x + 36, y + 11, st["tag"], 2, color)
        # number badge, top right
        bx, by = x + cw - 20, y + 18
        cv.circle(bx, by, 11, color)
        num = str(st["n"])
        cv.text(bx - cv.text_w(num, 1) // 2, by - 3, num, 1, PINWHITE)
        # title: up to 2 lines, pitch 13 (all caps, no descenders)
        tlines = cv.wrap(st["title"], cw - 16, 2)
        assert len(tlines) <= 2, f"title too long: {st['title']!r}"
        for k, ln in enumerate(tlines):
            cv.text(x + 8, y + 30 + k * 13, ln, 2, INK)
        # summary: up to 3 lines, pitch 14
        slines = cv.wrap(st["summary"], cw - 16, 2)
        assert len(slines) <= 3, f"summary too long ({len(slines)} lines): {st['summary']!r}"
        for k, ln in enumerate(slines):
            cv.text(x + 8, y + 56 + k * 14, ln, 2, GREY)

    # ---------------------------------------------------------- UTC timeline
    ty = 528
    cv.line(200, ty + 24, W - 60, ty + 24, LINE)
    tl = data["timeline"]
    for i, (t, label) in enumerate(tl):
        dx = 260 + i * 140
        cv.circle(dx, ty + 24, 5, RED)
        cv.text(dx - cv.text_w(t, 2) // 2, ty + 4, t, 2, INK)
        cv.text(dx - cv.text_w(label, 1) // 2, ty + 32, label, 1, GREY)

    # --------------------------------------------------------------- map
    my = 572
    cv.text(MARGIN, my, "WHERE IT HAPPENED", 2, INK)
    mx, mw, mh = MARGIN, 620, 104
    map_y = my + 16
    cv.rect(mx, map_y, mw, mh, SEA)

    def proj(lon, lat):
        return (mx + int((lon + 170) / 360 * mw),
                map_y + int((84 - lat) / 142 * mh))

    for poly in CONTINENTS:
        cv.poly([proj(lon, lat) for lon, lat in poly], LAND)
    for st in featured:
        px, py = proj(st["lon"], st["lat"])
        qx, qy = px + st.get("pin_dx", 0), py + st.get("pin_dy", 0)
        if (qx, qy) != (px, py):
            cv.line(px, py, qx, qy, INK)
        cv.circle(qx, qy, 9, COLORS[st["color"]])
        num = str(st["n"])
        cv.text(qx - cv.text_w(num, 1) // 2, qy - 3, num, 1, PINWHITE)

    # pin legend, right of the map
    lx = 660
    cv.text(lx, my, "PINNED STORIES", 2, INK)
    names = ["Copenhagen", "Poland", "London", "Junin, Peru", "The Hague",
             "Antalya", "Washington", "Washington", "Gaza", "Yemen",
             "New Delhi", "Perth"]
    for i, st in enumerate(featured):
        col, row = i % 2, i // 2
        px = lx + col * 172
        py = map_y + 4 + row * 11
        cv.circle(px + 4, py + 3, 4, COLORS[st["color"]])
        cv.text(px + 12, py, f"{st['n']} {names[i]}", 1, INK)
    leg_y = map_y + 4 + 6 * 11 + 6
    cv.text(lx, leg_y, "EUROPE  N. AMERICA  MIDDLE EAST", 1, GREY)
    cv.text(lx, leg_y + 9, "ASIA  LATIN AMERICA  OCEANIA  CLIMATE", 1, GREY)

    # ---------------------------------------------------------- ALSO list
    ay = 700
    cv.text(MARGIN, ay, "ALSO ON SATURDAY 21 NOVEMBER", 2, INK)
    cv.rect(MARGIN, ay + 18, W - 2 * MARGIN, 2, LINE)
    ly = ay + 24
    for i, item in enumerate(also):
        col, row = i % 2, i // 2
        x = MARGIN + col * 488
        y = ly + row * 16
        lines = cv.wrap(item, 464, 2)
        assert len(lines) == 1, f"also item too long: {item!r}"
        cv.rect(x, y + 3, 7, 7, RED)
        cv.text(x + 12, y, item, 2, INK)

    # ---------------------------------------------------------- DATE CHECK
    dy = 984
    cv.text(MARGIN, dy, "DATE CHECK:", 2, RED)
    dc = "LEFT OUT: " + " | ".join(data["date_check"])
    cv.text(MARGIN + cv.text_w("DATE CHECK: ", 2) + 4, dy + 4, dc, 1, GREY)

    # --------------------------------------------------------------- footer
    fy = 1002
    cv.text(MARGIN, fy,
            "Every story here happened or was first reported on Saturday 21 November 2026.",
            1, INK)
    cv.text(MARGIN, fy + 8,
            "Sources: " + data["sources"] + "  |  Original drawings",
            1, GREY)
    return cv


def main():
    with open(HERE / "stories.json", encoding="utf-8") as f:
        data = json.load(f)
    cv = draw(data)
    outdir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        out = outdir / "entry.png"
        n = write_png(out, W, H, cv.px)
    except OSError:
        out = HERE / "entry.png"
        n = write_png(out, W, H, cv.px)
    print(f"wrote {out} ({n} bytes, limit 1048576)")
    if n > 1048576:
        sys.exit("entry.png exceeds 1 MiB")


if __name__ == "__main__":
    main()
