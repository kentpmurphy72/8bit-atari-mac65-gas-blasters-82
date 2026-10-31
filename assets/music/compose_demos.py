#!/usr/bin/env python3
"""Original four-voice, POKEY-inspired music previews for Gas Blasters '82.

This exports MP3 reference tracks; it is NOT a register-accurate POKEY emulation.
It deliberately uses three monophonic pitched channels and one percussion channel,
with approximate chip timbres, a quantized frequency clock and synthetic noise.
All compositions are newly written for this project, not adaptations of existing music.
"""
from pathlib import Path
import math, subprocess, wave, zipfile, json
import numpy as np

OUT = Path(__file__).resolve().parent
SR=44100
SEED=1982
rng=np.random.default_rng(SEED)

NOTE_INDEX={'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}

def freq(note):
    if note in (None,'-', 'R'): return 0
    if isinstance(note,(int,float)): return float(note)
    n=note[:-1]; octave=int(note[-1]); midi=(octave+1)*12+NOTE_INDEX[n]
    return 440*2**((midi-69)/12)

def pokey_round(hz):
    # Approximate 15.7 kHz channel clock divider, useful for previews.
    return 15700/max(1,round(15700/hz))

def add_tone(track, beat, length, pitch, bpm, *, vol=.4, instrument='lead', gate=.90, slide=0, accent=1.0):
    if pitch in ('R','-',None): return
    f=pokey_round(freq(pitch))
    t0=beat*60/bpm
    seconds=length*60/bpm*gate
    if seconds<=0:return
    i0=int(t0*SR)
    n=min(int(seconds*SR),len(track)-i0)
    if n<=0:return
    t=np.arange(n)/SR
    # Chip oscillators: quantized phase, square/pulse, coarse synthetic distortion.
    if slide:
        # Expressive pitch scoops stay within one chip channel.
        semis=slide*(1-np.exp(-t*13))
        hz=f*2**(semis/12)
        cyc=np.cumsum(hz)/SR
    else:
        cyc=f*t
    phase=cyc%1
    if instrument=='bass':
        wav=np.where(phase<.5,1.,-1.)
        # Soften only the highest pulse harmonics for less harsh bass.
        wav=.65*wav+.35*np.sin(2*np.pi*cyc)
        attack=.006;release=.040
    elif instrument=='funkbass':
        wav=.75*np.where(phase<.27,1.,-1.)+.25*np.sin(2*np.pi*cyc)
        attack=.002;release=.060
    elif instrument=='pluck':
        wav=.80*np.where(phase<.29,1.,-1.)+.20*np.where(phase<.49,1.,-1.)
        attack=.003;release=.060
    elif instrument=='brass':
        wav=.72*np.where(phase<.48,1.,-1.)+.28*np.where(phase<.25,1.,-1.)
        attack=.013;release=.040
    elif instrument=='organ':
        wav=.56*np.where(phase<.5,1.,-1.)+.44*np.sin(2*np.pi*cyc)
        attack=.010;release=.024
    elif instrument=='arp':
        wav=np.where(phase<.37,1.,-1.)
        attack=.003;release=.024
    elif instrument=='bendy':
        wav=np.where(phase<.18,1.,-1.)
        attack=.003;release=.050
    else:
        wav=np.where(phase<.40,1.,-1.)
        attack=.003;release=.037
    # Note off and note on envelope; 4-channel chip volume control approximation.
    env=np.minimum(1.0,t/attack)*np.minimum(1.0,(seconds-t)/release)
    if instrument in ('pluck','funkbass','arp'):
        env*=.55+.45*np.exp(-t*8)
    wav*=env*vol*accent
    track[i0:i0+n]+=wav


def noise_lfsr(size,rate=9000):
    """Pseudo-noise with intentionally reduced bandwidth / old-console grit."""
    coarse=rng.choice([-1.,1.],int(np.ceil(size*rate/SR))+3)
    indices=np.minimum(len(coarse)-1,np.floor(np.arange(size)*rate/SR).astype(int))
    return coarse[indices]


def add_drum(track,beat,bpm,kind='hat',vol=1.0):
    i0=int(beat*60/bpm*SR)
    duration={'kick':.175,'snare':.145,'hat':.065,'openhat':.145,'tom':.145,'crash':.265}.get(kind,.07)
    n=min(int(SR*duration),len(track)-i0)
    if n<=0:return
    t=np.arange(n)/SR
    if kind=='kick':
        h=170*np.exp(-t*28)+64
        phase=np.cumsum(h)/SR
        wav=.85*np.sin(2*np.pi*phase)+.20*noise_lfsr(n,5400)*np.exp(-t*70)
        env=np.exp(-t*25)
        amp=.58
    elif kind=='snare':
        zz=noise_lfsr(n,11500)
        zz=zz-np.convolve(zz,np.ones(65)/65,'same')
        wav=.78*zz+.22*np.sin(2*np.pi*180*t)
        env=np.exp(-t*24)
        amp=.30
    elif kind=='tom':
        h=300*np.exp(-t*12)+130
        wav=np.where((np.cumsum(h)/SR)%1<.5,1.,-1.)
        env=np.exp(-t*27)
        amp=.21
    else:
        zz=noise_lfsr(n,14500)
        zz=zz-np.convolve(zz,np.ones(22)/22,'same')
        wav=zz
        env=np.exp(-t*({'hat':80,'openhat':24,'crash':16}.get(kind,80)))
        amp={'hat':.12,'openhat':.15,'crash':.22}.get(kind,.12)
    track[i0:i0+n]+=vol*amp*wav*env


def render_track(title, bpm, beats, instruments, voices, drum_pattern):
    duration=beats*60/bpm
    samples=int(np.ceil((duration+.24)*SR))
    buses={name:np.zeros(samples,dtype=np.float64) for name in ('melody','harmony','bass','drum')}
    for channel,events in voices.items():
        for e in events:
            start, length, pitch, vol, *opts=e
            inst=opts[0] if opts else instruments[channel]
            slide=opts[1] if len(opts)>1 else 0
            add_tone(buses[channel],start,length,pitch,bpm,vol=vol,instrument=inst,slide=slide)
    for beat,kind,vel in drum_pattern: add_drum(buses['drum'],beat,bpm,kind,vel)
    # Hand mix; reasonably punchy, no brickwall compressing the chip character.
    mix=.72*buses['melody']+.60*buses['harmony']+.87*buses['bass']+.92*buses['drum']
    mix=np.tanh(mix*1.55)
    mix/=max(1.0,np.max(np.abs(mix))/.88)
    # Gentle fade in/out only at track edges, prevent decoder pops.
    fade=int(.011*SR)
    mix[:fade]*=np.linspace(0,1,fade)
    end=int(.20*SR)
    mix[-end:]*=np.linspace(1,0,end)
    pcm=np.int16(np.clip(mix,-1,1)*32767)
    wavpath=OUT/(title+'.wav')
    with wave.open(str(wavpath),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(SR);wav.writeframes(pcm.tobytes())
    mp3=OUT/(title+'.mp3')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(wavpath),'-codec:a','libmp3lame','-b:a','192k','-ar','44100',str(mp3)],check=True)
    return {'title':title,'tempo_bpm':bpm,'beats':beats,'seconds':round(len(pcm)/SR,3),'mp3_bytes':mp3.stat().st_size,'peak':round(float(np.max(np.abs(mix))),4),'channels_used':4}


def place_bars(bars):
    # each bar list of (beat_within_bar,length,pitch,volume,optional_instrument,optional_pitch_bend)
    r=[]
    for i,bar in enumerate(bars):
        for event in bar:r.append((4*i+event[0],*event[1:]))
    return r

def drums_rock(nbars):
    out=[]
    for bar in range(nbars):
        b=4*bar
        for x in np.arange(0,4,.5):out.append((b+float(x),'hat',.75 if x%1 else .93))
        for x in (0,2):out.append((b+x,'kick',1.0))
        for x in (1,3):out.append((b+x,'snare',.97))
        for x in (2.5,) if bar in (3,7,11) else () :out.append((b+x,'kick',.65))
        if bar in (3,7,11):out.extend([(b+3.5,'tom',.68),(b+3.75,'snare',.50)])
    return out

def drums_funk(nbars):
    out=[]
    for bar in range(nbars):
        b=4*bar
        for x in np.arange(0,4,.5):out.append((b+float(x),'hat',.58 if x%1 else .9))
        out += [(b,'kick',1.05),(b+1,'snare',.82),(b+2.5,'kick',.82),(b+3,'snare',1.04)]
        if bar%2==1:out += [(b+1.75,'hat',.7),(b+3.75,'openhat',.8)]
        if bar%4==3:out += [(b+3.5,'snare',.38),(b+3.75,'snare',.4)]
    return out

def drums_adventure(nbars):
    out=[]
    for bar in range(nbars):
        b=4*bar
        out += [(b,'kick',.86),(b+2,'kick',.65),(b+1,'snare',.67),(b+3,'snare',.75)]
        for x in np.arange(0,4,.5):out.append((b+float(x),'hat',.42 if x%1 else .62))
        if bar in (1,5,9): out += [(b+3.5,'tom',.7),(b+3.75,'tom',.5)]
    return out

# ARCADE ROCK: A minor; aggressive repeating lead hook, eighth-note walking power-bass.
rock_lead4=[
 [(0,.48,'A4',.85),(.5,.47,'A4',.68),(1,.45,'C5',.90),(1.5,.48,'D5',.85),(2,.85,'E5',1.0),(3,.48,'G5',.92),(3.5,.47,'E5',.90)],
 [(0,.8,'A5',.98),(1,.46,'G5',.82),(1.5,.45,'E5',.78),(2,.48,'D5',.85),(2.5,.48,'C5',.84),(3,.85,'A4',1.0)],
 [(0,.45,'F5',.9),(.5,.45,'F5',.65),(1,.45,'A5',.94),(1.5,.46,'G5',.85),(2,.8,'F5',.9),(3,.45,'E5',.84),(3.5,.45,'D5',.72)],
 [(0,.45,'G5',.98),(.5,.47,'D5',.73),(1,.47,'G5',.86),(1.5,.48,'A5',.93),(2,.8,'G5',.9),(3,.46,'E5',.85),(3.5,.46,'C5',.8)],
]
rock_lead=rock_lead4 + rock_lead4 + [
 [(0,.45,'A4',.92),(.5,.45,'C5',.82),(1,.47,'D5',.92),(1.5,.48,'E5',.95),(2,.47,'G5',.9),(2.5,.48,'A5',1),(3,.9,'E5',.90)],
 [(0,.45,'F5',.9),(.5,.45,'A5',.94),(1,.47,'C6',1.0),(1.5,.48,'A5',.84),(2,.47,'G5',.86),(2.5,.48,'F5',.82),(3,.9,'E5',.88)],
 [(0,.6,'E5',.85),(.75,.2,'G#5',.88),(1,.45,'B5',.9),(1.5,.45,'G#5',.9),(2,.45,'E5',.88),(2.5,.45,'D5',.79),(3,.9,'B4',.89)],
 [(0,.46,'A4',.92),(.5,.46,'C5',.88),(1,.47,'E5',.95),(1.5,.48,'A5',1.0),(2,1.6,'A5',1.05)]
]
rock_roots=['A','A','F','G','A','A','F','G','A','F','E','A']
rock_bass=[];rock_harm=[]
for i,root in enumerate(rock_roots):
    fifth={'A':'E','F':'C','G':'D','E':'B'}[root]
    rootnote=root+'2';fifthnote=fifth+'3'
    for beat,note in [(0,rootnote),(.5,rootnote),(1,fifthnote),(1.5,rootnote),(2,rootnote),(2.5,rootnote),(3,fifthnote),(3.5,rootnote)]:
        rock_bass.append((4*i+beat,.40,note,.75,'bass'))
    chord={'A':['A4','C5','E5'],'F':['F4','A4','C5'],'G':['G4','B4','D5'],'E':['E4','G#4','B4']}[root]
    for beat in (0,.5,1,1.5,2,2.5,3,3.5):
        k=int(beat*2)%3
        rock_harm.append((4*i+beat,.26,chord[k],.26 if beat%1 else .34,'arp'))

# FUNKY GAS ATTACK: G dominant/blues; displaced notes and little falling glissando.
# 8 bars; rests are the most important feature of the funk groove.
funk_lead=[
 [(0,.3,'D5',.68),(.75,.25,'F5',.92),(1.25,.25,'G5',.91),(2,.31,'Bb5',.75),(2.75,.34,'G5',.86),(3.5,.38,'F5',.76)],
 [(.25,.31,'D5',.81),(1,.28,'F5',.79),(1.75,.26,'G5',.95),(2.25,.25,'B5',.72),(3,.64,'Bb5',.72,'bendy',-2)],
 [(0,.26,'G5',.88),(.5,.24,'D5',.72),(1.25,.36,'F5',.92),(2,.3,'G5',.84),(2.75,.37,'D6',.88),(3.5,.22,'C6',.78)],
 [(.25,.42,'Bb5',.83),(1,.27,'G5',.90),(1.75,.23,'F5',.85),(2.5,.26,'D5',.86),(3, .7,'G4',.91,'bendy',-3)],
 [(0,.25,'G5',.89),(.75,.26,'Bb5',.90),(1.5,.28,'B5',.88),(2.25,.27,'D6',.96),(3,.32,'B5',.83),(3.5,.33,'G5',.8)],
 [(.25,.3,'F5',.83),(1,.3,'D5',.80),(1.75,.36,'G5',.94),(2.5,.25,'A5',.85),(3,.65,'Bb5',.95,'bendy',-3)],
 [(0,.36,'D6',.89),(.75,.22,'C6',.89),(1.25,.3,'Bb5',.85),(2,.38,'G5',.91),(2.75,.27,'F5',.83),(3.5,.25,'D5',.71)],
 [(.25,.34,'G5',.9),(1,.24,'F5',.8),(1.75,.24,'D5',.77),(2.25,.36,'Bb4',.92),(3,.78,'G4',.95,'bendy',-5)]
]
funk_bass=[];funk_harm=[]
funk_patterns=[
 [(0,.28,'G2'),(.75,.25,'G2'),(1.25,.32,'Bb2'),(1.75,.25,'B2'),(2.5,.40,'D3'),(3.25,.26,'F2'),(3.75,.20,'F#2')],
 [(0,.31,'G2'),(.5,.26,'D3'),(1.5,.28,'G2'),(2.25,.24,'F2'),(2.75,.25,'D3'),(3.5,.30,'G2')],
 [(0,.27,'C3'),(.75,.27,'C3'),(1.25,.26,'Eb3'),(2,.28,'F3'),(2.75,.25,'Eb3'),(3.5,.22,'C3')],
 [(0,.27,'D3'),(.75,.25,'F3'),(1.5,.27,'D3'),(2.25,.25,'C3'),(2.75,.28,'A2'),(3.5,.32,'D3')],
]
for i in range(8):
    pattern=funk_patterns[i%4]
    for beat, length, pitch in pattern:
        funk_bass.append((4*i+beat,length,pitch,.96,'funkbass'))
    tones=['G4','Bb4','D5'] if i%4 in (0,1) else (['C5','Eb5','G5'] if i%4==2 else ['D5','F5','A5'])
    # Skanky short off-beat chord fragments; still a single monophonic channel.
    for beat in (.5,1.5,2.5,3.5):
        funk_harm.append((4*i+beat,.17,tones[(int(beat-.5)+i)%3],.42,'pluck'))

# CLASSIC ARCADE ADVENTURE: C major, bright original fanfare -> march.
adventure_lead=[
 [(0,.48,'C5',.86),(.5,.48,'E5',.88),(1,.9,'G5',.96),(2,.9,'C6',1),(3,.45,'B5',.85),(3.5,.45,'C6',.89)],
 [(0,.85,'D6',.96),(1,.47,'C6',.86),(1.5,.47,'B5',.88),(2,.84,'G5',.84),(3,.9,'E5',.95)],
 [(0,.45,'G5',.85),(.5,.45,'A5',.87),(1,.8,'B5',.9),(2,.45,'C6',.92),(2.5,.45,'G5',.84),(3,.9,'E5',.89)],
 [(0,.85,'A5',.9),(1,.45,'G5',.85),(1.5,.45,'F5',.84),(2,.92,'E5',.93),(3,.85,'C5',.9)],
 [(0,.45,'E5',.9),(.5,.45,'G5',.9),(1,.82,'C6',.98),(2,.45,'B5',.88),(2.5,.45,'A5',.83),(3,.85,'G5',.92)],
 [(0,.47,'F5',.86),(.5,.45,'A5',.9),(1,.85,'C6',.97),(2,.45,'D6',.94),(2.5,.47,'C6',.87),(3,.86,'A5',.92)],
 [(0,.45,'G5',.84),(.5,.45,'B5',.9),(1,.86,'D6',.95),(2,.45,'C6',.9),(2.5,.45,'B5',.84),(3,.85,'G5',.9)],
 [(0,.45,'E5',.87),(.5,.45,'F5',.82),(1,.45,'G5',.86),(1.5,.45,'A5',.87),(2,.45,'B5',.9),(2.5,.45,'C6',.92),(3,.85,'G5',.91)],
 [(0,.46,'C6',.98),(.5,.46,'B5',.87),(1,.45,'A5',.86),(1.5,.45,'G5',.84),(2,.86,'E5',.88),(3,.85,'F5',.86)],
 [(0,.45,'G5',.93),(.5,.45,'E5',.87),(1,.45,'C5',.85),(1.5,.45,'E5',.87),(2,1.65,'C6',1.05)]
]
adventure_roots=['C','G','G','F','C','F','G','G','C','C']
adventure_bass=[];adventure_harm=[]
for bar,root in enumerate(adventure_roots):
    chord={'C':['C4','E4','G4'],'G':['G3','B3','D4'],'F':['F3','A3','C4']}[root]
    bass=root+'3' if root!='G' else 'G2'
    fifth={'C':'G3','G':'D3','F':'C3'}[root]
    for pos,pitch in [(0,bass),(1,bass),(2,fifth),(3,bass)]:
        adventure_bass.append((bar*4+pos,.75,pitch,.58,'bass'))
    for pos in np.arange(0,4,.5):
        adventure_harm.append((bar*4+float(pos),.33,chord[int(pos*2)%3],.36,'arp'))

tracks=[]
tracks.append(render_track('01_Arcade_Rock',148,48,{'melody':'lead','harmony':'arp','bass':'bass'},
  {'melody':place_bars(rock_lead),'harmony':rock_harm,'bass':rock_bass},drums_rock(12)))
tracks.append(render_track('02_Funky_Gas_Attack',110,32,{'melody':'bendy','harmony':'pluck','bass':'funkbass'},
  {'melody':place_bars(funk_lead),'harmony':funk_harm,'bass':funk_bass},drums_funk(8)))
tracks.append(render_track('03_Classic_Arcade_Adventure',128,40,{'melody':'brass','harmony':'arp','bass':'bass'},
  {'melody':place_bars(adventure_lead),'harmony':adventure_harm,'bass':adventure_bass},drums_adventure(10)))

(OUT/'TRACK_NOTES.md').write_text('''# Gas Blasters '82 — original title-music concepts\n\nAll three pieces are original compositions for the game. The audio is **POKEY-inspired** (approximate four-channel chip synthesis), not register-accurate hardware capture. The MP3 files are for musical-direction review; the eventual Atari music engine must play POKEY registers directly.\n\n1. **Arcade Rock:** 148 BPM, A minor, crunchy pulse lead, driving eighth-note bass, arpeggio channel and rock-noise drum pattern.\n2. **Funky Gas Attack:** 110 BPM, G-blues/funk, highly syncopated bass and staccato offbeat melody, comic falling-pitch accents, lively percussion.\n3. **Classic Arcade Adventure:** 128 BPM, C major, rising hero fanfare into optimistic march with bright arpeggios, strong bass and marching drums.\n\nEach uses three monophonic tonal channels plus one noise/percussion channel to stay conceptually within POKEY's four audio channels; this rendering includes software envelopes and pitch transitions for demonstration. No music is copied from existing games or songs.\n\nTo regenerate on a computer: `python compose_demos.py` (requires NumPy and ffmpeg).\n''')
(OUT/'TRACK_METADATA.json').write_text(json.dumps(tracks,indent=2))
with zipfile.ZipFile(OUT/'GasBlasters82_Three_Music_Demos.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.iterdir()):
        if p.suffix in ('.mp3','.md','.json','.py') and p.name!='GasBlasters82_Three_Music_Demos.zip':z.write(p,p.name)
for tr in tracks:print(tr)
print('zip_bytes', (OUT/'GasBlasters82_Three_Music_Demos.zip').stat().st_size)
