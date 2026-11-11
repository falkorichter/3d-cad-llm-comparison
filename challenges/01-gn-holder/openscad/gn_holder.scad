// Challenge 01: GN 1/1 insert frame on legs (type A), OpenSCAD baseline.
// Spec: ../DESIGN.md (v1). Units mm. X = 530 side, Y = 325 side, Z up.
//
// Export one part:   openscad -o corner_ne.stl -D 'part="corner_ne"' gn_holder.scad
// Parts: corner_ne corner_nw corner_se corner_sw middle_n middle_s leg divider
// Views: assembly (default), exploded, frame (all rail parts, assembled, no legs)

/* [Selector] */
part = "assembly";

/* [DESIGN.md parameters] */
gn_l      = 530;   // GN 1/1 nominal (outer rim), long side
gn_w      = 325;   // GN 1/1 nominal, short side
play      = 1.0;   // gap per side between pan rim and frame
rim_w     = 12.5;  // pan rim width (estimate)
ledge_w   = 8;     // ledge reach under the rim, inward from the opening
ledge_t   = 4;     // ledge thickness
rim_t     = 2;     // pan rim thickness = rim pocket depth (rim ends flush)
wall      = 10;    // frame wall outside the opening
bar_h     = 20;    // frame rail height
max_depth = 150;   // deepest pan
clear     = 15;    // clearance under the deepest pan
leg       = 30;    // leg cross-section (square)
div_w     = 16;    // divider bar width
tol       = 0.3;   // fit tolerance for joints and removable parts
bed_x     = 256;   // printer bed
bed_y     = 256;

/* [Layout] */
// Pans along the 530 side (each 325 deep). Dividers go between them.
layout    = ["1/3", "1/3", "1/3"];
// "all": seats at every 1/2 and 1/3 position (also serves 2/3 + 1/3); "layout": only where `layout` needs them
seat_mode = "all";

/* [Joint and detail parameters (not in DESIGN.md)] */
split_x   = 114;   // long rails are cut at x = +-split_x (middle part 2*split_x + 2*dt_len)
boss_len  = 28;    // solid rail section (chamfer void filled) around each joint
dt_u      = 9;     // dovetail centre, measured inward from the outer face
dt_neck   = 6;     // dovetail width at the joint plane
dt_head   = 11;    // dovetail width at its end
dt_len    = 10;    // dovetail length
dt_floor  = 4;     // dovetail underside starts here at the joint plane, rises at 45 deg
seat_in   = 4;     // outer skin left behind a divider seat
div_web   = 8;     // divider web width (between two pan bodies)
pan_c     = 2;     // extra clearance around the pan body (gn - 2*rim_w) at legs/corners
tenon     = 14;    // leg tenon (square)
tenon_h   = 8;     // straight part of the tenon; a 45 deg pyramid sits on top
tenon_u   = 13;    // tenon centre, inward from both outer faces
explode   = 40;    // gap for part="exploded"
slice_z   = 170;   // part="slice": 2D cut of frame + legs at this height (absolute z), for measuring

/* [Derived] */
op_l   = gn_l + 2*play;            // 532  rim pocket / opening
op_w   = gn_w + 2*play;            // 327
hole_l = op_l - 2*ledge_w;         // 516  through-hole under the ledge
hole_w = op_w - 2*ledge_w;         // 311
out_l  = op_l + 2*wall;            // 552  outer frame
out_w  = op_w + 2*wall;            // 347
band   = wall + ledge_w;           // 18   rail width at the ledge level
ledge_top = bar_h - rim_t;         // 18   (rail-local z)
ledge_bot = ledge_top - ledge_t;   // 14
cham_z    = ledge_bot - ledge_w;   // 6    45 deg gusset under the ledge ends here
seat_z    = ledge_bot - ledge_t;   // 10   divider seat floor
z0     = max_depth + clear - ledge_bot;  // 151 rail bottom above floor (= leg height)
pan_l  = gn_l - 2*rim_w + 2*pan_c; // 509 pan body envelope kept free
pan_w  = gn_w - 2*rim_w + 2*pan_c; // 304
notch_u = out_l/2 - pan_l/2;       // 21.5 legs/corner blocks stop here (inner corner)

assert(cham_z >= 0, "bar_h too small for ledge + 45 deg gusset");
assert(seat_z >= 0);
assert(2*split_x + 2*dt_len <= max(bed_x, bed_y), "middle rail part too long for the bed");
assert(out_l/2 - split_x <= max(bed_x, bed_y));
assert(dt_u + dt_head/2 + tol < band - 2 && dt_u - dt_head/2 - tol > 2, "dovetail walls too thin");
assert(dt_len + tol < boss_len/2);

big = 1000;
eps = 0.01;

// ---------- layout ----------
fr_tab = [["1/1",1],["2/3",2/3],["1/2",1/2],["1/3",1/3]];
function frac(s) = fr_tab[search([s], fr_tab)[0]][1];
function cum(l, k) = k == 0 ? 0 : cum(l, k-1) + frac(l[k-1]);
assert(abs(cum(layout, len(layout)) - 1) < 1e-6, "layout fractions must add up to 1/1");
div_x   = len(layout) > 1 ? [for (k = [1:len(layout)-1]) -gn_l/2 + cum(layout, k)*gn_l] : [];
all_x   = [-gn_l/6, 0, gn_l/6];   // 1/3, 1/2 (and 2/3 + 1/3), 2/3
seats_x = seat_mode == "all" ? all_x : div_x;
echo(str("derived: opening ", op_l, "x", op_w, ", through-hole ", hole_l, "x", hole_w,
         ", outer ", out_l, "x", out_w, ", rail bottom z0 ", z0,
         ", ledge underside ", z0 + ledge_bot, ", top ", z0 + bar_h));
echo(str("dividers at x = ", div_x, ", seats at x = ", seats_x));

// ---------- helpers ----------
// box on a long rail (sy = +-1), u measured inward from the outer face
module rail_box(sy, x0, x1, u0, u1, zz0, zz1) {
    y0 = sy > 0 ? out_w/2 - u1 : -out_w/2 + u0;
    translate([x0, y0, zz0]) cube([x1 - x0, u1 - u0, zz1 - zz0]);
}
// local joint frame: s along `sd` (direction the tail points), u along `ud` (inward)
module jframe(p, sd, ud)
    multmatrix([[sd[0], ud[0], 0, p[0]], [sd[1], ud[1], 0, p[1]], [0, 0, 1, 0], [0, 0, 0, 1]])
        children();

// joints: [origin on outer face, tail direction, inward direction, tail owner, socket owner]
joints = [
    [[ split_x,  out_w/2], [ 1, 0], [0, -1], "middle_n", "corner_ne"],
    [[-split_x,  out_w/2], [-1, 0], [0, -1], "middle_n", "corner_nw"],
    [[ split_x, -out_w/2], [ 1, 0], [0,  1], "middle_s", "corner_se"],
    [[-split_x, -out_w/2], [-1, 0], [0,  1], "middle_s", "corner_sw"],
    [[ out_l/2, 0], [0, -1], [-1, 0], "corner_ne", "corner_se"],
    [[-out_l/2, 0], [0,  1], [ 1, 0], "corner_sw", "corner_nw"],
];

module dt_profile(g) {
    offset(delta = g) polygon([[-eps, dt_u - dt_neck/2], [dt_len, dt_u - dt_head/2],
                               [dt_len, dt_u + dt_head/2], [-eps, dt_u + dt_neck/2]]);
    if (g > 0) translate([-1, dt_u - dt_neck/2 - g]) square([1 + eps, dt_neck + 2*g]);
}
// underside rises at 45 deg away from the joint plane, so the tail prints without support
module dt_ramp(g, ztop)
    rotate([90, 0, 0]) linear_extrude(height = 200, center = true)
        polygon([[-5, dt_floor - g - 5], [dt_len + 5, dt_floor - g + dt_len + 5], [dt_len + 5, ztop], [-5, ztop]]);
module dt_tail()   intersection() { linear_extrude(bar_h) dt_profile(0); dt_ramp(0, bar_h); }
module dt_socket() intersection() { translate([0, 0, -1]) linear_extrude(bar_h + 2) dt_profile(tol); dt_ramp(tol, bar_h + 1); }

// leg tenon / socket in local corner coords (u, u from the outer corner)
module tenon_shape(g, zbase) {
    s = tenon + 2*g;
    translate([tenon_u, tenon_u, 0]) {
        translate([-s/2, -s/2, zbase]) cube([s, s, tenon_h + g - zbase]);
        hull() {
            translate([-s/2, -s/2, tenon_h + g - eps]) cube([s, s, eps]);
            translate([-eps/2, -eps/2, tenon_h + g + s/2]) cube([eps, eps, eps]);
        }
    }
}
// place children (built for the NE corner, local u = inward) at corner (sx, sy)
module at_corner(sx, sy)
    translate([sx*out_l/2, sy*out_w/2, 0]) mirror([sx > 0 ? 1 : 0, 0, 0]) mirror([0, sy > 0 ? 1 : 0, 0]) children();

corners = [[1, 1], [-1, 1], [1, -1], [-1, -1]];

// ---------- frame (rail-local z: 0 = rail bottom) ----------
module ring() difference() {
    translate([-out_l/2, -out_w/2, 0]) cube([out_l, out_w, bar_h]);
    cube([hole_l, hole_w, 3*bar_h], center = true);
    hull() {   // void under the ledge, 45 deg gusset
        translate([-op_l/2, -op_w/2, -1]) cube([op_l, op_w, cham_z + 1]);
        translate([-hole_l/2, -hole_w/2, -1]) cube([hole_l, hole_w, ledge_bot + 1]);
    }
}
module pocket() translate([-op_l/2, -op_w/2, ledge_top]) cube([op_l, op_w, bar_h]);
module pan_box() cube([pan_l, pan_w, big], center = true);
module bosses() {
    for (sy = [-1, 1], sx = [-1, 1]) rail_box(sy, sx*split_x - boss_len/2, sx*split_x + boss_len/2, 0, band, 0, bar_h);
    for (sx = [-1, 1]) translate([sx > 0 ? out_l/2 - band : -out_l/2, -boss_len/2, 0]) cube([band, boss_len, bar_h]);
}
module corner_blocks() for (c = corners) at_corner(c[0], c[1]) cube([leg, leg, bar_h]);
module seat_slots() for (x = seats_x, sy = [-1, 1])
    rail_box(sy, x - div_w/2 - tol, x + div_w/2 + tol, seat_in, band + 1, seat_z, bar_h + 1);
module leg_sockets() for (c = corners) at_corner(c[0], c[1]) tenon_shape(tol, -1);

module frame_raw() render() difference() {
    union() { ring(); bosses(); corner_blocks(); }
    pocket(); pan_box(); seat_slots(); leg_sockets();
}

function region(name) =   // [x0, x1, y0, y1]
    name == "middle_n"  ? [-split_x, split_x, 0, big] :
    name == "middle_s"  ? [-split_x, split_x, -big, 0] :
    name == "corner_ne" ? [ split_x,  big, 0,  big] :
    name == "corner_nw" ? [-big, -split_x, 0,  big] :
    name == "corner_se" ? [ split_x,  big, -big, 0] :
                          [-big, -split_x, -big, 0];   // corner_sw

module rail_part(name) {
    r = region(name);
    render() difference() {
        union() {
            intersection() {
                frame_raw();
                translate([r[0], r[2], -1]) cube([r[1] - r[0], r[3] - r[2], bar_h + 2]);
            }
            for (j = joints) if (j[3] == name) jframe(j[0], j[1], j[2]) dt_tail();
        }
        pocket();
        for (j = joints) if (j[4] == name) jframe(j[0], j[1], j[2]) dt_socket();
    }
}

// ---------- legs (absolute z: 0 = floor) ----------
module leg_local() {   // NE corner, local u inward
    difference() {
        cube([leg, leg, z0]);
        translate([notch_u, notch_u, -1]) cube([leg, leg, z0 + 2]);
    }
    translate([0, 0, z0 - eps]) tenon_shape(0, 0);
}

// ---------- divider (rail-local z), world position x = xd ----------
module divider_at(xd) {
    Y1 = out_w/2 - seat_in - tol;   // end of the bar, inside the seat
    Y2 = out_w/2 - wall;            // rail inner face (opening edge)
    Y3 = out_w/2 - band;            // ledge tip (through-hole edge)
    translate([xd, 0, 0]) rotate([90, 0, 90]) {
        linear_extrude(height = div_w, center = true) polygon([
            [-Y1, seat_z], [-Y3, seat_z], [-Y3, ledge_bot], [Y3, ledge_bot], [Y3, seat_z], [Y1, seat_z],
            [Y1, bar_h], [Y2, bar_h], [Y2, ledge_top], [-Y2, ledge_top], [-Y2, bar_h], [-Y1, bar_h]]);
        linear_extrude(height = div_web, center = true) polygon([
            [-Y3, seat_z], [-Y3 + seat_z, 0], [Y3 - seat_z, 0], [Y3, seat_z], [Y3, ledge_bot + 1], [-Y3, ledge_bot + 1]]);
    }
}

// ---------- views ----------
rail_names = ["corner_ne", "corner_nw", "corner_se", "corner_sw", "middle_n", "middle_s"];
function rcol(n) = n == "middle_n" || n == "middle_s" ? "SteelBlue" : (n == "corner_ne" || n == "corner_sw") ? "Orange" : "Gold";

module assembly(e = 0, dividers = true) {
    for (n = rail_names) {
        r = region(n);
        dx = n == "middle_n" || n == "middle_s" ? 0 : sign(r[0] + r[1]) * e;
        dy = sign(r[2] + r[3]) * e;
        color(rcol(n)) translate([dx, dy, z0 + e]) rail_part(n);
    }
    for (c = corners) color("DimGray")
        translate([c[0]*e, c[1]*e, -e*0.0]) at_corner(c[0], c[1]) leg_local();
    if (dividers) for (x = div_x) color("SeaGreen") translate([0, 0, z0 + 3*e]) divider_at(x);
}

// print orientation for each exported part, roughly centred on the origin
if (part == "assembly") assembly(0);
else if (part == "exploded") assembly(explode);
else if (part == "slice") projection(cut = true) translate([0, 0, -slice_z]) assembly(0, false);
else if (part == "overlap") {   // must come out empty: every pair of assembled parts intersected
    n = len(rail_names);
    for (i = [0:n-1], j = [0:n-1]) if (i < j)
        intersection() { rail_part(rail_names[i]); rail_part(rail_names[j]); }
    for (i = [0:n-1], x = div_x) intersection() { rail_part(rail_names[i]); divider_at(x); }
    for (i = [0:n-1], c = corners) intersection() { translate([0, 0, z0]) rail_part(rail_names[i]); at_corner(c[0], c[1]) leg_local(); }
}
else if (part == "frame") for (n = rail_names) rail_part(n);
else if (part == "leg") translate([-leg/2, -leg/2, 0]) leg_local();
else if (part == "divider")   // lying on its side, turned 45 deg to fit the bed diagonal
    rotate([0, 0, 45]) translate([bar_h/2, 0, div_w/2]) rotate([0, -90, 0]) divider_at(0);
else if (search([part], rail_names)[0] != []) {
    r = region(part);
    cx = max(-out_l/2, r[0]) + (min(out_l/2, r[1]) - max(-out_l/2, r[0]))/2;
    cy = max(-out_w/2, r[2]) + (min(out_w/2, r[3]) - max(-out_w/2, r[2]))/2;
    translate([-cx, -cy, 0]) rail_part(part);
}
else assert(false, str("unknown part: ", part));
