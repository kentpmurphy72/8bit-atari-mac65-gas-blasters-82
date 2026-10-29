#!/usr/bin/env python3
"""Atari 800XL ANTIC E conversion proof of concept from Gas Blasters '82 v2 artwork.
Produces full bitmap and mixed bitmap+40-column text XEX files, raw data and previews.
Standard Atari XEX, stock 64KB XL target. XEX has NOT been emulator tested.
"""
from pathlib import Path
import numpy as np, cv2, json, textwrap, zipfile, struct, sys
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent/'assets'/'intro'
SRC=ROOT/'source_art_original.png'
OUT=ROOT/'generated_atari_assets'
OUT.mkdir(exist_ok=True)
W=160; FULL_H=192; ART_H=128; ROW=40
BANDS=12; BAND_H=16

# Illustrative RGB rendering of GTIA register values. Every address is an
# actual GTIA hue/luminance byte: high nybble hue; even low nybble luminance.
# RGB approximate mapping from the Lospec Atari 8-bit Family GTIA palette.
HUE_SHADES=[
 ['000000','222222','444444','666666','888888','aaaaaa','cccccc','eeeeee'],
 ['190700','3b2900','5d4b00','7f6d00','a18f1a','c3b13c','e5d35e','fff582'],
 ['310000','531700','753900','975b0a','b97d2c','db9f4e','fdc170','ffe39c'],
 ['420404','600800','822a0d','a44c2f','c66e51','e89073','ffb298','ffd4c4'],
 ['410103','61001b','83203c','a5425e','c76480','e986a2','ffa8c8','ffcaef'],
 ['330035','55004c','771d6d','993f8f','bb61b1','dd83d3','ffa5e4','ffc7ee'],
 ['1d005c','400074','622195','8443b7','a665d9','c887eb','e9a9ec','ffcbef'],
 ['020071','240b8c','462dae','684fd0','8a71f2','ac93f7','ceb5f7','f0d7f7'],
 ['000068','081b90','2a3db2','4c5fd4','6e81f6','90a3ff','b2c5ff','d4e7ff'],
 ['000a4d','002c79','134ea0','3570c2','5792e4','79b4ff','9bd6ff','bdf8ff'],
 ['001a26','003c52','065e7c','28809e','4aa2c0','6cc4e2','8ee6ff','b0ffff'],
 ['01250a','004622','05684d','278a6f','49ac91','6bceb3','8df0d5','affff1'],
 ['04260d','054713','106b1b','328d3d','54af5f','76d181','98f3a3','baffbf'],
 ['00230a','044613','266713','488914','6aab36','8ccd58','aeef7a','d0ff97'],
 ['001707','1f3908','415b08','637d08','859f1e','a7c140','c9e362','ebff82'],
 ['1b0701','3c2900','5f4c00','816f00','a4921a','c7b43d','ead760','fffa84'],
]
PAL=np.zeros((256,3),np.uint8)
for h,vals in enumerate(HUE_SHADES):
    for i,s in enumerate(vals):
        PAL[h*16+i*2]=tuple(bytes.fromhex(s))
        PAL[h*16+i*2+1]=tuple(bytes.fromhex(s))
(OUT/'gtia_preview_palette.act').write_bytes(PAL.tobytes())

IM=Image.open(SRC).convert('RGB')
print('Input:',IM.size)
# Resize all native pixels from the existing user artwork; no new figures.
source_full=np.asarray(IM.resize((W,FULL_H), Image.Resampling.LANCZOS))
# Cut the original illustration BEFORE the row of character-name labels starts.
# The crop is intentional: no names remain and all five figures are retained.
ART_SOURCE_BOTTOM=693
source_art=np.asarray(IM.crop((0,0,IM.width,ART_SOURCE_BOTTOM)).resize((W,ART_H),Image.Resampling.LANCZOS))
Image.fromarray(source_art).save(OUT/'source_cropped_for_mixed_160x128.png')

# Candidate actual color-register bytes; even luminances only.
CODES=np.array([x for x in range(256) if (x&1)==0],dtype=np.uint8)
RGB=PAL[CODES]
# Lab approximates human sensitivity to hue and brightness.
LAB=cv2.cvtColor(RGB[None,:,:],cv2.COLOR_RGB2LAB)[0].astype(np.float32)
BG_CODE=0
BG_INDEX=int(np.where(CODES==0)[0][0]);
BAYER=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)

# GTIA band palette chosen using greedy approximate perceptual error minimization
# with mandatory black/background; evaluate only sampled pixels to keep repeatable.
def quantize(img, band_count, caption=False):
    ids=np.zeros(img.shape[:2],dtype=np.uint8)
    palettes=[]
    for k in range(band_count):
        ymin=k*16; ymax=min(img.shape[0],ymin+16)
        subset=img[ymin:ymax].copy()
        pix=cv2.cvtColor(subset,cv2.COLOR_RGB2LAB).reshape(-1,3).astype(np.float32)
        # Background black is mandatory to preserve outlines; optimize the other three.
        diff=((pix[:,None,:]-LAB[None,:,:])**2).sum(axis=2)
        current=diff[:,BG_INDEX].copy()
        selected=[BG_INDEX]
        for _ in range(3):
            improve=np.maximum(current[:,None]-diff,0).sum(axis=0)
            # Avoid very similar neighboring luminance selections unless highly beneficial
            improve[selected]=-1
            winner=int(np.argmax(improve))
            selected.append(winner)
            current=np.minimum(current,diff[:,winner])
        # Sort chosen by brightness into register slots 1..3, leaving black at 0.
        chosen=[BG_INDEX]+sorted(selected[1:],key=lambda i: float(LAB[i,0]))
        palette_lab=LAB[chosen]
        # Subtle ordered brightness dithering, lowers quantization posterization.
        yy,xx=np.mgrid[ymin:ymax,0:img.shape[1]]
        extra=((BAYER[yy%4,xx%4]-7.5)/7.5)*5.0
        shifted=cv2.cvtColor(subset,cv2.COLOR_RGB2LAB).astype(np.float32)
        shifted[:,:,0]+=extra
        dist=((shifted[:,:,None,:]-palette_lab[None,None,:,:])**2).sum(axis=3)
        ids[ymin:ymax]=np.argmin(dist,axis=2).astype(np.uint8)
        palettes.append([int(CODES[n]) for n in chosen])
    preview=np.empty((img.shape[0],img.shape[1],3),dtype=np.uint8)
    for i,p in enumerate(palettes):
        a0=i*16;b=min((i+1)*16,img.shape[0]);preview[a0:b]=PAL[np.array(p,dtype=np.uint8)][ids[a0:b]]
    return ids,palettes,preview

full_ids, full_pals, full_rgb=quantize(source_full,12)
art_ids, art_pals, art_rgb=quantize(source_art,8)

# The mixed 192 scanline design has 8 art bands (8*16 = 128) plus
# four 16-scanline text bands (eight ANTIC mode 2 character lines).
# The text band's 2-bit bitmap registers are not needed by ANTIC 2,
# but COLBK/COLPF2 are set to black/light gray for clarity.
caption_palette=[0x00,0x0a,0x0e,0x00]  # ANTIC 2: COLPF2=background hue, COLPF1=ink luminance
mixed_pals=art_pals+[caption_palette]*4

# ANTIC E stores four successive 2-bit pixels in one byte, high-to-low.
def pack4(pixel_ids):
    assert pixel_ids.shape[1]==160 and np.max(pixel_ids)<4
    b=pixel_ids.reshape(pixel_ids.shape[0],40,4).astype(np.uint8)
    return ((b[:,:,0]<<6)|(b[:,:,1]<<4)|(b[:,:,2]<<2)|b[:,:,3]).tobytes()

def unpack4(binary,height):
    b=np.frombuffer(binary,dtype=np.uint8).reshape(height,40)
    return np.stack([b>>6,(b>>4)&3,(b>>2)&3,b&3],axis=-1).reshape(height,160)&3

full_dat=pack4(full_ids);art_dat=pack4(art_ids)
assert len(full_dat)==7680 and len(art_dat)==5120
assert np.array_equal(unpack4(full_dat,192),full_ids)
assert np.array_equal(unpack4(art_dat,128),art_ids)
(OUT/'screen1_full_160x192_antic_e.bin').write_bytes(full_dat)
(OUT/'screen1_mixed_art_160x128_antic_e.bin').write_bytes(art_dat)
Image.fromarray(full_rgb).save(OUT/'screen1_full_160x192_4colors_per_band.png')
Image.fromarray(art_rgb).save(OUT/'screen1_mixed_art_160x128_4colors_per_band.png')

# Create an EIGHT-row 40-column caption: one blank margin row before the title,
# four balanced LEFT-ALIGNED quote rows, and a blank row before the Fire prompt.
# No extra/removed words: the approved quote remains byte-for-byte identical.
quote="Meet Billy Blaster. He's got a fast car, great friends, and a stomach that's about to become a national emergency."
wrapped=["Meet Billy Blaster. He's got","a fast car, great friends, and","a stomach that's about to","become a national emergency."]
assert ' '.join(wrapped)==quote
textlines=['', '             MEET THE CREW']+[('    '+v) for v in wrapped]+['', '          FIRE TO CONTINUE >']
assert len(textlines)==8 and all(len(x)<=40 for x in textlines)
textcells=b''.join(bytes([(ord(ch)-32) if 32<=ord(ch)<=95 else ord(ch) for ch in line.ljust(40)]) for line in textlines)
assert len(textcells)==320
(OUT/'screen1_40col_text_8rows.bin').write_bytes(textcells)
(OUT/'intro_quote.txt').write_text(quote+'\n',encoding='utf-8')

# Custom 1KB screen-code glyph ROM generated from a freely available system font.
# This avoids depending on the user's OS ROM charset for font appearance.
font_candidates=['/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf']
fontfile=next((x for x in font_candidates if Path(x).exists()),None)
if not fontfile: raise RuntimeError('No font available')
font=ImageFont.truetype(fontfile,8)
char_bytes=bytearray(1024)
for ascii_code in range(32,127):
    ch=chr(ascii_code)
    screen_code=(ascii_code-32) if ascii_code<=95 else ascii_code
    glyph=Image.new('1',(8,8),0);dr=ImageDraw.Draw(glyph)
    # FIXED BASELINE for ALL glyphs. Previous builder centered each letter
    # independently and created wavy text (ascenders/descenders jumped).
    dr.text((1,-2),ch,font=font,fill=1)
    imbytes=np.asarray(glyph,dtype=np.uint8)
    for y in range(8):
        v=0
        for x in range(8):v=(v<<1)|int(imbytes[y,x]!=0)
        char_bytes[screen_code*8+y]=v
(OUT/'screen1_custom_charset_1kb.bin').write_bytes(char_bytes)

# Correct the XEX text preview: mode 2 is 320 color clocks wide, bitmap mode E
# has 160 double-wide color-clock pixels. This is a 320x192 clock-space mockup.
artclock=np.repeat(art_rgb,2,axis=1)
captionclock=np.empty((64,320,3),np.uint8); captionclock[:]=PAL[0x00]
for row in range(8):
    for col in range(40):
        charcode=textcells[row*40+col]
        glyph=char_bytes[charcode*8:charcode*8+8]
        for yy,v in enumerate(glyph):
            for xx in range(8):
                if v&(0x80>>xx):captionclock[row*8+yy,col*8+xx]=PAL[0x0e]
mixedclock=np.vstack([artclock,captionclock]); assert mixedclock.shape==(192,320,3)
Image.fromarray(mixedclock).resize((960,720),Image.Resampling.NEAREST).save(OUT/'screen1_mixed_mode_TV_preview.png')
Image.fromarray(np.repeat(full_rgb,2,axis=1)).resize((960,720),Image.Resampling.NEAREST).save(OUT/'screen1_full_mode_TV_preview.png')
# Side by side user visual comparison
comp=Image.new('RGB',(1920,760),'#15151b');comp.paste(Image.open(OUT/'screen1_full_mode_TV_preview.png'),(0,36));comp.paste(Image.open(OUT/'screen1_mixed_mode_TV_preview.png'),(960,36))
d=ImageDraw.Draw(comp);ft=ImageFont.truetype(fontfile,20)
d.text((40,4),'FULL BITMAP  -  ALL 160 x 192, TEXT IS PIXELS',font=ft,fill='#e6e6e6')
d.text((1000,4),'RECOMMENDED  -  160 x 128 ART + 8 TEXT ROWS',font=ft,fill='#e6e6e6')
comp.save(OUT/'screen1_800xl_comparison.png')

# 12 register banks ×4 GTIA registers. Packed rows [COLBK,COLPF0,COLPF1,COLPF2].
def regtable(pals):return bytes(v for row in pals for v in row)
(OUT/'screen1_mixed_gtia_12bands_48bytes.bin').write_bytes(regtable(mixed_pals))
(OUT/'screen1_full_gtia_12bands_48bytes.bin').write_bytes(regtable(full_pals))
for name,p in [('mixed',mixed_pals),('full',full_pals)]:
 (OUT/f'screen1_{name}_palettes.json').write_text(json.dumps([{'scanlines':f'{i*16}-{(i+1)*16-1}', 'COLBK':f'${c[0]:02X}','COLPF0':f'${c[1]:02X}','COLPF1':f'${c[2]:02X}','COLPF2':f'${c[3]:02X}','preview_rgb':[list(map(int,PAL[v])) for v in c]} for i,c in enumerate(p)],indent=2)+'\n')

# XEX display list, 24 top blank lines, E graphics, optional mode 2 text.
DL_ADDR=0x3C00; CODE_ADDR=0x2000
# buffer 1: $4000-$4EFF (96*40), buffer 2: $5000-$5EFF (remaining <=96*40)
# segment boundaries never cross ANTIC's 4KB video DMA addressing boundary.
def build_display_list(mixed):
    out=bytearray([0x70,0x70,0x70])
    height=128 if mixed else 192
    for y in range(height):
        flag=0x80 if y%16==15 and y!=191 else 0
        if y==0:out+=bytes([0x4e|flag,0x00,0x40])
        elif y==96:out+=bytes([0x4e|flag,0x00,0x50])
        else:out.append(0x0e|flag)
    if mixed:
        for row in range(8):
            flag=0x80 if row in (1,3,5) else 0
            if row==0:out+=bytes([0x42|flag,0x00,0x58])
            else:out.append(0x02|flag)
    out+=bytes([0x41,DL_ADDR&255,DL_ADDR>>8]) # JVB at bottom
    return bytes(out)

# Tiny assembler/patcher for only the instructions this example uses.
class Asm:
 def __init__(self,base=0x2000):self.b=bytearray();self.base=base;self.labels={};self.patch=[]
 def here(self):return self.base+len(self.b)
 def label(self,name):self.labels[name]=self.here()
 def byte(self,*a):self.b.extend(a)
 def imm(self,v):self.byte(0xA9,v&255)
 def sta(self,addr):self.byte(0x8D,addr&255,(addr>>8)&255)
 def ldx(self,ref):self.byte(0xAE,0,0);self.patch.append((len(self.b)-2,'abs',ref))
 def stx(self,ref):self.byte(0x8E,0,0);self.patch.append((len(self.b)-2,'abs',ref))
 def lda_x(self,ref):self.byte(0xBD,0,0);self.patch.append((len(self.b)-2,'abs',ref))
 def jmp(self,ref):self.byte(0x4C,0,0);self.patch.append((len(self.b)-2,'abs',ref))
 def bcc(self,ref):self.byte(0x90,0);self.patch.append((len(self.b)-1,'rel',ref))
 def finish(self):
  for i,mode,ref in self.patch:
   target=self.labels[ref]
   if mode=='abs':self.b[i]=target&255;self.b[i+1]=target>>8
   else:
    offset=target-(self.base+i+1)
    if not -128<=offset<=127:raise ValueError('relative offset')
    self.b[i]=offset&255
  return bytes(self.b)

# Generate code with runtime DLI palette array read. DLI preserves A, X, Y.
def build_code(pals):
 asm=Asm(CODE_ADDR)
 asm.label('START')
 asm.byte(0x78)             # SEI
 asm.imm(0x00);asm.sta(0xD40E);asm.sta(0x022F)  # disable NMIs and DMA
 for reg,name,which in [(0x0200,'DLI','lo'),(0x0201,'DLI','hi')]:
  pass
 # Jump target address is in this code segment, patched after layout; fixups manually.
 asm.imm(0); lo_pos=len(asm.b)-1;asm.sta(0x0200)
 asm.imm(0); hi_pos=len(asm.b)-1;asm.sta(0x0201)
 asm.imm(DL_ADDR&255);asm.sta(0x0230)
 asm.imm(DL_ADDR>>8);asm.sta(0x0231)
 asm.imm(0x60);asm.sta(0x02F4)  # custom font CHBASE $6000
 asm.imm(0);asm.sta(0x026F)    # PRIOR normal
 # OS shadow colors used for topmost palette on VBLANK.
 for val,shadow in zip(pals[0],[0x02C8,0x02C4,0x02C5,0x02C6]):
  asm.imm(val);asm.sta(shadow)
 asm.imm(0x22);asm.sta(0x022F) # screen DMA, normal width
 asm.imm(0xC0);asm.sta(0xD40E) # enable VBI and DLI
 asm.byte(0x58)                # CLI
 asm.label('IDLE');asm.jmp('IDLE')
 asm.label('DLI')
 asm.byte(0x48,0x8A,0x48,0x98,0x48) # PHA / TXA / PHA / TYA / PHA
 asm.ldx('INDEX')
 asm.byte(0xA9,0x00);asm.sta(0xD40A) # WSYNC: change registers at line boundary
 for array,hw in [('BGT',0xD01A),('P0T',0xD016),('P1T',0xD017),('P2T',0xD018)]:
  asm.lda_x(array);asm.sta(hw)
 asm.byte(0xE8) # INX
 asm.byte(0xE0,0x0B) # CPX #11
 asm.bcc('SKIP_RESET')
 asm.byte(0xA2,0x00) # LDX #0
 asm.label('SKIP_RESET');asm.stx('INDEX')
 asm.byte(0x68,0xA8,0x68,0xAA,0x68,0x40) # PLA,TAY,PLA,TAX,PLA,RTI
 asm.label('INDEX');asm.byte(0)
 for index,name in enumerate(['BGT','P0T','P1T','P2T']):
  asm.label(name);asm.byte(*[p[index] for p in pals[1:]])
 code=bytearray(asm.finish());code[lo_pos]=asm.labels['DLI']&255;code[hi_pos]=asm.labels['DLI']>>8
 return bytes(code),asm.labels

def seg(start,data):
    end=start+len(data)-1
    if end>0xffff:raise ValueError('Segment too large')
    return struct.pack('<HH',start,end)+data

def xex_build(mixed):
    pals=mixed_pals if mixed else full_pals
    bits=art_dat if mixed else full_dat
    height=128 if mixed else 192
    dis=build_display_list(mixed)
    code,labels=build_code(pals)
    # Two segments align at $4000 and $5000, second 48/96 lines.
    out=bytearray(b'\xff\xff')
    out+=seg(0x2000,code)
    out+=seg(DL_ADDR,dis)
    out+=seg(0x4000,bits[:96*40])
    out+=seg(0x5000,bits[96*40:])
    if mixed:
        out+=seg(0x5800,textcells)
    # Charset stored at $6000; keep all RAM low enough for stock 800XL.
    out+=seg(0x6000,char_bytes)
    # Atari loader's RUNAD vector at $02E0 invokes START at end of load.
    out+=seg(0x02E0,struct.pack('<H',0x2000))
    name='screen1_800xl_mixed_40col.xex' if mixed else 'screen1_800xl_full_bitmap.xex'
    (OUT/name).write_bytes(out)
    (OUT/('screen1_mixed_display_list.bin' if mixed else 'screen1_full_display_list.bin')).write_bytes(dis)
    return name,labels,dis,code

mixed_name,mixed_labels,mixed_dl,mixed_code=xex_build(True)
full_name,full_labels,full_dl,full_code=xex_build(False)
# sanity check: one and only one interrupt at each 16-line band boundary, 11 total.
for mixed,dl in [(True,mixed_dl),(False,full_dl)]:
    y=0; interrupts=[]; i=3; modeCount=0
    while i<len(dl)-3:
        mode=dl[i];i+=1
        if (mode&15) not in (0x0E,0x02):raise ValueError('Bad ANTIC instruction')
        if mode&0x40:i+=2
        h=8 if (mode&15)==2 else 1
        y+=h;modeCount+=1
        if mode&0x80:interrupts.append(y)
    assert y==192 and len(interrupts)==11 and interrupts==list(range(16,192,16)),(mixed,y,interrupts)
assert full_dl[-3:]==mixed_dl[-3:]==bytes([0x41,0x00,0x3c])

manifest={'source':SRC.name,'native_full':{'dimensions':[160,192],'bytes':7680,'gtia_registers_per_band':['COLBK','COLPF0','COLPF1','COLPF2'],'palette_bands':12,'dlis':11,'mode':'ANTIC E'},'native_mixed':{'art_dimensions':[160,128],'art_bytes':5120,'text_columns':40,'text_rows':8,'text_bytes':320,'custom_font_bytes':1024,'mode':'ANTIC E + ANTIC 2','palette_bands':12,'dlis':11},'memory':{'code':'$2000','display_list':'$3C00','bitmap_0':'$4000 - $4EFF','bitmap_1':'$5000 - $5EFF (full image) / $5000 - $54FF (mixed)','text':'$5800','font':'$6000','run_vector':'$02E0'},'warning':'Generated and structurally validated; XEX display not emulator-tested. Palette RGB shown is approximate. Names in source image are unapproved placeholders.', 'text':quote}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

README=f'''# Gas Blasters '82 — Screen 1 / Atari 800XL proof of concept

**Source:** original user-approved Version 2 reference image, `{SRC.name}`.
**Target:** unmodified 64 KB NTSC Atari 800XL, ANTIC E and optional ANTIC 2 text.
**Status:** Byte packing, memory layout and display-list shape validated by generator; **not yet boot-tested on Altirra/actual Atari**.

## Start here

- `{mixed_name}` — **recommended** ready-to-load XEX. ANTIC E illustration, 160×128, followed by eight true 40-column ANTIC 2 text rows (crisper sentence). Full display height 192 scanlines.
- `screen1_mixed_mode_TV_preview.png` — expanded 4:3 preview of the recommended mixed display.
- `{full_name}` — faithful full-screen ANTIC E, 160×192, including automatically scaled original text (less legible).
- `screen1_full_mode_TV_preview.png` — enlarged full-bitmap version.
- `screen1_800xl_comparison.png` — comparison of both.

## 800XL raster implementation

ANTIC E is **160 logical pixels by 192 scanlines**, **2 bits/pixel**, **40 bytes per scanline**. Encoded pixels use most-significant pair first: `00=COLBK`, `01=COLPF0`, `10=COLPF1`, `11=COLPF2`.

The GTIA palette changes every **16 scanlines**, with **12 horizontal palette bands and 11 display-list interrupts (DLIs)**. In ANTIC mode 2, the text background uses COLPF2 and the foreground takes its brightness from COLPF1; the caption palettes deliberately select black COLPF2 and white-brightness COLPF1. Every band uses only four GTIA colors (one background + three playfield colors); no per-pixel arbitrary RGB colors, GPU textures, extra RAM, or PMG overlays.

Screen memory is **split at scanline 96** by a new LMS in the display list to avoid the ANTIC 4 KB display-memory DMA boundary:
- `$4000–$4EFF` = first 96 bitmap scanlines (3,840 bytes).
- `$5000–$5EFF` = next 96 scanlines in full-bitmap mode, or `$5000–$54FF` = next 32 scanlines in mixed mode.
- `$5800–$593F` = eight lines of ANTIC 2 screen codes in mixed mode.
- `$6000–$63FF` = 1 KB custom font.
- `$3C00` = display list; `$2000` = loader and DLI handler.

The intro sentence is kept **exact** in the 40-column mixed version, wrapped across four balanced left-aligned rows; one blank row above the lowered header and one blank row before the Fire prompt. All glyphs share a fixed baseline. The demo presently **holds the illustration on screen**; the Fire prompt is cosmetic, not an implemented input event.

## Run in Altirra

1. Configure an **Atari 800XL with 64 KB, NTSC**; BASIC can be disabled for convenience.
2. Open `.xex` via **File → Open** (executable/program) or drag it into Altirra; select `{mixed_name}` first.
3. Expect top illustration with a clear 40-column caption. Compare against the PNG previews.
4. Verify no flicker at 16-scanline color boundaries, no corruption at image scanline 96, and text glyphs. Report any discrepancies before adopting the engine.

## Files for Codex

- `screen1_mixed_art_160x128_antic_e.bin` — 5,120-byte graphics block; the character-name labels have been cropped out before bitmap conversion.
- `screen1_full_160x192_antic_e.bin` — 7,680-byte graphics block.
- `screen1_*_gtia_12bands_48bytes.bin` — 12 registers groups ×4 bytes: `[COLBK,COLPF0,COLPF1,COLPF2]`.
- `screen1_*_palettes.json` — human-readable GTIA code/color bands.
- `screen1_*_display_list.bin` — ANTIC display list, with 11 DLI markers.
- `screen1_40col_text_8rows.bin` — ANTIC 2 screen codes.
- `screen1_custom_charset_1kb.bin` — font used by this demo, 8 scanlines/character.
- `{Path(__file__).name}` — reproducible Python build script.
- `manifest.json` — asset sizes, memory map, text.

## Visual caveats

This is an **automated palette-limited conversion** of a richly colored high-resolution image. It respects 4 available register colors per scanline, but it is not hand-retouched pixel art and cannot match the arcade source detail. The palette RGB values are *approximate preview* colors; NTSC television/emulator palettes will differ. Full-resolution story type becomes difficult to read when reduced to 160 pixels, hence the mixed graphic+text production recommendation.

The names **Dave, Tracy, Mike, Jen** in the original concept are *artwork placeholders*, not canon. They are removed from this mixed-mode build by cropping before the label row; the original source is preserved separately. The higher-resolution source is not a native Atari bitmap. No GitHub game-design decisions are changed by this proof of concept.

### Hardware references

- Atari *De Re Atari*, ANTIC display lists/pixel encoding: https://www.atarimania.com/8bit/files/De-Re-Atari.pdf
- Atari Screenbyter, ANTIC E width and 7,680-byte full bitmap: https://www.atarimagazines.com/compute/issue43/213_1_Atari_Screenbyter.php
- Palette color codes based on Lospec's Atari 8-Bit Family GTIA palette: https://lospec.com/palette-list/atari-8-bit-family-gtia
'''
(OUT/'README.md').write_text(README)

# Deliver one self-contained source image and technical package.
(SRC.parent/'gasblasters_screen1_800xl_preview.png').write_bytes((OUT/'screen1_mixed_mode_TV_preview.png').read_bytes())
(SRC.parent/'gasblasters_screen1_800xl_comparison.png').write_bytes((OUT/'screen1_800xl_comparison.png').read_bytes())
(SRC.parent/'gasblasters_screen1_800xl_mixed.xex').write_bytes((OUT/mixed_name).read_bytes())
archive=SRC.parent/'gasblasters_screen1_800xl_complete.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in OUT.iterdir():
  if p.is_file():z.write(p,'gasblasters_screen1_800xl/'+p.name)
 z.write(SRC,'gasblasters_screen1_800xl/'+SRC.name)
 z.write(Path(__file__),'gasblasters_screen1_800xl/'+Path(__file__).name)
print('QUOTE WRAP:',textlines)
print('MIXED PALETTES:',mixed_pals)
print('FULL PALETTES:',full_pals)
print('XEX files',[(n,(OUT/n).stat().st_size) for n in [mixed_name,full_name]])
print('ARCHIVE:',archive,archive.stat().st_size)
