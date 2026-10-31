#!/usr/bin/env python3
"""Gas Blasters '82: selected original compositions -> 4-channel POKEY music + three screen XEXs.

Input: original compose_demos.py, its melody, harmony, bass, and drum events.
No music playback on the Atari uses Python, WAV/MP3 or samples; this offline builder
compiles a 6502 sequencer with register event tables into genuine XEX segments.
64kHz-clock POKEY pitch mapping: hz = 63921 / (2 * (AUDF + 1)), AUDCTL=0.
Bass rises one octave where its notes are too low for one 8-bit divider.
The audio MP3s created here are synthetic approximations of the *converted POKEY*
register streams, NOT recordings from a POKEY emulator or hardware.
"""
import ast, json, math, shutil, struct, wave, zipfile, hashlib, subprocess
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
COMPOSITION=HERE/'compose_demos.py'
MUSIC_ADDR=0x7000
POKEY_BASE=0xD200
STUFF={
 'rock':{'bpm':148,'title':'Arcade Rock','stem':'01_Arcade_Rock','bars':12,
         'screens':{'title':'GasBlasters82_Title_ArcadeRock_POKEY.xex'}},
 'funk':{'bpm':110,'title':'Funky Gas Attack','stem':'02_Funky_Gas_Attack','bars':8,
         'screens':{'crew':'GasBlasters82_MeetTheCrew_Funky_POKEY.xex','arrival':'GasBlasters82_Arrival_Funky_POKEY.xex'}}
}
SCREENS={
 'title':HERE/'base_screens'/'title_original.xex',
 'crew':HERE/'base_screens'/'crew_original.xex',
 'arrival':HERE/'base_screens'/'arrival_original.xex'
}

def composition_notes():
    # Evaluate only pure definitions (never call render_track, which produces old WAV previews).
    source=COMPOSITION.read_text()
    source=source.split('\ntracks=[]',1)[0]
    ns={'__file__':str(COMPOSITION)}
    exec(compile(source,str(COMPOSITION),'exec'),ns)
    return {
     'rock':{'melody':ns['place_bars'](ns['rock_lead']),'harmony':ns['rock_harm'],'bass':ns['rock_bass'],'drum':ns['drums_rock'](12)},
     'funk':{'melody':ns['place_bars'](ns['funk_lead']),'harmony':ns['funk_harm'],'bass':ns['funk_bass'],'drum':ns['drums_funk'](8)}
    },ns['freq']

def div_for_pitch(freq,raise_bass=False):
    hz=freq*(2.0 if raise_bass else 1.0)
    raw=round(63921/(2*hz)-1)
    # In case deeper notes than anticipated occur, transpose octave until in AUDF range.
    while raw>255:
        hz*=2
        raw=round(63921/(2*hz)-1)
    return min(255,max(0,raw))

def encode_events(track,info,frequency):
    n=info['bars']*16
    volbase={'melody':13,'harmony':7,'bass':12}
    reg=[[0 for _ in range(n)] for _ in range(8)]
    notes_for_docs={}
    for channel,(freq_reg,ctl_reg) in {'melody':(0,1),'harmony':(2,3),'bass':(4,5)}.items():
        events=track[channel]
        items=[]
        for beat,duration,pitch,vol,*opts in events:
            start=int(round(beat*4))
            ticks=max(1,int(round(duration*4)))
            start=min(n-1,start)
            end=min(n,start+ticks)
            # An individual POKEY audio channel is monophonic; last event wins in overlaps.
            divider=div_for_pitch(frequency(pitch),raise_bass=(channel=='bass'))
            level=min(15,max(1,round(volbase[channel]*float(vol))))
            timbre=0xA0 # pure POKEY square tones, avoiding pitch artifacts from polynomials
            for i in range(start,end):
                reg[freq_reg][i]=divider
                reg[ctl_reg][i]=timbre|level
            items.append({'tick':start,'length_ticks':end-start,'note':pitch,'a_f':divider,'audc':timbre|level})
        notes_for_docs[channel]=items
    # One dedicated percussion/noise channel; prioritize kick/snare over simultaneous hats.
    drums_by_tick={}
    rank={'kick':4,'snare':3,'tom':2,'crash':2,'openhat':1,'hat':0}
    for beat,kind,vel in track['drum']:
        start=int(round(beat*4))
        if start>=n:continue
        if start not in drums_by_tick or rank.get(kind,0)>rank.get(drums_by_tick[start][0],-1):
            drums_by_tick[start]=(kind,vel)
    for tick,(kind,vel) in drums_by_tick.items():
        # Noise and tone noises chosen to have useful character on actual POKEY.
        if kind=='kick': base,dist,level=124,0xC0,12
        elif kind=='snare':base,dist,level=13,0x80,11
        elif kind=='tom':base,dist,level=84,0xC0,10
        elif kind=='crash':base,dist,level=3,0x80,9
        else:base,dist,level=2,0x80,5
        reg[6][tick]=base
        reg[7][tick]=dist|min(15,round(level*vel))
    return reg,notes_for_docs

class Emit:
    def __init__(self,base):self.base=base;self.data=bytearray();self.labels={};self.absfix=[];self.relfix=[];self.lines=[]
    def label(self,l):self.labels[l]=self.base+len(self.data);self.lines.append(l)
    def op(self,name,*values):self.lines.append('    '+name);self.data.extend(values)
    def a(self,mnem,opcode,label):self.lines.append(f'    {mnem} {label}' + (',X' if opcode==0xBD else ''));self.data.extend([opcode,0,0]);self.absfix.append((len(self.data)-2,label))
    def b(self,mnem,opcode,label):self.lines.append(f'    {mnem} {label}');self.data.extend([opcode,0]);self.relfix.append((len(self.data)-1,label))
    def imm(self,mnem,opcode,value):self.lines.append(f'    {mnem} #${value:02X}');self.data.extend([opcode,value])
    def abs(self,mnem,opcode,addr):self.lines.append(f'    {mnem} ${addr:04X}');self.data.extend([opcode,addr&255,addr>>8])
    def zpg(self,mnem,opcode,addr):self.lines.append(f'    {mnem} ${addr:02X}');self.data.extend([opcode,addr])
    def byte(self,val):self.lines.append(f'    .BYTE ${val:02X}');self.data.append(val)
    def table(self,label,bs):
        self.label(label)
        for i in range(0,len(bs),16):
            chunk=bs[i:i+16]
            self.lines.append('    .BYTE '+','.join(f'${v:02X}' for v in chunk))
            self.data.extend(chunk)
    def finalize(self):
        for index,label in self.absfix:
            if label not in self.labels:raise ValueError(label)
            self.data[index:index+2]=struct.pack('<H',self.labels[label])
        for index,label in self.relfix:
            d=self.labels[label]-(self.base+index+1)
            if not -128<=d<=127:raise ValueError(f'branch {label}: {d}')
            self.data[index]=d&255
        return bytes(self.data)

def music_machine(regs,bpm,n,kind):
    # 60Hz NTSC Atari VBI; accumulate 65536 * (BPM * 4 / 3600) per video frame.
    increment=round(65536*bpm*4/3600)
    E=Emit(MUSIC_ADDR)
    E.label('MUSIC_START')
    E.imm('LDA',0xA9,0);E.abs('STA',0x8D,0xD208) # AUDCTL: 64k, 4 x 8-bit
    E.imm('LDA',0xA9,3);E.abs('STA',0x8D,0xD20F) # SKCTL normal
    for addr in [0xD201,0xD203,0xD205,0xD207]:
        E.imm('LDA',0xA9,0);E.abs('STA',0x8D,addr)
    E.zpg('LDA',0xA5,0x14) # RTCLOK low byte, incremented by Atari OS every VBI
    E.a('STA',0x8D,'LAST_FRAME')
    E.imm('LDA',0xA9,0)
    for name in ['PHASE_LO','PHASE_HI','STEP_INDEX']:E.a('STA',0x8D,name)
    E.a('JSR',0x20,'WRITE_STEP') # immediately first note on screen
    E.label('MAIN_LOOP')
    E.zpg('LDA',0xA5,0x14)
    E.a('CMP',0xCD,'LAST_FRAME')
    E.b('BEQ',0xF0,'MAIN_LOOP')
    E.a('STA',0x8D,'LAST_FRAME')
    E.op('CLC',0x18)
    E.a('LDA',0xAD,'PHASE_LO');E.imm('ADC',0x69,increment&255);E.a('STA',0x8D,'PHASE_LO')
    E.a('LDA',0xAD,'PHASE_HI');E.imm('ADC',0x69,increment>>8);E.a('STA',0x8D,'PHASE_HI')
    E.b('BCC',0x90,'NO_STEP')
    E.a('JSR',0x20,'WRITE_STEP')
    E.label('NO_STEP')
    if kind=='title':
        # Preserve standalone title's working START-to-"START PRESSED" behavior.
        E.abs('LDA',0xAD,0xD01F);E.imm('AND',0x29,1)
        E.b('BNE',0xD0,'KEEP_PLAYING')
        E.imm('LDA',0xA9,0)
        for addr in [0xD201,0xD203,0xD205,0xD207]:E.abs('STA',0x8D,addr)
        E.abs('JMP',0x4C,0x204D) # original title code, COPY_STATUS entry
        E.label('KEEP_PLAYING')
    E.a('JMP',0x4C,'MAIN_LOOP')
    E.label('WRITE_STEP')
    E.a('LDX',0xAE,'STEP_INDEX')
    for channel in range(8):
        E.a('LDA',0xBD,'DATA_'+str(channel))
        E.abs('STA',0x8D,POKEY_BASE+channel)
    E.op('INX',0xE8)
    E.imm('CPX',0xE0,n)
    E.b('BNE',0xD0,'NOT_WRAP')
    E.imm('LDX',0xA2,0)
    E.label('NOT_WRAP')
    E.a('STX',0x8E,'STEP_INDEX')
    E.op('RTS',0x60)
    for label in ['LAST_FRAME','PHASE_LO','PHASE_HI','STEP_INDEX']:
        E.label(label);E.byte(0)
    for j,v in enumerate(regs):E.table('DATA_'+str(j),v)
    binary=E.finalize()
    assert MUSIC_ADDR+len(binary)<=0x9000
    return binary, '\n'.join(['; 6502 reference; generated by build_pokey_music.py','; MAC/65-style, ORG $7000; no runtime Python','    *= $7000']+E.lines)+'\n',increment

def read_xex(path):
    b=path.read_bytes();assert b.startswith(b'\xFF\xFF');i=2;segments=[]
    while i<len(b):
        if b[i:i+2]==b'\xff\xff':i+=2;continue
        first,last=struct.unpack_from('<HH',b,i);i+=4
        assert last>=first and i+last-first+1<=len(b),(path,first,last,i)
        segments.append((first,bytearray(b[i:i+last-first+1])));i+=last-first+1
    return segments

def pack_xex(segments):
    data=bytearray(b'\xff\xff')
    for first,payload in segments:
        data+=struct.pack('<HH',first,first+len(payload)-1)+payload
    return bytes(data)

def patch_screen(kind,music,filename):
    ss=read_xex(SCREENS[kind])
    base,code=next((a,d) for a,d in ss if a==0x2000)
    if kind=='title':
        idx=code.find(b'\xAD\x1F\xD0\x29\x01\xD0')
        assert idx==0x46,(kind,idx)
    else:
        idx=code.find(b'\x4C\x46\x20')
        assert idx==0x46,(kind,idx)
    code[idx:idx+3]=bytes([0x4C,MUSIC_ADDR&255,MUSIC_ADDR>>8]) # JMP $7000
    # Music is a distinct RAM segment; screen art, display list and DLI remain byte-identical.
    ss.append((MUSIC_ADDR,bytearray(music)))
    for i,(x,a) in enumerate(ss):
        for y,b in ss[i+1:]:assert x+len(a)<=y or y+len(b)<=x,(hex(x),hex(y))
    data=pack_xex(ss)
    (HERE/filename).write_bytes(data)
    return {'file':filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
            'music_address':'$7000','patch_address':f'${base+idx:04X}',
            'screen_source':SCREENS[kind].name,'start_key':('mutes, displays START PRESSED' if kind=='title' else 'not yet wired')}

def render_register_preview(regs,bpm,beats,outfile):
    # Preview of *converted* 8-register stream, still NOT an exact POKEY renderer.
    sr=44100; per_tick=60/(bpm*4);duration=beats*60/bpm
    total=int((duration+.12)*sr)
    waveout=np.zeros(total,dtype=np.float32)
    # Periodic square waves, and deterministic primitive noise for channel 4.
    rng=np.random.default_rng(1982)
    # Process at tick boundaries so file matches the actual compiled sequence, not the source WAV.
    for t in range(len(regs[0])):
        start=round(t*per_tick*sr);end=min(total,round((t+1)*per_tick*sr))
        if start>=end:continue
        sec=np.arange(end-start,dtype=np.float64)/sr
        for ch in range(4):
            af,ac=regs[ch*2][t],regs[ch*2+1][t]
            vol=ac&15
            if not vol:continue
            freq=63921/(2*(af+1))
            if ch<3:
                tone=np.where((sec*freq)%1<.5,1.,-1.)
            elif (ac&0xF0)==0x80:
                # Approximate digital noise; actual POKEY uses polynomial counters.
                length=int(math.ceil((end-start)*freq/sr))+3
                vals=rng.choice([-1.,1.],size=length)
                indices=np.minimum(len(vals)-1,(sec*freq).astype(int))
                tone=vals[indices]
            else:
                tone=np.where((sec*freq)%1<.5,1.,-1.)
            # Soft edge on each note mimics volume envelope to suppress artificial clicks.
            envelope=np.minimum(1.,sec/.005)*np.minimum(1.,(per_tick-sec)/.006)
            waveout[start:end]+=tone*float(vol)/15*envelope*([.24,.16,.25,.18][ch])
    waveout=np.tanh(waveout*1.15)
    wav=outfile.with_suffix('.wav')
    with wave.open(str(wav),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.clip(waveout,-1,1)*32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-codec:a','libmp3lame','-b:a','160k',str(outfile)],check=True)
    wav.unlink()

def main():
    notes,freq=composition_notes()
    report={}
    for ident,info in STUFF.items():
        reg,events=encode_events(notes[ident],info,freq)
        beats=info['bars']*4;n=beats*4
        assert n<=255 and all(len(v)==n for v in reg)
        machine,src,inc=music_machine(reg,info['bpm'],n,'title' if ident=='rock' else 'cutscene')
        (HERE/(ident+'_pokey_6502.bin')).write_bytes(machine)
        (HERE/(ident+'_pokey_6502.asm')).write_text(src)
        (HERE/(ident+'_pokey_registers.bin')).write_bytes(bytes(v for tick in range(n) for v in (reg[j][tick] for j in range(8))))
        (HERE/(ident+'_pokey_note_events.json')).write_text(json.dumps(events,indent=2)+'\n')
        for screen,filename in info['screens'].items():
            report[screen]=patch_screen(screen,machine,filename)
        render_register_preview(reg,info['bpm'],beats,HERE/(info['stem']+'_POKEY_Approx.mp3'))
        report[ident]={'title':info['title'],'bpm':info['bpm'],'ticks':n,'duration_s':round(beats*60/info['bpm'],2),
                       'frame_increment':inc,'music_bytes':len(machine),'audio_clock_hz':63921,'audctl':0,
                       'register_order':['AUDF1','AUDC1','AUDF2','AUDC2','AUDF3','AUDC3','AUDF4','AUDC4'],
                       'song_source':COMPOSITION.name,'preview_mp3':info['stem']+'_POKEY_Approx.mp3',
                       'bass_octave_shift':'+1 octave (8-bit divider limitation)' }
    (HERE/'build_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
