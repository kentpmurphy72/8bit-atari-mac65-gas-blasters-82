> **HISTORICAL ARCHIVE.** Superseded by the [current accepted Stage 1 design](../../STAGE1_DESIGN.md). The original proposal/handoff may mention deleted feature branches, unbuilt XEXs or outdated acceptance status.

# Codex Handoff — Gas Blasters '82 Stage 1 v0.5 (Gas Blast)

**User Atari800 results:** v0.3 indoor gas-blast mechanics were terrible. **v0.4 player movement works well**: Billy is smooth, responsive, and eight-direction walking/diagonals feel good. **Do not regress movement.**

## Branch and baseline

1. Begin from **`feature/stage1-movement-v0.4`**, the **user-playtested working implementation**, *not* main's design-only data. Create **`feature/stage1-blast-v0.5`** from v0.4. Bring current design files from main into the feature branch carefully.
2. Read [the v0.5 gameplay specification](STAGE1_BLAST_V05.md), [v0.5 numeric JSON](../../../assets/gameplay/taco_smell_stage1_v05_blast.json), [v0.4 movement spec](STAGE1_MOVEMENT_V04.md) and [v0.2 three-room spec](STAGE1_ROOMMAP_SPEC_V02.md).
3. Inspect `tools/build_stage1_v04.py`, `tools/test_stage1_v04.py`, `assets/stage1_v04/README.md`, and `assets/stage1_v04/manifest.json` **on the v0.4 branch**. v0.4 uses a Q4 fixed-point player, single-line **GTIA Player 0** Billy sprite at `$BC00–$BCFF`, PMBASE `$B8`; it retains the v0.3 6502 core/AI. Do not overwrite or regenerate older release artifacts in-place.
4. The old v0.3 first blast routine exists in the core, but v0.4 intentionally bypasses it. **Replace its unsatisfying control/visual/combat behavior rather than simply restoring v0.3's three-tile ray.**

## Required playable v0.5 functionality

- **FIRE held = stop movement + aim** with joystick in **eight directions**: Up, Up-Right, Right, Down-Right, Down, Down-Left, Left and Up-Left. Any of the eight aims stable for four observed video ticks discharges one burst. This must work when FIRE is pressed **before** the joystick points a direction. A changed aim restarts the wind-up. No direction does not fire; **diagonal input is a valid independent direction**, never coerced to a cardinal aim. Release before discharge cancels with no cost. **Exactly one burst per FIRE hold**; release to rearm. Walk as soon as released and the eight-frame post-shot recovery has expired.
- **Billy turns his jeans-clad backside toward the target** and briefly poses during wind-up. Use visible Stage-1-only gameplay PMG pose/overlay frames; the gag must be recognizable despite Atari's coarse sprite resolution. Do not touch retired title PMG experiments.
- **Eight-direction expanding gas cloud**, three six-frame waves, growing from a 1-tile puff to a max 7-tile, 3-step cone (one-tile lateral flank width by depths 2/3); implement vector formula and **diagonal supercover/corner-safe occlusion** from the v0.5 spec/JSON, with no cloud across D/X or off-map. Temporary cloud layers must restore terrain and all actor sprite layers without leaving ghosts.
- **Impact:** Each enemy reached can be affected once per burst; several enemies can be hit in the same cloud. **Animate** up to three tile steps of knockback in any chosen cardinal/diagonal attack direction, one step every three frames; diagonal steps require target and **both orthogonal corner cells** clear; stop before solids/D/X/occupied workers. Collision with furniture shows 4-frame BONK impact and 75-frame stun; hitting another worker stops and staggers that other worker 24 frames (no chain push in v0.5). Preserve stun/collision grace and avoid duplicate enemies.
- **Resource + feedback:** 3 renewable charges, one spent for each actual discharge, one recharges every 120 NTSC frames, 20-frame cooldown from discharge, 8-frame movement recovery, existing bottom status rows display GAS 0–3/3 and READY/COOLING/EMPTY.
- **Sound:** Short original POKEY (~10-frame) airy gas whoosh, strictly during Stage 1; approved Arcade Rock title and Funky Gas Attack cutscenes must remain unchanged.
- **Do not change** v0.4 cardinal/diagonal movement speed/precision/wall slide/inset hitboxes; 40×22 room layouts, four reciprocal doorways, win/CAUGHT/restart, three v0.3 hazmat entities and AI timings, accepted title/cutscenes/music.
- **Do not add** Road 1, camera scrolling, new NPCs, grease slide, score/lives, a permanent gas-pressure meter or polished graphics outside the specific blast pose/cloud.

## Build, test, and report

- New output **`assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex`**, plus reproducible **`tools/build_stage1_v05.py`**, **`tools/test_stage1_v05.py`**, 6502 source listings, manifest, README and (where practical) a timing profile. Make no unapproved merge to main.
- Run all map and v0.3 validators plus **`python3 tools/validate_stage1_blast_v05.py`**. Run the existing **unchanged** v0.4 movement tests against its original binary. Add CPU/emulator-facing tests for **all eight joystick aim vectors (including FIRE-then-diagonal), distinct cardinal/diagonal cone geometry, blocked diagonal corners, eight pose orientations, diagonal knockback and collisions**, input state edges, direction changes, release/rearm, cooldown+charges, multi-wave rendering and occlusion, stun, sprite timing, enemy AI continuity, 6502 frame wrap, memory integrity and title/music regression.
- Measure at least a representative frame with **three active workers + expanding cloud + Billy PMG movement**, using py65/profiler; avoid frame stalls or whole-screen redraw every cloud frame.
- Explicitly distinguish **automated 6502 CPU tests** from actual **Atari800 visual and audio tests**. If Codex cannot run Atari800, tell the user what remains to be checked.
- Hand off branch name, commit, exact XEX path, reproducible build steps, testing summary and launch line:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex
```

**Desired outcome:** Billy still feels as smooth as v0.4, but the gas attack now looks funny and **feels powerful**, clearly knocks hazards away and is easy to trigger with one joystick. The actual fun factor can only be decided after user playtesting.
