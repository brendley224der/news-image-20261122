#!/usr/bin/env python3
"""The World Today -- a one-page newspaper front page for Sunday 22 November 2026.

Pure Python standard library only. Draws six of the day's biggest stories onto a
1024x1024 PNG and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
No network, no randomness, no clock: the same input always produces the same bytes.
"""

import os
import struct
import zlib
from binascii import crc32

W, H = 1024, 1024
PAPER = (251, 247, 236)
INK = (26, 26, 26)
RED = (163, 22, 33)
BLUE = (31, 78, 121)
GREY = (110, 105, 95)
LIGHT = (238, 231, 214)

# A 5x7 bitmap font. Each glyph is seven rows of five pixels, '#' on, '.' off.
# Uppercase, digits and the punctuation the page needs; all page text is set in caps.
FONT = {
    "A": ("..#..", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", "#.#.#", "#.##."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
}


class Canvas:
    """An RGB framebuffer with rectangle and bitmap-text drawing."""

    def __init__(self, width, height, color):
        self.w = width
        self.h = height
        self.px = bytearray(color * (width * height))

    def rect(self, x, y, w, h, color):
        r, g, b = color
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            for xx in range(w):
                i = base + xx * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def circle(self, cx, cy, r, color):
        """A 1px circle outline (midpoint algorithm)."""
        x, y, d = 0, r, 1 - r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                if 0 <= px < self.w and 0 <= py < self.h:
                    i = (py * self.w + px) * 3
                    self.px[i], self.px[i + 1], self.px[i + 2] = color
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def text(self, x, y, s, scale, color):
        """Draw uppercase text; unknown glyphs become blanks."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return max(0, len(s) * 6 * scale - scale)

    def center(self, y, s, scale, color):
        self.text((self.w - self.text_width(s, scale)) // 2, y, s, scale, color)


def wrap(s, width_chars):
    """Greedy word wrap to at most width_chars characters per line."""
    lines = []
    for chunk in s.split("\n"):
        line = ""
        for word in chunk.split(" "):
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= width_chars:
                line += " " + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def hrule(canvas, x, y, w, color, thick=2):
    canvas.rect(x, y, w, thick, color)


def story(canvas, x, y, w, kicker, headline, body, head_scale=3):
    """One boxed story: red kicker, headline, wrapped body text."""
    canvas.rect(x, y, 6, 14, RED)
    canvas.text(x + 14, y, kicker, 2, RED)
    hy = y + 26
    for line in wrap(headline, w // (6 * head_scale)):
        canvas.text(x, hy, line, head_scale, INK)
        hy += 7 * head_scale + 4
    by = hy + 6
    for line in wrap(body, w // 12):
        canvas.text(x, by, line, 2, INK)
        by += 18
    return by


def build_page():
    c = Canvas(W, H, PAPER)
    m = 40  # margin
    inner = W - 2 * m

    # Masthead, with a small globe emblem in the left margin.
    c.circle(m + 28, 68, 28, BLUE)
    c.rect(m + 28, 40, 1, 56, BLUE)
    c.rect(m, 68, 56, 1, BLUE)
    c.center(40, "THE WORLD TODAY", 8, INK)
    c.text(m, 116, "SUNDAY 22 NOVEMBER 2026", 2, BLUE)
    right = "SIX STORIES THAT DEFINED THE DAY"
    c.text(W - m - c.text_width(right, 2), 116, right, 2, BLUE)
    hrule(c, m, 142, inner, INK, 4)
    hrule(c, m, 150, inner, INK, 1)

    # Lead story: the Gulf war widens.
    y = 168
    c.rect(m, y, 6, 14, RED)
    c.text(m + 14, y, "GULF WAR WIDENS", 2, RED)
    y += 30
    for line in ("IRAN HITS US AIR BASE IN KUWAIT",
                 "AS FIGHTING SPREADS ACROSS THE GULF"):
        c.text(m, y, line, 4, INK)
        y += 36
    y += 8
    lead = ("TEHRAN STRUCK A US AIR BASE IN KUWAIT AND TARGETED BAHRAIN AS "
            "FIGHTING SPREAD ACROSS THE GULF. MULTIPLE TANKERS WERE HIT OFF "
            "OMAN AND OIL PRICES FELL SHARPLY AS NAVAL TENSIONS ESCALATED.")
    for line in wrap(lead, inner // 12):
        c.text(m, y, line, 2, INK)
        y += 18
    y += 12
    hrule(c, m, y, inner, INK, 1)
    y += 16

    # Four stories in a two-by-two grid.
    col_w = (inner - 20) // 2
    grid_top = y
    row_h = 208
    stories = [
        ("CLIMATE", "COP31 TALKS DEADLOCK",
         "A FIGHT OVER FOSSIL FUELS AND CLIMATE FINANCE LEFT THE COP31 "
         "SUMMIT STALLED AS NEGOTIATORS SEARCHED FOR A DEAL."),
        ("DISASTER", "QUAKE SHAKES PERU",
         "A MAGNITUDE 6.9 EARTHQUAKE STRUCK PERU'S ANDES. NO DAMAGE OR "
         "CASUALTIES WERE IMMEDIATELY REPORTED."),
        ("MEXICO", "CARTEL BOSS CAPTURED",
         "MEXICAN FORCES ARRESTED EL CHAPO ISIDRO IN A SPECIAL FORCES RAID. "
         "CARTEL VIOLENCE IN SINALOA LEFT 11 DEAD."),
        ("UKRAINE", "RUSSIA'S BIG BARRAGE",
         "RUSSIA FIRED 400 DRONES AND 110 MISSILES IN ONE OF THE WAR'S "
         "LARGEST ATTACKS. A STRIKE ON ZELENSKYY'S HOMETOWN KILLED TWO."),
    ]
    for i, (kicker, head, body) in enumerate(stories):
        sx = m + (i % 2) * (col_w + 20)
        sy = grid_top + (i // 2) * row_h
        story(c, sx, sy, col_w, kicker, head, body)
    y = grid_top + 2 * row_h - 8
    hrule(c, m, y, inner, INK, 1)
    y += 16

    # Fifth story, full width: Estonia closes its border with Russia.
    y = story(c, m, y, inner,
              "EUROPE", "ESTONIA TO CLOSE ITS BORDER WITH RUSSIA",
              "TALLINN SAID IT WILL SHUT ITS BORDER WITH RUSSIA. MOSCOW DECRIED "
              "A NEW IRON CURTAIN.", head_scale=3) + 28
    hrule(c, m, y, inner, INK, 1)
    y += 14

    # Footnote strip: the rest of the day in one line.
    c.text(m, y, "ALSO:", 2, RED)
    rest = ("TRUMP TOUTS SUMMIT WITH XI AND PUTIN - BOLSONARO IN INTENSIVE "
            "CARE - AIR NIUGINI JET LANDS SAFELY AFTER ENGINE FIRE")
    for line in wrap(rest, (inner - 64) // 12):
        c.text(m + 64, y, line, 2, GREY)
        y += 18
    y += 6
    hrule(c, m, y, inner, INK, 4)
    c.text(m, y + 12, "THE WORLD TODAY", 2, BLUE)
    right = "22 NOVEMBER 2026"
    c.text(W - m - c.text_width(right, 2), y + 12, right, 2, BLUE)
    return c


def png_bytes(canvas):
    raw = bytearray()
    for row in range(canvas.h):
        raw.append(0)  # filter: none
        start = row * canvas.w * 3
        raw.extend(canvas.px[start:start + canvas.w * 3])
    data = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        out = struct.pack(">I", len(payload)) + tag + payload
        return out + struct.pack(">I", crc32(tag + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", data) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_page())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
