// Builds the short in After Effects from this folder: plate, data.jsxinc, sfx.jsxinc, lib.jsx, scenes.jsx.
// Run with run_ae.sh (osascript DoScript + aerender) or File > Scripts > Run Script File. Re-running builds a fresh project.
var ROOT = File($.fileName).parent.fsName;
#include "data.jsxinc"
#include "sfx.jsxinc"
#include "lib.jsx"
#include "scenes.jsx"
run();
