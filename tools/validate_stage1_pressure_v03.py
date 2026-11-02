#!/usr/bin/env python3
"""Validate Stage 1 v0.3 encounter design against the unchanged v0.2 floor maps."""
from pathlib import Path
import json
from collections import deque

ROOT=Path(__file__).resolve().parent.parent
M=ROOT/"assets"/"maps"
P=ROOT/"assets"/"gameplay"
level=json.loads((P/"taco_smell_stage1_v03_rules.json").read_text(encoding="utf-8"))
base=json.loads((M/"taco_smell_stage1_v02.json").read_text(encoding="utf-8"))
assert level["schema_version"]==3 and level["base_room_maps"].endswith("taco_smell_stage1_v02.json")
assert level["ntsc_fps_nominal"]==60
assert level["room_order"]==base["room_order"]==["dining","kitchen","storage"]
assert level["other"]["layout"].startswith("no room geometry")
solid={s for s,v in base["terrain"].items() if v["solid"]}
rooms={}
for room,data in base["rooms"].items():
    lines=(M/data["map_file"]).read_text(encoding="ascii").splitlines()
    assert len(lines)==22 and all(len(s)==40 for s in lines)
    rooms[room]=lines
def ok(room,xy):
    x,y=xy
    return 0<=x<40 and 0<=y<22 and rooms[room][y][x] not in solid

units=level["hazmat"]["units"]
assert level["hazmat"]["active_at_once_max"]==3 and len(units)==3
assert [u["room"] for u in units]==["dining","kitchen","storage"]
assert len(set(u["id"] for u in units))==3
for u in units:
    assert ok(u["room"],u["spawn"]),(u["id"],"spawn solid/out of bounds")
    assert tuple(u["spawn"]) != tuple(base["objective"]["tile"]) or u["room"]!="storage"
    assert u["move_every_frames"]>=8
    k="activate_after_frames" if u["room"]=="dining" else "activate_after_first_room_entry_frames"
    assert u[k]>0
assert level["hazmat"]["door_follow_delay_frames"]>0
assert len(base["transitions"])==4
# Validate all new spawns reachable from a logical room entry, without touching an obstacle.
for room,data in base["rooms"].items():
    start=data.get("player_spawn") or data.get("entry_from_dining") or data.get("entry_from_kitchen")
    assert ok(room,start)
    q=deque([tuple(start)]);visited=set(q)
    while q:
        x,y=q.popleft()
        for x1,y1 in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            pos=(x1,y1)
            if pos not in visited and ok(room,pos):
                visited.add(pos);q.append(pos)
    for u in units:
        if u["room"]==room:
            assert tuple(u["spawn"]) in visited,(room,u["id"],"spawn unreachable")
    print(f"PASS: {room}: {len(visited)} connected passable tiles and all v0.3 spawns reachable")
blast=level["blast"]
assert 1<=blast["range_tiles"]<=5
assert 1<=blast["max_knockback_tiles"]<=3
assert blast["stun_frames"]>blast["visual_frames"]>0
assert blast["cooldown_frames"]>=blast["visual_frames"]
assert blast["wall_occlusion"] is True
assert level["other"]["no_time_gate"] is True
assert level["controls"]["fire"].startswith("FIRE + cardinal")
assert level["other"]["caught"].startswith("same Stage 1 restart")
print("PASS: unique actors, 3 valid spawns, timing ranges, gas-blast rules, preserved v0.2 maps")
