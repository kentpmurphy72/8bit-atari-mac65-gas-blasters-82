#!/usr/bin/env python3
"""Native v0.1-r3 CPU regression: original driving coverage plus real PMG Y."""
import hashlib,json,tempfile,unittest
from pathlib import Path
import build_stage2_v01_r3 as b
from build_opening_sequence import xex_segments
import test_stage2_v01 as original_tests

class RevisionTests(original_tests.DrivingTests):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.m=b.build(cls.out)
        cls.parts=xex_segments(cls.out/cls.m['output']);cls.l=cls.m['labels'];cls.t=cls.m['tuning']
        cls.protected={p:p.read_bytes() for folder in ['assets/stage2_v01','assets/stage2_v01_r2','assets/stage1_v05','assets/opening'] for p in (b.ROOT/folder).glob('*') if p.is_file()}
        for name in ['build_stage2_v01.py','test_stage2_v01.py','profile_stage2_v01.py','build_stage2_v01_r2.py','test_stage2_v01_r2.py','profile_stage2_v01_r2.py']:
            p=b.ROOT/'tools'/name;cls.protected[p]=p.read_bytes()
    def yq4(self):return self.get('CAR_Y_LO')+256*self.get('CAR_Y_HI')
    def target(self):return self.get('TARGET_Y_LO')+256*self.get('TARGET_Y_HI')
    def assert_sprite(self):
        # Compare every byte in both live player planes with the correct bitmap
        # translated to the actual Q4->integer Y. Old positions must be all zero.
        y=self.yq4()//16;self.assertTrue(0<=y<=192-16)
        first=32+y;self.assertEqual(self.get('OLD_PMG_Y'),first)
        sprite=self.parts[0x6800]
        for plane in range(2):
            expected=bytearray(256);expected[first:first+16]=sprite[plane*16:plane*16+16]
            start=b.PMG+1024+plane*256
            self.assertEqual(bytes(self.mem[start:start+256]),bytes(expected))
        self.assertEqual(bytes(self.mem[b.PMG:b.PMG+1024]),self.parts[b.PMG][:1024])
        self.assertEqual(bytes(self.mem[b.PMG+1536:b.PMG+2048]),self.parts[b.PMG][1536:])
    def settle(self):
        for _ in range(128):
            self.assert_sprite()
            if self.yq4()==self.target()==self.m['vertical_targets_q4'][self.get('SPEED')]:return
            self.frame()
        self.fail('Y target did not settle within bound')
    def test_up_maximum_physically_relocates_and_neutral_holds(self):
        initial=self.yq4();last=initial
        for _ in range(160):
            self.frame(254);y=self.yq4();self.assertLessEqual(y,last);self.assertLessEqual(last-y,12);self.assert_sprite();last=y
        self.assertEqual(self.get('SPEED'),56);self.assertEqual(self.target(),80*16);self.assertEqual(self.yq4(),80*16)
        self.assertLess(last,initial)
        for _ in range(120):self.frame();self.assertEqual(self.get('SPEED'),56);self.assertEqual(self.yq4(),80*16);self.assert_sprite()
    def test_down_minimum_positive_scroll_low_car_and_neutral_holds(self):
        for _ in range(120):self.frame(254)
        last=self.yq4()
        for _ in range(200):
            self.frame(253);y=self.yq4();self.assertGreaterEqual(y,last);self.assertLessEqual(y-last,12);self.assert_sprite();last=y
        self.assertEqual((self.get('SPEED'),self.yq4(),self.target()),(8,160*16,160*16))
        for _ in range(80):
            before=self.phase();self.frame();self.assertEqual(self.phase(),(before+8)%512);self.assertEqual(self.yq4(),160*16)
    def test_intermediate_speed_target_settles_without_spring_back(self):
        for _ in range(20):self.frame(254)
        self.assertEqual(self.get('SPEED'),44);self.assertEqual(self.target(),104*16)
        self.assertNotEqual(self.yq4(),self.target()) # explicitly exercise smoothing
        last=self.yq4()
        for _ in range(40):
            self.frame();self.assertLessEqual(self.yq4(),last);self.assertLessEqual(last-self.yq4(),12);last=self.yq4();self.assertEqual(self.get('SPEED'),44);self.assert_sprite()
        self.assertEqual(last,104*16);self.assertNotEqual(last,144*16)
    def test_steering_diagonals_and_fire_at_both_y_extremes(self):
        for speed,top in [(56,80),(8,160)]:
            self.put('SPEED',speed);self.settle();self.assertEqual(self.yq4(),top*16)
            for _ in range(200):self.frame(251,fire=True);self.assert_sprite()
            self.assertEqual(self.x(),0)
            for _ in range(200):self.frame(247,fire=True);self.assert_sprite()
            self.assertEqual(self.x(),1600);self.assertEqual(self.yq4(),top*16)
        for joy,ds,dx in [(250,1,-12),(246,1,12),(249,-1,-12),(245,-1,12)]:
            self.frame();self.frame(start=True);oldx=self.x();oldy=self.yq4();self.frame(joy,fire=True)
            self.assertEqual((self.get('SPEED'),self.x()),(24+ds,oldx+dx))
            self.assertEqual(self.yq4(),oldy-12 if ds>0 else oldy+12);self.assert_sprite()
    def test_start_resets_physical_y_fraction_and_all_old_rows(self):
        for joy in (254,253,246,249):
            for _ in range(17):self.frame(joy)
            self.assert_sprite()
            self.frame();self.frame(start=True)
            self.assertEqual((self.x(),self.yq4(),self.target(),self.get('SPEED'),self.phase()),(800,144*16,144*16,24,0))
            self.assertEqual(self.yq4()&15,0);self.assert_sprite()
            self.frame(start=True);self.assertEqual(self.yq4(),144*16)
    def test_pmg_guard_regions_road_hud_stay_fixed_through_reversals(self):
        baseline=bytes(self.mem[b.SCREEN:b.SCREEN+960]);dynamic={11*40+27+5,11*40+27+7,*range(13*40+27+5,13*40+27+10)}
        for n in range(256):
            self.frame(246 if (n//32)%2==0 else 249)
            self.assert_sprite()
            for offset,value in enumerate(baseline):
                if offset not in dynamic:self.assertEqual(self.mem[b.SCREEN+offset],value)
            for bank in (b.FONT_A,b.FONT_B):self.assertEqual(bytes(self.mem[bank+512:bank+1024]),self.parts[b.TEMPLATE][512:])
        self.assertEqual(bytes(self.mem[0x6800:0x6820]),self.parts[0x6800])
        self.assertLess(max(self.costs),8500)
    def test_mapping_monotonic_and_lookup_bounds(self):
        ys=self.m['vertical_targets_q4']
        self.assertEqual((ys[8],ys[24],ys[56]),(160*16,144*16,80*16))
        self.assertTrue(all(a>=z for a,z in zip(ys,ys[1:])))
        self.assertTrue(all(80*16<=y<=160*16 for y in ys))
        for speed in range(8,57):
            self.put('SPEED',speed);self.frame();self.assertEqual(self.target(),ys[speed]);self.assert_sprite()
    def test_r2_runtime_and_static_segments_exactly_preserved(self):
        r2=xex_segments(b.ROOT/'assets/stage2_v01_r2/GasBlasters82_Stage2_Driving_v01_r2.xex')
        self.assertEqual(set(r2),set(self.parts))
        changed={addr for addr in r2 if self.parts[addr]!=r2[addr]}
        self.assertEqual(changed,{0x6600,0x6700})
        self.assertEqual(self.parts[b.CODE],r2[b.CODE])
        for speed in range(25):
            self.assertEqual(self.parts[0x6600][speed],r2[0x6600][speed])
            self.assertEqual(self.parts[0x6700][speed],r2[0x6700][speed])
    def test_piecewise_continuity_exact_anchors_and_slope(self):
        ys=self.m['vertical_targets_q4']
        self.assertEqual([ys[i] for i in (8,24,56)],[160*16,144*16,80*16])
        self.assertEqual(ys[23],145*16);self.assertEqual(ys[25],142*16)
        self.assertEqual({ys[i]-ys[i+1] for i in range(8,24)},{16})
        self.assertEqual({ys[i]-ys[i+1] for i in range(24,56)},{32})
        self.assertEqual(ys[:8],[160*16]*8);self.assertEqual(ys[57:],[80*16]*199)
        # Sampling across the slope change must never jump more than the existing
        # smoothing cap, even though targets now change twice as fast above default.
        for _ in range(10):self.frame(253)
        self.settle()
        for _ in range(35):
            before=self.yq4();self.frame(254);self.assertLessEqual(abs(self.yq4()-before),12);self.assert_sprite()
    def test_build_reproducibility_segments_and_explicit_geometry(self):
        data=(self.out/self.m['output']).read_bytes();b.build(self.out)
        self.assertEqual(data,(self.out/self.m['output']).read_bytes());self.assertEqual(hashlib.sha256(data).hexdigest(),self.m['sha256'])
        for p,old in self.protected.items():self.assertEqual(p.read_bytes(),old,str(p))
        original=xex_segments(b.ROOT/'assets/stage2_v01/GasBlasters82_Stage2_Driving_v01.xex')
        for addr,blob in original.items():
            if addr!=b.CODE:self.assertEqual(self.parts[addr],blob)
        segments=sorted(self.parts.items())
        for (addr,blob),(nxt,_) in zip(segments,segments[1:]):self.assertLessEqual(addr+len(blob),nxt)
        self.assertLessEqual(b.CODE+len(self.parts[b.CODE]),b.SCREEN)
        self.assertEqual(len(self.parts[0x6800]),32)

if __name__=='__main__':unittest.main(verbosity=2)
