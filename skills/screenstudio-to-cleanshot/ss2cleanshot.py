#!/usr/bin/env python3
"""Convert a Screen Studio project (.screenstudio) to a CleanShot X 5 project (.cleanshotvideo).

usage: ss2cleanshot.py SRC.screenstudio [OUT.cleanshotvideo] [--template DIR]

--template: a CleanShot project (or dir with document.json + meta.json) whose style
settings (cursor, motion blur, background...) are reused. Defaults to ./template.

Format notes (CleanShot X 5.0.2, documentFormatVersion 1):
- mouse_events.bin: b"FLME", u32 version=1, u64 count, then columns:
  t[count] f64 seconds, x[count] f64 px, y[count] f64 px (BOTTOM-up origin),
  type[count] u8 (0 move, 1 down, 2 up, 3 drag), cursor[count] u8 (enum, 255 = other)
- document.json clips/zooms use source-video seconds; zoom mode 0 = follow cursor.
"""
import json, os, shutil, struct, subprocess, sys, uuid

import argparse
ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out', nargs='?')
ap.add_argument('--template', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template'))
a = ap.parse_args()
src, tpl = a.src.rstrip('/'), a.template.rstrip('/')
out = a.out or src.rsplit('.', 1)[0].replace(':', '.') + '.cleanshotvideo'
rec = os.path.join(src, 'recording')

meta = json.load(open(os.path.join(rec, 'metadata.json')))
disp = next(r for r in meta['recorders'] if r['type'] == 'display')
dsess = disp['sessions'][0]
b, scale = dsess['bounds'], 1 / dsess['recordingScale']  # points -> video px
H = b['height'] * scale  # CleanShot y-axis is bottom-up
t0 = dsess['processTimeStartMs']
proj = json.load(open(os.path.join(src, 'project.json')))['json']

# --- mouse events -> mouse_events.bin ---------------------------------------
CURSORS = ['arrow', 'pointingHand', 'iBeam', 'crosshair', 'openHand', 'closedHand',
           'resizeLeftRight', 'resizeUpDown', 'resizeLeft', 'resizeRight', 'resizeUp',
           'resizeDown', 'operationNotAllowed', 'dragCopy']
TYPES = {'mouseMoved': 0, 'mouseDown': 1, 'mouseUp': 2, 'mouseDragged': 3}
ev = json.load(open(os.path.join(rec, 'mousemoves-0.json'))) + \
     json.load(open(os.path.join(rec, 'mouseclicks-0.json')))
ev = [e for e in ev if e['type'] in TYPES and e.get('button', 'left') == 'left']
ev.sort(key=lambda e: (e['processTimeMs'], e['type'] == 'mouseUp'))
ev = [e for e in ev if e['processTimeMs'] >= t0]
n = len(ev)
cols = [
    struct.pack(f'<{n}d', *[(e['processTimeMs'] - t0) / 1000 for e in ev]),
    struct.pack(f'<{n}d', *[(e['x'] - b['x']) * scale for e in ev]),
    struct.pack(f'<{n}d', *[H - (e['y'] - b['y']) * scale for e in ev]),
    bytes(TYPES[e['type']] for e in ev),
    bytes(CURSORS.index(e['cursorId']) if e['cursorId'] in CURSORS else 255 for e in ev),
]
mouse_bin = b'FLME' + struct.pack('<IQ', 1, n) + b''.join(cols)

# --- document.json ----------------------------------------------------------
doc = json.load(open(os.path.join(tpl, 'document.json')))
scene = proj['scenes'][0]
doc['clips'] = [{'startTime': s['sourceStartMs'] / 1000,
                 'duration': (s['sourceEndMs'] - s['sourceStartMs']) / 1000,
                 'id': str(uuid.uuid4()).upper()} for s in scene['slices']]
doc['zooms'] = [{'position': [z['manualTargetPoint']['x'], z['manualTargetPoint']['y']],
                 'zoomValue': z['zoom'],
                 'mode': 1 if z['type'] == 'manual' else 0,  # 0 = follow cursor
                 'startTimestamp': z['sourceStartMs'] / 1000,
                 'endTimestamp': z['sourceEndMs'] / 1000,
                 'id': str(uuid.uuid4()).upper()}
                for s in proj['scenes'] for z in s.get('zooms', []) if not z.get('isDisabled')]
doc['recordingInfo'] = {'retinaFactor': scale, 'scaleFactor': 1}
doc['we'], doc['te'], doc['mouseEvents'], doc['keyboardEvents'] = [], [], [], []
doc['audioConfiguration'] = {'systemAudioTrack': {'audioType': 'system', 'isEnabled': False, 'volume': 1}}
doc['showKeystrokes'] = False

# --- write package ----------------------------------------------------------
if os.path.exists(out):
    shutil.rmtree(out)
os.makedirs(os.path.join(out, 'files'))
os.makedirs(os.path.join(out, 'previews'))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-allowed_extensions', 'ALL',
                '-i', os.path.join(rec, dsess['outputFilename']), '-c', 'copy',
                '-movflags', '+faststart', os.path.join(out, 'files', 'video.mov')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', os.path.join(out, 'files', 'video.mov'),
                '-frames:v', '1', '-update', '1', '-q:v', '3',
                os.path.join(out, 'previews', 'preview.jpg')], check=True)
wp = os.path.join(tpl, 'files', 'wallpaper.tiff')
if os.path.exists(wp):
    shutil.copy(wp, os.path.join(out, 'files'))
else:  # plain black background; only visible if padding is turned on
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=black:s=1920x1080',
                    '-frames:v', '1', '-update', '1', os.path.join(out, 'files', 'wallpaper.tiff')], check=True)
shutil.copy(os.path.join(tpl, 'meta.json'), out)
open(os.path.join(out, 'mouse_events.bin'), 'wb').write(mouse_bin)
json.dump(doc, open(os.path.join(out, 'document.json'), 'w'))
print(f'{out}: {n} mouse events, {len(doc["clips"])} clips, {len(doc["zooms"])} zooms')
