#!/usr/bin/env python3
"""Thursday, 26 November 2026 -- world news in one image.

Pure-stdlib poster renderer: draws a 1024x1024 front page with six stories
from 26 November 2026 and writes it to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png). No network, no local imports, no clock,
no randomness: two runs produce byte-identical output.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import base64
import os
import struct
import zlib

# ---------------------------------------------------------------------------
# Bitmap fonts (1-bit glyphs rendered from DejaVu Sans in this build session).
# Each blob packs 96 glyphs (printable ASCII + U+00B7) as: 1 width byte,
# then ceil(width * GLYPH_H / 8) bitmap bytes, row-major, MSB first.
# ---------------------------------------------------------------------------
GLYPH_H = 19

REG_B64 = (
        "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"
    "AAAAAAUAAAAAACEAAAAAAAA="
)

BOLD_B64 = (
        "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"
)


def _unpack_font(b64):
    raw = base64.b64decode(b64)
    glyphs = []
    i = 0
    while i < len(raw):
        w = raw[i]
        i += 1
        n = (w * GLYPH_H + 7) // 8
        glyphs.append((w, raw[i:i + n]))
        i += n
    return glyphs


REG = _unpack_font(REG_B64)
BOLD = _unpack_font(BOLD_B64)
N_GLYPHS = 96  # chars 32..126 then U+00B7


def _glyph_index(ch):
    if ch == "\u00b7":
        return 95
    o = ord(ch)
    if 32 <= o <= 126:
        return o - 32
    return 0  # unknown -> space


# ---------------------------------------------------------------------------
# Canvas: plain RGB bytearray + tiny rasterizer.
# ---------------------------------------------------------------------------
W, H = 1024, 1024


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:(i + (x1 - x0) * 3)] = color * (x1 - x0)

    def rect(self, x, y, w, h, color):
        self.fill_rect(x, y, w, 1, color)
        self.fill_rect(x, y + h - 1, w, 1, color)
        self.fill_rect(x, y, 1, h, color)
        self.fill_rect(x + w - 1, y, 1, h, color)

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        # Midpoint circle outline.
        x = 0
        y = r
        d = 1 - r
        while x <= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.set(cx + sx, cy + sy, color)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def ellipse(self, cx, cy, rx, ry, color):
        # Parametric ellipse outline, sampled densely enough to look solid.
        import math
        steps = max(48, int(2 * math.pi * max(rx, ry)))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            self.set(int(cx + rx * math.cos(a)),
                     int(cy + ry * math.sin(a)), color)

    def disc(self, cx, cy, r, color):
        for yy in range(-r, r + 1):
            half = int((r * r - yy * yy) ** 0.5)
            self.fill_rect(cx - half, cy + yy, 2 * half + 1, 1, color)


# ---------------------------------------------------------------------------
# Text: blit scaled glyph bitmaps, with word wrap.
# ---------------------------------------------------------------------------
def text_width(text, font, scale):
    total = 0
    for ch in text:
        total += font[_glyph_index(ch)][0] * scale
    return total


def draw_text(cv, x, y, text, font, scale, color, tracking=0):
    cx = x
    for ch in text:
        w, bits = font[_glyph_index(ch)]
        bit = 0
        for gy in range(GLYPH_H):
            for gx in range(w):
                byte = bits[bit // 8]
                on = (byte >> (7 - bit % 8)) & 1
                bit += 1
                if on:
                    cv.fill_rect(cx + gx * scale, y + gy * scale,
                                 scale, scale, color)
        cx += w * scale + tracking
    return cx


def wrap_text(text, font, scale, max_width):
    """Greedy word wrap; returns a list of lines."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, font, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, text, font, scale, color, max_width,
                 max_lines, line_gap):
    lines = wrap_text(text, font, scale, max_width)[:max_lines]
    for i, line in enumerate(lines):
        draw_text(cv, x, y + i * (GLYPH_H * scale + line_gap),
                  line, font, scale, color)
    return len(lines)


def mix(a, b, t):
    """Blend color a toward b by t (0..1)."""
    return bytes(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------------------
# Palette and content.
# ---------------------------------------------------------------------------
BG = bytes((12, 22, 38))        # deep navy
CARD = bytes((22, 38, 63))      # card navy
CARD_LINE = bytes((42, 63, 95))  # card border
GOLD = bytes((217, 164, 65))    # accent gold
WHITE = bytes((245, 241, 232))  # warm white
BODY = bytes((199, 208, 221))   # light grey-blue
MUTED = bytes((138, 151, 168))  # muted grey-blue
INK = bytes((12, 22, 38))       # dark text on chips

STORIES = [
    ("TRADE", bytes((228, 87, 46)), "AP",
     "US unveils sweeping new tariffs",
     "Washington hits China, the EU and Brazil with new duties on subsidised goods."),
    ("ENERGY", bytes((217, 164, 65)), "Reuters",
     "Houthis claim Saudi refinery hit",
     "Brent crude jumps 3.5% to $94.61; Riyadh says it shot down four drones."),
    ("WAR", bytes((178, 58, 72)), "BBC",
     "Russia's war dead near 500,000",
     "Leaked Rosstat records analysed by the BBC count 490,334 soldiers dead."),
    ("EGYPT", bytes((224, 123, 57)), "AP",
     "Cairo tanker inferno kills 31",
     "A fuel tanker overturns on the Ring Road; 21 more people are injured."),
    ("SPACE", bytes((91, 141, 239)), "ESA",
     "Hera shows asteroid's scarred face",
     "First close-ups reveal a stadium-sized crater and a tumbling Dimorphos."),
    ("RESCUE", bytes((46, 158, 107)), "BBC",
     "Colombia police free 20 hostages",
     "Officers storm a supermarket to end a 17-hour siege and free 20 people."),
]


def draw_globe(cv, cx, cy, r, color):
    cv.circle(cx, cy, r, color)
    cv.circle(cx, cy, r - 1, color)
    cv.ellipse(cx, cy, int(r * 0.45), r, color)
    cv.ellipse(cx, cy, int(r * 0.80), r, color)
    # Latitude chords, clipped inside the circle.
    for fy, frac in ((-0.55, 0.55), (0.0, 0.0), (0.55, 0.55)):
        yy = int(cy + fy * r)
        half = int((r * r - (yy - cy) ** 2) ** 0.5)
        cv.hline(cx - half, yy, 2 * half + 1, color)
    # Small marker dot for the day's hot spot.
    cv.disc(cx + int(r * 0.30), cy - int(r * 0.42), 4, GOLD)


def draw_poster():
    cv = Canvas(W, H, BG)

    # Header.
    draw_text(cv, 48, 46, "THE WORLD IN ONE IMAGE", BOLD, 1, GOLD, tracking=3)
    draw_text(cv, 48, 76, "Thursday, 26 November 2026", BOLD, 2, WHITE)
    draw_text(cv, 48, 128,
              "Trade wars, oil shocks, a war toll, a rescue -- and a scarred asteroid.",
              REG, 1, MUTED)
    draw_globe(cv, 908, 100, 52, GOLD)
    cv.fill_rect(48, 168, 928, 3, GOLD)

    # Story grid: 2 columns x 3 rows.
    x0, y0 = 48, 196
    cw, chh, gx, gy = 454, 245, 20, 18
    for i, (tag, accent, source, headline, summary) in enumerate(STORIES):
        col = i % 2
        row = i // 2
        x = x0 + col * (cw + gx)
        y = y0 + row * (chh + gy)
        cv.fill_rect(x, y, cw, chh, CARD)
        cv.rect(x, y, cw, chh, CARD_LINE)
        cv.fill_rect(x, y, 6, chh, accent)

        # Ghost number, top right, blended toward the card colour.
        num = "%02d" % (i + 1)
        ghost = mix(accent, CARD, 0.72)
        draw_text(cv, x + cw - 20 - text_width(num, BOLD, 3),
                  y + 10, num, BOLD, 3, ghost)

        # Tag chip.
        chip_w = text_width(tag, BOLD, 1) + 20
        cv.fill_rect(x + 20, y + 18, chip_w, 28, accent)
        draw_text(cv, x + 30, y + 24, tag, BOLD, 1, INK)

        # Headline, bold, up to 2 lines.
        n = draw_wrapped(cv, x + 20, y + 62, headline, BOLD, 2, WHITE,
                         cw - 40, 2, 6)
        # Summary, regular, up to 2 lines.
        sy = y + 62 + n * (GLYPH_H * 2 + 6) + 12
        draw_wrapped(cv, x + 20, sy, summary, REG, 1, BODY,
                     cw - 40, 2, 5)

        # Source line, pinned to the card's bottom edge.
        draw_text(cv, x + 20, y + chh - 36, "Source: " + source,
                  REG, 1, MUTED)

    # Footer.
    cv.fill_rect(48, 964, 928, 1, CARD_LINE)
    draw_text(cv, 48, 980, "Sources: AP · Reuters · BBC · ESA · CNN",
              REG, 1, MUTED)
    right = "26 November 2026"
    draw_text(cv, 976 - text_width(right, BOLD, 1), 980,
              right, BOLD, 1, GOLD)
    return cv


# ---------------------------------------------------------------------------
# Minimal deterministic PNG writer (truecolour, filter 0).
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(draw_poster(), path)
    print("wrote " + path)


if __name__ == "__main__":
    main()
