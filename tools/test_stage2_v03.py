#!/usr/bin/env python3
"""Geometry/graphics checks plus the full accepted r1 native gameplay suite.
py65 + GTIA register-alias shim, NOT Atari800/ANTIC video emulation.
"""
import hashlib,json,random,tempfile,unittest
from pathlib import Path
import build_stage2_v03 as b
import test_stage2_v02_r1 as r1
from build_opening_sequence import xex_segments

class RoadTests(r1.PrototypeTests):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.m=b.build(cls.out)
        cls.parts=xex_segments(cls.out/cls.m['output'])
        cls.prior_manifest=json.loads((b.BASE/'manifest.json').read_text())
        cls.prior=xex_segments(b.BASE/cls.prior_manifest['output'])
    def test_fixed_binary_preserves_gameplay_data_and_previous_artifacts(self):
        # Adapt the r1 fix-specific assertion: v0.3 changes scenery, never code.
        self.assertEqual(set(self.parts),set(self.prior))
        for address,data in self.parts.items():
            self.assertEqual(len(data),len(self.prior[address]))
            if address not in b.CHANGED:self.assertEqual(data,self.prior[address],hex(address))
        self.assertEqual(self.parts[0x2000],self.prior[0x2000]);self.assertEqual(self.parts[0x7000],self.prior[0x7000])
        self.assertEqual(self.m['state'],self.prior_manifest['state']);self.assertEqual(self.m['labels'],self.prior_manifest['labels'])
        for address in (0x3000,0x3400,0x6000):self.assertEqual(self.parts[address][256:],self.prior[address][256:])
        for address in (0x2400,0x9400):
            for y in range(24):self.assertEqual(self.parts[address][y*40+27:y*40+40],self.prior[address][y*40+27:y*40+40])
    def test_reproducible_manifest_segments_and_prior_hash(self):
        data=(self.out/self.m['output']).read_bytes();rebuilt=b.build(self.out)
        self.assertEqual(data,(self.out/rebuilt['output']).read_bytes());self.assertEqual(hashlib.sha256(data).hexdigest(),rebuilt['sha256'])
        self.assertEqual(len(data),len((b.BASE/self.prior_manifest['output']).read_bytes()))
        self.assertEqual(self.parts[0x2E0],b'\x00\x20')
        for (addr,blob),(nxt,_) in zip(sorted(self.parts.items()),sorted(self.parts.items())[1:]):self.assertLessEqual(addr+len(blob),nxt)
        self.assertLessEqual(max(addr+len(blob) for addr,blob in self.parts.items()),0xA000)
        self.assertEqual(rebuilt['baseline_v02_r1_sha256'],b.BASE_SHA)
    def test_measured_steady_frame_budget(self):
        from profile_stage2_v03 import profile
        self.assertTrue(profile()['steady_drive_budget_pass'])
    def test_geometry_widths_boundaries_and_symmetry(self):
        zones=self.m['zone_for_local_x']
        expected=['grass']*14+['shoulder']*7+['pavement']*66+['shoulder']*7+['grass']*14
        self.assertEqual(zones,expected);self.assertEqual(zones,zones[::-1])
        self.assertEqual([x['end']-x['start'] for x in self.m['geometry']['bands']],[14,7,66,7,14])
        for x in range(108):self.assertEqual(b.zone_at(x),expected[x])
        for x in (-1,108,1000,13.5):
            with self.assertRaises(ValueError):b.zone_at(x)
    def test_all_phase_pixels_match_the_geometric_cross_section(self):
        # Independent absolute-pixel oracle, including sub-character boundaries.
        for phase in range(32):
            for row in range(32):
                for x in range(108):
                    column=x//4;glyph=self.m['category_for_column'][column]*4+row//8
                    packed=self.parts[0x4000][phase*256+glyph*8+row%8]
                    pixel=(packed>>(6-2*(x%4)))&3
                    if x<14 or x>=94:
                        expected=0 if ((row-phase)%32+(x%4)*3)%8==0 else 1
                    elif x<21 or x>=87:
                        expected=3 if ((row-phase)%32+x%4)%8==0 else 2
                    else:expected=3 if x==54 and (row-phase)%32<16 else 0
                    self.assertEqual(pixel,expected,(phase,row,x))
    def test_screen_glyphs_geometry_and_hud_partition(self):
        self.assertEqual(len(self.m['road_categories']),8)
        for addr in (0x2400,0x9400):
            for y in range(24):
                for x in range(27):self.assertEqual(self.parts[addr][y*40+x],128+4*self.m['category_for_column'][x]+y%4)
        for addr in (0x3000,0x3400,0x6000):self.assertEqual(self.parts[addr][:256],self.parts[0x4000][:256])
        self.assertEqual(self.parts[0x2400],self.parts[0x9400])
    def test_native_font_publication_uses_new_geometry_on_every_phase(self):
        h=self.h
        for phase in range(32):
            # Prepare/publication via native r1 code; no Python font blit.
            h.put('PHASE_LO',(phase*16-24)&255);h.put('PHASE_HI',((phase*16-24)%512)>>8)
            h.frame();self.assertEqual(h.get('READY_PHASE'),phase)
            bank=h.get('NEXT_BANK')<<8
            self.assertEqual(bytes(h.mem[bank:bank+256]),self.parts[0x4000][phase*256:(phase+1)*256])
            h.frame();self.assertEqual(h.get('SHOWN_PHASE'),phase)
            self.assertEqual(bytes(h.mem[h.mem[0x2F4]*256:h.mem[0x2F4]*256+256]),self.parts[0x4000][phase*256:(phase+1)*256])
    def test_no_grass_or_shoulder_penalties_or_traction(self):
        for x in (0,14,50,90,100):
            h=r1.Harness(self.parts,self.m);h.put('CAR_LO',x*16);h.put('CAR_HI',x*16>>8)
            for _ in range(181):h.frame()
            self.assertEqual(h.get('STATE'),0);self.assertEqual(h.get('LIVES'),3)
            self.assertEqual(h.get('SPEED'),24);self.assertEqual(h.time(),905)
            before=h.get('CAR_LO')+256*h.get('CAR_HI');h.frame(251)
            self.assertEqual(h.get('CAR_LO')+256*h.get('CAR_HI'),max(0,before-12))
    def test_native_r1_differential_including_warning_and_result_transitions(self):
        for pal in (False,True):
            h=r1.Harness(self.parts,self.m,pal);prior=r1.Harness(self.prior,self.prior_manifest,pal)
            h.cpu.memory=r1.GTIAReadWriteBus(h.mem);prior.cpu.memory=r1.GTIAReadWriteBus(prior.mem)
            def tick(joy=255,fire=False,start=False):
                h.frame(joy,fire,start);prior.frame(joy,fire,start)
                for key in self.m['state']:self.assertEqual(h.get(key),prior.get(key),key)
                for key in self.m['driver_labels']:
                    if key in ('LAST_FRAME','NEXT_BANK','TABLE_HIGH','READY_PHASE','SHOWN_PHASE','PHASE_LO','PHASE_HI','SPEED','CAR_LO','CAR_HI','CAR_Y_LO','CAR_Y_HI','OLD_PMG_Y'):self.assertEqual(h.get(key),prior.get(key),key)
                self.assertEqual(h.mem[0x3C00:0x3E00],prior.mem[0x3C00:0x3E00])
                for addr in (0xD000,0xD001,0xD012,0xD013,0xD01D,0xD400,0xD409):self.assertEqual(h.mem[addr],prior.mem[addr])
                for y in range(24):self.assertEqual(h.hud(y),prior.hud(y))
            rng=random.Random(83)
            for _ in range(240):tick(rng.choice((255,254,253,251,247,246,249)),start=True)
            for value in (37120,44545,49000):
                h.settime(value);prior.settime(value)
                for _ in range(40):tick(249)
            # Failure, freeze, release, retry; then arrival, completion, new run.
            for obj in (h,prior):obj.settime(49494 if pal else 49495)
            for _ in range(40):tick(fire=True)
            tick();tick(fire=True)
            for obj in (h,prior):obj.setdist(1)
            tick();tick();tick(fire=True);tick(fire=True);tick();tick(fire=True)
            self.assertEqual(h.get('STATE'),0);self.assertEqual(h.get('LIVES'),3)

if __name__=='__main__':unittest.main(verbosity=2)
