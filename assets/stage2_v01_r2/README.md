# Stage 2 v0.1-r2 — speed-dependent vertical car movement

Native 6502 standalone XEX for a stock **64 KB Atari 800XL**, BASIC disabled,
NTSC reference timing. This is **revision 2 of v0.1**, not Stage 2 v0.2.
Built on `feature/stage2-driving-v0.1`. No merge or tag. **Atari800 testing pending.**

The original user-playtested v0.1 XEX, manifest, art and build/test/profile utilities
are preserved byte-for-byte at `assets/stage2_v01/` and `tools/*stage2_v01.py`.
Stage 1 and its opening/music remain unchanged.

## Run / compare

With Atari800's XL OS ROM configured, run from the repository root:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage2_v01_r2/GasBlasters82_Stage2_Driving_v01_r2.xex
```

For a downloaded file in your current directory:

```bash
atari800 -xl -ntsc -nobasic -run ./GasBlasters82_Stage2_Driving_v01_r2.xex
```

Original comparison baseline:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage2_v01/GasBlasters82_Stage2_Driving_v01.xex
```

## Controls / revised behavior

- Joystick port 1 **UP** accelerates the scrolling road and moves the actual car
  gradually upward toward the faster-speed target position.
- **DOWN** brakes to the same positive minimum and moves the car gradually down.
  Neither the road nor car reverses forward direction.
- **Neutral** preserves the speed and its Y target. Brief smoothing may continue;
  once settled the car stays there indefinitely, without springing to default Y.
- **LEFT/RIGHT** retain exact original smooth Q4 steering across the entire Y range.
  Diagonals combine steering and speed adjustment; opposing axes cancel.
- **FIRE** remains inert; it does not stop driving.
- **START/F4** restores X center, default speed, aligned default Y, road phase and
  demo HUD. Release to rearm; held START does not repeatedly reset.

## New provisional Y tuning

Y is the car's **top edge**, in logical scanlines from the 192-line viewport top.
The original 8-color-pixel ×16-scanline car artwork is unchanged.

| Speed (Q4 scroll units) | Road rate | Desired top Y | Car-center Y |
|---|---|---:|---:|
| Minimum 8 | 0.5 scanline/tick | 160 (low) | 168 |
| Default 24 | 1.5 scanlines/tick | 144 | 152 |
| Maximum 56 | 3.5 scanlines/tick | 112 (high) | 120 |

The speed-to-target mapping is monotonic and linear. With these defaults,
**targetY = 168 − speedQ4**; table entries are stored as 16-bit Q4 coordinates.
Targets are clamped in the generated lookup even for out-of-range speed indices.

Current Y approaches its target by at most **12 Q4 units = 0.75 scanline/tick**.
Movement is immediate toward the target, bounded, and clamped against overshoot.
PMG has one-scanline vertical resolution, so fractional movement produces visible
0/1-scanline changes, never character-cell steps or a jump to the final target.
No input-dependent accumulated Y drift is used.

At the unchanged acceleration rate, default→max speed takes 32 ticks; Y then
finishes smoothing in **11 neutral ticks (~0.18s nominal NTSC)**. Changing the full
speed range can require up to ~16 settling ticks. These ranges/smoothing values
are initial engineering choices for user playtest, not final game rules.

At the extremes the whole sprite remains well inside the road viewport: top
112..160, bottom 128..176, with 16+ scanlines of bottom margin. Hardware PMG starts
at **32 + floor(carY)**; P0/P1 row positions therefore range from 144 to 192.
Neither plane writes beyond its 256-byte bitmap.

Edit this revision's `tuning.json` for Y endpoints/smoothing. The build validates
that default speed still maps to default Y and the sprite fits. Fixed layout/art
constraints remain 27/13 columns and 8×16 car; unsupported geometry requires code.

## Preserved behavior and graphics method

The straight road, grass/shoulder/pavement boundaries, fixed 27/13-column HUD,
car X range [0,100] color pixels, 12-Q4 steering rate, speed min/default/max
8/24/56, acceleration ±1, FIRE reservation, zone telemetry, placeholder game values
and 32-line scroll period are unchanged. No pressure, destination, penalties,
traffic, forks, car blasts or Stage 1 integration is added.

The same double-buffered ANTIC 4 character-set animation keeps the right HUD
fixed. New code only selects a Y target, smooths current Y and relocates the car.
When integer Y changes, it clears **all 16 old rows in both PMG planes first**,
then writes the unchanged 16-row body/highlight images at the new location.
When integer Y stays the same, it skips bitmap writes. PMG setup, colors, horizontal
pixel mapping, display list, road pages, font banks and initial car bitmap are
identical to v0.1. This avoids accumulating old sprite rows; actual flicker/tearing
still requires observation in Atari800.

## Build and tests

Build is Python 3 standard library only; runtime is native 6502:

```bash
python3 tools/build_stage2_v01_r2.py
```

`tools/build_stage2_v01_r2.py` is authoritative. It reuses the original **read-only**
art generator, emits a separate controller and adds Y target/sprite tables.
`driving_6502.asm` is a generated instruction listing, not an independent MAC/65
build. Manifest records segments, tuning, exact targets, hashes and original XEX hash.

Test/profile dependency is the existing pinned py65 1.2.0:

```bash
python3 -m venv /tmp/gas-driving-tests
/tmp/gas-driving-tests/bin/pip install -r tools/requirements-stage1-test.txt
/tmp/gas-driving-tests/bin/python tools/test_stage2_v01.py
/tmp/gas-driving-tests/bin/python tools/test_stage2_v01_r2.py
/tmp/gas-driving-tests/bin/python tools/profile_stage2_v01_r2.py
```

**Results:** 19 revision tests PASS, including the inherited original driving
coverage and three-minute native simulated idle run; 12 original v0.1 tests PASS
against the original build. New checks cover both Y limits, neutral settling/hold,
intermediate targets, monotonic mapping, per-tick motion bounds, both PMG planes'
complete byte-level relocation/cleanup, steering and diagonals at both extremes,
FIRE, reset/fractions, fixed HUD/fonts, memory guards, deterministic builds and
original source/artifact preservation. Stage 1 v0.4/v0.5 tests (15+18), four design
validators and opening CPU/DLI/music validation also PASS.

## Memory and CPU samples

All original buffers and artwork allocations are retained. New/changed ranges:

| Range | Use |
|---|---|
| $2000–$23A5 | Revised controller/state (934 bytes), still below screen $2400 |
| $6600–$66FF | 256 low bytes of Q4 Y targets |
| $6700–$67FF | 256 high bytes of Q4 Y targets |
| $6800–$681F | Immutable original body/white-highlight images for row relocation |

Existing memory: screen $2400, display list $2800, fonts $3000/$3400, PMG block
$3800–$3FFF (P0 $3C00, P1 $3D00), road pages $4000–$5FFF, template $6000, telemetry
$6400/$6500, zero-page pointers $80–$83. No additional zero page or interrupts.
This is standalone memory and still requires explicit relocation/scene switching
before future Stage 1 integration.

`profile.json` contains repeatable CPU-only samples tied to this XEX hash:
neutral/default 4,766 cycles; sampled acceleration+steer max 5,513; brake+steer
max **5,517**; START reset from high Y 5,460. PMG plane bytes are verified on sampled
ticks. These exclude ANTIC DMA/OS interrupts and do not establish real frame timing.

## Known limits / recommended Atari800 checks

No actual Atari800, physical 800XL or PAL test has been run here. CPU byte checks
establish relocation logic, not visible cleanliness, final alignment or game feel.
All original demo limits and compact-font/PMG pixel quantization remain.

1. Compare the preserved original with r2: UP should now move the **car itself**
   upward while road speed rises. Hold until cap and confirm no continuing drift.
2. Release UP: speed stays high and Y settles briefly, then holds high. Test a
   partial acceleration/release too; it must not spring back to default height.
3. Hold DOWN through minimum: road keeps moving forward; car settles low without
   falling offscreen. Release and confirm low position/speed hold.
4. Steer left/right at both Y extremes; try all four steering/speed diagonals and
   FIRE held. Car stays within the driving pane and HUD remains fixed/readable.
5. Alternate acceleration/braking around intermediate speeds. Look closely for
   old red/white rows, trails, flicker, blanking, clipping or road/font corruption.
6. START from high/low/fractional Y and both X edges repeatedly: default X/Y and
   speed return, no residue; holding START should not repeatedly reset.
7. Leave neutral at a nondefault speed for several minutes. Report perceived Y
   range, smoothing delay, feel, sprite artifacts and whether the change is clear.

This is v0.1-r2 awaiting user review. No merge into main and no tag created.
