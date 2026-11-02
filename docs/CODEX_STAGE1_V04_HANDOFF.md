# Codex Handoff — Gas Blasters '82 Stage 1 Playable v0.4

**User's Atari800 feedback on actual v0.3:** “It's ok. Feels a little better, but moving Billy is slow and cumbersome and the gas blast mechanics were terrible.”

## Branch / sources

1. **Use `feature/stage1-pressure-v0.3` as the executable code baseline** (the user actually played it); it contains `assets/stage1_v03/GasBlasters82_Stage1_Playable_v03.xex`, `tools/build_stage1_v03.py`, `tools/test_stage1_v03.py` and profiler outputs. Do **not** begin from main's uncompiled assets alone.
2. Create **`feature/stage1-movement-v0.4`** from the v0.3 feature branch, and bring this v0.4 documentation and tuning JSON from main into it. Preserve all older assets/builds and `feature/stage1-pressure-v0.3` untouched; no merge until the user's emulator test.
3. Read **[`docs/STAGE1_MOVEMENT_V04.md`](STAGE1_MOVEMENT_V04.md)**, **[`assets/gameplay/taco_smell_stage1_v04_movement.json`](../assets/gameplay/taco_smell_stage1_v04_movement.json)**, [v0.3 combat/AI rules](../assets/gameplay/taco_smell_stage1_v03_rules.json), and [three-room map contract](STAGE1_ROOMMAP_SPEC_V02.md). Prior v0.3 blast behavior is historical—v0.4 explicitly turns it off pending v0.5 redesign.

## Implement exactly this focused milestone

- Replace Billy's **8-observed-frame / whole-tile movement** with continuous, immediately responsive **fixed-point sub-tile motion**: 1.5 logical px/frame cardinal; normalized diagonal 1.0625 px per axis/frame; 8-direction walking, no acceleration; v0.4 movement must be visibly smooth, not just change an internal fractional coordinate while leaving a character-glyph "snap" on screen.
- Implement the inset 6×6 AABB against the **existing** solid tiles, per-axis movement resolution and blocked-axis wall sliding. Prevent corner cutting, out-of-bounds movement and status-row trespass.
- Maintain existing three full-screen 40×22 maps, two status rows, all four reciprocal door links, door-trigger center crossing, entry position alignment and backtracking, original win/CAUGHT.
- Preserve the **v0.3 three-worker AI and encounter timing**, make player-vs-hazmat contact pixel-aware, and preserve stun/contact-grace/follow state. Do not retune enemies or add more.
- **Disable gameplay blasts only in v0.4**; FIRE does not fire and does not lock walking. Keep working Title/Meet Crew/Arrival FIRE/START behavior, artwork and both original POKEY tunes unchanged. Do not overwrite prior v0.3 binary/source; gas-control redesign is **Stage 1 v0.5**.
- Pick a credible Atari display method for visibly smooth movement (e.g., safe **in-game** PMG sprite for Billy or clipped software sprite with proper restoration). PMG title v2 was retired and must remain retired. Document actual 8x8 logical-pixel → on-screen mapping, RAM addresses and DLI/PMG decisions.
- Keep it native **6502**, playable in a **64 KB Atari 800XL**. Reuse/test the existing shared reverse BFS with no additional frame stalls. Avoid painting the entire map per pixel tick.

## Build/test expectations

- Create separate `tools/build_stage1_v04.py`, `tools/test_stage1_v04.py`, and `assets/stage1_v04/GasBlasters82_Stage1_Playable_v04.xex`, plus source, manifest and README with emulator commands; preserve all existing versioned XEXs.
- Run `python3 tools/validate_taco_smell_stage1.py`, `python3 tools/validate_taco_smell_stage1_v02.py`, `python3 tools/validate_stage1_pressure_v03.py`. Add new v0.4 movement tests (fixed-point speed/reverse, wall slide, diagonal/blocked corners, renderer motion, contact, doors, states, memory/timing).
- Run prior v0.3 tests against **the unchanged v0.3 build**. Do not change old tests just to make a v0.4 change pass.
- If real Atari800 visual/audio verification is unavailable, say so plainly; CPU simulation is *not* a substitute. Log frame-time/cycle samples and save a repeatable test scenario.
- Hand off the branch/commit, runnable XEX filename, exact build and launch commands, tests passed/failed, graphics compromises and any known issues. Do not merge into main until user playtests.

**Acceptance:** Billy visibly moves within 8x8 tiles, turns instantly, avoids snags on furniture, slides along walls, supports fair diagonals, crosses doors correctly and can still finish Stage 1. The purpose is **fun-to-control movement** rather than a final gas combat or game-balance implementation.
