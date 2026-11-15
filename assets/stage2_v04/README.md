# Stage 2 v0.4 — Off-Road Consequences

Standalone native 6502 XEX for stock Atari 800XL / 64 KB, based on accepted v0.3.
Authoritative gameplay specification: `docs/STAGE2_DESIGN.md` §28. All historical
XEX/source/manifest/test files are preserved. **Implemented and CPU verified;
Atari800/hardware NOT RUN here; user gameplay acceptance pending.**

## Build, test and launch

From repository root:

```bash
python3 tools/build_stage2_v04.py
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements-stage1-test.txt
.venv/bin/python tools/test_stage2_v04.py
.venv/bin/python tools/profile_stage2_v04.py
.venv/bin/python tools/test_stage2_v03.py
.venv/bin/python tools/test_stage2_v02_r1.py
.venv/bin/python tools/test_stage2_v01_r3.py
atari800 -xl -ntsc -nobasic -run assets/stage2_v04/GasBlasters82_Stage2_Offroad_v04.xex
# Repeat with -pal instead of -ntsc.
```

Build requires only Python 3 stdlib; offline tests use pinned py65 1.2.0.
Python never runs on the Atari. `build_stage2_v04.py` is the authoritative native
byte emitter. `pressure_destination_6502.asm` is its faithful emitted listing,
including all new state addresses and checked driver hooks; the unchanged native
r3 reference listing is also included. These are **not independently assembling
MAC/65 master inputs**. The manifest records exact entry, segments and checksum.

Joystick port 1 steers, UP accelerates, DOWN brakes; diagonals combine inputs.
FIRE is inert during driving and controls all result screens. START/F4 remains
disabled. Original 20/60/100-MPH anchors, speed-linked Y, smoothing, pressure,
mileage, lives, pharmacy scene and two-distinct-FIRE completion flow remain.

## Approved off-road behavior

Unshaken logical sprite-left `floor(X_Q4/16) + 4` selects the center zone:

| Center x (local color pixels) | Surface | Steering Q4 step | Grass clock |
| --- | --- | ---: | --- |
| [0,14), [94,108) | Grass | 8 | Runs/resumes |
| [14,21), [87,94) | Shoulder | 10 | Holds |
| [21,87) | Pavement | 12 | Resets to zero |

Pressure still requests steps 12/10/8 for normal/75%/90%. The actual steering
step is **min(surface, pressure)**; penalties never multiply/compound. Throttle,
MPH and vertical motion are unaffected by terrain.

Each update chooses steering from the current logical center/pressure, applies
the accepted native driving input, then reclassifies the resulting logical
center for this tick's grass clock. A frame reaching pavement immediately clears
exposure; reaching shoulder pauses it. Visual shake never changes logical X.
This sampling order adds no player-facing grace timer or new control.

The dedicated 16-bit grass clock uses 1/300-second units: +5 per nominal NTSC
60-Hz tick / +6 PAL 50-Hz tick; **600 units = 2 seconds**. It saturates at 600.
The existing low-byte RTC delta supports 1–255 missed ticks, with no duplicate
updates. Thus 1.3s grass → 3s shoulder → 0.7s grass crashes, whereas entering
pavement clears the clock. Left/right grass share the same exposure clock.

| Grass units | Presentation |
| --- | --- |
| 0–149 while exposed | Skid/tire cue |
| 150–299 | Mild bounded irregular render-only shake |
| 300–449 | Gray smoke and short normal warning beeps |
| 450–599 | Denser/brighter smoke, stronger shake, urgent beeps |
| 600 | Latched orange/red crash |

Retained shoulder exposure can retain the warning artwork/shake stage. Its
next-beep clock pauses and no new pulse starts; an existing short pulse finishes.
Pavement clears all off-road particles and sounds. GAS HUD flashing continues
independently; there is no grass gauge or new HUD field.

All terminal tests use unrounded counters, in order **GAS 100% → grass 600 →
MI zero**. GAS uses the accepted green explosion; grass uses an orange/red
explosion. Both freeze active driving/counters, run the existing 150-unit
half-second animation, then remove exactly one life. BILLY BLEW IT! / GAME OVER,
fresh-FIRE retries, retained lives and new-three-life-game rules are unchanged.
Retries reset GAS, mileage, speed/X/Y, scroll and every off-road effect/clock.
Arrival freezes effects/audio and preserves the pharmacy → FIRE → COMPLETE →
separate FIRE → new-game sequence. No later outcome can replace a latched result.

No winding/narrowing roads, forks, traffic, blasts, pickups, new HUD gauges,
Stage 3 or Stage 1 integration are implemented.

## Concrete provisional art/audio tuning

These are implementation choices within §28, pending actual Atari800 evaluation:

- Combined car shake amplitude is the **maximum**, not sum, of GAS and off-road
  requests, never more than ±2 native color pixels. Pressure-only shake keeps
  the accepted alternating cadence. Off-road stages use bounded eight-update
  irregular patterns; logical X is never perturbed. Both car planes align and
  clamp to hardware HPOS 48–148 (8-pixel car ends at pane edge 156).
- PMG P2 supplies 8×16 skid/smoke shapes, starting 12 scanlines below the car's
  top. Its old footprint is erased before every redraw/Y relocation. P0/P1
  remain the accepted red/white car. Particle colors are gray 6/10/14; max trail
  bottom is local scanline 188, inside the 192-line pane. No font/HUD redraw.
- POKEY **AUDF1/AUDC1** only: normal frequency divisor 100, control $A4; critical
  divisor 55, $A6. Pulses last 30 units (~0.1s), repeat after 120/60 units
  (~0.4/~0.2s) on grass. Other channels are untouched except existing cold-start
  silencing. Audio stops on pavement/results/retry. This executable is standalone;
  accepted opening music/source is not altered or integrated.
- Off-road cloud animation alternates palette $28 (orange), $36 (red), $28;
  GAS remains $C8 green. Shapes and 0.5s timing reuse accepted explosion art.

## Memory and performance

| Allocation | Use |
| --- | --- |
| $2000–$23A5 | Accepted native r3 driver/state, checked jump/steering hooks |
| $2400–$27BF, $2800 | Unchanged live screen / ANTIC display list |
| $2900+ | Existing GAS/distance/game state, unchanged addresses |
| **$2A00–$2A10** | **17 new state bytes**, including separate 16-bit grass clock |
| **$2B00–$2B3F** | Four 16-byte original skid/smoke patterns |
| **$2B40–$2B53, $2B60–$2B77** | Effect/POKEY tuning and bounded jitter tables |
| $3000/$3400, $3800 | Unchanged font banks / 2 KB PMG block |
| **$3E00–$3EFF** | Previously unused PMG P2 plane, runtime smoke/skid |
| $4000–$681F | Accepted geometry/font/Y/sprite data |
| $6900–$6E57 | Existing MPH/time-rate and explosion tables |
| $7000+ | Expanded native v0.4 controller, exact extent in manifest |
| $8000/$8400/$8800/$8C00 | Unchanged pharmacy/complete/failure/game-over scenes |
| $9400/$9800–$9FFF | Unchanged road/PMG reset templates |

All segments stay below $A000; stock 64 KB with BASIC disabled is sufficient.
No new zero page or interrupts: original $80–$84/$86–$89 remain. P2 uses existing
single-line PMG DMA, PMBASE $38 and DMACTL $3A; GRACTL remains 2. Color P2 shadow
$02C2 / hardware $D014 and HPOSP2 $D002 are added. HPOS is never read back.
New POKEY writes use $D200/$D201 and standalone reset AUDCTL=$00, SKCTL=$03.
The geometry, all HUD/font/scene data, car sprite, speed/Y and distance tables
are byte-identical to v0.3. Only native controller/hooks and declared new
state/effect tables differ. No accepted binary/listing/manifest is rewritten.

See `profile.json` and [validation results](validation.md) for measured costs.
CPU costs exclude ANTIC DMA/OS interrupts. Whole-screen scene/retry redraws may
span frames as in the accepted baseline. Low-byte clock sampling cannot recover
a full 256-tick wrap without an observation; 60/50-Hz timekeeping is nominal.
Actual raster/sound quality, hardware timing and handling feel need Atari800.

## Emulator playtest checklist

**Atari800: NOT RUN here (not installed); physical hardware: NOT RUN.**

1. In NTSC XL/64 KB/BASIC off, then PAL, steer onto each shoulder and each grass
   edge. Check car-center crossings, normal/shoulder/grass steering 12/10/8,
   and unchanged throttle/Y. Sprite overlap alone must not trigger grass.
2. Hold ~1.3s on grass, pause ~3s on shoulder, then re-enter grass: crash after
   ~0.7s. Return to pavement first: exposure/warnings clear and a fresh ~2s is
   available. Check skid, mild shake, smoke, critical smoke/sounds on both sides.
3. At GAS 75%/90%, compare pavement/shoulder/grass control: penalties must not
   stack below 8. Car remains visible, shake bounded, HUD fixed and GAS-only
   flashes independent. Check effects/audio clear on pavement and no PMG ghosts.
4. Compare orange/red grass crash with green GAS explosion. Check frozen GAS/MI,
   one life loss, fresh-FIRE retry with reset effects, 3→2→1→0 and GAME OVER
   new-three-life game; held FIRE/START must not bypass results.
5. Drive normally to the pharmacy, including after a retry. Check unchanged
   exterior, two separate fresh FIRE presses and clean new run. Report NTSC/PAL
   mode, audio/readability and performance before acceptance.

No merge, tag or branch deletion; awaiting explicit user gameplay acceptance.
