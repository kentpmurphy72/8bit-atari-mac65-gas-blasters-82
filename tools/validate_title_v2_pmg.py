#!/usr/bin/env python3
"""6502 control-flow, P/M DMA-register and immutable bitmap checks for title v2.
Does NOT reproduce actual Atari800's ANTIC/GTIA screen or sound: user emulator test required.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util,sys,hashlib,struct,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_title_v2_pmg as title
import build_opening_sequence as original
from validate_opening_sequence import CPU

def check(repo,out):
 manifest=title.build(repo,out)
 rom=original.xex_segments(out/manifest['file'])
 assert rom[0x02E0]==b'\x00\x20'
 assert rom[0xA000] and len(rom[0xA000])==2048
 assert len(rom[0x3600])==len(rom[0x3630])==44
 assert len(rom[0x2400])<0x400
 assert len(rom)==26
 assert hashlib.sha256((out/manifest['file']).read_bytes()).hexdigest()==manifest['sha256']
 source_title=original.xex_segments(repo/'assets/title/Title_Option3_Original.xex')
 assert rom[0x4000]==source_title[0x4000]
 assert rom[0x5000]==source_title[0x5000]
 assert rom[0x5A00]==source_title[0x6000]
 # Original songs and cutscene art still identical to the v1 build.
 for a in (0x2A00,0x3000,0x3500,0x3530,0x3560,0x3800,0x3C00,0x3D00,0x3E00,0x3F00,0x6000,0x7000,0x7600,0x8000,0x9000,0x9600,0x9800):
  previous=original.xex_segments(out/'_v1_repro'/'GasBlasters82_OpeningSequence_v1.xex')
  assert rom[a]==previous[a],hex(a)
 for p in range(4):
  assert any(rom[0xA000][0x400+p*256:0x500+p*256])
 assert any(rom[0xA000][0x300:0x400])
 # Confirm that no user-modded code is needed for original screen sequence.
 originals={kind:original.xex_segments(repo/f'assets/{folder}/{name}')[0x2000] for kind,folder,name in (
  ('title','title','Title_Option3_Original.xex'),('crew','intro','meet_the_crew_v4.xex'),('arrival','arrival','arrival_v3.xex'))}
 palettes={k:original.palette_data(originals[k],b'')[0] for k in originals}
 asm,code=original.assemble_controller(palettes)
 L=asm.labels
 sim=CPU(rom,0x2000)
 sim.run_until(L['FRAME_WAIT'])
 assert sim.mem[0xD407]==0xA0
 assert sim.mem[0xD400]==0x2E and sim.mem[0x22F]==0x2E
 assert sim.mem[0xD01D]==3 and sim.mem[0x26F]==0
 assert [sim.mem[0xD000+p] for p in range(4)]==[48+title.BANDS[0][p][0] for p in range(4)]
 assert [sim.mem[0xD012+p] for p in range(4)]==[title.BANDS[0][p][1] for p in range(4)]
 assert sim.mem[0x230]|sim.mem[0x231]<<8==0x3C00
 assert sim.mem[0xD40E]==0xC0
 def frame(console=False,fire=False):
  sim.mem[0xD01F]=0x06 if console else 0x07
  sim.mem[0xD010]=0x00 if fire else 0x01
  sim.mem[0x14]=(sim.mem[0x14]+1)&255
  sim.step();sim.run_until(L['FRAME_WAIT'])
 def simulate_dli(mode,source):
  pc=sim.pc
  for i in range(11):
   sim.push(pc>>8);sim.push(pc&255);sim.push(0)
   sim.pc=L['DLI_HANDLER'];sim.run_until(pc)
   for j,reg in enumerate((0xD01A,0xD016,0xD017,0xD018)):
    assert sim.mem[reg]==sim.mem[source+j*11+i],f'palette band {i}'
   if mode=='title':
    for p in range(4):
     assert sim.mem[0xD000+p]==rom[0x3600][p*11+i],(i,p,'HPOS')
     assert sim.mem[0xD012+p]==rom[0x3630][p*11+i],(i,p,'COLPM')
  assert sim.mem[L['DLI_POS']]==0
 simulate_dli('title',0x3500)
 assert [sim.mem[0xD000+p] for p in range(4)]==[48+title.BANDS[0][p][0] for p in range(4)],'frame-wrapped sprite positions'
 for _ in range(30):frame()
 assert sim.mem[L['NOTE_INDEX']]>1
 frame(console=True)
 assert sim.mem[L['SCENE']]==1
 assert sim.mem[0xD01D]==0 and sim.mem[0xD400]==0x22 and sim.mem[0x22F]==0x22
 assert sim.mem[0x230]|sim.mem[0x231]<<8==0x3D00
 simulate_dli('crew',0x3530)
 for _ in range(8):frame(console=True)
 assert sim.mem[L['SCENE']]==1
 for _ in range(10):frame()
 idx=sim.mem[L['NOTE_INDEX']]
 frame(fire=True)
 assert sim.mem[L['SCENE']]==2 and sim.mem[0xD01D]==0
 assert sim.mem[L['NOTE_INDEX']] in (idx, (idx+1)%128),'Funk restart on cutscene'
 simulate_dli('arrival',0x3560)
 for _ in range(5):frame()
 frame(fire=True)
 assert sim.mem[L['SCENE']]==3 and sim.mem[L['TRACK']]==2
 for _ in range(5):frame()
 frame(console=True)
 assert sim.mem[L['SCENE']]==0 and sim.mem[L['TRACK']]==0
 assert sim.mem[0xD407]==0xA0 and sim.mem[0xD01D]==3 and sim.mem[0xD400]==0x2E
 simulate_dli('title',0x3500)
 print('PASS: 26 XEX segments, original artwork and 6502 scene controller intact')
 print('PASS: 4 one-line players + 4 missiles at $A000; 11 title DLI bands + frame reset')
 print('PASS: START/FIRE/FIRE/START, music continuity, PMG on title only, replay')
 print('PASS: '+str(sim.steps)+' instructions simulated; not an actual Atari800 test')
 return True

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parent.parent);ap.add_argument('--output',type=Path,default=None);args=ap.parse_args()
 check(args.repo,args.output or args.repo/'assets/title_v2')
