# Codex Handoff — Gas Blasters '82 Stage 1 v0.2

**Intent:** Upgrade the already-playable Stage 1 v0.1 (feature branch `feature/stage1-playable-v0.1`) from horizontal scrolling to three full-screen restaurant rooms, preserving the accepted opening sequence and the v0.1 build as a fallback.

## Source-of-truth reading order

1. [Stage 1 v0.2 room-map contract](STAGE1_ROOMMAP_SPEC_V02.md)
2. `assets/maps/taco_smell_stage1_v02.json` plus the **three** `_dining.map`, `_kitchen.map`, `_storage.map` files
3. `tools/validate_taco_smell_stage1_v02.py`
4. `assets/stage1/README.md`, `tools/build_stage1.py`, and `tools/test_stage1.py` on **`feature/stage1-playable-v0.1`** (these are not yet on `main`)
5. The known-good title/intro source in `assets/opening/`, including `tools/build_opening_sequence.py`

**Branching:** Create `feature/stage1-room-screen-v0.2` based on the existing playable v0.1 branch. Bring in the v0.2 design/maps/tools docs from current `main` (merge/rebase/cherry-pick carefully). Do not overwrite v0.1 files or alter `main` unless the user authorizes a merge.

## Requested implementation

- Output **one 64 KB Atari 800XL-compatible 6502 XEX** (a new name such as `GasBlasters82_Stage1_Playable_v02.xex`) with Title → Meet the Crew → Arrival → *playable* restaurant Stage 1.
- Keep the existing 40-column ANTIC-style renderer as a starting point, but **eliminate camera scrolling**. Each of three 40×22 terrain maps fills the width, with two status lines at the bottom.
- Implement exact two-high `D` links and inward spawn tiles from the v0.2 JSON. Preserve y on room transitions. Allow entering previous rooms.
- Preserve collision rules and joystick movement, adapting map width from 48→40 and map count 1→3 everywhere (rendering, search, row tables, lookup, memory).
- Preserve **one** initial pursuer, caught/restart and finish states. Have that pursuer continue between rooms with the v0.2 delayed-follow rules; no magic resets or duplicates.
- Add tests for every forward/backward door, enter-after-exit debouncing, map bounds, per-room render, valid sprites and enemy follow, and memory-segment non-overlap.
- Keep Arcade Rock on Title, Funky Gas Attack across cutscenes, working START/FIRE, and the original title bitmap; **do not re-enable retired PMG title v2/v2.1**.
- Do **not** add gas attacks, grease sliding, multiple pursuers, scoring, new cutscenes or road gameplay yet.
- Create reproducible build instructions and a run command like `atari800 -xl -nobasic -run ./GasBlasters82_Stage1_Playable_v02.xex`; distinguish automated tests from a real Atari800 run.

## Acceptance / handoff

After running both map validators and 6502 tests, commit the new source and XEX on the **feature branch**, provide the specific binary and source paths, and summarize any emulator tests not performed. Do not merge into main until the user approves the actual emulator gameplay.

