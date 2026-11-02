#!/usr/bin/env python3
"""Repeatable py65 CPU-only cycle samples; excludes ANTIC DMA/OS interrupts."""
import json
from test_stage1_v03 import StageV03Tests as Harness


def profile():
    Harness.setUpClass()
    try:
        t=Harness();t.setUp()
        start=t.c.processorCycles;t.init()
        samples={'stage_initialization_full_draw':t.c.processorCycles-start}
        t.put('PX',38);t.put('PY',20)
        for i,(x,y) in enumerate([(5,1),(15,1),(25,1)]):t.worker(i,x,y)
        moves=[[],[],[]];last=[(t.wget(i,'EX'),t.wget(i,'EY')) for i in range(3)]
        for frame in range(45):
            t.frame()
            for i in range(3):
                pos=(t.wget(i,'EX'),t.wget(i,'EY'))
                if pos!=last[i]:moves[i].append(frame+1);last[i]=pos
        samples['three_worker_normal_frame_max']=t.max_cycles
        t.init();t.worker(0,8,15);t.worker(1,13,15);t.worker(2,16,15)
        t.frame();t.max_cycles=0;t.frame(joy=247,fire=True)
        samples['three_worker_blast_hit_frame']=t.max_cycles
        t.init();t.worker(0,2,10);t.worker(1,5,10);t.worker(2,1,10,room=1)
        t.put('PX',38);t.put('PY',10);t.put('TICKS',7);t.frame(joy=247)
        samples['occupied_room_transition_full_draw']=t.max_cycles
        return {'xex_sha256':t.man['sha256'],'model':'py65 6502, no ANTIC DMA or OS interrupt cycles',
                'atari800_tested':False,'samples_cpu_cycles':samples,
                'worker_move_frames_in_45_frame_sample':moves,
                'observed_move_intervals':[[b-a for a,b in zip(m,m[1:])] for m in moves],
                'search_budget_cells_per_frame':8,
                'notes':'Sampled costs, not an exhaustive worst-case proof or real Atari frame-time measurement. Full room draw is limited to transitions/restart.'}
    finally:Harness.tearDownClass()

if __name__=='__main__':print(json.dumps(profile(),indent=2))
