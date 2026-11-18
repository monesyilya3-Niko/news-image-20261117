#!/usr/bin/env python3
"""Render the newspaper front page for make.fun news-image-20261117.

Provenance renderer: produces entry.png (1024x1024) from the verified
story list. Deterministic: no randomness, no timestamps, fixed palette.
The graded program (main.py) ships the rendered PNG; this file documents
how it was made. Requires Pillow locally; it never runs in the sandbox.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/noto"
SERIF_BLACK = os.path.join(FONT_DIR, "NotoSerifDisplay-Black.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "NotoSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "NotoSerif-Regular.ttf")
SANS = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
SANS_SB = os.path.join(FONT_DIR, "NotoSans-SemiBold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# Palette
PAPER = (247, 242, 231)
PAPER_DK = (238, 231, 214)
INK = (26, 24, 20)
GRAY = (96, 92, 82)
RULE = (60, 56, 48)
RED = (158, 32, 24)
RED_DK = (120, 24, 18)
SEA = (206, 221, 224)
SEA_DK = (168, 196, 201)
LAND = (226, 216, 184)
LAND_LINE = (150, 138, 104)
SKY = (205, 224, 232)
SKY_DUSK = (233, 196, 150)
SAND = (232, 220, 188)
GREEN = (110, 138, 104)
NIGHT = (32, 44, 66)


def tracked(draw, xy, text, fnt, fill, tracking=2):
    """Draw text with manual letter tracking; returns total width."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += int(draw.textlength(ch, font=fnt)) + tracking
    return x - xy[0] - tracking


def tracked_width(draw, text, fnt, tracking=2):
    return sum(int(draw.textlength(c, font=fnt)) + tracking for c in text) - tracking


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, fnt, max_w, ellipsis="..."):
    """Truncate a single line to max_w, adding an ellipsis if cut."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + ellipsis, font=fnt) > max_w:
        text = text[:-1]
    return text + ellipsis


def rect(d, box, fill=None, outline=None, width=1):
    d.rectangle(box, fill=fill, outline=outline, width=width)


# ---------------- pictorial vignettes (flat, geometric, no text) ----------------

def _clip_scene(size):
    """Return a fresh scene image + draw for a vignette of `size`."""
    img = Image.new("RGB", size, PAPER)
    return img, ImageDraw.Draw(img)


def v_bridge(size):
    """Broken bridge arch over the sea, dawn sky."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, int(h * 0.62)], fill=SKY_DUSK)
    d.ellipse([int(w * 0.68), int(h * 0.10), int(w * 0.84), int(h * 0.10) + int(w * 0.16)], fill=(244, 214, 150))
    d.rectangle([0, int(h * 0.62), w, h], fill=SEA_DK)
    for i in range(3):  # wave lines
        y = int(h * 0.70) + i * int(h * 0.10)
        d.line([(0, y), (w, y)], fill=SEA, width=2)
    # deck + pillars: two standing spans, collapsed middle
    dy = int(h * 0.52)
    d.rectangle([0, dy, int(w * 0.38), dy + 8], fill=INK)
    d.rectangle([int(w * 0.62), dy, w, dy + 8], fill=INK)
    d.polygon([(int(w * 0.38), dy + 8), (int(w * 0.50), dy + 34), (int(w * 0.44), dy + 8)], fill=INK)
    d.polygon([(int(w * 0.62), dy + 8), (int(w * 0.52), dy + 30), (int(w * 0.58), dy + 8)], fill=INK)
    # truss diagonals under the standing spans
    for x0 in (int(w * 0.04), int(w * 0.16), int(w * 0.28)):
        d.line([(x0, dy + 8), (x0 + int(w * 0.08), dy + 24)], fill=INK, width=3)
    for x0 in (int(w * 0.66), int(w * 0.78), int(w * 0.90)):
        d.line([(x0, dy + 8), (x0 + int(w * 0.08), dy + 24)], fill=INK, width=3)
    # support pillars
    d.rectangle([int(w * 0.10), dy + 8, int(w * 0.13), int(h * 0.62)], fill=INK)
    d.rectangle([int(w * 0.86), dy + 8, int(w * 0.89), int(h * 0.62)], fill=INK)
    # splash where the middle section fell
    for sx in (int(w * 0.46), int(w * 0.50), int(w * 0.54)):
        d.line([(sx, int(h * 0.62)), (sx, int(h * 0.62) - 10)], fill=(255, 255, 255), width=3)
    return img


def v_jets(size, island=True):
    """Two jets over sea and an island silhouette."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, int(h * 0.70)], fill=SKY)
    d.rectangle([0, int(h * 0.70), w, h], fill=SEA_DK)
    d.line([(0, int(h * 0.82)), (w, int(h * 0.82))], fill=SEA, width=2)
    if island:
        d.polygon([(0, int(h * 0.70)), (int(w * 0.30), int(h * 0.52)),
                   (int(w * 0.55), int(h * 0.70))], fill=(96, 110, 96))
        d.polygon([(int(w * 0.30), int(h * 0.52)), (int(w * 0.38), int(h * 0.60)),
                   (int(w * 0.24), int(h * 0.60))], fill=(240, 238, 230))
    def jet(cx, cy, s, col):
        d.polygon([(cx - s, cy), (cx + s, cy - int(s * 0.28)), (cx + int(s * 0.4), cy + int(s * 0.2)),
                   (cx, cy + int(s * 0.55))], fill=col)
        d.line([(cx - s - int(w * 0.12), cy + 2), (cx - s, cy)], fill=(255, 255, 255), width=3)
    jet(int(w * 0.62), int(h * 0.30), int(w * 0.11), INK)
    jet(int(w * 0.80), int(h * 0.46), int(w * 0.08), (70, 66, 60))
    return img


def v_parliament(size):
    """Parliament building with dome, columns and a crowd."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, int(h * 0.78)], fill=SKY)
    d.rectangle([0, int(h * 0.78), w, h], fill=SAND)
    bx0, bx1 = int(w * 0.18), int(w * 0.82)
    by = int(h * 0.78)
    d.rectangle([bx0, int(h * 0.42), bx1, by], fill=(228, 220, 198))
    d.polygon([(bx0 - 8, int(h * 0.42)), (bx1 + 8, int(h * 0.42)),
               ((bx0 + bx1) // 2, int(h * 0.26))], fill=(196, 182, 148))
    d.pieslice([(bx0 + bx1) // 2 - 22, int(h * 0.10), (bx0 + bx1) // 2 + 22, int(h * 0.10) + 44],
               start=180, end=360, fill=(150, 130, 96))
    d.line([((bx0 + bx1) // 2, int(h * 0.10)), ((bx0 + bx1) // 2, int(h * 0.04))], fill=INK, width=2)
    for i in range(5):
        cx = bx0 + int((i + 0.5) * (bx1 - bx0) / 5)
        d.rectangle([cx - 6, int(h * 0.48), cx + 6, by], fill=(196, 182, 148))
    for i in range(9):  # crowd dots
        cx = int(w * 0.10) + i * int(w * 0.10)
        d.ellipse([cx - 5, int(h * 0.84) - 5, cx + 5, int(h * 0.84) + 5], fill=RED if i % 3 == 0 else INK)
    # flags
    d.line([(int(w * 0.08), int(h * 0.30)), (int(w * 0.08), int(h * 0.78))], fill=INK, width=2)
    d.polygon([(int(w * 0.08), int(h * 0.30)), (int(w * 0.17), int(h * 0.34)), (int(w * 0.08), int(h * 0.38))], fill=RED)
    return img


def v_podium(size):
    """Microphones at a podium with a flag behind."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, h], fill=(222, 228, 226))
    d.rectangle([int(w * 0.08), int(h * 0.12), int(w * 0.34), int(h * 0.52)], fill=RED)
    d.rectangle([int(w * 0.34), int(h * 0.12), int(w * 0.60), int(h * 0.52)], fill=(30, 60, 130))
    d.rectangle([int(w * 0.60), int(h * 0.12), int(w * 0.86), int(h * 0.52)], fill=RED)
    d.polygon([(int(w * 0.34), int(h * 0.66)), (int(w * 0.66), int(h * 0.66)),
               (int(w * 0.60), h), (int(w * 0.40), h)], fill=(70, 60, 48))
    d.line([(int(w * 0.44), int(h * 0.66)), (int(w * 0.40), int(h * 0.44))], fill=INK, width=3)
    d.line([(int(w * 0.56), int(h * 0.66)), (int(w * 0.60), int(h * 0.44))], fill=INK, width=3)
    d.ellipse([int(w * 0.40) - 6, int(h * 0.44) - 8, int(w * 0.40) + 6, int(h * 0.44) + 4], fill=INK)
    d.ellipse([int(w * 0.60) - 6, int(h * 0.44) - 8, int(w * 0.60) + 6, int(h * 0.44) + 4], fill=INK)
    return img


def v_ballot(size):
    """Ballot box with a paper going in."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, h], fill=(224, 230, 238))
    d.rectangle([int(w * 0.24), int(h * 0.42), int(w * 0.76), int(h * 0.90)], fill=RED_DK)
    d.rectangle([int(w * 0.20), int(h * 0.34), int(w * 0.80), int(h * 0.44)], fill=INK)
    d.polygon([(int(w * 0.42), int(h * 0.36)), (int(w * 0.58), int(h * 0.36)),
               (int(w * 0.54), int(h * 0.06)), (int(w * 0.38), int(h * 0.06))], fill=(250, 248, 242))
    d.line([(int(w * 0.43), int(h * 0.16)), (int(w * 0.53), int(h * 0.16))], fill=GRAY, width=2)
    d.line([(int(w * 0.43), int(h * 0.24)), (int(w * 0.53), int(h * 0.24))], fill=GRAY, width=2)
    return img


def v_chip(size):
    """Microchip on a circuit board."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, h], fill=(30, 44, 40))
    for i in range(4):
        y = int(h * (0.18 + i * 0.22))
        d.line([(0, y), (w, y)], fill=(52, 74, 66), width=2)
    cx, cy = w // 2, h // 2
    s = int(min(w, h) * 0.30)
    for i in range(5):
        off = -s + i * (2 * s // 4)
        d.line([(cx + off, cy - s - 10), (cx + off, cy - s)], fill=(180, 190, 180), width=3)
        d.line([(cx + off, cy + s), (cx + off, cy + s + 10)], fill=(180, 190, 180), width=3)
        d.line([(cx - s - 10, cy + off), (cx - s, cy + off)], fill=(180, 190, 180), width=3)
        d.line([(cx + s, cy + off), (cx + s + 10, cy + off)], fill=(180, 190, 180), width=3)
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(18, 110, 82), outline=(220, 225, 215), width=3)
    d.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=(220, 225, 215))
    return img


def v_virus(size):
    """Stylised virus particle on a lab-teal field."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, h], fill=(196, 216, 208))
    cx, cy, r = w // 2, h // 2, int(min(w, h) * 0.26)
    import math
    for k in range(12):
        a = math.pi * 2 * k / 12
        x1, y1 = cx + int(r * 0.9 * math.cos(a)), cy + int(r * 0.9 * math.sin(a))
        x2, y2 = cx + int(r * 1.45 * math.cos(a)), cy + int(r * 1.45 * math.sin(a))
        d.line([(x1, y1), (x2, y2)], fill=(70, 110, 92), width=3)
        d.ellipse([x2 - 5, y2 - 5, x2 + 5, y2 + 5], fill=(70, 110, 92))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 92, 74))
    d.ellipse([cx - r // 2, cy - r // 3, cx - r // 5, cy + r // 6], fill=(120, 165, 145))
    return img


def v_trains(size):
    """Two train fronts on parallel tracks."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, int(h * 0.66)], fill=SKY)
    d.rectangle([0, int(h * 0.66), w, h], fill=(150, 142, 128))
    def train(x0, col, flip):
        tw, th = int(w * 0.34), int(h * 0.52)
        x1 = x0 + tw
        d.rectangle([x0, int(h * 0.14), x1, int(h * 0.14) + th], fill=col)
        d.rectangle([x0 + 8, int(h * 0.22), x1 - 8, int(h * 0.38)], fill=(220, 232, 238))
        d.rectangle([x0, int(h * 0.14) + th - 10, x1, int(h * 0.14) + th], fill=INK)
        d.ellipse([x0 + 10, int(h * 0.14) + th - 26, x0 + 22, int(h * 0.14) + th - 14], fill=(250, 240, 180))
        d.ellipse([x1 - 22, int(h * 0.14) + th - 26, x1 - 10, int(h * 0.14) + th - 14], fill=(250, 240, 180))
    train(int(w * 0.06), RED_DK, False)
    train(int(w * 0.60), (40, 70, 110), True)
    for i in range(6):  # track sleepers
        x = int(w * 0.05) + i * int(w * 0.16)
        d.line([(x, int(h * 0.78)), (x + 14, int(h * 0.78))], fill=(60, 54, 46), width=4)
    d.line([(0, int(h * 0.72)), (w, int(h * 0.72))], fill=INK, width=2)
    return img


def v_cyclone(size, night=False):
    """Cyclone spiral over the sea."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, h], fill=NIGHT if night else SKY)
    d.rectangle([0, int(h * 0.72), w, h], fill=SEA_DK if not night else (24, 34, 52))
    cx, cy = w // 2, int(h * 0.46)
    col = (235, 238, 240) if night else (84, 134, 156)
    for r, a0, a1 in ((52, 20, 200), (40, 140, 320), (28, 260, 80), (16, 60, 240)):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=a0, end=a1, fill=col, width=7)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(244, 214, 150) if night else (240, 200, 130))
    return img


def v_football(size):
    """Football on a pitch with goal lines."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, h], fill=GREEN)
    d.rectangle([int(w * 0.06), int(h * 0.10), int(w * 0.94), int(h * 0.90)], outline=(240, 242, 235), width=3)
    d.line([(w // 2, int(h * 0.10)), (w // 2, int(h * 0.90))], fill=(240, 242, 235), width=2)
    d.ellipse([w // 2 - 16, h // 2 - 16, w // 2 + 16, h // 2 + 16], outline=(240, 242, 235), width=2)
    cx, cy, r = int(w * 0.68), int(h * 0.62), 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(248, 248, 244), outline=INK, width=2)
    import math
    pts = []
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        pts.append((cx + int(r * 0.55 * math.cos(a)), cy + int(r * 0.55 * math.sin(a))))
    d.polygon(pts, fill=INK)
    for px, py in pts:
        d.line([(px, py), (cx + int((px - cx) * 1.7), cy + int((py - cy) * 1.7))], fill=INK, width=2)
    return img


def v_space(size):
    """Spacecraft with dish antenna against stars."""
    img, d = _clip_scene(size)
    w, h = size
    d.rectangle([0, 0, w, h], fill=(16, 22, 38))
    stars = [(0.12, 0.20), (0.30, 0.12), (0.52, 0.22), (0.78, 0.14), (0.88, 0.38),
             (0.20, 0.52), (0.42, 0.70), (0.66, 0.62), (0.85, 0.72), (0.08, 0.80),
             (0.36, 0.86), (0.58, 0.88), (0.94, 0.55), (0.24, 0.34)]
    for fx, fy in stars:
        x, y = int(w * fx), int(h * fy)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(240, 240, 220))
    cx, cy = int(w * 0.46), int(h * 0.52)
    d.rectangle([cx - 34, cy - 6, cx + 10, cy + 6], fill=(200, 205, 210))
    d.polygon([(cx + 10, cy - 14), (cx + 34, cy), (cx + 10, cy + 14)], fill=(228, 222, 190))
    d.line([(cx - 34, cy), (cx - 52, cy - 18)], fill=(200, 205, 210), width=3)
    d.line([(cx - 20, cy - 6), (cx - 20, cy - 26)], fill=(200, 205, 210), width=2)
    d.ellipse([cx - 23, cy - 32, cx - 17, cy - 26], fill=(244, 214, 150))
    return img


# ---------------- world map ----------------
# Simplified continent outlines (lon/lat), equirectangular projection.

CONTINENTS = [
    # North America
    [(-165, 60), (-150, 61), (-140, 60), (-132, 56), (-125, 49), (-124, 40),
     (-117, 33), (-110, 24), (-105, 20), (-97, 16), (-92, 14), (-87, 13),
     (-83, 9), (-79, 9), (-81, 13), (-86, 16), (-88, 18), (-87, 21), (-90, 21),
     (-93, 18), (-97, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 26),
     (-80, 32), (-75, 37), (-71, 41), (-67, 45), (-60, 47), (-55, 48), (-59, 52),
     (-64, 58), (-68, 56), (-75, 60), (-82, 64), (-90, 67), (-100, 68),
     (-112, 68), (-122, 70), (-135, 69), (-148, 70), (-158, 71), (-165, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-42, 60), (-32, 68), (-22, 70), (-25, 76),
     (-40, 80), (-55, 78), (-62, 74), (-60, 70)],
    # South America
    [(-79, 9), (-76, 10), (-72, 12), (-64, 10), (-60, 8), (-53, 5), (-51, 4),
     (-50, 0), (-44, -3), (-35, -8), (-37, -13), (-40, -20), (-46, -24),
     (-49, -28), (-54, -33), (-58, -38), (-62, -41), (-66, -45), (-68, -50),
     (-70, -53), (-74, -52), (-73, -44), (-72, -36), (-70, -23), (-70, -18),
     (-75, -15), (-78, -8), (-81, -4), (-80, 1)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-5, 48), (-1, 50),
     (2, 51), (5, 53), (8, 55), (8, 57), (11, 58), (13, 56), (18, 56), (21, 58),
     (24, 60), (28, 61), (30, 62), (28, 66), (32, 70), (40, 68), (45, 66),
     (48, 62), (44, 58), (40, 56), (36, 54), (32, 52), (30, 48), (29, 45),
     (28, 44), (23, 40), (22, 37), (20, 40), (18, 42), (16, 40), (14, 42),
     (12, 44), (10, 44), (8, 44), (6, 43), (3, 42), (0, 39), (-2, 37), (-6, 36)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-4, 58), (-2, 57), (0, 54), (1, 51), (-2, 50)],
    # Africa
    [(-17, 15), (-16, 20), (-13, 27), (-9, 32), (-5, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (30, 31), (32, 31), (34, 28), (36, 24), (38, 20),
     (40, 15), (43, 12), (48, 11), (51, 12), (48, 5), (42, -1), (40, -6),
     (39, -12), (37, -18), (35, -22), (33, -26), (30, -31), (26, -33),
     (20, -35), (17, -32), (15, -27), (13, -22), (12, -17), (13, -12), (9, -1),
     (9, 4), (4, 6), (-3, 5), (-8, 5), (-13, 8), (-17, 12)],
    # Madagascar
    [(44, -16), (47, -15), (50, -17), (49, -22), (47, -25), (44, -22), (43, -18)],
    # Asia
    [(28, 41), (30, 46), (34, 48), (38, 50), (42, 52), (46, 54), (48, 58),
     (44, 62), (40, 66), (38, 70), (45, 70), (55, 69), (65, 69), (72, 72),
     (80, 73), (90, 75), (100, 76), (110, 74), (120, 73), (130, 72), (140, 72),
     (150, 70), (158, 69), (162, 66), (170, 66), (178, 65), (178, 62),
     (170, 60), (162, 60), (158, 55), (156, 50), (150, 46), (142, 44), (140, 39),
     (135, 35), (130, 33), (127, 34), (122, 31), (120, 27), (114, 22), (109, 18),
     (105, 9), (103, 7), (100, 9), (99, 12), (97, 16), (94, 18), (91, 22),
     (88, 22), (86, 20), (82, 16), (80, 13), (77, 8), (75, 12), (73, 16),
     (70, 21), (67, 25), (63, 25), (59, 26), (56, 27), (54, 27), (52, 28),
     (49, 30), (46, 30), (42, 31), (39, 32), (36, 36), (33, 36), (30, 36), (28, 38)],
    # Japan
    [(130, 31), (132, 33), (135, 35), (138, 37), (141, 39), (142, 42),
     (144, 44), (141, 45), (139, 41), (136, 36), (133, 34), (130, 32)],
    # Indonesia
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
     (131, -3), (136, -2), (141, -4), (141, -8), (136, -8), (130, -7),
     (124, -9), (118, -9), (112, -8), (106, -6), (100, -1), (95, 2)],
    # Philippines
    [(120, 18), (122, 17), (124, 14), (126, 11), (124, 7), (121, 7), (119, 10), (120, 14)],
    # Australia
    [(113, -22), (114, -28), (116, -32), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (143, -39), (146, -38),
     (150, -37), (153, -32), (153, -27), (151, -23), (149, -20), (146, -19),
     (143, -17), (142, -11), (140, -17), (136, -15), (135, -12), (132, -11),
     (130, -12), (126, -14), (122, -17), (118, -20), (114, -21)],
    # New Zealand
    [(172, -35), (175, -37), (178, -38), (176, -41), (173, -42), (170, -44),
     (167, -46), (168, -43), (171, -40), (173, -37)],
]

# (lon, lat, dot-offset, legend label) — 16 pins, six continents
PINS = [
    (-152, 62, (0, -7), "Alaska — Senate race"),
    (-72, 19, (7, 4), "Haiti — UN toll"),
    (-48, -16, (0, 8), "Brazil — 7–0 win"),
    (0, 51.5, (-9, -7), "London — sanctions"),
    (2.4, 48.8, (9, 6), "Paris — strike"),
    (30.5, 50.4, (2, -9), "Kyiv — bridges hit"),
    (20.5, 44.8, (-8, 8), "Belgrade — new MPs"),
    (35.2, 31.8, (8, -4), "Jerusalem — speaker vote"),
    (56, 27, (8, 4), "Qeshm — US strike"),
    (45, 12.8, (9, 7), "Aden — troops mass"),
    (32.5, 15.6, (-6, 8), "Sudan — UN toll"),
    (23, -2, (0, 9), "DR Congo — Ebola"),
    (107, 48, (7, -7), "Mongolia — president to quit"),
    (130, 34, (9, 0), "Japan — airspace"),
    (121, 14.6, (-9, 5), "Manila — Quad summit"),
    (-160, -21, (0, -9), "Cook Is. — cyclone"),
]


def draw_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=SEA, outline=RULE, width=1)
    lon_min, lon_max, lat_max, lat_min = -170, 190, 82, -58

    def proj(lon, lat):
        x = x0 + (lon - lon_min) / (lon_max - lon_min) * (x1 - x0)
        y = y0 + (lat_max - lat) / (lat_max - lat_min) * (y1 - y0)
        return x, y

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    num_font = font(SANS_BOLD, 9)
    for i, (lon, lat, (dx, dy), _label) in enumerate(PINS, 1):
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        if dx or dy:
            d.line([(px, py), (cx, cy)], fill=RED, width=1)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED, outline=(255, 255, 255), width=1)
        t = str(i)
        tw = d.textlength(t, font=num_font)
        d.text((cx - tw / 2, cy - 5), t, font=num_font, fill=(255, 255, 255))
    return proj


# ---------------- story data (all verified in-session, 17 Nov 2026) ----------------

FIGURES = [
    ("1,441", "drones Russia says it downed"),
    ("$115.8B", "Nvidia revenue, up 103%"),
    ("2,230", "verified Sudan deaths, Jan–Oct"),
    ("4,595", "killed in Haiti this year"),
    ("11,000+", "WHO: Ebola cases in DR Congo"),
    ("56–44", "Peltola's margin in Alaska"),
]

LEADS = [
    ("UKRAINE WAR", "Bridge to Crimea brought down in the night",
     "Ukraine says drones and missiles dropped the road arch into the sea; "
     "Russia says two people were killed.", v_bridge),
    ("THE GULF", "US jets strike Iranian missile site on Qeshm",
     "US jets hit an IRGC missile launch site late on Tuesday, after drone "
     "attacks on Bahrain. Iran confirmed it was hit.", v_jets),
    ("SERBIA", "Students take power, ending 14 years of Vučić rule",
     "140 of 250 MPs were sworn in at the first sitting. A new government "
     "must form within 90 days.", v_parliament),
]

CARDS = [
    ("Suspected Russian jets enter Japan's airspace", lambda s: v_jets(s, island=True)),
    ("Mongolia's president says he will resign", v_podium),
    ("Peltola wins Alaska Senate seat for Democrats", v_ballot),
    ("Nvidia's record quarter; board says no to Huang", v_chip),
    ("Ebola passes 11,000 cases in DR Congo", v_virus),
    ("Two trains collide in Prague; 46 hurt", v_trains),
    ("Cyclone Akvan strengthens in Bay of Bengal", lambda s: v_cyclone(s, night=False)),
    ("Cyclone Xavier reaches Category 5", lambda s: v_cyclone(s, night=True)),
    ("Vinícius hat-trick as Brazil rout Singapore 7–0", v_football),
    ("World flashes lights for Voyager 1", v_space),
]

BRIEFS = [
    ("RAMSTEIN", "Belgium 10 F-16s, France 2 Mirages"),
    ("QUAD", "Leaders meet in Manila; minerals and AI deals"),
    ("CANADA–CHINA", "Tariff relief on C$400M of goods"),
    ("MEASLES", "US, Mexico, Bolivia lose status"),
    ("COP31", "Ministers take over as draft deal draws fire"),
    ("MOZAMBIQUE", "Mondlane trial opens; denies charges"),
    ("FRANCE", "Strike and marches for higher pay"),
    ("DEUTSCHE BANK", "Shares slide on 15m leaked files"),
    ("SAFF FINAL", "India beat Pakistan 2–1 in Dhaka"),
    ("KYIV", "Russian missiles strike two Dnipro bridges"),
    ("N. MACEDONIA", "Alleged murder plot foiled; 5 held"),
    ("KIM MEETING", "Putin could meet Kim at APEC"),
    ("NSA", "Internal network goes down; 'no cyberattack'"),
    ("HORMONE CHEMICALS", "UN: costs top $1.1T a year"),
    ("RWANDA PLAN", "UN warns over return-hub plan"),
    ("AN-12 CRASH", "Russian transport down; all 19 killed"),
    ("POLAND", "Tusk survives no-confidence vote, 242–200"),
    ("SUDAN", "Drones caused 1,630+ of 2,230 deaths"),
    ("APPLE", "Outage hits iCloud, Pay; update blamed"),
    ("UK SANCTIONS", "8 firms and Tzav 9 named"),
    ("YEMEN", "Troops mass near Aden, AP reports"),
    ("HAITI", "UN counts 4,595 killed in violence this year"),
    ("MOLDOVA", "Airspace shut as 7 drones cross its skies"),
    ("BANDA SEA", "M6.6 quake; no tsunami threat"),
    ("KNESSET", "Kahana elected speaker, 66–52"),
    ("SÖZCÜ TV", "Turkey raids channel, appoints trustee"),
    ("TOGO", "Stun Algeria 3–0 in AFCON qualifier"),
    ("KENYA", "WFP feeds 30,000 who fled Ethiopia clashes"),
]

FOOTER_SOURCES = ("Sources: Reuters · AP · AFP · UN News · OHCHR · UNICEF · WHO · UNEP · IMD · "
                  "Fiji Met · CNA · Le Monde · Kyiv Independent · Times of Israel · Haaretz · "
                  "Al Jazeera · USA TODAY")
FOOTER_NOTE = ("Every story here happened or was first reported on Tuesday 17 November 2026. "
               "Contested claims are marked as claims; figures are as reported by the sources named.")


# ---------------- layout ----------------

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 28  # side margin
    CW = W - 2 * MX  # content width 968

    # --- top strip ---
    strip_f = font(SANS_BOLD, 13)
    y = 8
    tracked(d, (MX, y), "THE WORLD'S NEWS IN ONE PICTURE", strip_f, INK, tracking=1)
    right = "41 STORIES · SIX CONTINENTS"
    rw = tracked_width(d, right, strip_f, tracking=1)
    tracked(d, (W - MX - rw, y), right, strip_f, INK, tracking=1)
    d.line([(MX, 30), (W - MX, 30)], fill=RULE, width=2)

    # --- masthead ---
    title = "TUESDAY 17 NOVEMBER 2026"
    size = 60
    while size > 30:
        tf = font(SERIF_BLACK, size)
        if d.textlength(title, font=tf) <= CW:
            break
        size -= 2
    tf = font(SERIF_BLACK, size)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 34), title, font=tf, fill=INK)
    sub = "One day, six continents — the world as it happened on Tuesday."
    sf = font(SANS, 14)
    sw = d.textlength(sub, font=sf)
    d.text(((W - sw) / 2, 100), sub, font=sf, fill=GRAY)

    # --- figures strip ---
    fy0, fy1 = 124, 174
    d.line([(MX, fy0), (W - MX, fy0)], fill=RULE, width=1)
    d.line([(MX, fy1), (W - MX, fy1)], fill=RULE, width=1)
    nfig = len(FIGURES)
    fw = CW / nfig
    num_f = font(SERIF_BOLD, 21)
    lab_f = font(SANS, 10)
    for i, (num, lab) in enumerate(FIGURES):
        x0 = MX + i * fw
        if i:
            d.line([(x0, fy0 + 5), (x0, fy1 - 5)], fill=(190, 182, 164), width=1)
        d.text((x0 + 8, fy0 + 4), num, font=num_f, fill=RED_DK)
        for j, line in enumerate(wrap(d, lab, lab_f, fw - 16)):
            d.text((x0 + 8, fy0 + 28 + j * 12), line, font=lab_f, fill=GRAY)

    # --- three leads ---
    ly0 = 182
    gap = 16
    lw = (CW - 2 * gap) / 3
    kick_f = font(SANS_BOLD, 11)
    head_f = font(SERIF_BOLD, 21)
    deck_f = font(SANS, 12)
    for i, (kicker, head, deck, vign) in enumerate(LEADS):
        x0 = MX + i * (lw + gap)
        x1 = x0 + lw
        vig = vign((int(lw), 118))
        img.paste(vig, (int(x0), ly0))
        d.rectangle([int(x0), ly0, int(x1) - 1, ly0 + 117], outline=RULE, width=1)
        ky = ly0 + 124
        tracked(d, (int(x0), ky), kicker, kick_f, RED, tracking=1)
        hy = ky + 16
        lines = wrap(d, head, head_f, lw)
        for j, line in enumerate(lines[:3]):
            d.text((int(x0), hy + j * 24), line, font=head_f, fill=INK)
        dy = hy + len(lines[:3]) * 24 + 3
        for j, line in enumerate(wrap(d, deck, deck_f, lw)[:3]):
            d.text((int(x0), dy + j * 15), line, font=deck_f, fill=(58, 54, 46))

    # --- ten small cards: 5 x 2 ---
    cy0 = 436
    cgap = 10
    cw = (CW - 4 * cgap) / 5
    ch = 96
    card_f = font(SERIF_BOLD, 13)
    for i, (head, vign) in enumerate(CARDS):
        row, col = divmod(i, 5)
        x0 = MX + col * (cw + cgap)
        y0 = cy0 + row * (ch + 6)
        vig = vign((int(cw), 46))
        img.paste(vig, (int(x0), y0))
        d.rectangle([int(x0), y0, int(x0 + cw) - 1, y0 + 45], outline=RULE, width=1)
        for j, line in enumerate(wrap(d, head, card_f, cw - 2)[:2]):
            d.text((int(x0), y0 + 50 + j * 16), line, font=card_f, fill=INK)

    # --- map + legend ---
    my0 = 646
    sec_f = font(SANS_BOLD, 12)
    tracked(d, (MX, my0), "WHERE IT HAPPENED", sec_f, INK, tracking=1)
    leg_head = "16 PLACES · SIX CONTINENTS"
    lw_ = tracked_width(d, leg_head, sec_f, tracking=1)
    map_w = 560
    leg_x = MX + map_w + 18
    tracked(d, (leg_x, my0), leg_head, sec_f, INK, tracking=1)
    map_box = (MX, my0 + 18, MX + map_w, my0 + 18 + 104)
    draw_map(d, map_box)
    leg_f = font(SANS, 11)
    leg_b = font(SANS_BOLD, 11)
    col_w = (W - MX - leg_x) / 2
    for i, (_lon, _lat, _off, label) in enumerate(PINS):
        col, row = divmod(i, 8)
        lx = leg_x + col * col_w
        ly = my0 + 20 + row * 13
        num = f"{i + 1}."
        d.text((lx, ly), num, font=leg_b, fill=RED_DK)
        nw = d.textlength(num + " ", font=leg_b)
        d.text((lx + nw, ly), label, font=leg_f, fill=INK)

    # --- briefs ---
    by0 = 788
    tracked(d, (MX, by0), "ALSO ON TUESDAY 17 NOVEMBER", sec_f, INK, tracking=1)
    d.line([(MX, by0 + 18), (W - MX, by0 + 18)], fill=RULE, width=1)
    bcol_w = (CW - 2 * 16) / 3
    brief_b = font(SANS_BOLD, 11.5)
    brief_f = font(SANS, 11.5)
    per_col = [10, 9, 9]
    idx = 0
    for col in range(3):
        x0 = MX + col * (bcol_w + 16)
        for row in range(per_col[col]):
            lead, rest = BRIEFS[idx]
            idx += 1
            y = by0 + 22 + row * 17
            d.rectangle([x0, y + 4, x0 + 5, y + 9], fill=RED)
            tx = x0 + 10
            lead_t = lead + " — "
            avail = bcol_w - 10 - d.textlength(lead_t, font=brief_b)
            if d.textlength(rest, font=brief_f) > avail:
                rest = fit_text(d, rest, brief_f, avail)
            d.text((tx, y), lead_t, font=brief_b, fill=INK)
            d.text((tx + d.textlength(lead_t, font=brief_b), y), rest, font=brief_f, fill=(58, 54, 46))

    # --- footer ---
    d.line([(MX, 984), (W - MX, 984)], fill=RULE, width=1)
    foot_f = font(SANS, 10)
    for j, line in enumerate([FOOTER_SOURCES, FOOTER_NOTE]):
        lw2 = d.textlength(line, font=foot_f)
        d.text(((W - lw2) / 2, 990 + j * 14), line, font=foot_f, fill=GRAY)

    img.save(OUT, optimize=True)
    return OUT


if __name__ == "__main__":
    out = build()
    import os as _os
    print(out, _os.path.getsize(out), "bytes")
