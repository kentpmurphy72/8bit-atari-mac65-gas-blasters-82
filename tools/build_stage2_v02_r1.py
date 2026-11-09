#!/usr/bin/env python3
"""Native 6502 v0.2-r1: fix write-only GTIA position reads in warning shake.
Deterministic extension to the immutable accepted r3 driver.
The emitted listing plus the r3 listing describe the actual loaded machine code.
Python is an offline assembler/asset builder; no Python executes on the Atari.
"""
import hashlib,json,struct
from pathlib import Path
from build_opening_sequence import Asm,encode_xex,xex_segments
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/stage2_v02_r1'
BASE=ROOT/'assets/stage2_v01_r3'
NAME='GasBlasters82_Stage2_Pressure_Destination_v02_r1.xex'
SCREEN=0x2400
STATES=['STATE','LIVES','FIRE_ARM','TICK_OLD','DELTA','UNITS','TIME0','TIME1','DIST0','DIST1','DIST2','WARN','FLASH','FLASH_TIME','EXP_TIME','EXP_PHASE','TMP','TMP2','MUL0','MUL1','MUL2','RATE0','RATE1','RATE2','NUM0','NUM1','NUM2','REM0','REM1','DEN0','DEN1','PERCENT','CENTIMILES','MPH','HUND','TENS','ONES','LAST_GAS','LAST_MI','LAST_MPH','LAST_LIVES','LAST_FLASH','SHAKE_TIME']
S={n:0x2900+i for i,n in enumerate(STATES)}
# $80..83 accepted road-copy pointers; $84 steering step; $86..89 blit pointers.
class Extension(Asm):
    def abs(self,name,opcode,address):
        suffix=',X' if opcode in (0xBD,0x9D) else ',Y' if opcode in (0xB9,0x99) else ''
        self.op(f'{name} ${address:04X}{suffix}',opcode,address&255,address>>8)
    def branch(self,name,opcode,label):
        names={0x90:'BCC',0xB0:'BCS',0xF0:'BEQ',0xD0:'BNE',0x30:'BMI',0x10:'BPL'}
        super().branch(names[opcode],opcode,label)
    def finalize(self):
        for offset,label,kind in self.patches:
            addr=self.labels[label]
            if kind=='abs':self.buf[offset:offset+2]=struct.pack('<H',addr)
            else:
                rel=addr-(self.base+offset+1)
                assert -128<=rel<=127,(label,rel)
                self.buf[offset]=rel&255
        assert self.base+len(self.buf)<=0x8000
        return bytes(self.buf)

def build(out=OUT):
    old=json.loads((BASE/'manifest.json').read_text());r=old['labels']
    parts=xex_segments(BASE/old['output']);original=hashlib.sha256((BASE/old['output']).read_bytes()).hexdigest()
    assert original=='085ca4e7c283face0657f62b4ec08651c0be46f1d0adf51d725802e2b9da7079'
    # Use otherwise unused glyphs 32..40. ANTIC 4 pixels: green=01, gray=10, white=11.
    glyphs={32:[0,60,126,219,255,126,102,0],33:[85]*8,34:[170,130,130,130,130,130,130,170],
            35:[170,170,255,170,170,255,170,170],36:[85,85,85,85,85,85,85,85],
            37:[255,235,235,255,235,235,255,255],38:[20,20,85,85,20,20,0,0],
            39:[255,235,235,239,235,235,235,255],40:[170]*8}
    for addr in (0x3000,0x3400,0x6000):
        font=bytearray(parts[addr])
        for g,data in glyphs.items():font[g*8:g*8+8]=bytes(data)
        font[(ord('!')+32)*8:(ord('!')+32)*8+8]=bytes([0,48,48,48,0,48,0,0])
        parts[addr]=bytes(font)
    blank=ord(' ')+160
    screen=bytearray(parts[SCREEN])
    for y in range(24):screen[y*40+27:y*40+40]=bytes([blank]*13)
    def text(sc,y,x,string):sc[y*40+x:y*40+x+len(string)]=bytes(ord(c)+160 for c in string)
    for y,x,s in [(1,28,'GAS PRESSURE'),(4,30,'  0%'),(6,29,'PHARMACY'),(8,30,'2.00 MI'),(10,31,'SPEED'),(12,30,' 60 MPH'),(14,31,'LIVES'),(19,31,'SCORE'),(21,30,'000000')]:text(screen,y,x,s)
    for x in range(10):screen[2*40+28+x]=128+34
    for x in (30,33,36):screen[16*40+x]=128+32
    parts[SCREEN]=bytes(screen);parts[0x9400]=bytes(screen);parts[0x9800]=parts[0x3800]
    def scene(title,footer):
        sc=bytearray(screen)
        for y in range(24):sc[y*40:y*40+27]=bytes([blank]*27)
        text(sc,2,max(0,(27-len(title))//2),title)
        text(sc,21,max(0,(27-len(footer))//2),footer)
        return sc
    pharmacy=scene('PHARMACY REACHED','FIRE TO CONTINUE')
    # Original simple building exterior: roof, brick walls, windows, door, cross.
    for y in range(7,10):
        for x in range(3,24):pharmacy[y*40+x]=128+36
    for y in range(10,19):
        for x in range(4,23):pharmacy[y*40+x]=128+35
    for y in range(12,15):
        for x in (6,7,8,18,19,20):pharmacy[y*40+x]=128+37
    for y in range(14,19):
        for x in (12,13,14):pharmacy[y*40+x]=128+39
    for x in range(3,24):pharmacy[19*40+x]=128+40
    pharmacy[11*40+6]=128+38;pharmacy[11*40+20]=128+38
    text(pharmacy,11,9,'PHARMACY')
    parts[0x8000]=bytes(pharmacy)
    parts[0x8400]=bytes(scene('STAGE 2 COMPLETE','FIRE FOR NEW GAME'))
    parts[0x8800]=bytes(scene('BILLY BLEW IT!','FIRE TO RETRY'))
    parts[0x8C00]=bytes(scene('GAME OVER','FIRE FOR NEW GAME'))
    def qm(s):
        s=max(8,min(56,s));return s*10 if s<=24 else 240+(s-24)*5
    q=[qm(s) for s in range(256)]
    for base,units in [(0x6900,5),(0x6B00,6)]:
        parts[base]=bytes((v*units)&255 for v in q);parts[base+256]=bytes((v*units)>>8 for v in q)
    parts[0x6D00]=bytes(v//4 for v in q)
    a=Extension(0x7000)
    def lab(n):a.label(n)
    def im(v):a.imm('LDA',0xA9,v)
    def load(n):a.abs('LDA',0xAD,S[n] if isinstance(n,str) else n)
    def st(n):a.abs('STA',0x8D,S[n] if isinstance(n,str) else n)
    def op(n,code,k):a.abs(n,code,S[k] if isinstance(k,str) else k)
    def call(n):a.ref('JSR',0x20,n)
    def oldcall(n):a.abs('JSR',0x20,r[n])
    def jump(n):a.ref('JMP',0x4C,n)
    def br(code,n):a.branch('branch',code,n)
    def cmp(v):a.imm('CMP',0xC9,v)
    def ret():a.op('RTS',0x60)
    def inc(n):op('INC',0xEE,n)
    def dec(n):op('DEC',0xCE,n)
    def add(v):a.op('CLC',0x18);a.imm('ADC',0x69,v)
    def zero(*ns):
        im(0)
        for n in ns:st(n)
    def copy(source):im(source&255);a.zp('STA',0x85,0x86);im(source>>8);a.zp('STA',0x85,0x87);call('BLIT')
    lab('NEW_GAME');im(3);st('LIVES')
    lab('ATTEMPT');zero('STATE','FIRE_ARM','TIME0','TIME1','WARN','FLASH_TIME','EXP_TIME','EXP_PHASE','SHAKE_TIME')
    for n,v in [('DIST0',8640000&255),('DIST1',(8640000>>8)&255),('DIST2',8640000>>16),('FLASH',1),('UNITS',5)]:im(v);st(n)
    load(0x62);br(0xF0,'NTSC');im(6);st('UNITS');lab('NTSC')
    load(0x14);st('TICK_OLD');im(12);a.zp('STA',0x85,0x84)
    im(0xFF)
    for n in ['LAST_GAS','LAST_MI','LAST_MPH','LAST_LIVES','LAST_FLASH']:st(n)
    # Restore both PMG planes and normal GTIA colors after explosion/static scenes.
    a.imm('LDX',0xA2,0);lab('RESTORE_PMG')
    for p in range(8):a.abs('LDA',0xBD,0x9800+p*256);a.abs('STA',0x9D,0x3800+p*256)
    a.op('INX',0xE8);br(0xD0,'RESTORE_PMG')
    for addr,v in [(0xD01D,2),(0x2C0,0x36),(0xD012,0x36),(0x2C1,14),(0xD013,14),(r['OLD_PMG_Y'],176)]:im(v);st(addr)
    copy(0x9400)
    zero(r['PHASE_LO']);a.abs('JSR',0x20,r['RESET']+5)
    call('HUD');ret()
    # Main frame dispatcher. RTC low delta modulo256 handles bounded missed ticks.
    lab('FRAME');load(0x14);a.op('SEC',0x38);op('SBC',0xED,'TICK_OLD');st('DELTA');load(0x14);st('TICK_OLD')
    load('DELTA');br(0xD0,'HAS_TICK');ret()
    lab('HAS_TICK');zero('TMP2');load('DELTA');st('TMP')
    # TIME step = delta*units (5 NTSC / 6 PAL), exact integer 1/300 seconds.
    a.op('ASL A',0x0A);op('ROL',0x2E,'TMP2');st('MUL0');load('TMP2');st('MUL1')
    load('UNITS');cmp(6);br(0xF0,'PAL_STEP')
    load('MUL0');op('ASL',0x0E,'MUL0');op('ROL',0x2E,'MUL1');load('MUL0');a.op('CLC',0x18);op('ADC',0x6D,'DELTA');st('MUL0');load('MUL1');a.imm('ADC',0x69,0);st('MUL1');jump('STEP_READY')
    lab('PAL_STEP');load('MUL0');st('TMP');load('MUL1');st('TMP2');op('ASL',0x0E,'MUL0');op('ROL',0x2E,'MUL1');load('MUL0');a.op('CLC',0x18);op('ADC',0x6D,'TMP');st('MUL0');load('MUL1');op('ADC',0x6D,'TMP2');st('MUL1')
    lab('STEP_READY');call('FIRE_EDGE');load('STATE');br(0xF0,'DRIVING');cmp(1);br(0xD0,'RESULT_INPUT');jump('EXPLOSION_TICK')
    lab('RESULT_INPUT');load('TMP2');br(0xD0,'RESULT_PRESS');ret()
    lab('RESULT_PRESS');zero('FIRE_ARM');load('STATE');cmp(2);br(0xD0,'NOT_RETRY');jump('ATTEMPT')
    lab('NOT_RETRY');cmp(4);br(0xD0,'RESULT_NEW');im(5);st('STATE');copy(0x8400);call('HUD_DIRTY');ret()
    lab('RESULT_NEW');jump('NEW_GAME')
    lab('DRIVING')
    load(r['NEXT_BANK']);st(0x2F4);st(0xD409);load(r['READY_PHASE']);st(r['SHOWN_PHASE'])
    oldcall('DRIVE')
    load('TIME0');a.op('CLC',0x18);op('ADC',0x6D,'MUL0');st('TIME0');load('TIME1');op('ADC',0x6D,'MUL1');st('TIME1')
    call('DISTANCE')
    # Gas wins exact same-tick tie. Test underlying counters, never HUD strings.
    load('TIME0');cmp(49500&255);load('TIME1');a.imm('SBC',0xE9,49500>>8);br(0x90,'NOT_DEADLINE');jump('FAIL_BEGIN')
    lab('NOT_DEADLINE');load('DIST0');op('ORA',0x0D,'DIST1');op('ORA',0x0D,'DIST2');br(0xD0,'KEEP_DRIVING')
    im(4);st('STATE');zero('FIRE_ARM');im(1);st('FLASH');im(0);st(0xD01D);copy(0x8000);call('HUD_DIRTY');ret()
    lab('KEEP_DRIVING');call('WARNINGS');call('HUD');ret()
    lab('FIRE_EDGE');zero('TMP2');load(0xD010);a.imm('AND',0x29,1);br(0xF0,'PRESSED');im(1);st('FIRE_ARM');ret()
    lab('PRESSED');load('FIRE_ARM');st('TMP2');zero('FIRE_ARM');ret()
    # Telemetry hook retains original vertical smoothing and X mapping; no demo HUD.
    lab('TELEMETRY');oldcall('VERTICAL');load(r['CAR_LO']);st(r['PIX_LO']);load(r['CAR_HI']);st(r['PIX_HI'])
    for _ in range(4):op('LSR',0x4E,r['PIX_HI']);op('ROR',0x6E,r['PIX_LO'])
    load(r['PIX_LO']);add(48);st(0xD000);st(0xD001);ret()
    # Distance fixed point: quarter MPH * 1/300 sec; 2 miles = 8,640,000.
    lab('DISTANCE');a.abs('LDX',0xAE,r['SPEED']);load('UNITS');cmp(6);br(0xF0,'PAL_RATE')
    a.abs('LDA',0xBD,0x6900);st('RATE0');a.abs('LDA',0xBD,0x6A00);jump('RATE_READY')
    lab('PAL_RATE');a.abs('LDA',0xBD,0x6B00);st('RATE0');a.abs('LDA',0xBD,0x6C00)
    lab('RATE_READY');st('RATE1');zero('RATE2','NUM0','NUM1','NUM2');load('DELTA');st('TMP');a.imm('LDX',0xA2,8)
    lab('MULTIPLY');op('LSR',0x4E,'TMP');br(0x90,'NO_ADD');a.op('CLC',0x18)
    for n in range(3):load('NUM'+str(n));op('ADC',0x6D,'RATE'+str(n));st('NUM'+str(n))
    lab('NO_ADD');op('ASL',0x0E,'RATE0');op('ROL',0x2E,'RATE1');op('ROL',0x2E,'RATE2');a.op('DEX',0xCA);br(0xD0,'MULTIPLY')
    a.op('SEC',0x38)
    for n in range(3):load('DIST'+str(n));op('SBC',0xED,'NUM'+str(n));st('DIST'+str(n))
    br(0xB0,'DIST_OK');zero('DIST0','DIST1','DIST2');lab('DIST_OK');ret()
    lab('WARNINGS');im(0);st('TMP')
    for value,band,suffix in [(37125,1,'W75'),(44550,2,'W90')]:
        load('TIME0');cmp(value&255);load('TIME1');a.imm('SBC',0xE9,value>>8);br(0x90,suffix);im(band);st('TMP');lab(suffix)
    load('TMP');op('CMP',0xCD,'WARN');br(0xF0,'SAME_WARN');st('WARN');zero('FLASH_TIME');im(1);st('FLASH')
    lab('SAME_WARN');a.abs('LDX',0xAE,S['WARN']);a.abs('LDA',0xBD,0x6E00);a.zp('STA',0x85,0x84)
    load('WARN');br(0xD0,'DO_FLASH');ret()
    lab('DO_FLASH');load('FLASH_TIME');a.op('CLC',0x18);op('ADC',0x6D,'MUL0');st('FLASH_TIME');load('MUL1');a.imm('ADC',0x69,0);st('TMP2');a.abs('LDX',0xAE,S['WARN']);a.abs('LDA',0xBD,0x6E03);st('TMP');lab('FLASH_REDUCE');load('TMP2');br(0xD0,'FLASH_SUB');load('FLASH_TIME');op('CMP',0xCD,'TMP');br(0x90,'NO_FLASH');lab('FLASH_SUB');load('FLASH_TIME');a.op('SEC',0x38);op('SBC',0xED,'TMP');st('FLASH_TIME');load('TMP2');a.imm('SBC',0xE9,0);st('TMP2');load('FLASH');a.imm('EOR',0x49,1);st('FLASH');jump('FLASH_REDUCE')
    # HPOSP0 ($D000) is write-only: reading it returns M0PF collision flags.
    # Derive each visual offset from the unshaken RAM pixel X, never GTIA.
    lab('NO_FLASH');inc('SHAKE_TIME');load('SHAKE_TIME');a.imm('AND',0x29,4);br(0xF0,'SHAKE_LEFT')
    load(r['PIX_LO']);add(48);a.op('CLC',0x18);op('ADC',0x6D,'WARN');cmp(149);br(0x90,'SHAKE_SET');im(148);jump('SHAKE_SET')
    lab('SHAKE_LEFT');load(r['PIX_LO']);add(48);a.op('SEC',0x38);op('SBC',0xED,'WARN');cmp(48);br(0xB0,'SHAKE_SET');im(48)
    lab('SHAKE_SET');st(0xD000);st(0xD001);ret()
    # Failure first freezes counters. Life is deducted at animation completion.
    lab('FAIL_BEGIN');im(49500&255);st('TIME0');im(49500>>8);st('TIME1');im(1);st('STATE');st('FLASH');zero('FIRE_ARM','EXP_TIME','EXP_PHASE');call('EXP_DRAW');call('HUD');ret()
    lab('EXPLOSION_TICK');load('EXP_TIME');a.op('CLC',0x18);op('ADC',0x6D,'MUL0');br(0xB0,'EXP_DONE');st('EXP_TIME');load('MUL1');br(0xD0,'EXP_DONE');load('EXP_TIME');cmp(150);br(0xB0,'EXP_DONE');cmp(100);br(0x90,'EXP_UNDER100');im(2);jump('EXP_PHASE_READY')
    lab('EXP_UNDER100');cmp(50);br(0x90,'EXP_WAIT');im(1)
    lab('EXP_PHASE_READY');op('CMP',0xCD,'EXP_PHASE');br(0xF0,'EXP_WAIT');st('EXP_PHASE');call('EXP_DRAW')
    lab('EXP_WAIT');ret()
    lab('EXP_DONE');load('LIVES');br(0xF0,'NO_LIVES');dec('LIVES');lab('NO_LIVES');zero('FIRE_ARM');im(0);st(0xD01D);load('LIVES');br(0xF0,'GAME_OVER');im(2);st('STATE');copy(0x8800);jump('END_FAIL')
    lab('GAME_OVER');im(3);st('STATE');copy(0x8C00)
    lab('END_FAIL');call('HUD_DIRTY');ret()
    lab('EXP_DRAW');a.imm('LDX',0xA2,0);im(0);lab('EXP_CLEAR');a.abs('STA',0x9D,0x3C00);a.abs('STA',0x9D,0x3D00);a.op('INX',0xE8);br(0xD0,'EXP_CLEAR')
    for addr in (0x2C0,0xD012,0x2C1,0xD013):im(0xC8);st(addr)
    load('EXP_PHASE');a.op('ASL A',0x0A);a.op('ASL A',0x0A);a.op('ASL A',0x0A);st('TMP');a.op('ASL A',0x0A);a.op('CLC',0x18);op('ADC',0x6D,'TMP');a.op('TAY',0xA8)
    load(r['OLD_PMG_Y']);a.op('SEC',0x38);a.imm('SBC',0xE9,4);a.op('TAX',0xAA);im(24);st('TMP')
    lab('EXP_ROWS');a.abs('LDA',0xB9,0x6E10);a.abs('STA',0x9D,0x3C00);a.abs('STA',0x9D,0x3D00);a.op('INX',0xE8);a.op('INY',0xC8);dec('TMP');br(0xD0,'EXP_ROWS');ret()
    # Bounded 24-bit/16-bit unsigned long division. NUM becomes quotient.
    lab('DIVIDE');zero('REM0','REM1');a.imm('LDX',0xA2,24)
    lab('DIV_BIT');op('ASL',0x0E,'NUM0');op('ROL',0x2E,'NUM1');op('ROL',0x2E,'NUM2');op('ROL',0x2E,'REM0');op('ROL',0x2E,'REM1');br(0xB0,'DIV_SUB')
    load('REM0');op('CMP',0xCD,'DEN0');load('REM1');op('SBC',0xED,'DEN1');br(0x90,'DIV_NEXT')
    lab('DIV_SUB');a.op('SEC',0x38);load('REM0');op('SBC',0xED,'DEN0');st('REM0');load('REM1');op('SBC',0xED,'DEN1');st('REM1');inc('NUM0')
    lab('DIV_NEXT');a.op('DEX',0xCA);br(0xD0,'DIV_BIT');ret()
    # Three digits, HUND/TENS/ONES screen codes. Callers choose leading blank/zero.
    lab('DIGITS');st('TMP');zero('HUND','TENS');load('TMP');lab('DIG100');cmp(100);br(0x90,'DIG10');a.op('SEC',0x38);a.imm('SBC',0xE9,100);inc('HUND');jump('DIG100')
    lab('DIG10');cmp(10);br(0x90,'DIG_END');a.op('SEC',0x38);a.imm('SBC',0xE9,10);inc('TENS');jump('DIG10')
    lab('DIG_END');add(208);st('ONES');load('HUND');add(208);st('HUND');load('TENS');add(208);st('TENS');ret()
    lab('HUD_DIRTY');im(255)
    for n in ['LAST_GAS','LAST_MI','LAST_MPH','LAST_LIVES','LAST_FLASH']:st(n)
    lab('HUD')
    for n in (0,1):load('TIME'+str(n));st('NUM'+str(n))
    zero('NUM2');im(495&255);st('DEN0');im(495>>8);st('DEN1');call('DIVIDE');load('NUM0');st('PERCENT')
    for n in range(3):load('DIST'+str(n));st('NUM'+str(n))
    im(43200&255);st('DEN0');im(43200>>8);st('DEN1');call('DIVIDE');load('REM0');op('ORA',0x0D,'REM1');br(0xF0,'MI_EXACT');inc('NUM0');lab('MI_EXACT');load('NUM0');st('CENTIMILES')
    op('CMP',0xCD,'LAST_MI');br(0xF0,'MI_UNCHANGED');st('LAST_MI');call('DIGITS')
    for k,offset in [('HUND',0),('TENS',2),('ONES',3)]:load(k);st(SCREEN+8*40+30+offset)
    lab('MI_UNCHANGED');a.abs('LDX',0xAE,r['SPEED']);a.abs('LDA',0xBD,0x6D00);st('MPH');op('CMP',0xCD,'LAST_MPH');br(0xF0,'MPH_UNCHANGED');st('LAST_MPH');call('DIGITS');call('LEADING');
    for k,i in [('HUND',0),('TENS',1),('ONES',2)]:load(k);st(SCREEN+12*40+30+i)
    lab('MPH_UNCHANGED');load('LIVES');op('CMP',0xCD,'LAST_LIVES');br(0xF0,'LIVES_UNCHANGED');st('LAST_LIVES')
    for i,x in enumerate((30,33,36)):
        load('LIVES');cmp(i+1);im(blank);br(0x90,'LIFE'+str(i));im(160);lab('LIFE'+str(i));st(SCREEN+16*40+x)
    lab('LIVES_UNCHANGED');load('PERCENT');op('CMP',0xCD,'LAST_GAS');br(0xD0,'GAS_CHANGED');load('FLASH');op('CMP',0xCD,'LAST_FLASH');br(0xD0,'GAS_CHANGED');ret()
    lab('GAS_CHANGED');load('PERCENT');st('LAST_GAS');load('FLASH');st('LAST_FLASH');load('PERCENT');call('DIGITS');call('LEADING');load('FLASH');br(0xD0,'GAS_VISIBLE');im(blank);st('HUND');st('TENS');st('ONES')
    lab('GAS_VISIBLE')
    for k,i in [('HUND',0),('TENS',1),('ONES',2)]:load(k);st(SCREEN+4*40+30+i)
    load('FLASH');br(0xF0,'PERCENT_HIDDEN');im(ord('%')+160);jump('PERCENT_SET')
    lab('PERCENT_HIDDEN');im(blank);lab('PERCENT_SET');st(SCREEN+4*40+33)
    load('PERCENT');zero('TMP');load('PERCENT');lab('BAR_COUNT');cmp(1);br(0x90,'BAR_READY');inc('TMP');a.op('SEC',0x38);a.imm('SBC',0xE9,10);br(0xB0,'BAR_COUNT')
    lab('BAR_READY');a.imm('LDX',0xA2,0);lab('BAR_LOOP');load('FLASH');br(0xF0,'BAR_BLANK');a.op('TXA',0x8A);op('CMP',0xCD,'TMP');im(128+34);br(0xB0,'BAR_STORE');im(128+33);jump('BAR_STORE')
    lab('BAR_BLANK');im(blank);lab('BAR_STORE');a.abs('STA',0x9D,SCREEN+2*40+28);a.op('INX',0xE8);a.imm('CPX',0xE0,10);br(0x90,'BAR_LOOP');ret()
    lab('LEADING');load('HUND');cmp(208);br(0xD0,'LEAD_DONE');im(blank);st('HUND');load('TENS');cmp(208);br(0xD0,'LEAD_DONE');im(blank);st('TENS');lab('LEAD_DONE');ret()
    # Screen blit, 960 bytes, source $86/87; destination $88/89. No OS ZP used.
    lab('BLIT');im(0);a.zp('STA',0x85,0x88);im(0x24);a.zp('STA',0x85,0x89);a.imm('LDX',0xA2,3);a.imm('LDY',0xA0,0)
    lab('BLIT_PAGE');a.op('LDA ($86),Y',0xB1,0x86);a.op('STA ($88),Y',0x91,0x88);a.op('INY',0xC8);br(0xD0,'BLIT_PAGE');a.zp('INC',0xE6,0x87);a.zp('INC',0xE6,0x89);a.op('DEX',0xCA);br(0xD0,'BLIT_PAGE')
    lab('BLIT_TAIL');a.op('LDA ($86),Y',0xB1,0x86);a.op('STA ($88),Y',0x91,0x88);a.op('INY',0xC8);a.imm('CPY',0xC0,192);br(0x90,'BLIT_TAIL');ret()
    code=a.finalize();parts[0x7000]=code;parts[0x2900]=bytes(len(STATES));parts[0x6E00]=bytes([12,10,8,0,150,30])
    clouds=[]
    for radius in (4,8,12):
        for y in range(24):
            dy=abs(y-11.5);clouds.append(0 if dy>=radius else (0x18 if dy>radius*.75 else 0x7E if dy>radius*.4 else 0xFF))
    parts[0x6E10]=bytes(clouds)
    driver=bytearray(parts[0x2000]);patches=[]
    for oldname,newname in [('RESET','NEW_GAME'),('FRAME','FRAME'),('TELEMETRY','TELEMETRY')]:
        addr=r[oldname];target=a.labels[newname];driver[addr-0x2000:addr-0x2000+3]=bytes([0x4C,target&255,target>>8]);patches.append({'address':addr,'jump':target,'purpose':oldname})
    for start,end,pattern,replacement in [('STEER','RIGHT',b'\xe9\x0c',b'\xe5\x84'),('RIGHT','SCROLL',b'\x69\x0c',b'\x65\x84')]:
        lo=r[start]-0x2000;hi=r[end]-0x2000;assert driver[lo:hi].count(pattern)==1;off=driver.index(pattern,lo,hi);driver[off:off+2]=replacement;patches.append({'address':off+0x2000,'bytes':replacement.hex(),'purpose':'warning steering step from private ZP $84'})
    parts[0x2000]=bytes(driver);generated=encode_xex(parts)
    out.mkdir(parents=True,exist_ok=True);(out/NAME).write_bytes(generated)
    listing='; tools/build_stage2_v02_r1.py; corrected shake reads RAM PIX_LO + 48.\n; Native 6502 emitted listing, NOT standalone MAC/65 master.\n; Baseline r3 listing retained as r3_driver_reference.asm; exact patches below.\n; Python builder is authoritative.\n; State $2900; ZP $80..84,$86..89 reserved to this standalone executable.\n'
    listing+=''.join(f'; State {name} = ${addr:04X}\n' for name,addr in S.items())
    listing+='; Driver patches: '+json.dumps(patches)+'\n    *= $7000\n'+'\n'.join(a.asm)+'\n'
    (out/'pressure_destination_6502.asm').write_text(listing)
    (out/'r3_driver_reference.asm').write_bytes((BASE/'driving_6502.asm').read_bytes())
    manifest={'output':NAME,'sha256':hashlib.sha256(generated).hexdigest(),'bytes':len(generated),'revision':'v0.2-r1','labels':a.labels,'state':S,'driver_labels':r,'driver_patches':patches,'driver_code_bytes':len(driver),'extension_code_bytes':len(code),'segments':[{'start':addr,'end':addr+len(d)-1,'bytes':len(d)} for addr,d in sorted(parts.items())], 'zero_page':['$80-$84','$86-$89'],'r3_sha256':original,'time_units_per_second':300,'deadline_units':49500,'distance_units_per_mile':4320000,'warning_units':[37125,44550],'qmph':q,'atari800_tested':False,'hardware_tested':False}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
    m=build();print(m['output'],m['bytes'],'bytes',m['sha256'],'extension',m['extension_code_bytes'])
