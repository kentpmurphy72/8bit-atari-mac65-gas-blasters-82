#!/usr/bin/env python3
"""Offline 6502 emitter for Stage 1 room-screen v0.2; Python stdlib only. No baseline writes."""
import hashlib, json, struct
from pathlib import Path
from build_opening_sequence import Asm, xex_segments, encode_xex, assemble_controller, palette_data
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/stage1_v02'
BASE=ROOT/'assets/opening/GasBlasters82_OpeningSequence_v1.xex'
MAP=0xA000; FONT=0xAC00; SCREEN=0xB000; SEEN=0x9800

def build(out=OUT):
    meta=json.loads((ROOT/'assets/maps/taco_smell_stage1_v02.json').read_text())
    room_names=meta['room_order']
    room_rows=[(ROOT/'assets/maps'/meta['rooms'][r]['map_file']).read_text().splitlines() for r in room_names]
    rows=[row for room in room_rows for row in room]
    assert len(rows)==66 and all(len(row)==40 for row in rows)
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
    a.zp('LDA',0xA5,0x14);a.op('SEC',0x38);a.ref('SBC',0xED,'PREV_FRAME');br(0xD0,'HAVE_ELAPSED');imm(1)
    a.label('HAVE_ELAPSED');st('ELAPSED');a.zp('LDA',0xA5,0x14);st('PREV_FRAME')
    load(0xD01F);a.imm('AND',0x29,1);br(0xF0,'START_DOWN');imm(1);st('ARM');jump('FRAME_PLAY')
    a.label('START_DOWN');ld('ARM');br(0xF0,'FRAME_PLAY');call('INIT');ret()
    a.label('FRAME_PLAY');ld('STATE');br(0xF0,'PLAY');ret()
    a.label('PLAY');inc('TICKS');ld('ACTIVE');br(0xD0,'SPAWN_DONE')
    ld('DELAY');a.op('SEC',0x38);a.ref('SBC',0xED,'ELAPSED');br(0x90,'SPAWN_NOW');st('DELAY');br(0xD0,'SPAWN_DONE');a.label('SPAWN_NOW');imm(0);st('DELAY');imm(1);st('ACTIVE');call('CHECK_CAUGHT')
    a.label('SPAWN_DONE');ld('ROOM');st('LOOK_ROOM');ld('TICKS');a.imm('AND',0x29,7);br(0xD0,'ENEMY_TICK')
    ld('PX');st('NX');ld('PY');st('NY');load(0xD300);st('JOY')
    for bit,var,opcode in [(1,'NY',0xCE),(2,'NY',0xEE),(4,'NX',0xCE),(8,'NX',0xEE)]:
        ld('JOY');a.imm('AND',0x29,bit);br(0xD0,f'NO_{bit}');a.ref('DEC' if opcode==0xCE else 'INC',opcode,var);jump('PLAYER_STEP');a.label(f'NO_{bit}')
    jump('ENEMY_TICK')
    a.label('PLAYER_STEP');call('TRY_MOVE');call('CHECK_CAUGHT')
    ld('STATE');br(0xD0,'ENEMY_TICK');ld('ROOM');cmp(room_names.index(meta['objective']['room']));br(0xD0,'ENEMY_TICK');ld('PX');cmp(meta['objective']['tile'][0]);br(0xD0,'ENEMY_TICK');ld('PY');cmp(meta['objective']['tile'][1]);br(0xD0,'ENEMY_TICK');imm(2);st('STATE')
    a.label('ENEMY_TICK');ld('STATE');br(0xD0,'RENDER_FRAME');ld('ACTIVE');br(0xF0,'RENDER_FRAME')
    ld('ROOM');a.ref('CMP',0xCD,'EROOM');br(0xF0,'SAME_ROOM');call('ROOM_FOLLOW');jump('RENDER_FRAME')
    a.label('SAME_ROOM');imm(0);st('FOLLOW_TIMER');ld('SEARCH');br(0xF0,'NEW_CHASE');call('SEARCH_STEP');call('CHECK_CAUGHT');jump('RENDER_FRAME')
    a.label('NEW_CHASE');inc('ENEMY_TIMER');ld('ENEMY_TIMER');cmp(16);br(0x90,'RENDER_FRAME');imm(0);st('ENEMY_TIMER');call('CHASE');call('CHECK_CAUGHT')
    a.label('RENDER_FRAME');ld('STATE');br(0xD0,'RENDER_NOW');ld('TICKS');a.imm('AND',0x29,7);br(0xD0,'FRAME_DONE');a.label('RENDER_NOW');call('DRAW')
    a.label('FRAME_DONE');ret()
    a.label('CHECK_CAUGHT');ld('ACTIVE');br(0xF0,'CC_DONE');ld('ROOM');a.ref('CMP',0xCD,'EROOM');br(0xD0,'CC_DONE');ld('PX');a.ref('CMP',0xCD,'EX');br(0xD0,'CC_DONE');ld('PY');a.ref('CMP',0xCD,'EY');br(0xD0,'CC_DONE');imm(1);st('STATE')
    a.label('CC_DONE');ret()
    a.label('INIT');imm(0);store(0xD40E);st('STATE');st('TICKS');st('ACTIVE');st('ARM');st('ENEMY_TIMER');st('SEARCH');st('ROOM');st('EROOM');st('LOOK_ROOM');st('FOLLOW_TIMER')
    a.zp('LDA',0xA5,0x14);st('PREV_FRAME');imm(180);st('DELAY');imm(10);st('DOOR_Y_01');st('DOOR_Y_12')
    for xy,coord in [(meta['rooms']['dining']['player_spawn'],('PX','PY')),(next(e['xy'] for e in meta['rooms']['dining']['hazmat_spawns'] if e['enabled']),('EX','EY'))]:
        for var,value in zip(coord,xy):imm(value);st(var)
    for addr,value in [(0x230,0),(0x231,0x3F),(0xD402,0),(0xD403,0x3F),(0x2F4,0xAC),(0xD409,0xAC),(0x22F,0x22),(0xD400,0x22),(0x2C5,0x0E),(0xD017,0x0E),(0x2C6,0),(0xD018,0),(0x2C8,0),(0xD01A,0)]:imm(value);store(addr)
    imm(0x40);store(0xD40E);call('DRAW');ret()
    # Address helpers use NX/NY, return row pointer in $80. Caller uses Y=NX.
    a.label('MAP_PTR');ld('NY');a.op('ASL A',0x0A);st('ROW_OFFSET');a.ref('LDX',0xAE,'LOOK_ROOM');a.ref('LDA',0xBD,'ROOM_OFFSETS',idx=True);a.op('CLC',0x18);a.ref('ADC',0x6D,'ROW_OFFSET');a.op('TAX',0xAA);a.abs('LDA',0xBD,0xAA80);a.zp('STA',0x85,0x80);a.abs('LDA',0xBD,0xAA81);a.zp('STA',0x85,0x81);a.ref('LDY',0xAC,'NX');ret()
    a.label('SEEN_PTR');ld('NY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xAB40);a.zp('STA',0x85,0x82);a.abs('LDA',0xBD,0xAB41);a.zp('STA',0x85,0x83);a.ref('LDY',0xAC,'NX');ret()
    a.label('WALK');ld('NX');cmp(40);br(0xB0,'BLOCK');ld('NY');cmp(22);br(0xB0,'BLOCK');call('MAP_PTR');indyload(0x80);a.imm('AND',0x29,128);br(0xD0,'BLOCK');imm(1);ret()
    a.label('BLOCK');imm(0);ret()
    # BFS from Billy, recording a reverse direction at each discovered cell.
    # Two 16-bit FIFO pointers per coordinate array; at most 880 entries.
    a.label('CHASE');imm(1);st('SEARCH');ptr(SEEN,0x82);ldy(0);imm(0)
    a.imm('LDX',0xA2,3);a.label('CLEAR_PAGE');indystore(0x82);a.op('INY',0xC8);br(0xD0,'CLEAR_PAGE');a.zp('INC',0xE6,0x83);a.op('DEX',0xCA);br(0xD0,'CLEAR_PAGE')
    a.label('CLEAR_TAIL');indystore(0x82);a.op('INY',0xC8);a.imm('CPY',0xC0,112);br(0xD0,'CLEAR_TAIL')
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
    # A movement request is validated before committing either coordinates or room.
    a.label('TRY_MOVE');call('WALK');br(0xD0,'MOVE_PASSABLE');ret()
    a.label('MOVE_PASSABLE');call('MAP_PTR');indyload(0x80);a.imm('AND',0x29,127);cmp(ids['D']);br(0xF0,'DOOR_MOVE')
    ld('NX');st('PX');ld('NY');st('PY');ret()
    a.label('DOOR_MOVE')
    for i,link in enumerate(meta['transitions']):
        source=room_names.index(link['from']);target=room_names.index(link['to'])
        a.label(f'LINK_{i}');ld('ROOM');cmp(source);br(0xD0,f'LINK_{i+1}');ld('NX');cmp(link['trigger_tiles'][0][0]);br(0xD0,f'LINK_{i+1}')
        ld('NY');st('LINK_Y');imm(target);st('LOOK_ROOM');imm(link['entry_x']);st('NX');imm(0);st('WHO');call('FIND_ENTRY');br(0xD0,f'LINK_OK_{i}');ld('ROOM');st('LOOK_ROOM');ret()
        a.label(f'LINK_OK_{i}');ld('LINK_Y');st('DOOR_Y_01' if min(source,target)==0 else 'DOOR_Y_12');imm(target);st('ROOM');ld('NX');st('PX');ld('NY');st('PY');imm(0);st('SEARCH');st('ENEMY_TIMER')
        ld('ROOM');a.ref('CMP',0xCD,'EROOM');br(0xD0,f'LINK_DONE_{i}');imm(0);st('FOLLOW_TIMER')
        a.label(f'LINK_DONE_{i}');ret()
    a.label('LINK_4');ret()
    # Find the preferred inward entry, otherwise a cardinal neighbor. The same
    # helper avoids overlap with the other actor for both player and hazmat entry.
    a.label('FIND_ENTRY');ld('NX');st('ENTRY_X');ld('NY');st('ENTRY_Y');call('ENTRY_OK');br(0xF0,'ENTRY_ALTERNATES');ret()
    a.label('ENTRY_ALTERNATES')
    for i,(dx,dy) in enumerate([(0,-1),(0,1),(1,0),(-1,0)]):
        ld('ENTRY_X');add(dx);st('NX');ld('ENTRY_Y');add(dy);st('NY');call('ENTRY_OK');br(0xF0,f'ENTRY_NEXT_{i}');ret();a.label(f'ENTRY_NEXT_{i}')
    imm(0);ret()
    a.label('ENTRY_OK');call('WALK');br(0xD0,'ENTRY_WALKABLE');ret()
    a.label('ENTRY_WALKABLE');call('MAP_PTR');indyload(0x80);a.imm('AND',0x29,127);cmp(ids['D']);br(0xF0,'ENTRY_BAD');cmp(ids['X']);br(0xF0,'ENTRY_BAD')
    ld('WHO');br(0xD0,'AVOID_PLAYER');ld('ACTIVE');br(0xF0,'ENTRY_GOOD');ld('EROOM');a.ref('CMP',0xCD,'LOOK_ROOM');br(0xD0,'ENTRY_GOOD');ld('EX');a.ref('CMP',0xCD,'NX');br(0xD0,'ENTRY_GOOD');ld('EY');a.ref('CMP',0xCD,'NY');br(0xD0,'ENTRY_GOOD');jump('ENTRY_BAD')
    a.label('AVOID_PLAYER');ld('ROOM');a.ref('CMP',0xCD,'LOOK_ROOM');br(0xD0,'ENTRY_GOOD');ld('PX');a.ref('CMP',0xCD,'NX');br(0xD0,'ENTRY_GOOD');ld('PY');a.ref('CMP',0xCD,'NY');br(0xD0,'ENTRY_GOOD')
    a.label('ENTRY_BAD');imm(0);ret()
    a.label('ENTRY_GOOD');imm(1);ret()
    # Off-screen pursuit is a single queued adjacent link, not a respawn. Later
    # links are scheduled only after arrival in the intermediate room.
    a.label('ROOM_FOLLOW');imm(0);st('SEARCH');ld('FOLLOW_TIMER');br(0xD0,'FOLLOW_COUNTDOWN')
    ld('EROOM');a.ref('CMP',0xCD,'ROOM');br(0xB0,'QUEUE_LEFT')
    ld('EROOM');add(1);st('FROOM');imm(1);st('FX');ld('EROOM');br(0xF0,'USE_01');jump('USE_12')
    a.label('QUEUE_LEFT');ld('EROOM');add(-1);st('FROOM');imm(38);st('FX');ld('EROOM');cmp(1);br(0xF0,'USE_01')
    a.label('USE_12');ld('DOOR_Y_12');jump('QUEUE_FOLLOW')
    a.label('USE_01');ld('DOOR_Y_01')
    a.label('QUEUE_FOLLOW');st('FY');imm(90);st('FOLLOW_TIMER');ret()
    a.label('FOLLOW_COUNTDOWN');ld('FOLLOW_TIMER');a.op('SEC',0x38);a.ref('SBC',0xED,'ELAPSED');br(0x90,'FOLLOW_EXPIRED');st('FOLLOW_TIMER');br(0xF0,'FOLLOW_ARRIVE');ret()
    a.label('FOLLOW_EXPIRED');imm(0);st('FOLLOW_TIMER')
    a.label('FOLLOW_ARRIVE');ld('FROOM');st('LOOK_ROOM');ld('FX');st('NX');ld('FY');st('NY');imm(1);st('WHO');call('FIND_ENTRY');br(0xF0,'FOLLOW_RETRY')
    ld('FROOM');st('EROOM');ld('NX');st('EX');ld('NY');st('EY');imm(0);st('ENEMY_TIMER');jump('FOLLOW_RESTORE')
    a.label('FOLLOW_RETRY');imm(1);st('FOLLOW_TIMER')
    a.label('FOLLOW_RESTORE');ld('ROOM');st('LOOK_ROOM');call('CHECK_CAUGHT');ret()
    # Fixed 40x22 screen: no scrolling or side panel.
    a.label('DRAW');ld('ROOM');st('LOOK_ROOM');imm(0);st('RY')
    a.label('DRAW_ROW');ld('RY');st('NY');imm(0);st('NX');call('MAP_PTR');ld('RY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xAB10);a.zp('STA',0x85,0x82);a.abs('LDA',0xBD,0xAB11);a.zp('STA',0x85,0x83);ldy(0)
    # Copy a row first, then overlay actors once. Avoid per-cell actor tests.
    a.label('DRAW_CELL');indyload(0x80);a.imm('AND',0x29,127);indystore(0x82);a.op('INY',0xC8);a.imm('CPY',0xC0,40);br(0x90,'DRAW_CELL')
    inc('RY');ld('RY');cmp(22);br(0xB0,'DRAW_ACTORS');jump('DRAW_ROW')
    a.label('DRAW_ACTORS');ld('ACTIVE');br(0xF0,'OVERLAY_PLAYER');ld('EROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'OVERLAY_PLAYER')
    ld('EX');st('NX');ld('EY');st('NY');imm(15);st('GLYPH');call('DRAW_ACTOR')
    a.label('OVERLAY_PLAYER');ld('PX');st('NX');ld('PY');st('NY');imm(14);st('GLYPH');call('DRAW_ACTOR');jump('DRAW_STATUS')
    a.label('DRAW_ACTOR');ld('NY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xAB10);a.zp('STA',0x85,0x82);a.abs('LDA',0xBD,0xAB11);a.zp('STA',0x85,0x83);a.ref('LDY',0xAC,'NX');ld('GLYPH');indystore(0x82);ret()
    a.label('DRAW_STATUS');a.imm('LDX',0xA2,0);a.label('STATUS_LOOP');a.abs('LDA',0xBD,0x2800);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,80);br(0x90,'STATUS_LOOP');ld('STATE');br(0xF0,'DRAW_DONE');cmp(1);br(0xD0,'SUCCESS_TEXT');a.imm('LDX',0xA2,0);a.label('CAUGHT_LOOP');a.abs('LDA',0xBD,0x2850);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,40);br(0x90,'CAUGHT_LOOP');ret()
    a.label('SUCCESS_TEXT');a.imm('LDX',0xA2,0);a.label('SUCCESS_LOOP');a.abs('LDA',0xBD,0x2878);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,40);br(0x90,'SUCCESS_LOOP')
    a.label('DRAW_DONE');ret()
    for var in ['PX','PY','EX','EY','NX','NY','CX','CY','STATE','TICKS','DELAY','ACTIVE','ARM','ENEMY_TIMER','JOY','DIR','FOUND','RX','RY','GLYPH','SEARCH','BUDGET','ROOM','EROOM','LOOK_ROOM','ROW_OFFSET','FOLLOW_TIMER','FROOM','FX','FY','WHO','ENTRY_X','ENTRY_Y','DOOR_Y_01','DOOR_Y_12','LINK_Y','PREV_FRAME','ELAPSED']:a.byte(var,0)
    a.byte('ROOM_OFFSETS',0,44,88)
    code=a.finalize()
    parts=xex_segments(BASE);controller=bytearray(parts[0x2000])
    for old,new in [('DRAW_STAGE','INIT'),('HANDLE_INPUT','INPUT')]:
        offset=ol[old]-0x2000;controller[offset:offset+3]=bytes([0x4C])+struct.pack('<H',a.labels[new])
    parts[0x2000]=controller;parts[0x1000]=code;parts[MAP]=terrain
    parts[0xAA80]=b''.join(struct.pack('<H',MAP+r*880+y*40) for r in range(3) for y in range(22))
    for addr,base in [(0xAB10,SCREEN),(0xAB40,SEEN)]:parts[addr]=b''.join(struct.pack('<H',base+y*40) for y in range(22))
    font=bytearray(1024)
    patterns={'#':[255,129,189,165,165,189,129,255],'.':[0]*8,'B':[126,66,126,126,126,66,66,0],'T':[0,126,126,126,126,36,36,0],'C':[255,170,255,170,255,170,255,0],'R':[60,36,60,36,60,36,126,0],'K':[126,90,126,66,126,90,126,0],'S':[126,66,126,66,126,66,126,0],'G':[0,0,0,0,0,0,0,0],'D':[0]*8,'F':[0,24,24,24,24,24,24,0],'N':[0,24,24,24,24,24,24,0],'X':[129,66,36,24,24,36,66,129]}
    for s,p in patterns.items():font[ids[s]*8:ids[s]*8+8]=bytes(p)
    font[14*8:15*8]=bytes([24,60,24,126,24,36,66,0]);font[15*8:16*8]=bytes([60,126,90,126,60,60,102,0])
    # Uppercase HUD uses preserved cutscene font at codes 32..95, offset by 32.
    source=parts[0x3800]
    for c in range(32,96):font[c*8:c*8+8]=source[(c-32)*8:(c-32)*8+8]
    parts[FONT]=font
    def text(s):return s.ljust(40).encode('ascii')
    parts[0x2800]=text('BILLY: RUN TO REAR EXIT X!')+text('JOYSTICK 1 MOVE / START RESTART')
    parts[0x2850]=text('CAUGHT! START TO TRY AGAIN')
    parts[0x2878]=text('STAGE COMPLETE! START TO REPLAY STAGE')
    parts[0x3F00]=bytes([0x70]*3+[0x42,0,0xB0]+[2]*23+[0x41,0,0x3F])
    parts.pop(0x9800) # BFS scratch, not loaded placeholder
    parts[SCREEN]=bytes(960)
    data=encode_xex(parts);out.mkdir(parents=True,exist_ok=True)
    name='GasBlasters82_Stage1_Playable_v02.xex';(out/name).write_bytes(data)
    (out/'stage1_6502.asm').write_text('; Generated from tools/build_stage1_v02.py; authoritative source is byte emitter\n    *= $1000\n'+'\n'.join(a.asm)+'\n')
    manifest={'output':name,'sha256':hashlib.sha256(data).hexdigest(),'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'stage_code_bytes':len(code),'labels':a.labels,'opening_labels':ol,'emulator_tested':False,'segments':[{ 'start':s,'bytes':len(b)} for s,b in sorted(parts.items())]}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
    m=build();print(m['output'],m['stage_code_bytes'],'code bytes',m['sha256'])
