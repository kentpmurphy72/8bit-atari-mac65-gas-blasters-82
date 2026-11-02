#!/usr/bin/env python3
"""Offline 6502 emitter for Stage 1 gameplay-pressure v0.3; Python stdlib only. No baseline writes."""
import hashlib, json, struct
from pathlib import Path
from build_opening_sequence import Asm, xex_segments, encode_xex, assemble_controller, palette_data
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/stage1_v03'
BASE=ROOT/'assets/opening/GasBlasters82_OpeningSequence_v1.xex'
MAP=0xA000; FONT=0xAC00; SCREEN=0xB000; SEEN=0x9800

class StageAsm(Asm):
    """Same checked emitter, expanded stage-only $1000-$1FFF budget."""
    def finalize(self):
        for offset,label,kind in self.patches:
            addr=self.labels[label]
            if kind=='abs':self.buf[offset:offset+2]=struct.pack('<H',addr)
            else:
                rel=addr-(self.base+offset+1)
                if not -128<=rel<=127:raise ValueError(f'branch to {label}: {rel}')
                self.buf[offset]=rel&255
        assert len(self.buf)<=0x1000, 'Stage code overlaps opening controller'
        return bytes(self.buf)

def build(out=OUT):
    rules=json.loads((ROOT/'assets/gameplay/taco_smell_stage1_v03_rules.json').read_text())
    units=rules['hazmat']['units'];blast=rules['blast']
    fields=['EX','EY','EROOM','ACTIVE','DELAY','ENEMY_TIMER','FOLLOW_TIMER','FROOM','FX','FY','STUN','SEPARATE','AWAIT','ENTRY_GRACE','ENTRY_FRESH']
    meta=json.loads((ROOT/'assets/maps/taco_smell_stage1_v02.json').read_text())
    room_names=meta['room_order']
    room_rows=[(ROOT/'assets/maps'/meta['rooms'][r]['map_file']).read_text().splitlines() for r in room_names]
    rows=[row for room in room_rows for row in room]
    assert len(rows)==66 and all(len(row)==40 for row in rows)
    symbols=list(meta['terrain']); ids={s:i for i,s in enumerate(symbols)}
    terrain=bytes(ids[s]|(128 if meta['terrain'][s]['solid'] else 0) for row in rows for s in row)
    palettes={k:palette_data(xex_segments(ROOT/p)[0x2000],b'')[0] for k,p in [('title','assets/title/Title_Option3_Original.xex'),('crew','assets/intro/meet_the_crew_v4.xex'),('arrival','assets/arrival/arrival_v3.xex')]}
    original,_=assemble_controller(palettes); ol=original.labels
    a=StageAsm(0x1000)
    def imm(n):a.imm('LDA',0xA9,n)
    def ld(n):a.ref('LDA',0xAD,n)
    def st(n):a.ref('STA',0x8D,n)
    def inc(n):a.ref('INC',0xEE,n)
    def dec(n):a.ref('DEC',0xCE,n)
    def call(n):a.ref('JSR',0x20,n)
    def jump(n):a.ref('JMP',0x4C,n)
    def br(op,n):
        if n in {'PLAYER_DONE','WORKER_SAVE'}:
            skip=f'LONG_{len(a.buf)}';inverse={0xF0:0xD0,0xD0:0xF0,0x90:0xB0,0xB0:0x90}[op]
            a.branch('branch inverse',inverse,skip);a.ref('JMP',0x4C,n);a.label(skip)
        else:a.branch({0xF0:'BEQ',0xD0:'BNE',0x90:'BCC',0xB0:'BCS'}[op],op,n)
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
    def ldxvar(n):a.ref('LDX',0xAE,n)
    def indexed_load(n):a.ref('LDA',0xBD,n,idx=True)
    def indexed_store(n):a.ref('STA',0x9D,n,idx=True)
    def countdown(n):
        # Saturating elapsed-VBI subtraction, also valid across RTCLOK wrap.
        tag=f'TIMER_{len(a.buf)}';ld(n);br(0xF0,tag);a.op('SEC',0x38);a.ref('SBC',0xED,'ELAPSED');br(0xB0,tag+'_SAVE');imm(0);a.label(tag+'_SAVE');st(n);a.label(tag)
    # Dispatcher replaces only the first LDA of original HANDLE_INPUT.
    a.label('INPUT');load(ol['SCENE']);cmp(3);br(0xF0,'FRAME');load(ol['SCENE']);a.abs('JMP',0x4C,ol['HANDLE_INPUT']+3)
    a.label('FRAME')
    a.zp('LDA',0xA5,0x14);a.op('SEC',0x38);a.ref('SBC',0xED,'PREV_FRAME');br(0xD0,'HAVE_ELAPSED');imm(1)
    a.label('HAVE_ELAPSED');st('ELAPSED');a.zp('LDA',0xA5,0x14);st('PREV_FRAME')
    load(0xD01F);a.imm('AND',0x29,1);br(0xF0,'START_DOWN');imm(1);st('ARM');jump('FRAME_PLAY')
    a.label('START_DOWN');ld('ARM');br(0xF0,'FRAME_PLAY');call('INIT');ret()
    a.label('FRAME_PLAY');ld('STATE');br(0xF0,'PLAY');ret()
    a.label('PLAY');inc('TICKS');ld('ROOM');st('LOOK_ROOM');countdown('COOLDOWN');countdown('VISUAL')
    imm(255);st('TARGET');call('PLAYER_INPUT');ld('TICKS');a.imm('AND',0x29,7);br(0xD0,'NO_SEP_OPPORTUNITY');imm(0)
    for i in range(3):a.ref('STA',0x8D,f'SEP_{i}')
    a.label('NO_SEP_OPPORTUNITY');call('CHECK_CAUGHT')
    ld('STATE');br(0xD0,'RENDER_FRAME');call('UPDATE_WORKERS');call('NAV_FRAME');call('CHECK_CAUGHT')
    a.label('RENDER_FRAME');call('DRAW');ret()
    a.label('PLAYER_INPUT');load(0xD300);st('JOY');load(0xD010);a.imm('AND',0x29,1);br(0xD0,'FIRE_RELEASED')
    ld('FIRE_HELD');br(0xD0,'PLAYER_DONE');imm(1);st('FIRE_HELD');ld('COOLDOWN');br(0xD0,'PLAYER_DONE');call('AIM');ld('AIM_DIR');br(0xF0,'PLAYER_DONE');call('BLAST');ret()
    a.label('FIRE_RELEASED');imm(0);st('FIRE_HELD');ld('TICKS');a.imm('AND',0x29,7);br(0xD0,'PLAYER_DONE')
    ld('PX');st('NX');ld('PY');st('NY')
    for bit,var,opcode in [(1,'NY',0xCE),(2,'NY',0xEE),(4,'NX',0xCE),(8,'NX',0xEE)]:
        ld('JOY');a.imm('AND',0x29,bit);br(0xD0,f'NO_{bit}');a.ref('DEC' if opcode==0xCE else 'INC',opcode,var);jump('PLAYER_STEP');a.label(f'NO_{bit}')
    jump('PLAYER_OPPORTUNITY')
    a.label('PLAYER_STEP');call('TRY_MOVE')
    a.label('PLAYER_OPPORTUNITY')
    ld('ROOM');cmp(2);br(0xD0,'PLAYER_DONE');ld('PX');cmp(39);br(0xD0,'PLAYER_DONE');ld('PY');cmp(10);br(0xD0,'PLAYER_DONE');imm(2);st('STATE')
    a.label('PLAYER_DONE');ret()
    a.label('CHECK_CAUGHT');imm(0);st('COLLISION_ID')
    a.label('CONTACT_LOOP');ldxvar('COLLISION_ID');indexed_load('E_ACTIVE');br(0xF0,'CONTACT_NEXT');indexed_load('E_STUN');br(0xD0,'CONTACT_NEXT');indexed_load('E_SEPARATE');br(0xD0,'CONTACT_NEXT');indexed_load('E_ENTRY_GRACE');br(0xD0,'CONTACT_NEXT');indexed_load('E_EROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'CONTACT_NEXT');indexed_load('E_EX');a.ref('CMP',0xCD,'PX');br(0xD0,'CONTACT_NEXT');indexed_load('E_EY');a.ref('CMP',0xCD,'PY');br(0xD0,'CONTACT_NEXT');imm(1);st('STATE');ret()
    a.label('CONTACT_NEXT');inc('COLLISION_ID');ld('COLLISION_ID');cmp(3);br(0x90,'CONTACT_LOOP');ret()
    a.label('INIT');imm(0);store(0xD40E)
    for var in ['STATE','TICKS','ARM','SEARCH','ROOM','LOOK_ROOM','COOLDOWN','VISUAL','RAY_LEN','CURRENT']:st(var)
    imm(1);st('FIRE_HELD');st('FULL_DRAW');imm(255);st('NAV_ROOM')
    for i in range(4):a.ref('STA',0x8D,f'PREV_ROOM_{i}')
    a.zp('LDA',0xA5,0x14);st('PREV_FRAME');imm(10);st('DOOR_Y_01');st('DOOR_Y_12')
    for coord,value in zip(('PX','PY'),meta['rooms']['dining']['player_spawn']):imm(value);st(coord)
    for i,unit in enumerate(units):
        initial={f:0 for f in fields};initial.update(EX=unit['spawn'][0],EY=unit['spawn'][1],EROOM=i,DELAY=unit.get('activate_after_frames',unit.get('activate_after_first_room_entry_frames')),AWAIT=int(i>0))
        for field in fields:
            imm(initial[field]);a.ref('STA',0x8D,f'{field}_{i}')
    for addr,value in [(0x230,0),(0x231,0x3F),(0xD402,0),(0xD403,0x3F),(0x2F4,0xAC),(0xD409,0xAC),(0x22F,0x22),(0xD400,0x22),(0x2C5,0x0E),(0xD017,0x0E),(0x2C6,0),(0xD018,0),(0x2C8,0),(0xD01A,0)]:imm(value);store(addr)
    imm(0x40);store(0xD40E);call('DRAW');ret()
    # Address helpers use NX/NY, return row pointer in $80. Caller uses Y=NX.
    a.label('MAP_PTR');ld('NY');a.op('ASL A',0x0A);st('ROW_OFFSET');a.ref('LDX',0xAE,'LOOK_ROOM');a.ref('LDA',0xBD,'ROOM_OFFSETS',idx=True);a.op('CLC',0x18);a.ref('ADC',0x6D,'ROW_OFFSET');a.op('TAX',0xAA);a.abs('LDA',0xBD,0xAA80);a.zp('STA',0x85,0x80);a.abs('LDA',0xBD,0xAA81);a.zp('STA',0x85,0x81);a.ref('LDY',0xAC,'NX');ret()
    a.label('SEEN_PTR');ld('NY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xAB40);a.zp('STA',0x85,0x82);a.abs('LDA',0xBD,0xAB41);a.zp('STA',0x85,0x83);a.ref('LDY',0xAC,'NX');ret()
    a.label('WALK');ld('NX');cmp(40);br(0xB0,'BLOCK');ld('NY');cmp(22);br(0xB0,'BLOCK');call('MAP_PTR');indyload(0x80);a.imm('AND',0x29,128);br(0xD0,'BLOCK');imm(1);ret()
    a.label('BLOCK');imm(0);ret()
    # BFS from Billy, recording a reverse direction at each discovered cell.
    # Two 16-bit FIFO pointers per coordinate array; at most 880 entries.
    a.label('CHASE');ld('PX');st('NAV_X');ld('PY');st('NAV_Y');ld('ROOM');st('NAV_ROOM');imm(1);st('SEARCH');ptr(SEEN,0x82);ldy(0);imm(0)
    a.imm('LDX',0xA2,3);a.label('CLEAR_PAGE');indystore(0x82);a.op('INY',0xC8);br(0xD0,'CLEAR_PAGE');a.zp('INC',0xE6,0x83);a.op('DEX',0xCA);br(0xD0,'CLEAR_PAGE')
    a.label('CLEAR_TAIL');indystore(0x82);a.op('INY',0xC8);a.imm('CPY',0xC0,112);br(0xD0,'CLEAR_TAIL')
    for zp,addr in [(0x84,0xB400),(0x86,0xB900),(0x88,0xB400),(0x8A,0xB900)]:ptr(addr,zp)
    ld('PX');st('NX');ld('PY');st('NY');call('SEEN_PTR');imm(5);indystore(0x82);call('ENQUEUE')
    a.label('SEARCH_STEP');imm(8);st('BUDGET')
    a.label('BFS_LOOP');a.zp('LDA',0xA5,0x84);a.zp('CMP',0xC5,0x88);br(0xD0,'POP');a.zp('LDA',0xA5,0x85);a.zp('CMP',0xC5,0x89);br(0xD0,'POP');imm(0);st('SEARCH');ret()
    a.label('POP');ldy(0);indyload(0x88);st('CX');indyload(0x8A);st('CY');ptrinc(0x88);ptrinc(0x8A)
    # examine neighbors; stop BFS as soon as enemy reached
    for i,(dx,dy,reverse) in enumerate([(0,-1,2),(0,1,1),(-1,0,4),(1,0,3)]):
        ld('CX');add(dx);st('NX');ld('CY');add(dy);st('NY');imm(reverse);st('DIR');call('VISIT')
    dec('BUDGET');br(0xF0,'SEARCH_YIELD');jump('BFS_LOOP');a.label('SEARCH_YIELD');ret()
    a.label('VISIT');call('WALK');br(0xF0,'VISIT_DONE');call('SEEN_PTR');indyload(0x82);br(0xD0,'VISIT_DONE');ld('DIR');indystore(0x82);call('ENQUEUE')
    a.label('VISIT_DONE');ret()
    a.label('ENQUEUE');ldy(0);ld('NX');indystore(0x84);ld('NY');indystore(0x86);ptrinc(0x84);ptrinc(0x86);ret()
    # A movement request is validated before committing either coordinates or room.
    a.label('TRY_MOVE');call('WALK');br(0xD0,'MOVE_PASSABLE');ret()
    a.label('MOVE_PASSABLE');call('MAP_PTR');indyload(0x80);a.imm('AND',0x29,127);cmp(ids['D']);br(0xF0,'DOOR_MOVE')
    ld('NX');st('PX');ld('NY');st('PY');ret()
    a.label('DOOR_MOVE')
    for i,link in enumerate(meta['transitions']):
        source=room_names.index(link['from']);target=room_names.index(link['to'])
        a.label(f'LINK_{i}');ld('ROOM');cmp(source);br(0xD0,f'LINK_{i+1}');ld('NX');cmp(link['trigger_tiles'][0][0]);br(0xD0,f'LINK_{i+1}')
        ld('NY');st('LINK_Y');imm(target);st('LOOK_ROOM');imm(link['entry_x']);st('NX');imm(0);st('WHO');call('FIND_ENTRY');br(0xD0,f'LINK_OK_{i}');ld('ROOM');st('LOOK_ROOM');ret()
        a.label(f'LINK_OK_{i}');ld('LINK_Y');st('DOOR_Y_01' if min(source,target)==0 else 'DOOR_Y_12');imm(target);st('ROOM');ld('NX');st('PX');ld('NY');st('PY');imm(link['entry_x']);st('NX');ld('LINK_Y');st('NY');call('MARK_ENTRY_GRACE');imm(0);st('SEARCH');imm(1);st('FULL_DRAW');imm(255);st('NAV_ROOM');ret()
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
    call('OCCUPIED');br(0xD0,'ENTRY_BAD');ld('WHO');br(0xF0,'ENTRY_GOOD');ld('ROOM');a.ref('CMP',0xCD,'LOOK_ROOM');br(0xD0,'ENTRY_GOOD');ld('PX');a.ref('CMP',0xCD,'NX');br(0xD0,'ENTRY_GOOD');ld('PY');a.ref('CMP',0xCD,'NY');br(0xD0,'ENTRY_GOOD')
    a.label('ENTRY_BAD');imm(0);ret()
    a.label('ENTRY_GOOD');imm(1);ret()
    # Off-screen pursuit is a single queued adjacent link, not a respawn. Later
    # links are scheduled only after arrival in the intermediate room.
    a.label('ROOM_FOLLOW');ld('FOLLOW_TIMER');br(0xD0,'FOLLOW_COUNTDOWN')
    ld('EROOM');a.ref('CMP',0xCD,'ROOM');br(0xB0,'QUEUE_LEFT')
    ld('EROOM');add(1);st('FROOM');imm(1);st('FX');ld('EROOM');br(0xF0,'USE_01');jump('USE_12')
    a.label('QUEUE_LEFT');ld('EROOM');add(-1);st('FROOM');imm(38);st('FX');ld('EROOM');cmp(1);br(0xF0,'USE_01')
    a.label('USE_12');ld('DOOR_Y_12');jump('QUEUE_FOLLOW')
    a.label('USE_01');ld('DOOR_Y_01')
    a.label('QUEUE_FOLLOW');st('FY');imm(rules['hazmat']['door_follow_delay_frames']);st('FOLLOW_TIMER');ret()
    a.label('FOLLOW_COUNTDOWN');ld('FOLLOW_TIMER');a.op('SEC',0x38);a.ref('SBC',0xED,'ELAPSED');br(0x90,'FOLLOW_EXPIRED');st('FOLLOW_TIMER');br(0xF0,'FOLLOW_ARRIVE');ret()
    a.label('FOLLOW_EXPIRED');imm(0);st('FOLLOW_TIMER')
    a.label('FOLLOW_ARRIVE');ld('FROOM');st('LOOK_ROOM');ld('FX');st('NX');ld('FY');st('NY');imm(1);st('WHO');call('FIND_ENTRY');br(0xF0,'FOLLOW_RETRY')
    ld('FROOM');st('EROOM');ld('NX');st('EX');ld('NY');st('EY');imm(0);st('ENEMY_TIMER');jump('FOLLOW_RESTORE')
    a.label('FOLLOW_RETRY');imm(1);st('FOLLOW_TIMER')
    a.label('FOLLOW_RESTORE');ld('ROOM');st('LOOK_ROOM');ret()
    # Indexed persistent identity -> scratch context. Never duplicate an entity.
    a.label('LOAD_WORKER');ldxvar('CURRENT')
    for field in fields:indexed_load('E_'+field);st(field)
    ret()
    a.label('SAVE_WORKER');ldxvar('CURRENT')
    for field in fields:ld(field);indexed_store('E_'+field)
    ret()
    a.label('UPDATE_WORKERS');imm(0);st('CURRENT')
    a.label('WORKER_LOOP');call('LOAD_WORKER');ld('ACTIVE');br(0xD0,'WORKER_ACTIVE');ld('AWAIT');br(0xF0,'SPAWN_COUNTDOWN');ld('ROOM');a.ref('CMP',0xCD,'EROOM');br(0xF0,'FIRST_ENTRY');jump('WORKER_SAVE')
    a.label('FIRST_ENTRY');imm(0);st('AWAIT');jump('WORKER_SAVE')
    a.label('SPAWN_COUNTDOWN');countdown('DELAY');ld('DELAY');br(0xF0,'WORKER_SPAWN');jump('WORKER_SAVE')
    a.label('WORKER_SPAWN');imm(1);st('ACTIVE');ldxvar('CURRENT');indexed_load('CADENCE');st('ENEMY_TIMER');jump('WORKER_SAVE')
    a.label('WORKER_ACTIVE');ld('ENTRY_FRESH');br(0xF0,'GRACE_TICK');imm(0);st('ENTRY_FRESH');jump('GRACE_DONE')
    a.label('GRACE_TICK');countdown('ENTRY_GRACE')
    a.label('GRACE_DONE');ld('EROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'FOLLOW_NOT_CANCELLED');imm(0);st('FOLLOW_TIMER')
    a.label('FOLLOW_NOT_CANCELLED');ld('STUN');br(0xF0,'WORKER_MOBILE');ld('CURRENT');a.ref('CMP',0xCD,'TARGET');br(0xD0,'STUN_TICK');jump('WORKER_SAVE')
    a.label('STUN_TICK');countdown('STUN');ld('STUN');br(0xD0,'WORKER_SAVE');ld('EROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'WORKER_SAVE');ld('EX');a.ref('CMP',0xCD,'PX');br(0xD0,'WORKER_SAVE');ld('EY');a.ref('CMP',0xCD,'PY');br(0xD0,'WORKER_SAVE');imm(1);st('SEPARATE');jump('WORKER_SAVE')
    a.label('WORKER_MOBILE');ld('EROOM');a.ref('CMP',0xCD,'ROOM');br(0xF0,'WORKER_HERE');call('ROOM_FOLLOW');jump('WORKER_SAVE')
    a.label('WORKER_HERE');imm(0);st('FOLLOW_TIMER');countdown('ENEMY_TIMER');ld('ENEMY_TIMER');br(0xD0,'WORKER_SAVE');call('NAV_MOVE');ldxvar('CURRENT');indexed_load('CADENCE');st('ENEMY_TIMER')
    a.label('WORKER_SAVE');call('SAVE_WORKER');inc('CURRENT');ld('CURRENT');cmp(3);br(0xB0,'WORKERS_DONE');jump('WORKER_LOOP')
    a.label('WORKERS_DONE');ld('ROOM');st('LOOK_ROOM');ret()
    # Exactly one shared 8-cell search slice; pursuit uses known directions or a
    # collision-checked deterministic fallback while the shared field is growing.
    a.label('NAV_FRAME');ld('ROOM');st('LOOK_ROOM');ld('SEARCH');br(0xF0,'NAV_IDLE');call('SEARCH_STEP');ret()
    a.label('NAV_IDLE');ld('NAV_ROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'NAV_REBUILD');ld('NAV_X');a.ref('CMP',0xCD,'PX');br(0xD0,'NAV_REBUILD');ld('NAV_Y');a.ref('CMP',0xCD,'PY');br(0xD0,'NAV_REBUILD');ret()
    a.label('NAV_REBUILD');call('CHASE');ret()
    a.label('NAV_MOVE');ld('ROOM');st('LOOK_ROOM');imm(1);st('WHO');ld('NAV_ROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'NAV_GREEDY');ld('EX');st('NX');ld('EY');st('NY');call('SEEN_PTR');indyload(0x82);cmp(1);br(0x90,'NAV_GREEDY');cmp(5);br(0xB0,'NAV_GREEDY');add(-1);st('MOVE_DIR');call('MOVE_DIRECTION');br(0xF0,'NAV_GREEDY');ret()
    a.label('NAV_GREEDY');ld('EX');a.ref('CMP',0xCD,'PX');br(0xF0,'NAV_VERTICAL');br(0x90,'NAV_RIGHT');imm(2);jump('NAV_CHOOSE')
    a.label('NAV_RIGHT');imm(3);jump('NAV_CHOOSE')
    a.label('NAV_VERTICAL');ld('EY');a.ref('CMP',0xCD,'PY');br(0x90,'NAV_DOWN');imm(0);jump('NAV_CHOOSE')
    a.label('NAV_DOWN');imm(1)
    a.label('NAV_CHOOSE');st('MOVE_DIR');imm(4);st('MOVE_TRIES')
    a.label('NAV_TRY');call('MOVE_DIRECTION');br(0xD0,'NAV_MOVE_DONE');ld('MOVE_DIR');add(1);a.imm('AND',0x29,3);st('MOVE_DIR');dec('MOVE_TRIES');br(0xD0,'NAV_TRY')
    a.label('NAV_MOVE_DONE');ret()
    a.label('MOVE_DIRECTION');ldxvar('MOVE_DIR');indexed_load('DX');a.op('CLC',0x18);a.ref('ADC',0x6D,'EX');st('NX');indexed_load('DY');a.op('CLC',0x18);a.ref('ADC',0x6D,'EY');st('NY');call('RAY_WALK');br(0xF0,'MOVE_BLOCKED');call('OCCUPIED');br(0xD0,'MOVE_BLOCKED');ld('NX');st('EX');ld('NY');st('EY');imm(1);ret()
    a.label('MOVE_BLOCKED');imm(0);ret()
    # Shared occupancy check ignores only the worker currently being moved.
    a.label('OCCUPIED');imm(0);st('OCC_ID')
    a.label('OCC_LOOP');ld('WHO');br(0xF0,'OCC_EXAMINE');ld('OCC_ID');a.ref('CMP',0xCD,'CURRENT');br(0xF0,'OCC_NEXT')
    a.label('OCC_EXAMINE');ldxvar('OCC_ID');indexed_load('E_ACTIVE');br(0xF0,'OCC_NEXT');indexed_load('E_EROOM');a.ref('CMP',0xCD,'LOOK_ROOM');br(0xD0,'OCC_NEXT');indexed_load('E_EX');a.ref('CMP',0xCD,'NX');br(0xD0,'OCC_NEXT');indexed_load('E_EY');a.ref('CMP',0xCD,'NY');br(0xD0,'OCC_NEXT');imm(1);ret()
    a.label('OCC_NEXT');inc('OCC_ID');ld('OCC_ID');cmp(3);br(0x90,'OCC_LOOP');imm(0);ret()
    a.label('MARK_ENTRY_GRACE');imm(0);st('COLLISION_ID')
    a.label('MARK_GRACE_LOOP');ldxvar('COLLISION_ID');indexed_load('E_ACTIVE');br(0xF0,'MARK_GRACE_NEXT');indexed_load('E_EROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'MARK_GRACE_NEXT');indexed_load('E_EX');a.ref('CMP',0xCD,'NX');br(0xD0,'MARK_GRACE_NEXT');indexed_load('E_EY');a.ref('CMP',0xCD,'NY');br(0xD0,'MARK_GRACE_NEXT');imm(rules['hazmat']['player_entry_grace_frames']);indexed_store('E_ENTRY_GRACE');imm(1);indexed_store('E_ENTRY_FRESH')
    a.label('MARK_GRACE_NEXT');inc('COLLISION_ID');ld('COLLISION_ID');cmp(3);br(0x90,'MARK_GRACE_LOOP');ret()
    a.label('AIM');imm(0);st('AIM_DIR')
    for bit,direction in [(1,1),(2,2),(4,3),(8,4)]:
        ld('JOY');a.imm('AND',0x29,bit);br(0xD0,f'AIM_NEXT_{bit}');imm(direction);st('AIM_DIR');ret();a.label(f'AIM_NEXT_{bit}')
    ret()
    a.label('STEP_AIM');ld('AIM_DIR');add(-1);a.op('TAX',0xAA);indexed_load('DX');a.op('CLC',0x18);a.ref('ADC',0x6D,'NX');st('NX');indexed_load('DY');a.op('CLC',0x18);a.ref('ADC',0x6D,'NY');st('NY');ret()
    # Neither rays, navigation nor knockback cross linked/exterior exit triggers.
    a.label('RAY_WALK');call('WALK');br(0xD0,'RAY_PASSABLE');ret()
    a.label('RAY_PASSABLE');call('MAP_PTR');indyload(0x80);a.imm('AND',0x29,127);cmp(ids['D']);br(0xF0,'RAY_BLOCKED');cmp(ids['X']);br(0xF0,'RAY_BLOCKED');imm(1);ret()
    a.label('RAY_BLOCKED');imm(0);ret()
    a.label('BLAST');imm(blast['cooldown_frames']);st('COOLDOWN');imm(blast['visual_frames']);st('VISUAL');ld('ROOM');st('RAY_ROOM');st('LOOK_ROOM');ld('PX');st('RAY_X');st('NX');ld('PY');st('RAY_Y');st('NY');imm(0);st('RAY_LEN');imm(255);st('TARGET')
    a.label('BLAST_RAY');call('STEP_AIM');call('RAY_WALK');br(0xF0,'BLAST_DONE');inc('RAY_LEN');imm(0);st('COLLISION_ID')
    a.label('BLAST_TARGET');ldxvar('COLLISION_ID');indexed_load('E_ACTIVE');br(0xF0,'BLAST_NEXT');indexed_load('E_EROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'BLAST_NEXT');indexed_load('E_EX');a.ref('CMP',0xCD,'NX');br(0xD0,'BLAST_NEXT');indexed_load('E_EY');a.ref('CMP',0xCD,'NY');br(0xD0,'BLAST_NEXT');ld('COLLISION_ID');st('TARGET');jump('BLAST_HIT')
    a.label('BLAST_NEXT');inc('COLLISION_ID');ld('COLLISION_ID');cmp(3);br(0x90,'BLAST_TARGET');ld('RAY_LEN');cmp(blast['range_tiles']);br(0x90,'BLAST_RAY')
    a.label('BLAST_DONE');ret()
    a.label('BLAST_HIT');ld('TARGET');st('CURRENT');call('LOAD_WORKER');imm(blast['stun_frames']);st('STUN');imm(0);st('SEPARATE');imm(blast['max_knockback_tiles']);st('PUSH_LEFT');imm(1);st('WHO')
    a.label('PUSH_LOOP');ld('EX');st('NX');ld('EY');st('NY');call('STEP_AIM');call('RAY_WALK');br(0xF0,'PUSH_DONE');call('OCCUPIED');br(0xD0,'PUSH_DONE');ld('NX');st('EX');ld('NY');st('EY');dec('PUSH_LEFT');br(0xD0,'PUSH_LOOP')
    a.label('PUSH_DONE');call('SAVE_WORKER');ret()
    # Bounded dirty-cell rendering: restore old positions, overlay workers/Billy,
    # and finally the transient ray. Only room entry copies all 880 terrain cells.
    a.label('RESTORE_CELL');call('MAP_PTR');indyload(0x80);a.imm('AND',0x29,127);st('GLYPH');call('DRAW_ACTOR');ret()
    a.label('DYNAMIC_DRAW');imm(0);st('DRAW_ID')
    a.label('RESTORE_OLD');ldxvar('DRAW_ID');indexed_load('PREV_ROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'RESTORE_NEXT');indexed_load('PREV_X');st('NX');indexed_load('PREV_Y');st('NY');call('RESTORE_CELL')
    a.label('RESTORE_NEXT');inc('DRAW_ID');ld('DRAW_ID');cmp(4);br(0x90,'RESTORE_OLD')
    ld('RAY_ROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'DRAW_WORKERS');ld('RAY_X');st('NX');ld('RAY_Y');st('NY');imm(0);st('RAY_I')
    a.label('RESTORE_GAS_LOOP');ld('RAY_I');a.ref('CMP',0xCD,'RAY_LEN');br(0xB0,'DRAW_WORKERS');call('STEP_AIM');call('RESTORE_CELL');inc('RAY_I');jump('RESTORE_GAS_LOOP')
    a.label('DRAW_WORKERS');imm(0);st('DRAW_ID')
    a.label('DRAW_WORKER_LOOP');ldxvar('DRAW_ID');indexed_load('E_ACTIVE');br(0xF0,'DRAW_WORKER_NEXT');indexed_load('E_EROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'DRAW_WORKER_NEXT');indexed_load('E_EX');st('NX');indexed_load('E_EY');st('NY');indexed_load('E_STUN');br(0xF0,'DRAW_NORMAL');imm(16);jump('DRAW_WORKER_GLYPH')
    a.label('DRAW_NORMAL');imm(15)
    a.label('DRAW_WORKER_GLYPH');st('GLYPH');call('DRAW_ACTOR')
    a.label('DRAW_WORKER_NEXT');inc('DRAW_ID');ld('DRAW_ID');cmp(3);br(0x90,'DRAW_WORKER_LOOP')
    ld('PX');st('NX');ld('PY');st('NY');imm(14);st('GLYPH');call('DRAW_ACTOR')
    ld('VISUAL');br(0xF0,'RECORD_POSITIONS');ld('RAY_ROOM');a.ref('CMP',0xCD,'ROOM');br(0xD0,'RECORD_POSITIONS');ld('RAY_X');st('NX');ld('RAY_Y');st('NY');imm(0);st('RAY_I')
    a.label('GAS_DRAW_LOOP');ld('RAY_I');a.ref('CMP',0xCD,'RAY_LEN');br(0xB0,'RECORD_POSITIONS');call('STEP_AIM');imm(17);st('GLYPH');call('DRAW_ACTOR');inc('RAY_I');jump('GAS_DRAW_LOOP')
    a.label('RECORD_POSITIONS');ld('PX');a.ref('STA',0x8D,'PREV_X_0');ld('PY');a.ref('STA',0x8D,'PREV_Y_0');ld('ROOM');a.ref('STA',0x8D,'PREV_ROOM_0')
    for i in range(3):
        for source,dest in [('EX','PREV_X'),('EY','PREV_Y'),('EROOM','PREV_ROOM')]:
            a.ref('LDA',0xAD,f'{source}_{i}');a.ref('STA',0x8D,f'{dest}_{i+1}')
    ret()
    # Fixed 40x22 screen: no scrolling or side panel.
    a.label('DRAW');ld('ROOM');st('LOOK_ROOM');ld('FULL_DRAW');br(0xD0,'DRAW_FULL');jump('DRAW_ACTORS');a.label('DRAW_FULL');imm(0);st('FULL_DRAW');st('RY')
    a.label('DRAW_ROW');ld('RY');st('NY');imm(0);st('NX');call('MAP_PTR');ld('RY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xAB10);a.zp('STA',0x85,0x82);a.abs('LDA',0xBD,0xAB11);a.zp('STA',0x85,0x83);ldy(0)
    # Copy a row first, then overlay actors once. Avoid per-cell actor tests.
    a.label('DRAW_CELL');indyload(0x80);a.imm('AND',0x29,127);indystore(0x82);a.op('INY',0xC8);a.imm('CPY',0xC0,40);br(0x90,'DRAW_CELL')
    inc('RY');ld('RY');cmp(22);br(0xB0,'DRAW_ACTORS');jump('DRAW_ROW')
    a.label('DRAW_ACTORS');call('DYNAMIC_DRAW');jump('DRAW_STATUS')
    a.label('DRAW_ACTOR');ld('NY');a.op('ASL A',0x0A);a.op('TAX',0xAA);a.abs('LDA',0xBD,0xAB10);a.zp('STA',0x85,0x82);a.abs('LDA',0xBD,0xAB11);a.zp('STA',0x85,0x83);a.ref('LDY',0xAC,'NX');ld('GLYPH');indystore(0x82);ret()
    a.label('DRAW_STATUS');a.imm('LDX',0xA2,0);a.label('STATUS_LOOP');a.abs('LDA',0xBD,0x2800);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,80);br(0x90,'STATUS_LOOP');ld('STATE');br(0xF0,'DRAW_DONE');cmp(1);br(0xD0,'SUCCESS_TEXT');a.imm('LDX',0xA2,0);a.label('CAUGHT_LOOP');a.abs('LDA',0xBD,0x2850);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,40);br(0x90,'CAUGHT_LOOP');ret()
    a.label('SUCCESS_TEXT');a.imm('LDX',0xA2,0);a.label('SUCCESS_LOOP');a.abs('LDA',0xBD,0x2878);a.abs('STA',0x9D,SCREEN+880);a.op('INX',0xE8);a.imm('CPX',0xE0,40);br(0x90,'SUCCESS_LOOP')
    a.label('DRAW_DONE');ret()
    for var in ['PX', 'PY', 'EX', 'EY', 'NX', 'NY', 'CX', 'CY', 'STATE', 'TICKS', 'DELAY', 'ACTIVE', 'ARM', 'ENEMY_TIMER', 'JOY', 'DIR', 'RY', 'GLYPH', 'SEARCH', 'BUDGET', 'ROOM', 'EROOM', 'LOOK_ROOM', 'ROW_OFFSET', 'FOLLOW_TIMER', 'FROOM', 'FX', 'FY', 'WHO', 'ENTRY_X', 'ENTRY_Y', 'DOOR_Y_01', 'DOOR_Y_12', 'LINK_Y', 'PREV_FRAME', 'ELAPSED', 'STUN', 'SEPARATE', 'AWAIT', 'ENTRY_GRACE', 'ENTRY_FRESH', 'CURRENT', 'COOLDOWN', 'VISUAL', 'FIRE_HELD', 'AIM_DIR', 'RAY_LEN', 'RAY_X', 'RAY_Y', 'RAY_ROOM', 'RAY_I', 'TARGET', 'PUSH_LEFT', 'COLLISION_ID', 'OCC_ID', 'DRAW_ID', 'FULL_DRAW', 'NAV_X', 'NAV_Y', 'NAV_ROOM', 'MOVE_DIR', 'MOVE_TRIES']:a.byte(var,0)
    for field in fields:
        a.label('E_'+field)
        for i in range(3):
            if field=='SEPARATE':a.label(f'SEP_{i}')
            a.byte(f'{field}_{i}',0)
    for group in ['PREV_ROOM','PREV_X','PREV_Y']:
        a.label(group)
        for i in range(4):a.byte(f'{group}_{i}',0)
    a.byte('CADENCE',*[u['move_every_frames'] for u in units])
    a.byte('DX',0,0,255,1);a.byte('DY',255,1,0,0)
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
    font[16*8:17*8]=bytes([66,36,126,90,126,36,66,0])
    font[17*8:18*8]=bytes([0,36,90,189,126,90,36,0])
    parts[FONT]=font
    def text(s):return s.ljust(40).encode('ascii')
    parts[0x2800]=text('ESCAPE! FIRE + DIRECTION: GAS BLAST')+text('RELEASE FIRE TO MOVE / START RESTART')
    parts[0x2850]=text('CAUGHT! START TO TRY AGAIN')
    parts[0x2878]=text('STAGE COMPLETE! START TO REPLAY STAGE')
    parts[0x3F00]=bytes([0x70]*3+[0x42,0,0xB0]+[2]*23+[0x41,0,0x3F])
    parts.pop(0x9800) # BFS scratch, not loaded placeholder
    parts[SCREEN]=bytes(960)
    data=encode_xex(parts);out.mkdir(parents=True,exist_ok=True)
    name='GasBlasters82_Stage1_Playable_v03.xex';(out/name).write_bytes(data)
    (out/'stage1_6502.asm').write_text('; Generated from tools/build_stage1_v03.py; authoritative source is byte emitter\n    *= $1000\n'+'\n'.join(a.asm)+'\n')
    manifest={'output':name,'sha256':hashlib.sha256(data).hexdigest(),'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'stage_code_bytes':len(code),'labels':a.labels,'opening_labels':ol,'emulator_tested':False,'rules':rules,'pathfinding_budget_cells_per_frame':8,'segments':[{ 'start':s,'bytes':len(b)} for s,b in sorted(parts.items())]}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
    m=build();print(m['output'],m['stage_code_bytes'],'code bytes',m['sha256'])
