# Gas Blasters '82 — Technical Design (Incremental)

**Date:** 2026-11-01  
**Status:** Partial Stage 1 v0.2 engine + v0.3 encounter plan; **not** complete architecture for the whole game.

## Existing baselines

The accepted game opening is `assets/opening/GasBlasters82_OpeningSequence_v1.xex`, with Arcade Rock on title and Funky Gas Attack across the two cutscenes. The user has run the playable **Stage 1 v0.1** XEX on `feature/stage1-playable-v0.1`; this branch contains `tools/build_stage1.py`, `tools/test_stage1.py` and `assets/stage1/`, and it has not been merged to main. **Do not overwrite it.**

## Stage 1 v0.2 room engine

- Three independent **40×22 tile** maps, **880 bytes each** / **2,640 bytes total** uncompressed, plus two final 40-column status rows; 40×24 text characters fits a standard 192-scanline display plan. A prototype 8×8 tile footprint is proposed, not the eventual final art.
- All 40 columns are gameplay; **no scrolling or camera position in Stage 1**. Display one room at a time in a shared display buffer. Drawing a new screen can be a whole-buffer redraw; no need for three separate video buffers.
- Each room has its own map coordinates x=0..39, y=0..21. Access `offset=y*40+x` through a **16-bit pointer or row table** on 6502—do not overflow an 8-bit index. Fetch terrain/collision from the room selected by a room ID.
- Four linked doorway transitions defined in `assets/maps/taco_smell_stage1_v02.json`, each `D` tile two characters tall (y=10/11). Trigger on entering the doorway, move Billy to x=1 or x=38 **one tile inside** the destination, preserve y, redraw entire room. Allow reverse crossings; do not auto-bounce.
- `# B T C R K S` are solid; `. D F N G X` are walkable. `G` (grease) is inert v0.2 floor. `X` in storage (39,10) triggers the Stage Complete placeholder.
- One hazmat worker spawns 180 NTSC frames after Stage 1 begins in dining. Preserve its unique identity across transitions; after a door crossing it follows through the matching doorway after approximately 90 frames, without cloning, disappearing or teleporting across nonadjacent rooms. If Billy immediately returns before the follow completes, cancel that pending follow. Future side/rear spawns remain inactive.
- Preserve CAUGHT/restart, input behavior, intro assets/POKEY songs, and the exit success state. No indoor gas-blast/grease mechanics for v0.2.

## Stage 1 v0.3 pressure extension requirements

- The user successfully played v0.2, but found the single pursuer ineffective and Stage 1 too short. Keep the three fixed 40×22 rooms and reuse the currently playable `feature/stage1-room-screen-v0.2` code branch.
- Add three persistent enemy IDs across the restaurant: dining (2,10) at 60 frames, kitchen (29,11) at +30 frames from entry, storage (30,10) at +30 frames from entry. Movement cadence targets 12/10/10 frames and follow delay 45 frames; all are **tuning defaults**, not verified Atari800 behavior.
- One direction-aimed blast on each **new FIRE press**, block movement while FIRE held, ray up to three tiles blocked by solid terrain, knockback up to two cells, stun 60 frames, cooldown 72 frames and short visual effect. Stunned enemy cannot catch Billy. Follow the [v0.3 gameplay contract](STAGE1_GAMEPLAY_PRESSURE_V03.md) and its [machine-readable rules](../assets/gameplay/taco_smell_stage1_v03_rules.json).
- **6502 performance warning:** v0.2 runs one incremental BFS at eight nodes per observed frame. Three independent BFS workers may exceed available processing or make pursuit unresponsive. Codex should implement a bounded multi-enemy scheduling/cached-distance strategy, preserve room-follow identity, and instrument input responsiveness and visual behavior.
- Keep the actual v0.2 XEX and compiler untouched. New `feature/stage1-pressure-v0.3` is expected to produce separate versioned build artifacts, run all v0.1/v0.2 regression tests plus the new tuning validator, and undergo real Atari800 playtesting. Do not claim the tuning works until tested.

## Memory and runtime checks required of Codex

v0.1 uses buffers/data in the high RAM area (starting around `$A000`) and a 6502 extension. Three new maps cannot simply be appended without checking the Atari 64 KB memory map. Derive actual safe allocation from the v0.1 branch's `tools/build_stage1.py` and `assets/stage1/manifest.json`. Validate every XEX segment for overlap and avoid overwriting the working title/cutscene memory, video screen, character set, OS-reserved regions, and music buffers. Preserve the active display-list/DLI behavior.

Run both map validators, CPU/runtime tests of four doors, y-preserving spawn, transitions without auto-reentry, solid collision, unique hazmat, safe row lookup and stage completion. Then the user must test the v0.2 XEX in Atari800; simulation is not a substitute for that emulator check.

## Other stages

The **fixed-screen, non-scrolling** room behavior is specific to **Taco Smell Stage 1 v0.2**, not a restriction on room transitions elsewhere. Later indoor stages—including pharmacy and grocery—may use **room-to-room transitions, camera scrolling inside an area, or a hybrid of both**. A grocery aisle pursuit with police, hazmat workers and townspeople could scroll and then switch sections via a room transition; this remains a design possibility, not a completed technical specification. Driving road stages still use the separate overhead-scrolling driving/HUD design. All game-wide technical decisions remain open (final graphics modes, PMG for moving sprites, global memory map and frame timing, game distribution, lives, score and other levels).

## Implemented v0.2 prototype (feature branch, awaiting Atari800)

- Runtime byte-emitter source: `tools/build_stage1_v02.py`; generated listing,
  manifest, XEX and full memory/timing/build notes: [assets/stage1_v02/README.md](../assets/stage1_v02/README.md).
- Three immutable 880-byte maps at $A000–$AA4F; room-indexed row pointers; shared
  40×24 ANTIC 2 framebuffer at $B000. No camera. All segments remain below $C000; BASIC off.
- Persistent `ROOM`/`EROOM`, one active flag, one queued adjacent follow link and
  90-frame timer. Backtracking to the worker's room cancels that link. Intermediate
  room arrivals precede subsequent follow scheduling; no cloning or spawn reset.
- Shared collision-aware entry selection avoids the other actor's tile. In-room
  BFS is incremental; room changes invalidate stale search data. Spawn/follow
  timers subtract elapsed RTCLOK/VBI ticks, including wraparound.
- Sixteen v0.2 6502 CPU tests, nine retained v0.1 tests, both map validators and
  opening regression validation pass. This is automated CPU/data validation,
  not Atari800 visual/audio/controller acceptance or real-hardware validation.
- v0.1 maps/builder/tests/XEX and the original opening-v1 XEX remain unchanged.
  The v0.2 feature branch is not merged into main.

## Implemented v0.3 prototype (awaiting Atari800)

Source: `tools/build_stage1_v03.py`; executable/listing/manifest and measured
CPU-only profile: `assets/stage1_v03/`. See its [README](../assets/stage1_v03/README.md)
for build commands, exact memory allocations, launch controls and pending tests.

Three indexed persistent workers share one reverse-BFS field, with at most eight
dequeued cells per iteration total. A validated cardinal fallback keeps worker
movement active while the field fills; cached directions guide subsequent steps.
Worker move timers use per-entity JSON cadences (12/10/10 ticks). Off-screen follow
is a per-worker adjacent-room queue with cancellation, including while stunned.

Only room changes/restart redraw the entire terrain. Normal frames restore the
previous four actor cells and up to three effect cells, then overlay workers, Billy
and the transient blast. Sampled three-worker normal-loop maximum is 21,020 CPU
cycles; occupied room entry is 42,195 cycles and may span multiple video frames.
These exclude ANTIC DMA and OS interrupts; they do not prove emulator frame times.

FIRE edge and direction select one collision-occluded ray; nearest-worker targeting,
knockback occupancy, stun, cooldown and visual cleanup execute on the Atari. Contact
is checked both before and after worker motion. Stun-expiry overlap permits one
player movement opportunity; entry grace applies only to the worker at a preferred
destination tile. START clears all per-worker and attack states.

The new stage-only code/state budget is $1000–$1FFF, separate from the retained
opening at $2000. Prior v0.1/v0.2 runtime sources, maps, tests, binaries and opening
assets are unchanged. All 23 v0.3 CPU tests, 16 v0.2 tests, 9 v0.1 tests, three
validators and opening validation pass. Atari800 playtesting and merging remain
pending; no stage duration or final difficulty is claimed.
