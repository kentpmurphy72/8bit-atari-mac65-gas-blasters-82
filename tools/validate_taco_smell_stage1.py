#!/usr/bin/env python3
"""Validate the Stage 1 map contract and traversability. Python standard library only.
Run from any directory: python3 tools/validate_taco_smell_stage1.py
"""
import json
from pathlib import Path
from collections import deque
import sys

# In the repo this lives in tools/; in the portable package, beside the assets.
HERE = Path(__file__).resolve().parent
MAPDIR = next((p for p in (HERE.parent / 'assets' / 'maps', HERE / 'assets' / 'maps', HERE) if (p / 'taco_smell_stage1_v01.json').exists()), None)
assert MAPDIR is not None, 'Cannot locate taco_smell_stage1_v01.json'
META = MAPDIR / 'taco_smell_stage1_v01.json'
meta = json.loads(META.read_text(encoding='utf-8'))
rows = (MAPDIR / meta['terrain_file']).read_text(encoding='ascii').splitlines()
w, h = meta['width_tiles'], meta['height_tiles']
assert (w, h) == (48, 22), (w, h)
assert len(rows) == h and all(len(row) == w for row in rows), 'Incorrect tile-map dimensions'
assert set(''.join(rows)) <= set(meta['terrain']), 'Unexpected tile symbol'
assert len(meta['zones']) == 3, 'Expected 3 gameplay zones'
solid = {glyph for glyph, props in meta['terrain'].items() if props['solid']}
walkable = lambda x,y: 0 <= x < w and 0 <= y < h and rows[y][x] not in solid
assert rows[10][0] == 'F' and rows[0][27] == 'N' and rows[10][47] == 'X'
assert all(rows[y][x]=='#' for y in (0,h-1) for x in range(w) if (x,y) not in [(27,0)]), 'Open outer wall'
assert all(rows[y][x]=='#' for x in (0,w-1) for y in range(h) if (x,y) not in [(0,10),(47,10)]), 'Open outer wall'
# Expected breaks are the ONLY walkable crossing points between zones.
for x, permitted in [(17,{12,13}), (33,{9,10})]:
    assert {y for y in range(1,21) if walkable(x,y)} == permitted, f'Incorrect x={x} divider'
    assert all(rows[y][x]=='D' for y in permitted)
assert sorted((z['x_min'],z['x_max']) for z in meta['zones']) == [(0,17),(18,33),(34,47)]
start = tuple(next(e['spawn'] for e in meta['actors'] if e['id']=='billy'))
exit_tile = tuple(meta['exit']['tile'])
for e in meta['actors']:
    assert walkable(*e['spawn']), f"Invalid actor spawn: {e['id']}"
    assert tuple(e['spawn']) != exit_tile
assert walkable(*exit_tile) and rows[exit_tile[1]][exit_tile[0]] == 'X'
assert sum(row.count('X') for row in rows) == 1, 'Expected exactly one exit'

# Breadth-first search, no diagonal movement or corner-cutting.
queue = deque([start]); prior = {start: None}
while queue:
    x,y=queue.popleft()
    for nxt in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
        if nxt not in prior and walkable(*nxt):
            prior[nxt]=(x,y)
            queue.append(nxt)
assert exit_tile in prior, 'Billy cannot reach the exit'
assert all(tuple(e['spawn']) in prior for e in meta['actors']), 'Hazmat spawn disconnected'
assert any(x >= 18 for x,y in prior) and any(x >= 34 for x,y in prior)
# No isolated walkable islands: all floor tiles must be reachable.
all_walkable={(x,y) for y in range(h) for x in range(w) if walkable(x,y)}
assert len(prior)==len(all_walkable), f'{len(all_walkable)-len(prior)} unreachable floor tiles'
path=[]; pos=exit_tile
while pos is not None:
    path.append(pos);pos=prior[pos]
path.reverse()
assert any(x==17 and y in (12,13) for x,y in path)
assert any(x==33 and y in (9,10) for x,y in path)
assert all(rows[y][x] not in solid for x,y in path)
print(f'PASS {meta["map_id"]} {w}x{h}, {len(all_walkable)} walkable tiles, {len(path)-1} minimum steps Billy→exit, 3 zones, 2 chokepoints')
