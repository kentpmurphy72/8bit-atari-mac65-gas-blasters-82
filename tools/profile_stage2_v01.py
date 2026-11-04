#!/usr/bin/env python3
"""Repeatable CPU-only driving scenarios; excludes ANTIC DMA and OS interrupts."""
import json
from test_stage2_v01 import DrivingTests as Harness

def profile():
    Harness.setUpClass()
    try:
        samples={}
        for name,joy,speed in [('neutral_default',255,24),('accelerate_and_steer',246,24),('brake_and_steer',249,24),('maximum_speed',247,56),('minimum_speed',251,8)]:
            h=Harness();h.setUp();h.put('SPEED',speed)
            for _ in range(64):h.frame(joy)
            samples[name]={'min_cpu_cycles':min(h.costs),'max_cpu_cycles':max(h.costs),'last_speed_q4':h.get('SPEED')}
        h=Harness();h.setUp();h.frame();h.frame(start=True)
        samples['start_reset']={'cpu_cycles':h.costs[-1]}
        return {'xex_sha256':Harness.m['sha256'],'model':'py65 CPU only, excludes ANTIC DMA and OS interrupts','atari800_tested':False,'samples':samples,'road_copy_bytes_per_frame':256,'hud_hardware_scrolling':False,'notes':'One video-tick dispatch publishes a previously prepared font, updates controls/PMG/HUD and prepares the inactive road font. These samples do not establish real Atari timing or visual/audio behavior.'}
    finally:Harness.tearDownClass()
if __name__=='__main__':print(json.dumps(profile(),indent=2))
