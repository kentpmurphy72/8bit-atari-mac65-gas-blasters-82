#!/usr/bin/env python3
"""Structural and basic 6502 flow tests for the integrated title/crew/arrival XEX.

This is an independent lightweight test harness, NOT a full Atari emulator.
It exercises the 6502 instructions used by the controller, screen pointers,
POKEY register writes, and release-before-next-press debounce. An Atari800
emulator visual/audio test by the user remains mandatory.
"""
import argparse, importlib.util, struct
from pathlib import Path

class CPU:
    def __init__(self,rom,entry):
        self.mem=bytearray(65536)
        self.mem[0xD01F]=0x07 # all console switches released
        self.mem[0xD010]=0x01 # joystick 1 FIRE released
        self.mem[0x14]=0
        for start,data in rom.items():self.mem[start:start+len(data)]=data
        self.pc=entry;self.a=self.x=self.y=0;self.sp=0xFF
        self.c=self.z=self.n=0
        self.writes=[];self.steps=0
    def rd(self,addr):return self.mem[addr&65535]
    def wr(self,addr,v):
        self.mem[addr&65535]=v&255
        if 0xD200<=addr<=0xD20F:self.writes.append((addr,v&255))
    def fetch(self):v=self.rd(self.pc);self.pc=(self.pc+1)&65535;return v
    def abs(self):return self.fetch()|self.fetch()<<8
    def flags(self,v):self.z=int((v&255)==0);self.n=(v>>7)&1;return v&255
    def push(self,v):self.wr(0x100+self.sp,v);self.sp=(self.sp-1)&255
    def pop(self):self.sp=(self.sp+1)&255;return self.rd(0x100+self.sp)
    def step(self):
        pc=self.pc;op=self.fetch();self.steps+=1
        if op==0x78 or op==0x58:pass # SEI, CLI
        elif op==0xA9:self.a=self.flags(self.fetch())
        elif op==0xAD:self.a=self.flags(self.rd(self.abs()))
        elif op==0xA5:self.a=self.flags(self.rd(self.fetch()))
        elif op==0xBD:self.a=self.flags(self.rd(self.abs()+self.x))
        elif op==0xAE:self.x=self.flags(self.rd(self.abs()))
        elif op==0xA2:self.x=self.flags(self.fetch())
        elif op==0x8D:self.wr(self.abs(),self.a)
        elif op==0x8E:self.wr(self.abs(),self.x)
        elif op==0x29:self.a=self.flags(self.a & self.fetch())
        elif op==0xC9:
            v=self.fetch();self.c=int(self.a>=v);self.flags((self.a-v)&255)
        elif op==0xCD:
            v=self.rd(self.abs());self.c=int(self.a>=v);self.flags((self.a-v)&255)
        elif op==0xE0:
            v=self.fetch();self.c=int(self.x>=v);self.flags((self.x-v)&255)
        elif op in (0xF0,0xD0,0x90,0xB0):
            d=self.fetch();d=d if d<128 else d-256
            cond={0xF0:self.z==1,0xD0:self.z==0,0x90:self.c==0,0xB0:self.c==1}[op]
            if cond:self.pc=(self.pc+d)&65535
        elif op==0x20:
            target=self.abs();ret=(self.pc-1)&65535
            self.push(ret>>8);self.push(ret&255);self.pc=target
        elif op==0x60:self.pc=(self.pop()|(self.pop()<<8))+1;self.pc&=65535
        elif op==0x4C:self.pc=self.abs()
        elif op==0x18:self.c=0
        elif op==0x6D:
            v=self.rd(self.abs());tot=self.a+v+self.c;self.c=int(tot>255);self.a=self.flags(tot&255)
        elif op==0x69:
            v=self.fetch();tot=self.a+v+self.c;self.c=int(tot>255);self.a=self.flags(tot&255)
        elif op==0xE8:self.x=self.flags((self.x+1)&255)
        elif op==0x48:self.push(self.a)
        elif op==0x8A:self.a=self.flags(self.x)
        elif op==0x98:self.a=self.flags(self.y)
        elif op==0x68:self.a=self.flags(self.pop())
        elif op==0xA8:self.y=self.flags(self.a)
        elif op==0xAA:self.x=self.flags(self.a)
        elif op==0x40:
            _status=self.pop() # mock RTI restores PC; flags are not used afterward
            self.pc=self.pop()|(self.pop()<<8)
        else:raise AssertionError(f'unknown opcode ${op:02X} at ${pc:04X}')
    def run_until(self,addr,max_steps=10000):
        for _ in range(max_steps):
            if self.pc==addr:return
            self.step()
        raise AssertionError(f'CPU stuck (PC ${self.pc:04X}), wanted ${addr:04X}')


def run_test(repo,output):
    path=repo/'tools/build_opening_sequence.py'
    spec=importlib.util.spec_from_file_location('opening',path)
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    metadata=builder.build(repo,output)
    xex=output/metadata['output']
    data=xex.read_bytes();rom=builder.xex_segments(xex)
    assert 0x02E0 in rom and rom[0x02E0]==b'\x00\x20'
    assert max(start+len(blob) for start,blob in rom.items())<=0x9C00
    assert len(rom)==22
    # Confirm exact original artwork and script data in relocated memory.
    for source_name,src_start,dst_start in [
        ('title',0x4000,0x4000),('title',0x5000,0x5000),
        ('crew',0x4000,0x6000),('crew',0x5000,0x7000),
        ('arrival',0x4000,0x8000),('arrival',0x5000,0x9000)]:
        path={'title':repo/'assets/title/Title_Option3_Original.xex',
              'crew':repo/'assets/intro/meet_the_crew_v4.xex',
              'arrival':repo/'assets/arrival/arrival_v3.xex'}[source_name]
        src=builder.xex_segments(path)
        assert rom[dst_start]==src[src_start],(source_name,dst_start)
    for dl,art1,art2,txt in [(0x3C00,0x4000,0x5000,0x5A00),(0x3D00,0x6000,0x7000,0x7600),(0x3E00,0x8000,0x9000,0x9600)]:
        d=rom[dl]
        assert d.count(b'\x4e')==2,(dl,d.count(b'\x4e'))
        for addr in (art1,art2,txt,dl):assert struct.pack('<H',addr) in d,(hex(dl),hex(addr))
        assert d.count(b'\x8e')+d.count(b'\x82')>=10
        assert d[-3:]==bytes([0x41,dl&255,dl>>8])
    assert rom[0x3F00].endswith(b'\x41\x00\x3F')
    assert len(rom[0x9800])==960
    assert rom[0x2A00][0]==0x48 and rom[0x2A00][192]==0xAB
    assert rom[0x3000][0]==(repo/'assets/music/funk_pokey_registers.bin').read_bytes()[0]
    asm,code=builder.assemble_controller({k:builder.palette_data(builder.xex_segments(v)[0x2000],b'')[0]
                          for k,v in {'title':repo/'assets/title/Title_Option3_Original.xex',
                                      'crew':repo/'assets/intro/meet_the_crew_v4.xex',
                                      'arrival':repo/'assets/arrival/arrival_v3.xex'}.items()})
    label=asm.labels
    c=CPU(rom,0x2000)
    wait=label['FRAME_WAIT'];c.run_until(wait)
    def frame(console=False,fire=False):
        c.mem[0xD01F]=0x06 if console else 0x07
        c.mem[0xD010]=0x00 if fire else 0x01
        c.mem[0x14]=(c.mem[0x14]+1)&255
        c.step();c.run_until(wait)
    def scene(n,dl,track):
        assert c.mem[label['SCENE']]==n,(n,c.mem[label['SCENE']])
        assert c.mem[0x230]|c.mem[0x231]<<8==dl
        assert c.mem[label['TRACK']]==track
        assert c.mem[0xD40E]==0xC0
        assert c.mem[0x200]|c.mem[0x201]<<8==label['DLI_HANDLER']
    scene(0,0x3C00,0)
    def dli_test(source):
        # Simulate an NMI on each of the 11 DLI-marked scanline boundaries.
        # NMI pushes PC high, PC low and status; RTI reverses the pushes.
        saved_pc=c.pc
        for pos in range(11):
            c.push(saved_pc>>8);c.push(saved_pc&255);c.push(0)
            c.pc=label['DLI_HANDLER']
            c.run_until(saved_pc)
            assert c.mem[0xD01A]==c.mem[source+pos]
            assert c.mem[0xD016]==c.mem[source+11+pos]
            assert c.mem[0xD017]==c.mem[source+22+pos]
            assert c.mem[0xD018]==c.mem[source+33+pos]
        assert c.mem[label['DLI_POS']]==0 # wraps at the 12th color band
    dli_test(0x3500)
    assert c.mem[label['INC_LO']]==0x19 and c.mem[label['INC_HI']]==0x2A
    for i in range(30):frame()
    assert c.mem[label['NOTE_INDEX']]>2 and len(c.writes)>35
    frame(console=True);scene(1,0x3D00,1)
    dli_test(0x3530)
    assert c.mem[label['INC_LO']]==0x49 and c.mem[label['INC_HI']]==0x1F
    assert c.mem[label['NOTE_INDEX']]==1
    for i in range(12):frame(console=True) # held START mustn't advance
    scene(1,0x3D00,1)
    for i in range(45):frame()
    idx=c.mem[label['NOTE_INDEX']]
    frame(fire=True);scene(2,0x3E00,1)
    dli_test(0x3560)
    assert c.mem[label['NOTE_INDEX']] in (idx, (idx+1)%128), 'Funk theme unexpectedly restarted'
    for i in range(10):frame(fire=True)
    scene(2,0x3E00,1)
    for i in range(20):frame()
    frame(fire=True);scene(3,0x3F00,2)
    assert all(c.mem[addr]==0 for addr in [0xD201,0xD203,0xD205,0xD207]),'Stage1 not silent'
    for i in range(15):frame(fire=True)
    scene(3,0x3F00,2)
    for i in range(4):frame()
    frame(console=True);scene(0,0x3C00,0)
    assert c.mem[label['NOTE_INDEX']]==1
    # Ensure no accidental table overflow on song loop; 12 bars + 8 bars.
    for i in range(60*23):frame()
    scene(0,0x3C00,0)
    # 11 different DLI bands with one handler and correct palette source per scene.
    assert len(rom[0x3500])==44 and len(rom[0x3530])==44 and len(rom[0x3560])==44
    assert c.steps>25000
    return {'xex_bytes':len(data),'sha256':metadata['sha256'],'segments':len(rom),
            'cpu_instructions_simulated':c.steps,
            'scene_transitions_tested':'START->FIRE->FIRE->START replay',
            'music':'tempo switching, register writes and continuity checked',
            'screen':'3 relocated original ANTIC displays and Stage1 placeholder checked',
            'warning':'Not a real POKEY/ANTIC emulator test'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parent.parent)
    p.add_argument('--output',type=Path,default=None)
    args=p.parse_args();print(run_test(args.repo,args.output or args.repo/'assets/opening'))
