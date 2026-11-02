# Gas Blasters '82 — Codex Instructions

## Current target: Stage 1 playable v0.4 (movement feel)

- **Atari target:** stock **Atari 800XL, 64 KB**, actual **6502 machine code** in a runnable XEX. Python tools are offline build/test aids, not the Atari runtime.
- **Implementation source:** `feature/stage1-pressure-v0.3` — the user has **played** v0.3 and found Billy's tile movement slow/cumbersome and its first indoor gas blast unsatisfying. Build v0.4 on **a new branch** `feature/stage1-movement-v0.4` based on v0.3, bringing the current v0.4 design files from main; do not merge without approval.
- **Read first:** [v0.4 Codex handoff](docs/CODEX_STAGE1_V04_HANDOFF.md), [movement contract](docs/STAGE1_MOVEMENT_V04.md), [numeric defaults](assets/gameplay/taco_smell_stage1_v04_movement.json), then [v0.3 pressure baseline](docs/STAGE1_GAMEPLAY_PRESSURE_V03.md), [v0.3 encounter rules](assets/gameplay/taco_smell_stage1_v03_rules.json) and [v0.2 room map](docs/STAGE1_ROOMMAP_SPEC_V02.md).
- **Movement-only v0.4:** Replace 8-frame whole-tile stepping with *visibly smooth* fixed-point sub-tile movement, immediate stick response, normalized 8-way **walking**, inset 6x6 hitbox and wall sliding. The standard solid tiles and doorway geometry remain unchanged.
- **Preserve:** Three fixed full-screen 40x22 Taco Smell rooms (two footer rows), backtracking, all four doors, three distinct v0.3 hazmat entities and chase timings, CAUGHT/restart, exit/win, the accepted Title v1 → Meet the Crew → Arrival, all artwork/music and pre-stage START/FIRE controls. Do not alter existing v0.1/v0.2/v0.3 XEXs/builders/tests, do not resurrect the retired PMG **title** v2/v2.1.
- **Temporarily disable the unsatisfying v0.3 indoor blast** for the v0.4 movement-focused executable: gameplay FIRE does nothing **and does not freeze Billy's motion**. The four-direction indoor gas-attack redesign is planned for **v0.5**; **road driving blast rules are unaffected**.
- **No scope creep:** No room scrolling in Stage 1 v0.4, new encounters, retuned AI, grease slipping, crowd AI, changed stage pacing, Road 1, new cutscenes, or finalized game art.
- **Graphics caution:** Smooth *logical* coordinates are not enough. Billy must **visibly** move between character-tile positions. A safely configured gameplay PMG or clipped software sprite is acceptable; preserve title display/DLI/POKEY behavior and validate memory use.

## Verification and handoff

- Run old `tools/validate_taco_smell_stage1.py`, `tools/validate_taco_smell_stage1_v02.py` and `tools/validate_stage1_pressure_v03.py`. Run the prior v0.3 test suite **against unchanged v0.3 artifacts**, then run new v0.4 movement/renderer/collision/door/contact tests and XEX segment/cycle checks.
- Commit versioned `tools/build_stage1_v04.py`, `tools/test_stage1_v04.py`, a separately named `assets/stage1_v04/` XEX, its source/manifest/README, on the v0.4 feature branch. Provide launch command, test results, unknowns, and anything not truly run in Atari800. **py65 is not a substitute for emulator playtesting**.
- **Other indoor stages remain open architecturally:** pharmacy and grocery may combine room-to-room and scrolling or use either independently; grocery scrolling aisle pursuit remains an idea, not a fixed camera implementation.
