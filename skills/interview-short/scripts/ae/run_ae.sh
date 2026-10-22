#!/bin/bash
# Build the project in After Effects (runs build.jsx in the open app) and render it with aerender.
# usage: run_ae.sh PROJECT [--no-render]
# After Effects grows its disk cache by ~6 GB a render; "Error Code: 9988" / "Disk Full" means the disk is full:
# ask the user to empty the cache (Settings > Media & Disk Cache > Empty Disk Cache). Never delete it yourself.
set -uo pipefail
P="$(cd "$1" && pwd)"; APP="${AE_APP:-Adobe After Effects 2026}"
AER="${AERENDER:-/Applications/$APP/aerender}"
free=$(df -g /System/Volumes/Data | awk 'NR==2{print $4}'); [ "$free" -lt 8 ] && echo "WARNING: only ${free} GB free; After Effects renders can fail with error 9988"
osascript -e "with timeout of 1200 seconds" -e "tell application \"$APP\" to DoScript \"\$.evalFile(new File('$P/build.jsx'))\"" -e "end timeout" >/dev/null 2>&1
tr '\r' '\n' < "$P/build.log" | grep -vE "^(templates|placed)"
[ "${2:-}" = "--no-render" ] && exit 0
"$AER" -project "$P/$(sed -n 's/^var NAME = "\(.*\)";/\1/p' "$P/data.jsxinc").aep" > "$P/render/aerender.log" 2>&1
tr '\r' '\n' < "$P/render/aerender.log" | grep -E "Total Time Elapsed|rror|Disk Full" | tail -4
ls -la "$P/render"/*-graphics.* 2>/dev/null
