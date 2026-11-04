#!/usr/bin/env python3
"""Build standalone v0.1-r3 with speed-linked PMG Y; original v0.1 untouched. Python stdlib, no Stage 1 writes."""
import hashlib,json,struct
from pathlib import Path
from build_opening_sequence import Asm,encode_xex
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/stage2_v01_r3'
CODE=0x2000;SCREEN=0x2400;DL=0x2800;FONT_A=0x3000;FONT_B=0x3400;PMG=0x3800;TABLE=0x4000;TEMPLATE=0x6000

from build_stage2_v01 import art

def build(out=OUT):
    t=json.loads((OUT/'tuning.json').read_text());assert (t['driving_columns'],t['hud_columns'])==(27,13)
    assert 0<t['scroll_min_q4_scanlines_per_tick']<=t['scroll_default_q4_scanlines_per_tick']<=t['scroll_max_q4_scanlines_per_tick']<128
    assert t['acceleration_q4_per_tick']==1 and 0<t['steering_q4_color_pixels_per_tick']<=16
    pages,font,screen,pmg,categories,columns=art(t)
    lo=t['scroll_min_q4_scanlines_per_tick'];hi=t['scroll_max_q4_scanlines_per_tick']
    ylow=t['car_top_at_min_speed'];yhigh=t['car_top_at_max_speed'];smoothing=t['car_y_smoothing_q4_scanlines_per_tick']
    assert hi>lo and (t['car_width_color_pixels'],t['car_height_scanlines'])==(8,16)
    assert 0<=yhigh<t['car_top_scanline']<ylow<=192-t['car_height_scanlines']
    assert 0<smoothing<=16
    mid=t['scroll_default_q4_scanlines_per_tick'];ymid=t['car_top_scanline']
    assert lo<mid<hi
    # Piecewise continuous interpolation preserves the min/default anchors while
    # extending only the high-speed segment. No emitted 6502 instructions change.
    def target(speed):
        speed=min(hi,max(lo,speed))
        if speed<=mid:return ylow*16-(speed-lo)*(ylow-ymid)*16//(mid-lo)
        return ymid*16-(speed-mid)*(ymid-yhigh)*16//(hi-mid)
    targets=[target(speed) for speed in range(256)]
    assert targets[t['scroll_default_q4_scanlines_per_tick']]==t['car_top_scanline']*16
    sprite_start=32+t['car_top_scanline']
    sprites=pmg[1024+sprite_start:1024+sprite_start+16]+pmg[1280+sprite_start:1280+sprite_start+16]
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
    spawn=((108-8)//2)*16;imm(spawn&255);st('CAR_LO');imm(spawn>>8);st('CAR_HI');imm((t['car_top_scanline']*16)&255);st('CAR_Y_LO');imm(t['car_top_scanline']>>4);st('CAR_Y_HI')
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
    label('TELEMETRY');call('VERTICAL');ld('CAR_LO');st('PIX_LO');ld('CAR_HI');st('PIX_HI')
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
    # A speed lookup sets the desired Y; current Y approaches without springing
    # to default, accumulating unbounded motion, or overshooting the target.
    label('VERTICAL');a.ref('LDX',0xAE,'SPEED');a.abs('LDA',0xBD,0x6600);st('TARGET_Y_LO');a.abs('LDA',0xBD,0x6700);st('TARGET_Y_HI')
    ld('CAR_Y_LO');a.ref('CMP',0xCD,'TARGET_Y_LO');ld('CAR_Y_HI');a.ref('SBC',0xED,'TARGET_Y_HI');br(0x90,'Y_DOWN')
    ld('CAR_Y_LO');a.op('SEC',0x38);a.imm('SBC',0xE9,smoothing);st('CAR_Y_LO');ld('CAR_Y_HI');a.imm('SBC',0xE9,0);st('CAR_Y_HI')
    ld('CAR_Y_LO');a.ref('CMP',0xCD,'TARGET_Y_LO');ld('CAR_Y_HI');a.ref('SBC',0xED,'TARGET_Y_HI');br(0xB0,'Y_RENDER');jump('Y_CLAMP')
    label('Y_DOWN');ld('CAR_Y_LO');add(smoothing);st('CAR_Y_LO');ld('CAR_Y_HI');a.imm('ADC',0x69,0);st('CAR_Y_HI')
    ld('CAR_Y_LO');a.ref('CMP',0xCD,'TARGET_Y_LO');ld('CAR_Y_HI');a.ref('SBC',0xED,'TARGET_Y_HI');br(0x90,'Y_RENDER')
    label('Y_CLAMP');ld('TARGET_Y_LO');st('CAR_Y_LO');ld('TARGET_Y_HI');st('CAR_Y_HI')
    label('Y_RENDER');ld('CAR_Y_LO');st('Y_PIX_LO');ld('CAR_Y_HI');st('Y_PIX_HI')
    for _ in range(4):a.ref('LSR',0x4E,'Y_PIX_HI');a.ref('ROR',0x6E,'Y_PIX_LO')
    ld('Y_PIX_LO');add(32);st('NEW_PMG_Y');a.ref('CMP',0xCD,'OLD_PMG_Y');br(0xD0,'Y_RELOCATE');ret()
    # Erase the full old footprint before drawing either plane at its new rows.
    label('Y_RELOCATE');a.ref('LDX',0xAE,'OLD_PMG_Y');a.imm('LDY',0xA0,t['car_height_scanlines']);imm(0)
    label('Y_CLEAR');a.abs('STA',0x9D,PMG+1024);a.abs('STA',0x9D,PMG+1280);a.op('INX',0xE8);a.op('DEY',0x88);br(0xD0,'Y_CLEAR')
    a.ref('LDX',0xAE,'NEW_PMG_Y');a.imm('LDY',0xA0,0)
    label('Y_DRAW');a.abs('LDA',0xB9,0x6800);a.abs('STA',0x9D,PMG+1024);a.abs('LDA',0xB9,0x6810);a.abs('STA',0x9D,PMG+1280);a.op('INX',0xE8);a.op('INY',0xC8);a.imm('CPY',0xC0,t['car_height_scanlines']);br(0x90,'Y_DRAW')
    ld('NEW_PMG_Y');st('OLD_PMG_Y');ret()
    for name in ['LAST_FRAME','NEXT_BANK','TABLE_HIGH','READY_PHASE','SHOWN_PHASE','PHASE_LO','PHASE_HI','SPEED','CAR_LO','CAR_HI','ARMED','JOY','PIX_LO','PIX_HI','ZONE','CAR_Y_LO','CAR_Y_HI','TARGET_Y_LO','TARGET_Y_HI','Y_PIX_LO','Y_PIX_HI','NEW_PMG_Y']:a.byte(name,0)
    a.byte('OLD_PMG_Y',sprite_start)
    code=a.finalize();assert CODE+len(code)<=SCREEN,'Code overlaps screen'
    dl=bytes([0x70]*3+[0x44,SCREEN&255,SCREEN>>8]+[4]*23+[0x41,DL&255,DL>>8])
    parts={CODE:code,SCREEN:screen,DL:dl,FONT_A:font,FONT_B:font,PMG:pmg,TABLE:pages,TEMPLATE:font,
           0x6400:bytes(128+ord(str(i*10//16))+32 for i in range(16)),
           0x6500:bytes(128+ord(c)+32 for c in 'GRASSSHLDRPAVED'),
           0x6600:bytes(n&255 for n in targets),0x6700:bytes(n>>8 for n in targets),0x6800:sprites,0x2E0:struct.pack('<H',CODE)}
    generated=encode_xex(parts);out.mkdir(parents=True,exist_ok=True);name='GasBlasters82_Stage2_Driving_v01_r3.xex';(out/name).write_bytes(generated)
    (out/'driving_6502.asm').write_text('; Generated by tools/build_stage2_v01_r3.py; emitter is authoritative\n    *= $2000\n'+'\n'.join(a.asm)+'\n')
    m={'output':name,'sha256':hashlib.sha256(generated).hexdigest(),'bytes':len(generated),'labels':a.labels,'tuning':t,'code_bytes':len(code),'revision':'v0.1-r3','vertical_targets_q4':targets,'previous_r2_sha256':hashlib.sha256((ROOT/'assets/stage2_v01_r2/GasBlasters82_Stage2_Driving_v01_r2.xex').read_bytes()).hexdigest(),'original_v01_sha256':hashlib.sha256((ROOT/'assets/stage2_v01/GasBlasters82_Stage2_Driving_v01.xex').read_bytes()).hexdigest(),'road_categories':categories,'category_for_column':columns,'segments':[{'start':addr,'end':addr+len(d)-1,'bytes':len(d)} for addr,d in sorted(parts.items())],'atari800_tested':False,'hardware_tested':False,'notes':'Standalone driving-feel demo, all HUD game values are placeholders; speed/zone telemetry only.'}
    (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m
if __name__=='__main__':
    m=build();print(m['output'],m['bytes'],'bytes',m['sha256'])
