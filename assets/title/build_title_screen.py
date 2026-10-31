#!/usr/bin/env python3
"""Gas Blasters '82 title screen ANTIC E/ANTIC 2 demonstration.
Native 160x160 illustration + 4 x 40-column Atari OS-font text rows.
Builds an Atari DOS segmented binary XEX for 64K Atari 800XL.
"""
from pathlib import Path
import numpy as np, cv2, json, struct, shutil, zipfile
from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageEnhance
R=Path(__file__).resolve().parent; R.mkdir(exist_ok=True)
SRC=R/'source_art_option3.png'
D=R/'native_assets';D.mkdir(exist_ok=True)
W,H=160,160
# Atari palette approximation (16 hues x 8 luminances, even low nibble GTIA values)
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
PAL=np.zeros((256,3),dtype=np.uint8)
for h,vals in enumerate(HUE_SHADES):
 for i,c in enumerate(vals):PAL[h*16+i*2]=tuple(bytes.fromhex(c));PAL[h*16+i*2+1]=tuple(bytes.fromhex(c))
(D/'approx_gtia_palette.act').write_bytes(PAL.tobytes())
# Remove the top and bottom black margins. Source copyright/menu line is replaced by native ANTIC 2 text below.
im=Image.open(SRC).convert('RGB')
print('source',im.size)
cropped=im.crop((0,108,im.width,664))
# Slight contrast enhancement at the actual pixel footprint to make the logo outlines/crisp shapes survive 4 colors.
small=cropped.resize((W,H),Image.Resampling.LANCZOS)
small=ImageEnhance.Contrast(small).enhance(1.10)
small.save(D/'title_prequant_160x160.png')
pixels=np.asarray(small)
CODES=np.array([i for i in range(0,256,2)],dtype=np.uint8)
LAB=cv2.cvtColor(PAL[CODES][None,:,:],cv2.COLOR_RGB2LAB)[0].astype(np.float32)
PIX_LAB=cv2.cvtColor(pixels,cv2.COLOR_RGB2LAB).astype(np.float32)
BAYER=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)
# Limit to four colors per 16 scanlines, including required black at index zero.
# Optimize palette in CIELAB with a little priority for saturated highlights (title/car/gas).
ids=np.empty((H,W),np.uint8);banks=[]
for k in range(10):
 a,b=k*16,(k+1)*16
 pix=PIX_LAB[a:b].reshape(-1,3)
 dif=((pix[:,None,:]-LAB[None,:,:])**2).sum(axis=2)
 current=dif[:,0].copy(); selected=[0]
 for _ in range(3):
  imp=np.maximum(current[:,None]-dif,0).sum(axis=0)
  imp[selected]=-1
  w=int(np.argmax(imp));selected.append(w); current=np.minimum(current,dif[:,w])
 selected=[0]+sorted(selected[1:],key=lambda idx:float(LAB[idx,0]))
 palette_lab=LAB[selected]
 yy,xx=np.mgrid[a:b,0:W]
 shifted=PIX_LAB[a:b].copy()
 shifted[:,:,0]+=((BAYER[yy%4,xx%4]-7.5)/7.5)*4.0
 err=((shifted[:,:,None,:]-palette_lab[None,None,:,:])**2).sum(axis=3)
 ids[a:b]=np.argmin(err,axis=2).astype(np.uint8)
 banks.append([int(CODES[i]) for i in selected])
assert ids.shape==(H,W) and ids.max()<=3
imgRGB=np.empty((H,W,3),np.uint8)
for i,c in enumerate(banks):imgRGB[i*16:(i+1)*16]=PAL[np.array(c,np.uint8)][ids[i*16:(i+1)*16]]
Image.fromarray(imgRGB).save(D/'title_antic_e_160x160_preview.png')
# For Atari E: each byte is 4 adjacent 2-bit pixels, hi to lo.
groups=ids.reshape(H,40,4)
bmp=((groups[:,:,0]<<6)|(groups[:,:,1]<<4)|(groups[:,:,2]<<2)|groups[:,:,3]).astype(np.uint8).tobytes()
assert len(bmp)==6400
(D/'title_antic_e_160x160.bin').write_bytes(bmp)
# 4 x 40-column rows under art (ANTIC 2, 8 raster scanlines per row)
# Use built-in Atari OS font at $E000: no external font file required.
lines=['','                1 PLAYER','              PRESS START','']
assert len(lines)==4 and all(len(x)<=40 for x in lines)
def ascii_to_screen(ch):
 code=ord(ch)
 assert 32<=code<=95
 return code-32 if code<=95 else code
screen=bytes(ascii_to_screen(c) for line in lines for c in line.ljust(40))
assert len(screen)==160
(D/'title_menu_40col_4rows.bin').write_bytes(screen)
# title palette: 10 art bands + 2 text bands. At mode 2 dark background/bright letters.
text_pal=[0x00,0x0a,0x0e,0x00]
allbanks=banks+[text_pal]*2
(D/'title_12_palette_bands.bin').write_bytes(bytes(c for row in allbanks for c in row))
(D/'title_palette_bands.json').write_text(json.dumps([{'scanlines':f'{i*16:03}-{(i+1)*16-1:03}','COLBK':f'${p[0]:02X}','COLPF0':f'${p[1]:02X}','COLPF1':f'${p[2]:02X}','COLPF2':f'${p[3]:02X}','rgb_approx':[list(map(int,PAL[v])) for v in p]} for i,p in enumerate(allbanks)],indent=2)+'\n')
DL=0x3C00;TEXT=0x6000
# 24 blank top lines, 160 ANTIC E scanlines, 4 ANTIC 2 rows, jumps at bottom.
dl=bytearray([0x70]*3)
for y in range(H):
 flag=0x80 if y%16==15 else 0
 if y==0:dl.extend([0x4E|flag,0,0x40])
 elif y==96:dl.extend([0x4E|flag,0,0x50])
 else:dl.append(0x0E|flag)
for row in range(4):
 flag=0x80 if row==1 else 0  # at bottom of text row 1 = scanline 176, not last row
 if row==0:dl.extend([0x42|flag,TEXT&255,TEXT>>8])
 else:dl.append(0x02|flag)
dl.extend([0x41,DL&255,DL>>8])
(D/'title_display_list.bin').write_bytes(dl)
# Validate 11 interrupts at scanlines 16..176 and 192 scanlines total.
progress=0;dli_marks=[];i=3
while i<len(dl)-3:
 inst=dl[i];i+=1
 assert (inst&0x0f) in [0x0e,0x02]
 if inst&0x40:i+=2
 progress+=(8 if inst&0x0f==2 else 1)
 if inst&0x80:dli_marks.append(progress)
assert progress==192 and dli_marks==list(range(16,192,16)),(progress,dli_marks)

# Built-in tiny 6502 assembly emitter for a standalone demo with functioning START acknowledgement.
class Asm:
 def __init__(self,base):self.base=base;self.b=bytearray();self.sym={};self.patch=[]
 def label(self,name):self.sym[name]=self.base+len(self.b)
 def raw(self,*xs):self.b.extend(xs)
 def lda_imm(self,v):self.raw(0xA9,v&255)
 def lda_abs(self,v):self.raw(0xAD,v&255,v>>8)
 def sta_abs(self,v):self.raw(0x8D,v&255,v>>8)
 def abs_ref(self,op,label):self.raw(op,0,0);self.patch.append((len(self.b)-2,'abs',label))
 def rel_ref(self,op,label):self.raw(op,0);self.patch.append((len(self.b)-1,'rel',label))
 def lda_x_ref(self,s):self.abs_ref(0xBD,s)
 def stx_ref(self,s):self.abs_ref(0x8E,s)
 def ldx_ref(self,s):self.abs_ref(0xAE,s)
 def jmp_ref(self,s):self.abs_ref(0x4C,s)
 def resolve(self):
  for index,kind,name in self.patch:
   target=self.sym[name]
   if kind=='abs':self.b[index:index+2]=struct.pack('<H',target)
   else:
    offset=target-(self.base+index+1)
    assert -128<=offset<=127,(name,offset)
    self.b[index]=offset&0xff
  return bytes(self.b)
A=Asm(0x2000)
A.label('RUN')
A.raw(0x78) # SEI
A.lda_imm(0); A.sta_abs(0xD40E);A.sta_abs(0x022F) # NMIs and display DMA off
A.lda_imm(0);dli_lo=len(A.b)-1;A.sta_abs(0x0200)
A.lda_imm(0);dli_hi=len(A.b)-1;A.sta_abs(0x0201)
A.lda_imm(DL&255);A.sta_abs(0x0230)
A.lda_imm(DL>>8);A.sta_abs(0x0231)
A.lda_imm(0xE0);A.sta_abs(0x02F4)  # OS built-in font at $E000; CHBAS shadow
A.lda_imm(0);A.sta_abs(0x026F) # PRIOR
for val,shadow in zip(allbanks[0],[0x02C8,0x02C4,0x02C5,0x02C6]):
 A.lda_imm(val);A.sta_abs(shadow)
A.lda_imm(0x22);A.sta_abs(0x022F) # SDMCTL enabled narrow? $22 normal width (yes)
A.lda_imm(0xC0);A.sta_abs(0xD40E) # NMIEN DLI+VBI
A.raw(0x58) # CLI
# Poll START bit0 of console keyboard at $D01F (active low).
A.label('POLL_START');A.lda_abs(0xD01F);A.raw(0x29,0x01) # AND #1
A.rel_ref(0xD0,'POLL_START') # BNE if START not pressed
# Once pressed, write a full new message row, using ZP-not-needed indexed absolute store.
A.raw(0xA2,0x00) # LDX #0
A.label('COPY_STATUS')
A.lda_x_ref('STATUS_MSG')
A.raw(0x9D,(TEXT+2*40)&255,(TEXT+2*40)>>8) # STA $6050,X
A.raw(0xE8) # INX
A.raw(0xE0,40) # CPX #40
A.rel_ref(0xD0,'COPY_STATUS')
A.label('HOLD');A.jmp_ref('HOLD')
# DLI: save A,X,Y, WSYNC, registers for next band. 11 DLIs always.
A.label('DLI');A.raw(0x48,0x8A,0x48,0x98,0x48)
A.ldx_ref('DLI_INDEX')
A.lda_imm(0);A.sta_abs(0xD40A)
for reg,addr in [('C_BK',0xD01A),('C_PF0',0xD016),('C_PF1',0xD017),('C_PF2',0xD018)]:
 A.lda_x_ref(reg);A.sta_abs(addr)
A.raw(0xE8,0xE0,11) # INX / CPX #11
A.rel_ref(0x90,'DLI_INDEX_OK')
A.raw(0xA2,0x00)
A.label('DLI_INDEX_OK');A.stx_ref('DLI_INDEX')
A.raw(0x68,0xA8,0x68,0xAA,0x68,0x40) # restore and RTI
A.label('DLI_INDEX');A.raw(0)
for j,name in enumerate(['C_BK','C_PF0','C_PF1','C_PF2']):
 A.label(name);A.raw(*[p[j] for p in allbanks[1:]])
status='START PRESSED'
statusrow=status.center(40)
A.label('STATUS_MSG');A.raw(*[ascii_to_screen(c) for c in statusrow])
code=bytearray(A.resolve());code[dli_lo]=A.sym['DLI']&0xff;code[dli_hi]=A.sym['DLI']>>8
(D/'title_loader_6502.bin').write_bytes(code)
# segment loader; all payloads within stock XL 64K and no overlaps
segs=[(0x2000,bytes(code)),(DL,bytes(dl)),(0x4000,bmp[:96*40]),(0x5000,bmp[96*40:]),(TEXT,screen),(0x02E0,struct.pack('<H',0x2000))]
for i,(a,p) in enumerate(segs):
 assert a+len(p)-1<0xC000
 for x,q in segs[:i]:assert a+len(p)<=x or x+len(q)<=a,(hex(a),hex(x))
def segment(addr,p):return struct.pack('<HH',addr,addr+len(p)-1)+p
exe=b'\xFF\xFF'+b''.join(segment(a,p) for a,p in segs)
xex=R/'GasBlasters82_Title_Option3_ANTIC_E.xex';xex.write_bytes(exe)
# visual preview from actual packed 2bpp and palette color bands
raw=np.frombuffer(bmp,dtype=np.uint8).reshape(H,40)
back=np.empty((H,W),np.uint8)
back[:,0::4]=raw>>6
back[:,1::4]=(raw>>4)&3
back[:,2::4]=(raw>>2)&3
back[:,3::4]=raw&3
assert np.array_equal(back,ids)
# approximate caption using terminal mono font. Native ROM glyph differs from this simulated text.
clock=np.repeat(imgRGB,2,axis=1)
canvas=Image.fromarray(np.vstack([clock,np.zeros((32,320,3),np.uint8)]))
drw=ImageDraw.Draw(canvas)
fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
font=ImageFont.truetype(fontfile,8)
for row,line in enumerate(lines):
 for col,ch in enumerate(line.ljust(40)):
  if ch!=' ':drw.text((col*8,row*8+160-2),ch,font=font,fill=(238,238,238))
canvas.resize((960,720),Image.Resampling.NEAREST).save(R/'GasBlasters82_Title_Option3_Preview.png')
manifest={
 'title':'Gas Blasters 82 title screen Option 3','target':'Atari 800XL 64KB',
 'source_art':'source_art_option3.png',
 'display':{'mode':'ANTIC E 160x160 bitmap plus ANTIC mode 2 four 40-column rows','scanlines':192,'bitmap_bytes':len(bmp),'text_bytes':len(screen),'bands':len(allbanks),'dlis':len(dli_marks)},
 'memory':{'code':f'${0x2000:04X}','display_list':f'${DL:04X}','bitmap_first':'$4000-$4EFF','bitmap_second':'$5000-$59FF','text':'$6000-$609F','OS_charset':'$E000','RUNAD':'$02E0'},
 'start_behavior':'Actual START key console input (D01F bit0 active low) changes PRESS START to START PRESSED; this demo does not transition to Meet the Crew.',
 'status':'XEX structure and ANTIC data validated programmatically; not yet run in emulator.'}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
readme="""# Gas Blasters '82 - Title Screen Option 3

Target: Stock Atari 800XL with 64 KB; Atari DOS 2 segmented binary-load XEX.

The selected Option 3 image is converted into a genuine ANTIC E bitmap (160 x 160, 2bpp, 6,400 bytes) followed by 4 rows of ANTIC 2 40-column text (32 raster lines). The program uses 12 sixteen-line palette banks with 11 display-list interrupts. The built-in OS character ROM at $E000 is used for the menu text; no font files are included or required.

## Test

Load `GasBlasters82_Title_Option3_ANTIC_E.xex` into Atari800 or Altirra configured as 800XL (64 KB). The visual menu says `1 PLAYER` and `PRESS START`. Press the Atari console START key (often mapped to F4 in emulators, depending on settings); the prompt will change to `START PRESSED`. The program then holds this screen. It does not yet load the Meet the Crew screen or start the game.

## Build

Install Pillow, numpy and opencv-python, then run `python build_title_screen.py`. The script stores the generated bitmap, palette, display list, and 6502 loader in `native_assets` and rebuilds the XEX. It reads `source_art_option3.png` (included).

## Notes

- The artwork has to be reduced to a maximum of 4 color indices per scanline (actual GTIA colors vary per 16 scanlines). Fine details may be lost, particularly small lettering.
- The source illustration includes a fictional 1982 copyright line, which is not carried over into the executable.
- This is a standalone hardware-format demonstration, not game integration. The visual palette preview is approximate; use the emulator test to evaluate artwork legibility, START console mapping and screen behavior.
"""
(R/'README.md').write_text(readme)
print('XEX',len(exe),'code',len(code),'DL',len(dl),'bmp',len(bmp),'palette',len(allbanks),'DLI',dli_marks)
print('loader symbols', {k:hex(v) for k,v in A.sym.items() if k in ['RUN','POLL_START','DLI','DLI_INDEX','STATUS_MSG']})
# Work package with build script, source, generated data and XEX
with zipfile.ZipFile(R/'GasBlasters82_Title_Option3_Build_Package.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for file in R.rglob('*'):
  if file.is_file() and file.suffix!='.zip':z.write(file,file.relative_to(R).as_posix())
print('package', (R/'GasBlasters82_Title_Option3_Build_Package.zip').stat().st_size)
