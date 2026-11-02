# Gas Blasters '82 — Codex Instructions

## Current implementation: Stage 1 playable v0.3

- Target stock **Atari 800XL, 64 KB**, actual **6502 machine code** and runnable XEX. Python is offline build/test tooling, never Atari runtime.
- Read [Codex v0.3 handoff](docs/CODEX_STAGE1_V03_HANDOFF.md), [gameplay-pressure spec](docs/STAGE1_GAMEPLAY_PRESSURE_V03.md), [JSON tuning rules](assets/gameplay/taco_smell_stage1_v03_rules.json), and the existing [room map spec](docs/STAGE1_ROOMMAP_SPEC_V02.md) before coding.
- **Start from the user-playtested v0.2** on `feature/stage1-room-screen-v0.2`, create **`feature/stage1-pressure-v0.3`**, and bring current v0.3 design files from main. Keep the v0.1 and v0.2 XEXs/builders/tests and the original opening sequence unchanged. Do **not** merge to main without user approval.
- Preserve Title v1 → Meet the Crew → Arriving at Taco Smell, original artwork, text, Arcade Rock/Funky Gas Attack POKEY music and controls. Rejected PMG title experiments v2/v2.1 remain retired.

## Scope

- **Keep the three non-scrolling 40×22 fixed rooms**, two status rows, all doorway/backtrack transitions, collision rules, CAUGHT restart and X exit.
- Add **three persistent hazmat entities total**: existing front worker, new kitchen interceptor and storage blocker; quicker activity and room following. Avoid duplicate spawns and improve search scheduling to maintain responsiveness on the 6502.
- Add **FIRE + cardinal direction indoor gas blast**, one per FIRE press, 3-tile line of sight, 2-tile maximum knockback, 60-frame stun and 72-frame cooldown; movement pauses with FIRE held. Use simple temporary graphics. See JSON/spec for details.
- Do **not** add scrolling, grease slipping, new rooms, crowd AI, arbitrary time gates, gas-pressure rules, final graphics, scoring/lives, road gameplay or other features.

## Validation and handoff

- Run both prior map validators plus `python3 tools/validate_stage1_pressure_v03.py`. Preserve prior 6502 test coverage and add multiple-worker/blast/performance/memory-safety tests.
- Commit versioned new source/build/XEX to **v0.3 feature branch only**; document testing and supply Atari800 launch instructions. **CPU unit tests do not equal full Atari800 playtesting.**
- The **Taco Smell camera choice applies to Stage 1**, not every interior. Pharmacy and grocery can use room-to-room, scrolling within rooms, or a hybrid; a grocery aisle pursuit is an option.
