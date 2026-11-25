"""Challenge 01 v1 (DESIGN.md): flat GN 1/1 insert frame, built as a parametric FreeCAD document.

Everything is driven by the spreadsheet `Params` (aliases = DESIGN.md names). Every primitive's size and
placement is an *expression* on that sheet, so editing a cell in the GUI and pressing Recompute rebuilds all
parts. Run inside FreeCAD (MCP `execute_code`, the Python console, or `freecadcmd`):

    exec(open(".../gn_holder.py").read()); doc = build()

Frame bottom (= ledge underside) is z = 0, legs go down to z = -leg_h. Joints: M4 splice plates in bottom
recesses + heat-set inserts (same choice as the SolidCraft and Onshape builds).
"""
import FreeCAD as App

DOC = "GN_Holder"

# DESIGN.md parameters + joint/hardware sizes. Formulas start with "=", plain numbers are inputs.
PARAMS = [
    # name, value, comment
    ("gn_l", 530, "GN nominal length (1/1)"),
    ("gn_w", 325, "GN nominal width"),
    ("play", 1.0, "gap per side pan rim to frame"),
    ("rim_w", 12.5, "pan rim width (estimate)"),
    ("ledge_w", 8, "ledge reach under the rim"),
    ("ledge_t", 4, "seat notch depth / divider flange thickness"),
    ("rim_t", 2, "rim pocket depth"),
    ("wall", 10, "frame wall outside the opening"),
    ("bar_h", 20, "frame rail height"),
    ("max_depth", 150, "deepest pan"),
    ("clearance", 15, "DESIGN.md `clear`; `clear` is reserved in FreeCAD expressions"),
    ("leg", 30, "leg section"),
    ("div_w", 16, "divider flange width"),
    ("div_web", 8, "divider web width"),
    ("tol", 0.3, "fit tolerance"),
    ("bed_x", 256, "printer bed x"),
    ("bed_y", 256, "printer bed y"),
    ("split_x", 125, "long-rail joint position (+/-)"),
    ("sp_len", 68, "splice plate length"),
    ("sp_w", 14, "splice plate width"),
    ("sp_t", 4, "splice plate thickness"),
    ("ins_d", 5.6, "M4 heat-set insert hole diameter"),
    ("ins_h", 8, "insert hole depth above the recess"),
    ("ins_a", 10, "insert offset 1 from the joint"),
    ("ins_b", 24, "insert offset 2 from the joint"),
    ("scr_d", 4.5, "M4 clearance hole"),
    ("cb_d", 8, "leg bolt counterbore diameter"),
    ("cb_h", 4, "leg bolt counterbore depth"),
    ("leg_ins_h", 12, "insert depth in the leg top"),
    ("spig", 6, "leg spigot (anti-rotation) size"),
    ("seat_half", 1, "1 = seats/divider at the 1/2 position"),
    ("seat_third", 1, "1 = seats/dividers at 1/3 and 2/3"),
    # derived
    ("open_l", "=gn_l + 2*play", "rim pocket length (532)"),
    ("open_w", "=gn_w + 2*play", "rim pocket width (327)"),
    ("hole_l", "=open_l - 2*ledge_w", "through-hole length (516)"),
    ("hole_w", "=open_w - 2*ledge_w", "through-hole width (311)"),
    ("out_l", "=open_l + 2*wall", "outer length (552)"),
    ("out_w", "=open_w + 2*wall", "outer width (347)"),
    ("band", "=wall + ledge_w", "rail band width (18)"),
    ("ledge_z", "=bar_h - rim_t", "ledge top / rim seat height (18)"),
    ("leg_h", "=max_depth + clearance", "free height under the frame (165)"),
    ("band_x", "=out_l/2 - band/2", "short-rail band centre x"),
    ("band_y", "=out_w/2 - band/2", "long-rail band centre y"),
    ("wall_x", "=out_l/2 - wall/2", "leg bolt x"),
    ("wall_y", "=out_w/2 - wall/2", "leg bolt y"),
    ("leg_cx", "=hole_l/2 + leg/2", "leg centre x (inner face on the hole edge)"),
    ("leg_cy", "=hole_w/2 + leg/2", "leg centre y"),
    ("spig_x", "=hole_l/2 + 4", "spigot centre x"),
    ("spig_y", "=hole_w/2 + 4", "spigot centre y"),
    ("div_x", "=open_l/6 * seat_third", "divider position (+/-)"),
]

SIGNS = {"P": 1, "N": -1}


def _sheet(doc):
    s = doc.addObject("Spreadsheet::Sheet", "Params")
    s.set("A1", "name"); s.set("B1", "value"); s.set("C1", "comment")
    for i, (name, val, note) in enumerate(PARAMS, start=2):
        s.set(f"A{i}", name)
        s.set(f"B{i}", str(val))
        s.set(f"C{i}", note)
        s.setAlias(f"B{i}", name)
    doc.recompute()
    return s


def _q(e):
    """Expression referring to sheet aliases: 'open_l/2' -> 'Params.open_l/2'."""
    import re
    names = sorted((p[0] for p in PARAMS), key=len, reverse=True)
    return re.sub(r"\b(" + "|".join(names) + r")\b", r"Params.\1", str(e))


def box(doc, name, cx, cy, z0, lx, ly, lz, visible=False):
    """Part::Box centred on (cx, cy) in x/y, bottom at z0. All arguments are expressions."""
    b = doc.addObject("Part::Box", name)
    b.setExpression("Length", _q(lx))
    b.setExpression("Width", _q(ly))
    b.setExpression("Height", _q(lz))
    b.setExpression(".Placement.Base.x", _q(f"({cx}) - ({lx})/2"))
    b.setExpression(".Placement.Base.y", _q(f"({cy}) - ({ly})/2"))
    b.setExpression(".Placement.Base.z", _q(z0))
    _vis(b, visible)
    return b


def cyl(doc, name, cx, cy, z0, d, h, visible=False):
    c = doc.addObject("Part::Cylinder", name)
    c.setExpression("Radius", _q(f"({d})/2"))
    c.setExpression("Height", _q(h))
    c.setExpression(".Placement.Base.x", _q(cx))
    c.setExpression(".Placement.Base.y", _q(cy))
    c.setExpression(".Placement.Base.z", _q(z0))
    _vis(c, visible)
    return c


def _vis(o, visible):
    if App.GuiUp and o.ViewObject:
        o.ViewObject.Visibility = visible


def fuse(doc, name, shapes):
    f = doc.addObject("Part::MultiFuse", name)
    f.Shapes = shapes
    f.Refine = True
    _vis(f, False)
    return f


def cut(doc, name, base, tool, visible=False):
    c = doc.addObject("Part::Cut", name)
    c.Base, c.Tool = base, tool
    c.Refine = True
    _vis(c, visible)
    return c


def common(doc, name, a, b, visible=True):
    c = doc.addObject("Part::MultiCommon", name)
    c.Shapes = [a, b]
    c.Refine = True
    _vis(c, visible)
    return c


COLORS = {"Corner": (0.85, 0.55, 0.20), "Rail": (0.25, 0.55, 0.85), "Plate": (0.6, 0.6, 0.6),
          "Leg": (0.35, 0.65, 0.35), "Divider": (0.85, 0.30, 0.35)}


def _color(o, kind):
    if App.GuiUp and o.ViewObject:
        o.ViewObject.ShapeColor = COLORS[kind]


def build():
    if DOC in App.listDocuments():
        App.closeDocument(DOC)
    doc = App.newDocument(DOC)
    _sheet(doc)

    # ---- frame ring ---------------------------------------------------------------------------
    outer = box(doc, "Outer", 0, 0, 0, "out_l", "out_w", "bar_h")
    tools = [
        box(doc, "Pocket", 0, 0, "ledge_z", "open_l", "open_w", "rim_t + 1"),
        box(doc, "Hole", 0, 0, -1, "hole_l", "hole_w", "bar_h + 2"),
    ]
    # divider seats: one box per x position cuts the ledge of both long rails; a disabled seat is lifted
    # 100 mm above the frame so it cuts nothing.
    for nm, x, flag in (("Seat_0", "0", "seat_half"), ("Seat_P", "open_l/6", "seat_third"),
                        ("Seat_N", "-open_l/6", "seat_third")):
        tools.append(box(doc, nm, x, 0, f"ledge_z - ledge_t + (1 - {flag})*100",
                         "div_w + 2*tol", "open_w", "ledge_t + rim_t + 1"))
    rec_l, rec_w, rec_h = "sp_len + 2*tol", "sp_w + 2*tol", "sp_t + tol + 1"
    ins_z, ins_h = -1, "sp_t + tol + ins_h + 1"
    # long-rail joints at x = +/-split_x, y = +/-band_y
    for sx in "PN":
        for sy in "PN":
            X, Y = f"{SIGNS[sx]}*split_x", f"{SIGNS[sy]}*band_y"
            tools.append(box(doc, f"Rec_L{sx}{sy}", X, Y, -1, rec_l, rec_w, rec_h))
            for k, off in enumerate(("-ins_b", "-ins_a", "ins_a", "ins_b")):
                tools.append(cyl(doc, f"Ins_L{sx}{sy}{k}", f"{X} + {off}", Y, ins_z, "ins_d", ins_h))
    # short-rail joints at y = 0, x = +/-band_x
    for sx in "PN":
        X = f"{SIGNS[sx]}*band_x"
        tools.append(box(doc, f"Rec_S{sx}", X, 0, -1, rec_w, rec_l, rec_h))
        for k, off in enumerate(("-ins_b", "-ins_a", "ins_a", "ins_b")):
            tools.append(cyl(doc, f"Ins_S{sx}{k}", X, off, ins_z, "ins_d", ins_h))
    # leg seats under each corner: spigot socket + M4 bolt hole with counterbore from the top
    for sx in "PN":
        for sy in "PN":
            s_x, s_y = SIGNS[sx], SIGNS[sy]
            tools.append(box(doc, f"Sock_{sx}{sy}", f"{s_x}*spig_x", f"{s_y}*spig_y", -1,
                             "spig + 2*tol", "spig + 2*tol", "spig + tol + 1"))
            tools.append(cyl(doc, f"Bolt_{sx}{sy}", f"{s_x}*wall_x", f"{s_y}*wall_y", -1, "scr_d", "bar_h + 2"))
            tools.append(cyl(doc, f"CBore_{sx}{sy}", f"{s_x}*wall_x", f"{s_y}*wall_y", "bar_h - cb_h",
                             "cb_d", "cb_h + 1"))
    frame = cut(doc, "Frame", outer, fuse(doc, "FrameTools", tools))

    # ---- split into 4 corners + 2 middle rails (frame ∩ region box) -----------------------------
    big = "out_w/2 + 2"
    for sy in "PN":
        r = box(doc, f"Reg_Rail_{sy}", 0, f"{SIGNS[sy]}*({big})/2", -2, "2*split_x", big, "bar_h + 4")
        _color(common(doc, f"Rail_{sy}", frame, r), "Rail")
        for sx in "PN":
            w = "out_l/2 + 2 - split_x"
            r = box(doc, f"Reg_Corner_{sx}{sy}", f"{SIGNS[sx]}*(split_x + ({w})/2)",
                    f"{SIGNS[sy]}*({big})/2", -2, w, big, "bar_h + 4")
            _color(common(doc, f"Corner_{sx}{sy}", frame, r), "Corner")

    # ---- splice plates (sit in the recesses, flush with the frame bottom) -----------------------
    def plate(name, X, Y, along_x):
        lx, ly = ("sp_len", "sp_w") if along_x else ("sp_w", "sp_len")
        b = box(doc, name + "_Blank", X, Y, 0, lx, ly, "sp_t")
        holes = []
        for k, off in enumerate(("-ins_b", "-ins_a", "ins_a", "ins_b")):
            hx, hy = (f"{X} + {off}", Y) if along_x else (X, off)
            holes.append(cyl(doc, f"{name}_H{k}", hx, hy, -1, "scr_d", "sp_t + 2"))
        _color(cut(doc, name, b, fuse(doc, name + "_Holes", holes), visible=True), "Plate")

    n = 1
    for sx in "PN":
        for sy in "PN":
            plate(f"Plate_{n}", f"{SIGNS[sx]}*split_x", f"{SIGNS[sy]}*band_y", True); n += 1
    for sx in "PN":
        plate(f"Plate_{n}", f"{SIGNS[sx]}*band_x", "0", False); n += 1

    # ---- legs -------------------------------------------------------------------------------------
    for sx in "PN":
        for sy in "PN":
            s_x, s_y = SIGNS[sx], SIGNS[sy]
            post = box(doc, f"LegPost_{sx}{sy}", f"{s_x}*leg_cx", f"{s_y}*leg_cy", "-leg_h", "leg", "leg", "leg_h")
            spg = box(doc, f"LegSpig_{sx}{sy}", f"{s_x}*spig_x", f"{s_y}*spig_y", 0, "spig", "spig", "spig")
            ins = cyl(doc, f"LegIns_{sx}{sy}", f"{s_x}*wall_x", f"{s_y}*wall_y", "-leg_ins_h", "ins_d", "leg_ins_h + 1")
            _color(cut(doc, f"Leg_{sx}{sy}", fuse(doc, f"LegBody_{sx}{sy}", [post, spg]), ins, visible=True), "Leg")

    # ---- divider bars (T section: flange in the seats, web down between the ledges) ------------
    for i, sx in enumerate("PN", start=1):
        X = f"{SIGNS[sx]}*div_x"
        fl = box(doc, f"DivFlange_{i}", X, 0, "ledge_z - ledge_t", "div_w", "open_w - 2*tol", "ledge_t")
        web = box(doc, f"DivWeb_{i}", X, 0, 0, "div_web", "hole_w - 2*tol", "ledge_z - ledge_t")
        d = fuse(doc, f"Divider_{i}", [fl, web])
        _vis(d, True)
        _color(d, "Divider")

    doc.recompute()
    # MultiFuse copies its children's colours on recompute, so colour the final parts afterwards.
    for n in PARTS:
        _color(doc.getObject(n), next(k for k in COLORS if n.startswith(k)))
    return doc


PARTS = (["Corner_PP", "Corner_NP", "Corner_PN", "Corner_NN", "Rail_P", "Rail_N"]
         + [f"Plate_{i}" for i in range(1, 7)]
         + ["Leg_PP", "Leg_NP", "Leg_PN", "Leg_NN", "Divider_1", "Divider_2"])


def report(doc=None):
    """Bounding box and volume of every printed part, bed fit, derived sizes, pairwise interference."""
    import itertools
    doc = doc or App.getDocument(DOC)
    P = doc.getObject("Params")
    out = {}
    for n in PARTS:
        s = doc.getObject(n).Shape
        bb = s.BoundBox
        dims = sorted([bb.XLength, bb.YLength, bb.ZLength], reverse=True)
        fits = dims[1] <= P.bed_y and dims[0] <= P.bed_x
        diag = (dims[0] + dims[1]) / 2 ** 0.5  # footprint side when turned 45 degrees
        out[n] = dict(bbox=[round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)],
                      vol=round(s.Volume, 1), valid=s.isValid(), solids=len(s.Solids),
                      fits=fits or diag <= min(P.bed_x, P.bed_y), diag=None if fits else round(diag, 1))
    hits = []
    shapes = {n: doc.getObject(n).Shape for n in PARTS}
    for a, b in itertools.combinations(PARTS, 2):
        if shapes[a].BoundBox.intersect(shapes[b].BoundBox):
            v = shapes[a].common(shapes[b]).Volume
            if v > 1e-3:
                hits.append((a, b, round(v, 3)))
    fr = doc.getObject("Frame").Shape
    return dict(parts=out, interference=hits, frame_vol=round(fr.Volume, 1),
                total_vol=round(sum(p["vol"] for p in out.values()), 1),
                derived={k: getattr(P, k) for k in ("open_l", "open_w", "hole_l", "hole_w", "out_l", "out_w", "leg_h")})


def export(folder, doc=None):
    """One STL + STEP per placed part, plus the assembly STEP and the .FCStd."""
    import os, Import, Mesh, MeshPart
    doc = doc or App.getDocument(DOC)
    for sub in ("stl", "step"):
        os.makedirs(os.path.join(folder, sub), exist_ok=True)
    for n in PARTS:
        o = doc.getObject(n)
        m = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.05, AngularDeflection=0.2, Relative=False)
        m.write(os.path.join(folder, "stl", n.lower() + ".stl"))
        Import.export([o], os.path.join(folder, "step", n.lower() + ".step"))
    Import.export([doc.getObject(n) for n in PARTS], os.path.join(folder, "step", "gn_holder_assembly.step"))
    doc.saveAs(os.path.join(folder, "gn_holder.FCStd"))
