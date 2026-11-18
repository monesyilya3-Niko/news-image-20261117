#!/usr/bin/env python3
"""Draw one image summing up the world news of Tuesday 17 November 2026.

Standard library only, no network, fully deterministic: the same run
always writes the same bytes to $MAKEFUN_OUTPUT_DIR/entry.png (or
/output/entry.png). The image is a newspaper-style poster: a date
banner plus six single-column story rows, each with a headline, two
detail lines and a small geometric pictogram. Text uses a built-in
5x7 bitmap font so the program needs no font files in the grader.

Stories (each verified against at least two independent news sources
dated 17 November 2026 before this program was written):
  1. US jets strike an IRGC missile site on Qeshm Island after Iranian
     drones target a US radar in Bahrain (Gulf News, Indian Express).
  2. Ukraine hits the Crimea Bridge for a second straight day in a
     record 1,441-drone barrage, Russia says (Reuters, Times of India).
  3. Quad leaders meet in Manila; Trump touts critical-minerals deals
     (Philstar, Firstpost, News18).
  4. PAHO revokes the US measles elimination status held since 2000
     (USA Today, Associated Press, The Hindu).
  5. Japan scrambles jets after two suspected Russian planes enter
     its airspace near Okinoshima (CNA, Kuwait Times/AFP).
  6. COP31 ministers take over in Antalya as a draft fossil-fuel
     phaseout text divides nations (Le Monde, Watan News).
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (245, 241, 230)
WHITE = (255, 255, 255)
INK = (26, 26, 26)
GRAY = (68, 68, 68)
NAVY = (20, 36, 62)
GOLD = (217, 164, 65)
BORDER = (30, 30, 30)

# 5x7 bitmap font: each glyph is 7 rows of 5 bits ('1' = ink).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
}

# (headline, detail line 1, detail line 2, accent colour, pictogram)
STORIES = [
    (
        "US STRIKES IRAN SITE",
        "US JETS HIT A MISSILE SITE ON QESHM ISLAND",
        "AFTER DRONES TARGETED US RADAR IN BAHRAIN",
        (179, 64, 46),
        "rocket",
    ),
    (
        "CRIMEA BRIDGE HIT AGAIN",
        "UKRAINE STRIKES THE BRIDGE FOR A SECOND DAY",
        "A RECORD 1,441-DRONE BARRAGE, RUSSIA SAYS",
        (46, 107, 168),
        "bridge",
    ),
    (
        "QUAD LEADERS MEET",
        "TRUMP, MODI, TAKAICHI AND ALBANESE MEET IN",
        "MANILA; TRUMP TOUTS CRITICAL-MINERALS DEALS",
        (31, 122, 107),
        "quad",
    ),
    (
        "US LOSES MEASLES STATUS",
        "ELIMINATION STATUS HELD SINCE 2000 REVOKED",
        "BY PAHO; 5,412 US CASES IN 2026",
        (122, 78, 158),
        "virus",
    ),
    (
        "JETS SCRAMBLED OVER JAPAN",
        "TWO SUSPECTED RUSSIAN PLANES ENTER AIRSPACE",
        "NEAR OKINOSHIMA; TOKYO PROTESTS TO MOSCOW",
        (201, 106, 31),
        "jet",
    ),
    (
        "COP31 TALKS HEAT UP",
        "MINISTERS TAKE OVER IN ANTALYA AS A DRAFT",
        "FOSSIL-FUEL PHASEOUT TEXT DIVIDES NATIONS",
        (74, 124, 47),
        "globe",
    ),
]


class Canvas:
    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * self.width + x0) * 3
            self.pixels[start:start + len(row)] = row

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def draw_line(self, x0, y0, x1, y1, colour, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set_pixel(xx, yy, colour)

    def draw_circle(self, cx, cy, r, colour, thick=3):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d2 <= (r + thick) * (r + thick):
                    self.set_pixel(xx, yy, colour)

    def fill_polygon(self, points, colour):
        # Scanline fill: deterministic, integer arithmetic only.
        ys = [p[1] for p in points]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.fill_rect(nodes[i], yy, nodes[i + 1] - nodes[i] + 1, 1, colour)


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(canvas, x, y, text, scale, colour):
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is not None:
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        canvas.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, colour
                        )
        cx += 6 * scale


def draw_text_centred(canvas, y, text, scale, colour, width=WIDTH):
    draw_text(canvas, (width - text_width(text, scale)) // 2, y, text, scale, colour)


def tint(colour, fraction=0.88):
    return tuple(int(c + (255 - c) * fraction) for c in colour)


def draw_icon(canvas, x, y, size, kind, colour):
    """Draw a simple geometric pictogram inside the square (x, y, size)."""
    canvas.fill_rect(x, y, size, size, tint(colour))
    canvas.draw_line(x, y, x + size - 1, y, colour, 2)
    canvas.draw_line(x, y + size - 1, x + size - 1, y + size - 1, colour, 2)
    canvas.draw_line(x, y, x, y + size - 1, colour, 2)
    canvas.draw_line(x + size - 1, y, x + size - 1, y + size - 1, colour, 2)
    cx = x + size // 2
    cy = y + size // 2
    if kind == "rocket":
        # Body pointing up, fins, flame, and two sea lines below.
        canvas.fill_polygon([(cx, y + 8), (cx - 11, y + 30), (cx + 11, y + 30)], colour)
        canvas.fill_rect(cx - 11, y + 30, 22, 30, colour)
        canvas.fill_circle(cx, y + 42, 5, WHITE)
        canvas.fill_polygon(
            [(cx - 11, y + 48), (cx - 24, y + 64), (cx - 11, y + 60)], colour
        )
        canvas.fill_polygon(
            [(cx + 11, y + 48), (cx + 24, y + 64), (cx + 11, y + 60)], colour
        )
        canvas.fill_polygon([(cx - 6, y + 60), (cx + 6, y + 60), (cx, y + 74)], GOLD)
        canvas.draw_line(x + 10, y + size - 8, x + size - 10, y + size - 8, colour, 3)
    elif kind == "bridge":
        # Deck, two towers, a suspension arc, three drones above.
        canvas.draw_line(x + 8, cy + 18, x + size - 8, cy + 18, colour, 5)
        canvas.fill_rect(cx - 26, cy - 8, 6, 30, colour)
        canvas.fill_rect(cx + 20, cy - 8, 6, 30, colour)
        prev = None
        for step in range(0, 65):
            px = x + 8 + step
            py = cy - 8 + int(14 * (1 - ((step - 32) / 32.0) ** 2))
            if prev is not None:
                canvas.draw_line(prev[0], prev[1], px, py, colour, 3)
            prev = (px, py)
        for dx, dy in ((-26, -26), (0, -32), (26, -26)):
            canvas.draw_line(cx + dx - 6, cy + dy, cx + dx + 6, cy + dy, colour, 3)
            canvas.draw_line(cx + dx, cy + dy - 6, cx + dx, cy + dy + 6, colour, 3)
            canvas.fill_circle(cx + dx, cy + dy, 2, colour)
    elif kind == "quad":
        # Four linked circles.
        for dx, dy in ((-20, -20), (20, -20), (-20, 20), (20, 20)):
            canvas.draw_line(cx, cy, cx + dx, cy + dy, colour, 3)
        canvas.fill_circle(cx, cy, 7, colour)
        for dx, dy in ((-20, -20), (20, -20), (-20, 20), (20, 20)):
            canvas.fill_circle(cx + dx, cy + dy, 11, colour)
            canvas.fill_circle(cx + dx, cy + dy, 5, WHITE)
    elif kind == "virus":
        # Spiked circle.
        canvas.fill_circle(cx, cy, 20, colour)
        for dx, dy in (
            (0, -30), (21, -21), (30, 0), (21, 21),
            (0, 30), (-21, 21), (-30, 0), (-21, -21),
        ):
            canvas.draw_line(cx, cy, cx + dx, cy + dy, colour, 4)
            canvas.fill_circle(cx + dx, cy + dy, 5, colour)
        canvas.fill_circle(cx - 6, cy - 4, 3, WHITE)
        canvas.fill_circle(cx + 7, cy + 5, 3, WHITE)
    elif kind == "jet":
        # Side-profile jet pointing right.
        canvas.fill_polygon(
            [
                (x + 8, cy + 2), (x + 30, cy - 8), (x + 66, cy - 4),
                (x + 80, cy + 2), (x + 66, cy + 8), (x + 30, cy + 10),
            ],
            colour,
        )
        canvas.fill_polygon(
            [(x + 34, cy - 6), (x + 48, cy - 30), (x + 56, cy - 30), (x + 50, cy - 4)],
            colour,
        )
        canvas.fill_polygon(
            [(x + 14, cy - 2), (x + 22, cy - 18), (x + 30, cy - 18), (x + 28, cy - 2)],
            colour,
        )
        canvas.fill_circle(x + 62, cy - 1, 4, WHITE)
        canvas.draw_line(x + 6, cy + 22, x + 34, cy + 22, colour, 3)
        canvas.draw_line(x + 14, cy + 30, x + 42, cy + 30, colour, 3)
    elif kind == "globe":
        # Globe with latitude lines and a small sun.
        canvas.draw_circle(cx - 4, cy + 4, 26, colour, 4)
        canvas.draw_line(cx - 30, cy + 4, cx + 22, cy + 4, colour, 3)
        canvas.draw_line(cx - 26, cy - 10, cx + 18, cy - 10, colour, 3)
        canvas.draw_line(cx - 26, cy + 18, cx + 18, cy + 18, colour, 3)
        canvas.draw_line(cx - 4, cy - 22, cx - 4, cy + 30, colour, 3)
        canvas.fill_circle(x + size - 20, y + 16, 7, GOLD)
        for dx, dy in ((0, -11), (8, -8), (11, 0), (8, 8), (0, 11)):
            canvas.draw_line(
                x + size - 20, y + 16, x + size - 20 + dx, y + 16 + dy, GOLD, 2
            )


def build_image():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)

    # Header banner.
    canvas.fill_rect(0, 0, WIDTH, 172, NAVY)
    draw_text_centred(canvas, 22, "WORLD NEWS", 8, WHITE)
    rule_w = 640
    canvas.fill_rect((WIDTH - rule_w) // 2, 92, rule_w, 4, GOLD)
    draw_text_centred(canvas, 104, "TUESDAY 17 NOVEMBER 2026", 5, GOLD)
    draw_text_centred(canvas, 144, "SIX STORIES FROM AROUND THE GLOBE", 3, WHITE)

    # Story rows.
    top = 188
    row_h = 120
    gap = 12
    margin = 24
    row_w = WIDTH - 2 * margin
    for i, (headline, detail1, detail2, accent, icon) in enumerate(STORIES):
        y = top + i * (row_h + gap)
        canvas.fill_rect(margin, y, row_w, row_h, WHITE)
        canvas.fill_rect(margin, y, 10, row_h, accent)
        # Border.
        canvas.draw_line(margin, y, margin + row_w - 1, y, BORDER, 2)
        canvas.draw_line(margin, y + row_h - 1, margin + row_w - 1, y + row_h - 1, BORDER, 2)
        canvas.draw_line(margin, y, margin, y + row_h - 1, BORDER, 2)
        canvas.draw_line(margin + row_w - 1, y, margin + row_w - 1, y + row_h - 1, BORDER, 2)
        # Number badge.
        badge_x = margin + 16
        badge_y = y + 31
        canvas.fill_rect(badge_x, badge_y, 58, 58, accent)
        num = str(i + 1)
        draw_text(
            canvas,
            badge_x + (58 - text_width(num, 6)) // 2,
            badge_y + 8,
            num,
            6,
            WHITE,
        )
        # Headline and details.
        text_x = margin + 92
        draw_text(canvas, text_x, y + 18, headline, 5, INK)
        draw_text(canvas, text_x, y + 62, detail1, 3, GRAY)
        draw_text(canvas, text_x, y + 86, detail2, 3, GRAY)
        # Pictogram on the right.
        draw_icon(canvas, WIDTH - margin - 16 - 88, y + 16, 88, icon, accent)

    # Footer.
    draw_text_centred(
        canvas, 986, "SOURCES: REUTERS, AFP, AP, PAHO, CNA - 17 NOV 2026", 2, GRAY
    )
    return canvas


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.width * 3
    for yy in range(canvas.height):
        raw.append(0)  # filter: none
        start = yy * stride
        raw.extend(canvas.pixels[start:start + stride])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_image())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
