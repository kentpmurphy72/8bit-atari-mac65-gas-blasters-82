#!/usr/bin/env python3
"""Build standalone native 6502 driving demo. Python stdlib, no Stage 1 writes."""
import hashlib,json,struct
from pathlib import Path
from build_opening_sequence import Asm,encode_xex
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/stage2_v01'
CODE=0x2000;SCREEN=0x2400;DL=0x2800;FONT_A=0x3000;FONT_B=0x3400;PMG=0x3800;TABLE=0x4000;TEMPLATE=0x6000

# Original compact 3x5 HUD font, padded to four color pixels and eight scanlines.
FONT={
'A':['010','101','111','101','101'],'B':['110','101','110','101','110'],
'C':['011','100','100','100','011'],'D':['110','101','101','101','110'],
'E':['111','100','110','100','111'],'F':['111','100','110','100','100'],
'G':['011','100','101','101','011'],'H':['101','101','111','101','101'],
'I':['111','010','010','010','111'],'J':['001','001','001','101','010'],
'K':['101','101','110','101','101'],'L':['100','100','100','100','111'],
'M':['101','111','111','101','101'],'N':['101','111','111','111','101'],
'O':['010','101','101','101','010'],'P':['110','101','110','100','100'],
'Q':['010','101','101','111','011'],'R':['110','101','110','101','101'],
'S':['011','100','010','001','110'],'T':['111','010','010','010','010'],
'U':['101','101','101','101','111'],'V':['101','101','101','101','010'],
'W':['101','101','111','111','101'],'X':['101','101','010','101','101'],
'Y':['101','101','010','010','010'],'Z':['111','001','010','100','111'],
'0':['111','101','101','101','111'],'1':['010','110','010','010','111'],
'2':['110','001','010','100','111'],'3':['110','001','010','001','110'],
'4':['101','101','111','001','001'],'5':['111','100','110','001','110'],
'6':['011','100','111','101','111'],'7':['111','001','010','010','010'],
'8':['111','101','111','101','111'],'9':['111','101','111','001','110'],
' ':['000']*5,"'":['010','010','000','000','000'],'.':['000','000','000','000','010'],
'/':['001','001','010','100','100'],'%':['101','001','010','100','101'],
'(':['001','010','010','010','001'],')':['100','010','010','010','100'],
'-':['000','000','111','000','000'],':':['000','010','000','010','000']}

def pack(pixels):
    n=0
    for p in pixels:n=(n<<2)|p
    return n

def art(t):
    # Eight unique horizontal categories; four character-row phases per category.
    categories=[[1,1,1,1],[1,1,1,2],[2,2,2,2],[2,2,0,0],
                [0,0,0,0],[0,0,3,0],[0,0,2,2],[2,1,1,1]]
    cat_for_col=[0,1,2,3]+[4]*9+[5]+[4]*9+[6,2,7,0]
    assert len(cat_for_col)==27
    pages=bytearray()
    for phase in range(32):
        for cat,strip in enumerate(categories):
            for rowphase in range(4):
                for y in range(8):
                    world=(rowphase*8+y-phase)%32;line=[]
                    for x,p in enumerate(strip):
                        if p==3:p=3 if world<16 else 0
                        elif p==1 and (world+x*3)%8==0:p=0
                        elif p==2 and (world+x)%8==0:p=3
                        line.append(p)
                    pages.append(pack(line))
    assert len(pages)==8192
    font=bytearray(1024);font[:256]=pages[:256]
    for char,rows in FONT.items():
        index=ord(char)+32
        assert 64<=index<128
        pixels=[0]+[pack([3 if b=='1' else 0 for b in row]+[0]) for row in rows]+[0,0]
        font[index*8:index*8+8]=bytes(pixels)
    screen=bytearray(40*24)
    for y in range(24):
        for x in range(27):screen[y*40+x]=128+cat_for_col[x]*4+y%4
        screen[y*40+27:y*40+40]=bytes([128+ord(' ')+32])*13
    lines={1:'GAS BLASTERS',2:"    '82",4:'GAS     00%',6:'MI      5.0',8:'SCORE 000000',10:'LIVES     3',11:'SPD  1.5 PX/F',13:'ZONE PAVED',15:'TO PHARMACY',16:'   (DEMO)',18:'UP: FASTER',19:'DOWN: BRAKE',20:'L/R: STEER',22:'START: RESET',23:'NO PENALTIES'}
    for y,s in lines.items():
        assert len(s)<=13
        screen[y*40+27:y*40+40]=bytes(128+ord(c)+32 for c in s.ljust(13))
    # P0 is red body; P1 white headlights/glass, with no overlapping P0 bits.
    body=[0x18,0x3C,0x3C,0x7E,0x5A,0xC3,0xDB,0xFF,0xFF,0xDB,0xC3,0x7E,0x7E,0x66,0x3C,0x18]
    white=[0,0,0x42,0,0,0x18,0,0,0,0,0x18,0,0,0,0,0]
    pmg=bytearray(2048);start=32+t['car_top_scanline']
    pmg[1024+start:1024+start+16]=bytes(body);pmg[1280+start:1280+start+16]=bytes(white)
    return pages,font,screen,pmg,categories,cat_for_col

def build(out=OUT):
    t=json.loads((OUT/'tuning.json').read_text());assert (t['driving_columns'],t['hud_columns'])==(27,13)
    assert 0<t['scroll_min_q4_scanlines_per_tick']<=t['scroll_default_q4_scanlines_per_tick']<=t['scroll_max_q4_scanlines_per_tick']<128
    assert t['acceleration_q4_per_tick']==1 and 0<t['steering_q4_color_pixels_per_tick']<=16
    pages,font,screen,pmg,categories,columns=art(t)
    a=Asm(CODE)
    def label(n):a.label(n)
    def imm(v):a.imm('LDA',0xA9,v)
    def ld(n):a.ref('LDA',0xAD,n)
    def st(n):a.ref('STA',0x8D,n)
    def call(n):a.ref('JSR',0x20,n)
    def jump(n):a.ref('JMP',0x4C,n)
    def br(op,n):a.branch('branch',op,n)
    def cmp(v):a.imm('CMP',0xC9,v)
    def store(addr):a.abs('STA',0x8D,addr)
    def load(addr):a.abs('LDA',0xAD,addr)
    def add(v):a.op('CLC',0x18);a.imm('ADC',0x69,v)
    def ret():a.op('RTS',0x60)
    label('START');a.op('SEI',0x78);a.op('CLD',0xD8);imm(0);store(0xD40E);store(0x22F);store(0xD400)
    for reg in (0xD201,0xD203,0xD205,0xD207):store(reg)
    # Load both full fonts only once; normal rendering changes the inactive road page.
    for page in range(4):
        a.imm('LDX',0xA2,0);label('FONT_INIT_'+str(page));a.abs('LDA',0xBD,TEMPLATE+page*256);a.abs('STA',0x9D,FONT_A+page*256);a.abs('STA',0x9D,FONT_B+page*256);a.op('INX',0xE8);br(0xD0,'FONT_INIT_'+str(page))
    for addr,value in [(0x230,DL&255),(0x231,DL>>8),(0xD402,DL&255),(0xD403,DL>>8),
                       (0x2F4,0x30),(0xD409,0x30),(0x2C8,2),(0xD01A,2),(0x2C4,0xC6),(0xD016,0xC6),
                       (0x2C5,0x0A),(0xD017,0x0A),(0x2C6,6),(0xD018,6),(0x2C7,14),(0xD019,14),
                       (0xD407,PMG>>8),(0xD008,0),(0xD009,0),(0xD01D,2),
                       (0x26F,1),(0xD01B,1),(0x2C0,0x36),(0xD012,0x36),(0x2C1,14),(0xD013,14)]:imm(value);store(addr)
    call('RESET');imm(0x3A);store(0x22F);store(0xD400);imm(0x40);store(0xD40E);a.op('CLI',0x58)
    load(0x14);st('LAST_FRAME')
    label('WAIT');load(0x14);a.ref('CMP',0xCD,'LAST_FRAME');br(0xF0,'WAIT');st('LAST_FRAME');call('FRAME');jump('WAIT')
    label('RESET');imm(0);st('PHASE_LO');st('PHASE_HI');st('READY_PHASE');st('SHOWN_PHASE');st('ARMED');imm(0x30);st('NEXT_BANK');imm(t['scroll_default_q4_scanlines_per_tick']);st('SPEED')
    spawn=((108-8)//2)*16;imm(spawn&255);st('CAR_LO');imm(spawn>>8);st('CAR_HI')
    # While running, initialize only the hidden font. Current visible bank is
    # left untouched until next frame publication, preventing mid-raster tearing.
    load(0x2F4);a.imm('EOR',0x49,4);st('NEXT_BANK');imm(0x40);st('TABLE_HIGH');call('PREPARE');call('TELEMETRY');ret()
    label('FRAME');ld('NEXT_BANK');store(0x2F4);store(0xD409);ld('READY_PHASE');st('SHOWN_PHASE')
    load(0xD01F);a.imm('AND',0x29,1);br(0xD0,'RELEASED');ld('ARMED');br(0xF0,'DRIVE');call('RESET');ret()
    label('RELEASED');imm(1);st('ARMED')
    label('DRIVE');load(0xD300);st('JOY')
    a.imm('AND',0x29,3);cmp(2);br(0xD0,'BRAKE');ld('SPEED');cmp(t['scroll_max_q4_scanlines_per_tick']);br(0xB0,'STEER');add(t['acceleration_q4_per_tick']);st('SPEED');jump('STEER')
    label('BRAKE');cmp(1);br(0xD0,'STEER');ld('SPEED');cmp(t['scroll_min_q4_scanlines_per_tick']+1);br(0x90,'STEER');a.op('SEC',0x38);a.imm('SBC',0xE9,t['acceleration_q4_per_tick']);st('SPEED')
    label('STEER');ld('JOY');a.imm('AND',0x29,12);cmp(8);br(0xD0,'RIGHT');ld('CAR_LO');a.op('SEC',0x38);a.imm('SBC',0xE9,t['steering_q4_color_pixels_per_tick']);st('CAR_LO');ld('CAR_HI');a.imm('SBC',0xE9,0);st('CAR_HI');br(0xB0,'SCROLL');imm(0);st('CAR_LO');st('CAR_HI');jump('SCROLL')
    label('RIGHT');cmp(4);br(0xD0,'SCROLL');ld('CAR_LO');add(t['steering_q4_color_pixels_per_tick']);st('CAR_LO');ld('CAR_HI');a.imm('ADC',0x69,0);st('CAR_HI');cmp(6);br(0x90,'SCROLL');br(0xD0,'CLAMP_RIGHT');ld('CAR_LO');cmp(0x41);br(0x90,'SCROLL');label('CLAMP_RIGHT');imm(0x40);st('CAR_LO');imm(6);st('CAR_HI')
    label('SCROLL');ld('PHASE_LO');a.op('CLC',0x18);a.ref('ADC',0x6D,'SPEED');st('PHASE_LO');ld('PHASE_HI');a.imm('ADC',0x69,0);a.imm('AND',0x29,1);st('PHASE_HI')
    # Q4 modulo-32 accumulator -> 32 precomputed road-font pages.
    ld('PHASE_LO')
    for _ in range(4):a.op('LSR A',0x4A)
    st('READY_PHASE');ld('PHASE_HI')
    for _ in range(4):a.op('ASL A',0x0A)
    a.ref('ORA',0x0D,'READY_PHASE');st('READY_PHASE');add(TABLE>>8);st('TABLE_HIGH')
    ld('NEXT_BANK');a.imm('EOR',0x49,4);st('NEXT_BANK');call('TELEMETRY');call('PREPARE');ret()
    label('PREPARE');imm(0);a.zp('STA',0x85,0x80);a.zp('STA',0x85,0x82);ld('TABLE_HIGH');a.zp('STA',0x85,0x81);ld('NEXT_BANK');a.zp('STA',0x85,0x83);a.imm('LDY',0xA0,0)
    label('COPY_ROAD');a.op('LDA ($80),Y',0xB1,0x80);a.op('STA ($82),Y',0x91,0x82);a.op('INY',0xC8);br(0xD0,'COPY_ROAD');ret()
    label('TELEMETRY');ld('CAR_LO');st('PIX_LO');ld('CAR_HI');st('PIX_HI')
    for _ in range(4):a.ref('LSR',0x4E,'PIX_HI');a.ref('ROR',0x6E,'PIX_LO')
    ld('PIX_LO');add(48);store(0xD000);store(0xD001)
    ld('SPEED')
    for _ in range(4):a.op('LSR A',0x4A)
    add(128+ord('0')+32);store(SCREEN+11*40+27+5)
    ld('SPEED');a.imm('AND',0x29,15);a.op('TAX',0xAA);a.abs('LDA',0xBD,0x6400);store(SCREEN+11*40+27+7)
    ld('PIX_LO');add(4);cmp(7);br(0x90,'GRASS');cmp(101);br(0xB0,'GRASS');cmp(14);br(0x90,'SHOULDER');cmp(94);br(0xB0,'SHOULDER');imm(2);jump('SET_ZONE')
    label('GRASS');imm(0);jump('SET_ZONE')
    label('SHOULDER');imm(1)
    label('SET_ZONE');st('ZONE');a.op('ASL A',0x0A);a.op('ASL A',0x0A);a.op('CLC',0x18);a.ref('ADC',0x6D,'ZONE');a.op('TAX',0xAA);a.imm('LDY',0xA0,0)
    label('ZONE_TEXT');a.abs('LDA',0xBD,0x6500);a.abs('STA',0x99,SCREEN+13*40+27+5);a.op('INX',0xE8);a.op('INY',0xC8);a.imm('CPY',0xC0,5);br(0x90,'ZONE_TEXT');ret()
    for name in ['LAST_FRAME','NEXT_BANK','TABLE_HIGH','READY_PHASE','SHOWN_PHASE','PHASE_LO','PHASE_HI','SPEED','CAR_LO','CAR_HI','ARMED','JOY','PIX_LO','PIX_HI','ZONE']:a.byte(name,0)
    code=a.finalize();assert CODE+len(code)<=SCREEN,'Code overlaps screen'
    dl=bytes([0x70]*3+[0x44,SCREEN&255,SCREEN>>8]+[4]*23+[0x41,DL&255,DL>>8])
    parts={CODE:code,SCREEN:screen,DL:dl,FONT_A:font,FONT_B:font,PMG:pmg,TABLE:pages,TEMPLATE:font,
           0x6400:bytes(128+ord(str(i*10//16))+32 for i in range(16)),
           0x6500:bytes(128+ord(c)+32 for c in 'GRASSSHLDRPAVED'),0x2E0:struct.pack('<H',CODE)}
    generated=encode_xex(parts);out.mkdir(parents=True,exist_ok=True);name='GasBlasters82_Stage2_Driving_v01.xex';(out/name).write_bytes(generated)
    (out/'driving_6502.asm').write_text('; Generated by tools/build_stage2_v01.py; emitter is authoritative\n    *= $2000\n'+'\n'.join(a.asm)+'\n')
    m={'output':name,'sha256':hashlib.sha256(generated).hexdigest(),'bytes':len(generated),'labels':a.labels,'tuning':t,'code_bytes':len(code),'road_categories':categories,'category_for_column':columns,'segments':[{'start':addr,'end':addr+len(d)-1,'bytes':len(d)} for addr,d in sorted(parts.items())],'atari800_tested':False,'hardware_tested':False,'notes':'Standalone driving-feel demo, all HUD game values are placeholders; speed/zone telemetry only.'}
    (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m
if __name__=='__main__':
    m=build();print(m['output'],m['bytes'],'bytes',m['sha256'])
