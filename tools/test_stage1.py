#!/usr/bin/env python3
"""Execute delivered XEX's actual opcodes with py65 (not ANTIC/POKEY emulation)."""
import hashlib, json, tempfile, unittest
from collections import deque
from pathlib import Path
from py65.devices.mpu6502 import MPU
import build_stage1 as b
from build_opening_sequence import xex_segments

class StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.out=Path(cls.temp.name)
        cls.before=b.BASE.read_bytes();cls.man=b.build(cls.out)
        cls.parts=xex_segments(cls.out/cls.man['output'])
        cls.l=cls.man['labels'];cls.ol=cls.man['opening_labels']
        cls.meta=json.loads((b.ROOT/'assets/maps/taco_smell_stage1_v01.json').read_text())
        cls.rows=(b.ROOT/'assets/maps'/cls.meta['terrain_file']).read_text().splitlines()
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):
        self.c=MPU();self.m=self.c.memory
        for addr,data in self.parts.items():self.m[addr:addr+len(data)]=data
        self.m[0xD01F]=7;self.m[0xD010]=1;self.m[0xD300]=255
    def get(self,k):return self.m[self.l[k]]
    def put(self,k,v):self.m[self.l[k]]=v
    def call(self,k,limit=2000000):
        self.c.sp=0xFD;self.m[0x1FE]=0xFE;self.m[0x1FF]=0x0F;self.c.pc=self.l[k]
        for _ in range(limit):
            self.c.step()
            if self.c.pc==0x0FFF:return
        self.fail('CPU routine did not return: '+k)
    def walkable(self,x,y):return 0<=x<48 and 0<=y<22 and not self.meta['terrain'][self.rows[y][x]]['solid']
    def test_reproducibility_and_baseline(self):
        before=(self.out/self.man['output']).read_bytes();b.build(self.out)
        self.assertEqual(before,(self.out/self.man['output']).read_bytes())
        self.assertEqual(self.before,b.BASE.read_bytes())
        self.assertEqual(hashlib.sha256(self.before).hexdigest(),self.man['baseline_sha256'])
        baseline=xex_segments(b.BASE)
        for addr,data in baseline.items():
            if addr not in (0x2000,0x3F00,0x9800):self.assertEqual(data,self.parts[addr])
        changed=[i for i,(x,y) in enumerate(zip(baseline[0x2000],self.parts[0x2000])) if x!=y]
        allowed={self.ol[k]-0x2000+j for k in ('HANDLE_INPUT','DRAW_STAGE') for j in range(3)}
        self.assertTrue(set(changed)<=allowed)
        self.assertEqual(self.parts[0x2E0],b'\x00\x20')
        self.assertLess(max(a+len(d) for a,d in self.parts.items()),0xC000)
    def test_exhaustive_collision(self):
        for y in range(22):
            for x in range(48):
                self.put('NX',x);self.put('NY',y);self.call('WALK')
                self.assertEqual(self.c.a,int(self.walkable(x,y)),(x,y))
        for x,y in [(255,10),(48,10),(0,255),(27,22)]:
            self.put('NX',x);self.put('NY',y);self.call('WALK');self.assertEqual(self.c.a,0)
    def test_joystick_blocking_priority_and_boundary(self):
        self.call('INIT')
        for x,y,joy,expected in [(1,1,251,(1,1)),(0,10,251,(0,10)),
                                  (27,0,254,(27,0)),(7,13,246,(7,12))]:
            self.put('PX',x);self.put('PY',y);self.put('TICKS',7)
            self.m[0xD300]=joy;self.call('FRAME')
            self.assertEqual((self.get('PX'),self.get('PY')),expected)
    def test_opening_flow_music_and_debounce(self):
        self.c.pc=0x2000;wait=self.ol['FRAME_WAIT']
        def until():
            for _ in range(300000):
                if self.c.pc==wait:return
                self.c.step()
            self.fail('frame timeout')
        until()
        def frame(start=7,fire=1):
            self.m[0xD01F]=start;self.m[0xD010]=fire;self.m[0x14]=(self.m[0x14]+1)&255;self.c.step();until()
        def scene(n,dl,track):
            self.assertEqual(self.m[self.ol['SCENE']],n)
            self.assertEqual(self.m[0x230]|self.m[0x231]<<8,dl)
            self.assertEqual(self.m[self.ol['TRACK']],track)
        scene(0,0x3C00,0)
        for _ in range(30):frame()
        self.assertGreater(self.m[self.ol['NOTE_INDEX']],2)
        frame(6);scene(1,0x3D00,1)
        for _ in range(20):frame(6)
        scene(1,0x3D00,1);frame();idx=self.m[self.ol['NOTE_INDEX']]
        frame(fire=0);scene(2,0x3E00,1)
        self.assertIn(self.m[self.ol['NOTE_INDEX']],(idx,(idx+1)%128))
        for _ in range(10):frame(fire=0)
        scene(2,0x3E00,1);frame();frame(fire=0);scene(3,0x3F00,2)
        self.assertEqual(self.m[0xD40E],0x40)
        self.assertEqual([self.m[r] for r in (0xD201,0xD203,0xD205,0xD207)],[0]*4)
        self.assertEqual((self.get('PX'),self.get('PY')),(7,13))
    def test_spawn_caught_restart_and_frozen_state(self):
        self.call('INIT')
        for _ in range(179):self.call('FRAME')
        self.assertEqual(self.get('ACTIVE'),0);self.call('FRAME');self.assertEqual(self.get('ACTIVE'),1)
        self.put('EX',self.get('PX'));self.put('EY',self.get('PY'));self.put('ENEMY_TIMER',15)
        self.call('FRAME');self.assertEqual(self.get('STATE'),1)
        self.assertEqual(bytes(self.m[b.SCREEN+880:b.SCREEN+887]),b'CAUGHT!')
        xy=(self.get('PX'),self.get('PY'));self.m[0xD300]=247
        for _ in range(20):self.call('FRAME')
        self.assertEqual((self.get('PX'),self.get('PY')),xy)
        self.m[0xD01F]=6;self.call('FRAME');self.assertEqual(self.get('STATE'),0)
        self.assertEqual((self.get('PX'),self.get('PY')),(7,13));self.assertEqual(self.get('ACTIVE'),0)
        for _ in range(5):self.call('FRAME')
        self.assertEqual(self.get('DELAY'),175) # held START cannot repeatedly reset
    def test_actual_joystick_route_and_complete(self):
        start=(7,13);end=(47,10);q=deque([start]);prev={start:None}
        while q:
            x,y=q.popleft()
            for n in [(x,y-1),(x,y+1),(x-1,y),(x+1,y)]:
                if n not in prev and self.walkable(*n):prev[n]=(x,y);q.append(n)
        route=[];n=end
        while n!=start:route.append(n);n=prev[n]
        route.reverse();self.call('INIT');old=start
        for x,y in route:
            dx,dy=x-old[0],y-old[1];bit={(0,-1):1,(0,1):2,(-1,0):4,(1,0):8}[(dx,dy)]
            self.m[0xD300]=255^bit
            for _ in range(8):self.call('FRAME')
            self.assertEqual((self.get('PX'),self.get('PY')),(x,y));old=(x,y)
        self.assertEqual(self.get('STATE'),2);self.assertEqual(self.get('CAM'),18)
        self.assertEqual(bytes(self.m[b.SCREEN+880:b.SCREEN+894]),b'STAGE COMPLETE')
    def test_pursuit_routes_around_every_obstacle(self):
        # Test each reachable target with enemy at front spawn; every next step
        # must be cardinal, walkable, and reduce independent BFS distance by one.
        self.call('INIT');self.put('ACTIVE',1)
        preserved=bytes(self.m[0x4000:0x9800])+bytes(self.m[0xA000:0xB000])
        targets=[(7,13),(47,10),(27,0),(1,1),(45,19),(20,20)]
        for target in targets:
            dist={target:0};q=deque([target])
            while q:
                x,y=q.popleft()
                for n in [(x,y-1),(x,y+1),(x-1,y),(x+1,y)]:
                    if n not in dist and self.walkable(*n):dist[n]=dist[(x,y)]+1;q.append(n)
            self.put('PX',target[0]);self.put('PY',target[1]);self.put('EX',2);self.put('EY',10)
            while (self.get('EX'),self.get('EY'))!=target:
                old=(self.get('EX'),self.get('EY'));self.call('CHASE')
                for _ in range(150):
                    if not self.get('SEARCH'):break
                    self.call('SEARCH_STEP')
                self.assertEqual(self.get('SEARCH'),0)
                new=(self.get('EX'),self.get('EY'))
                self.assertTrue(self.walkable(*new));self.assertEqual(abs(new[0]-old[0])+abs(new[1]-old[1]),1)
                self.assertEqual(dist[new],dist[old]-1)
        self.assertEqual(preserved,bytes(self.m[0x4000:0x9800])+bytes(self.m[0xA000:0xB000]))
    def test_incremental_search_keeps_input_active(self):
        self.call('INIT');self.put('ACTIVE',1);self.put('PX',45);self.put('PY',10)
        self.call('CHASE');self.assertEqual(self.get('SEARCH'),1)
        self.put('TICKS',7);self.m[0xD300]=251;self.call('FRAME')
        self.assertEqual((self.get('PX'),self.get('PY')),(44,10))
        self.assertEqual(self.get('SEARCH'),1)
        for _ in range(150):
            if not self.get('SEARCH'):break
            self.call('FRAME')
        self.assertEqual(self.get('SEARCH'),0)
        self.assertNotEqual((self.get('EX'),self.get('EY')),(2,10))
    def test_renderer_camera_terrain_and_distinct_actors(self):
        self.call('INIT')
        for x in (7,25,47):
            self.put('PX',x);self.call('DRAW');cam=max(0,min(18,x-14));self.assertEqual(self.get('CAM'),cam)
            self.assertEqual(self.m[b.SCREEN+13*40+x-cam],14)
            for y in range(22):
                for col in range(30):
                    if (col+cam,y)==(x,13):continue
                    expected=self.parts[b.MAP][y*48+col+cam]&127
                    self.assertEqual(self.m[b.SCREEN+y*40+col],expected)
        self.assertNotEqual(self.parts[b.FONT][112:120],self.parts[b.FONT][120:128])

if __name__=='__main__':unittest.main(verbosity=2)
