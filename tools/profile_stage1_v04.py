#!/usr/bin/env python3
"""CPU-only repeatable scenarios. No ANTIC DMA or OS interrupt emulation."""
import json
from test_stage1_v04 import MovementTests as Harness

def profile():
    Harness.setUpClass()
    try:
        t=Harness();t.setUp();samples={}
        before=t.cpu.processorCycles;t.call('NEW_INIT');samples['restart_with_pmg_clear']=t.cpu.processorCycles-before
        for name,joy,delta,xy in [('cardinal_three_workers',247,1,(20*128,12*128)),('diagonal_three_workers',245,1,(20*128,12*128)),('wall_slide_three_workers',246,1,(73*16,4*128)),('bounded_two_tick_catchup',247,2,(20*128,12*128))]:
            t.call('NEW_INIT');t.position(*xy)
            for i,(x,y) in enumerate([(5,1),(15,1),(25,1)]):t.worker(i,x,y)
            costs=[]
            for _ in range(8):t.tick(joy,delta=delta,full=True);costs.append(t.cycles[-1])
            samples[name]={'max_cpu_cycles':max(costs),'cycles_per_dispatch':costs}
        t.call('NEW_INIT');t.position(307*16,10*128);t.tick(247,full=True);samples['door_entry_full_room_draw']=t.cycles[-1]
        return {'xex_sha256':t.man['sha256'],'model':'py65 CPU only, excludes ANTIC DMA and OS interrupts','atari800_tested':False,'search_budget_cells_per_dispatch':8,'max_movement_catchup_ticks':2,'samples':samples,'notes':'Measured scenarios, not exhaustive worst-case timing. Room redraw can span video frames. Verify control feel/PMG alignment in Atari800.'}
    finally:Harness.tearDownClass()
if __name__=='__main__':print(json.dumps(profile(),indent=2))
