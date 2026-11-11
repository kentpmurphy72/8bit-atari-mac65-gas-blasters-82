#!/usr/bin/env python3
"""Repeatable py65 costs. No ANTIC DMA or OS interrupt cost is included."""
import json,tempfile
from pathlib import Path
import build_stage2_v03 as b
from build_opening_sequence import xex_segments
from test_stage2_v02_r1 import Harness

def profile():
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp);m=b.build(out);parts=xex_segments(out/m['output']);samples={}
        for name,time,joy in [('neutral',0,255),('accelerate_steer',0,246),('brake_steer',0,249),('warning75',38000,246),('critical90',45000,249)]:
            h=Harness(parts,m);h.settime(time)
            for _ in range(120):h.frame(joy)
            samples[name]={'min':min(h.costs),'max':max(h.costs)}
        # Adversarial simultaneous digit/flash/PMG updates across every legal speed.
        h=Harness(parts,m);peak=0;case=None
        for speed in range(8,57):
            for time in (0,37120,44545,49490):
                for joy in (255,254,253,251,247,250,246,249,245):
                    h.put('STATE',0);h.put('SPEED',speed);h.settime(time);h.setdist(43201)
                    h.put('CAR_LO',32);h.put('CAR_HI',3);h.put('CAR_Y_LO',0);h.put('CAR_Y_HI',9)
                    h.put('WARN',0 if time<37125 else 1 if time<44550 else 2)
                    h.put('FLASH_TIME',145 if time<44550 else 25)
                    for key in ('LAST_GAS','LAST_MI','LAST_MPH','LAST_LIVES','LAST_FLASH'):h.put(key,255)
                    cost=h.frame(joy)
                    if cost>peak:peak=cost;case={'speed':speed,'time':time,'joystick':joy}
        samples['worst_case_drive_sweep']={'max':peak,'case':case,'cases':49*4*9}
        h=Harness(parts,m,pal=True);h.settime(45000);h.put('SPEED',8);h.put('WARN',2);samples['missed_255_tick_critical']={'max':h.frame(249,delta=255)}
        h=Harness(parts,m);h.settime(49495);samples['explosion_enter']={'max':h.frame()}
        for _ in range(30):h.frame()
        samples['explosion_and_failure']={'max':max(h.costs[1:])}
        h.frame();samples['retry']={'max':h.frame(fire=True)}
        h=Harness(parts,m);h.setdist(1);samples['arrival']={'max':h.frame()};h.frame();samples['complete']={'max':h.frame(fire=True)};h.frame();samples['new_game']={'max':h.frame(fire=True)}
        return {'xex_sha256':m['sha256'],'model':'py65 NMOS 6502 only, excludes ANTIC DMA and OS interrupts','steady_drive_budget_cycles':15000,'steady_drive_budget_pass':all(v['max']<15000 for n,v in samples.items() if n in ('neutral','accelerate_steer','brake_steer','warning75','critical90','worst_case_drive_sweep','missed_255_tick_critical')),'samples':samples,'notes':'Whole-screen transitions/retry intentionally may span video frames; clock delta resynchronizes. Actual Atari800 evidence is separate.'}
if __name__=='__main__':print(json.dumps(profile(),indent=2))
