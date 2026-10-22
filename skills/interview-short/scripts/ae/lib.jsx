// interview-short: After Effects library for hand-drawn vertical shorts.
// Included by build.jsx after data.jsxinc (CAPTIONS, CLIPS, TOTAL, OLD_T, NAME, PLATE) and sfx.jsxinc
// (SFX_HITS, SFX_CUES), before scenes.jsx (scene functions + var SCENES = [...]). ROOT is set by build.jsx.
var W = 1080, H = 1920, FPS = FPS_NUM / FPS_DEN;
var LOG = [];

function hex(h) { return [parseInt(h.substr(1, 2), 16) / 255, parseInt(h.substr(3, 2), 16) / 255, parseInt(h.substr(5, 2), 16) / 255]; }
var INK = hex("#1B1B1F"), PAPER = hex("#F4EFE4"), YEL = hex("#FFD400"), RED = hex("#E5484D"), GRN = hex("#30A46C"),
    BLU = hex("#6E7BFF"), WHITE = [1, 1, 1], PURP = hex("#8B5CF6"), PINK = hex("#EC4899"), NAVY = hex("#161A2B"),
    GREY = hex("#8E8E96"), ORANGE = hex("#FF7A1A");
var HAND = "Caveat-Bold", MARKER = "CoveredByYourGrace", POP = "Bangers-Regular", MONO = "IBMPlexMono-Bold",
    MONO_M = "IBMPlexMono-Medium", CAPTION = "AvenirNext-Heavy";

// ---------- keyframe helpers ----------
function ease(p) {
    for (var k = 1; k <= p.numKeys; k++) {
        var e = new KeyframeEase(0, 70);
        try { p.setTemporalEaseAtKey(k, [e], [e]); } catch (a) {
            try { p.setTemporalEaseAtKey(k, [e, e], [e, e]); } catch (b) {
                try { p.setTemporalEaseAtKey(k, [e, e, e], [e, e, e]); } catch (c) {} } }
    }
}
function keys(p, list, hold) { // list: [[t, v], ...]
    for (var i = 0; i < list.length; i++) p.setValueAtTime(list[i][0], list[i][1]);
    if (hold) { for (var k = 1; k <= p.numKeys; k++) p.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD); }
    else ease(p);
}
function xf(L, name) { return L.property("ADBE Transform Group").property(name); }
function center(L, x, y) { xf(L, "ADBE Anchor Point").setValue([x, y]); xf(L, "ADBE Position").setValue([x, y]); }
// pop in at t: scale 0 -> 112 -> 100, around (x, y)
function pop(L, x, y, t, from) {
    center(L, x, y);
    var f = (from === undefined) ? 0 : from;
    // anything on screen at the cut is already mostly there, so the handoff never shows blank paper
    if (t < 0.15) { t = 0; if (f < 85) f = 85; }
    keys(xf(L, "ADBE Scale"), [[t, [f, f]], [t + 0.12, [112, 112]], [t + 0.2, [100, 100]]]);
    if (f > 0) keys(xf(L, "ADBE Opacity"), [[t - 0.01, 0], [t, 100]], true);
    return L;
}
function between(L, a, b) { if (a !== null) L.inPoint = a; if (b !== null) L.outPoint = b; return L; }

// ---------- shapes ----------
function shape(c, name) {
    var L = c.layers.addShape(); L.name = name;
    xf(L, "ADBE Anchor Point").setValue([0, 0]); xf(L, "ADBE Position").setValue([0, 0]);
    return L;
}
function contents(L) { return L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group").property("ADBE Vectors Group"); }
// pts.smooth (set by curve(), wobble(), arc()) turns the points into a Catmull-Rom curve instead of straight segments
function addPath(g, pts, closed) {
    var p = g.addProperty("ADBE Vector Shape - Group"), s = new Shape();
    s.vertices = pts; s.closed = !!closed;
    if (pts.smooth) {
        var n = pts.length, ins = [], outs = [];
        for (var i = 0; i < n; i++) {
            var a = closed ? pts[(i - 1 + n) % n] : pts[Math.max(i - 1, 0)], b = closed ? pts[(i + 1) % n] : pts[Math.min(i + 1, n - 1)];
            var tx = (b[0] - a[0]) / 6, ty = (b[1] - a[1]) / 6;
            ins.push([-tx, -ty]); outs.push([tx, ty]);
        }
        s.inTangents = ins; s.outTangents = outs;
    }
    p.property("ADBE Vector Shape").setValue(s);
}
function curve(pts) { pts.smooth = true; return pts; }
function addRect(g, x, y, w, h, r) {
    var p = g.addProperty("ADBE Vector Shape - Rect");
    p.property("ADBE Vector Rect Size").setValue([w, h]); p.property("ADBE Vector Rect Position").setValue([x, y]);
    p.property("ADBE Vector Rect Roundness").setValue(r || 0);
}
function addEll(g, x, y, w, h) {
    var p = g.addProperty("ADBE Vector Shape - Ellipse");
    p.property("ADBE Vector Ellipse Size").setValue([w, h]); p.property("ADBE Vector Ellipse Position").setValue([x, y]);
}
function addTrim(g, t0, t1) {
    var e = g.addProperty("ADBE Vector Filter - Trim").property("ADBE Vector Trim End");
    if (t0 < 0.15) keys(e, [[0, 40], [Math.max(t1 - t0, 0.12), 100]]);  // already part-drawn at the cut
    else keys(e, [[t0, 0], [t1, 100]]);
}
function addStroke(g, col, w) {
    var s = g.addProperty("ADBE Vector Graphic - Stroke");
    s.property("ADBE Vector Stroke Color").setValue(col); s.property("ADBE Vector Stroke Width").setValue(w);
    s.property("ADBE Vector Stroke Line Cap").setValue(2); s.property("ADBE Vector Stroke Line Join").setValue(2);
}
function addFill(g, col, opacity) {
    var f = g.addProperty("ADBE Vector Graphic - Fill");
    f.property("ADBE Vector Fill Color").setValue(col);
    if (opacity !== undefined) f.property("ADBE Vector Fill Opacity").setValue(opacity);
    return f;
}
// ink line(s) drawn on between t0 and t1 (no fill)
function ink(c, name, paths, col, w, t0, t1, closed) {
    var L = shape(c, name), g = contents(L);
    for (var i = 0; i < paths.length; i++) addPath(g, paths[i], closed);
    if (t0 !== null) addTrim(g, t0, t1);
    addStroke(g, col, w);
    return L;
}
// filled, outlined box
function box(c, name, x, y, w, h, r, fillCol, strokeCol, sw) {
    var L = shape(c, name), g = contents(L);
    addRect(g, x, y, w, h, r);
    if (strokeCol) addStroke(g, strokeCol, sw || 7);
    if (fillCol) addFill(g, fillCol);
    return L;
}
function blob(c, name, pts, fillCol, strokeCol, sw) {
    var L = shape(c, name), g = contents(L);
    addPath(g, pts, true);
    if (strokeCol) addStroke(g, strokeCol, sw || 7);
    if (fillCol) addFill(g, fillCol);
    return L;
}
function ell(c, name, x, y, w, h, fillCol, strokeCol, sw) {
    var L = shape(c, name), g = contents(L);
    addEll(g, x, y, w, h);
    if (strokeCol) addStroke(g, strokeCol, sw || 7);
    if (fillCol) addFill(g, fillCol);
    return L;
}
function arc(cx, cy, r, a0, a1, n) {
    var pts = [];
    for (var i = 0; i <= n; i++) { var a = (a0 + (a1 - a0) * i / n) * Math.PI / 180; pts.push([cx + r * Math.cos(a), cy - r * Math.sin(a)]); }
    return curve(pts);
}
function star(cx, cy, r) {
    var pts = [];
    for (var i = 0; i < 8; i++) { var a = i * Math.PI / 4 - Math.PI / 2, rr = (i % 2) ? r * 0.32 : r; pts.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]); }
    return pts;
}
function wobble(cx, cy, R, seed, n, sy) {
    if (sy === undefined) sy = 0.92;
    var pts = [];
    for (var i = 0; i < n; i++) {
        var a = 2 * Math.PI * i / n;
        var r = R * (1 + 0.05 * Math.sin(3 * a + seed) + 0.025 * Math.sin(5 * a + seed * 1.7) + 0.01 * Math.sin(7 * a + seed * 0.3));
        pts.push([cx + r * Math.cos(a), cy + r * sy * Math.sin(a)]);
    }
    return curve(pts);
}
function arrowHead(x, y, ang, s) { // tip at (x, y), pointing along ang (deg)
    var a = ang * Math.PI / 180, b = 0.5;
    return [[x - s * Math.cos(a - b), y - s * Math.sin(a - b)], [x, y], [x - s * Math.cos(a + b), y - s * Math.sin(a + b)]];
}
function arrow(c, name, x0, y0, x1, y1, col, w, t0, t1) {
    var ang = Math.atan2(y1 - y0, x1 - x0) * 180 / Math.PI;
    return ink(c, name, [[[x0, y0], [x1, y1]], arrowHead(x1, y1, ang, 34)], col, w, t0, t1);
}
function check(c, name, x, y, s, col, t0) { return ink(c, name, [[[x - s, y], [x - s * 0.35, y + s * 0.7], [x + s, y - s * 0.9]]], col, s * 0.28, t0, t0 + 0.14); }
function cross(c, name, x, y, s, col, w, t0) {
    var a = ink(c, name + " a", [[[x - s, y - s], [x + s, y + s]]], col, w, t0, t0 + 0.1);
    var b = ink(c, name + " b", [[[x + s, y - s], [x - s, y + s]]], col, w, t0 + 0.1, t0 + 0.2);
    return [a, b];
}

// ---------- text ----------
// centred on (x, y) unless opts.left, in which case (x, y) is the baseline start
function txt(c, s, font, size, col, x, y, opts) {
    opts = opts || {};
    var L = opts.box ? c.layers.addBoxText(opts.box, s) : c.layers.addText(s);
    var sp = L.property("ADBE Text Properties").property("ADBE Text Document"), td = sp.value;
    td.resetCharStyle(); td.resetParagraphStyle();
    td.font = font; td.fontSize = size; td.fillColor = col; td.applyFill = true;
    if (opts.stroke) { td.applyStroke = true; td.strokeColor = opts.stroke; td.strokeWidth = opts.sw || 10; td.strokeOverFill = false; }
    else td.applyStroke = false;
    if (opts.tracking) td.tracking = opts.tracking;
    td.justification = opts.left ? ParagraphJustification.LEFT_JUSTIFY : ParagraphJustification.CENTER_JUSTIFY;
    sp.setValue(td);
    if (opts.left) { xf(L, "ADBE Anchor Point").setValue([0, 0]); xf(L, "ADBE Position").setValue([x, y]); }
    else {
        var r = L.sourceRectAtTime(0, false);
        center(L, x, y);
        xf(L, "ADBE Anchor Point").setValue([r.left + r.width / 2, r.top + r.height / 2]);
    }
    if (opts.rot) xf(L, "ADBE Rotate Z").setValue(opts.rot);
    return L;
}
// pop a text layer that was centred by txt()
function popText(L, t, from) {
    var a = xf(L, "ADBE Anchor Point").value, p = xf(L, "ADBE Position").value;
    var f = (from === undefined) ? 0 : from;
    // anything on screen at the cut is already mostly there, so the handoff never shows blank paper
    if (t < 0.15) { t = 0; if (f < 85) f = 85; }
    keys(xf(L, "ADBE Scale"), [[t, [f, f]], [t + 0.12, [112, 112]], [t + 0.2, [100, 100]]]);
    if (f > 0) keys(xf(L, "ADBE Opacity"), [[t - 0.01, 0], [t, 100]], true);
    return L;
}

// ---------- scenes ----------
var proj, main, folder;
// map a time on the original timeline onto the frame-exact plate, snapped to a frame
function remap(t) {
    var i = 0;
    while (i + 1 < OLD_T.length && OLD_T[i + 1] <= t + 1e-6) i++;
    return frame(CLIPS[i][0] + (t - OLD_T[i]));
}
function frame(t) { return Math.round(t * FPS) / FPS; }
function scene(name, t0, t1, paper) {
    t0 = remap(t0); t1 = remap(t1);
    var c = proj.items.addComp(name, W, H, 1, t1 - t0, FPS);
    c.parentFolder = folder;
    if (paper !== false) {
        var p = c.layers.addSolid(PAPER, "paper", W, H, 1, t1 - t0);
        var nz = p.property("ADBE Effect Parade").addProperty("ADBE Noise");
        nz.property("ADBE Noise-0001").setValue(5);
        nz.property("ADBE Noise-0002").setValue(0);
    }
    return { comp: c, t0: t0, t1: t1, T: function (t) { return remap(t) - t0; } };
}
// hand-drawn line boil: turbulent displace that re-seeds 8x a second
function boil(c, amount) {
    var a = c.layers.addSolid([1, 1, 1], "boil", W, H, 1, c.duration);
    a.adjustmentLayer = true;
    var td = a.property("ADBE Effect Parade").addProperty("ADBE Turbulent Displace");
    td.property("ADBE Turbulent Displace-0002").setValue(amount || 1.5);
    td.property("ADBE Turbulent Displace-0003").setValue(16);
    td.property("ADBE Turbulent Displace-0006").expression = "posterizeTime(8); time*997";
    a.moveToBeginning();
}
function place(s, opts) {
    boil(s.comp, opts && opts.boil);
    var L = main.layers.add(s.comp);
    L.startTime = s.t0;
    LOG.push("placed\t" + s.comp.name + "\t" + s.t0.toFixed(4) + "\t" + s.t1.toFixed(4) + "\t" + (s.comp.layer("paper") ? "cutaway" : "sticker"));
    L.name = s.comp.name;
    return L;
}
// a dark "lights off" multiply overlay
function dim(c, t0, t1, amount) {
    var d = c.layers.addSolid(NAVY, "lights off", W, H, 1, c.duration);
    d.blendingMode = BlendingMode.MULTIPLY;
    keys(xf(d, "ADBE Opacity"), [[t0, 0], [t1, amount]]);
    return d;
}

// ---------- captions ----------
function captions() {
    for (var i = 0; i < CAPTIONS.length; i++) {
        var e = CAPTIONS[i], t = e[0], end = (i + 1 < CAPTIONS.length) ? CAPTIONS[i + 1][0] : TOTAL;
        var O = txt(main, e[1], CAPTION, 92, INK, 540, 1330, { box: [980, 240], stroke: INK, sw: 20, tracking: 10 });
        var L = txt(main, e[1], CAPTION, 92, e[2] == "Q" ? YEL : WHITE, 540, 1330, { box: [980, 240], tracking: 10 });
        O.name = "cap " + i + " outline"; L.name = "cap " + i + " " + e[1];
        var pair = [O, L];
        for (var j = 0; j < 2; j++) { between(pair[j], t, end); keys(xf(pair[j], "ADBE Scale"), [[t, [86, 86]], [t + 0.1, [100, 100]]]); }
    }
}

// ---------- sound effects ----------
// one audio layer per cue; the cut's hit offset lands on the graphic's frame
function sfx() {
    var fold = proj.items.addFolder("sfx"), items = {};
    for (var name in SFX_HITS) {
        var it = proj.importFile(new ImportOptions(new File(ROOT + "/sfx/cut/" + name + ".wav")));
        it.parentFolder = fold; items[name] = it;
    }
    for (var i = SFX_CUES.length - 1; i >= 0; i--) {
        var q = SFX_CUES[i], L = main.layers.add(items[q[0]]);
        L.startTime = remap(q[1]) - SFX_HITS[q[0]];
        L.name = "sfx " + q[0] + " @" + q[1];
        L.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([q[2], q[2]]);
        L.moveToEnd();
    }
}

// ---------- main ----------
function build() {
    app.newProject();
    proj = app.project;
    folder = proj.items.addFolder("graphics");
    var plateItem = proj.importFile(new ImportOptions(new File(ROOT + "/" + PLATE)));
    main = proj.items.addComp("MAIN " + NAME, W, H, 1, TOTAL, FPS);
    var plate = main.layers.add(plateItem);
    plate.name = "plate (talking heads)";
    // jump zooms: alternate 100/112% on back-to-back close-ups
    center(plate, 540, 760);
    var sc = xf(plate, "ADBE Scale"), z = 100, prevClose = false;
    for (var i = 0; i < CLIPS.length; i++) {
        var close = CLIPS[i][2] == "close";
        z = (close && prevClose && z == 100) ? 112 : 100;
        sc.setValueAtTime(CLIPS[i][0], [z, z]);
        prevClose = close;
    }
    for (var k = 1; k <= sc.numKeys; k++) sc.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD);

    for (var f = 0; f < SCENES.length; f++) {
        try { SCENES[f](); } catch (err) { LOG.push("scene " + f + ": " + err.toString() + " line " + err.line); }
    }
    try { captions(); } catch (err2) { LOG.push("captions: " + err2.toString() + " line " + err2.line); }
    if (SFX_CUES.length) try { sfx(); } catch (err4) { LOG.push("sfx: " + err4.toString() + " line " + err4.line); }
    main.openInViewer();

    proj.save(new File(ROOT + "/" + NAME + ".aep"));

    // queue a render
    var rq = proj.renderQueue.items.add(main);
    try { rq.applyTemplate("Best Settings"); } catch (e3) {}
    var om = rq.outputModule(1), tpl = om.templates, pick = null;
    for (var j = 0; j < tpl.length; j++) if (/H\.264/.test(tpl[j]) && /Match Render/.test(tpl[j]) && /40/.test(tpl[j])) pick = tpl[j];
    for (j = 0; j < tpl.length && !pick; j++) if (/H\.264/.test(tpl[j])) pick = tpl[j];
    for (j = 0; j < tpl.length && !pick; j++) if (/High Quality/.test(tpl[j])) pick = tpl[j];
    if (pick) om.applyTemplate(pick);
    var ext = (pick && /H\.264/.test(pick)) ? ".mp4" : ".mov";
    var outDir = new Folder(ROOT + "/render"); if (!outDir.exists) outDir.create();
    om.file = new File(ROOT + "/render/" + NAME + "-graphics" + ext);
    proj.save();
    LOG.push("templates: " + tpl.join(" | "));
    LOG.push("picked: " + pick);
}

function run() {
    app.beginUndoGroup("build " + NAME);
    try { build(); } catch (e) { LOG.push("FATAL: " + e.toString() + " line " + e.line); }
    app.endUndoGroup();
    var lf = new File(ROOT + "/build.log"); lf.open("w"); lf.write(LOG.join("\n")); lf.close();
    return LOG.join("\n");
}
