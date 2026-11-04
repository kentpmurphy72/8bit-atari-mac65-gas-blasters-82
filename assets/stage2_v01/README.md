# Gas Blasters '82 — Stage 2 v0.1 Basic Driving Prototype

Standalone native **6502 Atari XEX**, stock **64 KB Atari 800XL**, BASIC disabled,
NTSC reference timing. Built on `feature/stage2-driving-v0.1`. **Implemented and
CPU tested; Atari800/user playtest and physical-hardware tests are pending.**
This is free driving, not a complete pharmacy chase and not connected to Stage 1.

## Run

Configure Atari800 with its XL OS ROM, then from the repository root:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage2_v01/GasBlasters82_Stage2_Driving_v01.xex
```

For a downloaded XEX in the current directory:

```bash
atari800 -xl -ntsc -nobasic -run ./GasBlasters82_Stage2_Driving_v01.xex
```

It boots directly into driving. There is no title/menu or music in this standalone
demo. Configure your keyboard or physical controller as **joystick port 1**.

- **Neutral:** keep driving automatically at the current positive speed.
- **LEFT/RIGHT:** smooth free steering, no lane snapping.
- **UP/DOWN:** accelerate / brake; speed never reaches zero or reverses.
- **Diagonals:** steer and change speed together. Opposing directions cancel.
- **FIRE:** reserved, no action; it does not stop steering.
- **Console START (normally F4):** reset car, speed, road phase and telemetry.
  Release before pressing again; holding START does not repeatedly reset.

Shoulder and grass driving are allowed with **no penalty or altered handling**.
GAS %, MI, SCORE and LIVES are **static illustrative placeholders**, clearly marked
(DEMO). They do not implement gas growth, mileage, scoring or a lives system.
Only SPD and ZONE are live tuning telemetry. Nothing ends the demo automatically.

## Build, tests and repeatable profile

Python 3 standard library builds the native machine code and original temporary
art offline; no Python runs on the Atari:

```bash
python3 tools/build_stage2_v01.py
```

`tools/build_stage2_v01.py` is authoritative source. `driving_6502.asm` is the
human-readable generated instruction listing, not an independent MAC/65 build.
`manifest.json` records checksum, labels, load ranges and provisional tuning.
`tuning.json` contains the chosen rates and geometry; geometry/layout changes
beyond the current schema also require corresponding renderer changes.

The pinned CPU-test dependency is the existing py65 1.2.0 requirement:

```bash
python3 -m venv /tmp/gas-driving-tests
/tmp/gas-driving-tests/bin/pip install -r tools/requirements-stage1-test.txt
/tmp/gas-driving-tests/bin/python tools/test_stage2_v01.py
/tmp/gas-driving-tests/bin/python tools/profile_stage2_v01.py
```

On Windows use your venv's `Scripts\python.exe` / `Scripts\pip.exe` equivalents.
Stage 1 and opening regression commands used for this change:

```bash
/tmp/gas-driving-tests/bin/python tools/test_stage1_v04.py
/tmp/gas-driving-tests/bin/python tools/test_stage1_v05.py
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
python3 tools/validate_stage1_pressure_v03.py
python3 tools/validate_stage1_blast_v05.py
python3 tools/validate_opening_sequence.py --output /tmp/gas-stage2-opening-regression
```

**Actual results:** 12 driving tests PASS; 15 Stage 1 v0.4 + 18 Stage 1 v0.5 tests
PASS; all four design validators and opening validation PASS. Driving checks cover
native initialization/registers, deterministic XEX, segment non-overlap, every
road phase/pixel-row wrap, the actual zone colors/boundaries, fixed HUD/font banks,
positive speed caps, neutral/diagonal/opposed inputs, fractional steering/clamps,
FIRE reservation, release-armed reset and RTCLOK wrap/duplicate ticks.

The full native frame loop executed **10,800 simulated NTSC ticks (three minutes)**
with unchanged car/PMG/HUD, correct modulo scroll phase and no runaway state.
This is a CPU-level extended idle test, **not three minutes of actual Atari800
visual observation**. The manifest's emulator/hardware flags remain false.

## Display and scrolling method

ANTIC **mode 4**, 40 columns × 24 eight-scanline rows = **160 color pixels × 192
scanlines**, equivalent to 320 high-resolution logical horizontal pixels.

- Left driving pane: **27 columns = 108 color pixels / 216 logical pixels**, 67.5%.
- Fixed right HUD: **13 columns = 52 color pixels / 104 logical pixels**, 32.5%.
- Paved road is dark gray, shoulders light gray, textured grass green, dashed
  centerline white. The HUD uses an original compact 3×5 font in 4×8 character
  cells. Readability at normal emulator scale remains a playtest question.

No hardware VSCROL/HSCROL is used. Eight horizontal terrain categories each have
four character-row phases. The fixed screen's road glyphs reference these 32
characters, whose 256 bytes animate through a precomputed **32-scanline downward
scroll period**. Grass/shoulder texture and 16-on/16-off center dashes move together.
For each pixel, world_y = (screen_y − scroll_phase) mod 32, including row/period wrap.
This is deliberately a straight, repeating road renderer, not a general world map.

Two 1 KB font banks retain identical static HUD glyphs. At each new RTCLOK tick,
the renderer **publishes the previously completed hidden font** using CHBASE and
its OS shadow. It updates controls/PMG/live telemetry, then copies only the next
256-byte road-font page into the now-hidden bank. The HUD half is never scrolled
or rewritten as scenery. Thus no partially updated road character set becomes
visible. There is one frame of road-phase preparation latency; steering is updated
immediately. Reset prepares phase zero in the hidden bank and publishes it next tick.

## Zone boundaries (provisional hardware rounding)

Coordinates are relative to the left pane; intervals are half-open:

| Zone | Color-pixel interval | Logical-pixel interval | Pane fraction |
|---|---|---|---:|
| Left grass | [0,7) | [0,14) | 6.48% |
| Left shoulder | [7,14) | [14,28) | 6.48% |
| Pavement | [14,94) | [28,188) | 74.07% |
| Right shoulder | [94,101) | [188,202) | 6.48% |
| Right grass | [101,108) | [202,216) | 6.48% |

These approximate the approved **6.25 / 6.25 / 75 / 6.25 / 6.25%** target within
one color pixel, not new canonical road rules. ZONE classifies the car's center.
Classification is telemetry only; no shoulder traction or grass timer is active.

## Car and provisional tuning

Original upward-facing car: normal-width GTIA players **P0 red body + P1 white
headlights/glass**, 8 color pixels (16 logical pixels) wide × 16 scanlines tall.
P0 leaves transparent holes for P1 highlights. Single-line DMA; both planes share
HPOS. Car top is y=144; center y=152, **79.2% down the 192-line viewport**.
The car does not move vertically. Horizontal bounds are top-left [0,100] color
pixels, so its whole sprite stays left of HUD x=108. Spawn is x=50 (center x=54).

| Value | Q4 units | Physical meaning |
|---|---:|---|
| Steering | 12/tick | 0.75 color px / 1.5 logical px per observed NTSC tick |
| Minimum road speed | 8 | 0.5 scanline/tick, nominally 30 scanlines/s |
| Default road speed | 24 | 1.5 scanlines/tick, nominally 90 scanlines/s |
| Maximum road speed | 56 | 3.5 scanlines/tick, nominally 210 scanlines/s |
| Acceleration/brake | ±1/tick | ±1/16 scanline/tick per held tick |

UP from default to maximum takes 32 observed ticks (~0.53 s); full min/max range
48 ticks (~0.8 s). These are initial feel choices to tune after playtesting.
Steering has fractional state, instant reversal and no acceleration. PMG horizontal
hardware steps are **one color clock / two logical pixels**; fractional movement
sometimes holds the same displayed pixel for one tick instead of snapping a tile.
SPD displays scanlines/tick to one truncated decimal (not MPH); it is indicative.

One simulation update per newly observed RTCLOK value, no duplicate updates and no
unbounded catch-up. An unusually missed video tick slows the demo rather than
teleporting scenery. No real 60 Hz guarantee is inferred from offline tests.

## Standalone memory map / timing

| Address range | Use |
|---|---|
| $02E0–$02E1 | RUNAD = $2000 |
| $2000–$22C4 | 709 bytes native controller and state |
| $2400–$27BF | Fixed 960-byte screen |
| $2800–$281F | ANTIC 4 display list, no scrolling flags or DLIs |
| $3000–$33FF / $3400–$37FF | Double-buffered character sets |
| $3800–$3FFF | Single-line PMG block; P0 $3C00, P1 $3D00 |
| $4000–$5FFF | 32 × 256-byte road-font phase pages |
| $6000–$63FF | Immutable initial font template |
| $6400–$640F / $6500–$650E | SPD fractional digits / ZONE labels |
| $80–$83 | Temporary font-copy pointers; BASIC disabled |

OS VBI is retained for clock/shadow registers; display interrupts are disabled
($D40E=$40). DMACTL/SDMCTL=$3A, GRACTL=2, PMBASE=$38, GPRIOR/PRIOR=1; PMG starts
at color-clock x=48 and display scanline y=32. No ROM/BASIC RAM required. Startup
silences POKEY; there is no music/SFX in this driving-feel milestone.

This allocation is **not integration-compatible in-place with Stage 1**: it overlaps
Stage 1's actual opening controller ($2000), footer ($2800), Funk tables ($3000),
font/display lists ($3800+), and artwork ($4000/$6000). A future stage loader must
switch/relocate resources and graphics explicitly; do not concatenate these XEXs.
All Stage 1 artifacts and the opening/music sources remain byte-identical.

`profile.json` records repeatable CPU-only scenarios tied to this XEX's checksum.
Neutral ticks cost **4,575 cycles**, sampled combined steering/acceleration peaks
at **4,614 cycles**, reset at **4,532 cycles**. These exclude ANTIC DMA/OS interrupts;
they support a bounded loop, not an actual emulator timing or flicker claim.

## Limits and recommended Atari800 playtest (not yet run)

No Atari800 executable is installed in this environment. Actual colors, sprite
alignment/priority, compact-font readability, tearing/flicker, input feel and
multi-minute visual stability are **unverified**, as are physical 800XL and PAL.

1. Boot the standalone XEX with NTSC, XL and BASIC off. Confirm upward-facing car,
   green grass, two shoulders, dark pavement, downward dashes and fixed right HUD.
2. Steer/reverse at default speed; compare precision and smoothness to Stage 1.
3. Hold UP then DOWN and try all four speed+steer diagonals. Neutral keeps moving;
   braking never stops or reverses the road. Check SPD changes visibly.
4. Cross shoulders/grass freely; ZONE should change, with no penalties. Hold left
   and right at their limits: the complete car must remain visible, outside HUD.
5. Leave the demo running **at least three actual minutes**; watch phase wraps,
   scenery continuity, HUD steadiness, car flicker and missing rows/markings.
6. Press/release START repeatedly at low/high speed and on both edges. Check reset
   position/speed, phase restart and no repeated reset while held. FIRE stays inert.
7. Report steering speed, acceleration/braking feel, perceived road width/speed,
   car/HUD readability and any artifacts. No pharmacy arrival/failure is expected.

Pressure/distance/arrival are v0.2 work. Curves, narrowing, off-road penalties,
police/hazmat collisions, forks, four-way car blasts and later Gas-Nix drops remain
future milestones. No merge/tag has been made; user review is required first.
