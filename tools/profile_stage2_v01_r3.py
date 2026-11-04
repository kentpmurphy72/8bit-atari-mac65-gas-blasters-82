#!/usr/bin/env python3
"""Repeatable CPU-only Y/PMG relocation scenarios, not Atari video validation."""
import json
from test_stage2_v01_r3 import RevisionTests as Harness

def profile():
    Harness.setUpClass()
    try:
        samples={}
        for name,joy in [('accelerate_and_steer',246),('brake_and_steer',249),('neutral_default',255)]:
            h=Harness();h.setUp()
            for _ in range(120):h.frame(joy);h.assert_sprite()
            samples[name]={'min_cpu_cycles':min(h.costs),'max_cpu_cycles':max(h.costs),'speed_q4':h.get('SPEED'),'car_y_q4':h.yq4(),'target_y_q4':h.target()}
        h=Harness();h.setUp()
        for _ in range(32):h.frame(254)
        h.costs=[]
        frames=0
        while h.yq4()!=h.target():h.frame();h.assert_sprite();frames+=1
        samples['neutral_settle_after_default_to_max']={'frames':frames,'max_cpu_cycles':max(h.costs),'car_y_q4':h.yq4()}
        h.frame(start=True);samples['start_reset']={'cpu_cycles':h.costs[-1],'car_y_q4':h.yq4()}
        return {'xex_sha256':Harness.m['sha256'],'model':'py65 CPU only; excludes ANTIC DMA and OS interrupts','atari800_tested':False,'samples':samples,'notes':'PMG plane bytes checked after each sampled tick. Actual flicker, sprite alignment and response require Atari800 testing.'}
    finally:Harness.tearDownClass()
if __name__=='__main__':print(json.dumps(profile(),indent=2))
