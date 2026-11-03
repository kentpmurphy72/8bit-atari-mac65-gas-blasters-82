> **HISTORICAL ARCHIVE.** Superseded by the [current accepted Stage 1 design](../../STAGE1_DESIGN.md). Old proposals may mention deleted branches, superseded controls or old test states.

# Codex Handoff — Stage 1 Playable v0.3 (Gameplay Pressure)

**User's Atari800 feedback:** Stage 1 v0.2 **works**, but the restaurant escape is **too easy and too short**; room transitions themselves are fine. Retain the **three non-scrolling rooms**.

## Starting point / branching

1. Use **`feature/stage1-room-screen-v0.2`** as the code baseline — NOT `main`. It contains the working, user-playtested `tools/build_stage1_v02.py`, `tools/test_stage1_v02.py`, `assets/stage1_v02/`, and all three maps.
2. Create **`feature/stage1-pressure-v0.3`** from v0.2. Bring the v0.3 design files from `main` without overwriting the older generated binaries or source.
3. Read [v0.3 game-pressure spec](STAGE1_GAMEPLAY_PRESSURE_V03.md) and `assets/gameplay/taco_smell_stage1_v03_rules.json` **first**. Retain the [v0.2 room geometry](STAGE1_ROOMMAP_SPEC_V02.md).
4. Implement in this order: (a) more responsive pursuit and room transitions; (b) add new kitchen/storage workers with unique persistent IDs; (c) add FIRE+direction gas blast, stun/knockback and effect; (d) new tests/build; (e) performance profiling and tuning.

## Required gameplay

- Three fixed 40×22 maps: dining → kitchen → storage; all four forward/reverse door transitions, working collision and storage win preserved.
- Hazmat workers: dining at (2,10) activates after 60 NTSC frames, kitchen at (29,11) 30 frames after first kitchen entry, storage at (30,10) 30 frames after first storage entry. Active maximum three; same entity persists on revisiting rooms. Door follow delay becomes 45 frames. Respect per-worker movement cadence in JSON. No duplicates, no magically teleporting.
- Billy gas blast: hold **FIRE** and choose a cardinal joystick direction (**movement disabled while Fire held**). One blast per new Fire press; three-tile line blocked by solids; closest worker in current room gets up to two-tile knockback and 60-frame stun. Cooldown 72 frames. Display a temporary 8-frame gas visual. No indoor pressure-meter effect.
- Stunned workers cannot catch Billy, including temporary tile overlap. Gas blasts must not push workers through solids or door triggers. All result/restart states still function.
- **Do not add** grease sliding, customer AI, fourth rooms, scroll camera, arbitrary time limits, key/item puzzles, title changes, new music, road gameplay, or a permanent lives system.

## Performance / build

- Use actual 6502 code, stock 64 KB Atari 800XL compatible. v0.2 already uses incremental BFS in its main loop; **3 actors must not cause search work to block gameplay**. Budget BFS and movement per VBI frame. Reuse/cache search results or restructure search if needed; show implementation and measured cadence.
- New versioned output such as `assets/stage1_v03/GasBlasters82_Stage1_Playable_v03.xex`, with reproducible `tools/build_stage1_v03.py`, `tools/test_stage1_v03.py`, and README + manifest; never overwrite v0.2.
- Run the old v0.1 and v0.2 map validators plus **`python3 tools/validate_stage1_pressure_v03.py`**. Run previous CPU tests and add true 6502 tests for all new mechanics, frame-clock wraparound, multiple workers, blast occlusion, stun, cooldown and memory segment non-overlap.
- Preserve the known-good title/cutscene visual and music bytes, START/FIRE pre-game controls, and the scene progression that already worked in Atari800.

## Handoff to user

Provide the binary's exact path and launcher, e.g.:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1_v03/GasBlasters82_Stage1_Playable_v03.xex
```

Specify the feature branch and commit, build/test results, and tests **not performed on Atari800**. Do not merge into `main` until the user has playtested.

**Game-feel evaluation:** Ask the user to report total clear time, catches/restarts, blast use and which room feels least challenging. 70–105 seconds remains an **aspirational playtest target**, not a mandate to pad gameplay with delays. Escalating danger and fun come first.
