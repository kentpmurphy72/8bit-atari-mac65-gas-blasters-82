# Gas Blasters '82 — Stage 1 Playable Prototype v0.2

> **Historical prototype status (2026-11-03):** This `v0.2` milestone is preserved at immutable Git tag `stage1-v0.2`. Its work and history were integrated into `main` via the accepted `stage1-v0.5` baseline; the original feature branches were deleted after tagging. Three fixed restaurant rooms; the user playtested room transitions and found the stage too short/easy. **Any older “not merged” or “emulator test pending” language below records the original build-time status, not current repository status.** For implemented current behavior, see [Stage 1 Design](../../docs/STAGE1_DESIGN.md). This versioned artifact and build instructions are retained unchanged except for this note.


Native 6502 XEX for a stock 64 KB Atari 800XL, BASIC disabled. Three fixed-screen
rooms replace the Stage 1 v0.1 scrolling map. Gameplay direction is approved;
exact maps, timing, sprites and difficulty remain provisional until Atari800 tests.
No Atari800 visual/audio test or real-hardware test has been performed here.

## Download and run

Use **GasBlasters82_Stage1_Playable_v02.xex** from this directory on branch
`feature/stage1-room-screen-v0.2`. From the repository root:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1_v02/GasBlasters82_Stage1_Playable_v02.xex
```

If the XEX was downloaded into your current directory:

```bash
atari800 -xl -ntsc -nobasic -run ./GasBlasters82_Stage1_Playable_v02.xex
```

Atari800 must have its XL OS ROM configured. NTSC is the existing opening's timing
reference; PAL timing and compatibility remain untested.

**Title: press console START (normally F4), not joystick FIRE.** On laptops this
may require Fn+F4, depending on function-key settings. Release before pressing.
At **Meet the Crew** and **Arrival**, use joystick port 1 **FIRE** (the trigger
key you configured in Atari800). Holding FIRE cannot skip multiple screens.

## Play

- Joystick port 1 moves Billy one cardinal tile per movement tick, with no diagonal
  movement. Multiple held directions use the v0.1 up/down/left/right priority.
- Dining, kitchen and storage each fill all 40 columns × 22 rows. The last two
  rows are instructions/status. No camera, panning or scrolling.
- Billy is a narrow running-person glyph; hazmat is a broad helmeted glyph. Walls
  and furniture have different solid patterns; floor and inert grease are blank.
  Rear X is a crossed marker. These are temporary monochrome graphics.
- Enter the two-high D opening on the dining right edge to reach kitchen. Kitchen
  left returns to dining; kitchen right reaches storage; storage left returns to
  kitchen. Both doorway rows preserve Billy's y. Spawn is one tile inside the
  destination, avoiding automatic bounce-back. You can deliberately step backward.
- One worker activates in dining at (2,10) after 180 NTSC frame ticks. In the same
  room it uses incremental cardinal breadth-first pursuit through walkable cells.
- Leaving its room retains the worker's position and schedules a 90-frame follow
  along the corresponding adjacent room link. Returning before arrival cancels
  that follow. If Billy travels through two rooms quickly, the worker must enter
  the intermediate room before scheduling the next 90-frame link.
- Both actors avoid an occupied preferred doorway entry by choosing a valid
  adjacent tile. Only the existing worker continues; no duplicate or reinforcement.
- Contact shows CAUGHT; storage rear exit at (39,10) shows STAGE COMPLETE. Either
  result freezes play. Release then press console START/F4 to restart Stage 1 in
  dining with Billy at (7,15), worker inactive, and a fresh initial delay.
- No gas attack, grease sliding, scoring, lives system, extra enemies or Road 1.
  Reload the XEX to replay the introduction.

## Source and build

Run from the repository root. Building requires only Python 3 standard library:

```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
python3 tools/build_stage1_v02.py
```

Authoritative runtime source is `tools/build_stage1_v02.py`, using the existing
`Asm` 6502 byte emitter in `tools/build_opening_sequence.py`. This runs offline;
only emitted 6502 machine code runs on Atari. `stage1_6502.asm` is the generated
instruction listing, not a standalone MAC/65 build. Terrain and link data come
from the canonical v0.2 JSON and three `.map` files under `assets/maps/`.

The builder produces only new files under `assets/stage1_v02/`. The known-good
opening v1 XEX, Stage 1 v0.1 assets, maps, builder and tests remain unchanged.
The manifest records output/baseline SHA-256, labels and segment allocations.

## Automated validation

Test-only dependency: py65 1.2.0, already pinned in the retained requirements file.
No py65 dependency is required to build or run the Atari binary.

```bash
python3 -m venv /tmp/gas-stage1-tests
/tmp/gas-stage1-tests/bin/pip install -r tools/requirements-stage1-test.txt
/tmp/gas-stage1-tests/bin/python tools/test_stage1_v02.py
/tmp/gas-stage1-tests/bin/python tools/test_stage1.py
python3 tools/validate_opening_sequence.py --output /tmp/gas-opening-v02-validation
```

Results on this branch:

- Both map validators PASS. v0.2: dining 662, kitchen 625, storage 613 connected
  walkable tiles; four reciprocal room links, one rear exit.
- **16 v0.2 CPU tests PASS**, executing the actual generated 6502 opcodes: all
  2,640 terrain cells and map bounds; eight door cells and reverse travel; held
  direction/re-entry behavior; delayed follow/cancellation/intermediate rooms;
  activation after leaving dining; both actors' occupied entry handling; pursuit
  and incremental input; all room renders and sprite validity/overlay order;
  CAUGHT/START and success; a joystick-driven full escape; VBI elapsed time and
  8-bit clock wrap; segment/scratch guards; deterministic builds and preservation.
- **9 v0.1 CPU tests PASS** without changing v0.1 source or output.
- Existing opening validation PASS, including 48,650 simulated CPU instructions,
  DLI palette handling, release-armed input and music continuity.
- CPU tests do not emulate ANTIC DMA, OS interrupts, audio, or Atari800 itself.

## Memory and timing

All executable/data allocations are below $C000, with BASIC off:

| Range | Use |
|---|---|
| $1000–$17BF | v0.2 controller, variables and room offsets (1,984 bytes) |
| $2000–$27FF | Existing opening controller; only two 3-byte dispatcher patches |
| $2800–$289F | Two-line instructions and result text |
| $2A00–$97FF | Retained opening music, fonts, palettes and three scenes |
| $9800–$9B6F | 880-byte BFS parent-direction scratch |
| $A000–$AA4F | Three 880-byte semantic room maps; high bit = JSON solid flag |
| $AA80–$AB03 | Three sets of 22 map row pointers |
| $AB10–$AB3B / $AB40–$AB6B | Screen / search row pointers |
| $AC00–$AFFF | Custom character set |
| $B000–$B3BF | Shared 40×24 ANTIC 2 display |
| $B400–$B76F / $B900–$BC6F | 880-entry BFS x/y queues |
| $80–$8B | Temporary zero-page pointers, BASIC disabled |

The row pointer lookup is room×44 + y×2, pointing to room×880 + y×40. There is no
48-column addressing or scrolling camera. Terrain is copied first, then the
same-room worker and Billy are overlaid, then the footer. Opening art and songs
are retained byte-for-byte, and stage DLIs are disabled while OS VBI stays active.

Billy retains the v0.1 eight-observed-frame input cadence; same-room searches
wait 16 observed frames between attempts and process at most eight cells per
iteration. Searches target Billy's position when they start. Initial spawn and
90-frame room-follow timers use elapsed RTCLOK/VBI ticks, including missed ticks
and wraparound, rather than assuming every main-loop iteration is one video frame.
Full redraw and search costs can still affect movement responsiveness. Practical
speed/difficulty and PAL behavior require emulator measurement, not CPU assertions.

## Atari800 acceptance checklist — pending user testing

1. START/F4 advances title; FIRE advances each cutscene after release. Compare art,
   captions, DLI palette bands, title Rock and continuous cutscene Funk to opening v1.
2. Each complete 40-column restaurant room is stable/readable with distinct actors.
   Try blocked movement against booths, tables, counters, equipment and shelves.
3. Traverse both doorway rows in all four directions. Hold a direction while
   crossing; confirm no involuntary bounce. Test intentional backtracking.
4. Wait for the one worker. Cross rooms, return before its delayed follow, and
   cross two rooms quickly. Confirm cancellation, ordered follow and no clones.
5. Stand at a preferred entry while the worker arrives; confirm it selects a
   neighboring floor cell. Return into a room with the worker near the doorway.
6. Check CAUGHT, frozen movement and START restart; then reach storage rear X and
   check STAGE COMPLETE, no Road 1, and another clean restart.
7. Check sustained input response, especially distant searches and room redraws.
   Confirm elapsed follow/spawn timing, repeated restarts, and stock 64 KB loading.
8. Real Atari 800XL testing remains outstanding after Atari800 acceptance.

This branch is for testing; it has not been merged into main.
