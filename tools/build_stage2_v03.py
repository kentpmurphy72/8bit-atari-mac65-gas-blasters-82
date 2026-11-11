#!/usr/bin/env python3
"""Geometry-only data revision of accepted v0.2-r1. No native code is patched.
The unchanged 6502 font-copy/PMG/gameplay engines run on a stock Atari 800XL.
Python is an offline asset builder, never an Atari runtime dependency.
"""
import hashlib,json,struct,zlib
from pathlib import Path
from build_opening_sequence import encode_xex,xex_segments
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/stage2_v03'
BASE=ROOT/'assets/stage2_v02_r1'
NAME='GasBlasters82_Stage2_Road_Geometry_v03.xex'
BASE_SHA='316ad4e7a1a5a495b23c4929b59a673c7acef0957699415f27b97840fb4f9a31'
CHANGED={0x2400,0x3000,0x3400,0x4000,0x6000,0x9400}

def geometry():
    g=json.loads((OUT/'geometry.json').read_text())
    assert (g['driving_columns'],g['hud_columns'],g['color_pixels_per_character'])==(27,13,4)
    assert [(b['start'],b['end'],b['zone']) for b in g['bands']]==[(0,14,'grass'),(14,21,'shoulder'),(21,87,'pavement'),(87,94,'shoulder'),(94,108,'grass')]
    assert g['centerline_x']==54
    return g

def zone_at(x,g=None):
    """Offline geometric lookup, not active traction/penalty gameplay.
    Coordinates are local integer color pixels; intervals are half open.
    Future car-center classification is deliberately outside this increment.
    """
    if not isinstance(x,int) or not 0<=x<108:raise ValueError('local x must be an integer in [0,108)')
    for band in (g or geometry())['bands']:
        if band['start']<=x<band['end']:return band['zone']
    raise AssertionError('uncovered pixel')

def road_art(g):
    terrain={'pavement':0,'grass':1,'shoulder':2}
    row=[terrain[zone_at(x,g)] for x in range(108)]
    row[g['centerline_x']]=3 # Preserve accepted dashed center marking at x=54.
    categories=[];columns=[]
    for x in range(0,108,4):
        strip=row[x:x+4]
        if strip not in categories:categories.append(strip)
        columns.append(categories.index(strip))
    assert len(categories)==8 # Exactly 32 glyphs; no font/CPU/memory expansion.
    pages=bytearray()
    for phase in range(32):
        for strip in categories:
            for rowphase in range(4):
                for y in range(8):
                    world=(rowphase*8+y-phase)%32;packed=0
                    for x,p in enumerate(strip):
                        if p==3:p=3 if world<16 else 0
                        elif p==1 and (world+x*3)%8==0:p=0
                        elif p==2 and (world+x)%8==0:p=3
                        packed=(packed<<2)|p
                    pages.append(packed)
    assert len(pages)==8192
    return bytes(pages),categories,columns

def write_preview(parts,out):
    """Static byte-layout illustration with approximate RGB; NOT emulator output."""
    colors=[(15,18,22),(80,170,65),(110,110,110),(230,230,230)];rows=[]
    for y in range(192):
        row=bytearray([0])
        for x in range(320):
            glyph=parts[0x2400][y//8*40+x//8]&127
            value=(parts[0x3000][glyph*8+y%8]>>(6-2*(x%8//2)))&3;color=colors[value]
            if 144<=y<160 and 50<=x//2<58:
                bit=1<<(7-(x//2-50));sprite_row=y-144
                if parts[0x6800][sprite_row]&bit:color=(200,65,65)
                if parts[0x6800][16+sprite_row]&bit:color=(240,240,240)
            row.extend(color)
        rows.append(row)
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',320,192,8,2,0,0,0))
    png+=chunk(b'tEXt',b'Description\0Software XEX memory layout preview with approximate RGB colors; NOT an Atari800 screenshot')
    png+=chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b'')
    (out/'layout_preview.png').write_bytes(png)

def build(out=OUT):
    prior=json.loads((BASE/'manifest.json').read_text());baseline=BASE/prior['output']
    assert hashlib.sha256(baseline.read_bytes()).hexdigest()==BASE_SHA
    before=xex_segments(baseline);parts=dict(before);g=geometry();pages,categories,columns=road_art(g)
    parts[0x4000]=pages
    for address in (0x3000,0x3400,0x6000):parts[address]=pages[:256]+before[address][256:]
    for address in (0x2400,0x9400):
        screen=bytearray(before[address])
        for y in range(24):
            for x in range(27):screen[y*40+x]=128+4*columns[x]+y%4
        parts[address]=bytes(screen)
    assert {a for a in before if before[a]!=parts[a]}==CHANGED
    generated=encode_xex(parts);out=Path(out);out.mkdir(parents=True,exist_ok=True);(out/NAME).write_bytes(generated)
    # Complete native runtime listings are unchanged, accurately attributed.
    for name in ('pressure_destination_6502.asm','r3_driver_reference.asm'):
        (out/name).write_bytes((BASE/name).read_bytes())
    m={**prior,'revision':'v0.3-geometry-only','output':NAME,'sha256':hashlib.sha256(generated).hexdigest(),'bytes':len(generated),
       'baseline_v02_r1_sha256':BASE_SHA,'geometry':g,'zone_for_local_x':[zone_at(x,g) for x in range(108)],
       'road_categories':categories,'category_for_column':columns,'changed_segments':sorted(CHANGED),
       'segments':[{'start':a,'end':a+len(d)-1,'bytes':len(d)} for a,d in sorted(parts.items())],
       'native_code_unchanged':True,'runtime_penalties_added':False,'atari800_tested':False,'hardware_tested':False}
    (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    write_preview(parts,out)
    return m
if __name__=='__main__':
    m=build();print(m['output'],m['bytes'],'bytes',m['sha256'])
