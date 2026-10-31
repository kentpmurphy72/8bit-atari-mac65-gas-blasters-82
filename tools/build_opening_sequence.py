#!/usr/bin/env python3
"""Create Gas Blasters '82 integrated three-screen NTSC Atari 800XL opening.

Offline build dependency: Python 3 standard library only.
Reads the known-good standalone XEX artwork/text assets and POKEY register streams
already tracked in GitHub.  The generated 6502 game shell runs on the Atari; Python
is only an offline build tool.

Memory (all below $A000; no BASIC RAM assumed):
  $2000-$27FF    unified 6502 scene controller, POKEY, DLI
  $2A00-$2FFF    Arcade Rock register streams (channel-major 8x192)
  $3000-$33FF    Funky Gas Attack register streams (8x128)
  $3500-$359F    three 12x4 GTIA band palette tables
  $3800-$3BFF    same custom 1 KiB font used by both cutscenes
  $3C00-$3CFF    title ANTIC display list
  $3D00-$3DFF    crew ANTIC display list
  $3E00-$3EFF    arrival ANTIC display list
  $3F00-$3FFF    Stage 1 temporary text display list
  $4000/$5000   title image, 160x160 ANTIC E
  $5A00          title screen 40-column caption
  $6000/$7000   crew image, 160x128 ANTIC E
  $7600          crew 40-column text
  $8000/$9000   arrival image, 160x128 ANTIC E
  $9600          arrival 40-column text
  $9800          40-column stage 1 placeholder text

Original pictures remain pixel/byte-identical; display lists point at relocated art.
DLI color bands copy exactly the original 4 bytes per group per scene.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / 'assets' / 'opening'
ADDR = dict(TITLE_BITMAP1=0x4000, TITLE_BITMAP2=0x5000, TITLE_TEXT=0x5A00,
            CREW_BITMAP1=0x6000, CREW_BITMAP2=0x7000, CREW_TEXT=0x7600,
            ARRIVAL_BITMAP1=0x8000, ARRIVAL_BITMAP2=0x9000, ARRIVAL_TEXT=0x9600,
            STAGE_TEXT=0x9800, FONT=0x3800,
            DL_TITLE=0x3C00, DL_CREW=0x3D00, DL_ARRIVAL=0x3E00, DL_STAGE=0x3F00,
            MUSIC_ROCK=0x2A00, MUSIC_FUNK=0x3000, PAL_TITLE=0x3500,
            PAL_CREW=0x3530, PAL_ARRIVAL=0x3560)


def xex_segments(path):
    b = Path(path).read_bytes()
    if b[:2] != b'\xff\xff': raise ValueError(f'{path}: missing XEX header')
    i=2; segs={}
    while i < len(b):
        if b[i:i+2] == b'\xff\xff': i+=2;continue
        if i+4>len(b):raise ValueError('truncated segment')
        start,end=struct.unpack_from('<HH',b,i);i+=4
        if end<start or i+end-start+1>len(b):raise ValueError('bad XEX segment')
        if start in segs:raise ValueError('duplicate segment')
        segs[start]=bytes(b[i:i+end-start+1]);i+=end-start+1
    return segs


def encode_xex(parts):
    items=sorted((a,bytes(v)) for a,v in parts.items())
    out=bytearray(b'\xff\xff')
    for i,(start,data) in enumerate(items):
        assert data and 0 <= start <= start+len(data)-1 <=0xFFFF
        if i:
            p,q=items[i-1]
            assert p+len(q)<=start, f'overlap ${p:04X}-${p+len(q)-1:04X} with ${start:04X}'
        out+=struct.pack('<HH',start,start+len(data)-1)+data
    return bytes(out)


class Asm:
    """Small deterministic 6502 byte emitter with validated labels/branches."""
    def __init__(self,base=0x2000):
        self.base=base;self.buf=bytearray();self.labels={};self.patches=[];self.asm=[]
    def label(self,label):
        assert label not in self.labels
        self.labels[label]=self.base+len(self.buf);self.asm.append(f'{label}:')
    def op(self,text,*bytes_):self.buf.extend(bytes_);self.asm.append('    '+text)
    def imm(self,name,op,n): self.op(f'{name} #${n&255:02X}',op,n&255)
    def abs(self,name,op,addr):self.op(f'{name} ${addr:04X}',op,addr&255,addr>>8)
    def zp(self,name,op,addr):self.op(f'{name} ${addr:02X}',op,addr)
    def ref(self,name,op,label,idx=False):
        self.op(f'{name} {label}'+(',X' if idx else ''),op,0,0)
        self.patches.append((len(self.buf)-2,label,'abs'))
    def branch(self,name,op,label):
        self.op(f'{name} {label}',op,0);self.patches.append((len(self.buf)-1,label,'relative'))
    def byte(self,label,*values):self.label(label);self.op('.BYTE '+','.join(f'${x:02X}' for x in values),*values)
    def finalize(self):
        for offset,label,kind in self.patches:
            addr=self.labels[label]
            if kind=='abs':self.buf[offset:offset+2]=struct.pack('<H',addr)
            else:
                rel=addr-(self.base+offset+1)
                if not -128<=rel<=127: raise ValueError(f'relative branch to {label}: {rel}')
                self.buf[offset]=rel&255
        if len(self.buf)>0x800:raise ValueError(f'controller exceeds memory budget: {len(self.buf)}')
        return bytes(self.buf)


def assemble_controller(initial_palettes):
    a=Asm()
    # mutable state, placed after executable by label; no fixed ZP except OS RTCLOK $14
    S=lambda k,op,l:a.ref(k,op,l)
    def LDA(k):S('LDA',0xAD,k)
    def STA(k):S('STA',0x8D,k)
    def JSR(k):S('JSR',0x20,k)
    def JMP(k):S('JMP',0x4C,k)
    def branch(k,opcode,label):a.branch(k,opcode,label)
    a.label('STARTUP')
    a.op('SEI',0x78)
    a.imm('LDA',0xA9,0)
    a.abs('STA',0x8D,0xD40E)  # disable display interrupts during initial setup
    a.abs('STA',0x8D,0xD208)  # POKEY 64 kHz clock, four channels
    a.imm('LDA',0xA9,3)
    a.abs('STA',0x8D,0xD20F)  # SKCTL = normal
    a.imm('LDA',0xA9,0)
    STA('SCENE')
    STA('TRACK')
    STA('ARMED')
    STA('DLI_POS')
    a.zp('LDA',0xA5,0x14)
    STA('FRAME_OLD')
    JSR('SET_SCENE')
    JSR('RESTART_MUSIC')
    a.op('CLI',0x58)
    a.label('FRAME_WAIT')
    a.zp('LDA',0xA5,0x14) # RTCLOK low, OS VBI counter
    S('CMP',0xCD,'FRAME_OLD')
    branch('BEQ',0xF0,'FRAME_WAIT')
    STA('FRAME_OLD')
    JSR('MUSIC_FRAME')
    JSR('HANDLE_INPUT')
    JMP('FRAME_WAIT')

    # Handle START for title and placeholder, FIRE (TRIG0) for both cutscenes.
    # ARMED becomes true only after relevant key was released for at least one frame.
    a.label('HANDLE_INPUT')
    LDA('SCENE')
    branch('BEQ',0xF0,'CHECK_START')
    a.imm('CMP',0xC9,3)
    branch('BEQ',0xF0,'CHECK_START')
    a.abs('LDA',0xAD,0xD010) # TRIG0 bit0 active low
    a.imm('AND',0x29,1)
    JMP('KEY_STATE')
    a.label('CHECK_START')
    a.abs('LDA',0xAD,0xD01F) # CONSOL bit0 active low for START
    a.imm('AND',0x29,1)
    a.label('KEY_STATE')
    branch('BEQ',0xF0,'BUTTON_DOWN')
    a.imm('LDA',0xA9,1)
    STA('ARMED')
    a.op('RTS',0x60)
    a.label('BUTTON_DOWN')
    LDA('ARMED')
    branch('BEQ',0xF0,'BUTTON_DONE')
    a.imm('LDA',0xA9,0)
    STA('ARMED')
    LDA('SCENE')
    a.imm('CMP',0xC9,3)
    branch('BEQ',0xF0,'START_OVER')
    a.op('CLC',0x18)
    a.imm('ADC',0x69,1)
    STA('SCENE')
    a.imm('CMP',0xC9,1)
    branch('BEQ',0xF0,'START_FUNK')
    a.imm('CMP',0xC9,3)
    branch('BEQ',0xF0,'STOP_MUSIC')
    # scene == 2: preserve Funk phase and existing notes
    JSR('SET_SCENE')
    a.op('RTS',0x60)
    a.label('START_FUNK')
    a.imm('LDA',0xA9,1)
    STA('TRACK')
    JSR('SET_SCENE')
    JSR('RESTART_MUSIC')
    a.op('RTS',0x60)
    a.label('STOP_MUSIC')
    a.imm('LDA',0xA9,2)
    STA('TRACK')
    JSR('SILENCE')
    JSR('SET_SCENE')
    a.op('RTS',0x60)
    a.label('START_OVER')
    a.imm('LDA',0xA9,0)
    STA('SCENE')
    STA('TRACK')
    JSR('SET_SCENE')
    JSR('RESTART_MUSIC')
    a.label('BUTTON_DONE')
    a.op('RTS',0x60)

    # Scene configuration is atomic w.r.t. NMI (interrupt vector and display list).
    a.label('SET_SCENE')
    a.imm('LDA',0xA9,0)
    a.abs('STA',0x8D,0xD40E)  # NMIEN off
    STA('DLI_POS')
    a.imm('LDA',0xA9,0x22)
    a.abs('STA',0x8D,0x22F) # SDMCTL normal playfield DMA
    a.abs('STA',0x8D,0xD400)
    a.ref('LDA',0xAD,'DLI_VECTOR_LO') # constant byte stored after code
    a.abs('STA',0x8D,0x200)
    a.ref('LDA',0xAD,'DLI_VECTOR_HI')
    a.abs('STA',0x8D,0x201)
    # leave OS VBI active for frame clock and palette shadows
    LDA('SCENE')
    branch('BEQ',0xF0,'TO_TITLE')
    a.imm('CMP',0xC9,1)
    branch('BEQ',0xF0,'TO_CREW')
    a.imm('CMP',0xC9,2)
    branch('BEQ',0xF0,'TO_ARRIVAL')
    JMP('DRAW_STAGE')
    a.label('TO_TITLE')
    JMP('DRAW_TITLE')
    a.label('TO_CREW')
    JMP('DRAW_CREW')
    a.label('TO_ARRIVAL')
    JMP('DRAW_ARRIVAL')

    def load_dl(label,addr,font,top_bg,pf0,pf1,pf2):
        a.label(label)
        a.imm('LDA',0xA9,addr&255);a.abs('STA',0x8D,0x230);a.abs('STA',0x8D,0xD402)
        a.imm('LDA',0xA9,addr>>8);a.abs('STA',0x8D,0x231);a.abs('STA',0x8D,0xD403)
        a.imm('LDA',0xA9,font);a.abs('STA',0x8D,0x2F4);a.abs('STA',0x8D,0xD409)
        for shadow,hw,n in [(0x2C8,0xD01A,top_bg),(0x2C4,0xD016,pf0),(0x2C5,0xD017,pf1),(0x2C6,0xD018,pf2)]:
            a.imm('LDA',0xA9,n);a.abs('STA',0x8D,shadow);a.abs('STA',0x8D,hw)
        a.imm('LDA',0xA9,0xC0);a.abs('STA',0x8D,0xD40E)
        a.op('RTS',0x60)
    # Palette band zero is loaded from the original XEX's first color shadows.
    # These are substituted later from source artwork (no guessed palette values).
    load_dl('DRAW_TITLE',ADDR['DL_TITLE'],0xE0,*initial_palettes['title'])
    load_dl('DRAW_CREW',ADDR['DL_CREW'],0x38,*initial_palettes['crew'])
    load_dl('DRAW_ARRIVAL',ADDR['DL_ARRIVAL'],0x38,*initial_palettes['arrival'])
    load_dl('DRAW_STAGE',ADDR['DL_STAGE'],0x38,0x00,0x0E,0x9A,0x4A)

    a.label('RESTART_MUSIC')
    LDA('TRACK')
    branch('BEQ',0xF0,'ROCK_TEMPO')
    a.imm('LDA',0xA9,0x49)  # Funk 110 BPM, increment $1F49
    STA('INC_LO')
    a.imm('LDA',0xA9,0x1F)
    STA('INC_HI')
    JMP('RESET_PHASE')
    a.label('ROCK_TEMPO')
    a.imm('LDA',0xA9,0x19)  # Rock 148 BPM, increment $2A19
    STA('INC_LO')
    a.imm('LDA',0xA9,0x2A)
    STA('INC_HI')
    a.label('RESET_PHASE')
    a.imm('LDA',0xA9,0)
    STA('PHASE_LO');STA('PHASE_HI');STA('NOTE_INDEX')
    JSR('SILENCE')
    JSR('WRITE_NOTE')
    a.op('RTS',0x60)
    a.label('SILENCE')
    a.imm('LDA',0xA9,0)
    for reg in [0xD201,0xD203,0xD205,0xD207]:a.abs('STA',0x8D,reg)
    a.op('RTS',0x60)
    a.label('MUSIC_FRAME')
    LDA('TRACK')
    a.imm('CMP',0xC9,2)
    branch('BCS',0xB0,'MUSIC_DONE')
    a.op('CLC',0x18)
    LDA('PHASE_LO')
    a.ref('ADC',0x6D,'INC_LO') # tempo-specific 16-bit increment
    STA('PHASE_LO')
    LDA('PHASE_HI')
    a.ref('ADC',0x6D,'INC_HI')
    STA('PHASE_HI')
    branch('BCC',0x90,'MUSIC_DONE')
    JSR('WRITE_NOTE')
    a.label('MUSIC_DONE')
    a.op('RTS',0x60)
    a.label('WRITE_NOTE')
    LDA('TRACK')
    branch('BEQ',0xF0,'ROCK_NOTE')
    a.imm('CMP',0xC9,1)
    branch('BEQ',0xF0,'FUNK_NOTE')
    a.op('RTS',0x60)
    def note(label,addr,ticks,endlabel):
        a.label(label)
        a.ref('LDX',0xAE,'NOTE_INDEX')
        for j in range(8):
            a.op(f'LDA ${addr+j*ticks:04X},X',0xBD,(addr+j*ticks)&255,(addr+j*ticks)>>8)
            a.abs('STA',0x8D,0xD200+j)
        a.op('INX',0xE8)
        a.imm('CPX',0xE0,ticks)
        branch('BNE',0xD0,endlabel)
        a.imm('LDX',0xA2,0)
        a.label(endlabel)
        a.ref('STX',0x8E,'NOTE_INDEX')
        a.op('RTS',0x60)
    note('ROCK_NOTE',ADDR['MUSIC_ROCK'],192,'ROCK_INC_DONE')
    note('FUNK_NOTE',ADDR['MUSIC_FUNK'],128,'FUNK_INC_DONE')

    # DLI handler: 11 flags -> 12 sixteen-line bands per screen. Preserve A/X/Y.
    a.label('DLI_HANDLER')
    a.op('PHA',0x48);a.op('TXA',0x8A);a.op('PHA',0x48);a.op('TYA',0x98);a.op('PHA',0x48)
    a.ref('LDX',0xAE,'DLI_POS')
    a.imm('LDA',0xA9,0);a.abs('STA',0x8D,0xD40A) # WSYNC
    LDA('SCENE')
    branch('BEQ',0xF0,'DLI_TITLE')
    a.imm('CMP',0xC9,1)
    branch('BEQ',0xF0,'DLI_CREW')
    JMP('DLI_ARRIVAL')
    def dli(label,addr):
        a.label(label)
        for n,reg in [(0,0xD01A),(1,0xD016),(2,0xD017),(3,0xD018)]:
            # jump to palette tables of next group index. Interleaved register tables
            # are converted to 4 column-major 11-byte color arrays by builder.
            a.abs('LDA',0xBD,addr+n*11)
            a.abs('STA',0x8D,reg)
        JMP('DLI_DONE')
    dli('DLI_TITLE',ADDR['PAL_TITLE'])
    dli('DLI_CREW',ADDR['PAL_CREW'])
    dli('DLI_ARRIVAL',ADDR['PAL_ARRIVAL'])
    a.label('DLI_DONE')
    a.op('INX',0xE8)
    a.imm('CPX',0xE0,11)
    branch('BCC',0x90,'DLI_SAVE')
    a.imm('LDX',0xA2,0)
    a.label('DLI_SAVE')
    a.ref('STX',0x8E,'DLI_POS')
    a.op('PLA',0x68);a.op('TAY',0xA8);a.op('PLA',0x68);a.op('TAX',0xAA);a.op('PLA',0x68);a.op('RTI',0x40)

    a.byte('SCENE',0);a.byte('TRACK',0);a.byte('ARMED',0);a.byte('DLI_POS',0)
    a.byte('FRAME_OLD',0);a.byte('PHASE_LO',0);a.byte('PHASE_HI',0);a.byte('NOTE_INDEX',0)
    a.byte('INC_LO',0);a.byte('INC_HI',0)
    a.byte('DLI_VECTOR_LO',a.labels['DLI_HANDLER']&0xFF)
    a.byte('DLI_VECTOR_HI',a.labels['DLI_HANDLER']>>8)
    binary=a.finalize()
    return a,binary


def relocate_dl(dl, old_img1, new_img1, old_img2,new_img2,old_text,new_text, new_addr):
    dl=bytearray(dl)
    # LMS 0x4E = set bitmap address; 0x42 = 40-column mode 2 LMS; 0x41 = JVB.
    i=0; edits=[]
    while i<len(dl):
        code=dl[i]
        if code in (0x4E,0x42):
            old=dl[i+1]|dl[i+2]<<8
            if old==old_img1:target=new_img1
            elif old==old_img2:target=new_img2
            elif old==old_text:target=new_text
            else:raise ValueError(f'unexpected DL LMS address {old:04X}')
            dl[i+1:i+3]=struct.pack('<H',target);edits.append((old,target));i+=3
        elif code==0x41:
            dl[i+1:i+3]=struct.pack('<H',new_addr);break
        elif code&0x0F == 0 and code&0x70:
            i+=1 # 8-line vertical blank
        else:i+=1
    else: raise ValueError('display list lacks JVB')
    assert len(edits)==3,(len(edits),edits)
    return bytes(dl)


def stage1_text():
    # ANTIC 2 encoding: ASCII printable 32-95 converts to character code 0-63.
    screen=[' '*40 for _ in range(24)]
    def put(row,msg):
        assert 0<=row<24 and len(msg)<=40,(row,msg)
        screen[row]=msg.center(40)
    put(2,"GAS BLASTERS '82")
    put(5,'STAGE 1')
    put(7,'TACO SMELL')
    put(8,'RESTAURANT ESCAPE')
    put(11,"BILLY'S DINNER IS OVER.")
    put(13,'THE TROUBLE IS JUST BEGINNING.')
    put(16,'GAMEPLAY COMING SOON')
    put(20,'PRESS START TO REPLAY')
    out=bytearray()
    for line in screen:
        for char in line:out.append(ord(char)-32 if 32<=ord(char)<=95 else ord(char))
    assert len(out)==24*40
    return bytes(out),screen


def stage1_dl():
    # All in one 4K region so no additional LMS is needed.
    dl=bytearray([0x70,0x70,0x70,0x42,0x00,0x98])
    dl.extend([0x02]*23)
    dl.extend([0x41,0x00,0x3F])
    return bytes(dl)


def palette_data(screen_code, dl):
    # Code contains four 11-byte palette streams indexed by DLI handler, and
    # initial color shadows in SETUP portion of original screen code.
    # Screen code begins $2000. Title palette at $2093, crew/arrival at $207f.
    palette_at=0x93 if len(screen_code)==231 else 0x7f
    dlist=screen_code[palette_at:palette_at+44]
    assert len(dlist)==44
    # DLI reads 4 column-major 11-byte arrays, color0 is background.
    first=(screen_code[0x2D],screen_code[0x37],screen_code[0x3C],screen_code[0x41])
    # Correct initialization comes from LDA #value / STA COLOR shadow pairs.
    # Extract *actual* immediate value for stores of COLOR0/1/2, including back.
    def initial_at(addr):
        needle=bytes([0x8D,addr&0xFF,addr>>8]);pos=screen_code.find(needle)
        assert pos>=2 and screen_code[pos-2]==0xA9,hex(addr)
        return screen_code[pos-1]
    first=(initial_at(0x2C8),initial_at(0x2C4),initial_at(0x2C5),initial_at(0x2C6))
    return first, dlist


def build(repo,out):
    title=xex_segments(repo/'assets/title/Title_Option3_Original.xex')
    crew=xex_segments(repo/'assets/intro/meet_the_crew_v4.xex')
    arrival=xex_segments(repo/'assets/arrival/arrival_v3.xex')
    assert len(title[0x4000])==3840 and len(title[0x5000])==2560
    assert len(crew[0x4000])==3840 and len(crew[0x5000])==1280
    assert len(arrival[0x4000])==3840 and len(arrival[0x5000])==1280
    assert crew[0x6000]==arrival[0x6000], 'intro fonts differ; need per-scene bank'
    rock_steps=(repo/'assets/music/rock_pokey_registers.bin').read_bytes()
    funk_steps=(repo/'assets/music/funk_pokey_registers.bin').read_bytes()
    # Original assets use step-major $D200-$D207 byte order.
    # Reshape into 8 contiguous channel tables for indexed LDA ...,X.
    rock=bytes(rock_steps[t*8+c] for c in range(8) for t in range(192))
    funk=bytes(funk_steps[t*8+c] for c in range(8) for t in range(128))
    assert len(rock)==192*8 and len(funk)==128*8
    for name,b in [('rock',rock),('funk',funk)]:
        assert any(b),name
    # The source MP3-conversion script exported register arrays channel-major.
    # Music code reads contiguous per-channel buffers, not step-interleaved bytes.
    for name,data,n in [('rock',rock,192),('funk',funk,128)]:
        assert len(data)==8*n
    color0={};color_streams={}
    for kind,source in [('title',title),('crew',crew),('arrival',arrival)]:
        first,streams=palette_data(source[0x2000],source[0x3C00])
        color0[kind]=first;color_streams[kind]=streams
    asm,code=assemble_controller(color0)
    assert len(code)<0x800
    out.mkdir(parents=True,exist_ok=True)
    parts={0x2000:code,0x2A00:rock,0x3000:funk,
           0x3500:color_streams['title'],0x3530:color_streams['crew'],0x3560:color_streams['arrival'],
           0x3800:crew[0x6000],
           0x3C00:relocate_dl(title[0x3C00],0x4000,0x4000,0x5000,0x5000,0x6000,0x5A00,0x3C00),
           0x3D00:relocate_dl(crew[0x3C00],0x4000,0x6000,0x5000,0x7000,0x5800,0x7600,0x3D00),
           0x3E00:relocate_dl(arrival[0x3C00],0x4000,0x8000,0x5000,0x9000,0x5800,0x9600,0x3E00),
           0x3F00:stage1_dl(),
           0x4000:title[0x4000],0x5000:title[0x5000],0x5A00:title[0x6000],
           0x6000:crew[0x4000],0x7000:crew[0x5000],0x7600:crew[0x5800],
           0x8000:arrival[0x4000],0x9000:arrival[0x5000],0x9600:arrival[0x5800],
           0x9800:stage1_text()[0],
           0x02E0:struct.pack('<H',0x2000)}
    generated=encode_xex(parts)
    name='GasBlasters82_OpeningSequence_v1.xex'
    (out/name).write_bytes(generated)
    (out/'generated_6502.asm').write_text('; Generated by tools/build_opening_sequence.py\n; Rebuild from Python script for authoritative bytes.\n    *= $2000\n'+'\n'.join(asm.asm)+'\n')
    metadata={'output':name,'sha256':hashlib.sha256(generated).hexdigest(),
              'bytes':len(generated),'scene_order':['title','meet_the_crew','arrival','stage1_placeholder'],
              'controls':{'title':'console START','meet_the_crew':'joystick 1 FIRE','arrival':'joystick 1 FIRE','stage1_placeholder':'console START to replay'},
              'music':{'title':'Arcade Rock (148 BPM)','meet_the_crew':'Funky Gas Attack (110 BPM)','arrival':'Funky Gas Attack (continuous from crew)','stage1_placeholder':'silence'},
              'segments':[{'start':f'${addr:04X}','end':f'${addr+len(data)-1:04X}','bytes':len(data)} for addr,data in sorted(parts.items())],
              'notes':'Emulator run pending; source XEX artwork/palette/data reused exactly.'}
    (out/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=REPO)
    p.add_argument('--output',type=Path,default=None)
    args=p.parse_args()
    m=build(args.repo,args.output or args.repo/'assets/opening')
    print(json.dumps({'file':m['output'],'bytes':m['bytes'],'sha256':m['sha256'],'segments':len(m['segments'])},indent=2))

if __name__=='__main__':main()
