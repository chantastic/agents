// "Your PR Throughput Is Up 3x. Is Your ARR?" Pavan (Amplitude) x Greg Sabo (WorkOS), ELC 2026.
// Times are on the graphics timeline (OLD_T); scene() and T() remap them onto the plate.
// v2: fewer cartoon objects, more product/diagram language; curves smoothed in lib.jsx.

// rubber-stamp sticker over a talking head
function stamp(name, t0, t1, label, col, x, y, w, rot) {
    var s = scene(name, t0, t1, false), c = s.comp;
    box(c, "stamp", x, y, w, 150, 16, null, col, 13);
    txt(c, label, POP, 118, col, x, y);
    var L = place(s, { boil: 2 });
    center(L, x, y);
    xf(L, "ADBE Rotate Z").setValue(rot);
    keys(xf(L, "ADBE Scale"), [[s.t0, [260, 260]], [s.t0 + 0.1, [92, 92]], [s.t0 + 0.17, [100, 100]]]);
    L.property("ADBE Effect Parade").addProperty("ADBE Roughen Edges");
    return L;
}
// a null at the origin, so children drawn around (0, 0) follow it exactly
function rig(c, name, parts) {
    var n = c.layers.addNull(); n.name = name;
    xf(n, "ADBE Position").setValue([0, 0]);
    for (var i = 0; i < parts.length; i++) parts[i].parent = n;
    return n;
}
// a pipeline stage box with a mono label
function stage(c, label, x, y, w, t, ly) {
    pop(box(c, "stage " + label, x, y, w, 130, 18, WHITE, INK, 7), x, y, t, 70);
    popText(txt(c, label, MONO, 34, INK, x, ly || y), t, 70);
}

// 1. Hook: everyone's building a software factory (PR cards roll off the line)
function sFactory() {
    var s = scene("01 software factory (hook)", 0, OLD_T[2]), c = s.comp;
    ink(c, "title marker", [[[200, 445], [880, 437]]], YEL, 40, 0.1, 0.35);
    popText(txt(c, "everyone's building a", MARKER, 84, INK, 540, 285), 0, 60);
    popText(txt(c, "software factory", MARKER, 112, INK, 540, 400), 0.06, 60);
    // PR cards first, so they slide out from behind the building
    var offs = [0, 0.25, 0.5, 0.75];
    for (var i = 0; i < offs.length; i++) {
        var n = rig(c, "pr " + i, [box(c, "pr card " + i, 0, 0, 150, 84, 12, WHITE, INK, 6), txt(c, "PR", MONO, 40, INK, 0, 0)]);
        xf(n, "ADBE Position").expression = "var p=(time*0.55+" + offs[i] + ")%1; [560 + p*560, 994 + 4*Math.sin(time*20+" + i + ")]";
        xf(n, "ADBE Rotate Z").setValue((i % 2) ? 3 : -3);
    }
    // one outline: sawtooth roof, a flat section, and the chimney rising out of it
    var outline = [[110, 1050], [110, 790], [230, 710], [230, 790], [350, 710], [350, 790], [470, 710], [470, 790],
        [505, 790], [505, 610], [560, 610], [560, 790], [600, 790], [600, 1050]];
    pop(blob(c, "building", outline, PAPER, INK, 11), 355, 1050, 0, 70);
    var xs = [170, 290, 410];
    for (var w = 0; w < xs.length; w++) pop(box(c, "window " + w, xs[w], 890, 80, 68, 6, YEL, INK, 7), xs[w], 890, 0.08 + w * 0.04);
    pop(box(c, "door", 545, 990, 70, 110, 4, INK, INK, 6), 545, 1050, 0.1);
    ink(c, "smoke", [curve([[532, 595], [514, 565], [546, 535], [526, 505]])], GREY, 8, 0.1, 0.6);
    ink(c, "belt", [[[600, 1040], [1000, 1040]], [[600, 1078], [1000, 1078]]], INK, 8, 0, 0.3);
    for (var r = 0; r < 5; r++) pop(ell(c, "roller " + r, 640 + r * 85, 1059, 30, 30, null, INK, 5), 640 + r * 85, 1059, 0.1 + r * 0.03);
    ink(c, "ground", [[[80, 1050], [600, 1050]]], INK, 10, 0, 0.25);
    // merged-PR counter
    pop(box(c, "counter card", 820, 790, 330, 120, 16, WHITE, INK, 6), 820, 790, 0.12);
    popText(txt(c, "PRs MERGED", MONO_M, 26, GREY, 820, 758, { tracking: 80 }), 0.12);
    var ctr = txt(c, "1,180", MONO, 54, INK, 820, 812);
    ctr.property("ADBE Text Properties").property("ADBE Text Document").expression =
        "var v=Math.floor(linear(time,0,3.8,1180,1460)).toString(); v.substr(0,v.length-3)+','+v.substr(v.length-3)";
    popText(ctr, 0.12);
    return place(s);
}

// 1b. sticker over Greg: good = ?
function sGood() {
    var s = scene("02 good tag", 5.15, OLD_T[3], false), c = s.comp;
    box(c, "tag", 200, 420, 300, 116, 58, YEL, INK, 7);
    txt(c, "good = ?", HAND, 74, INK, 200, 424);
    var L = place(s, { boil: 2 });
    center(L, 200, 420); xf(L, "ADBE Rotate Z").setValue(-8);
    keys(xf(L, "ADBE Scale"), [[s.t0, [0, 0]], [s.t0 + 0.12, [112, 112]], [s.t0 + 0.2, [100, 100]]]);
    return L;
}

// 2. the real outcome: a dashboard of what the business measures
function sOutcomes() {
    var s = scene("03 real outcomes", 8.78, OLD_T[4]), c = s.comp, T = s.T;
    ink(c, "title marker", [[[250, 380], [830, 372]]], YEL, 36, 0.1, 0.35);
    popText(txt(c, "the real outcome", HAND, 112, INK, 540, 335), 0, 60);
    var rows = [["ADOPTION", T(10.6)], ["ARR", T(11.35)], ["VALUE TO USERS", T(12.55)]];
    var ys = [580, 800, 1020];
    for (var i = 0; i < 3; i++) {
        var y = ys[i], t = rows[i][1];
        pop(box(c, "tile " + i, 540, y, 860, 180, 22, WHITE, INK, 7), 540, y, 0.04 * i, 70);
        popText(txt(c, rows[i][0], MONO, 44, INK, 150, y + 15, { left: true, tracking: 40 }), t);
        var sp = curve([[580, y + 45], [650, y + 30], [720, y + 38], [790, y + 5], [860, y - 15], [920, y - 45]]);
        ink(c, "spark " + i, [sp], GRN, 9, t, t + 0.4);
        pop(ell(c, "spark dot " + i, 920, y - 45, 26, 26, GRN, null), 920, y - 45, t + 0.38);
    }
    return place(s);
}

// 3. sticker over Pavan: 3x PRs
function s3x() { return stamp("04 3x prs stamp", 15.02, 16.3, "3× PRs", GRN, 245, 430, 330, -10); }

// 4. PRs rocket up; ARR and adoption don't. The gap is the point.
function sDivergence() {
    var s = scene("05 divergence", OLD_T[5], OLD_T[7]), c = s.comp, T = s.T;
    var t1 = txt(c, "3× the PRs...", HAND, 112, INK, 540, 330); popText(t1, 0, 60); between(t1, null, T(20.35));
    popText(txt(c, "3× the ARR?", HAND, 112, RED, 540, 330), T(20.35));
    pop(box(c, "chart", 540, 830, 900, 780, 26, WHITE, INK, 8), 540, 830, 0, 70);
    ink(c, "axes", [[[170, 500], [170, 1100], [960, 1100]]], INK, 8, 0, 0.2);
    ink(c, "prs line", [curve([[170, 1090], [330, 1045], [480, 945], [620, 800], [760, 650], [900, 530]])], GRN, 13, 0, 0.5);
    popText(txt(c, "PRs", HAND, 70, GRN, 760, 540), 0.25);
    ink(c, "arr line", [curve([[170, 1090], [330, 1076], [480, 1074], [620, 1062], [760, 1060], [900, 1045]])], BLU, 12, T(19.1), T(19.75));
    popText(txt(c, "ARR", HAND, 64, BLU, 845, 1000), T(19.6));
    ink(c, "gap bracket", [[[922, 532], [945, 532], [945, 1043], [922, 1043]]], RED, 7, T(20.35), T(20.6));
    popText(txt(c, "the gap", HAND, 66, RED, 830, 820), T(20.5));
    ink(c, "adoption line", [curve([[170, 1092], [330, 1088], [480, 1084], [620, 1086], [760, 1080], [900, 1076]])], ORANGE, 10, T(21.9), T(22.5));
    popText(txt(c, "adoption", HAND, 58, ORANGE, 860, 1150), T(22.35));
    return place(s);
}

// 5. easy to increase the surface area: a settings screen that keeps growing
function sBloat() {
    var s = scene("06 surface area", OLD_T[9], OLD_T[10]), c = s.comp, T = s.T;
    popText(txt(c, "more surface area", HAND, 108, INK, 540, 330), 0, 60);
    pop(box(c, "window", 540, 845, 860, 760, 30, WHITE, INK, 9), 540, 845, 0, 70);
    pop(ink(c, "frame lines", [[[110, 530], [970, 530]], [[330, 530], [330, 1225]]], INK, 6, null), 540, 845, 0, 70);
    for (var d = 0; d < 3; d++) pop(ell(c, "dot " + d, 160 + d * 45, 497, 22, 22, null, INK, 5), 540, 845, 0, 70);
    // sidebar nav
    var nav = ["General", "Billing", "Team", "Integrations", "AI assistant", "Labs", "Workflows", "Insights", "Webhooks", "Automations", "Templates", "Beta"];
    for (var i = 0; i < nav.length; i++) {
        var L = txt(c, nav[i], MONO_M, 22, i < 3 ? INK : BLU, 140, 590 + i * 46, { left: true });
        if (i < 3) popText(L, 0); else popText(L, T(29.55) + (i - 3) * 0.17);
    }
    // tabs
    var tabs = ["Overview", "Analytics", "AI", "Labs", "Beta"], x = 360;
    for (var j = 0; j < tabs.length; j++) {
        var w = 34 + tabs[j].length * 15, cx = x + w / 2, tt = j ? T(29.7) + (j - 1) * 0.25 : 0;
        pop(box(c, "tab " + j, cx, 585, w, 50, 12, j ? hex("#FFF4B8") : hex("#EFEAE0"), INK, 5), cx, 585, tt, j ? 0 : 70);
        popText(txt(c, tabs[j], MONO_M, 24, INK, cx, 587), tt, j ? 0 : 70);
        x += w + 10;
    }
    // toggle rows
    var rows = [["Notifications", 1], ["Dark mode", 0], ["AI suggestions", 1], ["Beta features", 1], ["Smart replies", 0], ["Auto-sync", 1], ["Experiments", 1]];
    for (var k = 0; k < rows.length; k++) {
        var y = 680 + k * 72, t = k < 2 ? 0 : T(29.65) + (k - 2) * 0.22, on = rows[k][1];
        popText(txt(c, rows[k][0], MONO_M, 26, INK, 360, y + 9, { left: true }), t);
        pop(box(c, "toggle " + k, 900, y, 84, 44, 22, on ? GRN : hex("#D6D1C6"), INK, 5), 900, y, t, k < 2 ? 70 : 0);
        pop(ell(c, "knob " + k, on ? 920 : 880, y, 32, 32, WHITE, INK, 4), 900, y, t, k < 2 ? 70 : 0);
    }
    return place(s);
}

// 6. a lot more complex, outcomes stuck at zero
function sComplex() {
    var s = scene("07 complex", OLD_T[11], OLD_T[12]), c = s.comp, T = s.T;
    popText(txt(c, "a lot more complex", HAND, 108, INK, 540, 330), 0, 60);
    var pts = [];
    for (var i = 0; i < 70; i++) pts.push([540 + 330 * Math.sin(i * 1.73) * Math.cos(i * 0.31), 655 + 135 * Math.sin(i * 2.29 + 1) * Math.cos(i * 0.47)]);
    ink(c, "tangle", [curve(pts)], INK, 6, 0, 1.0);
    ink(c, "arc red", [arc(540, 1120, 230, 180, 126, 20)], RED, 38, 0, 0.12);
    ink(c, "arc yellow", [arc(540, 1120, 230, 118, 62, 20)], YEL, 38, 0.06, 0.18);
    ink(c, "arc green", [arc(540, 1120, 230, 54, 0, 20)], GRN, 38, 0.12, 0.24);
    var nd = ink(c, "needle", [[[540, 1120], [540, 935]]], INK, 14, null);
    center(nd, 540, 1120);
    keys(xf(nd, "ADBE Rotate Z"), [[0, -76], [T(38.0), -76], [T(38.25), -52], [T(38.45), -78], [T(38.55), -74]]);
    ell(c, "hub", 540, 1120, 50, 50, INK, null);
    popText(txt(c, "business outcomes", HAND, 62, INK, 540, 1200), T(38.75));
    return place(s);
}

// 7. sticker over Greg: SLOP
function sSlop() { return stamp("08 slop stamp", 40.70, 41.95, "SLOP", PINK, 185, 420, 300, -9); }

// 8. when it was hard to build: the build stage was the friction
function sFriction() {
    var s = scene("09 slow pipeline", OLD_T[15], OLD_T[17]), c = s.comp, T = s.T;
    popText(txt(c, "when it was hard to build", HAND, 96, INK, 540, 330), 0, 60);
    stage(c, "idea", 165, 700, 150, 0);
    stage(c, "spec", 345, 700, 150, 0.04);
    stage(c, "build", 615, 700, 330, 0.08, 668);
    stage(c, "ship", 885, 700, 150, 0.12);
    ink(c, "track", [[[165, 840], [885, 840]]], GREY, 6, 0, 0.3);
    var bg = box(c, "progress bg", 615, 728, 280, 26, 13, hex("#E4DED2"), null); pop(bg, 615, 728, 0.08, 70);
    var bar = box(c, "progress", 615, 728, 280, 26, 13, YEL, INK, 4); center(bar, 475, 728);
    keys(xf(bar, "ADBE Scale"), [[T(44.5), [0, 100]], [T(47.3), [100, 100]]]);
    var tok = ell(c, "feature", 0, 0, 46, 46, YEL, INK, 6);
    keys(xf(tok, "ADBE Position"), [[0, [165, 840]], [T(44.0), [165, 840]], [T(44.4), [345, 840]], [T(44.8), [470, 840]], [T(47.3), [760, 840]]]);
    popText(txt(c, "friction", HAND, 74, RED, 600, 560, { rot: -3 }), T(46.6));
    ink(c, "gate", [[[795, 610], [795, 880]]], RED, 10, T(47.95), T(48.15));
    var pz = c.layers.addNull(); pz.name = "pause"; xf(pz, "ADBE Position").setValue([820, 545]);
    var pp = [ell(c, "pause circle", 820, 545, 110, 110, YEL, INK, 6), box(c, "pause bar a", 802, 545, 16, 50, 4, INK, null), box(c, "pause bar b", 838, 545, 16, 50, 4, INK, null)];
    for (var i = 0; i < pp.length; i++) pp[i].parent = pz;
    keys(xf(pz, "ADBE Scale"), [[T(49.3), [0, 0]], [T(49.42), [112, 112]], [T(49.5), [100, 100]]]);
    pop(box(c, "review card", 540, 1050, 860, 150, 20, WHITE, INK, 7), 540, 1050, T(50.05));
    pop(box(c, "checkbox", 175, 1050, 58, 58, 8, null, INK, 6), 175, 1050, T(50.1));
    popText(txt(c, "is this really necessary?", HAND, 70, INK, 570, 1056), T(51.45));
    return place(s);
}

// 9. now: give the prompt, features pour out
function sPrompt() {
    var s = scene("10 prompt features", OLD_T[18], OLD_T[19]), c = s.comp, T = s.T;
    popText(txt(c, "now it's easy", HAND, 108, INK, 540, 330), 0, 60);
    pop(box(c, "prompt", 540, 520, 900, 120, 22, INK, INK, 6), 540, 520, 0, 70);
    var ty = c.layers.addText(">");
    var sp = ty.property("ADBE Text Properties").property("ADBE Text Document"), td = sp.value;
    td.resetCharStyle(); td.font = MONO; td.fontSize = 46; td.fillColor = YEL; td.applyFill = true; td.applyStroke = false;
    td.justification = ParagraphJustification.LEFT_JUSTIFY; sp.setValue(td);
    sp.expression = "var t='> add a feature'; var n=Math.floor(linear(time,0.05," + T(55.6).toFixed(2) + ",1,t.length)); t.substr(0,n)+((Math.floor(time*3)%2==0)?'_':' ')";
    xf(ty, "ADBE Position").setValue([130, 536]);
    var f = ["dark mode", "AI chat", "export", "widgets", "beta tab", "templates", "share", "labs", "emoji", "sync", "bots", "pro"];
    var pos = [[540, 1130, 3], [330, 1130, -5], [750, 1130, 6], [430, 1050, -4], [650, 1050, 5], [240, 1050, 7], [840, 1050, -6], [540, 970, 2], [330, 970, -7], [750, 970, 4], [440, 890, 6], [640, 890, -3]];
    for (var i = 0; i < f.length; i++) {
        var p = pos[i], nl = c.layers.addNull(); nl.name = "feature " + i;
        xf(nl, "ADBE Position").setValue([p[0], p[1]]);
        var parts = [box(c, "feature card " + i, p[0], p[1], 210, 74, 12, WHITE, INK, 6), txt(c, f[i], MONO, 30, INK, p[0], p[1])];
        for (var k = 0; k < parts.length; k++) parts[k].parent = nl;
        xf(nl, "ADBE Rotate Z").setValue(p[2]);
        var t = T(55.95) + i * 0.07;
        keys(xf(nl, "ADBE Position"), [[t - 1 / FPS, [540, 520]], [t, [540, 600]], [t + 0.2, [p[0], p[1] + 10]], [t + 0.26, [p[0], p[1]]]]);
        keys(xf(nl, "ADBE Scale"), [[t - 1 / FPS, [0, 0]], [t, [40, 40]], [t + 0.2, [100, 100]]]);
    }
    return place(s);
}

// 10. productive friction: a fast pipeline with a checkpoint that cuts some features
function sGate() {
    var s = scene("11 productive friction", OLD_T[19], OLD_T[21]), c = s.comp, T = s.T;
    ink(c, "title marker", [[[150, 400], [930, 392]]], YEL, 40, T(58.55), T(58.75));
    popText(txt(c, "productive friction", MARKER, 108, INK, 540, 345), T(58.0));
    ink(c, "track", [[[120, 880], [960, 880]]], GREY, 6, 0, 0.25);
    // features flow left to right; every other one is cut at the checkpoint and drops into the bin
    for (var i = 0; i < 6; i++) {
        var off = (i / 6).toFixed(3), rej = (i % 2) ? "true" : "false";
        var card = box(c, "feature card " + i, 0, 0, 74, 44, 10, WHITE, INK, 5);
        var n = rig(c, "feature " + i, [card]);
        xf(n, "ADBE Position").expression = "var p=(time*0.42+" + off + ")%1, x=120+p*840, y=880; if (" + rej + " && x>630) y=880+(x-630)*1.6; [x,y]";
        xf(card, "ADBE Opacity").expression =
            "var p=(time*0.42+" + off + ")%1, x=120+p*840, o=linear(x,120,170,0,100)*linear(x,900,960,1,0); if (" + rej + " && x>630) o=o*linear(x,630,770,1,0); o";
    }
    stage(c, "idea", 165, 700, 150, 0);
    stage(c, "build", 395, 700, 150, 0.04);
    pop(blob(c, "checkpoint", [[630, 600], [730, 700], [630, 800], [530, 700]], YEL, INK, 7), 630, 700, 0.08, 70);
    popText(txt(c, "worth it?", HAND, 46, INK, 630, 703), 0.08, 70);
    stage(c, "ship", 885, 700, 150, 0.12);
    ink(c, "bin", [[[650, 1060], [668, 1150], [782, 1150], [800, 1060]]], INK, 7, 0, 0.25);
    popText(txt(c, "cut", HAND, 56, RED, 875, 1115), 0.1, 70);
    popText(txt(c, "PDLC", MONO_M, 30, GREY, 165, 600, { tracking: 120 }), T(60.3));
    return place(s);
}

var SCENES = [sFactory, sGood, sOutcomes, s3x, sDivergence, sBloat, sComplex, sSlop, sFriction, sPrompt, sGate];
