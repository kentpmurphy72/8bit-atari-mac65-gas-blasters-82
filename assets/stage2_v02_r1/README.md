# Stage 2 v0.2-r1 — Car visibility during pressure warnings

Fix for the disappearing car at 75% gas pressure. The original v0.2 XEX/source/
manifest/tests are preserved under `assets/stage2_v02` and their original tools.
Use this **separately versioned r1 XEX** for further v0.2 gameplay evaluation.
No steering, speed/Y, pressure, warning amplitude, HUD flash or life rules change.

## Root cause and correction

GTIA addresses have different meanings on reads and writes. `$D000` is **HPOSP0**
(player 0 horizontal position) on writes and **M0PF** (missile 0/playfield collision
flags) on reads. The original warning code read `$D000`, added/subtracted the
shake amplitude, and wrote it back to HPOSP0/HPOSP1. With the normal zero collision
flags, it positioned the car at 1 or 255 when warnings began, outside the road.
PMG image bytes, colors and display enables remained intact.

r1 computes both shake directions from the accepted driver's RAM `PIX_LO` plus
origin 48, then adds/subtracts the original ±1/±2 amplitude and clamps to 48–148.
It never reads back the GTIA position register. This also keeps visual jitter
independent of collision flags and prevents cumulative shake drift. Both player
planes stay aligned; the accepted driver's PMG Y relocation is unchanged.

The previous py65 tests used flat RAM, which incorrectly let HPOSP0 reads return
its last written position. New tests explicitly model the collision-read alias,
reproduce the defect in the original XEX and check the fixed emitted 6502.
This minimal CPU-bus model is **not Atari800 or ANTIC/GTIA video emulation**.

## Build and run

```bash
python3 tools/build_stage2_v02_r1.py
# Install tools/requirements-stage1-test.txt in a virtual environment first.
.venv/bin/python tools/test_stage2_v02_r1.py
.venv/bin/python tools/test_stage2_v01_r3.py
.venv/bin/python tools/profile_stage2_v02_r1.py
atari800 -xl -ntsc -nobasic -run assets/stage2_v02_r1/GasBlasters82_Stage2_Pressure_Destination_v02_r1.xex
# Repeat with -pal in place of -ntsc.
```

Builder needs only Python stdlib. Tests/profiler use pinned py65 1.2.0.
`tools/build_stage2_v02_r1.py` and the emitted
`pressure_destination_6502.asm` describe the native correction. Listings remain
emitter output, not independent MAC/65 master sources. RAM/load allocations are
unchanged; the extension grows by six bytes below $8000. No extra state/ZP,
interrupt or I/O register is introduced. See `manifest.json` for exact segments,
entry and checksum; `profile.json` for CPU-only costs excluding DMA/OS interrupts.

All segments except the native controller at $7000 match original v0.2 byte
for byte, including the complete r3 driver/hooks and all gameplay data. `preservation.json`
compares every pre-fix asset/tool blob with commit
`e2a615cb6653b7d7b30a0f430706957066f3f35f`. See `validation.md` and test logs for
actual run results. The original [v0.2 build notes](../stage2_v02/README.md) describe
unchanged gameplay, timing, memory, provisional tuning and known limitations.

## Atari800 playtest still required

**Atari800: NOT RUN; physical hardware: NOT RUN.** No Atari800 executable is
installed in this environment. CPU tests cannot establish actual raster output,
controller mapping, flicker or handling feel; user acceptance is pending.

1. Brake below default speed so arrival does not precede warnings. Check the
   red/white car is continuously visible around 74→75%, 90% and 99%, including
   while GAS blinks off. Repeat in NTSC and PAL.
2. At both warning levels steer across the road to both edges; accelerate/brake
   and combine diagonal inputs. Check mild/strong shake, Y smoothing, aligned
   body/highlights, no HUD intrusion and unchanged control feel.
3. Confirm explosion at 100%, one lost life, FIRE retry with reduced lives, and
   restored visible red/white car. Check pharmacy/completion replay as before.

No merge or tag; awaiting gameplay acceptance.
