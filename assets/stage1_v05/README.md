# Gas Blasters '82 — Stage 1 v0.5: eight-way gas blast

**Current documentation:** [Stage 1 Design](../../docs/STAGE1_DESIGN.md) · [Deferred Work](../../docs/STAGE1_DEFERRED_WORK.md) · [Regression Checklist](../../docs/STAGE1_REGRESSION_CHECKLIST.md). This file remains the **version-specific implementation and original build/test record**.

Native 6502 Atari XEX for **64 KB Atari 800XL**, BASIC disabled. Built on
the former `feature/stage1-blast-v0.5` from the working, user-playtested v0.4 branch. **Merged into `main` and preserved at tag `stage1-v0.5`. The user has since played v0.5 and says gas blasting is good enough for now; exhaustive visual/audio/hardware regression remains open.**
All existing v0.1–v0.4 XEXs, sources and tests remain unchanged.

## Download / run

From the repository root (Atari800 must have its XL OS ROM configured):

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex
```

After downloading the binary into your current directory:

```bash
atari800 -xl -ntsc -nobasic -run ./GasBlasters82_Stage1_Playable_v05.xex
```

Title: **console START / normally F4**, not joystick FIRE. Crew and Arrival:
**joystick port 1 FIRE**, released between screens. Original artwork, captions,
DLI behavior, Arcade Rock and continuous Funky Gas Attack are retained.

## Play / attack controls

- Without FIRE, Billy uses the exact v0.4 Q4 eight-way movement, normalized
  diagonals, immediate response, inset hitbox and wall sliding.
- **Hold FIRE to stop and aim.** Select any of eight directions, including a
  diagonal. FIRE may be pressed before the direction; no-direction holds do not fire.
- A stable direction for **four video ticks** discharges one burst. Changing aim
  restarts wind-up. Releasing early cancels without consuming gas.
- **One burst per hold.** Release to rearm. A press during cooldown or with no
  charges is consumed, not queued for later. Release and press again when ready.
- Walking resumes on release once the **eight-frame recovery** from discharge
  ends. Holding FIRE keeps Billy in his stance even after cooldown ends.
- Start with **GAS 3/3**. Each discharge spends one; one charge returns every
  **120 frame ticks**, up to three, while moving or aiming. Cooldown is **20 ticks**.
  The footer shows the supply and READY / COOLING / EMPTY. There is no indoor
  gas-pressure meter or permanently finite ammunition.
- Billy leans away and presents blue jeans toward the aimed direction. The
  temporary two-plane PMG art has eight orientations and two wind-up phases.
  Its readability/comedy needs actual emulator feedback.
- Gas expands over **18 ticks**: one cell for six ticks, then four cumulative
  cone cells for six, then seven for six. The two cloud glyphs alternate shape.
  All eight orientations use the vector/perpendicular geometry in the JSON.
- Each target cell requires supercover visibility: solids, D and X are opaque,
  including both side cells at a diagonal corner. No cloud crosses rooms.
- Several same-room workers can be hit, **once per burst each**. Workers are
  stunned for **75 ticks**; up to three cardinal/diagonal knockback tile steps
  animate at **one step every three ticks**. Target and both orthogonal side
  cells must be terrain- and actor-clear. No wall, door, exit or actor clipping.
- A blocked push displays a **four-tick impact star/BONK**. A blocking worker
  receives **24-tick stagger**, without chain pushing or shortening longer stun.
  Stunned workers remain harmless; existing stun-expiry contact grace is retained.
- A short original ten-tick POKEY noise whoosh accompanies discharge. Result
  screens/restart silence it; opening music tables and timings remain untouched.
- START/F4 restarts Stage 1, resetting workers, charge supply and transient state.
  CAUGHT and storage X completion freeze gameplay; no Road 1 follows.

The same three 40×22 fixed rooms, reciprocal doors, three persistent workers and
AI timings remain. No new maps, scrolling, grease physics, lives or scoring.

## Build, source and tests

Build needs Python 3 standard library only. It reads v0.4 through its unchanged
builder into a temporary directory; it never regenerates older artifacts in-place.

```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
python3 tools/validate_stage1_pressure_v03.py
python3 tools/validate_stage1_blast_v05.py
python3 tools/build_stage1_v05.py
```

`tools/build_stage1_v05.py` is the authoritative native-code emitter and offline
supercover/temporary-art generator. `blast_6502.asm` lists the emitted instructions;
`movement_reference.asm` records v0.4 before the documented PMG hook. These listings
are not independent MAC/65 builds. Manifest: exact segment addresses, hook targets,
version hashes and JSON tuning rules. Python never runs on the Atari.

Test-only dependency is py65 1.2.0, using the existing pinned requirements:

```bash
python3 -m venv /tmp/gas-stage1-tests
/tmp/gas-stage1-tests/bin/pip install -r tools/requirements-stage1-test.txt
/tmp/gas-stage1-tests/bin/python tools/test_stage1_v04.py
/tmp/gas-stage1-tests/bin/python tools/test_stage1_v05.py
/tmp/gas-stage1-tests/bin/python tools/profile_stage1_v05.py
```

**Results:** all four validators PASS; all **15 unchanged v0.4 tests PASS against
v0.4**; all **18 v0.5 CPU tests PASS**. The new tests execute actual XEX opcodes:
all eight FIRE-first and simultaneous aims, wind-up/aim change/cancel/rearm,
no-queue cooldown/empty holds, recovery, renewable supply and clock wrap, distinct
PMG orientations/phases and exposed blue-plane pixels, cone visibility against an
independent closed-square/line intersection oracle in all three rooms, wave
expansion/cleanup, multi-hit single-burst bookkeeping, eight-way animated pushes,
corner/worker collisions and stagger, sound/register cleanup, restart, door entry
alignment/resource continuity, exit, free movement speeds, opening/song continuity,
segment non-overlap, original asset identity and deterministic rebuilds.

## Memory and rendering

The retained v0.4 code/movement is used directly, with checked dispatch patches:
new Stage 1 init/input, before-actor cloud restoration, footer/cloud/HUD rendering,
and a wrapper around gameplay PMG drawing. The original 6×6 pixel contact code,
movement collision and shared eight-cell BFS budget are unchanged.

New allocations occupy previously unused RAM gaps, with overlap checks:

- **$7800 onward**: attack native code (exact extent in manifest). The emitter can
  bridge to other verified empty holes if needed; this build fits before $8000.
- **$5B00–$5FF7**: 56 supercover paths, lengths, cone offsets, two-phase directional
  pose bytes, direction/joystick lookup, sound steps and HUD words. These are in a
  gap after the title captions, not over title artwork.
- **$28A0–$28DF**: blue jeans pose plane data.
- **$2900 onward**: attack state, seven cloud cells/visibility bits, per-worker hit,
  push and impact timers; below the rock music tables at $2A00.
- Existing PMBASE **$B8**: player 0 **$BC00–$BCFF** for red body; player 1
  **$BD00–$BDFF** for blue rear overlay. No missile/extra-player gameplay object.
  P0 leaves transparent holes for the lower-priority P1 blue pixels.
- Existing v0.4 PMG sizing/alignment remains: 2 logical pixels per horizontal PMG
  bit/position step, 1 per scanline, 8×8 logical footprint. Origins remain 48 color
  clocks / 32 scanlines. This is coarse temporary art, not final character artwork.
- Character codes **18/19** are alternating cloud shapes; **20** is the impact star.
  Previously unused glyph slots only. PMG is configured only in Stage 1, not title.
- Existing BFS field, queues, map/font/screen and PMG block do not overlap. The
  v0.4 $80–$8B zero-page pointers are retained; LOS adds **$8C–$8D**, BASIC off.

The cone's seven visibility bits are computed once per discharge. Normal frames
restore only prior cloud cells before the existing dirty-actor renderer, then
paint current cloud/HUD/impact overlays. No whole-map redraw per cloud frame.
Enemy positions update on push ticks, keeping their original identities and room
state. The same elapsed RTCLOK tick source drives effect/resource/push timers.

## CPU profile and limits

`profile.json` is tied to the exact XEX hash and reproducible with the profiler.
Scenario: three workers, four-tick right aim, eight held ticks with cloud/pushes,
then release and walk up while the cloud finishes. **Maximum sampled cost: 20,689
CPU cycles**. Full per-dispatch samples are recorded. These exclude ANTIC DMA and
OS interrupts; they are not an exhaustive worst-case bound or an Atari frame-rate
claim. Existing room redraw/restart can still span video frames.

## Detailed Atari800 acceptance checklist — not yet fully evidenced

1. Confirm unchanged title/cutscene graphics, START/FIRE controls and both songs.
2. Reconfirm v0.4 smooth walking/diagonals and steering around furniture.
3. Try all eight attacks, especially FIRE first then diagonal, direction changes,
   early cancellation, continuous holds and release-to-walk recovery.
4. Is the red-body/blue-jeans backside pose readable and funny? Do all orientations
   and two phases show? Check player-plane priority, alignment and old-row cleanup.
5. Do the three cloud waves grow visibly and feel broad/powerful, with no ghosts
   over actors/furniture and no gas leaking through walls, corners or doors?
6. Watch multi-worker knockback, diagonal corner stops, BONK stars and stagger;
   check stun-expiry fairness and preserved identities across room revisits.
7. Hear the brief noisy whoosh; check it ends on caught/win/restart and never
   corrupts opening audio. Assess READY/COOLING/EMPTY readability and refill pace.
8. Check sustained three-worker input response, PMG flicker and frame pauses;
   reach X and restart repeatedly. Real 800XL and PAL checks remain outstanding.

The user has given broad v0.5 gameplay acceptance, **not an itemized pass for every check above**. For future changes, please report aiming ease, pose/cloud readability, knockback punch, recovery feel,
charge waits, flicker/sound artifacts and overall fun. Numeric values remain
prototype tuning; no stage-duration or final-balance claim is made.
