#!/usr/bin/env python3
"""Offline 6502 emitter for Stage 1; Python stdlib only. No baseline writes."""
import hashlib, json, struct
from pathlib import Path
from build_opening_sequence import Asm, xex_segments, encode_xex, assemble_controller, palette_data
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/stage1'
BASE=ROOT/'assets/opening/GasBlasters82_OpeningSequence_v1.xex'
MAP=0xA000; FONT=0xAC00; SCREEN=0xB000; SEEN=0x9800

def build(out=OUT):
    meta=json.loads((ROOT/'assets/maps/taco_smell_stage1_v01.json').read_text())
    rows=(ROOT/'assets/maps'/meta['terrain_file']).read_text().splitlines()
    symbols=list(meta['terrain']); ids={s:i for i,s in enumerate(symbols)}
    terrain=bytes(ids[s]|(128 if meta['terrain'][s]['solid'] else 0) for row in rows for s in row)
    palettes={k:palette_data(xex_segments(ROOT/p)[0x2000],b'')[0] for k,p in [('title','assets/title/Title_Option3_Original.xex'),('crew','assets/intro/meet_the_crew_v4.xex'),('arrival','assets/arrival/arrival_v3.xex')]}
    original,_=assemble_controller(palettes); ol=original.labels
    a=Asm(0x1000)
    def imm(n):a.imm('LDA',0xA9,n)
    def ld(n):a.ref('LDA',0xAD,n)
    def st(n):a.ref('STA',0x8D,n)
    def inc(n):a.ref('INC',0xEE,n)
    def dec(n):a.ref('DEC',0xCE,n)
    def call(n):a.ref('JSR',0x20,n)
    def jump(n):a.ref('JMP',0x4C,n)
    def br(op,n):a.branch({0xF0:'BEQ',0xD0:'BNE',0x90:'BCC',0xB0:'BCS'}[op],op,n)
    def ret():a.op('RTS',0x60)
    def store(addr):a.abs('STA',0x8D,addr)
    def load(addr):a.abs('LDA',0xAD,addr)
    def cmp(n):a.imm('CMP',0xC9,n)
    def add(n):a.op('CLC',0x18);a.imm('ADC',0x69,n)
    def ptr(addr,zp):imm(addr&255);a.zp('STA',0x85,zp);imm(addr>>8);a.zp('STA',0x85,zp+1)
    def indyload(zp):a.op(f'LDA (${zp:02X}),Y',0xB1,zp)
    def indystore(zp):a.op(f'STA (${zp:02X}),Y',0x91,zp)
    def ldy(n):a.imm('LDY',0xA0,n)
    def ptrinc(zp):
        a.zp('INC',0xE6,zp); tag=f'PI_{len(a.buf)}';br(0xD0,tag);a.zp('INC',0xE6,zp+1);a.label(tag)
    # Dispatcher replaces only the first LDA of original HANDLE_INPUT.
    a.label('INPUT');load(ol['SCENE']);cmp(3);br(0xF0,'FRAME');load(ol['SCENE']);a.abs('JMP',0x4C,ol['HANDLE_INPUT']+3)
    a.label('FRAME')
    load(0xD01F);a.imm('AND',0x29,1);br(0xF0,'START_DOWN');imm(1);st('ARM');jump('FRAME_PLAY')
    a.label('START_DOWN');ld('ARM');br(0xF0,'FRAME_PLAY');call('INIT');ret()
    a.label('FRAME_PLAY');ld('STATE');br(0xF0,'PLAY');ret()
    a.label('PLAY');inc('TICKS');ld('ACTIVE');br(0xD0,'SPAWN_DONE')
    dec('DELAY');br(0xD0,'SPAWN_DONE');imm(1);st('ACTIVE');call('CHECK_CAUGHT')
    a.label('SPAWN_DONE');ld('TICKS');a.imm('AND',0x29,7);br(0xD0,'ENEMY_TICK')
    ld('PX');st('NX');ld('PY');st('NY');load(0xD300);st('JOY')
    for bit,var,opcode in [(1,'NY',0xCE),(2,'NY',0xEE),(4,'NX',0xCE),(8,'NX',0xEE)]:
        ld('JOY');a.imm('AND',0x29,bit);br(0xD0,f'NO_{bit}');a.ref('DEC' if opcode==0xCE else 'INC',opcode,var);jump('PLAYER_STEP');a.label(f'NO_{bit}')
    jump('ENEMY_TICK')
    a.label('PLAYER_STEP');call('WALK');br(0xF0,'ENEMY_TICK');ld('NX');st('PX');ld('NY');st('PY');call('CHECK_CAUGHT')
    ld('STATE');br(0xD0,'ENEMY_TICK');ld('PX');cmp(meta['exit']['tile'][0]);br(0xD0,'ENEMY_TICK');ld('PY');cmp(meta['exit']['tile'][1]);br(0xD0,'ENEMY_TICK');imm(2);st('STATE')
    a.label('ENEMY_TICK');ld('STATE');br(0xD0,'RENDER_FRAME');ld('ACTIVE');br(0xF0,'RENDER_FRAME');ld('SEARCH');br(0xF0,'NEW_CHASE');call('SEARCH_STEP');call('CHECK_CAUGHT');jump('RENDER_FRAME');a.label('NEW_CHASE');inc('ENEMY_TIMER');ld('ENEMY_TIMER');cmp(16);br(0x90,'RENDER_FRAME');imm(0);st('ENEMY_TIMER');call('CHASE');call('CHECK_CAUGHT')
    a.label('RENDER_FRAME');ld('STATE');br(0xD0,'RENDER_NOW');ld('TICKS');a.imm('AND',0x29,7);br(0xD0,'FRAME_DONE');a.label('RENDER_NOW');call('DRAW')
    a.label('FRAME_DONE');ret()
    a.label('CHECK_CAUGHT');ld('ACTIVE');br(0xF0,'CC_DONE');ld('PX');a.ref('CMP',0xCD,'EX');br(0xD0,'CC_DONE');ld('PY');a.ref('CMP',0xCD,'EY');br(0xD0,'CC_DONE');imm(1);st('STATE')
    a.label('CC_DONE');ret()
    a.label('INIT');imm(0);store(0xD40E);st('STATE');st('TICKS');st('ACTIVE');st('ARM');st('ENEMY_TIMER');st('SEARCH')
    imm(180);st('DELAY')
    for name,coord in [('billy',('PX','PY')),('hazmat_front',('EX','EY'))]:
        xy=next(e['spawn'] for e in meta['actors'] if e['id']==name)
        for var,value in zip(coord,xy):imm(value);st(var)
    for addr,value in [(0x230,0),(0x231,0x3F),(0xD402,0),(0xD403,0x3F),(0x2F4,0xAC),(0xD409,0xAC),(0x22F,0x22),(0xD400,0x22),(0x2C5,0x0E),(0xD017,0x0E),(0x2C6,0),(0xD018,0),(0x2C8,0),(0xD01A,0)]:imm(value);store(addr)
    imm(0x40);store(0xD40E);call('DRAW');ret()
    # Address helpers use NX/NY, return row pointer in $80. Caller uses Y=NX.
    a.label('MAP_PTR');ld('NY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xA500);a.zp('STA',0x85,0x80);a.abs('LDA',0xBD,0xA501);a.zp('STA',0x85,0x81);a.ref('LDY',0xAC,'NX');ret()
    a.label('SEEN_PTR');ld('NY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xA580);a.zp('STA',0x85,0x82);a.abs('LDA',0xBD,0xA581);a.zp('STA',0x85,0x83);a.ref('LDY',0xAC,'NX');ret()
    a.label('WALK');ld('NX');cmp(48);br(0xB0,'BLOCK');ld('NY');cmp(22);br(0xB0,'BLOCK');call('MAP_PTR');indyload(0x80);a.imm('AND',0x29,128);br(0xD0,'BLOCK');imm(1);ret()
    a.label('BLOCK');imm(0);ret()
    # BFS from Billy, recording a reverse direction at each discovered cell.
    # Two 16-bit FIFO pointers per coordinate array; at most 1056 entries.
    a.label('CHASE');imm(1);st('SEARCH');ptr(SEEN,0x82);ldy(0);imm(0)
    a.imm('LDX',0xA2,4);a.label('CLEAR_PAGE');indystore(0x82);a.op('INY',0xC8);br(0xD0,'CLEAR_PAGE');a.zp('INC',0xE6,0x83);a.op('DEX',0xCA);br(0xD0,'CLEAR_PAGE')
    a.label('CLEAR_TAIL');indystore(0x82);a.op('INY',0xC8);a.imm('CPY',0xC0,32);br(0xD0,'CLEAR_TAIL')
    for zp,addr in [(0x84,0xB400),(0x86,0xB900),(0x88,0xB400),(0x8A,0xB900)]:ptr(addr,zp)
    ld('PX');st('NX');ld('PY');st('NY');call('SEEN_PTR');imm(5);indystore(0x82);call('ENQUEUE')
    a.label('SEARCH_STEP');imm(8);st('BUDGET')
    a.label('BFS_LOOP');a.zp('LDA',0xA5,0x84);a.zp('CMP',0xC5,0x88);br(0xD0,'POP');a.zp('LDA',0xA5,0x85);a.zp('CMP',0xC5,0x89);br(0xD0,'POP');imm(0);st('SEARCH');ret()
    a.label('POP');ldy(0);indyload(0x88);st('CX');indyload(0x8A);st('CY');ptrinc(0x88);ptrinc(0x8A)
    # examine neighbors; stop BFS as soon as enemy reached
    for i,(dx,dy,reverse) in enumerate([(0,-1,2),(0,1,1),(-1,0,4),(1,0,3)]):
        ld('CX');add(dx);st('NX');ld('CY');add(dy);st('NY');imm(reverse);st('DIR');call('VISIT');ld('FOUND');br(0xF0,f'NEXT_{i}');jump('FOLLOW');a.label(f'NEXT_{i}')
    dec('BUDGET');br(0xF0,'SEARCH_YIELD');jump('BFS_LOOP');a.label('SEARCH_YIELD');ret()
    a.label('VISIT');imm(0);st('FOUND');call('WALK');br(0xF0,'VISIT_DONE');call('SEEN_PTR');indyload(0x82);br(0xD0,'VISIT_DONE');ld('DIR');indystore(0x82);call('ENQUEUE');ld('NX');a.ref('CMP',0xCD,'EX');br(0xD0,'VISIT_DONE');ld('NY');a.ref('CMP',0xCD,'EY');br(0xD0,'VISIT_DONE');imm(1);st('FOUND')
    a.label('VISIT_DONE');ret()
    a.label('ENQUEUE');ldy(0);ld('NX');indystore(0x84);ld('NY');indystore(0x86);ptrinc(0x84);ptrinc(0x86);ret()
    a.label('FOLLOW');imm(0);st('SEARCH');ld('EX');st('NX');ld('EY');st('NY');call('SEEN_PTR');indyload(0x82)
    for direction,var,opcode in [(1,'EY',0xCE),(2,'EY',0xEE),(3,'EX',0xCE),(4,'EX',0xEE)]:
        cmp(direction);br(0xD0,f'FOLLOW_{direction}');a.ref('DEC' if opcode==0xCE else 'INC',opcode,var);ret();a.label(f'FOLLOW_{direction}')
    ret()
    # Redraw 30x22 viewport + 10-column status strip and 2 text rows.
    a.label('DRAW');ld('PX');cmp(15);br(0xB0,'CAM_SUB');imm(0);jump('CAM_SET')
    a.label('CAM_SUB');add(-14);cmp(19);br(0x90,'CAM_SET');imm(18)
    a.label('CAM_SET');st('CAM');imm(0);st('RY')
    a.label('DRAW_ROW');ld('RY');st('NY');ld('CAM');st('NX');call('MAP_PTR');ld('RY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xA540);a.zp('STA',0x85,0x82);a.abs('LDA',0xBD,0xA541);a.zp('STA',0x85,0x83);imm(0);st('RX')
    a.label('DRAW_CELL');ld('RX');a.op('CLC',0x18);a.ref('ADC',0x6D,'CAM');st('WX');a.op('TAY',0xA8);indyload(0x80);a.imm('AND',0x29,127);st('GLYPH')
    ld('ACTIVE');br(0xF0,'DRAW_PLAYER');ld('WX');a.ref('CMP',0xCD,'EX');br(0xD0,'DRAW_PLAYER');ld('RY');a.ref('CMP',0xCD,'EY');br(0xD0,'DRAW_PLAYER');imm(15);st('GLYPH')
    a.label('DRAW_PLAYER');ld('WX');a.ref('CMP',0xCD,'PX');br(0xD0,'DRAW_PUT');ld('RY');a.ref('CMP',0xCD,'PY');br(0xD0,'DRAW_PUT');imm(14);st('GLYPH')
    a.label('DRAW_PUT');a.ref('LDY',0xAC,'RX');ld('GLYPH');indystore(0x82);inc('RX');ld('RX');cmp(30);br(0x90,'DRAW_CELL')
    ldy(30);a.label('PANEL');imm(ids['.']);indystore(0x82);a.op('INY',0xC8);a.imm('CPY',0xC0,40);br(0x90,'PANEL');inc('RY');ld('RY');cmp(22);br(0xB0,'DRAW_STATUS');jump('DRAW_ROW')
    a.label('DRAW_STATUS');a.imm('LDX',0xA2,0);a.label('STATUS_LOOP');a.abs('LDA',0xBD,0xA600);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,80);br(0x90,'STATUS_LOOP');ld('STATE');br(0xF0,'DRAW_DONE');cmp(1);br(0xD0,'SUCCESS_TEXT');a.imm('LDX',0xA2,0);a.label('CAUGHT_LOOP');a.abs('LDA',0xBD,0xA650);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,40);br(0x90,'CAUGHT_LOOP');ret()
    a.label('SUCCESS_TEXT');a.imm('LDX',0xA2,0);a.label('SUCCESS_LOOP');a.abs('LDA',0xBD,0xA678);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,40);br(0x90,'SUCCESS_LOOP')
    a.label('DRAW_DONE');ret()
    for var in ['PX','PY','EX','EY','NX','NY','CX','CY','STATE','TICKS','DELAY','ACTIVE','ARM','ENEMY_TIMER','JOY','DIR','FOUND','CAM','RX','RY','WX','GLYPH','SEARCH','BUDGET']:a.byte(var,0)
    code=a.finalize()
    parts=xex_segments(BASE);controller=bytearray(parts[0x2000])
    for old,new in [('DRAW_STAGE','INIT'),('HANDLE_INPUT','INPUT')]:
        offset=ol[old]-0x2000;controller[offset:offset+3]=bytes([0x4C])+struct.pack('<H',a.labels[new])
    parts[0x2000]=controller;parts[0x1000]=code;parts[MAP]=terrain
    for addr,base,stride in [(0xA500,MAP,48),(0xA540,SCREEN,40),(0xA580,SEEN,48)]:parts[addr]=b''.join(struct.pack('<H',base+y*stride) for y in range(22))
    font=bytearray(1024)
    patterns={'#':[255,129,189,165,165,189,129,255],'.':[0]*8,'B':[126,66,126,126,126,66,66,0],'T':[0,126,126,126,126,36,36,0],'C':[255,170,255,170,255,170,255,0],'R':[60,36,60,36,60,36,126,0],'K':[126,90,126,66,126,90,126,0],'S':[126,66,126,66,126,66,126,0],'G':[0,0,0,0,0,0,0,0],'D':[0]*8,'F':[0,24,24,24,24,24,24,0],'N':[0,24,24,24,24,24,24,0],'X':[129,66,36,24,24,36,66,129]}
    for s,p in patterns.items():font[ids[s]*8:ids[s]*8+8]=bytes(p)
    font[14*8:15*8]=bytes([24,60,24,126,24,36,66,0]);font[15*8:16*8]=bytes([60,126,90,126,60,60,102,0])
    # Uppercase HUD uses preserved cutscene font at codes 32..95, offset by 32.
    source=parts[0x3800]
    for c in range(32,96):font[c*8:c*8+8]=source[(c-32)*8:(c-32)*8+8]
    parts[FONT]=font
    def text(s):return s.ljust(40).encode('ascii')
    parts[0xA600]=text('BILLY: RUN TO REAR EXIT X!')+text('JOYSTICK 1 MOVE / START RESTART')
    parts[0xA650]=text('CAUGHT! START TO TRY AGAIN')
    parts[0xA678]=text('STAGE COMPLETE! START TO REPLAY STAGE')
    parts[0x3F00]=bytes([0x70]*3+[0x42,0,0xB0]+[2]*23+[0x41,0,0x3F])
    parts.pop(0x9800) # BFS scratch, not loaded placeholder
    parts[SCREEN]=bytes(960)
    data=encode_xex(parts);out.mkdir(parents=True,exist_ok=True)
    name='GasBlasters82_Stage1_Playable_v01.xex';(out/name).write_bytes(data)
    (out/'stage1_6502.asm').write_text('; Generated from tools/build_stage1.py; authoritative source is byte emitter\n    *= $1000\n'+'\n'.join(a.asm)+'\n')
    manifest={'output':name,'sha256':hashlib.sha256(data).hexdigest(),'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'stage_code_bytes':len(code),'labels':a.labels,'opening_labels':ol,'emulator_tested':False,'segments':[{ 'start':s,'bytes':len(b)} for s,b in sorted(parts.items())]}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
    m=build();print(m['output'],m['stage_code_bytes'],'code bytes',m['sha256'])
