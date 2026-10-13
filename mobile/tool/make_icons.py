"""Generate launcher icons (mipmap PNGs) for the Android app.

Pure standard library (struct/zlib/binascii). Re-run any time:
    python mobile/tool/make_icons.py <mobile-dir>

Design: night-signals — deep ink background, phosphor-teal cipher-node
grid, one signal-amber bar. Abstract, no clichés.
"""
import binascii
import struct
import sys
import zlib
from pathlib import Path

BG = (10, 14, 20)        # #0A0E14 ink
TEAL = (95, 227, 192)    # #5FE3C0 phosphor teal
AMBER = (224, 168, 62)   # #E0A83E signal amber

DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96,
             "xxhdpi": 144, "xxxhdpi": 192}


def chunk(typ, data):
    c = typ + data
    return struct.pack(">I", len(data)) + c + struct.pack(
        ">I", binascii.crc32(c) & 0xFFFFFFFF)


def write_png(path, pixels):
    h = len(pixels)
    w = len(pixels[0])
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row)
                   for row in pixels)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    path.write_bytes(png)


def icon(size):
    px = [[BG for _ in range(size)] for _ in range(size)]
    # cipher-node dot grid
    cols, rows = 4, 5
    mx, my = size * 0.20, size * 0.16
    dx = (size - 2 * mx) / (cols - 1)
    dy = (size - 2 * my) / (rows - 1)
    r = size * 0.032
    for ci in range(cols):
        for ri in range(rows):
            cx, cy = mx + ci * dx, my + ri * dy
            for y in range(size):
                for x in range(size):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                        px[y][x] = TEAL
    # signal-amber bar across the middle row
    y0 = int(size * 0.46)
    y1 = int(size * 0.54)
    x0 = int(size * 0.14)
    x1 = int(size * 0.86)
    for y in range(y0, y1):
        for x in range(x0, x1):
            px[y][x] = AMBER
    return px


def main():
    mobile = Path(sys.argv[1])
    for name, size in DENSITIES.items():
        d = (mobile / "android" / "app" / "src" / "main" / "res"
             / f"mipmap-{name}")
        d.mkdir(parents=True, exist_ok=True)
        write_png(d / "ic_launcher.png", icon(size))
        print(f"wrote {d / 'ic_launcher.png'} ({size}x{size})")


if __name__ == "__main__":
    main()
