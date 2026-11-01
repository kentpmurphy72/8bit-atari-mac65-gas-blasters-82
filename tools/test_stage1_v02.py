#!/usr/bin/env python3
"""Execute delivered XEX's actual opcodes with py65 (not ANTIC/POKEY emulation)."""
import hashlib, json, tempfile, unittest
from collections import deque
from pathlib import Path
from py65.devices.mpu6502 import MPU
import build_stage1_v02 as b
from build_opening_sequence import xex_segments

class StageV02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.out=Path(cls.temp.name)
        cls.before=b.BASE.read_bytes();cls.man=b.build(cls.out)
        cls.parts=xex_segments(cls.out/cls.man['output'])
        cls.l=cls.man['labels'];cls.ol=cls.man['opening_labels']
        cls.meta=json.loads((b.ROOT/'assets/maps/taco_smell_stage1_v02.json').read_text())
        cls.rooms=[(b.ROOT/'assets/maps'/cls.meta['rooms'][r]['map_file']).read_text().splitlines() for r in cls.meta['room_order']]
        protected=[*sorted((b.ROOT/'assets/stage1').glob('*')),*sorted((b.ROOT/'assets/opening').glob('*')),b.ROOT/'tools/build_stage1.py',b.ROOT/'tools/test_stage1.py',b.ROOT/'assets/maps/taco_smell_stage1_v01.map',b.ROOT/'assets/maps/taco_smell_stage1_v01.json']
        cls.protected={p:p.read_bytes() for p in protected if p.is_file()}
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
    def walkable(self,x,y,room=0):return 0<=x<40 and 0<=y<22 and not self.meta['terrain'][self.rooms[room][y][x]]['solid']
    def test_reproducibility_and_baseline(self):
        before=(self.out/self.man['output']).read_bytes();b.build(self.out)
        self.assertEqual(before,(self.out/self.man['output']).read_bytes())
        self.assertEqual(self.before,b.BASE.read_bytes())
        for path,data in self.protected.items():self.assertEqual(path.read_bytes(),data)
        self.assertEqual(hashlib.sha256(self.before).hexdigest(),self.man['baseline_sha256'])
        baseline=xex_segments(b.BASE)
        for addr,data in baseline.items():
            if addr not in (0x2000,0x3F00,0x9800):self.assertEqual(data,self.parts[addr])
        changed=[i for i,(x,y) in enumerate(zip(baseline[0x2000],self.parts[0x2000])) if x!=y]
        allowed={self.ol[k]-0x2000+j for k in ('HANDLE_INPUT','DRAW_STAGE') for j in range(3)}
        self.assertTrue(set(changed)<=allowed)
        self.assertEqual(self.parts[0x2E0],b'\x00\x20')
        self.assertLess(max(a+len(d) for a,d in self.parts.items()),0xC000)
    def test_exhaustive_collision_and_bounds_in_all_rooms(self):
        for room in range(3):
            self.put('ROOM',room);self.put('LOOK_ROOM',room)
            for y in range(22):
                for x in range(40):
                    self.put('NX',x);self.put('NY',y);self.call('WALK')
                    self.assertEqual(self.c.a,int(self.walkable(x,y,room)),(room,x,y))
            for x,y in [(255,10),(40,10),(0,255),(22,22)]:
                self.put('NX',x);self.put('NY',y);self.call('WALK');self.assertEqual(self.c.a,0)
    def move(self,room,x,y,dx,dy):
        self.put('ROOM',room);self.put('LOOK_ROOM',room);self.put('PX',x);self.put('PY',y)
        self.put('TICKS',7)
        bit={(0,-1):1,(0,1):2,(-1,0):4,(1,0):8}[(dx,dy)]
        self.m[0xD300]=255^bit;self.call('FRAME')
    def test_all_eight_door_cells_and_held_direction(self):
        for room,x,dx,target,entry in [(0,38,1,1,1),(1,1,-1,0,38),(1,38,1,2,1),(2,1,-1,1,38)]:
            for y in (10,11):
                self.call('INIT');self.move(room,x,y,dx,0)
                self.assertEqual((self.get('ROOM'),self.get('PX'),self.get('PY')),(target,entry,y))
                self.assertEqual(self.get('DELAY'),179) # no room-load timer reset
                self.assertEqual(self.m[b.SCREEN+y*40+entry],14)
                for _ in range(8):self.call('FRAME')
                self.assertEqual(self.get('ROOM'),target) # held direction moves inward
                self.assertEqual((self.get('PX'),self.get('PY')),(entry+dx,y))
    def test_real_return_step_and_front_service_bounds(self):
        self.call('INIT');self.move(0,38,10,1,0)
        self.move(1,1,10,-1,0)
        self.assertEqual((self.get('ROOM'),self.get('PX'),self.get('PY')),(0,38,10))
        self.move(0,0,10,-1,0);self.assertEqual((self.get('ROOM'),self.get('PX')),(0,0))
        self.move(1,22,0,0,-1);self.assertEqual((self.get('ROOM'),self.get('PY')),(1,0))
        self.move(0,7,15,1,0);self.assertEqual(self.get('PX'),8)
        self.move(0,1,1,-1,0);self.assertEqual(self.get('PX'),1)
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
        self.assertEqual((self.get('PX'),self.get('PY')),(7,15))
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
        self.assertEqual((self.get('PX'),self.get('PY')),(7,15));self.assertEqual(self.get('ACTIVE'),0)
        for _ in range(5):self.call('FRAME')
        self.assertEqual(self.get('DELAY'),175) # held START cannot repeatedly reset
    def path(self,room,start,end):
        q=deque([start]);prev={start:None}
        while q:
            x,y=q.popleft()
            for n in [(x,y-1),(x,y+1),(x-1,y),(x+1,y)]:
                if n not in prev and self.walkable(*n,room):prev[n]=(x,y);q.append(n)
        route=[];n=end
        while n!=start:route.append(n);n=prev[n]
        return list(reversed(route))
    def test_playable_route_across_three_rooms_and_exit(self):
        self.call('INIT')
        for room,goal in [(0,(39,10)),(1,(39,11)),(2,(39,10))]:
            old=(self.get('PX'),self.get('PY'))
            for x,y in self.path(room,old,goal):
                bit={(0,-1):1,(0,1):2,(-1,0):4,(1,0):8}[(x-old[0],y-old[1])]
                self.m[0xD300]=255^bit
                for _ in range(8):self.call('FRAME')
                self.assertEqual(self.get('STATE'),2 if (room,x,y)==(2,39,10) else 0)
                old=(x,y)
        self.assertEqual(self.get('ROOM'),2)
        self.assertEqual(bytes(self.m[b.SCREEN+880:b.SCREEN+894]),b'STAGE COMPLETE')
        xy=(self.get('PX'),self.get('PY'))
        for _ in range(20):self.call('FRAME')
        self.assertEqual(xy,(self.get('PX'),self.get('PY')))
        self.m[0xD01F]=6;self.call('FRAME')
        self.assertEqual((self.get('STATE'),self.get('ROOM'),self.get('EROOM')),(0,0,0))
        self.assertEqual(self.get('DELAY'),180)
    def test_pursuit_stays_cardinal_walkable_and_in_same_room(self):
        self.call('INIT');self.put('ACTIVE',1)
        preserved=bytes(self.m[0x4000:0x9800])+bytes(self.m[0xA000:0xB000])
        for room in range(3):
            self.put('ROOM',room);self.put('LOOK_ROOM',room);self.put('EROOM',room)
            target=(38,11);dist={target:0};q=deque([target])
            while q:
                x,y=q.popleft()
                for n in [(x,y-1),(x,y+1),(x-1,y),(x+1,y)]:
                    if n not in dist and self.walkable(*n,room):dist[n]=dist[(x,y)]+1;q.append(n)
            self.put('PX',target[0]);self.put('PY',target[1]);self.put('EX',1);self.put('EY',10)
            while (self.get('EX'),self.get('EY'))!=target:
                old=(self.get('EX'),self.get('EY'));self.call('CHASE')
                for _ in range(120):
                    if not self.get('SEARCH'):break
                    self.call('SEARCH_STEP')
                self.assertEqual(self.get('SEARCH'),0)
                new=(self.get('EX'),self.get('EY'));self.assertTrue(self.walkable(*new,room))
                self.assertEqual(abs(new[0]-old[0])+abs(new[1]-old[1]),1)
                self.assertEqual(dist[new],dist[old]-1)
        self.assertEqual(preserved,bytes(self.m[0x4000:0x9800])+bytes(self.m[0xA000:0xB000]))
    def test_delayed_follow_preserves_identity_and_cancels_on_return(self):
        self.call('INIT');self.put('ACTIVE',1);self.put('DELAY',23)
        self.move(0,38,11,1,0)
        self.assertEqual((self.get('EROOM'),self.get('EX'),self.get('EY')),(0,2,10))
        self.assertEqual(self.get('FOLLOW_TIMER'),90);self.assertEqual(self.get('FY'),11)
        self.m[0xD300]=255
        for _ in range(40):self.call('FRAME')
        self.move(1,1,11,-1,0)
        self.assertEqual(self.get('FOLLOW_TIMER'),0)
        self.assertEqual((self.get('EROOM'),self.get('EX'),self.get('EY')),(0,2,10))
        self.assertEqual(self.get('DELAY'),23)
        self.move(0,38,10,1,0);self.m[0xD300]=255
        for _ in range(89):self.call('FRAME')
        self.assertEqual(self.get('EROOM'),0);self.assertEqual(self.get('FOLLOW_TIMER'),1)
        self.call('FRAME')
        self.assertEqual((self.get('EROOM'),self.get('EX'),self.get('EY')),(1,1,9)) # Billy at preferred entry
        self.assertEqual(self.get('ACTIVE'),1);self.assertEqual(self.get('STATE'),0)
    def test_follow_traverses_intermediate_rooms_and_backwards(self):
        self.call('INIT');self.put('ACTIVE',1)
        self.move(0,38,11,1,0);self.move(1,38,10,1,0);self.m[0xD300]=255
        self.assertEqual(self.get('FROOM'),1)
        for _ in range(self.get('FOLLOW_TIMER')):self.call('FRAME')
        self.assertEqual(self.get('EROOM'),1)
        self.call('FRAME');self.assertEqual(self.get('FOLLOW_TIMER'),90);self.assertEqual(self.get('FROOM'),2)
        for _ in range(90):self.call('FRAME')
        self.assertEqual(self.get('EROOM'),2);self.assertEqual(self.get('ACTIVE'),1)
        self.move(2,1,11,-1,0);self.assertEqual(self.get('FROOM'),1);self.assertEqual(self.get('FY'),11)
        self.m[0xD300]=255
        for _ in range(90):self.call('FRAME')
        self.assertEqual(self.get('EROOM'),1)
        self.assertTrue(self.walkable(self.get('EX'),self.get('EY'),1))
    def test_activation_after_leaving_dining_and_occupied_player_entry(self):
        self.call('INIT');self.move(0,38,10,1,0);self.m[0xD300]=255
        for _ in range(179):self.call('FRAME')
        self.assertEqual(self.get('ACTIVE'),1);self.assertEqual(self.get('EROOM'),0)
        self.assertEqual(self.get('FOLLOW_TIMER'),90)
        self.put('EROOM',0);self.put('EX',38);self.put('EY',10)
        self.move(1,1,10,-1,0)
        self.assertEqual(self.get('ROOM'),0)
        self.assertNotEqual((self.get('PX'),self.get('PY')),(38,10))
        self.assertEqual(abs(self.get('PX')-38)+abs(self.get('PY')-10),1)
        self.assertEqual(self.get('STATE'),0)
    def test_render_every_cell_in_each_room_and_sprites(self):
        self.call('INIT');self.put('ACTIVE',1)
        self.assertNotEqual(self.parts[b.FONT][112:120],self.parts[b.FONT][120:128])
        self.assertTrue(any(self.parts[b.FONT][112:120]));self.assertTrue(any(self.parts[b.FONT][120:128]))
        for room in range(3):
            self.put('ROOM',room);self.put('PX',1);self.put('PY',1)
            self.put('EROOM',room);self.put('EX',2);self.put('EY',1);self.call('DRAW')
            for y in range(22):
                for x in range(40):
                    expected=14 if (x,y)==(1,1) else 15 if (x,y)==(2,1) else self.parts[b.MAP][room*880+y*40+x]&127
                    self.assertEqual(self.m[b.SCREEN+y*40+x],expected,(room,x,y))
            self.put('EROOM',(room+1)%3);self.call('DRAW')
            self.assertNotEqual(self.m[b.SCREEN+42],15)
    def test_incremental_pursuit_keeps_input_live(self):
        self.call('INIT');self.put('ACTIVE',1);self.put('PX',38);self.put('PY',10)
        self.call('CHASE');self.assertEqual(self.get('SEARCH'),1)
        self.put('TICKS',7);self.m[0xD300]=251;self.call('FRAME')
        self.assertEqual(self.get('PX'),37);self.assertEqual(self.get('SEARCH'),1)
        # Crossing invalidates the old room's BFS, preserving the worker's position.
        self.move(0,38,10,1,0);self.assertEqual(self.get('SEARCH'),0)
        self.assertEqual(self.get('EROOM'),0)
    def test_real_vbi_elapsed_ticks_and_clock_wrap(self):
        self.call('INIT');self.put('DELAY',20);self.put('PREV_FRAME',250);self.m[0x14]=3
        self.call('FRAME');self.assertEqual(self.get('ELAPSED'),9);self.assertEqual(self.get('DELAY'),11)
        self.m[0x14]=15;self.call('FRAME')
        self.assertEqual(self.get('ACTIVE'),1);self.assertEqual(self.get('DELAY'),0)
        self.move(0,38,10,1,0);self.assertEqual(self.get('FOLLOW_TIMER'),90)
        self.m[0xD300]=255;self.m[0x14]=45;self.call('FRAME')
        self.assertEqual(self.get('FOLLOW_TIMER'),60)
        self.m[0x14]=110;self.call('FRAME')
        self.assertEqual(self.get('FOLLOW_TIMER'),0);self.assertEqual(self.get('EROOM'),1)
    def test_actor_overlay_order_and_hud_glyphs(self):
        self.call('INIT');self.put('ACTIVE',1);self.put('EX',7);self.put('EY',15);self.call('DRAW')
        self.assertEqual(self.m[b.SCREEN+15*40+7],14) # Billy drawn last
        for char in set(b"BILLY CAUGHT STAGE COMPLETE START")-{32}:
            self.assertTrue(any(self.parts[b.FONT][char*8:char*8+8]))
    def test_memory_layout_and_scratch_guards(self):
        segments=sorted(self.parts.items())
        for (addr,data),(nxt,_) in zip(segments,segments[1:]):self.assertLessEqual(addr+len(data),nxt)
        self.assertEqual(len(self.parts[b.MAP]),2640)
        self.assertEqual(len(self.parts[b.FONT]),1024)
        self.assertLessEqual(0x1000+len(self.parts[0x1000]),0x1800)
        self.assertEqual(self.parts[0x3F00],bytes([0x70]*3+[0x42,0,0xB0]+[2]*23+[0x41,0,0x3F]))
        self.call('INIT');self.put('ACTIVE',1)
        for addr in (b.SEEN-1,b.SEEN+880,0xB400+880,0xB900+880):self.m[addr]=0xA7
        self.put('PX',38);self.put('PY',11);self.call('CHASE')
        for _ in range(120):
            if not self.get('SEARCH'):break
            self.call('SEARCH_STEP')
        for addr in (b.SEEN-1,b.SEEN+880,0xB400+880,0xB900+880):self.assertEqual(self.m[addr],0xA7)

if __name__=='__main__':unittest.main(verbosity=2)
