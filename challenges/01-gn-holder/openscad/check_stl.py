#!/usr/bin/env python3
"""Bounding box, volume and bed-fit check for ASCII/binary STL files (numpy only).

usage: python3 check_stl.py [--bed 256 256] file.stl ...
"""
import struct
import sys

import numpy as np


def load(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:1000]:
        v = [list(map(float, ln.split()[1:4])) for ln in data.decode().splitlines() if ln.strip().startswith("vertex")]
        return np.array(v).reshape(-1, 3, 3)
    n = struct.unpack("<I", data[80:84])[0]
    a = np.frombuffer(data[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(float)


def volume(t):
    return np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6.0


def main(argv):
    bed = (256.0, 256.0)
    if argv[:1] == ["--bed"]:
        bed = (float(argv[1]), float(argv[2]))
        argv = argv[3:]
    ok = True
    for p in argv:
        t = load(p)
        lo, hi = t.reshape(-1, 3).min(0), t.reshape(-1, 3).max(0)
        d = hi - lo
        fits = (d[0] <= bed[0] and d[1] <= bed[1]) or (d[0] <= bed[1] and d[1] <= bed[0])
        ok &= fits
        print(f"{p:32s} tris {len(t):6d}  bbox {d[0]:7.2f} x {d[1]:7.2f} x {d[2]:7.2f}  "
              f"vol {volume(t)/1000:8.1f} cm3  fits {bed[0]:.0f}x{bed[1]:.0f}: {'yes' if fits else 'NO'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
