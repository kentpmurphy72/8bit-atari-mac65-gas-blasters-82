#!/usr/bin/env python3
"""Execute real v0.5 XEX opcodes with py65. No ANTIC/POKEY/OS emulation."""
import json,tempfile,unittest,hashlib
from fractions import Fraction
from pathlib import Path
from py65.devices.mpu6502 import MPU
import build_stage1_v05 as b
from build_opening_sequence import xex_segments

class BlastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.man=b.build(cls.out);cls.parts=xex_segments(cls.out/cls.man['output']);cls.l=cls.man['labels'];cls.c=cls.man['core_labels'];cls.v=cls.man['movement_labels']
        cls.rules=cls.man['rules'];cls.dirs=[(d['dx'],d['dy']) for d in cls.rules['controls']['aim_directions']]
        cls.meta=json.loads((b.ROOT/'assets/maps/taco_smell_stage1_v02.json').read_text());cls.rows=[(b.ROOT/'assets/maps'/cls.meta['rooms'][r]['map_file']).read_text().splitlines() for r in cls.meta['room_order']]
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):
        self.cpu=MPU();self.mem=self.cpu.memory
        for addr,data in self.parts.items():self.mem[addr:addr+len(data)]=data
        self.mem[0xD010]=1;self.mem[0xD01F]=7;self.mem[0xD300]=255;self.costs=[]
        self.call('INIT')
    def addr(self,k):return self.l[k] if k in self.l else self.v[k] if k in self.v else self.c[k]
    def get(self,k):return self.mem[self.addr(k)]
    def put(self,k,v):self.mem[self.addr(k)]=v
    def call(self,k):
        self.cpu.sp=0xFD;self.mem[0x1FE]=0xFE;self.mem[0x1FF]=0x0F;self.cpu.pc=self.addr(k);start=self.cpu.processorCycles
        for _ in range(300000):
            self.cpu.step()
            if self.cpu.pc==0xFFF:self.costs.append(self.cpu.processorCycles-start);return
        self.fail('timeout '+k)
    def xy(self):return self.get('POS_X')+self.get('POS_XH')*256,self.get('POS_Y')+self.get('POS_YH')*256
    def position(self,x,y,room=0):
        for k,z in [('POS_X',x&255),('POS_XH',x>>8),('POS_Y',y&255),('POS_YH',y>>8),('PX',(x+64)//128),('PY',(y+64)//128),('ROOM',room),('LOOK_ROOM',room),('FULL_DRAW',1)]:self.put(k,z)
        self.call('DRAW')
    def worker(self,i,x,y,room=0,stun=0):
        for k,z in dict(EX=x,EY=y,EROOM=room,ACTIVE=1,STUN=stun,SEPARATE=0,ENTRY_GRACE=0,ENTRY_FRESH=0,ENEMY_TIMER=100,AWAIT=0,FOLLOW_TIMER=0).items():self.put(f'{k}_{i}',z)
    def joy(self,d):
        if d is None:return 255
        dx,dy=self.dirs[d];return 255^(1 if dy<0 else 2 if dy>0 else 0)^(4 if dx<0 else 8 if dx>0 else 0)
    def tick(self,fire=False,d=None,delta=1,full=True):
        self.mem[0x14]=(self.mem[0x14]+delta)&255;self.mem[0xD010]=0 if fire else 1;self.mem[0xD300]=self.joy(d)
        self.call('FRAME' if full else 'INPUT')
    def fire(self,d):
        self.tick()
        for _ in range(4):self.tick(True,d)
    def floor(self,x,y,room=0):
        return 0<=x<40 and 0<=y<22 and self.rows[room][y][x] not in '#BTCRKSDX'
    def reference_cover(self,dx,dy):
        # Independent closed-square/line slab intersection, not the builder's DDA.
        found=[]
        for x in range(min(0,dx),max(0,dx)+1):
            for y in range(min(0,dy),max(0,dy)+1):
                if (x,y)==(0,0):continue
                lo=Fraction(0);hi=Fraction(1)
                for axis,delta in [(x,dx),(y,dy)]:
                    if delta==0:
                        if not 2*axis<=1<=2*axis+2:lo=2;break
                    else:
                        a=Fraction(2*axis-1,2*delta);z=Fraction(2*axis+1,2*delta)
                        lo=max(lo,min(a,z));hi=min(hi,max(a,z))
                if lo<=hi:found.append((x,y))
        return found
    def expected(self,d,origin,room=0):
        dx,dy=self.dirs[d];cells=[]
        for depth,ks in [(1,[0]),(2,[-1,0,1]),(3,[-1,0,1])]:
            for k in ks:
                off=depth*dx-k*dy,depth*dy+k*dx;path=self.reference_cover(*off)
                x,y=origin[0]+off[0],origin[1]+off[1]
                cells.append(((x,y),all(self.floor(origin[0]+sx,origin[1]+sy,room) for sx,sy in path)))
        return cells
    def test_fire_first_eight_aims_four_frame_windup_and_poses(self):
        signatures=[]
        for d in range(8):
            self.call('INIT');self.position(24*128,12*128);self.tick();self.tick(True,None)
            start=self.xy()
            for n in range(3):
                self.tick(True,d);self.assertEqual(self.get('CHARGES'),3)
            rows1=bytes(self.mem[0xBC00+self.get('OLD_Y'):0xBC00+self.get('OLD_Y')+8]);blue=bytes(self.mem[0xBD00+self.get('OLD_Y'):0xBD00+self.get('OLD_Y')+8]);self.assertTrue(any(blue));self.assertTrue(any(b & ~r for b,r in zip(blue,rows1)))
            self.tick(True,d);self.assertEqual(self.get('CHARGES'),2);self.assertEqual(self.get('BURST_AIM'),d);self.assertEqual(self.xy(),start)
            rows2=bytes(self.mem[0xBC00+self.get('OLD_Y'):0xBC00+self.get('OLD_Y')+8]);self.assertNotEqual(rows1,rows2);signatures.append(rows2)
        self.assertEqual(len(set(signatures)),8)
    def test_direction_change_release_cancel_one_burst_and_no_direction(self):
        self.tick();self.tick(True,None);self.tick(True,None);self.assertEqual(self.get('CHARGES'),3)
        for _ in range(3):self.tick(True,0)
        self.tick(True,1);self.assertEqual(self.get('WIND'),1)
        self.tick();self.assertEqual(self.get('CHARGES'),3)
        self.fire(2);self.assertEqual(self.get('CHARGES'),2)
        for _ in range(30):self.tick(True,2)
        self.assertEqual(self.get('CHARGES'),2);self.assertEqual(self.get('COOL'),0)
    def test_recovery_cooldown_and_blocked_hold_does_not_queue(self):
        self.position(24*128,12*128);self.fire(2);p=self.xy()
        for _ in range(7):self.tick(False,2)
        self.assertEqual(self.xy(),p)
        self.tick(False,2);self.assertEqual(self.xy()[0],p[0]+24)
        # A new press during cooldown is permanently consumed until released.
        for _ in range(25):self.tick(True,2)
        self.assertEqual(self.get('CHARGES'),2)
        self.tick();self.fire(2);self.assertEqual(self.get('CHARGES'),1)
    def test_renewable_supply_and_clock_wrap(self):
        self.put('CHARGES',0);self.put('REFILL',120);self.put('CLOCK',250);self.mem[0x14]=250
        self.tick(delta=60);self.assertEqual(self.get('CHARGES'),0)
        self.tick(delta=60);self.assertEqual(self.get('CHARGES'),1)
        self.put('CHARGES',0);self.tick(True,1)
        for _ in range(10):self.tick(True,1)
        self.put('REFILL',1);self.tick(True,1);self.assertEqual(self.get('CHARGES'),1)
        for _ in range(5):self.tick(True,1)
        self.assertEqual(self.get('CHARGES'),1);self.assertEqual(self.get('LIVE'),0)
    def test_geometry_supercover_matches_all_eight_orientations(self):
        for room in range(3):
            for origin in [(24,12),(19,14),(1,10),(38,11)]:
                for d in range(8):
                    self.call('INIT');self.position(origin[0]*128,origin[1]*128,room);self.put('AIM',d);self.call('DISCHARGE')
                    for i,(xy,valid) in enumerate(self.expected(d,origin,room)):
                        self.assertEqual((self.mem[self.addr('CLOUD_X')+i],self.mem[self.addr('CLOUD_Y')+i]),(xy[0]&255,xy[1]&255))
                        self.assertEqual(bool(self.mem[self.addr('VALID')+i]),valid,(room,origin,d,i))
    def test_waves_expansion_restore_and_no_room_leak(self):
        self.position(24*128,12*128);self.fire(2)
        self.assertEqual(self.get('COUNT'),1)
        for _ in range(6):self.tick(True,2)
        self.assertEqual(self.get('COUNT'),4)
        for _ in range(6):self.tick(True,2)
        self.assertEqual(self.get('COUNT'),7)
        for _ in range(6):self.tick(True,2)
        self.assertEqual(self.get('COUNT'),0)
        self.assertNotIn(18,self.mem[b.base.SCREEN:b.base.SCREEN+880]);self.assertNotIn(19,self.mem[b.base.SCREEN:b.base.SCREEN+880])
        self.assertEqual(self.get('LIVE'),0)
    def test_multiple_hits_once_and_animated_three_steps(self):
        self.position(24*128,12*128)
        self.worker(0,25,12);self.worker(1,26,11);self.fire(2)
        self.assertEqual(self.get('STUN_0'),75);self.assertEqual(self.get('EX_0'),25)
        for _ in range(2):self.tick(True,2)
        self.assertEqual(self.get('EX_0'),25)
        self.tick(True,2);self.assertEqual(self.get('EX_0'),26)
        for _ in range(3):self.tick(True,2)
        self.assertEqual(self.get('STUN_1'),75)
        self.assertEqual(self.mem[self.addr('HIT')],1);self.assertEqual(self.mem[self.addr('HIT')+1],1)
        stun=self.get('STUN_0')
        for _ in range(3):self.tick(True,2)
        self.assertEqual(self.get('EX_0'),28);self.assertLess(self.get('STUN_0'),stun)
    def test_diagonal_push_and_corner_bonk(self):
        self.position(24*128,12*128);self.worker(0,25,13);self.fire(3)
        for _ in range(3):self.tick(True,3)
        self.assertEqual((self.get('EX_0'),self.get('EY_0')),(26,14))
        # Wall/counter immediately beyond target must stop without diagonal clipping.
        self.call('INIT');self.position(18*128,13*128);self.worker(0,19,14);self.fire(3)
        for _ in range(3):self.tick(True,3)
        self.assertEqual((self.get('EX_0'),self.get('EY_0')),(19,14));self.assertGreater(self.mem[self.addr('BONK')],0)
    def test_worker_collision_stagger_no_chain_push(self):
        self.position(24*128,12*128);self.worker(0,25,12);self.worker(1,26,12)
        self.fire(2)
        for _ in range(3):self.tick(True,2)
        self.assertEqual(self.get('EX_0'),25);self.assertEqual(self.get('EX_1'),26)
        self.assertGreaterEqual(self.get('STUN_1'),24);self.assertEqual(self.mem[self.addr('PUSH')+1],0)
    def test_hud_sound_restart_and_silent_opening_data(self):
        self.fire(2);self.assertGreater(self.mem[0xD201],0);self.assertEqual(self.mem[b.base.SCREEN+885],ord('2'))
        for _ in range(10):self.tick(True,2)
        self.assertEqual(self.mem[0xD201],0)
        self.put('STATE',1);self.mem[0xD01F]=7;self.call('FRAME');self.mem[0xD01F]=6;self.call('FRAME')
        self.assertEqual(self.get('CHARGES'),3);self.assertEqual(self.get('LIVE'),0);self.assertEqual(self.mem[0xD201],0)
        self.assertEqual([self.get(f'ACTIVE_{i}') for i in range(3)],[0,0,0])
    def test_free_movement_speeds_preserved(self):
        self.position(8*16,8*16)
        for _ in range(10):self.tick(False,2,full=False)
        self.assertEqual(self.xy()[0],128+240)
        self.call('INIT');self.position(8*16,12*128)
        for _ in range(10):self.tick(False,3,full=False)
        self.assertEqual(self.xy(),(128+170,12*128+170))
    def test_each_direction_animated_knockback_and_corner_safety(self):
        for d,(dx,dy) in enumerate(self.dirs):
            self.call('INIT');self.position(24*128,12*128);x,y=24+dx,12+dy;self.worker(0,x,y);self.fire(d)
            self.assertEqual(self.get('STUN_0'),75,d)
            stopped=False
            for step in range(3):
                allowed=not stopped and self.floor(x+dx,y+dy) and self.floor(x+dx,y) and self.floor(x,y+dy)
                for _ in range(3):self.tick(True,d)
                if allowed:x+=dx;y+=dy
                else:stopped=True
                self.assertEqual((self.get('EX_0'),self.get('EY_0')),(x,y),(d,step))
            self.assertEqual(self.get('EROOM_0'),0)
    def test_four_links_fractional_entries_charge_continuity_and_exit(self):
        for room,right,target,entry in [(0,True,1,1),(1,False,0,38),(1,True,2,1),(2,False,1,38)]:
            for y in (10,11):
                self.call('INIT');self.put('CHARGES',2);self.position((307 if right else 5)*16,y*128+3,room)
                self.tick(False,2 if right else 6)
                self.assertEqual((self.get('ROOM'),self.get('PX'),self.get('PY')),(target,entry,y))
                self.assertEqual(self.xy(),(entry*128,y*128));self.assertEqual(self.get('CHARGES'),2)
        self.position(307*16,10*128,2);self.tick(False,2);self.assertEqual(self.get('STATE'),2)
    def test_restart_clears_active_cloud_and_result_silences_sfx(self):
        self.position(24*128,12*128);self.fire(2);self.assertGreater(self.get('LIVE'),0)
        self.call('INIT');self.assertEqual(self.get('LIVE'),0)
        self.assertNotIn(18,self.mem[b.base.SCREEN:b.base.SCREEN+880]);self.assertNotIn(19,self.mem[b.base.SCREEN:b.base.SCREEN+880])
        self.tick();self.fire(2);self.put('STATE',1);self.call('DRAW');self.assertEqual(self.mem[0xD201],0)
    def test_diagonal_side_worker_blocks_without_chain_push(self):
        self.position(24*128,12*128);self.worker(0,25,13);self.worker(1,26,13);self.fire(3)
        for _ in range(3):self.tick(True,3)
        self.assertEqual((self.get('EX_0'),self.get('EY_0')),(25,13))
        self.assertEqual((self.get('EX_1'),self.get('EY_1')),(26,13))
        self.assertGreaterEqual(self.get('STUN_1'),24);self.assertEqual(self.mem[self.addr('PUSH')+1],0)
    def test_stagger_does_not_shorten_longer_stun(self):
        self.position(24*128,12*128);self.worker(0,25,12);self.worker(1,26,12,stun=120)
        self.fire(2)
        for _ in range(3):self.tick(True,2)
        self.assertGreater(self.get('STUN_1'),100)
    def test_opening_original_controls_and_song_continuity(self):
        self.mem[:]=[0]*65536
        for addr,data in self.parts.items():self.mem[addr:addr+len(data)]=data
        self.mem[0xD01F]=7;self.mem[0xD010]=1;self.mem[0xD300]=255
        labels=self.man['opening_labels'];wait=labels['FRAME_WAIT'];self.cpu.pc=0x2000
        def until():
            for _ in range(200000):
                if self.cpu.pc==wait:return
                self.cpu.step()
            self.fail('opening loop timeout')
        def frame(start=False,fire=False):
            self.mem[0xD01F]=6 if start else 7;self.mem[0xD010]=0 if fire else 1;self.mem[0x14]=(self.mem[0x14]+1)&255;self.cpu.step();until()
        until();self.assertEqual(self.mem[0xD400],0x22)
        frame();frame(True);self.assertEqual(self.mem[labels['SCENE']],1)
        frame();idx=self.mem[labels['NOTE_INDEX']];frame(fire=True)
        self.assertEqual(self.mem[labels['SCENE']],2);self.assertIn(self.mem[labels['NOTE_INDEX']],(idx,(idx+1)%128));self.assertEqual(self.mem[0xD400],0x22)
        frame();frame(fire=True);self.assertEqual(self.mem[labels['SCENE']],3)
        self.assertEqual(self.get('CHARGES'),3);self.assertEqual(self.mem[0xD400],0x3A)
    def test_memory_segments_old_assets_and_deterministic_build(self):
        old=xex_segments(b.ROOT/'assets/stage1_v04/GasBlasters82_Stage1_Playable_v04.xex')
        for addr,data in old.items():
            if addr not in (0x400,0x1000,0x2800,b.base.FONT):self.assertEqual(self.parts[addr],data)
        items=sorted(self.parts.items())
        for (addr,data),(nxt,_) in zip(items,items[1:]):self.assertLessEqual(addr+len(data),nxt)
        self.assertLess(max(addr+len(data) for addr,data in items),0xC001)
        before=(self.out/self.man['output']).read_bytes();b.build(self.out);self.assertEqual(before,(self.out/self.man['output']).read_bytes())

if __name__=='__main__':unittest.main(verbosity=2)
