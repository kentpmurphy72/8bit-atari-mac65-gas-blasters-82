#!/usr/bin/env python3
from pathlib import Path
import numpy as np, cv2, json, zipfile, struct
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent.parent/'assets'/'arrival'
SRC=ROOT/'source_art_original.png'
OUT=ROOT/'generated_atari_assets'
OUT.mkdir(exist_ok=True)
W=160; FULL_H=192; ART_H=128; ROWS=8
BANDS=12; BAND_H=16

# Approximate GTIA preview palette
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
print('Input:', IM.size)
# Full pure-bitmap version: direct resize to native display size for comparison.
source_full=np.asarray(IM.resize((W,FULL_H), Image.Resampling.LANCZOS))
# Recommended mixed mode: fit/crop gently to 160x128, preserving group and restaurant.
source_art=np.asarray(ImageOps.fit(IM, (W,ART_H), method=Image.Resampling.LANCZOS, centering=(0.52,0.48)))
Image.fromarray(source_art).save(OUT/'arrival_source_cropped_for_mixed_160x128.png')

CODES=np.array([x for x in range(256) if (x&1)==0],dtype=np.uint8)
RGB=PAL[CODES]
LAB=cv2.cvtColor(RGB[None,:,:],cv2.COLOR_RGB2LAB)[0].astype(np.float32)
BG_INDEX=int(np.where(CODES==0)[0][0])
BAYER=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)

def quantize(img, band_count):
    ids=np.zeros(img.shape[:2],dtype=np.uint8)
    pals=[]
    for k in range(band_count):
        ymin=k*16; ymax=min(img.shape[0],ymin+16)
        subset=img[ymin:ymax].copy()
        pix=cv2.cvtColor(subset,cv2.COLOR_RGB2LAB).reshape(-1,3).astype(np.float32)
        diff=((pix[:,None,:]-LAB[None,:,:])**2).sum(axis=2)
        current=diff[:,BG_INDEX].copy()
        selected=[BG_INDEX]
        for _ in range(3):
            improve=np.maximum(current[:,None]-diff,0).sum(axis=0)
            improve[selected]=-1
            winner=int(np.argmax(improve))
            selected.append(winner)
            current=np.minimum(current,diff[:,winner])
        chosen=[BG_INDEX]+sorted(selected[1:], key=lambda i: float(LAB[i,0]))
        palette_lab=LAB[chosen]
        yy,xx=np.mgrid[ymin:ymax,0:img.shape[1]]
        extra=((BAYER[yy%4,xx%4]-7.5)/7.5)*5.0
        shifted=cv2.cvtColor(subset,cv2.COLOR_RGB2LAB).astype(np.float32)
        shifted[:,:,0]+=extra
        dist=((shifted[:,:,None,:]-palette_lab[None,None,:,:])**2).sum(axis=3)
        ids[ymin:ymax]=np.argmin(dist,axis=2).astype(np.uint8)
        pals.append([int(CODES[n]) for n in chosen])
    preview=np.empty((img.shape[0],img.shape[1],3),dtype=np.uint8)
    for i,p in enumerate(pals):
        a=i*16; b=min((i+1)*16,img.shape[0]); preview[a:b]=PAL[np.array(p,dtype=np.uint8)][ids[a:b]]
    return ids,pals,preview

full_ids, full_pals, full_rgb=quantize(source_full,12)
art_ids, art_pals, art_rgb=quantize(source_art,8)
caption_palette=[0x00,0x0a,0x0e,0x00]
mixed_pals=art_pals+[caption_palette]*4

def pack4(pixel_ids):
    b=pixel_ids.reshape(pixel_ids.shape[0],40,4).astype(np.uint8)
    return ((b[:,:,0]<<6)|(b[:,:,1]<<4)|(b[:,:,2]<<2)|b[:,:,3]).tobytes()

def unpack4(binary,height):
    b=np.frombuffer(binary,dtype=np.uint8).reshape(height,40)
    return np.stack([b>>6,(b>>4)&3,(b>>2)&3,b&3],axis=-1).reshape(height,160)&3

full_dat=pack4(full_ids); art_dat=pack4(art_ids)
assert len(full_dat)==7680 and len(art_dat)==5120
assert np.array_equal(unpack4(full_dat,192),full_ids)
assert np.array_equal(unpack4(art_dat,128),art_ids)
(OUT/'arrival_full_160x192_antic_e.bin').write_bytes(full_dat)
(OUT/'arrival_mixed_art_160x128_antic_e.bin').write_bytes(art_dat)
Image.fromarray(full_rgb).save(OUT/'arrival_full_160x192_4colors_per_band.png')
Image.fromarray(art_rgb).save(OUT/'arrival_mixed_art_160x128_4colors_per_band.png')

story_lines=[
    'Billy came for a killer burrito.',
    'The beans came with a warning.',
    'Nobody read it. Especially Billy.'
]
assert [len(x) for x in story_lines]==[32,30,33]
# 8 rows: top blank; centered heading; blank; 3 flush-left story lines;
# blank; centered visual prompt. Keep 4-column left margin for the story.
textlines=[
    '',
    'ARRIVING AT TACO SMELL'.center(40),
    '',
    *['    '+line for line in story_lines],
    '',
    'FIRE TO CONTINUE >'.center(40),
]
assert len(textlines)==ROWS and all(len(x)<=40 for x in textlines)
textcells=b''.join(bytes([(ord(ch)-32) if 32<=ord(ch)<=95 else ord(ch) for ch in line.ljust(40)]) for line in textlines)
assert len(textcells)==40*ROWS
(OUT/'arrival_40col_text_8rows.bin').write_bytes(textcells)

font_candidates=['/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf']
fontfile=next((x for x in font_candidates if Path(x).exists()),None)
if not fontfile: raise RuntimeError('No font available')
font=ImageFont.truetype(fontfile,8)
char_bytes=bytearray(1024)
for ascii_code in range(32,127):
    ch=chr(ascii_code)
    screen_code=(ascii_code-32) if ascii_code<=95 else ascii_code
    glyph=Image.new('1',(8,8),0); dr=ImageDraw.Draw(glyph)
    dr.text((1,-2), ch, font=font, fill=1)
    arr=np.asarray(glyph,dtype=np.uint8)
    for y in range(8):
        v=0
        for x in range(8): v=(v<<1)|int(arr[y,x]!=0)
        char_bytes[screen_code*8+y]=v
(OUT/'arrival_custom_charset_1kb.bin').write_bytes(char_bytes)

artclock=np.repeat(art_rgb,2,axis=1)
captionclock=np.empty((ROWS*8,320,3),np.uint8); captionclock[:]=PAL[0x00]
for row in range(ROWS):
    for col in range(40):
        ch=textcells[row*40+col]
        glyph=char_bytes[ch*8:ch*8+8]
        for yy,v in enumerate(glyph):
            for xx in range(8):
                if v&(0x80>>xx): captionclock[row*8+yy,col*8+xx]=PAL[0x0e]
mixedclock=np.vstack([artclock,captionclock]); assert mixedclock.shape==(192,320,3)
Image.fromarray(mixedclock).resize((960,720),Image.Resampling.NEAREST).save(OUT/'arrival_mixed_mode_TV_preview.png')
Image.fromarray(np.repeat(full_rgb,2,axis=1)).resize((960,720),Image.Resampling.NEAREST).save(OUT/'arrival_full_mode_TV_preview.png')
comp=Image.new('RGB',(1920,760),'#15151b')
comp.paste(Image.open(OUT/'arrival_full_mode_TV_preview.png'),(0,36))
comp.paste(Image.open(OUT/'arrival_mixed_mode_TV_preview.png'),(960,36))
d=ImageDraw.Draw(comp); ft=ImageFont.truetype(fontfile,20)
d.text((40,4),'FULL BITMAP  -  ALL 160 x 192',font=ft,fill='#e6e6e6')
d.text((1000,4),'RECOMMENDED  -  160 x 128 ART + 8 TEXT ROWS',font=ft,fill='#e6e6e6')
comp.save(OUT/'arrival_800xl_comparison.png')

# palette exports
regtable=lambda pals: bytes(v for row in pals for v in row)
(OUT/'arrival_mixed_gtia_12bands_48bytes.bin').write_bytes(regtable(mixed_pals))
(OUT/'arrival_full_gtia_12bands_48bytes.bin').write_bytes(regtable(full_pals))
for name,p in [('mixed',mixed_pals),('full',full_pals)]:
    (OUT/f'arrival_{name}_palettes.json').write_text(json.dumps([
        {'scanlines':f'{i*16}-{(i+1)*16-1}','COLBK':f'${c[0]:02X}','COLPF0':f'${c[1]:02X}','COLPF1':f'${c[2]:02X}','COLPF2':f'${c[3]:02X}','preview_rgb':[list(map(int,PAL[v])) for v in c]}
        for i,c in enumerate(p)
    ], indent=2)+'\n')

DL_ADDR=0x3C00; CODE_ADDR=0x2000

def build_display_list(mixed):
    out=bytearray([0x70,0x70,0x70])
    height=128 if mixed else 192
    for y in range(height):
        flag=0x80 if y%16==15 and y!=191 else 0
        if y==0: out += bytes([0x4e|flag,0x00,0x40])
        elif y==96: out += bytes([0x4e|flag,0x00,0x50])
        else: out.append(0x0e|flag)
    if mixed:
        for row in range(ROWS):
            flag=0x80 if row in (1,3,5) else 0
            if row==0: out += bytes([0x42|flag,0x00,0x58])
            else: out.append(0x02|flag)
    out += bytes([0x41,DL_ADDR&255,DL_ADDR>>8])
    return bytes(out)

class Asm:
    def __init__(self,base=0x2000): self.b=bytearray(); self.base=base; self.labels={}; self.patch=[]
    def here(self): return self.base+len(self.b)
    def label(self,name): self.labels[name]=self.here()
    def byte(self,*a): self.b.extend(a)
    def imm(self,v): self.byte(0xA9,v&255)
    def sta(self,addr): self.byte(0x8D,addr&255,(addr>>8)&255)
    def ldx(self,ref): self.byte(0xAE,0,0); self.patch.append((len(self.b)-2,'abs',ref))
    def stx(self,ref): self.byte(0x8E,0,0); self.patch.append((len(self.b)-2,'abs',ref))
    def lda_x(self,ref): self.byte(0xBD,0,0); self.patch.append((len(self.b)-2,'abs',ref))
    def jmp(self,ref): self.byte(0x4C,0,0); self.patch.append((len(self.b)-2,'abs',ref))
    def bcc(self,ref): self.byte(0x90,0); self.patch.append((len(self.b)-1,'rel',ref))
    def finish(self):
        for i,mode,ref in self.patch:
            target=self.labels[ref]
            if mode=='abs': self.b[i]=target&255; self.b[i+1]=target>>8
            else:
                offset=target-(self.base+i+1)
                if not -128<=offset<=127: raise ValueError('relative offset')
                self.b[i]=offset&255
        return bytes(self.b)


def build_code(pals):
    asm=Asm(CODE_ADDR)
    asm.label('START')
    asm.byte(0x78)
    asm.imm(0x00); asm.sta(0xD40E); asm.sta(0x022F)
    asm.imm(0); lo_pos=len(asm.b)-1; asm.sta(0x0200)
    asm.imm(0); hi_pos=len(asm.b)-1; asm.sta(0x0201)
    asm.imm(DL_ADDR&255); asm.sta(0x0230)
    asm.imm(DL_ADDR>>8); asm.sta(0x0231)
    asm.imm(0x60); asm.sta(0x02F4)
    asm.imm(0); asm.sta(0x026F)
    for val,shadow in zip(pals[0],[0x02C8,0x02C4,0x02C5,0x02C6]):
        asm.imm(val); asm.sta(shadow)
    asm.imm(0x22); asm.sta(0x022F)
    asm.imm(0xC0); asm.sta(0xD40E)
    asm.byte(0x58)
    asm.label('IDLE'); asm.jmp('IDLE')
    asm.label('DLI')
    asm.byte(0x48,0x8A,0x48,0x98,0x48)
    asm.ldx('INDEX')
    asm.byte(0xA9,0x00); asm.sta(0xD40A)
    for arr,hw in [('BGT',0xD01A),('P0T',0xD016),('P1T',0xD017),('P2T',0xD018)]:
        asm.lda_x(arr); asm.sta(hw)
    asm.byte(0xE8)
    asm.byte(0xE0,0x0B)
    asm.bcc('SKIP_RESET')
    asm.byte(0xA2,0x00)
    asm.label('SKIP_RESET'); asm.stx('INDEX')
    asm.byte(0x68,0xA8,0x68,0xAA,0x68,0x40)
    asm.label('INDEX'); asm.byte(0)
    for index,name in enumerate(['BGT','P0T','P1T','P2T']):
        asm.label(name); asm.byte(*[p[index] for p in pals[1:]])
    code=bytearray(asm.finish()); code[lo_pos]=asm.labels['DLI']&255; code[hi_pos]=asm.labels['DLI']>>8
    return bytes(code), asm.labels

def seg(start,data):
    end=start+len(data)-1
    return struct.pack('<HH',start,end)+data

def xex_build(mixed):
    pals=mixed_pals if mixed else full_pals
    bits=art_dat if mixed else full_dat
    dis=build_display_list(mixed)
    code,labels=build_code(pals)
    out=bytearray(b'\xff\xff')
    out+=seg(0x2000,code)
    out+=seg(DL_ADDR,dis)
    out+=seg(0x4000,bits[:96*40])
    out+=seg(0x5000,bits[96*40:])
    if mixed: out+=seg(0x5800,textcells)
    out+=seg(0x6000,char_bytes)
    out+=seg(0x02E0,struct.pack('<H',0x2000))
    name='arrival_800xl_mixed_40col.xex' if mixed else 'arrival_800xl_full_bitmap.xex'
    (OUT/name).write_bytes(out)
    (OUT/('arrival_mixed_display_list.bin' if mixed else 'arrival_full_display_list.bin')).write_bytes(dis)
    return name,dis

mixed_name,mixed_dl=xex_build(True)
full_name,full_dl=xex_build(False)
# sanity check DLI boundaries
for mixed,dl in [(True,mixed_dl),(False,full_dl)]:
    y=0; ints=[]; i=3
    while i<len(dl)-3:
        mode=dl[i]; i+=1
        if (mode&15) not in (0x0E,0x02): raise ValueError('bad mode')
        if mode&0x40: i+=2
        h=8 if (mode&15)==2 else 1
        y+=h
        if mode&0x80: ints.append(y)
    expected=list(range(16,192,16)); assert y==192 and ints==expected, (mixed,y,ints,expected)

manifest={
  'source':SRC.name,
  'mixed':{'art_dimensions':[160,128],'art_bytes':5120,'text_columns':40,'text_rows':ROWS,'text_bytes':40*ROWS,'custom_font_bytes':1024,'mode':'ANTIC E + ANTIC 2','palette_bands':12,'dlis':11},
  'full':{'dimensions':[160,192],'bytes':7680,'mode':'ANTIC E','palette_bands':12,'dlis':11},
  'memory':{'code':'$2000','display_list':'$3C00','bitmap_0':'$4000-$4EFF','bitmap_1':'$5000-$54FF (mixed) / $5000-$5EFF (full)','text':'$5800','font':'$6000','run_vector':'$02E0'},
  'note':'Generated and structurally validated; emulator test still needed.'
}
(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
README=f'''# Gas Blasters \'82 — Arrival Screen / Atari 800XL proof of concept

**Source:** `{SRC.name}` (selected Taco Smell arrival concept).
**Target:** stock 64 KB Atari 800XL. **Status:** structurally validated XEX package; emulator test still needed.

## Included outputs
- `{mixed_name}` — recommended XEX: 160x128 ANTIC E art plus 8 rows of 40-column text.
- `{full_name}` — full-screen 160x192 ANTIC E bitmap.
- `arrival_mixed_mode_TV_preview.png` — enlarged preview of recommended version.
- `arrival_full_mode_TV_preview.png` — enlarged preview of full-bitmap version.
- `arrival_800xl_comparison.png` — side-by-side comparison.

## Scene
Five friends walk from their parked car toward the Taco Smell entrance at sunset. The mixed version adds **ARRIVING AT TACO SMELL**, the approved three-line burrito/beans joke, and a visual **FIRE TO CONTINUE >** prompt.

## Technical notes
- ANTIC E art uses 2bpp / 40 bytes per line.
- 12 total 16-scanline palette bands, 11 DLI boundaries.
- Mixed version uses 8 art bands (128 scanlines) + 4 ANTIC 2 text bands (64 scanlines).
- XEX contains code at $2000, display list at $3C00, bitmap at $4000/$5000, text at $5800, font at $6000.
- FIRE TO CONTINUE is visual only in this proof of concept.
'''
(OUT/'README.md').write_text(README+'\n## Story text (exact three-line version)\n\n'+chr(10).join(story_lines)+'\n\nAll text lines fit a 40-column display. The Fire prompt is visual only.\n')
# convenience copies
(ROOT/'GasBlasters82_Arrival_preview.png').write_bytes((OUT/'arrival_mixed_mode_TV_preview.png').read_bytes())
(ROOT/'GasBlasters82_Arrival_comparison.png').write_bytes((OUT/'arrival_800xl_comparison.png').read_bytes())
(ROOT/'GasBlasters82_Arrival_ANTIC_E_Mixed.xex').write_bytes((OUT/mixed_name).read_bytes())
(ROOT/'GasBlasters82_Arrival_ANTIC_E_FullBitmap.xex').write_bytes((OUT/full_name).read_bytes())
with zipfile.ZipFile(ROOT/'GasBlasters82_Arrival_build_package.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in OUT.iterdir():
        if p.is_file(): z.write(p,'GasBlasters82_ArrivalScreen/'+p.name)
    z.write(SRC,'GasBlasters82_ArrivalScreen/'+SRC.name)
    z.write(Path(__file__),'GasBlasters82_ArrivalScreen/'+Path(__file__).name)
print('built', mixed_name, full_name)
