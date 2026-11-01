#!/usr/bin/env python3
"""Validate Taco Smell Stage 1 room-to-room v0.2 contract; stdlib only."""
import json
from pathlib import Path
from collections import deque

ROOT=Path(__file__).resolve().parent.parent
DIR=ROOT/"assets"/"maps"
cfg=json.loads((DIR/"taco_smell_stage1_v02.json").read_text(encoding="utf-8"))
assert cfg["schema_version"] == 2
disp=cfg["display"]
assert (disp["tile_columns"],disp["tile_rows"],disp["status_rows"])==(40,22,2)
assert disp["scrolling"] is False and disp["room_replaces_screen"] is True
assert len(cfg["rooms"])==3 and cfg["room_order"]==["dining","kitchen","storage"]
symbols=cfg["terrain"]
solid={char for char,val in symbols.items() if val["solid"]}
rooms={}
for name,meta in cfg["rooms"].items():
    lines=(DIR/meta["map_file"]).read_text(encoding="ascii").splitlines()
    assert len(lines)==22 and all(len(row)==40 for row in lines),(name,"map dimensions")
    assert set("".join(lines))<=set(symbols),(name,"tile alphabet")
    rooms[name]=lines
def char(room,x,y):
    assert 0<=x<40 and 0<=y<22
    return rooms[room][y][x]
def passable(room,x,y):
    return 0<=x<40 and 0<=y<22 and rooms[room][y][x] not in solid
def reach(room,start):
    q=deque([tuple(start)]);seen={tuple(start):0}
    while q:
        x,y=q.popleft()
        for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if passable(room,nx,ny) and (nx,ny) not in seen:
                seen[(nx,ny)]=seen[(x,y)]+1
                q.append((nx,ny))
    return seen
# Check outer borders, exact door locations, single escape and room connectivity.
expected={
    "dining":{"D":{(39,10),(39,11)},"F":{(0,10)}},
    "kitchen":{"D":{(0,10),(0,11),(39,10),(39,11)},"N":{(22,0)}},
    "storage":{"D":{(0,10),(0,11)},"X":{(39,10)}},
}
for room,lines in rooms.items():
    for sym in "DFNX":
        actual={(x,y) for y in range(22) for x in range(40) if char(room,x,y)==sym}
        assert actual==expected[room].get(sym,set()),(room,sym,actual)
    allowed=expected[room].get("D",set()) | expected[room].get("F",set()) | expected[room].get("N",set()) | expected[room].get("X",set())
    for y in range(22):
        for x in range(40):
            if x in (0,39) or y in (0,21):
                assert (x,y) in allowed or char(room,x,y)=="#",(room,x,y)
    first=cfg["rooms"][room].get("player_spawn") or cfg["rooms"][room].get("entry_from_dining") or cfg["rooms"][room].get("entry_from_kitchen")
    assert first and passable(room,*first)
    area={(x,y) for y in range(22) for x in range(40) if passable(room,x,y)}
    dist=reach(room,first)
    assert set(dist)==area,(room,"unreachable tiles",len(area)-len(dist))
    for spawn in cfg["rooms"][room].get("hazmat_spawns",[]):
        assert passable(room,*spawn["xy"]),(room,spawn["id"])
    print(f"PASS {room}: 40x22, {len(area)} connected walkable tiles")
# Every doorway has exactly one matching reciprocal link.
links=cfg["transitions"]
assert len(links)==4
for link in links:
    source,target=link["from"],link["to"]
    assert source!=target
    for x,y in link["trigger_tiles"]:
        assert char(source,x,y)=="D"
        dx=link["entry_x"]
        assert dx in (1,38)
        assert passable(target,dx,y),(source,target,"bad destination",dx,y)
    reverse=[other for other in links if other["from"]==target and other["to"]==source]
    assert len(reverse)==1,(source,target,"missing reciprocal link")
for room_id,room_cfg in cfg["rooms"].items():
    for item in room_cfg.get("hazmat_spawns",[]):
        if item.get("enabled"):
            assert room_id=="dining" and item["id"]=="hazmat_front"
assert cfg["gameplay_v02"]["hazmat_room_follow"] and cfg["gameplay_v02"]["backtrack"]
ex=cfg["objective"]
assert ex["room"]=="storage" and char("storage",*ex["tile"])=="X"
assert passable("dining",*cfg["rooms"]["dining"]["player_spawn"])
print("PASS: 3 screens; 4 reciprocal doorway transitions; one exit; 1 active hazmat; no scrolling")
