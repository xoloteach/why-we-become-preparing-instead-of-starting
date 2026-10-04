"""Offline, deterministic extraction of supplied contact sheets; no network or credentials.
Usage: python3 extract_panels.py [project_root]
Never treats blank grid cells as illustrations. Never claims neural reconstruction.
"""
from pathlib import Path
import hashlib, json, os, sys
import numpy as np
from PIL import Image

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sheets = root / 'stickman_contact_sheets'
out = root / 'panels_native'
out.mkdir(parents=True, exist_ok=True)

def boundaries(profile):
    positions = np.flatnonzero(profile > 0.82)
    groups = []
    for p in positions:
        p = int(p)
        if not groups or p > groups[-1][-1] + 1:
            groups.append([p])
        else:
            groups[-1].append(p)
    return [int(round(sum(g) / len(g))) for g in groups]

records, sheet_records = [], []
for path in sorted(sheets.glob('Sheet_*.png')):
    sheet_id = int(path.name.split('_')[1])
    im = Image.open(path).convert('RGB')
    a = np.asarray(im)
    ink = a.mean(axis=2) < 95
    xs = boundaries(ink.mean(axis=0))
    ys = boundaries(ink.mean(axis=1))
    if len(xs) != 4 or len(ys) != (5 if sheet_id == 4 else 4):
        raise ValueError(f'Boundary detection needs review: {path.name}, x={xs}, y={ys}')
    sheet_records.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size': list(im.size), 'x_boundaries': xs, 'y_boundaries': ys})
    for ri in range(len(ys) - 1):
        for ci in range(len(xs) - 1):
            box = [xs[ci] + 4, ys[ri] + 4, xs[ci+1] - 4, ys[ri+1] - 4]
            crop = im.crop(box)
            ca = np.asarray(crop)
            ink_fraction = float((ca.mean(axis=2) < 180).mean())
            blank = ink_fraction < 0.0005
            identifier = f'S{sheet_id:02d}-R{ri+1}-C{ci+1}'
            record = {'id': identifier, 'sheet': path.name, 'row': ri+1, 'column': ci+1, 'crop_box': box, 'native_size': list(crop.size), 'ink_fraction': round(ink_fraction,6), 'status': 'omitted_blank' if blank else 'available_not_timed', 'reason': 'No supplied illustration in cell' if blank else 'Awaiting final narration-timed scene assignment', 'file': None if blank else f'panels_native/{identifier}.png'}
            if not blank:
                tmp = out / (identifier + '.tmp.png')
                crop.save(tmp)
                os.replace(tmp, root / record['file'])
            records.append(record)

inventory = {'title': 'Why You Keep Preparing Instead of Starting.', 'timing_status': 'UNLOCKED: narration not synthesized or aligned', 'sheets': sheet_records, 'panels': records, 'counts': {'sheets':len(sheet_records), 'grid_cells':len(records), 'illustrated_panels':sum(r['status']!='omitted_blank' for r in records), 'blank_cells':sum(r['status']=='omitted_blank' for r in records)}, 'qa_scope': 'All original sheets inspected; extracted native crops not individually visually approved; final motion/typography/caption QA pending.'}
(root/'panel_inventory.json').write_text(json.dumps(inventory, indent=2))
(root/'upscale_report.json').write_text(json.dumps({'status':'pending','method':None,'neural_reconstruction_performed':False,'panels':[{'id':r['id'],'native_size':r['native_size'],'upscaled_size':None} for r in records if r['file']]}, indent=2))
print(json.dumps(inventory['counts']))
for r in records:
    if r['status']=='omitted_blank': print('Blank:',r['id'])
print('Native crops only. Neural reconstruction and final crop/edge QA remain pending.')
