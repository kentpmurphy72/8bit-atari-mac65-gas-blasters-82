# Gas Blasters '82 — Stage 1 v0.4: movement feel

Native 6502 XEX, stock **64 KB Atari 800XL**, BASIC disabled. Built from the
user-playtested v0.3 implementation on `feature/stage1-movement-v0.4` plus the
v0.4 design files from main. **Not merged. Atari800 and real-hardware tests pending.**

## Run

From the repository root, with Atari800's XL OS ROM configured:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1_v04/GasBlasters82_Stage1_Playable_v04.xex
```

For a downloaded file in the current directory:

```bash
atari800 -xl -ntsc -nobasic -run ./GasBlasters82_Stage1_Playable_v04.xex
```

Title: **console START, normally F4** (Fn+F4 on some laptops). Crew/Arrival:
**joystick port 1 FIRE**, released between presses. In Stage 1, joystick gives
continuous eight-way walking. **Gameplay FIRE is ignored and does not stop Billy.**
START restarts Stage 1 from CAUGHT, COMPLETE or during play. Reload to replay intro.

## Implemented movement

- Top-left coordinates are 16-bit Q4 (one unit = 1/16 logical pixel). Cardinal
  speed is 24 units = **1.5 px per video tick**; diagonals use 17 units per axis =
  **1.0625 px/axis**. Opposite directions cancel. No acceleration or eight-frame gate.
- Motion reads RTCLOK/VBI independently, rejects duplicate ticks, handles clock wrap,
  and catches up at most two ticks per dispatch. Excess lag is dropped, preventing
  a long stall from making Billy jump across furniture. Input is read each dispatch.
- Inset half-open 6×6 AABB: [x+1,x+7) × [y+1,y+7). Every axis is split into <=1px
  candidate steps. Collision checks every distinct overlapped tile. A blocked step
  uses bounded binary search to stop at the last safe 1/16-pixel position.
- X then Y resolution supports wall sliding at the cardinal rate along the free
  axis. Full 8×8 sprite stays in 320×176 gameplay bounds, above the footer.
- Integer hitbox-center tiles feed the unchanged worker/navigation engine. D door
  transitions trigger on the center, use the existing linked metadata, preserve
  doorway y, align to inward tile x=1/38 and clear fractions. Backtracking remains.
- Worker contact uses overlapping inset 6×6 pixel AABBs, not same-tile occupancy.
  Stun/contact grace is respected. Entering storage X with the center wins.
- All three v0.3 worker identities, spawn/movement/follow defaults, shared 8-cell
  BFS budget, maps, CAUGHT/restart and COMPLETE behavior are retained. No AI retuning.
- No gameplay blast/cooldown/knockback/cloud can be invoked in v0.4. The old code
  remains in the immutable baseline for regression; redesign is deferred to v0.5.

## Visible sprite / Atari mapping

Billy is now **GTIA player 0**, separate from the ANTIC 2 terrain. The old Billy
character glyph is suppressed; workers remain temporary character sprites.

- ANTIC 2 standard width is **320 logical pixels / 160 GTIA color clocks**.
- Normal-width PMG has one bit per color clock. Billy uses **four active horizontal
  bits × eight scanlines**, occupying an 8×8 logical-pixel footprint. This is an
  intentionally temporary horizontally coarse sprite: **2 logical pixels per PMG
  bit and horizontal position step**, 1 logical pixel per vertical step.
- Horizontal position = **48 + floor(logicalX/2)** color clocks; vertical position
  = **32 + floor(logicalY)** PMG scanlines (three ANTIC blank rows, plus ANTIC's
  initial display-list scanline offset). Pixel phase/alignment needs Atari800 review.
- Horizontal motion therefore appears in 2px increments, vertical in 1px increments,
  both well within each 8px terrain cell. Fractional state still governs accurate
  speed/collision. There is no claim of 1px horizontal PMG resolution or final art.
- PMBASE=$B8, single-line PMG block **$B800–$BFFF**, player 0 bitmap **$BC00–$BCFF**.
  DMACTL/SDMCTL=$3A; GRACTL=2; normal player size; priority shadow/hardware set to 1;
  COLPM0 shadow/hardware=$36. Each render clears the old eight scanlines, writes the
  new sprite and updates HPOSP0. Other PMG bitmap planes remain zero.
- PMG is configured **only on Stage 1 entry**. No title artwork, title PMG experiment,
  cutscene display list, DLI, captions or song data is changed. Stage retains VBI
  only ($D40E=$40); title/cutscene DLI behavior is preserved.

## Source, build and validation

Build needs Python 3 standard library only:

```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
python3 tools/validate_stage1_pressure_v03.py
python3 tools/build_stage1_v04.py
```

`tools/build_stage1_v04.py` reproducibly builds v0.3 into a temporary directory,
then adds the movement/PMG code and four checked dispatch patches. The old BFS Y
queue is relocated out of the PMG block. No older source or artifact is overwritten.
`movement_6502.asm` is the generated extension listing; `core_6502_reference.asm`
is the unchanged core listing **before** the manifest's dispatch/queue patches.
The Python emitter is authoritative; these are not independently MAC/65 builds.
The manifest contains all addresses, tuning, loaded segments, patches and hashes.

Test-only dependency is py65 1.2.0, using the retained requirements file:

```bash
python3 -m venv /tmp/gas-stage1-tests
/tmp/gas-stage1-tests/bin/pip install -r tools/requirements-stage1-test.txt
/tmp/gas-stage1-tests/bin/python tools/test_stage1_v04.py
/tmp/gas-stage1-tests/bin/python tools/test_stage1_v03.py
/tmp/gas-stage1-tests/bin/python tools/profile_stage1_v04.py
```

**Results:** 15 v0.4 tests pass, including 7,920 fractional terrain-oracle cases,
60-frame speed, reversal, diagonal normalization, wall slide, boundaries/corners,
clock wrap/duplicate ticks/catch-up, all eight door cells, center vs corner trigger,
win/restart, PMG sub-tile register/bitmap motion and cleanup, pixel contact,
FIRE-independent walking, live pursuit during input, actual opening control/music
flow, deterministic output, original-segment identity and memory safety.
All **23 unchanged v0.3 tests** pass against the unchanged v0.3 build, and all
three requested validators pass. CPU tests do not model ANTIC DMA or OS interrupts.

## Memory / measured timing

- **$0400–$096C:** new movement/PMG code and Q4 state, 1,389 bytes. This uses low
  application RAM; gameplay performs no cassette/printer/CIO operations there.
- **$1000–$1E45:** retained v0.3 core, with manifest-listed dispatch and queue patches.
- **$2000 onward:** retained opening/art/music and stage messages; opening unchanged.
- **$9800–$9B6F:** existing BFS field; **$9C00–$9F6F:** relocated 880-entry Y FIFO.
- Existing maps $A000–$AA4F, row tables, font $AC00–$AFFF and screen $B000–$B3BF.
- X FIFO $B400–$B76F; PMG $B800–$BFFF. All loaded segments below $C000, no overlap.
- Original $80–$8B zero-page pointers remain in use; BASIC must stay disabled.

Repeatable CPU-only profile (`profile.json`, tied to the output hash):

| Scenario | Maximum sampled CPU cycles |
|---|---:|
| Cardinal walking, three workers | 23,741 |
| Diagonal walking, three workers | 25,069 |
| Wall sliding, three workers | 26,534 |
| Two-tick movement catch-up, three workers | 25,296 |
| Door entry with whole-room redraw | 42,918 |
| Restart with PMG clear | 34,240 |

Steady-state samples after search initialization are generally lower; complete
per-dispatch sequences are saved in the profile. Search still processes at most
eight cells total per dispatch, rather than per worker. Terrain is not redrawn per
pixel; Billy uses PMG while the core retains dirty-cell rendering for workers.
Room transitions/restart can span video frames. These figures exclude DMA/VBI
costs, are sampled rather than exhaustive worst cases, and do **not** establish
Atari800 smoothness, absence of flicker, or a hardware frame-rate guarantee.

## Atari800 acceptance — pending

1. Compare title, crew and arrival visuals/music/controls with v0.3. No PMG on title.
2. Verify Billy's sprite aligns to tiles and moves within cells in every room,
   including vertical positioning, priority, old-row cleanup and no ghosting/flicker.
3. Compare felt speed with v0.3; reverse/stop/turn immediately and walk diagonally.
4. Slide along tables/counters/shelves, probe corners and both door rows in both
   directions. Check no clipping, footer trespass, bounce-back or fractional spawn.
5. Hold FIRE while moving: no lock, gas effect or attack. Test evading three workers
   without combat, pixel contact fairness, CAUGHT/START reset and storage X success.
6. Watch input latency during active pursuit and room changes. Real hardware and
   PAL behavior are also untested. Difficulty is not rebalanced in this milestone.

Please report steering precision, diagonal/wall-slide feel, sprite alignment and
flicker, catch fairness, and any pauses. Decide whether movement feels ready before
we redesign gas controls in v0.5.
