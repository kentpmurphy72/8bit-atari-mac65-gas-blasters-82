# Gas Blasters '82 — Stage 1 v0.3 Gameplay Pressure Specification

**Design date:** 2026-11-01  
**Status:** First-playable balancing proposal after user tested v0.2 in Atari800 and reported **works, but too easy and too short**.  
**Camera decision:** Keep **three non-scrolling, full-screen, linked rooms**. Their transitions were not a problem in playtesting.  
**Scope:** Historical gameplay-pressure and first gas-blast specification; its XEX was subsequently built by Codex on `feature/stage1-pressure-v0.3` and **playtested by the user**. User feedback: pressure somewhat better, **Billy slow/cumbersome, gas-blast terrible**. **Current v0.4 movement milestone** is [here](STAGE1_MOVEMENT_V04.md); v0.5 will redesign blasting. Keep this document for v0.3 regression and provenance.

## Why v0.3

The existing three-room geometry has a shortest direct route of **37 moves in dining + 40 in kitchen + 40 in storage = 117 cardinal tile moves**. With Billy's v0.2 8-NTSC-frame tile cadence that is approximately **15.6 seconds of uninterrupted movement**, excluding transition overhead. Camera style alone is not causing the shortness: the lone hazmat pursuer starts behind Billy after 3 seconds and follows rooms after 90 frames, so it creates little pressure for a player moving toward the exit.

**Design aim:** Generate meaningful evasive decisions, attacks and close calls, not artificial wait timers, locked doors, or unnecessary map expansion. Long-term 70–105 seconds was a *conceptual target* and is **not guaranteed** by simply adding enemies. Measure actual clear times and tune after user emulator tests; if still short, revisit room routes or stage objectives separately.

## 1. Reuse the working v0.2 stage

Use the already-played `feature/stage1-room-screen-v0.2` branch, in particular:
- `tools/build_stage1_v02.py`, `tools/test_stage1_v02.py`, `assets/stage1_v02/GasBlasters82_Stage1_Playable_v02.xex` and its manifest/README.
- `docs/STAGE1_ROOMMAP_SPEC_V02.md`, `assets/maps/taco_smell_stage1_v02.json` and the three canonical 40×22 `_dining.map`, `_kitchen.map`, `_storage.map` files.
- The **new v0.3 tuning data**: [`assets/gameplay/taco_smell_stage1_v03_rules.json`](../assets/gameplay/taco_smell_stage1_v03_rules.json). Its explicit numeric values are prototype defaults; code and tests should derive their constants from it where practical.

Build v0.3 on a new branch `feature/stage1-pressure-v0.3` based on the v0.2 feature branch, bringing in the current main-branch design docs. Keep all prior v0.1/v0.2 XEXs and their build scripts untouched and separately runnable. Do not merge until user tests it.

## 2. Encounters and room identity

| Room | Intended experience | Prototype enemy |
| --- | --- | --- |
| **Dining** | Teach evasion; a worker enters behind Billy but reaches him if he dithers around booths/tables | Existing `hazmat_front`, **(2,10)**, 60 frames after stage begins; **12 frames/tile** |
| **Kitchen** | More challenging: first threat ahead of Billy near his route; player must dodge or use gas blast | Additional `hazmat_kitchen`, **(29,11)**, 30 frames after first entering kitchen; **10 frames/tile** |
| **Storage** | Final pressure: another interceptor near rear escape; avoid a free sprint to X | Additional `hazmat_storage`, **(30,10)**, 30 frames after first entering storage; **10 frames/tile** |

Three **unique** worker entities maximum, not three new workers per room visit. Spawn exactly once per stage/restart and preserve each worker's active/stunned state and last position across room transitions. The chosen future-worker spawn coordinates were checked against the actual v0.2 floor plan and are **walkable**. They are distinct from Billy's entry tiles and the exit.

An enemy in another room remains alive and can follow through room doors after **45 NTSC frames (~0.75 s)** per adjacent transition instead of v0.2's 90. No teleporting across multiple rooms; no spawning duplicate copies. The v0.2 follow cancellation/backtracking contract still applies. Workers stunned by gas cannot move for the duration and are harmless to touch while stunned.

**Fairness:** If a worker would enter on Billy's destination tile, select a neighboring non-solid/unoccupied entry cell. Provide a small 15-frame transition grace *only* for a worker already occupying Billy's destination on a room load, not broad invincibility.

**Performance:** v0.2 uses **incremental BFS** (8 queue cells per observed frame). Simply tripling independent searches will likely produce enemies that barely move and eat CPU. Codex must use a bounded work scheduler/cached room distance field or another safe approach so all active enemies pursue responsively, screen updates and joystick remain responsive, and Atari800 timing is acceptable. Target cadences are game-behavior goals; real timing must be measured, not inferred from Python test execution.

## 3. Billy's first indoor gas blast

Use joystick port 1 + **FIRE with a cardinal direction**:
- Normal: hold joystick without FIRE to move Billy as in v0.2.
- With FIRE held: **no movement**; joystick direction aims the blast. Use v0.2's deterministic single-axis priority if diagonals are input.
- **Only one blast per new FIRE press** (rising edge). Holding FIRE continuously must *not* trigger repeated blasts. No-direction press has no blast.
- **Range: 3 logical tiles**, one tile wide, straight forward; the **first solid obstacle blocks it**. It hits at most the nearest worker in that ray **in the current room**, without crossing a doorway to another room.
- On hit, push worker **up to 2 walkable tiles** away from Billy, stopping at solid walls, bounds or doors; also **stun for 60 frames (~1s)**. While stunned, the worker cannot catch Billy and Billy can move through its tile. If stun ends while they still overlap, allow one player movement tick to separate before resolving contact.
- **Cooldown 72 frames (~1.2s)** per successful fired blast; no gas-pressure cost yet. If FIRE is pressed during cooldown, no shot: release and press again after cooldown.
- Show a simple **8-frame** gas-cloud effect in the aimed direction, then restore covered terrain/actors. Avoid overwriting obstacles or title/cutscene assets. A permanent gas cloud image, complex sprites and new music are **not** required.

Keep the already approved **road** gas-blast design separate. This is the first indoor control experiment, not a global gas-pressure rule.

## 4. Restart, win and preservation

- **CAUGHT:** Touching a *non-stunned* worker freezes play; START restarts the stage, player back in dining; clear all worker activations, stun/cooldown and gas-effect transient states. No final lives penalty yet.
- **STAGE COMPLETE:** Billy entering storage **X=(39,10)** ends Stage 1. No new Road 1 gameplay.
- **No layout changes:** Retain three existing 40×22 maps, four reciprocal door links, and current full-width drawing. Don't add room scrolling to Taco Smell yet.
- Preserve user-approved Title v1, Meet the Crew and Arrival, Arcade Rock/Funky Gas Attack data, START/FIRE cutscene progression and debounce behavior. Do not reenable rejected title PMG v2/v2.1.
- Defer grease slipping, customer crowd AI, score/lives, gas-pressure meter, item puzzles, locks, elaborate art and new stages.

## 5. Acceptance tests for Codex and Atari800

Run:
```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
python3 tools/validate_stage1_pressure_v03.py
```

Also execute v0.2 CPU/6502 regression tests and add v0.3 executable-level tests for: timing and unique spawns; multi-worker pursuit without frame stalls; maintaining workers on backtracking; full memory/segment safety on 64 KB; FIRE edge/release and cooldown; line-of-sight and wall stops; knockback, stun and stunned overlap; restarting all state; storage win; unchanged intro/music. Preserve v0.2 build outputs byte-for-byte.

**User playtest measurements requested:** successful clear time and time per room, catches/restarts, number of blasts needed/used, player responsiveness, enemy fairness and whether the final storage room feels climactic. If it remains a 20-second sprint, adjust AI/pathing or the room challenges before inflating map size or adding artificial timers. A challenging, fun short level is preferable to a padded 90-second level.

## 6. Handoff

See [`docs/CODEX_STAGE1_V03_HANDOFF.md`](CODEX_STAGE1_V03_HANDOFF.md) for the specific implementation order, versioned binary/source expectations and reporting format.

**Historical status:** Codex implemented the v0.3 source/XEX on `feature/stage1-pressure-v0.3`, and the user later played it successfully in Atari800. The added pressure felt somewhat better but the movement and blast were **not approved**. See the current v0.4 movement spec and subsequent planned v0.5 blast redesign. This is retained for version history and repeatable regression checks.
