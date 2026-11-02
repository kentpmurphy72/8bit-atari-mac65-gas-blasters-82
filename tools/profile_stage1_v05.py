#!/usr/bin/env python3
"""Repeatable 6502-only blast/PMG/three-worker scenarios, excludes ANTIC/OS."""
import json
from test_stage1_v05 import BlastTests as Harness

def profile():
    Harness.setUpClass()
    try:
        t=Harness();t.setUp();t.position(24*128,12*128)
        for i,(x,y) in enumerate([(25,12),(26,11),(27,13)]):t.worker(i,x,y)
        t.tick();aim=[]
        for _ in range(4):t.tick(True,2);aim.append(t.costs[-1])
        cloud=[]
        for _ in range(8):t.tick(True,2);cloud.append(t.costs[-1])
        moving=[]
        for _ in range(8):t.tick(False,0);moving.append(t.costs[-1])
        return {'xex_sha256':t.man['sha256'],'model':'py65 CPU, excludes ANTIC DMA / OS interrupts','atari800_tested':False,'three_active_workers':True,'scenario':'Dining (24,12), aim right 4 ticks; hold 8; release and walk up 8 while cloud completes','windup_and_discharge_cpu_cycles':aim,'cloud_and_knockback_cpu_cycles':cloud,'cloud_plus_pmg_walking_cpu_cycles':moving,'max_sample_cpu_cycles':max(aim+cloud+moving),'notes':'Sampled native runtime costs, not an exhaustive timing bound or real Atari frame-rate measurement.'}
    finally:Harness.tearDownClass()
if __name__=='__main__':print(json.dumps(profile(),indent=2))
