# Stage 2 v0.2 — Pressure & Pharmacy Destination

Implemented native 6502 standalone prototype for stock 64 KB Atari 800XL.
CPU verified; **Atari800: NOT RUN; hardware: NOT RUN; user acceptance pending**.
Accepted Stage 1/opening and Stage 2 v0.1/r2/r3 files remain unchanged.

From the repository root:

```bash
python3 tools/build_stage2_v02.py
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements-stage1-test.txt
.venv/bin/python tools/test_stage2_v02.py
.venv/bin/python tools/profile_stage2_v02.py
atari800 -xl -ntsc -nobasic -run assets/stage2_v02/GasBlasters82_Stage2_Pressure_Destination_v02.xex
# Repeat with -pal in place of -ntsc.
```

The builder needs Python 3 standard library only. py65 1.2.0 is an offline test
requirement. The XEX runs native NMOS 6502 instructions with actual ANTIC 4/GTIA
PMG hardware; it needs no Python or emulator-specific service on the Atari.
Configure joystick **port 1** and its trigger in Atari800. UP accelerates, DOWN
brakes to a positive minimum, LEFT/RIGHT steer; diagonals combine actions.
Neutral holds speed and settles toward its speed-dependent Y. FIRE is inert
while driving. **Console START/F4 is disabled in this version.**

Reach the pharmacy before pressure reaches 100%. Arrival freezes the simulation
and displays an original pharmacy exterior. Release then press FIRE to see
STAGE 2 COMPLETE; release and press again for a new three-life run.
At 100%, a half-second, three-frame green gas explosion freezes the drive, then
removes exactly one life. FIRE after BILLY BLEW IT! retries with remaining lives.
FIRE after GAME OVER starts a new three-life game. Each result requires a fresh
press; holding FIRE cannot dismiss multiple scenes. A same-tick arrival/100%
tie is a failure. Success is latched and cannot subsequently explode.

## Confirmed rules and provisional tuning

The approved Sections 16–21 rules are implemented. Numerical balancing and the
following visual/handling choices remain provisional until user playtesting:

- Mild warning at 75%: ±1 color-clock visual shake, steering step 10/16 pixel
  instead of normal 12/16; gas bar/percentage flash with 0.5-second half-period.
- Critical warning at 90%: ±2 color-clock shake, steering step 8/16 pixel;
  0.1-second flash half-period. Shake direction alternates every four observed
  updates. Both warnings retain acceleration, speed limits, and r3 Y behavior.
- Shake offsets the rendered PMG only and is clamped inside the 108-color-pixel
  road pane. Logical X does not drift. All other HUD content stays stationary.
- GAS displays floor(percent); the bar uses ceil(percent/10) filled segments.
  Distance displays ceil(remaining hundredths), so 0.01 remains until actual zero.
  MPH displays floor(modeled MPH), while distance retains quarter-MPH precision.
- Explosion lasts 150 time units (0.5 seconds), with three expanding 24-row PMG
  shapes. Lives change **after** the animation. No new audio is implemented.
- Pharmacy art uses brick walls, roof, windows, door, green crosses and a readable
  PHARMACY sign. Static scenes retain the 27/13 split and final HUD values.

## Source, arithmetic and memory

`tools/build_stage2_v02.py` is the authoritative offline emitter. It reads the
immutable, checksum-checked r3 XEX and emits five documented patches: RESET,
FRAME and TELEMETRY jumps, plus the two steering operands. The unchanged r3
controller remains at $2000. `pressure_destination_6502.asm` is the extension's
faithful emitted listing, with exact driver patches; `r3_driver_reference.asm`
is the unmodified baseline listing. These listings are **not independently
assembling MAC/65 masters**. Complete baseline builders/source remain in Git.

The r3 Q4 speed mapping uses exact quarter-MPH values: 8→80, 24→240, 56→400,
piecewise steps 10 then 5. Time uses 300 units/second: five per nominal NTSC
60-Hz tick, six per PAL 50-Hz tick, selected from OS PALNTS ($62).
GAS deadline is 49,500 units; warning thresholds 37,125 and 44,550.
Distance uses 4,320,000 units/mile; each clock tick subtracts
`quarter_MPH * elapsed_time_units` from initial 8,640,000. A bounded eight-bit
multiply preserves missed ticks, and native 24/16-bit long division formats HUD
values independently. Events inspect underlying counters, gas first.
At steady default speed, arrival is exactly 7,200 NTSC / 6,000 PAL ticks.

RTCLOK low-byte deltas account for **1–255** elapsed ticks, including wrap.
Driving retains r3's one input/motion update per observed tick; elapsed time and
distance account for the whole delta at the sampled speed. Pausing/starving the
emulator for an entire 256-tick wrap is outside this low-byte clock contract.
Nominal 60/50-Hz arithmetic is used; small real video-rate deviations remain.
Success/failure screens retain a visible final gas indication.
All drive counters/scroll freeze in terminal states; only the explosion's own
timer runs during its animation.

| Allocation | Purpose |
| --- | --- |
| $2000–$23A5 | r3 native driver/state, five checked patches |
| $2400–$27BF | live 40×24 screen |
| $2800–$281F | ANTIC 4 display list |
| $2900+ | v0.2 state (exact extent in manifest) |
| $3000–$37FF | double-buffered 1 KB character sets; first 256 bytes animated |
| $3800–$3FFF | single-line PMG; P0 $3C00, P1 $3D00 |
| $4000–$5FFF | immutable 32-phase road-font pages |
| $6000–$681F | font template, legacy telemetry, r3 Y targets and sprite template |
| $6900–$6DFF | clamped NTSC/PAL fractional-distance and whole-MPH tables |
| $6E00+ | warning tuning and original gas-cloud frames |
| $7000+ | native v0.2 controller (exact end/size in manifest) |
| $8000/$8400/$8800/$8C00 | four 960-byte static scenes |
| $9400–$97BF | initial road/HUD template |
| $9800–$9FFF | immutable original PMG restore template |
| $80–$84, $86–$89 | private ZP pointers/steering; stock OS application-free area |

XEX entry is $2000 via RUNAD $02E0. All assets/code are below $A000; no BASIC
or OS ROM underneath is required. The manifest records every actual segment and
checksum. Standard OS VBI/RTCLOK is enabled, no DLI is added. Hardware/shadow
setup remains r3's ANTIC 4, DMACTL $3A, CHBASE $30/$34, PMBASE $38, GRACTL 2;
static scenes hide players with GRACTL 0 and retries restore both PMG planes and
red/white colors. POKEY channels remain silent. Runtime write auditing covers
private state, stack/ZP, screen/fonts/PMG and specific OS shadows/hardware regs.
This allocation overlaps the separate Stage 1 executable; **no integration**.

## Verification and limits

See [validation results](validation.md), [machine report](validation.json),
[checksum/load segments](manifest.json) and [CPU profile](profile.json).
The suite executes emitted 6502 gameplay, including full-duration 120/165-second
runs for both video standards, fractional integration, fresh/held FIRE, lives,
warning boundaries, latched outcomes, font integrity, write confinement and a
2,000-frame differential r3 driving regression.

CPU costs exclude ANTIC DMA and OS interrupts. Steady driving stays below the
15,000-cycle harness ceiling, including a 1,764-case adversarial sweep.
Whole-screen arrival/retry transitions intentionally span video frames; a brief
redraw can be visible. CPU tests cannot prove raster stability, physical joystick
mapping, appearance, or actual Atari800 frame rate. **Atari800 was not installed**;
a source checkout was investigated, but local autotools/SDL development tooling
and package candidates were unavailable. No real NTSC/PAL emulator, audio,
input-mapping, transition or feel test is claimed. Physical hardware is untested.

## User Atari800 playtest

1. Run NTSC XL/64 KB with BASIC off, then repeat in PAL. Check initial 0%,
   2.00 MI, 60 MPH, three cars and 000000. Verify fixed HUD and smooth road/car.
2. Compare steering, diagonals, acceleration, braking and Y=160/144/80 anchors
   with accepted r3; check edge clamping and font/PMG ghosts.
3. Stay at default speed: arrive near 2:00 at about 72–73% GAS. Inspect the
   pharmacy building; hold FIRE, release/press to COMPLETE, then use a second
   release/press for a fresh three-life run. START must not bypass any state.
4. Brake to minimum and wait: mild warning around 2:03.75, critical around
   2:28.5. Check controllability, escalating shake and **GAS-only** flash.
5. At 2:45 check green explosion, then two lives/BILLY BLEW IT!; FIRE retries
   from default state retaining two lives. Repeat to one then GAME OVER/zero.
   FIRE there must restore three lives. Holding FIRE must not skip results.
6. Check redraw stutter, text/bar/icon readability, no HUD intrusions, and no
   stale sprites after repeated retry/arrival/new-game cycles. Report NTSC/PAL
   timing and balancing impressions before acceptance.
