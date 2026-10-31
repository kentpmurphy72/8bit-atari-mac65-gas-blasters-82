#!/usr/bin/env python3
"""Offline structural checks for each music-enabled Atari binary (not an emulator test)."""
from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_pokey_music as m
R=Path(__file__).resolve().parent
meta=json.loads((R/'build_manifest.json').read_text())
for screen in ('title','crew','arrival'):
    entry=meta[screen]
    original=m.read_xex(m.SCREENS[screen]); produced=m.read_xex(R/entry['file'])
    assert hashlib.sha256((R/entry['file']).read_bytes()).hexdigest()==entry['sha256']
    orig={k:bytes(v) for k,v in original}
    target={k:bytes(v) for k,v in produced}
    assert target[0x02e0]==b'\x00\x20'
    assert set(target)==set(orig)|{0x7000}
    assert target[0x7000]==(R/(('rock' if screen=='title' else 'funk')+'_pokey_6502.bin')).read_bytes()
    for addr,old in orig.items():
        if addr==0x2000:
            idx=0x46
            assert target[addr][:idx]==old[:idx]
            assert target[addr][idx:idx+3]==b'\x4c\x00\x70'
            assert target[addr][idx+3:]==old[idx+3:]
        else:assert target[addr]==old
    assert target[0x7000][:2]==b'\xa9\x00' # music start: LDA #$00, STA AUDCTL
    assert bytes.fromhex('8d 08 d2') in target[0x7000] # AU DCTL set
    for hardware in range(0xD200,0xD208):
        assert bytes([0x8D,hardware&255,hardware>>8]) in target[0x7000],hex(hardware)
    print('VALID',entry['file'],len(target[0x7000]),'music bytes')
for name,length in [('rock',192),('funk',128)]:
    b=(R/(name+'_pokey_registers.bin')).read_bytes()
    assert len(b)==length*8
    assert any(b[i+7]&15 for i in range(0,len(b),8)),'percussion silent'
    assert any(b[i+1]&15 for i in range(0,len(b),8)),'melody silent'
    assert len(set(b[i] for i in range(1,len(b),8)))>=4,'no volume variation'
    print('VALID',name,'register ticks:',length)
print('All structural checks passed. Emulator/hardware playback not claimed.')
