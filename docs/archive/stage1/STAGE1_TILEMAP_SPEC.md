> **HISTORICAL ARCHIVE.** Superseded by the [current accepted Stage 1 design](../../STAGE1_DESIGN.md). Old proposals may mention deleted branches, superseded controls or old test states.

# Gas Blasters '82 — Stage 1 Tile-Map Contract v0.1

> **Legacy scrolling v0.1 contract.** Retained for the user-played prototype and regression tests. **For Stage 1 v0.2, use [three fixed-room maps](STAGE1_ROOMMAP_SPEC_V02.md) and the [Codex v0.2 handoff](CODEX_STAGE1_V02_HANDOFF.md).** Do not use the v0.1 48×22 scrolling layout as the authoritative v0.2 plan.

**Status:** Proposed implementation-ready prototype layout; not yet approved by gameplay testing.  
**Date:** 2026-11-01  
**Target:** Atari 800XL, 6502 assembly, MAC/65-friendly data.  
**Scope:** Floor plan / collision / actors / win trigger. NOT a playable XEX.

## 1. Purpose and boundaries

Define the **Taco Smell restaurant escape** using one continuous, believable fast-food footprint: dining room -> kitchen -> storage/rear exit. The game progresses through escalating hazmat pressure, **not** by exploring an unrealistically enormous restaurant or hunting for keys. This is the *indoor overhead prototype layout*, not a commitment that every indoor stage must be top-down. No change to the user-tested **Title v1 -> Meet the Crew -> Arriving at Taco Smell** intro or its music is authorized by this specification.

This is the single source of truth for the first level layout:

- [`assets/maps/taco_smell_stage1_v01.map`](../../../assets/maps/taco_smell_stage1_v01.map) — raw 48 x 22 ASCII terrain; no row numbers/headers, exactly 22 newline-terminated 48-character rows.
- [`assets/maps/taco_smell_stage1_v01.json`](../../../assets/maps/taco_smell_stage1_v01.json) — tile semantics, entities, room boundaries, passages, camera proposal, and prototype rules; no duplicated map rows.
- [`assets/maps/taco_smell_stage1_v01_preview.svg`](../../../assets/maps/taco_smell_stage1_v01_preview.svg) — human visualization only; **not an Atari bitmap**.
- [`tools/validate_taco_smell_stage1.py`](../../../tools/validate_taco_smell_stage1.py) — executable constraints/route validation (Python standard library).

The ASCII map and JSON are normative. The diagram is non-normative. If these disagree, update the files and validator intentionally; never silently hand-adjust the image.

## 2. Coordinate system, geometry, and zones

- Integer grid; origin **(x=0,y=0)** at top left; +x right, +y down.
- Exactly **48 columns (x=0..47)** by **22 rows (y=0..21)** = **1,056 terrain cells**.
- Prototype logical tile footprint **8 x 8 pixels** (384 x 176 logical pixels), subject to rendering/character-set decisions. **Do not** confuse the 48-wide world with 40-column Atari viewport.
- Dining zone x=0..17 (18 columns); kitchen x=18..33 (16); storage x=34..47 (14). Zone x ranges include exterior/partition cells, which may not be traversable.
- Perimeter wall is solid except left **front entrance F=(0,10)**, north **kitchen side entrance N=(27,0)**, and right **rear exit X=(47,10)**. Actors cannot leave map bounds even through F or N.
- Dining -> kitchen counter passage: **D=(17,12)** and **D=(17,13)**, two tiles high. All other x=17 cells are solid.
- Kitchen -> storage passage: **D=(33,9)** and **D=(33,10)**, two tiles high. All other x=33 cells are solid.
- Passage geometry is intentionally simple; no locked doors, key fetches, or maze puzzles in v0.1.

## 3. Exact tile map (row label is not part of data)

Columns x=00..47; each line below has exactly 48 tile characters **after** the two-digit row index and two spaces. Canonical, unlabeled rows are in the `.map` file.

```text
00  ###########################N####################
01  #................#...............#.............#
02  #.BBB.........RR.#..KKKKKKK......#..SSS...SSS..#
03  #.BBB..TT.....RR.#..KKKKKKK......#..SSS...SSS..#
04  #.BBB..TT........C...............#..SSS...SSS..#
05  #..........TT....C...............#..SSS........#
06  #..........TT....C..KKK..........#.............#
07  #................C..KKK..........#.............#
08  #................C...............#.............#
09  #.....TT.........C...GG..........D.............#
10  F.....TT.........C...........G...D.............X
11  #................#.....KKKK......#......SS.....#
12  #..TT............D.....KKKK.G....#......SS.....#
13  #..TT............D...............#..SS.........#
14  #................#...........KKK.#..SS.........#
15  #.........TT.....#...........KKK.#..SS...SSS...#
16  #.........TT.....#...........KKK.#..SS...SSS...#
17  #.BBB............#..KKKK....G....#..SS...SSS.S.#
18  #.BBB............#..KKKK.........#.......SSS.S.#
19  #.BBB............#...............#.............#
20  #................#...............#.............#
21  ################################################
```

## 4. Terrain legend and collisions

| Tile | Meaning | Blocks Billy/enemies? | v0.1 behavior |
|---|---|---|---|
| `#` | Building wall/partition | Yes | Cannot traverse |
| `.` | Walkable floor | No | Normal ground |
| `B` | Dining booth | Yes | Fixed obstacle |
| `T` | Dining table | Yes | Fixed obstacle |
| `C` | Service counter | Yes | Fixed obstacle, with two-tile passage |
| `R` | Drink station | Yes | Fixed obstacle |
| `K` | Kitchen equipment | Yes | Fixed obstacle |
| `S` | Storage shelves/boxes | Yes | Fixed obstacle |
| `G` | Grease spill | No | Behaves as floor in v0.1; slipping deferred |
| `D` | Open passage | No | Normal floor at zone boundary |
| `F` | Front entrance | No | Spawn / entry marker; no out-of-bounds exit |
| `N` | Kitchen side entrance | No | Future spawn marker; no out-of-bounds exit |
| `X` | Rear escape door | No | Billy entering it completes Stage 1 |

Collision decisions are determined **solely by the semantic symbol's `solid` field in JSON**. Player and enemies are **dynamic entities**, not embedded glyphs in the terrain string. Avoid rendering `B`, `T` etc. as the final 8-bit art: these are logical map codes awaiting an Atari charset/sprite pass.

## 5. Actor and objective coordinates

| ID | Role | Spawn (x,y) | v0.1 |
|---|---|---:|---|
| `billy` | Player | **(7,13)** | Spawn immediately |
| `hazmat_front` | Pursuer | **(2,10)** | Spawn ~3s after Stage 1 starts |
| `hazmat_service` | Later reinforcement | **(27,1)** | Disabled; candidate at 35s |
| `hazmat_rear` | Later reinforcement | **(45,19)** | Disabled; candidate at 65s |
| `rear_escape_exit` | Win tile (`X`) | **(47,10)** | Touch to complete level |

Only **one hazmat enemy** is active in the first playable version. The 35s/65s reinforcements are **future balancing hooks** rather than approved active mechanics. No required keys, switches, hidden items or randomized maze exits.

## 6. Scene rules for Codex to implement (v0.1)

1. **Enter from current integrated introduction.** On FIRE at Arriving at Taco Smell, replace only the static Stage 1 placeholder with the tile-map prototype. Preserve approved title, intro, captions, POKEY music and all earlier screen input behavior.
2. **Draw floor:** For each visible map tile, fetch from row-major data with `offset = y * 48 + x`; never read outside the map. Render terrain, then enemies, then Billy. Mark solid tiles visibly different from floor. Use a simple provisional Atari character set before polished art.
3. **Movement:** Joystick port 1 moves Billy in four directions, one axis at a time. A requested step onto any `solid=true` tile or out of bounds is rejected. No diagonal corner cutting. For v0.1 **tile-at-a-time movement** is acceptable; animation and sub-tile motion can be a separate phase.
4. **Enemy:** After the initial 3s delay, spawn one hazmat worker at (2,10). Its pursuit should obey identical solid tile rules and cardinals-only movement. Use predictable pathfinding or a simple move-to-player routine (must not walk through fixed obstacles). Tune move cadence after emulator playtesting; no unapproved new spawn rules.
5. **Failure:** If Billy and hazmat occupy the same tile, show a `CAUGHT` state and offer stage restart; **no lives deducted in v0.1**, because game-wide lives/restart rules are not yet finalized.
6. **Success:** Entering `X` at (47,10) shows `STAGE COMPLETE` or a temporary success state. **Do not jump to Road 1 until its gameplay exists**.
7. **No gas attack yet:** The indoor Fire-button gas-blast control, knockback, enemy invulnerability, grease sliding and escalation are intentionally excluded from this first map/collision milestone. Preserve Fire for cutscene advance only until indoor control design is approved.
8. **No feature creep:** Do not create extra rooms, objectives, locked doors, hidden keys, extra active enemies or a scripted fake 90-second countdown simply to inflate stage duration.

## 7. Renderer/camera proposal (not final art architecture)

A straightforward debug renderer can target **40 Atari character columns x 24 rows** (8x8 character cells; 192 active scanlines) using 30 columns x 22 rows for the map, a 10-column right status strip, and two bottom text lines for instructions. **This is a prototype proposal**, not a permanent indoor HUD design. Horizontal camera origin: `clamp(billy_x - 14, 0, 18)`; vertical origin always 0. On entering a scene, draw a complete frame; then redraw only affected cells as needed to keep CPU usage reasonable. If implementer uses a different ANTIC display plan, preserve the **same map, collision geometry, actors, and exit**.

The world tile list consumes **1,056 bytes** uncompressed. A one-bit occupancy mask would take **132 bytes**; a 4-bit packed semantic map **528 bytes** only if <=16 symbols are kept. These are *options*, not requirements. In a staged Atari 64KB executable, budget for existing music, art and display-list assets before adding stage map data. There is no requirement for PMG on the title; the earlier PMG title v2/v2.1 experiments remain retired. Moving characters could be drawn as temporary characters initially.

## 8. Acceptance tests

- Exact file dimensions and recognized symbols: **48x22**, 1,056 cells.
- Only expected breaks in divider x=17 (y12-13) and x=33 (y9-10); perimeter entrances and exit correct.
- Billy, all future spawn placeholders, and X are valid non-solid terrain.
- Breadth-first search over cardinal, walkable moves finds a path **through both passages** from Billy to X.
- There are **no isolated walkable floor islands**.
- One and only one X exists; Billy cannot walk through walls, booths, counters, fryers or shelves.
- In emulator: joystick moves Billy; walls prevent crossing; one enemy follows without clipping; rear door completes; CAUGHT state resets; existing opening presentation preserved. Actual controller timing and rendering must be tested on Atari800.

Run the machine validator from the repository root:

```bash
python3 tools/validate_taco_smell_stage1.py
```

Expected result for this initial map: **751 walkable cells; 43 minimum four-direction steps** from Billy to X. This is **not** a 70–105 second walk by itself. The proposed full-stage 70–105s pacing should come from genuine enemy pressure, incidental hazards, detours and player decisions **and must be tuned from actual playtests**. Do not imply that it is already achieved.

## 9. Codex handoff / implementation boundary

> Implement Taco Smell Stage 1 **v0.1** using `docs/STAGE1_TILEMAP_SPEC.md`, `assets/maps/taco_smell_stage1_v01.map`, and `assets/maps/taco_smell_stage1_v01.json` as authoritative map inputs. Run `python3 tools/validate_taco_smell_stage1.py` before editing code. Preserve `assets/opening/GasBlasters82_OpeningSequence_v1.xex` as the known-good baseline; do not re-enable experimental PMG title v2/v2.1. Build a separate Stage 1 playable test XEX from the current title/crew/arrival flow, with tile-based movement, fixed collisions, one hazmat chaser and an X-tile stage-complete state. Keep indoor gas attacks, grease effects, reinforcement spawns and finalized HUD out of v0.1. Include the reproducible 6502 build/source and emulator launch command. Confirm scene transitions, map route and collision in tests; clearly state emulator/real-hardware validation status.

**Design status:** implementation-ready first draft of a realistic restaurant floor plan; layout and tuning are **provisional until the first playable Atari800 test**. This file does not by itself complete the playable Stage 1 task.