# Gas Blasters '82 — Technical Design (Incremental)

**Date:** 2026-11-01  
**Status:** Partial Stage 1 v0.2–v0.5 engine/encounter/movement/blast plans; **not** a complete game-wide technical architecture.

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

## Stage 1 v0.3 pressure extension (implemented on feature branch; playtested with issues)

- Following the user's successful v0.2 test, Codex built and the user played **v0.3** on `feature/stage1-pressure-v0.3`. The three fixed 40×22 rooms remain. The user reports pressure is somewhat better, but player movement remains slow/cumbersome and the blast unsatisfying. This section records the v0.3 baseline, not an upcoming task.
- Add three persistent enemy IDs across the restaurant: dining (2,10) at 60 frames, kitchen (29,11) at +30 frames from entry, storage (30,10) at +30 frames from entry. Movement cadence targets 12/10/10 frames and follow delay 45 frames; all are **tuning defaults**, not verified Atari800 behavior.
- One direction-aimed blast on each **new FIRE press**, block movement while FIRE held, ray up to three tiles blocked by solid terrain, knockback up to two cells, stun 60 frames, cooldown 72 frames and short visual effect. Stunned enemy cannot catch Billy. Follow the [v0.3 gameplay contract](STAGE1_GAMEPLAY_PRESSURE_V03.md) and its [machine-readable rules](../assets/gameplay/taco_smell_stage1_v03_rules.json).
- **6502 performance warning:** v0.2 runs one incremental BFS at eight nodes per observed frame. Three independent BFS workers may exceed available processing or make pursuit unresponsive. Codex should implement a bounded multi-enemy scheduling/cached-distance strategy, preserve room-follow identity, and instrument input responsiveness and visual behavior.
- Preserve all v0.2/v0.3 versioned binaries, builders and test fixtures unchanged. v0.3 already supplies its own `tools/build_stage1_v03.py`, `tools/test_stage1_v03.py`, `assets/stage1_v03/`, manifest and CPU-only profile. The user's playtest confirms v0.3 runs but **not** that its control feel is approved. The old timing numbers remain historical defaults.

## Stage 1 v0.4 movement-control prototype (implemented and user-playtested)

- **Active spec:** [v0.4 movement contract](STAGE1_MOVEMENT_V04.md), [tuning data](../assets/gameplay/taco_smell_stage1_v04_movement.json), and [Codex handoff](CODEX_STAGE1_V04_HANDOFF.md).
- **Source branch:** Codex built `feature/stage1-movement-v0.4` from the v0.3 baseline, with `tools/build_stage1_v04.py`, `tools/test_stage1_v04.py` and `assets/stage1_v04/`. **The user played the v0.4 XEX and reports Billy moves smoothly and diagonal walking works well.** Preserve the v0.4 XEX, source, Q4 movement and GTIA sprite code unchanged for regression.
- **Problem:** The old movement is one full **8×8 tile every 8 NTSC frames**, and the existing renderer snaps Billy to character-cell positions. User finds this awkward and sluggish.
- **Movement target:** Keep three 40×22 fixed-screen maps, but represent Billy with **4-bit fractional logical-pixel precision per axis** (1/16-pixel units; use 16-bit coordinate components). Cardinal **24/16 = 1.5 px/frame**; diagonal **17/16 px/frame per axis**, for normalized 8-way joystick walking. Poll at each observed video tick, not every eighth; stop/reverse immediately.
- **Sprite rendering:** Implemented using **gameplay GTIA Player 0**, single-line PMG **PMBASE=$B8**, player plane **$BC00–$BCFF**; logical 8×8 sprite footprint, 2px horizontal PMG steps, 1px vertical steps. User confirms overall control feel, not necessarily final graphics. Do **not** modify the retired PMG *title* art.
- **Hitboxes:** 8×8 visible sprite, **6×6 inset collision** rectangle. Resolve X and Y per-axis with swept/substeps to avoid wall tunneling; if one axis is obstructed, slide along the other at full cardinal speed. Enemy tiles remain at existing integer grid positions, but collision against Billy becomes overlapping AABBs rather than exact tile equality. Keep stun/contact grace.
- **Door triggers:** Billy's hitbox **center** enters D/X; after a room swap align Billy with x=1 or x=38 destination tile (8px/integer alignment), preserving doorway row (10/11). Do not bounce repeatedly on held input. Keep all room/enemy states.
- **FIRE:** v0.4 gameplay intentionally ignores FIRE; pre-game intro FIRE is unchanged. v0.5 specifically reinstates and redesigns four-direction indoor blasting without regressing movement.
- **Performance:** Need true video-cadenced movement even while the shared BFS/three-worker logic runs, without full-screen redraw per frame. 6502 cycle and memory-segment checks mandatory; py65 measurement is not a stand-in for user Atari800 playtesting.

## Stage 1 v0.5 gas-blast extension (proposed; XEX pending)

**Authority:** [v0.5 blast gameplay specification](STAGE1_BLAST_V05.md), [machine-readable tuning](../assets/gameplay/taco_smell_stage1_v05_blast.json), [Codex handoff](CODEX_STAGE1_V05_HANDOFF.md).

- **Actual baseline:** User-tested v0.4 branch `feature/stage1-movement-v0.4`; new branch `feature/stage1-blast-v0.5`. Keep the Q4 16-bit player coordinates, 1.5px/frame cardinal movement, normalized diagonals, wall sliding and inset 6×6 player hitbox. Preserve three v0.3 workers and their BFS scheduling.
- **Input state machine:** Gameplay-only `WALK → AIM/WINDUP → BLAST/CLOUD → RECOVERY`, with `FIRE` held switching to aiming and suppressing walking. Independently read joystick each observed frame, allow FIRE-first aiming, require **4 stable cardinal aim ticks**, one shot per press, release-to-rearm. Diagonal input is never a new blast aim; release early cancels without cost. Cooldown and resource checks must **not queue delayed phantom shots**.
- **Funny pose:** Billy remains GTIA **Player 0** for gameplay. Adjust frame/pose and, if safe, leverage a second in-game PMG plane for a **visible jeans-clad backside protrusion in the selected blast direction**. Must not reconfigure Title v1, DLI/PMG during cutscenes, or corrupt the fixed 40-column room display.
- **Cloud rendering:** Three 6-frame waves within a maximum **3-cell-deep, 7-cell cone**, using an ephemeral overlay separate from terrain and workers; clip by solids `# B T C R K S`, room bounds and D/X. No permanent edits to the authoritative room maps or overwritten worker/PMG art. Restore all affected background glyphs after every wave. Avoid full-screen redraw per wave.
- **Collision and combat:** Affected workers in same room once per burst; animate up to **three 8px knockback moves** (one per three video frames), stop before furniture/other workers/D/X. Apply **75-frame stun** to target and **24-frame stagger** to a worker blocking knockback, with a brief impact animation. Respect existing stunned-contact grace and global persistent worker IDs.
- **Meter and pacing:** The prototype contains **three rechargeable indoor GAS charges**, one consumed per discharge, refill one every **120 NTSC frames**, **20-frame cooldown** from discharge and **8-frame recovery** from discharge. Display GAS 0–3/3 and status within the existing **two footer rows**. This is **not** the Stage 2 road gas-pressure system.
- **POKEY:** Short original in-game whoosh (~10 ticks); start/stop stage-only registers safely. Approved Arcade Rock and Funky Gas Attack source and playback state stay byte-identical.
- **CPU/memory:** v0.4's manifest already allocates PMG **$B800–$BFFF** and player code in lower RAM, with three-worker BFS and maps elsewhere. Codex must audit *all* new frame, status, sprite/cloud overlay and sound allocations against the actual v0.4 manifest; avoid modifying shared OS/display-list or enemy queue memory. Do not claim cycle safe based only on 6502 simulation.
- **Validation:** Keep unchanged v0.4 movement tests and previous validators; add `tools/validate_stage1_blast_v05.py` and true v0.5 CPU tests for all four aims, input edge ordering, animation waves/occlusion, hit-once, knockback and collisions, resource refill, restart, 16-bit frame wrap, music regression and room-state continuity. The user must evaluate the actual XEX in Atari800 for comedy/impact/smoothness.

## Memory and runtime checks required of Codex

v0.1 uses buffers/data in the high RAM area (starting around `$A000`) and a 6502 extension. Three new maps cannot simply be appended without checking the Atari 64 KB memory map. Derive actual safe allocation from the v0.1 branch's `tools/build_stage1.py` and `assets/stage1/manifest.json`. Validate every XEX segment for overlap and avoid overwriting the working title/cutscene memory, video screen, character set, OS-reserved regions, and music buffers. Preserve the active display-list/DLI behavior.

Run both map validators, CPU/runtime tests of four doors, y-preserving spawn, transitions without auto-reentry, solid collision, unique hazmat, safe row lookup and stage completion. The user has already played v0.2 and v0.3 in Atari800. New versions still require their own actual Atari800 playtests; CPU simulation alone cannot establish visual motion, music or controller feel.

## Other stages

The **fixed-screen, non-scrolling** room behavior is specific to **Taco Smell Stage 1 v0.2**, not a restriction on room transitions elsewhere. Later indoor stages—including pharmacy and grocery—may use **room-to-room transitions, camera scrolling inside an area, or a hybrid of both**. A grocery aisle pursuit with police, hazmat workers and townspeople could scroll and then switch sections via a room transition; this remains a design possibility, not a completed technical specification. Driving road stages still use the separate overhead-scrolling driving/HUD design. All game-wide technical decisions remain open (final graphics modes, PMG for moving sprites, global memory map and frame timing, game distribution, lives, score and other levels).
