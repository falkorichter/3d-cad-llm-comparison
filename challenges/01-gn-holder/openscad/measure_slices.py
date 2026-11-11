#!/usr/bin/env python3
"""Measure the derived sizes on horizontal cuts of the assembled frame + legs (no dividers).

The cuts come from `openscad -D 'part="slice"' -D slice_z=Z -o zZ.svg gn_holder.scad`.
usage: python3 measure_slices.py DIR   (DIR holds z<Z>.svg files)
"""
import glob
import os
import re
import sys


def loops(path):
    d = re.search(r'd="(.*?)"', open(path).read(), re.S).group(1)
    out = []
    for part in d.split("M")[1:]:
        pts = [tuple(map(float, p.split(","))) for p in re.findall(r"-?[\d.e+-]+,-?[\d.e+-]+", part)]
        out.append([(x, -y) for x, y in pts])  # SVG y is flipped
    return out


def edges(ls):
    for lp in ls:
        for i in range(len(lp)):
            yield lp[i], lp[(i + 1) % len(lp)]


def hits_x(ls, y):
    """x where the horizontal line at y crosses an edge"""
    r = []
    for (x1, y1), (x2, y2) in edges(ls):
        if (y1 - y) * (y2 - y) < 0:
            r.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    return sorted(r)


def span(h, c=0.0):
    """free span around c on a line: nearest crossing on each side"""
    lo = max(v for v in h if v < c)
    hi = min(v for v in h if v > c)
    return hi - lo, lo, hi


def inside_box(ls, hx, hy):
    """True if any vertex or edge of the cut enters the open box |x|<hx, |y|<hy"""
    for (x1, y1), (x2, y2) in edges(ls):
        for t in [i / 50 for i in range(51)]:
            x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
            if abs(x) < hx - 1e-6 and abs(y) < hy - 1e-6:
                return True
    return False


def main(d):
    files = sorted(glob.glob(os.path.join(d, "z*.svg")), key=lambda f: float(os.path.basename(f)[1:-4]))
    for f in files:
        z = float(os.path.basename(f)[1:-4])
        ls = loops(f)
        hx = hits_x(ls, 40.0)                                       # line y = 40 (away from joints and seats)
        hy = hits_x([[(y, x) for x, y in lp] for lp in ls], 40.0)   # line x = 40, measured along y
        pts = [p for lp in ls for p in lp]
        outer = (max(p[0] for p in pts) - min(p[0] for p in pts), max(p[1] for p in pts) - min(p[1] for p in pts))
        inner = (span(hx)[0], span(hy)[0]) if len(hx) > 2 else None
        pan = inside_box(ls, 505 / 2, 300 / 2)
        print(f"z={z:6.1f}  outer {outer[0]:6.1f} x {outer[1]:6.1f}  "
              f"inner {'%6.1f x %6.1f' % inner if inner else '   (legs only)   '}  "
              f"geometry inside pan body 505x300: {'YES' if pan else 'no'}")


if __name__ == "__main__":
    main(sys.argv[1])
