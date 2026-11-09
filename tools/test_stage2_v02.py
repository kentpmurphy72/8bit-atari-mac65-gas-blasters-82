#!/usr/bin/env python3
"""Actual emitted NMOS 6502 gameplay tests. py65, NOT Atari800/video emulation."""
import hashlib,json,tempfile,unittest,random
from pathlib import Path
from py65.devices.mpu6502 import MPU
import build_stage2_v02 as b
from build_opening_sequence import xex_segments

class Harness:
    def __init__(self,parts,m,pal=False):
        self.m=m;self.r=m['driver_labels'];self.s=m['state'];self.l=m['labels'];self.cpu=MPU();self.mem=self.cpu.memory;self.costs=[]
        for addr,data in parts.items():self.mem[addr:addr+len(data)]=data
        self.mem[0x62]=1 if pal else 0;self.mem[0xD300]=255;self.mem[0xD010]=1;self.mem[0xD01F]=7;self.cpu.pc=0x2000;self.until()
    def until(self):
        for _ in range(80000):
            if self.cpu.pc==self.r['WAIT']:return
            self.cpu.step()
        raise AssertionError(f'CPU hung ${self.cpu.pc:04x}')
    def get(self,k):return self.mem[(self.s if k in self.s else self.r)[k]]
    def put(self,k,v):self.mem[(self.s if k in self.s else self.r)[k]]=v&255
    def word(self,k):return self.get(k+'0')+256*self.get(k+'1')
    def time(self):return self.word('TIME')
    def dist(self):return self.word('DIST')+65536*self.get('DIST2')
    def settime(self,v):self.put('TIME0',v);self.put('TIME1',v>>8)
    def setdist(self,v):
        for n in range(3):self.put('DIST'+str(n),v>>(8*n))
    def frame(self,joy=255,fire=False,start=False,delta=1):
        self.mem[0x14]=(self.mem[0x14]+delta)&255;self.mem[0xD300]=joy;self.mem[0xD010]=0 if fire else 1;self.mem[0xD01F]=6 if start else 7
        before=self.cpu.processorCycles;self.cpu.step();self.until();cost=self.cpu.processorCycles-before;self.costs.append(cost);return cost
    def call(self,label):
        saved_pc=self.cpu.pc;self.cpu.pc=0x1000;addr=self.l[label];self.mem[0x1000:0x1004]=[0x20,addr&255,addr>>8,0xEA]
        before=self.cpu.processorCycles;self.cpu.step()
        for _ in range(80000):
            if self.cpu.pc==0x1003:
                self.cpu.pc=saved_pc;return self.cpu.processorCycles-before
            self.cpu.step()
        raise AssertionError('subroutine hung')
    def hud(self,row,col=27,n=13):return ''.join(chr((x-160)&255) for x in self.mem[b.SCREEN+row*40+col:b.SCREEN+row*40+col+n])
    def fail(self):
        self.settime(49495 if self.get('UNITS')==5 else 49494);self.frame()
        assert self.get('STATE')==1
        for _ in range(30 if self.get('UNITS')==5 else 25):self.frame()
    def fresh(self):self.frame();self.frame(fire=True)

class PrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.m=b.build(cls.out);cls.parts=xex_segments(cls.out/cls.m['output'])
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):self.h=Harness(self.parts,self.m)
    def test_initial_hud_native_setup(self):
        h=self.h;self.assertEqual((h.time(),h.dist(),h.get('SPEED'),h.get('LIVES')),(0,8640000,24,3))
        self.assertEqual(h.hud(4,30,4),'  0%');self.assertEqual(h.hud(8,30,7),'2.00 MI');self.assertEqual(h.hud(12,30,7),' 60 MPH');self.assertEqual(h.hud(21,30,6),'000000')
        self.assertEqual([h.mem[b.SCREEN+16*40+x] for x in (30,33,36)],[160]*3)
        for reg,v in [(0xD400,0x3A),(0xD407,0x38),(0xD40E,0x40),(0xD01D,2),(0xD000,98)]:self.assertEqual(h.mem[reg],v)
        self.assertEqual(h.get('CAR_Y_LO')+256*h.get('CAR_Y_HI'),144*16)
        self.assertTrue(any(self.parts[0x6000][(ord('!')+32)*8:(ord('!')+32)*8+8]))
    def test_full_ntsc_pal_deadlines_warning_thresholds_and_freeze(self):
        for pal,fps,units in [(False,60,5),(True,50,6)]:
            h=Harness(self.parts,self.m,pal);h.put('SPEED',8)
            for frame in range(1,165*fps+1):
                h.frame();t=frame*units
                self.assertEqual(h.time(),t)
                self.assertEqual(h.get('STATE'),int(t>=49500))
                if t<49500:self.assertEqual(h.get('WARN'),0 if t<37125 else 1 if t<44550 else 2)
                self.assertEqual(h.get('PERCENT'),t//495)
            frozen=(h.time(),h.dist(),h.get('PHASE_LO'),h.get('PHASE_HI'))
            for _ in range(fps*4):h.frame(246,fire=True,start=True)
            self.assertEqual(h.get('STATE'),2);self.assertEqual(h.get('LIVES'),2)
            self.assertEqual((h.time(),h.dist(),h.get('PHASE_LO'),h.get('PHASE_HI')),frozen)
    def test_exact_120_second_default_drive_both_video_standards(self):
        for pal,fps in [(False,60),(True,50)]:
            h=Harness(self.parts,self.m,pal)
            # Real native per-frame integration, not fast-forwarding.
            for frame in range(1,120*fps):h.frame();self.assertEqual(h.get('STATE'),0)
            self.assertGreater(h.dist(),0);self.assertGreater(h.get('CENTIMILES'),0)
            h.frame();self.assertEqual((h.get('STATE'),h.dist(),h.time()),(4,0,36000));self.assertEqual(h.get('LIVES'),3)
            frozen=(h.time(),h.dist(),h.get('PHASE_LO'),h.get('PHASE_HI'))
            for _ in range(240):h.frame(246,start=True)
            self.assertEqual((h.time(),h.dist(),h.get('PHASE_LO'),h.get('PHASE_HI')),frozen)
    def test_mapping_all_values_and_fractional_integration(self):
        q=self.m['qmph'];self.assertEqual([q[i] for i in (8,24,56)],[80,240,400])
        self.assertEqual(q[:8],[80]*8);self.assertEqual(q[57:],[400]*199)
        self.assertEqual([q[i+1]-q[i] for i in range(8,24)],[10]*16);self.assertEqual([q[i+1]-q[i] for i in range(24,56)],[5]*32)
        for pal in (False,True):
            h=Harness(self.parts,self.m,pal);expected=8640000
            rng=random.Random(82)
            for _ in range(600):
                speed=rng.randrange(8,57);delta=rng.randrange(1,5);h.put('SPEED',speed);h.frame(delta=delta);expected-=q[speed]*h.get('UNITS')*delta
                self.assertEqual(h.dist(),expected);self.assertEqual(h.get('MPH'),q[speed]//4)
    def test_native_mapping_clamps_every_table_entry_and_duplicate_ticks(self):
        for pal in (False,True):
            h=Harness(self.parts,self.m,pal)
            for speed in range(256):
                h.put('SPEED',speed);h.put('DELTA',1);h.setdist(8640000);h.call('DISTANCE')
                self.assertEqual(h.dist(),8640000-self.m['qmph'][speed]*h.get('UNITS'))
                self.assertEqual(self.parts[0x6D00][speed],self.m['qmph'][speed]//4)
        h=self.h;before=(h.time(),h.dist(),h.get('PHASE_LO'));h.frame(delta=0)
        self.assertEqual((h.time(),h.dist(),h.get('PHASE_LO')),before)
    def test_rtc_wrap_and_missed_ticks(self):
        for pal in (False,True):
            h=Harness(self.parts,self.m,pal);total=0
            for delta in (1,2,17,255,3,254,1):
                h.frame(delta=delta);total+=delta*h.get('UNITS');self.assertEqual(h.time(),total);self.assertEqual(h.dist(),8640000-total*240)
    def test_distance_underflow_and_no_early_zero_or_hundred_percent(self):
        h=self.h
        for remain in (1,43199,43200,43201,8640000):
            h.setdist(remain);h.call('HUD');self.assertEqual(h.get('CENTIMILES'),(remain+43199)//43200)
        h.settime(49499);h.call('HUD');self.assertEqual(h.get('PERCENT'),99);self.assertEqual(h.hud(4,30,4),' 99%')
        h.settime(0);h.setdist(1);h.frame();self.assertEqual((h.dist(),h.get('STATE')),(0,4));self.assertEqual(h.hud(8,30,7),'0.00 MI')
    def test_gas_priority_tie_and_latched_success(self):
        h=self.h;h.settime(49495);h.setdist(1);h.frame();self.assertEqual(h.get('STATE'),1);self.assertEqual(h.dist(),0)
        h=Harness(self.parts,self.m);h.settime(49490);h.setdist(1);h.frame();self.assertEqual(h.get('STATE'),4)
        for _ in range(300):h.frame()
        self.assertEqual(h.time(),49495);self.assertEqual(h.get('STATE'),4);self.assertEqual(h.get('LIVES'),3)
    def test_three_lives_retry_and_new_game_release_edges(self):
        h=self.h
        for lives in (2,1,0):
            h.fail();self.assertEqual(h.get('LIVES'),lives);self.assertEqual(h.get('STATE'),2 if lives else 3)
            text=''.join(h.hud(y,0,27) for y in range(24))
            self.assertIn('BILLY BLEW IT!' if lives else 'GAME OVER',text);self.assertNotIn('GAME OVER' if lives else 'BILLY BLEW IT!',text)
            for _ in range(80):h.frame(start=True)
            self.assertEqual(h.get('LIVES'),lives);h.fresh()
            self.assertEqual(h.get('STATE'),0);self.assertEqual(h.get('LIVES'),lives if lives else 3)
            self.assertEqual((h.time(),h.dist(),h.get('SPEED'),h.get('WARN'),h.get('PHASE_LO'),h.get('PHASE_HI')),(0,8640000,24,0,0,0))
            self.assertEqual((h.get('CAR_LO')+256*h.get('CAR_HI'),h.get('CAR_Y_LO')+256*h.get('CAR_Y_HI')),(800,2304))
            self.assertEqual(h.mem[0xD01D],2);self.assertEqual(h.mem[0xD012],0x36)
    def test_held_fire_cannot_skip_failure_or_pharmacy_or_complete(self):
        h=self.h;h.frame(fire=True);h.setdist(1);h.frame(fire=True);self.assertEqual(h.get('STATE'),4)
        for _ in range(30):h.frame(fire=True,start=True)
        self.assertEqual(h.get('STATE'),4);h.fresh();self.assertEqual(h.get('STATE'),5)
        for _ in range(30):h.frame(fire=True,start=True)
        self.assertEqual(h.get('STATE'),5);h.fresh();self.assertEqual((h.get('STATE'),h.get('LIVES')),(0,3))
        h.frame(fire=True);h.settime(49495);h.frame(fire=True)
        for _ in range(100):h.frame(fire=True,start=True)
        self.assertEqual((h.get('STATE'),h.get('LIVES')),(2,2));h.fresh();self.assertEqual((h.get('STATE'),h.get('LIVES')),(0,2))
    def test_fire_inert_and_start_disabled_during_driving(self):
        a=self.h;c=Harness(self.parts,self.m)
        for i in range(180):
            a.frame(246 if i<50 else 249,fire=True,start=True);c.frame(246 if i<50 else 249)
            for key in ['SPEED','CAR_LO','CAR_HI','CAR_Y_LO','CAR_Y_HI','PHASE_LO','PHASE_HI','STATE','LIVES','TIME0','TIME1','DIST0','DIST1','DIST2']:self.assertEqual(a.get(key),c.get(key))
    def test_warning_threshold_boundaries_step_shake_clamp_and_gas_only_flash(self):
        h=self.h
        for time,band,step in [(37124,0,12),(37125,1,10),(44549,1,10),(44550,2,8)]:
            h.settime(time);h.call('WARNINGS');self.assertEqual(h.get('WARN'),band);self.assertEqual(h.mem[0x84],step)
        for edge in (0,1600):
            h.put('CAR_LO',edge);h.put('CAR_HI',edge>>8);h.settime(45000)
            for _ in range(40):
                h.frame();self.assertGreaterEqual(h.mem[0xD000],48);self.assertLessEqual(h.mem[0xD000]+8,156)
                self.assertEqual(h.get('CAR_LO')+256*h.get('CAR_HI'),edge)
        for band,time,period in [(1,38000,150),(2,45000,30)]:
            h.settime(time);h.call('WARNINGS');h.put('FLASH',1);h.put('FLASH_TIME',0);h.call('HUD_DIRTY')
            before=bytes(h.mem[b.SCREEN:b.SCREEN+960]);h.setdist(1000000)
            for _ in range(period//5):h.frame()
            after=bytes(h.mem[b.SCREEN:b.SCREEN+960]);self.assertEqual(h.get('FLASH'),0)
            allowed={y*40+x for y,xs in [(2,range(28,38)),(4,range(30,34)),(8,range(30,34))] for x in xs}
            self.assertTrue(all(i in allowed for i,(a,c) in enumerate(zip(before,after)) if a!=c))
    def test_division_native_precision_randomized(self):
        h=self.h;rng=random.Random(6502)
        for _ in range(150):
            n=rng.randrange(8640001);den=rng.choice((495,43200,rng.randrange(1,65536)))
            for i in range(3):h.put('NUM'+str(i),n>>(8*i))
            h.put('DEN0',den);h.put('DEN1',den>>8);h.call('DIVIDE')
            self.assertEqual(h.word('NUM')+65536*h.get('NUM2'),n//den);self.assertEqual(h.word('REM'),n%den)
    def test_pharmacy_art_and_terminal_pmg_disable(self):
        h=self.h;h.put('FLASH',0);h.setdist(1);h.frame();self.assertEqual(h.mem[0xD01D],0);self.assertEqual(h.get('FLASH'),1);self.assertEqual(h.hud(4,30,4),'  0%')
        road=bytes(h.mem[b.SCREEN+y*40+x] for y in range(24) for x in range(27))
        self.assertGreater(sum(road.count(128+g) for g in (35,36,37,38,39)),100)
        self.assertIn('PHARMACY',h.hud(11,0,27));h.fresh();self.assertIn('STAGE 2 COMPLETE',h.hud(2,0,27))
    def test_explosion_frames_green_then_life_loss_once(self):
        h=self.h;h.settime(49495);h.frame();self.assertEqual(h.get('LIVES'),3);self.assertEqual(h.mem[0xD012],0xC8)
        shapes=set()
        for i in range(29):
            shapes.add(bytes(h.mem[0x3C00:0x3D00]));h.frame();self.assertEqual(h.get('LIVES'),3)
        h.frame();self.assertEqual(h.get('LIVES'),2);self.assertEqual(len(shapes),3)
    def test_long_scroll_fonts_and_panel_preserved(self):
        h=self.h
        static=bytes(h.mem[0x3100:0x3400]);labels={y:h.hud(y) for y in (1,6,10,14,19,21)}
        for i in range(1800):
            h.frame(246 if i%300<150 else 249)
            bank=h.mem[0x2F4]<<8;self.assertEqual(bytes(h.mem[bank+256:bank+1024]),static)
            for y,v in labels.items():self.assertEqual(h.hud(y),v)
            self.assertTrue(all(h.mem[b.SCREEN+y*40+x]==self.parts[b.SCREEN][y*40+x] for y in range(24) for x in range(27)))
    def test_driving_native_differential_r3_below_warning(self):
        old=json.loads((b.BASE/'manifest.json').read_text());parts=xex_segments(b.BASE/old['output']);cpu=MPU();mem=cpu.memory
        for addr,data in parts.items():mem[addr:addr+len(data)]=data
        mem[0xD300]=255;mem[0xD010]=1;mem[0xD01F]=7;cpu.pc=0x2000
        def until():
            for _ in range(20000):
                if cpu.pc==old['labels']['WAIT']:return
                cpu.step()
            raise AssertionError('r3 hang')
        until();h=self.h; rng=random.Random(3)
        for i in range(2000):
            joy=rng.choice((255,254,253,251,247,250,246,249,245));h.frame(joy)
            mem[0x14]=(mem[0x14]+1)&255;mem[0xD300]=joy;cpu.step();until()
            for key in ('SPEED','CAR_LO','CAR_HI','CAR_Y_LO','CAR_Y_HI','READY_PHASE','SHOWN_PHASE','PHASE_LO','PHASE_HI','NEXT_BANK'):
                self.assertEqual(h.get(key),mem[old['labels'][key]],(i,key))
            for reg in (0xD000,0xD001,0xD409):self.assertEqual(h.mem[reg],mem[reg])
            self.assertEqual(h.mem[0x3C00:0x3E00],mem[0x3C00:0x3E00])
    def test_runtime_writes_confined_to_declared_ram_and_registers(self):
        class Traced(list):
            def __init__(self,values):super().__init__(values);self.writes=set()
            def __setitem__(self,key,value):
                if isinstance(key,int):self.writes.add(key)
                super().__setitem__(key,value)
        h=self.h;mem=Traced(h.mem);h.mem=mem;h.cpu.memory=mem
        for _ in range(160):h.frame(246)
        h.settime(38000)
        for _ in range(180):h.frame(249)
        h.fail();h.fresh();h.setdist(1);h.frame();h.fresh();h.fresh()
        allowed=set(range(0x100,0x200))|set(range(0x80,0x85))|set(range(0x86,0x8A))
        for start,end in [(h.r['LAST_FRAME'],h.r['OLD_PMG_Y']+1),(0x2900,0x2900+len(b.STATES)),(0x2400,0x27C0),(0x3000,0x4000)]:allowed.update(range(start,end))
        allowed.update([0x14,0xD300,0xD010,0xD01F,0x22F,0x230,0x231,0x26F,0x2C0,0x2C1,0x2C4,0x2C5,0x2C6,0x2C7,0x2C8,0x2F4,0xD000,0xD001,0xD008,0xD009,0xD012,0xD013,0xD016,0xD017,0xD018,0xD019,0xD01A,0xD01B,0xD01D,0xD201,0xD203,0xD205,0xD207,0xD400,0xD402,0xD403,0xD407,0xD409,0xD40E])
        self.assertEqual(mem.writes-allowed,set())
        # Static code/data, OS memory and ROMs must never be overwritten.
        self.assertFalse(any(0x4000<=addr<0xA000 for addr in mem.writes))
    def test_measured_steady_frame_budget(self):
        from profile_stage2_v02 import profile
        results=profile();self.assertTrue(results['steady_drive_budget_pass'],results)
    def test_reproducible_manifest_segments_and_prior_hash(self):
        before=(self.out/self.m['output']).read_bytes();b.build(self.out);self.assertEqual(before,(self.out/self.m['output']).read_bytes());self.assertEqual(hashlib.sha256(before).hexdigest(),self.m['sha256'])
        segments=sorted(self.parts.items())
        for (addr,data),(nxt,_) in zip(segments,segments[1:]):self.assertLessEqual(addr+len(data),nxt)
        self.assertEqual(self.parts[0x2E0],b'\x00\x20');self.assertLessEqual(max(a+len(d) for a,d in segments),0xA000)
        self.assertEqual(self.m['r3_sha256'],hashlib.sha256((b.BASE/'GasBlasters82_Stage2_Driving_v01_r3.xex').read_bytes()).hexdigest())
        self.assertEqual(self.parts[0x2800],bytes([0x70]*3+[0x44,0,0x24]+[4]*23+[0x41,0,0x28]))

if __name__=='__main__':unittest.main(verbosity=2)
