#!/usr/bin/env python3
"""Gas Blasters '82 title v2: POKEY + player/missile detail on ORIGINAL ANTIC bitmap.

Builds an ALTERNATE complete opening-sequence XEX without altering v1. Four 1-line
GTIA players and four missiles provide hand-aligned highlight pixels on the title ONLY.
DLI reuses player X/color in 16-line strips; crew, arrival, and Stage 1 stay untouched.
The 160x160 bitmap, palettes, music tables, screen texts and stage flow remain byte-identical.

Requires Python 3 and Pillow (for the optional visual comparison preview). `build_opening_sequence.py` next to this script
and four existing Atari XEX/data assets in the repository.

PMBASE=$A000 with single-line DMA ($2E); player data at $A400/$A500/$A600/$A700,
missile bits at $A300. Atari800 -xl -nobasic is the tested CONFIGURATION, but this
particular program still needs an emulator image-and-sound playtest.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_opening_sequence as v1

REPO=Path(__file__).resolve().parent.parent
OUT=REPO/'assets'/'title_v2'
PMG_BASE=0xA000
HOOK_BASE=0x2400
POS_TABLE=0x3600
COLOR_TABLE=0x3630
MISSILE_POS=[76,120,132,145] # in 160-cc image coordinate (converted to GTIA HPOS)
ART_START_SCANLINE=32 # 8 ANTIC top + three blank (8-scanline) DL instructions

# per 16-scanline band: the chosen 8-clock-wide player windows and color values.
# Band numbers 0-9 cover original art; 10/11 are the original menu text area.
# Actual artist-approved bitmap is NEVER modified.
BANDS=[
 [(59,0x1E),(46,0x0E),(75,0x9E),(87,0x3C)], # logo crown
 [(39,0x1E),(51,0x0E),(99,0x9E),(110,0x3C)], # GAS letters
 [(35,0x1E),(57,0x0E),(88,0x9E),(105,0x3E)], # BLASTERS
 [(31,0x1E),(41,0x0E),(103,0x9E),(141,0x3E)], # B and the blue '82'
 [(144,0x1E),(76,0x0E),(102,0x9E),(136,0x3E)], # '82', Taco Smell sign, cap
 [(75,0x1E),(85,0x0E),(133,0x9E),(59,0x3E)], # Billy face/sign, hand
 [(74,0x1E),(62,0x0E),(108,0x9E),(96,0x3E)], # shirt, side mirror, car
 [(106,0x1E),(86,0x0E),(96,0x9E),(121,0x3E)], # windshield/hood shine
 [(75,0x1E),(115,0x0E),(96,0x9E),(64,0x3E)], # front headlights/grille
 [(66,0x1E),(119,0x0E),(106,0x9E),(52,0x3E)], # bumper and tire
 [(0,0x00)]*4, # text, no player graphics
 [(59,0x1E),(46,0x0E),(75,0x9E),(87,0x3C)], # reset to top image before next frame
]

# Small intentional highlights; no reshaping of a scene, logo or character.
# Format: player, [startX, startY, endX, endY] in native 160x160 image coords.
# A blend of fine diagonal edge accents, individual 'specular' reflections and
# brighter facial/car/sign points. Lines are clipped to one 8-clock player per band.
STROKES=[
 (0,59,10,65,6),(0,61,8,66,5),(0,42,23,44,21),
 (0,36,39,41,35),(0,33,51,35,47),(0,34,58,37,55),
 (0,146,66,148,69),(0,145,73,150,71),
 (0,76,85,79,82),(0,78,91,80,88),
 (0,75,98,78,96),(0,76,104,79,102),
 (0,107,116,111,118),(0,108,122,111,120),
 (0,76,130,79,129),(0,79,133,81,133),
 (0,68,148,72,149),
 (1,47,14,51,11),(1,47,12,49,12),
 (1,53,29,55,27),(1,59,40,62,38),
 (1,41,51,44,50),(1,78,76,81,74),
 (1,87,87,89,86),(1,86,93,87,92),
 (1,64,107,68,105),(1,88,117,91,116),
 (1,90,123,93,122),(1,116,130,119,131),
 (1,117,134,120,134),(1,120,145,123,145),
 (2,78,13,80,10),(2,101,25,104,22),
 (2,90,41,93,39),(2,104,59,106,56),
 (2,105,64,108,61),(2,104,70,106,67),
 (2,134,87,136,87),(2,136,91,137,91),
 (2,109,105,112,104),(2,97,122,100,121),
 (2,98,138,103,138),(2,107,146,111,145),
 (3,89,10,93,9),(3,110,28,114,26),
 (3,107,42,110,41),(3,143,57,146,56),
 (3,143,61,146,61),(3,138,69,142,67),
 (3,139,74,142,74),(3,139,87,141,86),
 (3,61,88,64,87),(3,62,94,65,94),
 (3,98,106,102,108),(3,124,119,127,118),
 (3,125,126,129,126),(3,65,128,70,127),
 (3,54,150,57,148),
]

# Two-bit missiles can pick up just 2 color clocks at a time. They reuse
# the corresponding player's COLOR ($D012-$D015), without needing extra DLIs.
MISSILE_ROWS={
 0: [(73,76),(74,76),(75,77),(89,76),(90,77)],  # eye/cap glimmer
 1: [(117,121),(118,120),(119,121),(123,120)], # windshield chrome
 2: [(130,132),(131,132),(132,133),(133,133)], # headlight streak
 3: [(56,145),(57,146),(59,145),(69,146)],          # sign sparkle
}


def line_pixels(x1,y1,x2,y2):
 dx=abs(x2-x1);dy=-abs(y2-y1);sx=1 if x1<x2 else -1;sy=1 if y1<y2 else -1;err=dx+dy
 while True:
  yield x1,y1
  if x1==x2 and y1==y2:break
  e=2*err
  if e>=dy:err+=dy;x1+=sx
  if e<=dx:err+=dx;y1+=sy


def create_pmg_data(origin=ART_START_SCANLINE):
 if not 8<=origin<=56:raise ValueError('PM vertical origin must be 8..56')
 buf=bytearray(2048)
 mask=[[(None) for _ in range(160)] for _ in range(160)]
 count=[0]*4
 # Hand-selected pixels only; guard 3 lines at start of each band to allow DLI
 # time for the new player HPOS/color registers to settle.
 for p,x1,y1,x2,y2 in STROKES:
  for x,y in line_pixels(x1,y1,x2,y2):
   if not (0<=x<160 and 0<=y<160):continue
   band=y//16
   left,color=BANDS[band][p]
   if y%16<3 or not left<=x<left+8:continue
   off=origin+y
   assert off<256
   pos=0x400+p*0x100+off
   bit=(1<<(7-(x-left)))
   if not buf[pos]&bit:count[p]+=1
   buf[pos]|=bit
   mask[y][x]=color
 for p,locations in MISSILE_ROWS.items():
  mx=MISSILE_POS[p]
  for y,x in locations:
   if not 0<=y<160 or y%16<3 or not mx<=x<mx+2:continue
   if y+origin>=256:continue
   shift=p*2+(x-mx)
   buf[0x300+origin+y]|=1<<shift
   mask[y][x]=BANDS[y//16][p][1]
 assert any(buf[0x300:0x400])
 assert all(sum(bool(x) for x in buf[0x400+p*256:0x500+p*256])>0 for p in range(4))
 return bytes(buf),mask,count


def create_tables():
 # DLI index 0 sets next band1, ... index 9 text band10,
 # index 10 resets to band0 for next raster frame (during text band11).
 pos=bytes((48+BANDS[(i+1)%11][p][0]) for p in range(4) for i in range(11))
 col=bytes(BANDS[(i+1)%11][p][1] for p in range(4) for i in range(11))
 assert len(pos)==len(col)==44
 # index10 explicit top-band reset (important: first art band of next frame)
 assert [pos[p*11+10] for p in range(4)]==[48+BANDS[0][p][0] for p in range(4)]
 return pos,col


def make_hook_code(base_labels,original):
 set_scene=base_labels['SET_SCENE']
 draw_title=base_labels['DRAW_TITLE']
 dli_title=base_labels['DLI_TITLE']
 dli_done=base_labels['DLI_DONE']
 assert original[set_scene-0x2000:set_scene-0x2000+5]==bytes([0xA9,0x00,0x8D,0x0E,0xD4])
 assert original[draw_title-0x2000]==0xA9 and original[draw_title-0x2000+2:draw_title-0x2000+5]==bytes([0x8D,0x30,0x02])
 assert original[dli_title-0x2000:dli_title-0x2000+3]==bytes([0xBD,0x00,0x35])
 a=v1.Asm(HOOK_BASE)
 a.label('PM_DISABLE')
 a.imm('LDA',0xA9,0)
 a.abs('STA',0x8D,0xD40E) # overwritten original: NMIEN off FIRST
 a.abs('STA',0x8D,0xD01D) # GRACTL off on ALL scene changes
 for reg in range(0xD00D,0xD012):a.abs('STA',0x8D,reg) # GRAFPn/GRAFM zero
 a.abs('JMP',0x4C,set_scene+5)
 a.label('PM_TITLE_SETUP')
 a.imm('LDA',0xA9,PMG_BASE>>8);a.abs('STA',0x8D,0xD407) # PMBASE
 a.imm('LDA',0xA9,0)
 for reg in (0xD008,0xD009,0xD00A,0xD00B,0xD00C):a.abs('STA',0x8D,reg)
 a.abs('STA',0x8D,0x026F);a.abs('STA',0x8D,0xD01B) # players in front of playfield
 for p in range(4):
  x,c=BANDS[0][p]
  a.imm('LDA',0xA9,48+x);a.abs('STA',0x8D,0xD000+p)
  a.imm('LDA',0xA9,48+MISSILE_POS[p]);a.abs('STA',0x8D,0xD004+p)
  a.imm('LDA',0xA9,c);a.abs('STA',0x8D,0x02C0+p);a.abs('STA',0x8D,0xD012+p)
 a.imm('LDA',0xA9,3);a.abs('STA',0x8D,0xD01D) # both players and missiles
 a.imm('LDA',0xA9,0x2E);a.abs('STA',0x8D,0x022F);a.abs('STA',0x8D,0xD400)
 # Original DRAW_TITLE starts LDA #<DL_TITLE, STA SDLSTL. Restore these exact ops.
 a.imm('LDA',0xA9,base_labels['DRAW_TITLE_ORIGINAL_LOW'])
 a.abs('STA',0x8D,0x0230)
 a.abs('JMP',0x4C,draw_title+5)
 a.label('PM_TITLE_DLI')
 # Original palette DLI logic. The color clock DMA is intentionally unchanged.
 for idx,reg in enumerate((0xD01A,0xD016,0xD017,0xD018)):
  addr=0x3500+idx*11
  a.op(f'LDA ${addr:04X},X',0xBD,addr&255,addr>>8)
  a.abs('STA',0x8D,reg)
 # Positions and colors on the next band, reusing all four players.
 # PM data blank for the first 3 lines of each band to avoid DLI settling artifacts.
 for p in range(4):
  addr=POS_TABLE+11*p
  a.op(f'LDA ${addr:04X},X',0xBD,addr&255,addr>>8)
  a.abs('STA',0x8D,0xD000+p)
 for p in range(4):
  addr=COLOR_TABLE+11*p
  a.op(f'LDA ${addr:04X},X',0xBD,addr&255,addr>>8)
  a.abs('STA',0x8D,0xD012+p)
 a.abs('JMP',0x4C,dli_done)
 code=a.finalize()
 assert HOOK_BASE+len(code)<=0x2800, f'extension too large: {len(code)}'
 return a,code,dict(PM_DISABLE=a.labels['PM_DISABLE'],PM_TITLE_SETUP=a.labels['PM_TITLE_SETUP'],PM_TITLE_DLI=a.labels['PM_TITLE_DLI'])


def patch_original(original,base_labels,entry):
 code=bytearray(original)
 def writehook(addr,length,target):
  assert length>=3
  o=addr-0x2000
  code[o:o+length]=bytes([0x4C,target&255,target>>8]+[0xEA]*(length-3))
 writehook(base_labels['SET_SCENE'],5,entry['PM_DISABLE'])
 writehook(base_labels['DRAW_TITLE'],5,entry['PM_TITLE_SETUP'])
 writehook(base_labels['DLI_TITLE'],3,entry['PM_TITLE_DLI'])
 assert len(code)==len(original)
 return bytes(code)


def render_preview(title,mask,out):
 """Generate an illustrative overlay comparison, not an emulator screenshot."""
 source=Path(__file__).resolve().parent.parent/'assets'/'title_v2'/'title_original_160x160_preview.png'
 if not source.exists():
  raise FileNotFoundError(f'Required checked-in quantized baseline preview: {source}')
 before=Image.open(source).convert('RGB')
 if before.size!=(160,160):raise ValueError(f'expected exact native preview, got {before.size}')
 after=before.copy()
 gtia_palette={0x1E:(255,245,130),0x0E:(238,238,238),0x9E:(176,255,255),0x9C:(138,230,255),0x3E:(255,220,196),0x3C:(244,175,148)}
 count=0
 for y,row in enumerate(mask):
  for x,color in enumerate(row):
   if color is not None:
    after.putpixel((x,y),gtia_palette.get(color,(255,255,235)));count+=1
 before=before.resize((640,640),Image.Resampling.NEAREST)
 after=after.resize((640,640),Image.Resampling.NEAREST)
 canvas=Image.new('RGB',(1320,690),'#0c0c18');canvas.paste(before,(10,35));canvas.paste(after,(670,35))
 d=ImageDraw.Draw(canvas);d.text((20,12),'V1 ORIGINAL (bitmap unchanged)',fill='white');d.text((680,12),'V2 PMG HIGHLIGHTS (illustrative)',fill='white')
 canvas.save(out/'Title_v1_vs_v2_PMG_Comparison.png')
 return count


def build(repo=REPO,out=OUT,origin=ART_START_SCANLINE):
 repo=Path(repo);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 # Validate original combined executable from same exact builders/artwork, but do not modify it.
 orig_out=out/'_v1_repro';base_meta=v1.build(repo,orig_out)
 base_parts=v1.xex_segments(orig_out/base_meta['output'])
 if base_meta['sha256']!='08971fa2ca324e1e5e36bbc7c7d0fe891cb23c568230abb70c93a4f6de3d7e29':
  raise ValueError('The known-good v1 build changed; do not create overlays against unverified code')
 # Controller label addresses from authoritative original assembler.
 titles=v1.xex_segments(repo/'assets/title/Title_Option3_Original.xex')
 crew=v1.xex_segments(repo/'assets/intro/meet_the_crew_v4.xex')
 arrival=v1.xex_segments(repo/'assets/arrival/arrival_v3.xex')
 palette={kind:v1.palette_data(seg[0x2000],seg[0x3C00])[0] for kind,seg in [('title',titles),('crew',crew),('arrival',arrival)]}
 asm,original=v1.assemble_controller(palette)
 assert original==base_parts[0x2000], 'reference code differs from integrated v1'
 # Extract the v1 loading of SDLSTL low byte at DRAW_TITLE; no guessing.
 dlorig=original[asm.labels['DRAW_TITLE']-0x2000:asm.labels['DRAW_TITLE']-0x2000+5]
 assert dlorig[0]==0xA9 and dlorig[2:]==b'\x8d\x30\x02'
 asm.labels['DRAW_TITLE_ORIGINAL_LOW']=dlorig[1]
 hookasm,hookcode,entries=make_hook_code(asm.labels,original)
 pmg,mask,pixcount=create_pmg_data(origin)
 pos,col=create_tables()
 parts=dict(base_parts)
 parts[0x2000]=patch_original(original,asm.labels,entries)
 parts[HOOK_BASE]=hookcode
 parts[POS_TABLE]=pos
 parts[COLOR_TABLE]=col
 parts[PMG_BASE]=pmg
 xex=v1.encode_xex(parts)
 name='GasBlasters82_TitleV2_PMG_OpeningSequence.xex'
 (out/name).write_bytes(xex)
 (out/'pmg_2kb.bin').write_bytes(pmg)
 (out/'pmg_position_11x4.bin').write_bytes(pos)
 (out/'pmg_colors_11x4.bin').write_bytes(col)
 (out/'pmg_extension_6502.asm').write_text('; Valid 6502 mnemonics; reference listing, Python script emits actual machine code.\n    *= $2400\n'+'\n'.join(hookasm.asm)+'\n')
 (out/'pmg_overlay_data.json').write_text(json.dumps({'origin':origin,'horizontal_missiles':MISSILE_POS,'bands':BANDS,'strokes':STROKES,'missile_rows':MISSILE_ROWS,'player_set_pixels':pixcount,'overlay_bands':10},indent=2)+'\n')
 count=render_preview(titles,mask,out)
 meta={'file':name,'sha256':hashlib.sha256(xex).hexdigest(),'bytes':len(xex),'original_v1_sha256':base_meta['sha256'],'pmg':'four players and four missiles; one-line $A000 DMA', 'pmg_origin_scanline':origin,'pmg_pixels_approx':count,
 'original_title_bitmap_sha256':hashlib.sha256(titles[0x4000]+titles[0x5000]).hexdigest(),
 'unmodified_segments':[f'${a:04X}' for a in base_parts if a!=0x2000],
 'modified_code':'$2000 controller receives 3 branch hooks, $2400 PMG extension',
 'new_segments':['$2400','$3600','$3630','$A000'],'player_bands':BANDS,
 'plays':'Title v2 PMG (Arcade Rock) -> original Crew (Funky Gas Attack) -> original Arrival (continuous Funk) -> Stage 1 placeholder (silent)',
 'test_status':'CPU hook and binary validations only; requires user Atari800 screenshot/listening test'}
 (out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
 print(json.dumps({'file':name,'bytes':len(xex),'sha256':meta['sha256'],'overlay_pixels':count,'pmg_pixels_per_player':pixcount,'hooks':entries},indent=2))
 return meta

def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=REPO);p.add_argument('--output',type=Path,default=OUT);p.add_argument('--pmg-y-offset',type=int,default=32)
 a=p.parse_args();build(a.repo,a.output,a.pmg_y_offset)
if __name__=='__main__':main()
