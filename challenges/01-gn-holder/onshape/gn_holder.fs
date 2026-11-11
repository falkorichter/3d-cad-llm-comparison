FeatureScript 3112;
import(path : "onshape/std/common.fs", version : "3112.0");
import(path : "onshape/std/geometry.fs", version : "3112.0");

// Challenge 01, DESIGN.md v1: flat GN insert frame on 4 legs, split into parts that fit a small bed.
// One custom feature builds every printed part as its own body, in assembly position.
// Frame bottom at z = 0, legs go down to z = -(maxDepth + clear). Same parameter names as DESIGN.md.

export enum GNLayout
{
    annotation { "Name" : "3 x 1/3 (2 dividers)" }
    THIRDS,
    annotation { "Name" : "2 x 1/2 (1 divider)" }
    HALVES,
    annotation { "Name" : "1 x 1/1 (no divider)" }
    FULL
}

annotation { "Feature Type Name" : "GN Holder" }
export const gnHolder = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "GN length (nominal)" }
        isLength(definition.gnL, { (millimeter) : [100, 530, 1000] } as LengthBoundSpec);
        annotation { "Name" : "GN width (nominal)" }
        isLength(definition.gnW, { (millimeter) : [100, 325, 1000] } as LengthBoundSpec);
        annotation { "Name" : "Layout" }
        definition.layout is GNLayout;
        annotation { "Name" : "Play per side" }
        isLength(definition.play, { (millimeter) : [0, 1, 10] } as LengthBoundSpec);
        annotation { "Name" : "Ledge width" }
        isLength(definition.ledgeW, { (millimeter) : [2, 8, 50] } as LengthBoundSpec);
        annotation { "Name" : "Ledge thickness (seat depth)" }
        isLength(definition.ledgeT, { (millimeter) : [1, 4, 20] } as LengthBoundSpec);
        annotation { "Name" : "Rim thickness (pocket depth)" }
        isLength(definition.rimT, { (millimeter) : [0, 2, 10] } as LengthBoundSpec);
        annotation { "Name" : "Wall" }
        isLength(definition.wall, { (millimeter) : [3, 10, 50] } as LengthBoundSpec);
        annotation { "Name" : "Rail height" }
        isLength(definition.barH, { (millimeter) : [8, 20, 100] } as LengthBoundSpec);
        annotation { "Name" : "Max pan depth" }
        isLength(definition.maxDepth, { (millimeter) : [10, 150, 300] } as LengthBoundSpec);
        annotation { "Name" : "Clearance under pan" }
        isLength(definition.clear, { (millimeter) : [0, 15, 100] } as LengthBoundSpec);
        annotation { "Name" : "Leg size" }
        isLength(definition.leg, { (millimeter) : [15, 30, 80] } as LengthBoundSpec);
        annotation { "Name" : "Divider width" }
        isLength(definition.divW, { (millimeter) : [6, 16, 50] } as LengthBoundSpec);
        annotation { "Name" : "Fit tolerance" }
        isLength(definition.tol, { (millimeter) : [0, 0.3, 2] } as LengthBoundSpec);
        annotation { "Name" : "Split position (x)" }
        isLength(definition.splitX, { (millimeter) : [40, 125, 500] } as LengthBoundSpec);
        annotation { "Name" : "Printer bed (square, and max height)" }
        isLength(definition.bed, { (millimeter) : [100, 256, 1000] } as LengthBoundSpec);
    }
    {
        buildGnHolder(context, id, definition);
    }, {
        "gnL" : 530 * millimeter, "gnW" : 325 * millimeter, "layout" : GNLayout.THIRDS,
        "play" : 1 * millimeter, "ledgeW" : 8 * millimeter, "ledgeT" : 4 * millimeter,
        "rimT" : 2 * millimeter, "wall" : 10 * millimeter, "barH" : 20 * millimeter,
        "maxDepth" : 150 * millimeter, "clear" : 15 * millimeter, "leg" : 30 * millimeter,
        "divW" : 16 * millimeter, "tol" : 0.3 * millimeter, "splitX" : 125 * millimeter,
        "bed" : 256 * millimeter
    });

// ---------- fixed joint sizes (M4 hardware) ----------
const SP_LEN = 68 * millimeter;      // splice plate length
const SP_T = 4 * millimeter;         // splice plate thickness = recess depth
const INS_R = 2.8 * millimeter;      // M4 heat-set insert hole radius (D5.6)
const INS_D = 8 * millimeter;        // insert hole depth in the rails
const BOLT_R = 2.25 * millimeter;    // M4 clearance (D4.5)
const CB_R = 4 * millimeter;         // counterbore D8
const CB_D = 4 * millimeter;
const SPIG = 8 * millimeter;         // square leg spigot
const SPIG_H = 7.5 * millimeter;
const LEG_INS_D = 12 * millimeter;   // insert hole depth in the leg top
const EPS = 1 * millimeter;          // overshoot for clean cuts

function gnLo(a, b) { return a < b ? a : b; }
function gnHi(a, b) { return a < b ? b : a; }

/** Axis-aligned box from any two opposite corners. */
function gnBox(context is Context, id is Id, x1, y1, z1, x2, y2, z2) returns Query
{
    fCuboid(context, id, {
                "corner1" : vector(gnLo(x1, x2), gnLo(y1, y2), gnLo(z1, z2)),
                "corner2" : vector(gnHi(x1, x2), gnHi(y1, y2), gnHi(z1, z2))
            });
    return qCreatedBy(id, EntityType.BODY);
}

/** Vertical cylinder from z1 to z2. */
function gnCyl(context is Context, id is Id, x, y, z1, z2, r) returns Query
{
    fCylinder(context, id, {
                "bottomCenter" : vector(x, y, z1),
                "topCenter" : vector(x, y, z2),
                "radius" : r
            });
    return qCreatedBy(id, EntityType.BODY);
}

function gnSubtract(context is Context, id is Id, target is Query, tools is array)
{
    if (size(tools) > 0)
        opBoolean(context, id, { "tools" : qUnion(tools), "targets" : target, "operationType" : BooleanOperationType.SUBTRACTION });
}

/** Derived sizes, one place. */
function gnDims(d is map) returns map
{
    const openL = d.gnL + 2 * d.play;
    const openW = d.gnW + 2 * d.play;
    const holeL = openL - 2 * d.ledgeW;
    const holeW = openW - 2 * d.ledgeW;
    return {
            "openL" : openL, "openW" : openW, "holeL" : holeL, "holeW" : holeW,
            "outL" : openL + 2 * d.wall, "outW" : openW + 2 * d.wall,
            "zl" : d.barH - d.rimT,                     // ledge top = where the rims sit
            "bandY" : (holeW / 2 + openW / 2 + d.wall) / 2, // long rail centre line
            "bandX" : (holeL / 2 + openL / 2 + d.wall) / 2, // short rail centre line
            "legH" : d.maxDepth + d.clear
        };
}

/** The whole frame ring with every cut, before splitting. */
function buildFrame(context is Context, id is Id, d is map, m is map) returns Query
{
    const H = d.barH;
    const frame = gnBox(context, id + "outer", -m.outL / 2, -m.outW / 2, 0 * millimeter, m.outL / 2, m.outW / 2, H);
    var tools = [];
    // rim pocket and through-hole
    tools = append(tools, gnBox(context, id + "pocket", -m.openL / 2, -m.openW / 2, m.zl, m.openL / 2, m.openW / 2, H + EPS));
    tools = append(tools, gnBox(context, id + "hole", -m.holeL / 2, -m.holeW / 2, -EPS, m.holeL / 2, m.holeW / 2, H + EPS));
    var n = 0;
    // divider seats in both long rails at 1/3, 1/2, 2/3 (1/3 and 2/3|1/3 share a position)
    for (var sx in [-m.openL / 6, 0 * millimeter, m.openL / 6])
    {
        for (var sy in [-1, 1])
        {
            tools = append(tools, gnBox(context, id + ("seat" ~ n), sx - d.divW / 2 - d.tol, sy * (m.holeW / 2 - EPS), m.zl - d.ledgeT,
                        sx + d.divW / 2 + d.tol, sy * m.openW / 2, H + EPS));
            n += 1;
        }
    }
    // splice plate recesses + insert holes: 4 joints across the long rails, 2 across the short rails
    for (var sx in [-1, 1])
    {
        for (var sy in [-1, 1])
        {
            const jx = sx * d.splitX;
            tools = append(tools, gnBox(context, id + ("recL" ~ n), jx - SP_LEN / 2 - d.tol, sy * (m.holeW / 2 - EPS), -EPS,
                        jx + SP_LEN / 2 + d.tol, sy * (m.outW / 2 + EPS), SP_T));
            for (var off in [-24, -10, 10, 24])
            {
                tools = append(tools, gnCyl(context, id + ("insL" ~ n ~ "_" ~ (off + 30)), jx + off * millimeter, sy * m.bandY, SP_T - EPS, SP_T + INS_D, INS_R));
            }
            // leg socket + bolt hole + counterbore at this corner
            const cx = sx * (m.openL / 2 + d.wall / 2);
            const cy = sy * (m.openW / 2 + d.wall / 2);
            const s = SPIG / 2 + d.tol;
            tools = append(tools, gnBox(context, id + ("sock" ~ n), cx - s, cy - s, -EPS, cx + s, cy + s, SPIG_H + 0.5 * millimeter));
            tools = append(tools, gnCyl(context, id + ("bolt" ~ n), cx, cy, -EPS, H + EPS, BOLT_R));
            tools = append(tools, gnCyl(context, id + ("cb" ~ n), cx, cy, H - CB_D, H + EPS, CB_R));
            n += 1;
        }
        tools = append(tools, gnBox(context, id + ("recS" ~ n), sx * (m.holeL / 2 - EPS), -SP_LEN / 2 - d.tol, -EPS,
                    sx * (m.outL / 2 + EPS), SP_LEN / 2 + d.tol, SP_T));
        for (var off in [-24, -10, 10, 24])
        {
            tools = append(tools, gnCyl(context, id + ("insS" ~ n ~ "_" ~ (off + 30)), sx * m.bandX, off * millimeter, SP_T - EPS, SP_T + INS_D, INS_R));
        }
        n += 1;
    }
    gnSubtract(context, id + "cut", frame, tools);
    return frame;
}

function buildGnHolder(context is Context, id is Id, d is map)
{
    const m = gnDims(d);
    if (2 * d.splitX + SP_LEN >= m.holeL)
        throw regenError("Split position too far out: the long splice plates would reach the corners.", ["splitX"]);

    const BIG = 1000 * millimeter;
    var parts = []; // [name, query, colour]
    var done = qNothing();

    // ---- frame: 4 corners + 2 middle rails, each = full frame AND region ----
    const regions = [
        ["Corner +X+Y", d.splitX, BIG, 0 * millimeter, BIG],
        ["Corner -X+Y", -BIG, -d.splitX, 0 * millimeter, BIG],
        ["Corner -X-Y", -BIG, -d.splitX, -BIG, 0 * millimeter],
        ["Corner +X-Y", d.splitX, BIG, -BIG, 0 * millimeter],
        ["Rail +Y", -d.splitX, d.splitX, 0 * millimeter, BIG],
        ["Rail -Y", -d.splitX, d.splitX, -BIG, 0 * millimeter]
    ];
    for (var i = 0; i < size(regions); i += 1)
    {
        const r = regions[i];
        const pid = id + ("part" ~ i);
        const f = buildFrame(context, pid + "frame", d, m);
        const reg = gnBox(context, pid + "region", r[1], r[3], -EPS, r[2], r[4], d.barH + EPS);
        opBoolean(context, pid + "split", { "tools" : qUnion([f, reg]), "operationType" : BooleanOperationType.INTERSECTION });
        // queries are lazy: resolve now, or "new body" would also match parts built later
        const body = qUnion(evaluateQuery(context, qSubtraction(qBodyType(qCreatedBy(id, EntityType.BODY), BodyType.SOLID), done)));
        parts = append(parts, [r[0], body, i < 4 ? color(0.20, 0.45, 0.75) : color(0.30, 0.65, 0.85)]);
        done = qUnion([done, body]);
    }

    // ---- splice plates ----
    var k = 0;
    for (var sx in [-1, 1])
    {
        for (var sy in [-1, 1])
        {
            const jx = sx * d.splitX;
            const pid = id + ("spL" ~ k);
            const plate = gnBox(context, pid + "plate", jx - SP_LEN / 2, sy * m.holeW / 2, 0 * millimeter, jx + SP_LEN / 2, sy * m.outW / 2, SP_T);
            var holes = [];
            for (var off in [-24, -10, 10, 24])
                holes = append(holes, gnCyl(context, pid + ("h" ~ (off + 30)), jx + off * millimeter, sy * m.bandY, -EPS, SP_T + EPS, BOLT_R));
            gnSubtract(context, pid + "cut", plate, holes);
            parts = append(parts, ["Splice plate " ~ (k + 1), plate, color(0.85, 0.55, 0.15)]);
            k += 1;
        }
        const pidS = id + ("spS" ~ k);
        const plateS = gnBox(context, pidS + "plate", sx * m.holeL / 2, -SP_LEN / 2, 0 * millimeter, sx * m.outL / 2, SP_LEN / 2, SP_T);
        var holesS = [];
        for (var off in [-24, -10, 10, 24])
            holesS = append(holesS, gnCyl(context, pidS + ("h" ~ (off + 30)), sx * m.bandX, off * millimeter, -EPS, SP_T + EPS, BOLT_R));
        gnSubtract(context, pidS + "cut", plateS, holesS);
        parts = append(parts, ["Splice plate " ~ (k + 1), plateS, color(0.85, 0.55, 0.15)]);
        k += 1;
    }

    // ---- legs: inner faces flush with the through-hole, so the pan path stays clear ----
    k = 0;
    for (var sx in [-1, 1])
    {
        for (var sy in [-1, 1])
        {
            const pid = id + ("leg" ~ k);
            const cx = sx * (m.openL / 2 + d.wall / 2);
            const cy = sy * (m.openW / 2 + d.wall / 2);
            const post = gnBox(context, pid + "post", sx * m.holeL / 2, sy * m.holeW / 2, -m.legH, sx * (m.holeL / 2 + d.leg), sy * (m.holeW / 2 + d.leg), 0 * millimeter);
            const spig = gnBox(context, pid + "spig", cx - SPIG / 2, cy - SPIG / 2, -EPS, cx + SPIG / 2, cy + SPIG / 2, SPIG_H);
            opBoolean(context, pid + "join", { "tools" : qUnion([post, spig]), "operationType" : BooleanOperationType.UNION });
            const legBody = qUnion(evaluateQuery(context, qCreatedBy(pid, EntityType.BODY)));
            gnSubtract(context, pid + "cut", legBody, [gnCyl(context, pid + "ins", cx, cy, SPIG_H - LEG_INS_D, SPIG_H + EPS, INS_R)]);
            parts = append(parts, ["Leg " ~ (k + 1), legBody, color(0.35, 0.35, 0.40)]);
            k += 1;
        }
    }

    // ---- divider bars: bar between the rails + end tabs that drop into the seats ----
    var divXs = [];
    if (d.layout == GNLayout.THIRDS)
        divXs = [-m.openL / 6, m.openL / 6];
    else if (d.layout == GNLayout.HALVES)
        divXs = [0 * millimeter];
    k = 0;
    for (var x in divXs)
    {
        const pid = id + ("div" ~ k);
        const yb = m.holeW / 2 - d.tol;
        const yt = m.openW / 2 - d.tol;
        const bar = gnBox(context, pid + "bar", x - d.divW / 2, -yb, 0 * millimeter, x + d.divW / 2, yb, m.zl);
        const t1 = gnBox(context, pid + "tab1", x - d.divW / 2, yb - EPS, m.zl - d.ledgeT, x + d.divW / 2, yt, m.zl);
        const t2 = gnBox(context, pid + "tab2", x - d.divW / 2, -yb + EPS, m.zl - d.ledgeT, x + d.divW / 2, -yt, m.zl);
        opBoolean(context, pid + "join", { "tools" : qUnion([bar, t1, t2]), "operationType" : BooleanOperationType.UNION });
        parts = append(parts, ["Divider " ~ (k + 1), qUnion(evaluateQuery(context, qCreatedBy(pid, EntityType.BODY))), color(0.40, 0.70, 0.35)]);
        k += 1;
    }

    // ---- name, colour, and check every part against the bed ----
    var misfits = [];
    for (var p in parts)
    {
        setProperty(context, { "entities" : p[1], "propertyType" : PropertyType.NAME, "value" : p[0] });
        setProperty(context, { "entities" : p[1], "propertyType" : PropertyType.APPEARANCE, "value" : p[2] });
        const bb = evBox3d(context, { "topology" : p[1], "tight" : true });
        const s = bb.maxCorner - bb.minCorner;
        const sz = sort([s[0] / millimeter, s[1] / millimeter, s[2] / millimeter], function(a, b) { return a - b; });
        const bed = d.bed / millimeter;
        var fit = "NO";
        if (sz[0] <= bed && sz[2] <= bed)
            fit = "flat";
        else if (sz[0] <= bed && sz[1] <= bed && (sz[1] + sz[2]) / sqrt(2) <= bed)
            fit = "diagonal";
        if (fit == "NO")
            misfits = append(misfits, p[0]);
        const vol = evVolume(context, { "entities" : p[1] }) / (millimeter ^ 3);
        println(p[0] ~ " | bbox " ~ roundToPrecision(s[0] / millimeter, 1) ~ " x " ~ roundToPrecision(s[1] / millimeter, 1) ~ " x " ~
                roundToPrecision(s[2] / millimeter, 1) ~ " | vol " ~ roundToPrecision(vol, 1) ~ " | bed " ~ fit);
    }
    println("parts " ~ size(parts) ~ " | out " ~ roundToPrecision(m.outL / millimeter, 2) ~ " x " ~ roundToPrecision(m.outW / millimeter, 2) ~
            " | opening " ~ roundToPrecision(m.openL / millimeter, 2) ~ " x " ~ roundToPrecision(m.openW / millimeter, 2) ~
            " | hole " ~ roundToPrecision(m.holeL / millimeter, 2) ~ " x " ~ roundToPrecision(m.holeW / millimeter, 2) ~
            " | clearance " ~ roundToPrecision(m.legH / millimeter, 2));
    if (size(misfits) > 0)
        reportFeatureWarning(context, id, "Parts that do not fit a " ~ roundToPrecision(d.bed / millimeter, 0) ~ " mm bed: " ~ toString(misfits));
}
