#!/usr/bin/env python3
"""Execute the standalone Stage 2 XEX using py65; no ANTIC or OS emulation."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from py65.devices.mpu6502 import MPU
import build_stage2_v01 as b
from build_opening_sequence import xex_segments

class DrivingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.m=b.build(cls.out);cls.parts=xex_segments(cls.out/cls.m['output']);cls.l=cls.m['labels'];cls.t=cls.m['tuning']
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):
        self.cpu=MPU();self.mem=self.cpu.memory
        for addr,data in self.parts.items():self.mem[addr:addr+len(data)]=data
        self.mem[0xD300]=255;self.mem[0xD01F]=7;self.mem[0xD010]=1
        self.cpu.pc=b.CODE;self.wait=self.l['WAIT'];self.costs=[];self.until()
    def get(self,k):return self.mem[self.l[k]]
    def put(self,k,v):self.mem[self.l[k]]=v
    def until(self):
        for _ in range(20000):
            if self.cpu.pc==self.wait:return
            self.cpu.step()
        self.fail('CPU did not return to frame wait')
    def frame(self,joy=255,start=False,fire=False,delta=1):
        self.mem[0x14]=(self.mem[0x14]+delta)&255;self.mem[0xD300]=joy;self.mem[0xD01F]=6 if start else 7;self.mem[0xD010]=0 if fire else 1
        before=self.cpu.processorCycles;self.cpu.step();self.until();self.costs.append(self.cpu.processorCycles-before)
    def x(self):return self.get('CAR_LO')+256*self.get('CAR_HI')
    def phase(self):return self.get('PHASE_LO')+256*self.get('PHASE_HI')
    def pixels(self,phase,row,col):
        category=self.m['category_for_column'][col];glyph=category*4+row//8%4
        return self.parts[b.TABLE][phase*256+glyph*8+row%8]
    def test_boot_native_registers_sprite_and_standalone_memory(self):
        self.assertEqual(self.parts[0x2E0],b'\x00\x20')
        self.assertEqual(self.x(),800);self.assertEqual(self.get('SPEED'),24)
        for addr,value in [(0xD400,0x3A),(0x22F,0x3A),(0xD407,0x38),(0xD01D,2),(0xD40E,0x40)]:self.assertEqual(self.mem[addr],value)
        self.assertEqual(self.mem[0xD000],98);self.assertEqual(self.mem[0xD001],98)
        top=32+144
        self.assertTrue(any(self.mem[b.PMG+1024+top:b.PMG+1024+top+16]))
        self.assertEqual(sum(bool(v) for v in self.mem[b.PMG:b.PMG+1024]),0)
        for reg in (0xD201,0xD203,0xD205,0xD207):self.assertEqual(self.mem[reg],0)
    def test_neutral_automatic_positive_motion_and_pipeline(self):
        for n in range(1,81):
            self.frame()
            self.assertEqual(self.phase(),(n*24)%512)
            self.assertEqual(self.get('SHOWN_PHASE'),(((n-1)*24)%512)//16)
            self.assertEqual(self.x(),800)
    def test_speed_caps_braking_and_neutral_retention(self):
        for _ in range(100):self.frame(254)
        self.assertEqual(self.get('SPEED'),56)
        for _ in range(10):self.frame()
        self.assertEqual(self.get('SPEED'),56)
        for _ in range(100):self.frame(253)
        self.assertEqual(self.get('SPEED'),8)
        before=self.phase();self.frame(253);self.assertEqual(self.phase(),(before+8)%512)
        self.assertEqual(self.get('SPEED'),8)
    def test_combined_diagonals_steering_speed_and_opposition(self):
        for joy,dx,ds in [(250,-12,1),(249,-12,-1),(245,12,-1),(246,12,1)]:
            self.frame();self.frame(start=True);before=self.x();self.frame(joy)
            self.assertEqual(self.x(),before+dx);self.assertEqual(self.get('SPEED'),24+ds)
        x=self.x();speed=self.get('SPEED');self.frame(240)
        self.assertEqual(self.x(),x);self.assertEqual(self.get('SPEED'),speed)
    def test_steering_fractional_immediate_reverse_bounds_and_fire_reserved(self):
        self.frame(247);self.assertEqual(self.x(),812);self.assertEqual(self.mem[0xD000],98)
        self.frame(247,fire=True);self.assertEqual(self.x(),824);self.assertEqual(self.mem[0xD000],99)
        self.frame(251);self.assertEqual(self.x(),812)
        for _ in range(180):self.frame(251,fire=True)
        self.assertEqual(self.x(),0);self.assertEqual(self.mem[0xD000],48)
        for _ in range(240):self.frame(247)
        self.assertEqual(self.x(),1600);self.assertEqual(self.mem[0xD000]+8,48+108)
        before=self.x();self.frame();self.assertEqual(self.x(),before)
    def test_fonts_swap_coherently_and_hud_never_scrolls(self):
        baseline=self.parts[b.SCREEN]
        # Ignore only live speed/zone character addresses, all game values are static.
        dynamic={11*40+27+5,11*40+27+7,*range(13*40+27+5,13*40+27+10)}
        for i in range(64):
            self.frame(249 if i%2 else 246)
            shown=self.mem[0xD409]*256;hidden=self.get('NEXT_BANK')*256
            self.assertNotEqual(shown,hidden)
            p=self.get('SHOWN_PHASE');ready=self.get('READY_PHASE')
            self.assertEqual(bytes(self.mem[shown:shown+256]),self.parts[b.TABLE][p*256:p*256+256])
            self.assertEqual(bytes(self.mem[hidden:hidden+256]),self.parts[b.TABLE][ready*256:ready*256+256])
            for bank in (b.FONT_A,b.FONT_B):self.assertEqual(bytes(self.mem[bank+512:bank+1024]),self.parts[b.TEMPLATE][512:])
            for offset,value in enumerate(baseline):
                if offset not in dynamic:self.assertEqual(self.mem[b.SCREEN+offset],value)
        self.assertEqual(self.parts[b.DL][3]&0x30,0) # no hardware VSCROL/HSCROL
    def test_downward_pixel_motion_all_phases_including_wrap(self):
        for phase in range(32):
            for col in range(27):
                for y in range(192):
                    self.assertEqual(self.pixels((phase+1)%32,y,col),self.pixels(phase,(y-1)%192,col),(phase,y,col))
        self.assertNotEqual(self.pixels(0,0,13),self.pixels(16,0,13))
    def test_rendered_zone_boundaries_and_lane_location(self):
        edges=self.t['zone_edges_color_pixels']
        for phase in range(32):
            for y in range(32):
                for x in range(108):
                    packed=self.pixels(phase,y,x//4);color=(packed>>(6-2*(x%4)))&3
                    if x<edges[1] or x>=edges[4]:self.assertIn(color,(0,1))
                    elif x<edges[2] or x>=edges[3]:self.assertIn(color,(2,3))
                    else:
                        self.assertIn(color,(0,3))
                        if color==3:self.assertEqual(x,54)
    def test_zone_classification_center_and_no_penalties(self):
        for pixel,zone in [(0,0),(6,0),(7,1),(13,1),(14,2),(93,2),(94,1),(100,1),(101,0),(107,0)]:
            # Reachable centers are 4..104; edge examples use the nearest valid center.
            center=max(4,min(104,pixel));x=(center-4)*16
            self.put('CAR_LO',x&255);self.put('CAR_HI',x>>8);self.frame()
            expected=0 if center<7 or center>=101 else 1 if center<14 or center>=94 else 2
            self.assertEqual(self.get('ZONE'),expected)
        self.assertEqual(self.mem[b.SCREEN+10*40+27+10],128+ord('3')+32)
    def test_restart_release_armed_and_clock_wrap(self):
        for _ in range(12):self.frame(249)
        self.frame(start=True)
        self.assertEqual((self.x(),self.get('SPEED'),self.phase()),(800,24,0))
        for _ in range(5):self.frame(247,start=True)
        self.assertEqual(self.x(),860) # held START does not reset repeatedly
        self.frame();self.frame(start=True);self.assertEqual(self.x(),800)
        self.mem[0x14]=255;self.put('LAST_FRAME',255);old=self.phase();self.frame()
        self.assertEqual(self.phase(),(old+24)%512)
        old=self.phase();self.frame(delta=0);self.assertEqual(self.phase(),old)
    def test_extended_idle_three_minutes_no_drift_or_corruption(self):
        pristine=bytes(self.mem[b.PMG:b.PMG+2048]);hud=bytes(self.mem[b.SCREEN:b.SCREEN+960])
        # 10,800 simulated NTSC ticks, 180 seconds; full native loop executes.
        for n in range(10800):self.frame()
        self.assertEqual(self.phase(),(10800*24)%512)
        self.assertEqual(self.x(),800);self.assertEqual(self.get('SPEED'),24)
        self.assertEqual(bytes(self.mem[b.PMG:b.PMG+2048]),pristine)
        self.assertEqual(bytes(self.mem[b.SCREEN:b.SCREEN+960]),hud)
        self.assertLess(max(self.costs),8500)
    def test_build_reproducibility_segments_and_explicit_geometry(self):
        data=(self.out/self.m['output']).read_bytes();b.build(self.out)
        self.assertEqual(data,(self.out/self.m['output']).read_bytes());self.assertEqual(hashlib.sha256(data).hexdigest(),self.m['sha256'])
        segments=sorted(self.parts.items())
        for (addr,blob),(nxt,_) in zip(segments,segments[1:]):self.assertLessEqual(addr+len(blob),nxt)
        self.assertLessEqual(max(a+len(v) for a,v in segments),0xA000)
        self.assertEqual(self.t['zone_edges_color_pixels'],[0,7,14,94,101,108])
        self.assertEqual(len(self.parts[b.TABLE]),8192)
        self.assertEqual(len(self.parts[b.DL]),32)
        for char in 'GASMI0%SCORELIVES3DEMO':self.assertTrue(any(self.parts[b.TEMPLATE][(ord(char)+32)*8:(ord(char)+33)*8]))

if __name__=='__main__':unittest.main(verbosity=2)
