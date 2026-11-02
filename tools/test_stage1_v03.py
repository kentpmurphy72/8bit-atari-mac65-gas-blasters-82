#!/usr/bin/env python3
"""Execute Stage 1 v0.3 XEX opcodes with py65; not a full Atari emulator."""
import hashlib, json, tempfile, unittest
from collections import deque
from pathlib import Path
from py65.devices.mpu6502 import MPU
import build_stage1_v03 as b
from build_opening_sequence import xex_segments

class StageV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.out=Path(cls.temp.name)
        cls.before=b.BASE.read_bytes();cls.man=b.build(cls.out)
        cls.parts=xex_segments(cls.out/cls.man['output'])
        cls.l=cls.man['labels'];cls.ol=cls.man['opening_labels']
        cls.meta=json.loads((b.ROOT/'assets/maps/taco_smell_stage1_v02.json').read_text())
        cls.rooms=[(b.ROOT/'assets/maps'/cls.meta['rooms'][r]['map_file']).read_text().splitlines() for r in cls.meta['room_order']]
        protected=[*sorted((b.ROOT/'assets/stage1').glob('*')),*sorted((b.ROOT/'assets/opening').glob('*')),b.ROOT/'tools/build_stage1.py',b.ROOT/'tools/test_stage1.py',b.ROOT/'assets/maps/taco_smell_stage1_v01.map',b.ROOT/'assets/maps/taco_smell_stage1_v01.json']
        protected += [*sorted((b.ROOT/'assets/stage1_v02').glob('*')),b.ROOT/'tools/build_stage1_v02.py',b.ROOT/'tools/test_stage1_v02.py']
        cls.protected={p:p.read_bytes() for p in protected if p.is_file()}
        cls.rules=json.loads((b.ROOT/'assets/gameplay/taco_smell_stage1_v03_rules.json').read_text())

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

    def path(self,room,start,end):
        q=deque([start]);prev={start:None}
        while q:
            x,y=q.popleft()
            for n in [(x,y-1),(x,y+1),(x-1,y),(x+1,y)]:
                if n not in prev and self.walkable(*n,room):prev[n]=(x,y);q.append(n)
        route=[];n=end
        while n!=start:route.append(n);n=prev[n]
        return list(reversed(route))

    def init(self):
        self.call('INIT');self.max_cycles=0
    def worker(self,i,x,y,room=0,stun=0):
        for field,value in dict(EX=x,EY=y,EROOM=room,ACTIVE=1,AWAIT=0,DELAY=0,STUN=stun,SEPARATE=0,ENTRY_GRACE=0,ENTRY_FRESH=0,ENEMY_TIMER=10,FOLLOW_TIMER=0).items():self.put(f'{field}_{i}',value)
    def wget(self,i,field):return self.get(f'{field}_{i}')
    def frame(self,joy=255,fire=False,start=False,delta=1):
        self.m[0x14]=(self.m[0x14]+delta)&255;self.m[0xD300]=joy
        self.m[0xD010]=0 if fire else 1;self.m[0xD01F]=6 if start else 7
        before=self.c.processorCycles;self.call('FRAME');self.max_cycles=max(self.max_cycles,self.c.processorCycles-before)
    def shoot(self,direction):
        self.frame() # release rearm
        self.frame(joy=255^{1:1,2:2,3:4,4:8}[direction],fire=True)
    def test_spawn_times_unique_and_preserved_across_revisits(self):
        self.init()
        for _ in range(59):self.frame()
        self.assertEqual(self.wget(0,'ACTIVE'),0);self.frame();self.assertEqual(self.wget(0,'ACTIVE'),1)
        self.assertEqual([self.wget(i,'ACTIVE') for i in range(3)],[1,0,0])
        self.move(0,38,11,1,0);self.assertEqual(self.get('ROOM'),1)
        for _ in range(29):self.frame()
        self.assertEqual(self.wget(1,'ACTIVE'),0);self.frame();self.assertEqual(self.wget(1,'ACTIVE'),1)
        pos=(self.wget(1,'EX'),self.wget(1,'EY'))
        self.move(1,1,11,-1,0);self.move(0,38,11,1,0)
        self.assertEqual(self.wget(1,'ACTIVE'),1);self.assertNotEqual(self.wget(1,'DELAY'),30)
        self.assertEqual((self.wget(1,'EX'),self.wget(1,'EY')),pos)
        self.move(1,38,10,1,0)
        for _ in range(30):self.frame()
        self.assertEqual([self.wget(i,'ACTIVE') for i in range(3)],[1,1,1])
    def test_all_forward_reverse_door_cells_and_no_held_bounce(self):
        for room,x,dx,target,entry in [(0,38,1,1,1),(1,1,-1,0,38),(1,38,1,2,1),(2,1,-1,1,38)]:
            for y in (10,11):
                self.init();self.move(room,x,y,dx,0)
                self.assertEqual((self.get('ROOM'),self.get('PX'),self.get('PY')),(target,entry,y))
                for _ in range(8):self.frame(joy=247 if dx>0 else 251)
                self.assertEqual(self.get('ROOM'),target)
    def test_multi_worker_follow_cancellation_and_adjacent_progress(self):
        self.init();self.worker(0,2,10);self.worker(1,5,10,room=0)
        self.move(0,38,11,1,0)
        self.assertEqual([self.wget(i,'FOLLOW_TIMER') for i in (0,1)],[45,45])
        for _ in range(20):self.frame()
        self.move(1,1,11,-1,0)
        self.assertEqual([self.wget(i,'FOLLOW_TIMER') for i in (0,1)],[0,0])
        self.assertEqual([self.wget(i,'EROOM') for i in (0,1)],[0,0])
        self.move(0,38,10,1,0);self.move(1,38,11,1,0)
        for _ in range(self.wget(0,'FOLLOW_TIMER')):self.frame()
        self.assertEqual([self.wget(i,'EROOM') for i in (0,1)],[1,1])
        self.assertNotEqual((self.wget(0,'EX'),self.wget(0,'EY')),(self.wget(1,'EX'),self.wget(1,'EY')))
        self.frame()
        self.assertEqual([self.wget(i,'FOLLOW_TIMER') for i in (0,1)],[45,45])
        for _ in range(45):self.frame()
        self.assertEqual([self.wget(i,'EROOM') for i in (0,1)],[2,2])
    def test_fire_blocks_movement_edge_and_cooldown(self):
        self.init();self.worker(0,10,15);xy=(self.get('PX'),self.get('PY'))
        self.shoot(4)
        self.assertEqual((self.get('PX'),self.get('PY')),xy)
        self.assertEqual(self.get('COOLDOWN'),72);self.assertEqual(self.get('VISUAL'),8)
        self.assertEqual(self.wget(0,'STUN'),60);self.assertEqual(self.wget(0,'EX'),12)
        for _ in range(90):self.frame(joy=247,fire=True)
        self.assertEqual(self.get('COOLDOWN'),0);self.assertEqual(self.get('VISUAL'),0)
        self.assertEqual((self.get('PX'),self.get('PY')),xy)
        self.frame();self.frame(joy=247,fire=True)
        self.assertEqual(self.get('COOLDOWN'),72)
    def test_no_direction_and_cooldown_press_consumed(self):
        self.init();self.frame();self.frame(fire=True)
        self.assertEqual(self.get('COOLDOWN'),0)
        self.frame(joy=247,fire=True);self.assertEqual(self.get('COOLDOWN'),0)
        self.shoot(4);self.assertEqual(self.get('COOLDOWN'),72)
        self.frame();self.frame(joy=247,fire=True)
        for _ in range(80):self.frame(joy=247,fire=True)
        self.assertEqual(self.get('COOLDOWN'),0)
    def test_direction_priority_and_all_four_blasts(self):
        for direction,player,enemy,expected in [(1,(10,15),(10,14),(10,12)),(2,(10,12),(10,13),(10,15)),(3,(10,13),(9,13),(7,13)),(4,(7,13),(8,13),(10,13))]:
            self.init();self.put('PX',player[0]);self.put('PY',player[1]);self.worker(0,*enemy)
            self.shoot(direction);self.assertEqual(self.wget(0,'STUN'),60)
            self.assertEqual((self.wget(0,'EX'),self.wget(0,'EY')),expected)
        self.init();self.frame();self.frame(joy=246,fire=True);self.assertEqual(self.get('AIM_DIR'),1)
    def test_nearest_only_current_room_range_and_wall_occlusion(self):
        self.init();self.worker(0,8,15);self.worker(1,10,15);self.worker(2,8,15,room=1)
        self.shoot(4)
        self.assertEqual(self.wget(0,'STUN'),60);self.assertEqual(self.wget(1,'STUN'),0);self.assertEqual(self.wget(2,'STUN'),0)
        self.init();self.worker(0,11,15);self.shoot(4);self.assertEqual(self.wget(0,'STUN'),0)
        # Dining table at x=20..22,y=14 blocks a worker on x=23.
        self.init();self.put('PX',19);self.put('PY',14);self.worker(0,23,14);self.shoot(4)
        self.assertEqual(self.get('RAY_LEN'),0);self.assertEqual(self.wget(0,'STUN'),0)
    def test_knockback_solid_bounds_door_exit_and_other_worker(self):
        for room,px,py,ex,ey,direction,expected in [(0,36,10,38,10,4,(38,10)),(2,36,10,38,10,4,(38,10)),(0,1,10,0,10,3,(0,10)),(0,10,13,10,12,1,(10,12))]:
            self.init();self.put('ROOM',room);self.put('LOOK_ROOM',room);self.put('PX',px);self.put('PY',py);self.worker(0,ex,ey,room)
            self.shoot(direction);self.assertEqual((self.wget(0,'EX'),self.wget(0,'EY')),expected)
            self.assertEqual(self.wget(0,'EROOM'),room)
        self.init();self.worker(0,8,15);self.worker(1,9,15);self.shoot(4)
        self.assertEqual(self.wget(0,'EX'),8)
    def test_stunned_contact_and_separation_after_expiry(self):
        self.init();self.worker(0,7,15,stun=2)
        self.frame();self.assertEqual(self.get('STATE'),0)
        self.frame();self.assertEqual(self.wget(0,'STUN'),0);self.assertEqual(self.wget(0,'SEPARATE'),1)
        for _ in range(5):self.frame()
        self.assertEqual(self.get('STATE'),0)
        self.frame(joy=247);self.assertEqual(self.get('PX'),8);self.assertEqual(self.get('STATE'),0)
        self.init();self.worker(0,7,15,stun=1)
        for _ in range(8):self.frame()
        self.assertEqual(self.get('STATE'),1)
    def test_entry_grace_only_for_occupied_preferred_tile(self):
        self.init();self.worker(1,1,10,room=1);self.worker(2,4,10,room=1)
        self.move(0,38,10,1,0)
        self.assertNotEqual((self.get('PX'),self.get('PY')),(1,10))
        self.assertEqual(self.wget(1,'ENTRY_GRACE'),15);self.assertEqual(self.wget(2,'ENTRY_GRACE'),0)
        self.assertEqual(self.get('STATE'),0)
        self.put('PX',4);self.put('PY',10);self.call('CHECK_CAUGHT');self.assertEqual(self.get('STATE'),1)
    def test_visual_expires_and_restores_terrain_actors(self):
        self.init();self.worker(0,8,15);self.shoot(4)
        self.assertEqual(self.m[b.SCREEN+15*40+8],17)
        for _ in range(8):self.frame(joy=247,fire=True)
        self.assertEqual(self.get('VISUAL'),0)
        self.assertEqual(self.m[b.SCREEN+15*40+8],1) # floor
        self.assertEqual(self.m[b.SCREEN+15*40+10],16) # stunned worker
        for glyph in (14,15,16,17):self.assertTrue(any(self.parts[b.FONT][glyph*8:glyph*8+8]))
    def test_restart_resets_every_worker_and_transient_state(self):
        self.init();self.worker(0,7,15);self.frame();self.assertEqual(self.get('STATE'),1)
        self.frame(start=True)
        self.assertEqual(self.get('STATE'),0);self.assertEqual(self.get('ROOM'),0)
        self.assertEqual([self.wget(i,'ACTIVE') for i in range(3)],[0,0,0])
        self.assertEqual([self.wget(i,'DELAY') for i in range(3)],[60,30,30])
        for field in ('STUN','FOLLOW_TIMER','SEPARATE','ENTRY_GRACE'):
            self.assertEqual([self.wget(i,field) for i in range(3)],[0,0,0])
        self.assertEqual([self.get(k) for k in ('COOLDOWN','VISUAL','RAY_LEN')],[0,0,0])
    def test_storage_exit_and_frozen_results(self):
        self.init();self.move(2,38,10,1,0)
        self.assertEqual(self.get('STATE'),2);self.assertEqual(bytes(self.m[b.SCREEN+880:b.SCREEN+894]),b'STAGE COMPLETE')
        for _ in range(20):self.frame(joy=251)
        self.assertEqual(self.get('PX'),39)
    def test_vbi_wrap_and_elapsed_stun_follow_cooldown(self):
        self.init();self.worker(0,5,15,stun=20);self.put('COOLDOWN',30);self.put('VISUAL',8);self.put('PREV_FRAME',250);self.m[0x14]=2
        self.call('FRAME');self.assertEqual(self.get('ELAPSED'),8)
        self.assertEqual(self.wget(0,'STUN'),12);self.assertEqual(self.get('COOLDOWN'),22);self.assertEqual(self.get('VISUAL'),0)
        self.worker(0,2,10);self.move(0,38,10,1,0)
        self.frame(delta=44);self.assertEqual(self.wget(0,'EROOM'),0)
        self.frame();self.assertEqual(self.wget(0,'EROOM'),1)
    def test_shared_search_routes_around_obstacles_in_every_room(self):
        for room in range(3):
            self.init();self.put('ROOM',room);self.put('LOOK_ROOM',room);self.put('PX',38);self.put('PY',20);self.worker(0,1,1,room)
            # Keep the other two initial spawns pending for this isolated path test.
            self.put('DELAY_1',255);self.put('DELAY_2',255)
            old=(1,1)
            for f in range(1000):
                # Delay other spawns without altering the tested worker or movement.
                self.put('AWAIT_1',1);self.put('AWAIT_2',1)
                self.frame()
                new=(self.wget(0,'EX'),self.wget(0,'EY'))
                self.assertTrue(self.walkable(*new,room))
                self.assertLessEqual(abs(old[0]-new[0])+abs(old[1]-new[1]),1);old=new
                if self.get('STATE')==1:break
            self.assertEqual(new,(38,20),room)
            self.assertEqual(self.get('STATE'),1,room)
    def test_contact_resolves_before_worker_can_move_away(self):
        self.init();self.worker(0,8,15);self.put('ENEMY_TIMER_0',1);self.put('TICKS',7)
        self.frame(joy=247)
        self.assertEqual(self.get('STATE'),1)
        self.assertEqual((self.wget(0,'EX'),self.wget(0,'EY')),(8,15))
    def test_stun_freezes_follow_and_fire_does_not_extend_separation(self):
        self.init();self.worker(0,2,10,stun=20);self.move(0,38,11,1,0)
        for _ in range(10):self.frame()
        self.assertEqual(self.wget(0,'FOLLOW_TIMER'),0);self.assertEqual(self.wget(0,'EROOM'),0)
        self.init();self.worker(0,7,15,stun=1)
        for _ in range(8):self.frame(fire=True)
        self.assertEqual(self.get('STATE'),1)
    def test_return_cancels_queued_follow_even_while_stunned(self):
        self.init();self.worker(0,2,10);self.move(0,38,11,1,0)
        self.assertEqual(self.wget(0,'FOLLOW_TIMER'),45)
        self.put('STUN_0',20)
        for _ in range(3):self.frame()
        self.move(1,1,11,-1,0)
        self.assertEqual(self.wget(0,'FOLLOW_TIMER'),0)
        self.assertEqual((self.wget(0,'EX'),self.wget(0,'EY')),(2,10))
        self.assertGreater(self.wget(0,'STUN'),0)
    def test_activation_clock_wrap_and_cutscene_fire_release(self):
        self.init();self.put('PREV_FRAME',250);self.m[0x14]=250
        self.frame(delta=20);self.assertEqual(self.wget(0,'DELAY'),40)
        self.frame(delta=40);self.assertEqual(self.wget(0,'ACTIVE'),1)
        self.init()
        for _ in range(10):self.frame(joy=247,fire=True)
        self.assertEqual(self.get('COOLDOWN'),0);self.assertEqual(self.get('PX'),7)
        self.frame();self.frame(joy=247,fire=True);self.assertEqual(self.get('COOLDOWN'),72)
    def test_bounded_pursuit_regular_cadence_and_memory(self):
        self.init();self.put('PX',38);self.put('PY',20)
        for i,(x,y) in enumerate([(5,1),(15,1),(25,1)]):self.worker(i,x,y)
        moves=[[],[],[]];last=[(self.wget(i,'EX'),self.wget(i,'EY')) for i in range(3)]
        guard=[b.SEEN-1,b.SEEN+880,0xB400+880,0xB900+880]
        for addr in guard:self.m[addr]=0xA7
        for f in range(45):
            self.frame()
            for i in range(3):
                now=(self.wget(i,'EX'),self.wget(i,'EY'))
                if now!=last[i]:
                    self.assertEqual(abs(now[0]-last[i][0])+abs(now[1]-last[i][1]),1)
                    self.assertTrue(self.walkable(*now));moves[i].append(f+1);last[i]=now
        self.assertGreaterEqual(min(map(len,moves)),3)
        for i in range(3):self.assertEqual(set(b-a for a,b in zip(moves[i],moves[i][1:])),{self.rules['hazmat']['units'][i]['move_every_frames']})
        self.assertLess(self.max_cycles,26000)
        for addr in guard:self.assertEqual(self.m[addr],0xA7)
        segments=sorted(self.parts.items())
        for (addr,data),(nxt,_) in zip(segments,segments[1:]):self.assertLessEqual(addr+len(data),nxt)
        self.assertLessEqual(0x1000+len(self.parts[0x1000]),0x2000)
        print('\nPROFILE normal-frame max cycles:',self.max_cycles,'worker move frames:',moves)

if __name__=='__main__':unittest.main(verbosity=2)
