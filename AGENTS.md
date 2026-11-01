# Gas Blasters '82 — Codex Instructions

## Current Stage 1 v0.2 task

- Target a stock **Atari 800XL, 64 KB**, native **6502 machine code** and a runnable Atari XEX. Python tooling is **offline only**, not Atari runtime.
- Read [the Codex Stage 1 v0.2 handoff](docs/CODEX_STAGE1_V02_HANDOFF.md), [the room-map contract](docs/STAGE1_ROOMMAP_SPEC_V02.md), and the canonical three room-map files with [JSON metadata](assets/maps/taco_smell_stage1_v02.json).
- **Start from the user-played v0.1 implementation** on branch `feature/stage1-playable-v0.1`. Create `feature/stage1-room-screen-v0.2` from it, then bring v0.2 design files from `main`. Do not merge without user approval.
- Preserve v0.1 XEX, map, builder/tests and the approved `assets/opening/GasBlasters82_OpeningSequence_v1.xex`. The old scrolling v0.1 map is **historical** for v0.2. Do not use rejected PMG title v2 or v2.1.

## Implementation scope and quality gates

- Replace Stage 1 scrolling with three **40×22** fixed-screen maps (dining, kitchen, storage) using the full 40-column gameplay width and two footer/status rows.
- Implement linked door transitions in both directions, 1-tile-inside destination spawn, original movement and collision, **one** hazmat pursuer that follows across rooms without respawning/duplicating, CAUGHT/restart and X exit completion.
- Do not add gas attack, grease physics, new enemies, final art, extra gameplay stages, changes to title/intro/music, or a finalized lives system.
- Run `python3 tools/validate_taco_smell_stage1.py` and `python3 tools/validate_taco_smell_stage1_v02.py`, then add/run real 6502 tests for movement, room transitions (both directions), enemy continuity, debounce and XEX memory safety.
- Commit new v0.2 source/build/XEX **on the feature branch only**. Clearly distinguish automated test results from genuine Atari800 visual/audio testing; include the exact `atari800 -xl -nobasic -run ./YOUR_FILE.xex` command and build instructions.
- Stage 1's room-to-room design **does not apply to pharmacy or grocery**: scrolling remains an option for those stages, including the grocery aisle pursuit concept.
