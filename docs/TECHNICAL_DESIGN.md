# Gas Blasters '82 — Technical Design (Incremental)

**Date:** 2026-11-01  
**Status:** Partial Stage 1 v0.2 technical plan; **not** complete architecture for the whole game.

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

## Memory and runtime checks required of Codex

v0.1 uses buffers/data in the high RAM area (starting around `$A000`) and a 6502 extension. Three new maps cannot simply be appended without checking the Atari 64 KB memory map. Derive actual safe allocation from the v0.1 branch's `tools/build_stage1.py` and `assets/stage1/manifest.json`. Validate every XEX segment for overlap and avoid overwriting the working title/cutscene memory, video screen, character set, OS-reserved regions, and music buffers. Preserve the active display-list/DLI behavior.

Run both map validators, CPU/runtime tests of four doors, y-preserving spawn, transitions without auto-reentry, solid collision, unique hazmat, safe row lookup and stage completion. Then the user must test the v0.2 XEX in Atari800; simulation is not a substitute for that emulator check.

## Other stages

The room-to-room design is **specific to Taco Smell Stage 1**. Pharmacy scrolling is an available design option; a scrolling grocery aisle chase with police, hazmat workers and townspeople is the intended direction but not yet technically specified. Driving road stages still use the separate overhead-scrolling driving/HUD design. All game-wide technical decisions remain open (final graphics modes, PMG for moving sprites, global memory map and frame timing, game distribution, lives, score and other levels).
