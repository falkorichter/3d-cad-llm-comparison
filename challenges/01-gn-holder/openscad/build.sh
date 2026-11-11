#!/usr/bin/env bash
# Export every printed part as STL, the renders, and run the checks.
# usage: ./build.sh            (extra -D overrides can be passed: ./build.sh -D 'play=1.5')
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")"
OPENSCAD=${OPENSCAD:-openscad}
SRC=gn_holder.scad
mkdir -p stl renders

for p in corner_ne corner_nw corner_se corner_sw middle_n middle_s leg divider; do
  echo "== $p"
  "$OPENSCAD" -q "$@" -D "part=\"$p\"" -o "stl/$p.stl" "$SRC"
done

echo "== assembly.stl (reference only, not printable as one piece)"
"$OPENSCAD" -q "$@" -D 'part="assembly"' -o stl/assembly.stl "$SRC"

echo "== renders"
r() { "$OPENSCAD" -q "$@" "$SRC"; }
r -D 'part="assembly"' -o renders/assembly.png --imgsize=1600,1100 --viewall --autocenter --camera=0,0,0,62,0,32,0
r -D 'part="exploded"' -o renders/exploded.png --imgsize=1600,1100 --viewall --autocenter --camera=0,0,0,62,0,32,0
r -D 'part="assembly"' -o renders/corner_closeup.png --imgsize=1200,900 --camera=150,40,240,270,160,165
r -D 'part="assembly"' -o renders/seat_divider_closeup.png --imgsize=1200,900 --camera=20,60,240,88,170,165
r -D 'part="corner_ne"' -o renders/part_corner_ne.png --render --imgsize=1200,900 --viewall --autocenter --camera=0,0,0,55,0,215,0
r -D 'part="corner_ne"' -o renders/part_corner_ne_bottom.png --render --imgsize=1200,900 --viewall --autocenter --camera=0,0,0,130,0,215,0
r -D 'part="middle_n"' -o renders/part_middle_n.png --render --imgsize=1400,700 --viewall --autocenter --camera=0,0,0,55,0,20,0
r -D 'part="leg"' -o renders/part_leg.png --render --imgsize=600,1000 --viewall --autocenter --camera=0,0,0,70,0,35,0
r -D 'part="divider"' -o renders/part_divider_on_bed.png --render --imgsize=1000,1000 --viewall --autocenter --camera=0,0,0,0,0,0,0

echo "== bed fit"
python3 check_stl.py stl/corner_*.stl stl/middle_*.stl stl/leg.stl stl/divider.stl

echo "== derived sizes (horizontal cuts of frame + legs, no dividers)"
SL=$(mktemp -d)
for z in 0.5 75 150 160 164.9 165.1 167 170; do
  "$OPENSCAD" -q "$@" -D 'part="slice"' -D "slice_z=$z" -o "$SL/z$z.svg" "$SRC"
done
python3 measure_slices.py "$SL"
python3 check_stl.py --bed 9999 9999 stl/assembly.stl

echo "== overlap check (volume must be ~0)"
"$OPENSCAD" -q "$@" -D 'part="overlap"' -o "$SL/overlap.stl" "$SRC"
python3 -c "import sys; sys.path.insert(0, '.'); from check_stl import load, volume; print('overlap volume mm3: %.6f' % volume(load('$SL/overlap.stl')))"
