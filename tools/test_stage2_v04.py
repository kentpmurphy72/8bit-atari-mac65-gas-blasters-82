#!/usr/bin/env python3
"""Emitted 6502 v0.4 tests. py65 + GTIA aliases, NOT Atari800/video emulation."""
import hashlib,json,random,tempfile,unittest
from pathlib import Path
import build_stage2_v04 as b
import test_stage2_v02_r1 as legacy
from build_opening_sequence import xex_segments

class Harness(legacy.Harness):
    def center(self,c,fraction=0):
        q=(c-4)*16+fraction;self.put('CAR_LO',q);self.put('CAR_HI',q>>8)
    def grass(self):return self.word('GRASS')
    def setgrass(self,value):self.put('GRASS0',value);self.put('GRASS1',value>>8)
    def xq4(self):return self.get('CAR_LO')+256*self.get('CAR_HI')

class OffroadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.m=b.build(cls.out);cls.parts=xex_segments(cls.out/cls.m['output'])
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):self.h=Harness(self.parts,self.m)
    # Preserve applicable baseline gameplay checks on the new actual binary.
    test_initial_hud_native_setup=legacy.PrototypeTests.test_initial_hud_native_setup
    test_full_ntsc_pal_deadlines_warning_thresholds_and_freeze=legacy.PrototypeTests.test_full_ntsc_pal_deadlines_warning_thresholds_and_freeze
    test_exact_120_second_default_drive_both_video_standards=legacy.PrototypeTests.test_exact_120_second_default_drive_both_video_standards
    test_mapping_all_values_and_fractional_integration=legacy.PrototypeTests.test_mapping_all_values_and_fractional_integration
    test_native_mapping_clamps_every_table_entry_and_duplicate_ticks=legacy.PrototypeTests.test_native_mapping_clamps_every_table_entry_and_duplicate_ticks
    test_rtc_wrap_and_missed_ticks=legacy.PrototypeTests.test_rtc_wrap_and_missed_ticks
    test_distance_underflow_and_no_early_zero_or_hundred_percent=legacy.PrototypeTests.test_distance_underflow_and_no_early_zero_or_hundred_percent
    test_gas_priority_tie_and_latched_success=legacy.PrototypeTests.test_gas_priority_tie_and_latched_success
    test_three_lives_retry_and_new_game_release_edges=legacy.PrototypeTests.test_three_lives_retry_and_new_game_release_edges
    test_held_fire_cannot_skip_failure_or_pharmacy_or_complete=legacy.PrototypeTests.test_held_fire_cannot_skip_failure_or_pharmacy_or_complete
    test_fire_inert_and_start_disabled_during_driving=legacy.PrototypeTests.test_fire_inert_and_start_disabled_during_driving
    test_division_native_precision_randomized=legacy.PrototypeTests.test_division_native_precision_randomized
    test_pharmacy_art_and_terminal_pmg_disable=legacy.PrototypeTests.test_pharmacy_art_and_terminal_pmg_disable
    test_explosion_frames_green_then_life_loss_once=legacy.PrototypeTests.test_explosion_frames_green_then_life_loss_once

    def test_center_thresholds_fractional_floor_both_sides_and_shake_independence(self):
        h=self.h;bus=legacy.GTIAReadWriteBus(h.mem,15);h.cpu.memory=bus
        for c,z in [(4,2),(13,2),(14,1),(20,1),(21,0),(54,0),(86,0),(87,1),(93,1),(94,2),(104,2)]:
            for fraction in (0,15):
                h.center(c,fraction);h.mem[0xD000]=255;h.mem[0xD001]=0;h.call('CLASSIFY')
                self.assertEqual((h.get('CENTER'),h.get('SURFACE')),(c,z))
        self.assertEqual(bus.collision_reads,[])
    def test_single_strongest_steering_penalty_all_nine_combinations(self):
        for c,surface_step in [(54,12),(18,10),(98,8)]:
            for pressure,pressure_step in [(0,12),(37125,10),(44550,8)]:
                h=Harness(self.parts,self.m);h.center(c);h.settime(pressure)
                before=h.xq4();h.frame(251)
                self.assertEqual(before-h.xq4(),min(surface_step,pressure_step))
                self.assertEqual(h.mem[0x84],min(surface_step,pressure_step))
                self.assertEqual(h.get('SPEED'),24)
    def test_exact_two_second_grass_crash_ntsc_pal_both_sides(self):
        for pal,fps in [(False,60),(True,50)]:
            for c in (10,98):
                h=Harness(self.parts,self.m,pal);h.center(c)
                for n in range(1,2*fps):
                    h.frame();self.assertEqual(h.grass(),n*h.get('UNITS'));self.assertEqual(h.get('STATE'),0)
                h.frame();self.assertEqual((h.grass(),h.get('STATE'),h.get('FAIL_KIND')),(600,1,2))
                self.assertEqual(h.get('LIVES'),3);self.assertEqual(h.time(),600)
    def test_exact_599_600_boundary_no_overflow_and_duplicate_ticks(self):
        h=self.h;h.center(10);h.setgrass(594);h.frame();self.assertEqual((h.grass(),h.get('STATE')),(599,0))
        before=(h.grass(),h.time(),h.dist());h.frame(delta=0);self.assertEqual((h.grass(),h.time(),h.dist()),before)
        h.frame();self.assertEqual((h.grass(),h.get('STATE')),(600,1))
        for value in (65535,65534,600):
            h=Harness(self.parts,self.m);h.center(10);h.setgrass(value);h.frame();self.assertEqual(h.grass(),600);self.assertEqual(h.get('FAIL_KIND'),2)
        h=Harness(self.parts,self.m,pal=True);h.center(98);h.frame(delta=255);self.assertEqual(h.grass(),600);self.assertEqual(h.get('FAIL_KIND'),2)
    def test_13_plus_07_second_grass_shoulder_pause_and_side_switch(self):
        for pal,fps in [(False,60),(True,50)]:
            h=Harness(self.parts,self.m,pal);h.center(10)
            for _ in range(13*fps//10):h.frame()
            self.assertEqual(h.grass(),390);h.center(18)
            for _ in range(3*fps):h.frame()
            self.assertEqual(h.grass(),390);self.assertEqual(h.get('STATE'),0)
            h.center(98)
            for _ in range(7*fps//10-1):h.frame();self.assertEqual(h.get('STATE'),0)
            h.frame();self.assertEqual((h.grass(),h.get('STATE')),(600,1))
    def test_pavement_resets_exposure_and_graphics_audio_immediately(self):
        h=self.h;h.center(10);h.setgrass(450);h.frame();self.assertTrue(any(h.mem[0x3E00:0x3F00]));self.assertNotEqual(h.mem[0xD201],0)
        h.center(54);h.frame();self.assertEqual(h.grass(),0);self.assertFalse(any(h.mem[0x3E00:0x3F00]));self.assertEqual(h.mem[0xD201],0);self.assertEqual(h.get('AMP'),0)
        h.center(10)
        for _ in range(119):h.frame();self.assertEqual(h.get('STATE'),0)
        h.frame();self.assertEqual(h.grass(),600);self.assertEqual(h.get('STATE'),1)
    def test_warning_stage_boundaries_skid_smoke_and_audio(self):
        h=self.h;h.center(10)
        for timer,stage in [(5,0),(149,0),(150,1),(299,1),(300,2),(449,2),(450,3),(599,3)]:
            h.setgrass(timer-5);h.put('PREV_STAGE',255);h.frame()
            self.assertEqual(h.get('OFF_STAGE'),stage);top=h.get('FX_Y')
            self.assertEqual(bytes(h.mem[0x3E00+top:0x3E00+top+16]),self.parts[0x2B00][stage*16:stage*16+16])
            self.assertTrue(any(h.mem[0x3E00:0x3F00]))
            if stage>=2:self.assertEqual(h.mem[0xD201],0xA4 if stage==2 else 0xA6)
            else:self.assertEqual(h.mem[0xD201],0)
    def test_shoulder_pauses_audio_escalation_retains_smoke_and_pulse_finishes(self):
        h=self.h;h.center(10);h.setgrass(300);h.frame();self.assertEqual(h.get('AUDIO_LEFT'),30)
        h.center(18);wait=h.get('AUDIO_WAIT');grass=h.grass()
        for _ in range(180):
            h.frame();self.assertEqual(h.grass(),grass);self.assertEqual(h.get('AUDIO_WAIT'),wait);self.assertEqual(h.get('OFF_STAGE'),2)
        self.assertEqual(h.mem[0xD201],0);self.assertTrue(any(h.mem[0x3E00:0x3F00]));h.center(10)
        for _ in range(wait//5):h.frame()
        self.assertNotEqual(h.mem[0xD201],0)
    def test_warning_audio_channel_safety_and_brief_cadence(self):
        h=self.h;h.center(10);h.setgrass(300);h.frame()
        starts=0;last=False
        for _ in range(80):
            h.setgrass(300);h.frame();on=h.mem[0xD201]!=0
            if on and not last:starts+=1
            last=on
            for reg in (0xD203,0xD205,0xD207):self.assertEqual(h.mem[reg],0)
            self.assertLessEqual(h.get('AUDIO_LEFT'),30)
        self.assertGreaterEqual(starts,3);self.assertEqual(h.mem[0xD208],0);self.assertEqual(h.mem[0xD20F],3)
    def test_bounded_combined_shake_and_pmg_visibility_no_gtia_position_reads(self):
        for pal in (False,True):
            h=Harness(self.parts,self.m,pal);bus=legacy.GTIAReadWriteBus(h.mem,15);h.cpu.memory=bus
            for c in (4,13,14,20,21,86,87,93,94,104):
                for time in (36630,37125,44550,49005):
                    for speed in (8,24,56):
                        for _ in range(8):
                            h.center(c);h.put('SPEED',speed);h.settime(time);h.setgrass(450);h.frame()
                            self.assertGreaterEqual(h.mem[0xD000],48);self.assertLessEqual(h.mem[0xD000]+8,156)
                            self.assertEqual(h.mem[0xD000],h.mem[0xD001]);self.assertLessEqual(h.get('AMP'),2)
                            top=h.get('OLD_PMG_Y')
                            self.assertEqual(bytes(h.mem[0x3C00+top:0x3C00+top+16]),self.parts[0x6800][:16])
                            self.assertEqual(bytes(h.mem[0x3D00+top:0x3D00+top+16]),self.parts[0x6800][16:])
                            self.assertEqual(h.mem[0xD012],0x36);self.assertEqual(h.mem[0xD013],14);self.assertEqual(h.mem[0xD01D],2)
                            self.assertEqual(h.xq4(),(c-4)*16)
                            if h.get('FX_LIVE'):self.assertLessEqual(h.get('FX_Y')+16,224)
            self.assertEqual(bus.collision_reads,[])
    def test_all_pairwise_and_three_way_terminal_priorities(self):
        # Full event matrix: no ties; all pairs; all three at the same tick.
        for gas in (False,True):
            for grass in (False,True):
                for arrival in (False,True):
                    h=Harness(self.parts,self.m);h.center(10 if grass else 54)
                    h.settime(49495 if gas else 0);h.setgrass(595 if grass else 0)
                    if arrival:h.setdist(1)
                    h.frame();kind=1 if gas else 2 if grass else 0
                    self.assertEqual(h.get('FAIL_KIND'),kind)
                    self.assertEqual(h.get('STATE'),1 if kind else 4 if arrival else 0)
                    self.assertEqual(h.get('LIVES'),3)
    def test_orange_red_crash_vs_green_gas_animation_and_frozen_counters(self):
        for kind in (1,2):
            h=Harness(self.parts,self.m)
            if kind==1:h.settime(49495)
            else:h.center(10);h.setgrass(595)
            h.frame();self.assertEqual(h.mem[0xD012],0xC8 if kind==1 else 0x28)
            frozen=(h.time(),h.dist(),h.grass(),h.get('PHASE_LO'),h.get('PHASE_HI'));colors=set()
            for _ in range(30):
                colors.add(h.mem[0xD012]);h.frame(246,fire=True,start=True)
                self.assertEqual((h.time(),h.dist(),h.grass(),h.get('PHASE_LO'),h.get('PHASE_HI')),frozen)
            self.assertEqual(colors,{0xC8} if kind==1 else {0x28,0x36});self.assertEqual(h.get('LIVES'),2);self.assertEqual(h.get('STATE'),2)
            self.assertFalse(any(h.mem[0x3E00:0x3F00]));self.assertEqual(h.mem[0xD201],0)
            for _ in range(40):h.frame(fire=True,start=True)
            self.assertEqual(h.get('LIVES'),2)
    def test_offroad_three_lives_release_to_retry_and_complete_reset(self):
        h=self.h
        for lives in (2,1,0):
            h.center(10);h.setgrass(595);h.frame(fire=True)
            for _ in range(40):h.frame(fire=True,start=True)
            self.assertEqual(h.get('STATE'),2 if lives else 3);self.assertEqual(h.get('LIVES'),lives)
            h.fresh();self.assertEqual(h.get('STATE'),0);self.assertEqual(h.get('LIVES'),lives or 3)
            self.assertEqual(h.grass(),0);self.assertEqual(h.time(),0);self.assertEqual(h.dist(),8640000)
            self.assertEqual(h.get('SPEED'),24);self.assertEqual(h.xq4(),800);self.assertEqual(h.get('CAR_Y_LO')+256*h.get('CAR_Y_HI'),2304)
            self.assertEqual(h.get('PHASE_LO'),0);self.assertEqual(h.get('PHASE_HI'),0)
            self.assertEqual(h.get('FAIL_KIND'),0);self.assertEqual(h.get('FX_LIVE'),0);self.assertEqual(h.mem[0xD201],0)
            self.assertFalse(any(h.mem[0x3E00:0x3F00]));self.assertEqual(h.mem[0xD012],0x36)
    def test_latched_arrival_never_crashes_later_and_clears_warning_effects(self):
        h=self.h;h.center(10);h.setgrass(450);h.frame();self.assertTrue(h.get('FX_LIVE'))
        h.center(18);h.setdist(1);h.frame();self.assertEqual(h.get('STATE'),4);grass=h.grass()
        for _ in range(200):h.frame()
        self.assertEqual(h.get('STATE'),4);self.assertEqual(h.grass(),grass);self.assertEqual(h.get('LIVES'),3)
        self.assertEqual(h.mem[0xD201],0);self.assertFalse(any(h.mem[0x3E00:0x3F00]))
    def test_geometry_hud_fonts_and_road_data_preserved(self):
        root=b.ROOT/'assets/stage2_v03';m=json.loads((root/'manifest.json').read_text());prior=xex_segments(root/m['output'])
        for addr in (0x2400,0x2800,0x3000,0x3400,0x3800,0x4000,0x6000,0x6600,0x6700,0x6800,0x8000,0x8400,0x8800,0x8C00,0x9400,0x9800):self.assertEqual(self.parts[addr],prior[addr],hex(addr))
        h=self.h;labels={row:h.hud(row) for row in (1,6,10,14,19,21)};static=bytes(h.mem[0x3100:0x3400])
        for _ in range(300):
            h.center(10);h.setgrass(450);h.settime(45000);h.frame()
            for row,text in labels.items():self.assertEqual(h.hud(row),text)
            bank=h.mem[0x2F4]<<8;self.assertEqual(bytes(h.mem[bank+256:bank+1024]),static)
            for y in range(24):self.assertEqual(bytes(h.mem[0x2400+y*40:0x2400+y*40+27]),prior[0x2400][y*40:y*40+27])
    def test_native_pavement_driver_matches_accepted_v03(self):
        root=b.ROOT/'assets/stage2_v03';m=json.loads((root/'manifest.json').read_text());prior=legacy.Harness(xex_segments(root/m['output']),m);h=self.h
        rng=random.Random(84)
        for _ in range(600):
            # Restrict X to pavement; later traction changes are intentional.
            for obj in (h,prior):obj.put('CAR_LO',800&255);obj.put('CAR_HI',800>>8)
            joy=rng.choice((255,254,253,251,247,246,249));h.frame(joy);prior.frame(joy)
            for key in ('SPEED','CAR_LO','CAR_HI','CAR_Y_LO','CAR_Y_HI','PHASE_LO','PHASE_HI','NEXT_BANK','TIME0','TIME1','DIST0','DIST1','DIST2'):
                self.assertEqual(h.get(key),prior.get(key),key)
            for addr in (0xD000,0xD001,0xD409):self.assertEqual(h.mem[addr],prior.mem[addr])
    def test_offroad_runtime_writes_stay_in_declared_ram_and_registers(self):
        class Traced(list):
            def __init__(self,values):super().__init__(values);self.writes=set()
            def __setitem__(self,key,value):
                if isinstance(key,int):self.writes.add(key)
                super().__setitem__(key,value)
        h=self.h;mem=Traced(h.mem);h.mem=mem;h.cpu.memory=mem
        for center in (54,18,10,98):
            h.center(center)
            for timer in (0,150,300,450):
                h.setgrass(timer);h.frame()
        h.setgrass(595);h.frame()
        for _ in range(30):h.frame()
        h.fresh();h.setdist(1);h.frame();h.fresh();h.fresh()
        allowed=set(range(0x100,0x200))|set(range(0x80,0x85))|set(range(0x86,0x8A))
        for first,last in [(h.r['LAST_FRAME'],h.r['OLD_PMG_Y']+1),(0x2400,0x27C0),(0x2900,0x2900+len(b.STATES)),(0x2A00,0x2A00+len(b.OFFROAD)),(0x3000,0x4000)]:allowed.update(range(first,last))
        allowed.update([0x14,0xD300,0xD010,0xD01F,0x22F,0x230,0x231,0x26F,0x2C0,0x2C1,0x2C2,0x2C4,0x2C5,0x2C6,0x2C7,0x2C8,0x2F4,0xD000,0xD001,0xD002,0xD008,0xD009,0xD00A,0xD012,0xD013,0xD014,0xD016,0xD017,0xD018,0xD019,0xD01A,0xD01B,0xD01D,0xD200,0xD201,0xD203,0xD205,0xD207,0xD208,0xD20F,0xD400,0xD402,0xD403,0xD407,0xD409,0xD40E])
        self.assertEqual(mem.writes-allowed,set());self.assertFalse(any(0x4000<=addr<0xA000 for addr in mem.writes))
    def test_pmg_effect_rows_clear_on_y_relocations_and_speed_anchors(self):
        h=self.h;h.center(10)
        for speed in [8]*130+[56]*130+[24]*130:
            h.put('SPEED',speed);h.setgrass(450);h.frame()
            top=h.get('FX_Y');self.assertGreaterEqual(top,32);self.assertLessEqual(top+16,224)
            self.assertFalse(any(h.mem[0x3E00:0x3E00+top]));self.assertFalse(any(h.mem[0x3E00+top+16:0x3F00]))
        h.center(54);h.frame();self.assertFalse(any(h.mem[0x3E00:0x3F00]))
    def test_pharmacy_two_press_flow_after_retained_grass_exposure(self):
        h=self.h;h.center(10);h.setgrass(450);h.frame();h.center(18);h.setdist(1);h.frame(fire=True)
        self.assertEqual(h.get('STATE'),4)
        for _ in range(30):h.frame(fire=True,start=True)
        self.assertEqual(h.get('STATE'),4);h.fresh();self.assertEqual(h.get('STATE'),5)
        for _ in range(30):h.frame(fire=True,start=True)
        self.assertEqual(h.get('STATE'),5);h.fresh();self.assertEqual(h.get('STATE'),0);self.assertEqual(h.grass(),0);self.assertEqual(h.get('LIVES'),3)
    def test_timer_599_boundary_pal_and_pavement_full_reset(self):
        h=Harness(self.parts,self.m,pal=True);h.center(98);h.setgrass(593);h.frame();self.assertEqual(h.grass(),599);self.assertEqual(h.get('STATE'),0)
        h.center(90);h.frame();self.assertEqual(h.grass(),599);h.center(54);h.frame();self.assertEqual(h.grass(),0)
        h.center(98);h.frame();self.assertEqual(h.grass(),6)
    def test_xex_reproducibility_segments_state_and_source(self):
        data=(self.out/self.m['output']).read_bytes();b.build(self.out);self.assertEqual(data,(self.out/self.m['output']).read_bytes());self.assertEqual(hashlib.sha256(data).hexdigest(),self.m['sha256'])
        self.assertEqual(self.parts[0x2E0],b'\x00\x20')
        parts=sorted(self.parts.items())
        for (addr,blob),(nxt,_) in zip(parts,parts[1:]):self.assertLessEqual(addr+len(blob),nxt)
        self.assertLessEqual(max(a+len(d) for a,d in parts),0xA000)
        self.assertTrue(0x2A00<=self.m['state']['GRASS0']<0x2B00)
        self.assertEqual(self.m['state']['GRASS1'],self.m['state']['GRASS0']+1)
        self.assertNotEqual(self.m['state']['GRASS0'],self.m['state']['TIME0'])

if __name__=='__main__':unittest.main(verbosity=2)
