#!/usr/bin/env python3
"""Build native Q4 movement + gameplay PMG extension over immutable v0.3 source."""
import hashlib,json,struct,tempfile
from pathlib import Path
import build_stage1_v03 as base
from build_opening_sequence import Asm,encode_xex,xex_segments
ROOT=base.ROOT;OUT=ROOT/'assets/stage1_v04';SCREEN=base.SCREEN;FONT=base.FONT;MAP=base.MAP
class Extension(Asm):
    def finalize(self):
        for off,label,kind in self.patches:
            addr=self.labels[label]
            if kind=='abs':self.buf[off:off+2]=struct.pack('<H',addr)
            else:
                delta=addr-(self.base+off+1)
                if not -128<=delta<=127:raise ValueError(f'branch {label}: {delta}')
                self.buf[off]=delta&255
        assert len(self.buf)<=0xC00,'Extension overlaps v0.3 core'
        return bytes(self.buf)

def build(out=OUT):
    rules=json.loads((ROOT/'assets/gameplay/taco_smell_stage1_v04_movement.json').read_text())
    with tempfile.TemporaryDirectory() as t:
        tmp=Path(t);m=base.build(tmp);parts=xex_segments(tmp/m['output']);core_listing=(tmp/'stage1_6502.asm').read_text()
    c=m['labels'];a=Extension(0x0400);a.labels.update({'C_'+k:v for k,v in c.items()})
    def label(n):a.label(n)
    def imm(v):a.imm('LDA',0xA9,v)
    def ld(n):a.ref('LDA',0xAD,n)
    def st(n):a.ref('STA',0x8D,n)
    def call(n):a.ref('JSR',0x20,n)
    def jump(n):a.ref('JMP',0x4C,n)
    def br(op,n):
        if n in {'BOX_BAD','CONTACT_NEXT'}:
            skip=f'LONG_{len(a.buf)}';a.branch('branch inverse',{0xF0:0xD0,0xD0:0xF0,0x90:0xB0,0xB0:0x90}[op],skip);a.ref('JMP',0x4C,n);a.label(skip)
        else:a.branch('branch',op,n)
    def ret():a.op('RTS',0x60)
    def cmp(v):a.imm('CMP',0xC9,v)
    def inc(n):a.ref('INC',0xEE,n)
    def dec(n):a.ref('DEC',0xCE,n)
    def ldx(n):a.ref('LDX',0xAE,n)
    def ixld(n):a.ref('LDA',0xBD,n,idx=True)
    def ixst(n):a.ref('STA',0x9D,n,idx=True)
    def add(v):a.op('CLC',0x18);a.imm('ADC',0x69,v)
    def absolute_store(addr):a.abs('STA',0x8D,addr)
    def tile_of(pos,offset,dest):
        ld(pos);add(offset);st('TMP_LO');ld(pos+'H');a.imm('ADC',0x69,0);st('TMP_HI')
        ld('TMP_LO');cmp(128);ld('TMP_HI');a.op('ROL A',0x2A);st(dest)
    def align_axis(tile,pos):
        ld(tile);a.op('LSR A',0x4A);st(pos+'H');imm(0);a.op('ROR A',0x6A);st(pos)
    label('NEW_INIT');imm(0);absolute_store(0xD40E);a.abs('JSR',0x20,c['INIT']+5)
    call('ALIGN');a.zp('LDA',0xA5,0x14);st('MOTION_CLOCK');imm(0);st('OLD_Y')
    # PMG single-line block B800-BFFF; only player 0 at BC00 is enabled.
    a.imm('LDX',0xA2,0);label('CLEAR_PMG')
    for page in range(0xB8,0xC0):a.abs('STA',0x9D,page<<8)
    a.op('INX',0xE8);br(0xD0,'CLEAR_PMG')
    for addr,value in [(0xD407,0xB8),(0xD008,0),(0xD009,0),(0xD00A,0),(0xD00B,0),(0xD01D,2),(0x26F,1),(0xD01B,1),(0x2C0,0x36),(0xD012,0x36),(0x22F,0x3A),(0xD400,0x3A)]:imm(value);absolute_store(addr)
    call('PMG_DRAW');ret()
    label('ALIGN');align_axis('C_PX','POS_X');align_axis('C_PY','POS_Y');ret()
    # The wrapper suppresses only Billy's old tile glyph, retaining every worker.
    label('GLYPH_DISPATCH');ld('C_GLYPH');cmp(14);br(0xD0,'CORE_GLYPH');ret()
    label('CORE_GLYPH');ld('C_NY');a.abs('JMP',0x4C,c['DRAW_ACTOR']+3)
    label('MOVE');a.zp('LDA',0xA5,0x14);a.op('SEC',0x38);a.ref('SBC',0xED,'MOTION_CLOCK');br(0xD0,'NEW_TICK');ret()
    label('NEW_TICK');cmp(rules['frame_clock']['max_simulated_delta_frames_per_dispatch']+1);br(0x90,'DELTA_OK');imm(rules['frame_clock']['max_simulated_delta_frames_per_dispatch'])
    label('DELTA_OK');st('UPDATES');a.zp('LDA',0xA5,0x14);st('MOTION_CLOCK')
    imm(0)
    for i in range(3):a.ref('STA',0x8D,f'C_SEP_{i}')
    a.abs('LDA',0xAD,0xD300);st('JOY');imm(0);st('SIGN_X');st('SIGN_Y')
    for axis,mask,negative,positive in [('X',12,8,4),('Y',3,2,1)]:
        ld('JOY');a.imm('AND',0x29,mask);cmp(negative);br(0xD0,f'POSITIVE_{axis}');imm(255);st('SIGN_'+axis);jump(f'INPUT_DONE_{axis}')
        label(f'POSITIVE_{axis}');cmp(positive);br(0xD0,f'INPUT_DONE_{axis}');imm(1);st('SIGN_'+axis)
        label(f'INPUT_DONE_{axis}')
    label('UPDATE');imm(rules['player_movement']['cardinal_speed_sixteenths_px_per_frame']);st('SPEED');imm(0);st('DIAGONAL')
    ld('SIGN_X');br(0xF0,'SPEED_READY');ld('SIGN_Y');br(0xF0,'SPEED_READY');imm(rules['player_movement']['diagonal_speed_each_axis_sixteenths_px_per_frame']);st('SPEED');imm(1);st('DIAGONAL')
    label('SPEED_READY');imm(0);st('AXIS');ld('SIGN_X');st('SIGN');ld('SPEED');st('REMAIN');call('AXIS_MOVE');ld('BLOCKED');st('BLOCK_X')
    imm(2);st('AXIS');ld('SIGN_Y');st('SIGN');ld('SPEED');st('REMAIN');ld('BLOCK_X');br(0xF0,'Y_SPEED');imm(rules['player_movement']['cardinal_speed_sixteenths_px_per_frame']);st('REMAIN')
    label('Y_SPEED');call('AXIS_MOVE');ld('BLOCKED');br(0xF0,'MOTION_DONE');ld('BLOCK_X');br(0xD0,'MOTION_DONE');ld('DIAGONAL');br(0xF0,'MOTION_DONE')
    imm(0);st('AXIS');ld('SIGN_X');st('SIGN');imm(rules['player_movement']['cardinal_speed_sixteenths_px_per_frame']-rules['player_movement']['diagonal_speed_each_axis_sixteenths_px_per_frame']);st('REMAIN');call('AXIS_MOVE')
    label('MOTION_DONE');tile_of('POS_X',64,'C_PX');tile_of('POS_Y',64,'C_PY')
    ld('C_ROOM');st('OLD_ROOM');st('C_LOOK_ROOM');ld('C_PX');st('C_NX');ld('C_PY');st('C_NY');call('C_TRY_MOVE')
    ld('C_ROOM');a.ref('CMP',0xCD,'OLD_ROOM');br(0xF0,'NO_ROOM_CHANGE');call('ALIGN');jump('MOVE_FINISH')
    label('NO_ROOM_CHANGE');ld('C_ROOM');cmp(2);br(0xD0,'MORE_UPDATES');ld('C_PX');cmp(39);br(0xD0,'MORE_UPDATES');ld('C_PY');cmp(10);br(0xD0,'MORE_UPDATES');imm(2);st('C_STATE');jump('MOVE_FINISH')
    label('MORE_UPDATES');dec('UPDATES');br(0xF0,'MOVE_FINISH');jump('UPDATE')
    label('MOVE_FINISH');call('PMG_DRAW');ret()
    # Each component uses <=1 logical-pixel substeps. A failed substep is resolved
    # by a four-iteration binary search to the last safe 1/16-pixel coordinate.
    label('AXIS_MOVE');imm(0);st('BLOCKED');ld('SIGN');br(0xD0,'AXIS_LOOP');ret()
    label('AXIS_LOOP');ld('REMAIN');cmp(17);br(0x90,'CHUNK_READY');imm(16)
    label('CHUNK_READY');st('CHUNK');st('AMOUNT');ldx('AXIS');ixld('POS_X');st('SAVE_LO');ixld('POS_XH');st('SAVE_HI');call('APPLY');call('BOX_OK');br(0xF0,'AXIS_COLLISION')
    ld('REMAIN');a.op('SEC',0x38);a.ref('SBC',0xED,'CHUNK');st('REMAIN');br(0xD0,'AXIS_LOOP');ret()
    label('AXIS_COLLISION');imm(1);st('BLOCKED');imm(0);st('LOW');ld('CHUNK');add(-1);st('HIGH')
    label('BINARY');ld('LOW');a.ref('CMP',0xCD,'HIGH');br(0xF0,'BINARY_DONE');a.op('CLC',0x18);a.ref('ADC',0x6D,'HIGH');add(1);a.op('LSR A',0x4A);st('MID');st('AMOUNT');call('APPLY');call('BOX_OK');br(0xF0,'BINARY_BAD');ld('MID');st('LOW');jump('BINARY')
    label('BINARY_BAD');ld('MID');add(-1);st('HIGH');jump('BINARY')
    label('BINARY_DONE');ld('LOW');st('AMOUNT');call('APPLY');ret()
    label('APPLY');ldx('AXIS');ld('SIGN');cmp(1);br(0xD0,'APPLY_MINUS');ld('SAVE_LO');a.op('CLC',0x18);a.ref('ADC',0x6D,'AMOUNT');ixst('POS_X');ld('SAVE_HI');a.imm('ADC',0x69,0);ixst('POS_XH');ret()
    label('APPLY_MINUS');ld('SAVE_LO');a.op('SEC',0x38);a.ref('SBC',0xED,'AMOUNT');ixst('POS_X');ld('SAVE_HI');a.imm('SBC',0xE9,0);ixst('POS_XH');ret()
    label('BOX_OK')
    for axis,maximum in [('X',312*16),('Y',168*16)]:
        ld('POS_'+axis+'H');cmp((maximum>>8)+1);br(0xB0,'BOX_BAD');cmp(maximum>>8);br(0x90,'BOUNDS_'+axis);ld('POS_'+axis);cmp((maximum&255)+1);br(0xB0,'BOX_BAD');label('BOUNDS_'+axis)
    tile_of('POS_X',16,'LEFT');tile_of('POS_X',111,'RIGHT');tile_of('POS_Y',16,'TOP');tile_of('POS_Y',111,'BOTTOM')
    ld('C_ROOM');st('C_LOOK_ROOM')
    ld('LEFT');st('C_NX');ld('TOP');st('C_NY');call('C_WALK');br(0xF0,'BOX_BAD')
    ld('RIGHT');a.ref('CMP',0xCD,'LEFT');br(0xF0,'SKIP_TOP_RIGHT');st('C_NX');call('C_WALK');br(0xF0,'BOX_BAD')
    label('SKIP_TOP_RIGHT');ld('BOTTOM');a.ref('CMP',0xCD,'TOP');br(0xF0,'BOX_GOOD');st('C_NY');ld('LEFT');st('C_NX');call('C_WALK');br(0xF0,'BOX_BAD')
    ld('RIGHT');a.ref('CMP',0xCD,'LEFT');br(0xF0,'BOX_GOOD');st('C_NX');call('C_WALK');br(0xF0,'BOX_BAD')
    label('BOX_GOOD');imm(1);ret()
    label('BOX_BAD');imm(0);ret()
    # Pixel-aware contact, using |player top-left - worker top-left| < 6px.
    label('CONTACT');imm(0);st('CONTACT_ID')
    label('CONTACT_LOOP');ldx('CONTACT_ID')
    for field,opcode in [('ACTIVE',0xF0),('STUN',0xD0),('SEPARATE',0xD0),('ENTRY_GRACE',0xD0)]:ixld('C_E_'+field);br(opcode,'CONTACT_NEXT')
    ixld('C_E_EROOM');a.ref('CMP',0xCD,'C_ROOM');br(0xD0,'CONTACT_NEXT')
    for axis,field in [('X','EX'),('Y','EY')]:
        ldx('CONTACT_ID');ixld('C_E_'+field);a.op('LSR A',0x4A);st('ENEMY_HI');imm(0);a.op('ROR A',0x6A);st('ENEMY_LO')
        ld('POS_'+axis);a.op('SEC',0x38);a.ref('SBC',0xED,'ENEMY_LO');st('DIFF_LO');ld('POS_'+axis+'H');a.ref('SBC',0xED,'ENEMY_HI');st('DIFF_HI');br(0x10,'DIFF_POS_'+axis)
        ld('DIFF_LO');a.imm('EOR',0x49,255);add(1);st('DIFF_LO');ld('DIFF_HI');a.imm('EOR',0x49,255);a.imm('ADC',0x69,0);st('DIFF_HI')
        label('DIFF_POS_'+axis);ld('DIFF_HI');br(0xD0,'CONTACT_NEXT');ld('DIFF_LO');cmp(96);br(0xB0,'CONTACT_NEXT')
    imm(1);st('C_STATE');ret()
    label('CONTACT_NEXT');inc('CONTACT_ID');ld('CONTACT_ID');cmp(3);br(0xB0,'CONTACT_DONE');jump('CONTACT_LOOP')
    label('CONTACT_DONE');ret()
    # ANTIC 2: 320 logical pixels = 160 GTIA color clocks. One PMG bit covers
    # two logical pixels horizontally, single-line DMA is one logical pixel tall.
    label('PMG_DRAW');ldx('OLD_Y');imm(0)
    for i in range(8):a.abs('STA',0x9D,0xBC00+i)
    # Convert Q4 Y to integer pixels and offset first displayed line by 32.
    ld('POS_YH');st('PIX_HI');ld('POS_Y');st('PIX_LO')
    for _ in range(4):a.ref('LSR',0x4E,'PIX_HI');a.ref('ROR',0x6E,'PIX_LO')
    ld('PIX_LO');add(32);st('OLD_Y');a.op('TAX',0xAA)
    for i,v in enumerate([0x60,0xF0,0x60,0xF0,0x60,0x90,0x90,0]):imm(v);a.abs('STA',0x9D,0xBC00+i)
    ld('POS_XH');st('PIX_HI');ld('POS_X');st('PIX_LO')
    for _ in range(5):a.ref('LSR',0x4E,'PIX_HI');a.ref('ROR',0x6E,'PIX_LO')
    ld('PIX_LO');add(48);absolute_store(0xD000);ret()
    for name in ['POS_X','POS_XH','POS_Y','POS_YH','MOTION_CLOCK','UPDATES','JOY','SIGN_X','SIGN_Y','SIGN','SPEED','DIAGONAL','AXIS','REMAIN','BLOCKED','BLOCK_X','CHUNK','AMOUNT','SAVE_LO','SAVE_HI','LOW','HIGH','MID','TMP_LO','TMP_HI','LEFT','RIGHT','TOP','BOTTOM','OLD_ROOM','CONTACT_ID','ENEMY_LO','ENEMY_HI','DIFF_LO','DIFF_HI','OLD_Y','PIX_LO','PIX_HI']:a.byte(name,0)
    code=a.finalize();core=bytearray(parts[0x1000]);patches=[]
    for old,new,size in [('INIT','NEW_INIT',5),('PLAYER_INPUT','MOVE',3),('CHECK_CAUGHT','CONTACT',3),('DRAW_ACTOR','GLYPH_DISPATCH',3)]:
        offset=c[old]-0x1000;core[offset:offset+size]=b'\x4c'+struct.pack('<H',a.labels[new])+b'\xea'*(size-3);patches.append({'core':old,'extension':new,'address':c[old]})
    # Move the old Y queue out of the aligned PMG block. No other queue changes.
    for zp in (0x86,0x8A):
        needle=bytes([0xA9,0,0x85,zp,0xA9,0xB9,0x85,zp+1]);assert core.count(needle)==1
        core=core.replace(needle,bytes([0xA9,0,0x85,zp,0xA9,0x9C,0x85,zp+1]))
    parts[0x1000]=core;parts[0x400]=code;parts[0xB800]=bytes(2048)
    def text(s):assert len(s)<=40;return s.ljust(40).encode('ascii')
    parts[0x2800]=text('ESCAPE! JOYSTICK: 8-WAY WALK')+text('FIRE DISABLED V0.4 / START RESTART')
    data=encode_xex(parts);out.mkdir(parents=True,exist_ok=True);name='GasBlasters82_Stage1_Playable_v04.xex';(out/name).write_bytes(data)
    (out/'movement_6502.asm').write_text('; Authoritative emitter: tools/build_stage1_v04.py\n    *= $0400\n'+'\n'.join(a.asm)+'\n')
    (out/'core_6502_reference.asm').write_text('; v0.3 reference before the documented dispatch/queue patches\n'+core_listing)
    result={'output':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'v03_sha256':m['sha256'],'labels':{k:v for k,v in a.labels.items() if not k.startswith('C_')},'core_labels':c,'opening_labels':m['opening_labels'],'extension_bytes':len(code),'patches':patches,'rules':rules,'emulator_tested':False,'pmg':{'base':0xB800,'player0':0xBC00,'x_color_clock_origin':48,'y_scanline_origin':32,'horizontal_logical_pixels_per_bit':2,'vertical_logical_pixels_per_bit':1},'segments':[{'start':s,'bytes':len(d)} for s,d in sorted(parts.items())]}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    m=build();print(m['output'],m['extension_bytes'],'extension bytes',m['sha256'])
