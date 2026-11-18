#!/usr/bin/env python3
"""Generate PWA icons: warm cream field, accent loaf with scoring slashes."""
import zlib, struct, math

CREAM = (247, 243, 236)
ACCENT = (164, 86, 43)
DARK = (140, 70, 35)

def blend(bg, fg, a):
    return tuple(int(round(b + (f - b) * a)) for b, f in zip(bg, fg))

def loaf_alpha(x, y):
    """x,y in 0..1. Returns coverage of the loaf body."""
    # body: ellipse, centre 0.5/0.545, radii 0.315/0.205
    cx, cy, rx, ry = 0.5, 0.545, 0.315, 0.205
    d = math.hypot((x - cx) / rx, (y - cy) / ry)
    # flat-ish bottom: squash lower half slightly
    if y > cy:
        d = math.hypot((x - cx) / rx, (y - cy) / (ry * 0.88))
    return 1.0 if d <= 1 else 0.0

def slash_alpha(x, y, cx, cy, length, thick, angle_deg):
    ang = math.radians(angle_deg)
    dx, dy = x - cx, y - cy
    u = dx * math.cos(ang) + dy * math.sin(ang)
    v = -dx * math.sin(ang) + dy * math.cos(ang)
    if abs(u) > length / 2:
        return 0.0
    # taper toward the ends
    t = 1 - (abs(u) / (length / 2)) ** 2
    return 1.0 if abs(v) <= (thick / 2) * t else 0.0

SLASHES = [
    (0.395, 0.470, 0.115, 0.036, -58),
    (0.505, 0.455, 0.125, 0.040, -58),
    (0.615, 0.470, 0.115, 0.036, -58),
]

def shade(x, y):
    """Return RGB for a supersample point."""
    col = CREAM
    if loaf_alpha(x, y):
        # subtle vertical gradient on the crust
        g = min(1.0, max(0.0, (y - 0.34) / 0.42))
        col = blend(ACCENT, DARK, g * 0.35)
        for s in SLASHES:
            if slash_alpha(x, y, *s):
                col = CREAM
    return col

def render(size, ss=4):
    rows = []
    inv = 1.0 / (size * ss)
    for py in range(size):
        row = bytearray()
        for px in range(size):
            r = g = b = 0
            for sy in range(ss):
                for sx in range(ss):
                    x = (px * ss + sx + 0.5) * inv
                    y = (py * ss + sy + 0.5) * inv
                    c = shade(x, y)
                    r += c[0]; g += c[1]; b += c[2]
            n = ss * ss
            row += bytes((r // n, g // n, b // n))
        rows.append(bytes(row))
    return rows

def write_png(path, size, ss=4):
    rows = render(size, ss)
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    print(f"{path}  {size}x{size}  {len(png)/1024:.1f} KB")

write_png("icon-512.png", 512, ss=4)
write_png("icon-192.png", 192, ss=6)
write_png("apple-touch-icon.png", 180, ss=6)
