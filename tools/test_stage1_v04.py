#!/usr/bin/env python3
"""Execute v0.4 XEX movement/PMG code using py65; not Atari800 validation."""
import json,tempfile,unittest,hashlib
from pathlib import Path
from py65.devices.mpu6502 import MPU
import build_stage1_v04 as b
from build_opening_sequence import xex_segments

class MovementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.man=b.build(cls.out);cls.parts=xex_segments(cls.out/cls.man['output']);cls.l=cls.man['labels'];cls.core=cls.man['core_labels'];cls.opening=cls.man['opening_labels']
        cls.meta=json.loads((b.ROOT/'assets/maps/taco_smell_stage1_v02.json').read_text())
        cls.rows=[(b.ROOT/'assets/maps'/cls.meta['rooms'][r]['map_file']).read_text().splitlines() for r in cls.meta['room_order']]
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):
        self.cpu=MPU();self.mem=self.cpu.memory
        for addr,data in self.parts.items():self.mem[addr:addr+len(data)]=data
        self.mem[0xD010]=1;self.mem[0xD01F]=7;self.mem[0xD300]=255;self.cycles=[]
        self.call('NEW_INIT')
    def addr(self,k):return self.l[k] if k in self.l else self.core[k]
    def get(self,k):return self.mem[self.addr(k)]
    def put(self,k,v):self.mem[self.addr(k)]=v
    def call(self,k):
        self.cpu.sp=0xFD;self.mem[0x1FE]=0xFE;self.mem[0x1FF]=0x0F;self.cpu.pc=self.addr(k);before=self.cpu.processorCycles
        for _ in range(300000):
            self.cpu.step()
            if self.cpu.pc==0xFFF:self.cycles.append(self.cpu.processorCycles-before);return
        self.fail('routine timeout: '+k)
    def xy(self):return self.get('POS_X')+256*self.get('POS_XH'),self.get('POS_Y')+256*self.get('POS_YH')
    def position(self,x,y,room=0):
        for k,v in [('POS_X',x&255),('POS_XH',x>>8),('POS_Y',y&255),('POS_YH',y>>8),('ROOM',room),('LOOK_ROOM',room),('PX',(x+64)//128),('PY',(y+64)//128),('FULL_DRAW',1)]:self.put(k,v)
        self.call('DRAW')
    def tick(self,joy=255,delta=1,fire=False,full=False):
        self.mem[0x14]=(self.mem[0x14]+delta)&255;self.mem[0xD300]=joy;self.mem[0xD010]=0 if fire else 1
        self.call('FRAME' if full else 'MOVE')
    def worker(self,i,x,y,room=0,stun=0,grace=0):
        for k,v in dict(EX=x,EY=y,EROOM=room,ACTIVE=1,STUN=stun,SEPARATE=0,ENTRY_GRACE=grace,ENTRY_FRESH=0,ENEMY_TIMER=10,AWAIT=0,FOLLOW_TIMER=0).items():self.put(f'{k}_{i}',v)
    def test_cardinal_speed_60_frames_reverse_stop(self):
        self.position(8*16,8*16)
        for _ in range(60):self.tick(247)
        self.assertEqual(self.xy(),(98*16,8*16))
        self.tick(251);self.assertEqual(self.xy()[0],98*16-24)
        self.tick();self.assertEqual(self.xy()[0],98*16-24)
    def test_diagonal_speed_and_opposed_axes(self):
        self.position(8*16,12*8*16)
        for _ in range(10):self.tick(245) # down-right
        self.assertEqual(self.xy(),(8*16+170,12*8*16+170))
        before=self.xy();self.tick(240);self.assertEqual(self.xy(),before)
    def test_video_clock_no_duplicate_and_bounded_catchup_wrap(self):
        self.position(8*16,8*16);self.tick(247,delta=0);self.assertEqual(self.xy()[0],128)
        self.tick(247,delta=10);self.assertEqual(self.xy()[0],176)
        self.put('MOTION_CLOCK',255);self.mem[0x14]=255;self.tick(247);self.assertEqual(self.xy()[0],200)
    def test_fire_inert_does_not_lock_walk(self):
        self.position(8*16,8*16)
        for _ in range(10):self.tick(247,fire=True,full=True)
        self.assertEqual(self.xy()[0],128+240)
        self.assertEqual([self.get(k) for k in ('COOLDOWN','VISUAL','RAY_LEN')],[0,0,0])
    def test_visible_pmg_moves_inside_tile_and_clears_old_lines(self):
        self.position(8*16,8*16);self.call('PMG_DRAW');h=self.mem[0xD000]
        self.tick(247);self.tick(247);self.assertNotEqual(self.mem[0xD000],h)
        self.assertEqual(self.get('PX'),1) # still inside same tile center
        old=self.get('OLD_Y');self.tick(253);self.tick(253)
        self.assertNotEqual(self.get('OLD_Y'),old);self.assertEqual(self.mem[0xBC00+old],0)
        self.assertTrue(any(self.mem[0xBC00+self.get('OLD_Y'):0xBC00+self.get('OLD_Y')+8]))
        self.assertEqual((self.mem[0xD407],self.mem[0xD400],self.mem[0xD01D]),(0xB8,0x3A,2))
        self.assertNotEqual(self.mem[b.SCREEN+1*40+1],14)
    def safe(self,x,y,room):
        if not(0<=x<=312*16 and 0<=y<=168*16):return False
        for tx in ((x+16)//128,(x+111)//128):
            for ty in ((y+16)//128,(y+111)//128):
                if self.meta['terrain'][self.rows[room][ty][tx]]['solid']:return False
        return True
    def test_aabb_matches_independent_fractional_oracle(self):
        # Sample every solid type and all room boundaries, including fractional edges.
        for room in range(3):
            for y in range(22):
                for x in range(40):
                    for offset in (0,17,111):
                        fx=x*128+offset;fy=y*128
                        self.put('ROOM',room)
                        for k,v in [('POS_X',fx&255),('POS_XH',fx>>8),('POS_Y',fy&255),('POS_YH',fy>>8)]:self.put(k,v)
                        self.call('BOX_OK');self.assertEqual(bool(self.cpu.a),self.safe(fx,fy,room),(room,x,y,offset))
    def test_wall_slide_cardinal_free_axis_and_exact_stop(self):
        # Right side of dining table x=10..12,y=4..5; x=73 is last safe left side.
        self.position(73*16,4*8*16)
        self.tick(246) # up-right, X blocked, slide up at cardinal speed
        self.assertEqual(self.xy(),(73*16,4*8*16-24))
        self.assertTrue(self.safe(*self.xy(),0))
        # Y blocked below table y=5 while X is free: use full cardinal X speed.
        self.position(11*8*16,47*16)
        self.tick(246)
        self.assertEqual(self.xy(),(11*8*16+24,47*16))
    def test_diagonal_corners_and_no_tunneling_after_stall(self):
        self.position(73*16,5*8*16)
        for _ in range(20):
            self.tick(245,delta=100);self.assertTrue(self.safe(*self.xy(),0))
        self.position(8*16,8*16)
        for _ in range(20):self.tick(254,delta=100)
        self.assertGreaterEqual(self.xy()[1],7*16)
        self.position(0,10*8*16)
        for _ in range(5):self.tick(251)
        self.assertEqual(self.xy()[0],0)
        self.position(8*16,168*16)
        for _ in range(5):self.tick(253)
        self.assertLessEqual(self.xy()[1],168*16)
    def test_all_doors_center_threshold_alignment_and_held_no_bounce(self):
        for room,right,target,entry in [(0,True,1,1),(1,False,0,38),(1,True,2,1),(2,False,1,38)]:
            for y in (10,11):
                self.call('NEW_INIT');x=(307*16 if right else 5*16)
                self.position(x,y*128+3,room)
                self.tick(247 if right else 251)
                self.assertEqual((self.get('ROOM'),self.get('PX'),self.get('PY')),(target,entry,y))
                self.assertEqual(self.xy(),(entry*128,y*128))
                self.tick(247 if right else 251)
                self.assertEqual(self.get('ROOM'),target)
    def test_center_graze_is_not_door_transition_and_exit(self):
        self.position(306*16,10*128)
        self.tick(247);self.assertEqual(self.get('ROOM'),0) # sprite corner already touches D
        self.tick(247);self.assertEqual(self.get('ROOM'),1)
        self.position(307*16,10*128,2);self.tick(247);self.assertEqual(self.get('STATE'),2)
    def test_pixel_contact_half_open_and_stun_grace(self):
        self.worker(0,10,12)
        self.position((80-6)*16,96*16);self.call('CONTACT');self.assertEqual(self.get('STATE'),0)
        self.position((80-6)*16+1,96*16);self.call('CONTACT');self.assertEqual(self.get('STATE'),1)
        self.put('STATE',0);self.put('STUN_0',20);self.call('CONTACT');self.assertEqual(self.get('STATE'),0)
        self.put('STUN_0',0);self.put('ENTRY_GRACE_0',15);self.call('CONTACT');self.assertEqual(self.get('STATE'),0)
        self.put('ENTRY_GRACE_0',0);self.position((80+6)*16,96*16);self.call('CONTACT');self.assertEqual(self.get('STATE'),0)
    def test_restart_alignment_workers_and_frozen_result(self):
        self.position(1001,1701);self.put('STATE',1);before=self.xy();self.tick(247,full=True);self.assertEqual(self.xy(),before)
        self.mem[0xD01F]=7;self.call('FRAME');self.mem[0xD01F]=6;self.call('FRAME')
        self.assertEqual(self.xy(),(7*128,15*128));self.assertEqual([self.get(f'ACTIVE_{i}') for i in range(3)],[0,0,0])
    def test_live_workers_pursuit_timing_and_input_during_search(self):
        self.position(30*128,18*128)
        for i,(x,y) in enumerate([(5,1),(15,1),(25,1)]):self.worker(i,x,y)
        before=[(self.get(f'EX_{i}'),self.get(f'EY_{i}')) for i in range(3)]
        costs=[]
        for f in range(32):
            self.tick(247 if f<8 else 251 if f<16 else 255,full=True);costs.append(self.cycles[-1])
            self.assertEqual(self.get('STATE'),0)
        self.assertNotEqual(before,[(self.get(f'EX_{i}'),self.get(f'EY_{i}')) for i in range(3)])
        self.assertEqual([self.get(f'ACTIVE_{i}') for i in range(3)],[1,1,1])
        self.assertEqual(self.xy()[0],30*128)
        self.assertLess(max(costs[1:]),50000)
    def test_opening_flow_pmg_off_until_stage_and_music(self):
        # Fresh XEX memory, rather than setUp's already-initialized Stage 1.
        self.mem[:]=[0]*65536
        for addr,data in self.parts.items():self.mem[addr:addr+len(data)]=data
        self.mem[0xD01F]=7;self.mem[0xD010]=1;self.mem[0xD300]=255
        self.cpu.pc=0x2000;wait=self.opening['FRAME_WAIT']
        def until():
            for _ in range(200000):
                if self.cpu.pc==wait:return
                self.cpu.step()
            self.fail('opening loop timeout')
        def frame(start=False,fire=False):
            self.mem[0xD01F]=6 if start else 7;self.mem[0xD010]=0 if fire else 1;self.mem[0x14]=(self.mem[0x14]+1)&255
            self.cpu.step();until()
        until();self.assertEqual(self.mem[0xD400],0x22)
        frame();frame(start=True);self.assertEqual(self.mem[self.opening['SCENE']],1)
        self.assertEqual(self.mem[self.opening['TRACK']],1)
        frame();idx=self.mem[self.opening['NOTE_INDEX']];frame(fire=True)
        self.assertEqual(self.mem[self.opening['SCENE']],2)
        self.assertIn(self.mem[self.opening['NOTE_INDEX']],(idx,(idx+1)%128))
        self.assertEqual(self.mem[0xD400],0x22)
        frame();frame(fire=True);self.assertEqual(self.mem[self.opening['SCENE']],3)
        self.assertEqual(self.mem[self.opening['TRACK']],2)
        self.assertEqual(self.mem[0xD400],0x3A);self.assertEqual(self.xy(),(7*128,15*128))
        self.assertEqual(self.mem[0xD40E],0x40)
    def test_memory_preservation_and_reproducibility(self):
        old=xex_segments(b.ROOT/'assets/stage1_v03/GasBlasters82_Stage1_Playable_v03.xex')
        for addr,data in old.items():
            if addr not in (0x1000,0x2800):self.assertEqual(data,self.parts[addr])
        original=(self.out/self.man['output']).read_bytes();b.build(self.out);self.assertEqual(original,(self.out/self.man['output']).read_bytes())
        items=sorted(self.parts.items())
        for (addr,data),(nxt,_) in zip(items,items[1:]):self.assertLessEqual(addr+len(data),nxt)
        self.assertLessEqual(0x400+len(self.parts[0x400]),0x1000)
        self.assertEqual(len(self.parts[0xB800]),2048)
        # Queue relocation is real machine code, avoiding the PMG block.
        for zp in (0x86,0x8A):self.assertIn(bytes([0xA9,0,0x85,zp,0xA9,0x9C,0x85,zp+1]),self.parts[0x1000])

if __name__=='__main__':unittest.main(verbosity=2)
