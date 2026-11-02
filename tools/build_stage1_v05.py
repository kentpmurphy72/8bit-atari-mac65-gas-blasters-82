#!/usr/bin/env python3
"""Native Stage 1 v0.5 attack overlay over the unchanged v0.4 build."""
import hashlib,json,struct,tempfile
from pathlib import Path
import build_stage1_v04 as base
from build_opening_sequence import encode_xex,xex_segments
ROOT=base.ROOT;OUT=ROOT/'assets/stage1_v05'

# Every touched supercover cell, including both sides of exact corner crossings.
def supercover(dx,dy):
    x=y=ix=iy=0;nx=abs(dx);ny=abs(dy);sx=1 if dx>0 else -1;sy=1 if dy>0 else -1;out=[]
    def put(p):
        if p!=(0,0) and p not in out:out.append(p)
    while ix<nx or iy<ny:
        cross=(1+2*ix)*ny-(1+2*iy)*nx
        if cross==0:
            put((x+sx,y));put((x,y+sy));x+=sx;y+=sy;ix+=1;iy+=1
        elif cross<0:x+=sx;ix+=1
        else:y+=sy;iy+=1
        put((x,y))
    return out

class Segments:
    """Checked emitter spanning unused artwork holes, with native jump bridges."""
    def __init__(self):
        self.holes=[(0x7800,0x8000),(0x3600,0x3800),(0x4F00,0x5000),(0x6F00,0x7000),(0x7500,0x7600),(0x8F00,0x9000),(0x9500,0x9600)]
        self.region=0;self.chunks={};self.pc=self.holes[0][0];self.labels={};self.patches=[];self.listing=[]
    def op(self,text,*values):
        if self.pc+len(values)+3>self.holes[self.region][1]:
            self.region+=1;assert self.region<len(self.holes),'Attack exceeds free RAM budget'
            nxt=self.holes[self.region][0];self.chunks[self.pc]=bytearray([0x4C,nxt&255,nxt>>8]);self.pc=nxt
        addr=self.pc;self.chunks[addr]=bytearray(values);self.pc+=len(values);self.listing.append(f'    ; ${addr:04X}\n    {text}');return addr
    def label(self,name):assert name not in self.labels;self.labels[name]=self.pc;self.listing.append(name+':')
    def ref(self,text,opcode,label):
        addr=self.op(text+' '+label,opcode,0,0);self.patches.append((addr,1,label))
    def branch(self,opcode,label):
        inverse={0xF0:0xD0,0xD0:0xF0,0x90:0xB0,0xB0:0x90}[opcode]
        addr=self.op('conditional jump '+label,inverse,3,0x4C,0,0);self.patches.append((addr,3,label))
    def finish(self):
        for addr,off,label in self.patches:self.chunks[addr][off:off+2]=struct.pack('<H',self.labels[label])
        parts={};start=None;buf=bytearray();last=None
        for addr,data in sorted(self.chunks.items()):
            if last!=addr:
                if start is not None:parts[start]=bytes(buf)
                start=addr;buf=bytearray()
            buf+=data;last=addr+len(data)
        if start is not None:parts[start]=bytes(buf)
        return parts

def build(out=OUT):
    rules=json.loads((ROOT/'assets/gameplay/taco_smell_stage1_v05_blast.json').read_text());resource=rules['resource'];combat=rules['combat']
    dirs=[(d['dx'],d['dy']) for d in rules['controls']['aim_directions']]
    with tempfile.TemporaryDirectory() as t:
        tmp=Path(t);m=base.build(tmp);parts=xex_segments(tmp/m['output']);movement_listing=(tmp/'movement_6502.asm').read_text()
    c=m['core_labels'];v=m['labels'];a=Segments();a.labels.update({'C_'+k:z for k,z in c.items()});a.labels.update({'V_'+k:z for k,z in v.items()})
    # State lies in the unused $2900-$29FF gap before the rock music tables.
    variables=['CLOCK','DELTA','HELD','SPENT','AIM','LAST_AIM','WIND','CHARGES','REFILL','COOL','RECOVER','LIVE','AGE','SOUND','CLOUD_ROOM','ORIGIN_X','ORIGIN_Y','COUNT','OLD_COUNT','DIR_BASE','CELL','GLOBAL_CELL','PATH_POS','PATH_LEN','TEST_X','TEST_Y','INDEX','PUSH_ID','SAVE_X','SAVE_Y','DEST_X','DEST_Y','POSE_PHASE','SOUND_INDEX','FRAME_ROOM']
    nextaddr=0x2900
    for name in variables:a.labels[name]=nextaddr;nextaddr+=1
    for name,count in [('CLOUD_X',7),('CLOUD_Y',7),('VALID',7),('HIT',3),('PUSH',3),('PUSH_TIME',3),('BONK',3)]:a.labels[name]=nextaddr;nextaddr+=count
    assert nextaddr<=0x2A00
    def label(n):a.label(n)
    def imm(n):a.op('LDA #',0xA9,n&255)
    def ld(n):a.ref('LDA',0xAD,n)
    def st(n):a.ref('STA',0x8D,n)
    def ldx(n):a.ref('LDX',0xAE,n)
    def ixld(n):a.ref('LDA,X',0xBD,n)
    def ixst(n):a.ref('STA,X',0x9D,n)
    def call(n):a.ref('JSR',0x20,n)
    def jump(n):a.ref('JMP',0x4C,n)
    def br(op,n):a.branch(op,n)
    def ret():a.op('RTS',0x60)
    def cmp(n):a.op('CMP #',0xC9,n)
    def inc(n):a.ref('INC',0xEE,n)
    def dec(n):a.ref('DEC',0xCE,n)
    def add(n):a.op('CLC',0x18);a.op('ADC #',0x69,n&255)
    def store(addr):a.op('STA absolute',0x8D,addr&255,addr>>8)
    def load(addr):a.op('LDA absolute',0xAD,addr&255,addr>>8)
    def timer(name):
        tag='T_'+str(a.pc);ld(name);br(0xF0,tag);a.op('SEC',0x38);a.ref('SBC',0xED,'DELTA');br(0xB0,tag+'_S');imm(0);label(tag+'_S');st(name);label(tag)
    # Reset wraps the whole original INIT, including PMG clear and player alignment.
    label('INIT');a.op('LDA #0',0xA9,0);store(0xD40E);st('LIVE');st('OLD_COUNT');st('SOUND');store(0xD201);a.op('JSR core init+5',0x20,(c['INIT']+5)&255,(c['INIT']+5)>>8)
    # Above core INIT no longer calls v0.4 NEW_INIT, so finish its exact setup here.
    call('V_ALIGN');load(0x14);st('V_MOTION_CLOCK');imm(0);st('V_OLD_Y')
    a.op('LDX #0',0xA2,0);label('CLEAR_PMG')
    for page in range(0xB8,0xC0):a.op('STA PMG,X',0x9D,0,page)
    a.op('INX',0xE8);br(0xD0,'CLEAR_PMG')
    for addr,value in [(0xD407,0xB8),(0xD008,0),(0xD009,0),(0xD01D,2),(0x26F,1),(0xD01B,1),(0x2C0,0x36),(0xD012,0x36),(0x2C1,0x86),(0xD013,0x86),(0x22F,0x3A),(0xD400,0x3A),(0xD40E,0x40)]:imm(value);store(addr)
    imm(0);a.op('LDX #',0xA2,nextaddr-0x2900);label('CLEAR_STATE');a.op('STA state,X',0x9D,0,0x29);a.op('DEX',0xCA);a.op('CPX #255',0xE0,255);br(0xD0,'CLEAR_STATE')
    imm(resource['start_charges']);st('CHARGES');imm(resource['regenerate_one_charge_every_frames']);st('REFILL');imm(255);st('AIM');st('LAST_AIM');imm(1);st('HELD');st('SPENT');load(0x14);st('CLOCK');imm(0);store(0xD201);call('V_PMG_DRAW');ret()
    label('INPUT');load(0x14);a.op('SEC',0x38);a.ref('SBC',0xED,'CLOCK');br(0xD0,'TICK');ret()
    label('TICK');st('DELTA');load(0x14);st('CLOCK');imm(0)
    for i in range(3):a.ref('STA',0x8D,f'C_SEP_{i}')
    timer('COOL');timer('RECOVER');timer('LIVE');timer('SOUND')
    ld('CHARGES');cmp(resource['max_charges']);br(0xB0,'REFILL_FULL');timer('REFILL');ld('REFILL');br(0xD0,'REFILL_DONE');inc('CHARGES');imm(resource['regenerate_one_charge_every_frames']);st('REFILL');jump('REFILL_DONE')
    label('REFILL_FULL');imm(resource['regenerate_one_charge_every_frames']);st('REFILL')
    label('REFILL_DONE');call('PUSH_FRAME');call('SFX');load(0xD010);a.op('AND #1',0x29,1);br(0xF0,'FIRE')
    imm(0);st('HELD');st('SPENT');st('WIND');imm(255);st('LAST_AIM');ld('RECOVER');br(0xD0,'STAY');call('V_MOVE');jump('EFFECTS')
    label('FIRE');load(0x14);st('V_MOTION_CLOCK');ld('HELD');br(0xD0,'AIMING');imm(1);st('HELD');imm(0);st('SPENT');ld('COOL');br(0xD0,'BLOCK_HOLD');ld('CHARGES');br(0xD0,'AIMING')
    label('BLOCK_HOLD');imm(1);st('SPENT')
    label('AIMING');load(0xD300);a.op('AND #15',0x29,15);a.op('TAX',0xAA);a.op('LDA joy table,X',0xBD,0xB8,0x5F);st('AIM');cmp(255);br(0xD0,'VALID_AIM');imm(0);st('WIND');imm(255);st('LAST_AIM');jump('STAY')
    label('VALID_AIM');ld('SPENT');br(0xD0,'STAY');ld('AIM');a.ref('CMP',0xCD,'LAST_AIM');br(0xF0,'STABLE');st('LAST_AIM');imm(1);st('WIND');jump('WIND_CHECK')
    label('STABLE');ld('WIND');a.op('CLC',0x18);a.ref('ADC',0x6D,'DELTA');st('WIND')
    label('WIND_CHECK');ld('WIND');cmp(rules['controls']['windup_frames']);br(0x90,'STAY');call('DISCHARGE')
    label('STAY');load(0x14);st('V_MOTION_CLOCK');call('V_PMG_DRAW')
    label('EFFECTS');ld('LIVE');br(0xF0,'INPUT_DONE');ld('C_ROOM');a.ref('CMP',0xCD,'CLOUD_ROOM');br(0xD0,'INPUT_DONE');call('HITS')
    label('INPUT_DONE');ret()
    label('DISCHARGE');imm(1);st('SPENT');dec('CHARGES');imm(resource['cooldown_frames_from_discharge']);st('COOL');imm(resource['recovery_frames_from_discharge']);st('RECOVER');imm(rules['animation']['cloud_live_frames']);st('LIVE');imm(rules['animation']['sfx']['duration_frames']);st('SOUND');ld('C_ROOM');st('CLOUD_ROOM');ld('C_PX');st('ORIGIN_X');ld('C_PY');st('ORIGIN_Y')
    imm(0)
    for i in range(3):a.op('STA hit',0x8D,(a.labels['HIT']+i)&255,(a.labels['HIT']+i)>>8)
    ld('AIM');st('BURST_AIM');a.op('ASL',0x0A);a.op('ASL',0x0A);a.op('ASL',0x0A);a.op('SEC',0x38);a.ref('SBC',0xED,'AIM');st('DIR_BASE');imm(0);st('CELL')
    label('MAKE_CELL');ld('DIR_BASE');a.op('CLC',0x18);a.ref('ADC',0x6D,'CELL');st('GLOBAL_CELL');a.op('TAX',0xAA);a.op('LDA off X',0xBD,0xB8,0x5E);a.op('CLC',0x18);a.ref('ADC',0x6D,'ORIGIN_X');ldx('CELL');ixst('CLOUD_X')
    ldx('GLOBAL_CELL');a.op('LDA off Y',0xBD,0xF0,0x5E);a.op('CLC',0x18);a.ref('ADC',0x6D,'ORIGIN_Y');ldx('CELL');ixst('CLOUD_Y');call('LOS');ldx('CELL');ixst('VALID');inc('CELL');ld('CELL');cmp(7);br(0x90,'MAKE_CELL');call('SFX');ret()
    # Static supercover paths are translated to the fixed burst origin at runtime.
    label('LOS');ld('CLOUD_ROOM');st('C_LOOK_ROOM');ldx('CELL');ixld('CLOUD_X');st('C_NX');ixld('CLOUD_Y');st('C_NY');call('C_RAY_WALK');br(0xF0,'LOS_BAD');ldx('GLOBAL_CELL');a.op('LDA path length',0xBD,0x80,0x5E);st('PATH_LEN');br(0xD0,'LOS_HAS_PATH');imm(1);ret();label('LOS_HAS_PATH');ld('GLOBAL_CELL');a.op('LSR',0x4A);a.op('LSR',0x4A);a.op('LSR',0x4A);a.op('LSR',0x4A);add(0x5B);a.op('STA zp',0x85,0x8D);ld('GLOBAL_CELL')
    for _ in range(4):a.op('ASL',0x0A)
    a.op('STA zp',0x85,0x8C);imm(0);st('PATH_POS')
    label('LOS_LOOP');ld('PATH_POS');a.op('ASL',0x0A);a.op('TAY',0xA8);a.op('LDA indirect,Y',0xB1,0x8C);a.op('CLC',0x18);a.ref('ADC',0x6D,'ORIGIN_X');st('C_NX');a.op('INY',0xC8);a.op('LDA indirect,Y',0xB1,0x8C);a.op('CLC',0x18);a.ref('ADC',0x6D,'ORIGIN_Y');st('C_NY');call('C_RAY_WALK');br(0xF0,'LOS_BAD');inc('PATH_POS');ld('PATH_POS');a.ref('CMP',0xCD,'PATH_LEN');br(0x90,'LOS_LOOP');imm(1);ret()
    label('LOS_BAD');imm(0);ret()
    label('GET_COUNT');imm(0);st('COUNT');ld('LIVE');br(0xF0,'COUNT_DONE');cmp(13);br(0xB0,'COUNT_ONE');cmp(7);br(0xB0,'COUNT_FOUR');imm(7);jump('COUNT_SET')
    label('COUNT_FOUR');imm(4);jump('COUNT_SET')
    label('COUNT_ONE');imm(1)
    label('COUNT_SET');st('COUNT')
    label('COUNT_DONE');ret()
    label('HITS');call('GET_COUNT');imm(0);st('INDEX')
    label('HIT_WORKER');ldx('INDEX');ixld('C_E_ACTIVE');br(0xF0,'HIT_NEXT');ixld('HIT');br(0xD0,'HIT_NEXT');ixld('C_E_EROOM');a.ref('CMP',0xCD,'CLOUD_ROOM');br(0xD0,'HIT_NEXT');imm(0);st('CELL')
    label('HIT_CELL');ldx('CELL');ixld('VALID');br(0xF0,'HIT_CELL_NEXT');ixld('CLOUD_X');st('TEST_X');ixld('CLOUD_Y');st('TEST_Y');ldx('INDEX');ixld('C_E_EX');a.ref('CMP',0xCD,'TEST_X');br(0xD0,'HIT_CELL_NEXT');ixld('C_E_EY');a.ref('CMP',0xCD,'TEST_Y');br(0xD0,'HIT_CELL_NEXT');imm(1);ixst('HIT');imm(combat['max_knockback_tiles']);ixst('PUSH');imm(combat['knockback_frames_per_tile']);ixst('PUSH_TIME');imm(combat['stun_frames']);a.op('CLC',0x18);a.ref('ADC',0x6D,'C_ELAPSED');ixst('C_E_STUN');imm(0);ixst('C_E_SEPARATE');jump('HIT_NEXT')
    label('HIT_CELL_NEXT');inc('CELL');ld('CELL');a.ref('CMP',0xCD,'COUNT');br(0x90,'HIT_CELL')
    label('HIT_NEXT');inc('INDEX');ld('INDEX');cmp(3);br(0x90,'HIT_WORKER');ret()
    # Knockback is independent of chasing: stunned workers keep their original IDs.
    label('PUSH_FRAME');imm(0);st('PUSH_ID')
    label('PUSH_WORKER');ldx('PUSH_ID');ixld('BONK');br(0xF0,'NO_BONK_TICK');a.op('SEC',0x38);a.ref('SBC',0xED,'DELTA');br(0xB0,'BONK_SAVE');imm(0)
    label('BONK_SAVE');ixst('BONK')
    label('NO_BONK_TICK');ixld('PUSH');br(0xF0,'PUSH_NEXT');ixld('PUSH_TIME');a.op('SEC',0x38);a.ref('SBC',0xED,'DELTA');br(0x90,'PUSH_STEP');ixst('PUSH_TIME');br(0xD0,'PUSH_NEXT')
    label('PUSH_STEP');ld('PUSH_ID');st('C_CURRENT');call('C_LOAD_WORKER');ld('C_EROOM');st('C_LOOK_ROOM');ld('C_EX');st('SAVE_X');ld('C_EY');st('SAVE_Y');ldx('BURST_AIM');a.op('LDA DX',0xBD,0xA8,0x5F);a.op('CLC',0x18);a.ref('ADC',0x6D,'SAVE_X');st('DEST_X');ldx('BURST_AIM');a.op('LDA DY',0xBD,0xB0,0x5F);a.op('CLC',0x18);a.ref('ADC',0x6D,'SAVE_Y');st('DEST_Y')
    # Destination and both diagonal side cells must be terrain- and actor-clear.
    imm(1);st('C_WHO')
    for xx,yy in [('DEST_X','SAVE_Y'),('SAVE_X','DEST_Y'),('DEST_X','DEST_Y')]:
        ld(xx);st('C_NX');ld(yy);st('C_NY');call('PUSH_TILE');cmp(2);br(0xF0,'WORKER_IMPACT');cmp(0);br(0xF0,'PUSH_BONK')
    jump('PUSH_GO')
    label('WORKER_IMPACT')
    ldx('C_OCC_ID');imm(combat['blocking_enemy_stagger_frames']);a.op('CLC',0x18);a.ref('ADC',0x6D,'C_ELAPSED');st('TEST_X');ixld('C_E_STUN');a.ref('CMP',0xCD,'TEST_X');br(0xB0,'STAGGER_KEPT');ld('TEST_X');ixst('C_E_STUN');label('STAGGER_KEPT');imm(combat['impact_flash_frames']);ixst('BONK');jump('PUSH_BONK')
    label('PUSH_GO');ld('DEST_X');st('C_EX');ld('DEST_Y');st('C_EY');call('C_SAVE_WORKER');ldx('PUSH_ID');ixld('PUSH');add(-1);ixst('PUSH');imm(combat['knockback_frames_per_tile']);ixst('PUSH_TIME');jump('PUSH_NEXT')
    label('PUSH_BONK');ldx('PUSH_ID');imm(0);ixst('PUSH');imm(combat['impact_flash_frames']);ixst('BONK');imm(combat['stun_frames']);a.op('CLC',0x18);a.ref('ADC',0x6D,'C_ELAPSED');ixst('C_E_STUN')
    label('PUSH_NEXT');inc('PUSH_ID');ld('PUSH_ID');cmp(3);br(0x90,'PUSH_WORKER');ld('C_ROOM');st('C_LOOK_ROOM');ret()
    label('PUSH_TILE');call('C_RAY_WALK');br(0xD0,'PUSH_TILE_WALK');ret()
    label('PUSH_TILE_WALK');call('C_OCCUPIED');br(0xF0,'PUSH_TILE_EMPTY');imm(2);ret()
    label('PUSH_TILE_EMPTY');imm(1);ret()
    # Restore old cloud before the retained dirty actor renderer runs.
    label('DYNAMIC');ld('CLOUD_ROOM');a.ref('CMP',0xCD,'C_ROOM');br(0xD0,'DYNAMIC_CORE');imm(0);st('CELL')
    label('RESTORE_LOOP');ld('CELL');a.ref('CMP',0xCD,'OLD_COUNT');br(0xB0,'DYNAMIC_CORE');ldx('CELL');ixld('VALID');br(0xF0,'RESTORE_NEXT');ixld('CLOUD_X');st('C_NX');ixld('CLOUD_Y');st('C_NY');call('C_RESTORE_CELL')
    label('RESTORE_NEXT');inc('CELL');jump('RESTORE_LOOP')
    label('DYNAMIC_CORE');imm(0);st('C_DRAW_ID');a.op('JSR old dynamic+5',0x20,(c['DYNAMIC_DRAW']+5)&255,(c['DYNAMIC_DRAW']+5)>>8);ret()
    label('STATUS');call('STATUS_COPY');ld('C_STATE');br(0xF0,'STATUS_PLAY');imm(0);st('SOUND');store(0xD201);ret();label('STATUS_PLAY');call('GET_COUNT');imm(0);st('OLD_COUNT');ld('CLOUD_ROOM');a.ref('CMP',0xCD,'C_ROOM');br(0xD0,'HUD');ld('COUNT');st('OLD_COUNT');imm(0);st('CELL')
    label('DRAW_CLOUD');ld('CELL');a.ref('CMP',0xCD,'COUNT');br(0xB0,'HUD');ldx('CELL');ixld('VALID');br(0xF0,'DRAW_CLOUD_NEXT');ixld('CLOUD_X');st('C_NX');ixld('CLOUD_Y');st('C_NY');ld('LIVE');a.op('AND',0x29,1);add(18);st('C_GLYPH');call('C_DRAW_ACTOR')
    label('DRAW_CLOUD_NEXT');inc('CELL');jump('DRAW_CLOUD')
    label('HUD');imm(0);st('INDEX')
    label('BONK_DRAW');ldx('INDEX');ixld('C_E_ACTIVE');br(0xF0,'BONK_NEXT');ixld('BONK');br(0xF0,'BONK_NEXT');ixld('C_E_EROOM');a.ref('CMP',0xCD,'C_ROOM');br(0xD0,'BONK_NEXT');ixld('C_E_EX');st('C_NX');ixld('C_E_EY');st('C_NY');imm(20);st('C_GLYPH');call('C_DRAW_ACTOR')
    label('BONK_NEXT');inc('INDEX');ld('INDEX');cmp(3);br(0x90,'BONK_DRAW');ld('CHARGES');add(ord('0'));store(base.SCREEN+885);ld('CHARGES');br(0xF0,'HUD_EMPTY');ld('COOL');br(0xD0,'HUD_COOL');imm(0);jump('HUD_TEXT')
    label('HUD_EMPTY');imm(16);jump('HUD_TEXT')
    label('HUD_COOL');imm(8)
    label('HUD_TEXT');st('SOUND_INDEX');imm(0);st('CELL')
    label('HUD_LOOP');ld('SOUND_INDEX');a.op('CLC',0x18);a.ref('ADC',0x6D,'CELL');a.op('TAX',0xAA);a.op('LDA HUD text',0xBD,0xE0,0x5F);ldx('CELL');a.op('STA HUD,X',0x9D,(base.SCREEN+896)&255,(base.SCREEN+896)>>8);inc('CELL');ld('CELL');cmp(8);br(0x90,'HUD_LOOP')
    label('STATUS_DONE');ret()
    # Copy self-contained old footer routine before patching its entry point.
    label('STATUS_COPY');a.op('original footer bytes',*parts[0x1000][c['DRAW_STATUS']-0x1000:c['DRAW_DONE']-0x1000+1])
    label('SFX');ld('SOUND');br(0xD0,'SFX_NOTE');imm(0);store(0xD201);ret()
    label('SFX_NOTE');add(-1);a.op('TAX',0xAA);a.op('LDA whoosh frequency',0xBD,0xC8,0x5F);store(0xD200);a.op('LDA whoosh volume',0xBD,0xD2,0x5F);store(0xD201);ret()
    # PMG pose wrapper erases both planes, then draws a red facing-away torso and
    # blue jeans overlay. Eight orientations, two windup phases, never title PMG.
    label('POSE');ldx('V_OLD_Y');imm(0)
    for i in range(8):a.op('STA P1 old row',0x9D,i,0xBD)
    ldx('V_OLD_Y');a.op('JSR old PMG+3',0x20,(v['PMG_DRAW']+3)&255,(v['PMG_DRAW']+3)>>8)
    ld('HELD');br(0xD0,'POSE_ACTIVE');ld('RECOVER');br(0xF0,'POSE_DONE')
    label('POSE_ACTIVE');ld('AIM');cmp(255);br(0xF0,'POSE_DONE');a.op('ASL',0x0A);a.op('ASL',0x0A);a.op('ASL',0x0A);a.op('ASL',0x0A);st('POSE_PHASE');ld('WIND');a.op('AND',0x29,2);a.op('ASL',0x0A);a.op('ASL',0x0A);a.op('CLC',0x18);a.ref('ADC',0x6D,'POSE_PHASE');st('POSE_PHASE');imm(0);st('CELL')
    label('POSE_LOOP');ld('POSE_PHASE');a.op('CLC',0x18);a.ref('ADC',0x6D,'CELL');a.op('TAX',0xAA);a.op('LDA pose',0xBD,0x28,0x5F);st('TEST_X');ld('V_OLD_Y');a.op('CLC',0x18);a.ref('ADC',0x6D,'CELL');a.op('TAX',0xAA);ld('TEST_X');a.op('STA player0',0x9D,0,0xBC)
    ld('AIM');a.op('ASL',0x0A);a.op('ASL',0x0A);a.op('ASL',0x0A);a.op('CLC',0x18);a.ref('ADC',0x6D,'CELL');a.op('TAX',0xAA);a.op('LDA jeans overlay',0xBD,0xA0,0x28);st('TEST_X');ld('V_OLD_Y');a.op('CLC',0x18);a.ref('ADC',0x6D,'CELL');a.op('TAX',0xAA);ld('TEST_X');a.op('STA player1',0x9D,0,0xBD);inc('CELL');ld('CELL');cmp(8);br(0x90,'POSE_LOOP');load(0xD000);store(0xD001)
    label('POSE_DONE');ret()
    # Immutable per-direction supercover paths and temporary PMG art.
    table=bytearray(0x100);paths=[];lengths=[];offsets=[]
    for dx,dy in dirs:
        for depth,flanks in [(1,[0]),(2,[-1,0,1]),(3,[-1,0,1])]:
            for k in flanks:
                end=(depth*dx-k*dy,depth*dy+k*dx);path=supercover(*end)[:-1];assert len(path)<=8
                paths.extend([z&255 for pair in path for z in pair]+[0]*(16-len(path)*2));lengths.append(len(path));offsets.append(end)
    table=bytearray(paths+lengths+[p[0]&255 for p in offsets]+[p[1]&255 for p in offsets]);assert len(table)==0x428
    jeans=[];poses=[]
    for n,(dx,dy) in enumerate(dirs):
        # P0 red head/torso leans opposite the gas. P1 blue rear bulges toward it.
        blue=[0,0,0,0x60,0xF0,0xF0,0,0]
        if dx>0:blue=[(r>>1)&0xF0 for r in blue]
        if dx<0:blue=[(r<<1)&0xF0 for r in blue]
        if dy<0:blue=list(reversed(blue))
        for phase in range(2):
            rows=[0x60,0x60,0xF0,0x60,0xF0 if phase else 0x90,0xF0,0x90,0]
            if dx>0:rows=[(r<<1)&0xF0 for r in rows]
            if dx<0:rows=[(r>>1)&0xF0 for r in rows]
            if dy<0:rows=list(reversed(rows))
            rows[(n+phase)%8]^=0x10
            # P0 has priority over P1: leave transparent holes for the jeans.
            masked=[r & ~b for r,b in zip(rows,blue)]
            head=7 if dy<0 else 0
            marker=6 if dy<0 else 1
            masked[marker]=(n+1)<<4 # eight distinct head/shoulder orientations
            if phase:masked[head]^=0x80 # visible wind-up shift outside jeans plane
            poses.extend(masked)
        jeans.extend(blue)
    table+=bytes(poses)+bytes([dx&255 for dx,dy in dirs])+bytes([dy&255 for dx,dy in dirs])
    joy=[255]*16
    for i,(dx,dy) in enumerate(dirs):joy[15^(1 if dy<0 else 2 if dy>0 else 0)^(4 if dx<0 else 8 if dx>0 else 0)]=i
    table+=bytes(joy)+bytes([100,85,76,67,58,49,40,31,22,16])+bytes([1,2,2,3,4,5,6,7,8,8])
    assert len(table)==0x4DC
    table+=b'\x00'*4+b'READY   COOLING EMPTY   '
    # BURST_AIM separate stable vector must not follow later aim changes.
    a.labels['BURST_AIM']=nextaddr;nextaddr+=1
    # Patch symbolic refs only after the complete symbol table exists.
    additions=a.finish();parts.update(additions);parts[0x5B00]=bytes(table);parts[0x28A0]=bytes(jeans);parts[0x2900]=bytes(nextaddr-0x2900)
    core=bytearray(parts[0x1000]);move=bytearray(parts[0x400]);patches=[]
    for target,new,where in [(c['INIT'],'INIT',core),(c['PLAYER_INPUT'],'INPUT',core),(c['DYNAMIC_DRAW'],'DYNAMIC',core),(c['DRAW_STATUS'],'STATUS',core),(v['PMG_DRAW'],'POSE',move)]:
        start=0x1000 if where is core else 0x400;off=target-start;where[off:off+3]=b'\x4C'+struct.pack('<H',a.labels[new]);patches.append({'address':target,'target':new})
    parts[0x1000]=core;parts[0x400]=move
    # Footer text is already encoded as the stage's ASCII-indexed font.
    parts[0x2800]=b'GAS  3/3  HOLD FIRE + AIM: 8 DIRECTIONS '.ljust(40)+b'RELEASE TO WALK / START RESTART'.ljust(40)
    font=bytearray(parts[base.FONT]);font[18*8:19*8]=bytes([0x18,0x3C,0x7E,0xFF,0x7E,0x3C,0x18,0]);font[19*8:20*8]=bytes([0x24,0x5A,0xBD,0xFF,0xDB,0x7E,0x24,0]);font[20*8:21*8]=bytes([0x81,0x5A,0x3C,0xFF,0x3C,0x5A,0x81,0]);parts[base.FONT]=font
    # Blue player1 color is restored by OS VBI from its shadow; P0 stays red.
    data=encode_xex(parts);out.mkdir(parents=True,exist_ok=True);name='GasBlasters82_Stage1_Playable_v05.xex';(out/name).write_bytes(data)
    (out/'blast_6502.asm').write_text('; tools/build_stage1_v05.py is authoritative\n'+'\n'.join(a.listing)+'\n')
    (out/'movement_reference.asm').write_text('; unchanged v0.4 reference before PMG wrapper patch\n'+movement_listing)
    result={'output':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'v04_sha256':m['sha256'],'labels':{k:z for k,z in a.labels.items() if not k.startswith(('C_','V_'))},'core_labels':c,'movement_labels':v,'opening_labels':m['opening_labels'],'patches':patches,'rules':rules,'emulator_tested':False,'code_bytes':sum(map(len,additions.values())),'segments':[{'start':s,'bytes':len(d)} for s,d in sorted(parts.items())]}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    m=build();print(m['output'],m['bytes'],'bytes',m['sha256'])
