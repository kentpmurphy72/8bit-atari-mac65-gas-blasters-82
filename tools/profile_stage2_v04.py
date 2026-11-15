#!/usr/bin/env python3
"""Repeatable NMOS 6502 costs; excludes ANTIC DMA and OS interrupt overhead."""
import json,tempfile
from pathlib import Path
import build_stage2_v04 as b
from test_stage2_v04 import Harness
from build_opening_sequence import xex_segments

def profile():
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp);m=b.build(out);parts=xex_segments(out/m['output']);samples={}
        for name,c,grass,time,joy in [('pavement',54,0,0,246),('shoulder',18,200,0,255),('grass_skid',10,0,0,255),('grass_mild',10,150,0,255),('grass_smoke',10,300,0,255),('critical_combined',98,450,45000,255)]:
            h=Harness(parts,m);h.center(c);h.setgrass(grass);h.settime(time)
            for _ in range(12):h.frame(joy)
            samples[name]={'min':min(h.costs),'max':max(h.costs)}
        h=Harness(parts,m);peak=0;case=None;cases=0
        # All legal speeds, pressure boundaries, surface types, exposure stages,
        # diagonal/throttle combinations; force simultaneous HUD/PMG updates.
        for speed in range(8,57):
            for time in (0,37120,44545,49490):
                for center in (10,18,54):
                    for grass in (0,145,295,445):
                        for joy in (255,246,249):
                            h.put('STATE',0);h.put('FAIL_KIND',0);h.put('SPEED',speed);h.center(center);h.settime(time);h.setgrass(grass);h.setdist(43201)
                            h.put('CAR_Y_LO',0);h.put('CAR_Y_HI',9);h.put('FLASH_TIME',25);h.put('PREV_STAGE',255)
                            for key in ('LAST_GAS','LAST_MI','LAST_MPH','LAST_LIVES','LAST_FLASH'):h.put(key,255)
                            cost=h.frame(joy);cases+=1
                            if cost>peak:peak=cost;case={'speed':speed,'time_units':time,'center':center,'grass_units':grass,'joy':joy}
        samples['drive_sweep']={'max':peak,'case':case,'cases':cases}
        for name,kind in [('gas_failure',1),('offroad_failure',2)]:
            h=Harness(parts,m)
            if kind==1:h.settime(49495)
            else:h.center(10);h.setgrass(595)
            enter=h.frame();h.costs=[]
            for _ in range(30):h.frame()
            samples[name]={'entry':enter,'animation_result_max':max(h.costs)};h.frame();samples[name+'_retry']={'max':h.frame(fire=True)}
        h=Harness(parts,m);h.setdist(1);samples['arrival']={'max':h.frame()};h.frame();samples['completion']={'max':h.frame(fire=True)}
        h=Harness(parts,m,pal=True);h.settime(45000);h.center(54);samples['missed_255_ticks_paved']={'max':h.frame(delta=255)}
        return {'xex_sha256':m['sha256'],'model':'py65 NMOS 6502 only; ANTIC DMA and OS interrupts NOT included','active_drive_budget_cycles':15000,'active_drive_budget_pass':peak<15000 and samples['missed_255_ticks_paved']['max']<15000,'samples':samples,'notes':'Full-screen result/retry transitions may span frames as in accepted v0.3; actual raster and audio need Atari800.'}
if __name__=='__main__':
    report=profile();print(json.dumps(report,indent=2));raise SystemExit(0 if report['active_drive_budget_pass'] else 1)
