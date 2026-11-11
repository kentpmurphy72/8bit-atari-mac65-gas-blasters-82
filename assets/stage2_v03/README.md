# Stage 2 v0.3 — Road Geometry Only

Standalone native 6502 XEX for stock Atari 800XL / 64 KB. Changes accepted
v0.2-r1 scenery to **14 grass / 7 shoulder / 66 pavement / 7 shoulder / 14 grass**
color pixels across the 108-pixel driving pane. The 13-column HUD is unchanged.
**Implemented, CPU tested, and user-playtested/accepted in Atari800 on 2026-11-11.** Codex's build environment did **not** run Atari800; this acceptance comes from the user's independent gameplay check.

## Build, test and launch

From repository root (builder needs Python 3 standard library only):

```bash
python3 tools/build_stage2_v03.py
# For CPU tests, install pinned py65 requirements into a virtual environment:
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements-stage1-test.txt
.venv/bin/python tools/test_stage2_v03.py
.venv/bin/python tools/test_stage2_v02_r1.py
.venv/bin/python tools/test_stage2_v01_r3.py
.venv/bin/python tools/profile_stage2_v03.py
atari800 -xl -ntsc -nobasic -run assets/stage2_v03/GasBlasters82_Stage2_Road_Geometry_v03.xex
# Repeat with -pal instead of -ntsc.
```

Joystick port 1: LEFT/RIGHT steer; UP accelerates, DOWN brakes to a positive
minimum; diagonals combine actions. FIRE is inert during driving and controls
result-screen retries/continuation. START/F4 is disabled. Reach the pharmacy
before GAS reaches 100%; the three-life explosion/retry and two-press pharmacy →
COMPLETE → new-game flow are unchanged from accepted r1.

There is **no traction change, grass timer, crash, winding road, fork, enemy,
car blast or pickup**. Driving onto grass/shoulder has no gameplay penalty.
Pressure warnings and gas explosions still occur for their original reasons.
Stage 1/opening and all historical artifacts remain separate and unchanged.

## Geometry and source

| Band | Width | Local x interval |
| --- | ---: | --- |
| Left grass | 14 | [0,14) |
| Left shoulder | 7 | [14,21) |
| Pavement | 66 | [21,87) |
| Right shoulder | 7 | [87,94) |
| Right grass | 14 | [94,108) |

Widths approximate the approved 13/6.5/61/6.5/13% as
12.96/6.48/61.11/6.48/12.96%. `geometry.json` is the canonical input;
`zone_at()` and manifest `zone_for_local_x` expose the same half-open boundaries
for offline verification. **No runtime zone classifier or timer is activated.**
Car-center classification at Billy's Y belongs to the subsequent off-road
increment; render-only shake must never determine that future logical position.

The builder checks the accepted r1 XEX checksum, regenerates the 32 road-font
phases and 27-column screen assignments, and encodes a new XEX. It uses eight
four-color horizontal categories with four vertical row phases each: exactly
the existing 32 animated glyphs. New sub-character boundaries therefore need
no native CPU, mode, palette, font-budget or memory-allocation change. Original
grass/shoulder textures and the centerline at local x=54 remain. Temporary gray
shoulders retain the accepted palette; final art is not part of this task.

Only six segments differ from r1:

- $2400 and $9400: the 27 road columns in live screen / restart template.
- $3000, $3400, $6000: only the first 256 font bytes (animated road glyphs).
- $4000–$5FFF: the 32 immutable road-font pages.

HUD screen cells and font glyphs, pharmacy/failure/completion scenes, PMG sprite
bytes, palettes, distance/time/speed tables, all state and **every native code
byte at $2000 and $7000 remain identical**. RUNAD, ANTIC display list and all
load-segment start/end addresses are unchanged. The accepted r1 GTIA write-only
position repair is preserved; no new I/O or zero-page usage is introduced.
The unused historical zone telemetry in the old driver is not active gameplay.

The complete unchanged native runtime is copied as
`pressure_destination_6502.asm` and `r3_driver_reference.asm`, with its original
attribution. These are emitted listings, **not independent MAC/65 masters**.
Authoritative native emitters remain the preserved r1/r3 builders. v0.3's
geometry source/build tool is `tools/build_stage2_v03.py`; it never rewrites
accepted artifacts. The XEX executes actual 6502/ANTIC/GTIA code, not Python.

## Evidence and limitations

See [actual validation results](validation.md), `validation.json`, native test
logs, checksum/load [manifest](manifest.json), `profile.json` and
`preservation.json`. The suite inherits all 27 r1 cases (adapting its two
version-specific artifact assertions and profiling to the new XEX), then adds
six geometry/differential tests. Accepted r1 and older regressions run separately.

[Layout preview](layout_preview.png) is generated directly from XEX font/screen
bytes with approximate RGB and an illustrative default car pose. It is **not
an Atari800 screenshot** or proof of real raster behavior.

**Atari800 NTSC/PAL: NOT RUN; hardware: NOT RUN.** No Atari800 executable is
installed in the build environment. CPU tests use py65 and the r1 GTIA register
read/write-alias shim; they do not emulate ANTIC DMA or OS interrupts. Native
code is unchanged, so existing CPU timing/transition/nominal-60/50-Hz clock limits
remain. Visible redraw stutter, colors, flicker, actual input and handling feel
were left for emulator confirmation; the user subsequently played the v0.3 XEX and confirmed it **looks good and works great**. Exact NTSC/PAL mode and physical Atari 800XL coverage remain unspecified. Off-road gameplay behavior is deliberately not included in this accepted geometry revision.

## Brief Atari800 checklist

1. Run NTSC XL/64 KB with BASIC off, then PAL. Compare to r1: grass is wider,
   pavement narrower, shoulders equal on each side. Centerline and full-height
   boundaries scroll cleanly; all five HUD sections remain fixed/readable.
2. Steer freely across pavement, shoulders and grass at minimum/default/maximum
   speed, including diagonals and both edges. Check r1 speed/Y/smoothing and
   steering feel, no traction changes or off-road life loss after >2 seconds.
3. Brake to see 75%/90% warnings: car stays visible and inside the road pane
   while shaking and GAS flashes. At 100%, check the original explosion/life
   loss/FIRE retry, and that the new road geometry returns after retries.
4. Drive at default speed to the pharmacy (~2 minutes); inspect unchanged
   exterior and both fresh-FIRE transitions. Repeat new-game/retry cycles;
   check no HUD/font/PMG ghosts. START must not bypass lives or results.

**Geometry user-accepted.** The user approved immutable tag `stage2-v0.3`, integration into `main`, and retirement of the completed feature branch, pending actual remote Git ref verification. No additional gameplay behavior is included.
