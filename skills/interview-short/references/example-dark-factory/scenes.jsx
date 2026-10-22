// Worked example: the 14 scenes of "Nobody runs a dark software factory" (Andrew Churchill x Michael Grinich).
// Times are on the graphics timeline (OLD_T); scene() and T() remap them onto the plate.
// 1. Hook: a factory whose lights go out
function sFactory() {
    var s = scene("01 factory (hook)", 0, OLD_T[1]);
    var c = s.comp;
    ink(c, "title marker", [[[170, 440], [910, 430]]], YEL, 40, 0.15, 0.4);
    popText(txt(c, "nobody runs a", MARKER, 92, INK, 540, 280), 0, 60);
    popText(txt(c, "dark software factory", MARKER, 104, INK, 540, 398), 0.08, 60);
    ink(c, "ground", [[[110, 1080], [970, 1080]]], INK, 10, 0.05, 0.3);
    ink(c, "building", [[[200, 1080], [200, 800], [340, 710], [340, 800], [480, 710], [480, 800], [620, 710], [620, 800], [880, 800], [880, 1080]]], INK, 11, 0.05, 0.42);
    ink(c, "chimney", [[[730, 800], [730, 600], [800, 600], [800, 800]]], INK, 11, 0.2, 0.42);
    ink(c, "door", [[[490, 1080], [490, 980], [570, 980], [570, 1080]]], INK, 9, 0.3, 0.45);
    var xs = [270, 400, 680, 805];
    for (var i = 0; i < xs.length; i++) {
        var L = shape(c, "window " + i), g = contents(L);
        addRect(g, xs[i], 900, 84, 72, 6); addStroke(g, INK, 7);
        keys(addFill(g, YEL).property("ADBE Vector Fill Color"), [[0, YEL], [0.58 + i * 0.07, NAVY]], true);
        pop(L, xs[i], 900, 0.3 + i * 0.04);
    }
    var puffs = [[775, 555, 44], [815, 510, 58], [868, 462, 72]];
    for (var k = 0; k < puffs.length; k++) pop(ell(c, "smoke " + k, puffs[k][0], puffs[k][1], puffs[k][2], puffs[k][2] * 0.8, null, INK, 6), puffs[k][0], puffs[k][1], 0.35 + k * 0.08);
    dim(c, 0.95, 1.15, 78);
    return place(s);
}

// 2. "lights off" switch
function sSwitch() {
    var s = scene("02 lights off", 5.85, OLD_T[4]), c = s.comp, T = s.T;
    var plate = box(c, "plate", 540, 780, 380, 600, 40, WHITE, INK, 10); pop(plate, 540, 780, 0);
    var sc = [ell(c, "screw a", 540, 525, 24, 24, null, INK, 5), ell(c, "screw b", 540, 1035, 24, 24, null, INK, 5)];
    pop(sc[0], 540, 780, 0); pop(sc[1], 540, 780, 0);
    var slot = box(c, "slot", 540, 780, 130, 330, 20, hex("#E4DED2"), INK, 7); pop(slot, 540, 780, 0.04);
    var on = txt(c, "ON", POP, 70, INK, 540, 560); popText(on, 0.06);
    var off = txt(c, "OFF", POP, 70, INK, 540, 1000); popText(off, 0.06);
    var lever = shape(c, "lever"), g = contents(lever);
    addRect(g, 540, 700, 110, 150, 18); addStroke(g, INK, 7);
    keys(addFill(g, YEL).property("ADBE Vector Fill Color"), [[0, YEL], [T(6.32), GREY]], true);
    keys(xf(lever, "ADBE Position"), [[T(6.24), [0, 0]], [T(6.32), [0, 170]]]);
    dim(c, T(6.70), T(6.95), 82);
    popText(txt(c, "no humans.", HAND, 120, YEL, 540, 330), T(6.85));
    popText(txt(c, "(in theory)", HAND, 70, WHITE, 540, 430), T(7.35));
    return place(s);
}

// 3. sticker: MEME stamp over Andrew
function sMeme() {
    var s = scene("03 meme stamp", 8.86, OLD_T[5], false), c = s.comp;
    box(c, "stamp", 280, 470, 420, 170, 16, null, RED, 13);
    txt(c, "MEME", POP, 140, RED, 280, 470);
    var L = place(s, { boil: 2 });
    center(L, 280, 470);
    xf(L, "ADBE Rotate Z").setValue(-12);
    keys(xf(L, "ADBE Scale"), [[s.t0, [260, 260]], [s.t0 + 0.1, [92, 92]], [s.t0 + 0.17, [100, 100]]]);
    L.property("ADBE Effect Parade").addProperty("ADBE Roughen Edges");
    return L;
}

// 4. "startups that do this... you can tell" — a vibe-coded landing page, then crossed out
function sSlop() {
    var s = scene("04 vibe-coded ui", OLD_T[5], OLD_T[7]), c = s.comp, T = s.T;
    pop(box(c, "window", 540, 780, 860, 900, 30, WHITE, INK, 9), 540, 780, 0, 60);
    pop(ink(c, "top bar", [[[110, 410], [970, 410]]], INK, 7, null), 540, 780, 0, 60);
    for (var d = 0; d < 3; d++) pop(ell(c, "dot " + d, 160 + d * 45, 370, 22, 22, null, INK, 5), 540, 780, 0, 60);
    pop(ell(c, "gradient blob a", 430, 650, 540, 380, PURP, null), 430, 650, 0.08);
    pop(ell(c, "gradient blob b", 660, 720, 470, 340, PINK, null), 660, 720, 0.12);
    var h1 = box(c, "headline", 500, 520, 600, 62, 31, INK, null); pop(h1, 500, 520, 0.15); xf(h1, "ADBE Rotate Z").setValue(-3);
    var h2 = box(c, "subhead", 440, 600, 420, 40, 20, GREY, null); pop(h2, 440, 600, 0.19); xf(h2, "ADBE Rotate Z").setValue(4);
    var btn = [[380, 860, -7], [570, 905, 5], [730, 845, -2]];
    for (var b = 0; b < btn.length; b++) {
        var B = box(c, "button " + b, btn[b][0], btn[b][1], 280, 92, 46, PURP, INK, 6);
        pop(B, btn[b][0], btn[b][1], 0.24 + b * 0.06); xf(B, "ADBE Rotate Z").setValue(btn[b][2]);
        var bt = txt(c, "Get Started", "Inter-Bold", 40, WHITE, btn[b][0], btn[b][1], { rot: btn[b][2] });
        popText(bt, 0.24 + b * 0.06);
    }
    var st = [[850, 520, 46], [230, 990, 38], [870, 1060, 30], [610, 470, 26]];
    for (var k = 0; k < st.length; k++) pop(blob(c, "sparkle " + k, star(st[k][0], st[k][1], st[k][2]), YEL, INK, 5), st[k][0], st[k][1], 0.4 + k * 0.05);
    for (var q = 0; q < 3; q++) pop(box(c, "card " + q, 300 + q * 240, 1100, 200, 150, 16, null, INK, 6), 300 + q * 240, 1100, 0.45 + q * 0.04);
    ink(c, "label marker", [[[520, 1222], [900, 1214]]], YEL, 46, T(11.2), T(11.4));
    popText(txt(c, "you can tell.", HAND, 96, INK, 710, 1205, { rot: -4 }), T(11.2));
    cross(c, "big x", 540, 780, 380, RED, 32, T(11.9));
    return place(s);
}

// 5. token-maxing: a counter that won't stop, money on fire, and a pink slip
function sTokens() {
    var s = scene("05 token maxing", OLD_T[7], OLD_T[9]), c = s.comp, T = s.T;
    var n, coins = [[130, 0.0, 0.62], [300, 0.37, 0.55], [470, 0.71, 0.7], [640, 0.15, 0.6], [820, 0.52, 0.66], [960, 0.83, 0.58], [220, 0.6, 0.75], [560, 0.92, 0.52], [900, 0.28, 0.72], [390, 0.45, 0.64]];
    for (n = 0; n < coins.length; n++) {
        var C = shape(c, "coin " + n), g = contents(C);
        addEll(g, 0, 0, 70, 70); addRect(g, 0, 0, 10, 30, 3); addStroke(g, INK, 6); addFill(g, YEL);
        xf(C, "ADBE Position").expression = "var p=(time*" + coins[n][2] + "+" + coins[n][1] + ")%1; [" + coins[n][0] + ", -80 + p*1600]";
        xf(C, "ADBE Rotate Z").expression = "time*" + (90 + n * 23);
    }
    ink(c, "title marker", [[[190, 370], [890, 362]]], YEL, 34, 0.1, 0.35);
    popText(txt(c, "the token-maxing era", HAND, 104, INK, 540, 330), 0.04, 60);
    pop(box(c, "counter box", 540, 620, 860, 230, 24, WHITE, INK, 8), 540, 620, 0.1);
    popText(txt(c, "TOKENS BURNED", MONO_M, 40, GREY, 540, 555, { tracking: 120 }), 0.12);
    var ctr = c.layers.addText("0");
    var sp = ctr.property("ADBE Text Properties").property("ADBE Text Document"), td = sp.value;
    td.resetCharStyle(); td.font = MONO; td.fontSize = 92; td.fillColor = INK; td.applyFill = true; td.applyStroke = false;
    td.justification = ParagraphJustification.CENTER_JUSTIFY; sp.setValue(td);
    sp.expression = "var v=Math.floor(Math.pow(10, linear(time,0.15,4.8,4,10.3))); var s=v.toString(), o=''; while(s.length>3){o=','+s.substr(s.length-3)+o; s=s.substr(0,s.length-3);} s+o";
    xf(ctr, "ADBE Position").setValue([540, 690]);
    for (var b = 0; b < 3; b++) pop(box(c, "bill " + b, 540, 1010 - b * 36, 420, 70, 10, hex("#9BD49B"), INK, 7), 540, 1010, 0.18 + b * 0.04);
    var f1 = blob(c, "flame", [[440, 950], [415, 870], [470, 800], [500, 845], [525, 760], [572, 830], [602, 790], [655, 875], [640, 950]], ORANGE, INK, 7);
    var f2 = blob(c, "flame core", [[485, 950], [478, 895], [515, 865], [540, 815], [576, 870], [598, 905], [592, 950]], YEL, null);
    var fl = [f1, f2];
    for (var k = 0; k < 2; k++) {
        center(fl[k], 540, 950); between(fl[k], 0.3, null);
        xf(fl[k], "ADBE Scale").expression = "var w=wiggle(12,9); [100+(w[0]-100)*0.5, w[1]]";
    }
    // pink slip, parented to a null so it rotates as one piece
    var slipNull = c.layers.addNull(); slipNull.name = "pink slip";
    xf(slipNull, "ADBE Position").setValue([540, 760]);
    var slip = [box(c, "slip", 540, 760, 780, 340, 10, hex("#FFD6E0"), INK, 8),
        txt(c, "PERFORMANCE REVIEW", MONO, 40, INK, 540, 650, { tracking: 80 }),
        txt(c, "tokens burned: not enough", HAND, 76, INK, 540, 750)];
    for (var i = 0; i < slip.length; i++) slip[i].parent = slipNull;
    xf(slipNull, "ADBE Rotate Z").setValue(4);
    keys(xf(slipNull, "ADBE Scale"), [[T(15.85), [0, 0]], [T(15.97), [108, 108]], [T(16.05), [100, 100]]]);
    var stamp = c.layers.addNull(); stamp.name = "fired stamp"; xf(stamp, "ADBE Position").setValue([560, 865]);
    var st = [box(c, "fired box", 560, 865, 380, 150, 14, null, RED, 12), txt(c, "FIRED", POP, 130, RED, 560, 868)];
    for (var j = 0; j < st.length; j++) st[j].parent = stamp;
    xf(stamp, "ADBE Rotate Z").setValue(-10);
    // hidden until the frame before it slams in (two keys 0.01s apart would collapse onto one frame)
    var hit = T(17.18), sc = xf(stamp, "ADBE Scale");
    keys(sc, [[hit - 1 / FPS, [0, 0]], [hit, [260, 260]], [hit + 0.1, [92, 92]], [hit + 0.17, [100, 100]]]);
    sc.setInterpolationTypeAtKey(1, KeyframeInterpolationType.HOLD);
    return place(s);
}

// 6. era of efficiency: gauge needle swings from maxing to efficient
function sGauge() {
    var s = scene("06 efficiency gauge", 19.95, OLD_T[12]), c = s.comp, T = s.T;
    popText(txt(c, "the era of efficiency", HAND, 104, INK, 540, 330), 0, 60);
    ink(c, "arc red", [arc(540, 980, 330, 180, 126, 24)], RED, 48, 0, 0.12);
    ink(c, "arc yellow", [arc(540, 980, 330, 118, 62, 24)], YEL, 48, 0.08, 0.2);
    ink(c, "arc green", [arc(540, 980, 330, 54, 0, 24)], GRN, 48, 0.16, 0.28);
    ink(c, "arc outline", [arc(540, 980, 368, 180, 0, 48)], INK, 7, 0, 0.3);
    popText(txt(c, "token maxing", HAND, 62, RED, 245, 1060), 0.2);
    popText(txt(c, "efficient", HAND, 70, GRN, 845, 1060), 0.24);
    var nd = ink(c, "needle", [[[540, 980], [540, 700]]], INK, 18, null);
    center(nd, 540, 980);
    keys(xf(nd, "ADBE Rotate Z"), [[0, -72], [0.18, -72], [0.6, 76], [0.74, 58], [0.86, 66]]);
    xf(nd, "ADBE Rotate Z").expression = "wiggle(5,2.5)";
    ell(c, "hub", 540, 980, 64, 64, INK, null);
    ink(c, "circle efficient", [wobble(845, 1058, 175, 2, 40, 0.42)], INK, 7, T(21.35), T(21.65), true);
    return place(s);
}

// 7. CI is the bottleneck: PRs pile up on a funnel
function sCI() {
    var s = scene("07 ci bottleneck", OLD_T[12], OLD_T[13]), c = s.comp;
    popText(txt(c, "the next bottleneck", HAND, 104, INK, 540, 330), 0, 60);
    ink(c, "funnel", [[[140, 560], [470, 905], [470, 1190]], [[940, 560], [610, 905], [610, 1190]]], INK, 13, 0, 0.3);
    popText(txt(c, "CI", POP, 120, INK, 540, 1070), 0.22);
    var pos = [[540, 860, 3], [420, 770, -6], [660, 770, 5], [300, 680, -4], [540, 680, 7], [780, 680, -8], [200, 590, 6], [420, 590, -3], [660, 590, 4], [880, 590, -7], [320, 500, 8], [560, 500, -5], [800, 500, 3]];
    for (var i = 0; i < pos.length; i++) {
        var p = pos[i], nl = c.layers.addNull(); nl.name = "pr " + i;
        xf(nl, "ADBE Position").setValue([p[0], p[1]]);
        var parts = [box(c, "pr card " + i, p[0], p[1], 210, 86, 14, WHITE, INK, 6), txt(c, "PR #" + (1041 + i * 7), MONO, 32, INK, p[0], p[1])];
        for (var k = 0; k < parts.length; k++) parts[k].parent = nl;
        xf(nl, "ADBE Rotate Z").setValue(p[2]);
        var t = 0.12 + i * 0.09;
        keys(xf(nl, "ADBE Position"), [[t, [p[0], p[1] - 1100]], [t + 0.18, [p[0], p[1] + 12]], [t + 0.24, [p[0], p[1]]]]);
    }
    popText(txt(c, "10\u00D7 the PRs", HAND, 84, RED, 830, 1180, { rot: -5 }), 1.25);
    return place(s);
}

// 8. title card: dynamic validation
function sDV() {
    var s = scene("08 dynamic validation", OLD_T[14], OLD_T[15]), c = s.comp;
    ink(c, "marker", [[[160, 900], [920, 888]]], YEL, 60, 0.12, 0.3);
    popText(txt(c, "dynamic", MARKER, 200, INK, 540, 640), 0, 60);
    popText(txt(c, "validation", MARKER, 200, INK, 540, 850), 0.07, 60);
    check(c, "tick", 880, 1040, 60, GRN, 0.32);
    return place(s);
}

// 9. CI pipeline: run everything -> only what the change touches
function sPipeline() {
    var s = scene("09 pipeline", 28.40, OLD_T[18]), c = s.comp, T = s.T;
    pop(box(c, "pr card", 540, 330, 920, 120, 20, WHITE, INK, 7), 540, 330, 0, 60);
    popText(txt(c, "PR #2187 \u00B7 changed api/billing.ts", MONO, 36, INK, 540, 332), 0, 60);
    pop(box(c, "pipeline card", 540, 810, 880, 760, 28, WHITE, INK, 8), 540, 810, 0.08, 60);
    var hdr = txt(c, "CI pipeline", HAND, 76, INK, 135, 500, { left: true }); between(hdr, 0.1, null);
    var slow = txt(c, "~45 min", HAND, 76, RED, 830, 478); popText(slow, 0.15); between(slow, null, T(31.5));
    var fast = txt(c, "~9 min", HAND, 76, GRN, 830, 478); popText(fast, T(31.5));
    var rows = [["lint", 1], ["api tests", 1], ["frontend unit tests", 0], ["e2e: checkout", 1], ["visual regression", 0]];
    var y0 = 610, dy = 108;
    var scan = box(c, "scanner", 540, 0, 840, 92, 14, YEL, null);
    keys(xf(scan, "ADBE Position"), [[T(30.3), [0, y0]], [T(31.15), [0, y0 + dy * 4]]]);
    keys(xf(scan, "ADBE Opacity"), [[T(30.25), 0], [T(30.32), 70], [T(31.15), 70], [T(31.25), 0]]);
    for (var i = 0; i < rows.length; i++) {
        var y = y0 + i * dy, t = 0.2 + i * 0.06, tm = T(30.45) + i * 0.18;
        pop(box(c, "checkbox " + i, 170, y, 58, 58, 8, null, INK, 6), 170, y, t);
        var lab = txt(c, rows[i][0], MONO_M, 40, INK, 228, y + 14, { left: true }); between(lab, t, null);
        if (rows[i][1]) check(c, "pass " + i, 170, y, 30, GRN, tm);
        else {
            cross(c, "skip " + i, 170, y, 20, RED, 9, tm);
            ink(c, "strike " + i, [[[222, y], [228 + rows[i][0].length * 24, y]]], GREY, 6, tm, tm + 0.15);
            keys(xf(lab, "ADBE Opacity"), [[tm, 100], [tm + 0.15, 40]]);
        }
    }
    ink(c, "circle frontend", [wobble(500, y0 + 2 * dy, 375, 1, 48, 0.19)], RED, 7, T(32.6), T(32.95), true);
    popText(txt(c, "no frontend changes = skip it", HAND, 60, RED, 540, 1135), T(32.75));
    return place(s);
}

// 10. how hard is the task? a sealed box and a meter that can't decide
function sComplexity() {
    var s = scene("10 complexity", 36.20, OLD_T[20]), c = s.comp, T = s.T;
    popText(txt(c, "how hard is it?", HAND, 108, INK, 540, 330), 0, 60);
    var parts = [blob(c, "box side", [[720, 580], [840, 490], [840, 870], [720, 960]], hex("#C99C66"), INK, 9),
        blob(c, "box top", [[280, 580], [400, 490], [840, 490], [720, 580]], hex("#EFD3AE"), INK, 9),
        box(c, "box front", 500, 770, 440, 380, 0, hex("#E3BE8F"), INK, 9),
        txt(c, "?", POP, 300, INK, 500, 790)];
    for (var i = 0; i < parts.length; i++) {
        if (i < 3) pop(parts[i], 560, 725, 0.04); else popText(parts[i], 0.12);
        xf(parts[i], "ADBE Rotate Z").expression = "time>" + T(37.6).toFixed(2) + " ? wiggle(16,5) : value";
    }
    ink(c, "meter", [[[200, 1070], [880, 1070]]], INK, 8, 0.1, 0.3);
    popText(txt(c, "easy", HAND, 64, GRN, 200, 1130), 0.2);
    popText(txt(c, "hard", HAND, 64, RED, 880, 1130), 0.24);
    var mk = blob(c, "marker", [[0, -12], [-26, -56], [26, -56]], RED, INK, 5);
    between(mk, 0.3, null);
    xf(mk, "ADBE Position").expression = "[540 + 300*Math.sin(time*6.1)*Math.cos(time*2.3), 1070]";
    return place(s);
}

// 11. same prompt, two worlds
function sRust() {
    var s = scene("11 rust two worlds", OLD_T[21], OLD_T[26]), c = s.comp, T = s.T;
    pop(box(c, "prompt", 540, 340, 940, 130, 22, INK, INK, 6), 540, 340, 0, 60);
    var ty = c.layers.addText(">");
    var sp = ty.property("ADBE Text Properties").property("ADBE Text Document"), td = sp.value;
    td.resetCharStyle(); td.font = MONO; td.fontSize = 46; td.fillColor = YEL; td.applyFill = true; td.applyStroke = false;
    td.justification = ParagraphJustification.LEFT_JUSTIFY; sp.setValue(td);
    sp.expression = "var t='> refactor this to Rust'; var n=Math.floor(linear(time,0.05,0.85,0,t.length)); t.substr(0,n)+((Math.floor(time*3)%2==0)?'_':' ')";
    xf(ty, "ADBE Position").setValue([105, 356]);
    arrow(c, "arrow left", 430, 415, 300, 560, INK, 9, T(42.5), T(42.75));
    popText(txt(c, "weekend project", HAND, 70, INK, 290, 625), T(44.3));
    pop(blob(c, "folder", [[170, 700], [245, 700], [268, 728], [410, 728], [410, 870], [170, 870]], YEL, INK, 7), 290, 790, T(44.45));
    popText(txt(c, "3 files", HAND, 56, INK, 290, 810), T(44.5));
    arrow(c, "arrow down left", 290, 895, 290, 975, INK, 8, T(45.8), T(46.0));
    pop(box(c, "chip deepseek a", 290, 1045, 310, 100, 50, hex("#CDEFD6"), INK, 7), 290, 1045, T(46.15));
    popText(txt(c, "deepseek", MONO, 40, INK, 290, 1047), T(46.15));
    check(c, "ok", 470, 1040, 32, GRN, T(46.8));
    arrow(c, "arrow right", 650, 415, 780, 560, INK, 9, T(47.9), T(48.15));
    popText(txt(c, "Linux kernel", HAND, 70, INK, 790, 625), T(48.15));
    for (var r = 0; r < 6; r++) for (var b = 0; b < 3; b++) {
        var x = 700 + b * 90 + ((r % 2) ? 20 : 0), y = 935 - r * 44;
        pop(box(c, "brick " + r + "-" + b, x, y, 86, 40, 4, hex("#D9D4CC"), INK, 5), x, y, T(48.25) + r * 0.05 + b * 0.015);
    }
    pop(box(c, "chip deepseek b", 790, 1045, 310, 100, 50, hex("#CDEFD6"), INK, 7), 790, 1045, T(49.0));
    popText(txt(c, "deepseek", MONO, 40, INK, 790, 1047), T(49.0));
    cross(c, "nope", 790, 1045, 120, RED, 22, T(49.45));
    return place(s);
}

// 12. the agent reveals the contours of the problem as it works
function sContours() {
    var s = scene("12 contours", OLD_T[27], OLD_T[28]), c = s.comp, T = s.T;
    var lab = [["complexity: ???", INK, 0, T(52.6)], ["complexity: medium", ORANGE, T(52.6), T(53.5)], ["complexity: HIGH", RED, T(53.5), null]];
    for (var i = 0; i < lab.length; i++) { var L = txt(c, lab[i][0], HAND, 100, lab[i][1], 540, 320); popText(L, lab[i][2] || 0, i ? 0 : 60); between(L, null, lab[i][3]); }
    pop(box(c, "map", 540, 790, 900, 820, 30, NAVY, INK, 9), 540, 790, 0, 60);
    var cols = [BLU, BLU, hex("#8FD3FF"), hex("#9EE6A0"), YEL, ORANGE, RED];
    var R = [335, 282, 228, 175, 125, 80, 40];
    for (var k = 0; k < R.length; k++) {
        var t0 = 0.25 + k * 0.33;
        ink(c, "contour " + k, [wobble(540 - k * 4, 770 + k * 4, R[k], k * 1.3, 64)], cols[k], 7, t0, t0 + 0.45, true);
    }
    var path = [[0, [200, 1130]], [0.55, [320, 990]], [1.05, [450, 1030]], [1.55, [470, 870]], [2.2, [530, 805]], [2.9, [516, 790]]];
    var trail = [];
    for (var p = 0; p < path.length; p++) trail.push(path[p][1]);
    ink(c, "trail", [trail], WHITE, 5, 0, 2.9);
    var dot = ell(c, "agent", 0, 0, 40, 40, YEL, WHITE, 5);
    keys(xf(dot, "ADBE Position"), path);
    var cmds = [["grep -r", 300, 1165, 0.05], ["ls src/", 330, 930, 0.5], ["cat sched.c", 640, 1080, 1.0], ["make", 340, 830, 1.5], ["run tests", 720, 700, 2.15]];
    for (var q = 0; q < cmds.length; q++) popText(txt(c, cmds[q][0], MONO, 34, WHITE, cmds[q][1], cmds[q][2]), cmds[q][3]);
    return place(s);
}

// 13. sticker: Astra-level tag over Andrew
function sAstra() {
    var s = scene("13 astra tag", 54.98, OLD_T[29], false), c = s.comp;
    box(c, "tag", 270, 440, 380, 124, 62, YEL, INK, 7);
    txt(c, "Astra-level", HAND, 76, INK, 270, 444);
    var L = place(s, { boil: 2 });
    center(L, 270, 440); xf(L, "ADBE Rotate Z").setValue(-8);
    keys(xf(L, "ADBE Scale"), [[s.t0, [0, 0]], [s.t0 + 0.12, [112, 112]], [s.t0 + 0.2, [100, 100]]]);
    return L;
}

// 14. half the cost, twice the speed
function sBars() {
    var s = scene("14 cost and speed", OLD_T[29], OLD_T[30]), c = s.comp, T = s.T;
    popText(txt(c, "vs. Astra alone", HAND, 104, INK, 540, 330), 0, 60);
    ink(c, "baseline", [[[150, 1100], [930, 1100]]], INK, 8, 0, 0.2);
    var g1 = box(c, "cost was", 330, 800, 220, 600, 6, null, GREY, 6); pop(g1, 330, 1100, 0.05);
    var cost = box(c, "cost", 330, 800, 220, 600, 6, RED, INK, 7); center(cost, 330, 1100);
    keys(xf(cost, "ADBE Scale"), [[0, [100, 70]], [0.18, [100, 100]], [T(56.6), [100, 100]], [T(56.85), [100, 46]], [T(56.95), [100, 50]]]);
    popText(txt(c, "\u00BD", POP, 170, RED, 330, 700), T(56.85));
    var g2 = box(c, "speed was", 750, 950, 220, 300, 6, null, GREY, 6); pop(g2, 750, 1100, 0.05);
    var spd = box(c, "speed", 750, 950, 220, 300, 6, GRN, INK, 7); center(spd, 750, 1100);
    keys(xf(spd, "ADBE Scale"), [[0, [100, 70]], [0.18, [100, 100]], [T(57.55), [100, 100]], [T(57.85), [100, 208]], [T(57.95), [100, 200]]]);
    popText(txt(c, "2\u00D7", POP, 150, GRN, 945, 560), T(57.85));
    popText(txt(c, "cost", HAND, 66, INK, 330, 1165), 0.1);
    popText(txt(c, "speed", HAND, 66, INK, 750, 1165), 0.14);
    return place(s);
}


var SCENES = [sFactory, sSwitch, sMeme, sSlop, sTokens, sGauge, sCI, sDV, sPipeline, sComplexity, sRust, sContours, sAstra, sBars];
