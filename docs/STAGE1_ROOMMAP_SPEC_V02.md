# Gas Blasters '82 — Stage 1 Room-Map Contract v0.2

**Date:** 2026-11-01  
**Status:** Gameplay direction approved; exact maps and timing are implementation-ready **prototypes** awaiting Atari800 playtesting.  
**Platform:** Stock Atari 800XL (64 KB), real 6502 code and ANTIC/GTIA.  
**Authority:** This v0.2 contract supersedes v0.1 **for the Stage 1 room-based prototype only**; it does not delete or rewrite v0.1 or any opening asset.

## 1. Design choice

Taco Smell uses a **fixed, full-screen, room-to-room** overhead perspective: **Dining Room → Kitchen / Service → Storage / Rear Exit**. No horizontal/vertical scrolling within Stage 1. Billy may go backward through doorways. Transition is immediate on entering the doorway tile, with the entire next room replacing the screen.

This **non-scrolling, fixed-screen implementation decision is for Stage 1 v0.2 only**. Later indoor stages, including pharmacy and grocery, may use **room-to-room transitions, scrolling within rooms/areas, or both together**. For example, Billy could run down a **scrolling grocery aisle** while pursued by police, hazmat workers and townspeople, then transition into another department or room. Exact layouts and camera mechanics are still open; do not impose a single camera style on all indoor stages.

## 2. Canonical files

- [Stage 1 v0.2 metadata](../assets/maps/taco_smell_stage1_v02.json): symbols, semantics, actor spawns, doors, coordinates, camera and encounter rules.
- [Dining room](../assets/maps/taco_smell_stage1_v02_dining.map), [kitchen](../assets/maps/taco_smell_stage1_v02_kitchen.map), [storage](../assets/maps/taco_smell_stage1_v02_storage.map): one ASCII terrain cell per 8×8 logical pixel character.
- [Map visual preview](../assets/maps/taco_smell_stage1_v02_preview.svg): overview only, not the final runtime artwork.
- [Validator](../tools/validate_taco_smell_stage1_v02.py) (Python 3 stdlib): exact topology, spawn/connectivity, and reciprocal doors.
- [Codex v0.2 implementation handoff](CODEX_STAGE1_V02_HANDOFF.md): implementation scope and acceptance instructions.

**Do not modify or delete** v0.1 files in assets/maps, Stage 1 v0.1 executable or its builder, nor the accepted original [opening v1](../assets/opening/GasBlasters82_OpeningSequence_v1.xex). Codex's Stage 1 v0.1 implementation exists on the branch `feature/stage1-playable-v0.1`; use it as the code baseline, not a replacement for the main branch's old prototype files.

## 3. Geometry and rendering contract

Each room is **40 columns × 22 rows**, screen filling **all 40 horizontal character columns**. Reserve **two final 40-column rows** for a modest status/instructions footer. A simple 40×24, 8×8 Atari text-mode screen is an **initial implementation target**, not a permanent finalized indoor-graphics mode.

Logical coordinate origin is **top-left (0,0)** separately within each room. X grows right; Y grows down. Valid coordinates: x 0…39; y 0…21. Tile index is `y*40+x`; **never index outside bounds**. One room's uncompressed semantic map is 880 bytes; all three total **2,640 bytes**. Loading/swapping from these tables into a shared 960-byte display buffer is preferred to keeping three screen copies. Real 6502 and OS/stack/screen/font/POKEY memory boundaries must be validated by Codex against its v0.1 memory map.

At every room change, **replace the entire gameplay display**; no scrolling camera or half-screen pan. Before drawing the next room: set current room, assign destination player tile, load or reference the room tile map, draw terrain, draw hazmat if in same room, draw Billy, then status. Only those state transitions that have been tested are considered complete.

## 4. Door and position contract

**Each door is two tiles tall** (y=10 and y=11). `D` means walkable **linked doorway**; moving **into** it triggers the room swap. To avoid an immediate bounce-back, Billy appears **one tile inside** the destination room, preserving y, not on its doorway tile.

| Source | Door location | Destination | Billy appears |
|---|---|---|---|
| Dining | (39,10), (39,11) | Kitchen | (1,10), (1,11) respectively |
| Kitchen | (0,10), (0,11) | Dining | (38,10), (38,11) |
| Kitchen | (39,10), (39,11) | Storage | (1,10), (1,11) |
| Storage | (0,10), (0,11) | Kitchen | (38,10), (38,11) |

Dining front door `F` at (0,10) and kitchen exterior service entrance `N` at (22,0) are hazmat spawn markers, **not** Billy room transitions; no outside-map movement. The one rear exit `X` at **Storage (39,10)** triggers `STAGE COMPLETE`, not another room or Road 1. The topology is linear but **backtracking is allowed**.

## 5. Player, collision and obstacles

Billy begins in dining **(7,15)**. Existing v0.1 four-direction joystick movement, collision and movement pacing should carry over. Non-solid map symbols: `.`, `D`, `F`, `N`, `G`, `X`. Solid: `#`, `B`, `T`, `C`, `R`, `K`, `S`. The v0.2 JSON has the definitive symbol table. Moving diagonally or through corners is not permitted in this tile-step prototype. A room swap must not put Billy inside furniture, a wall, or a pursuing enemy.

**Room character:** Dining is open with booths/tables, kitchen constricts routes with equipment/counters and inert grease patches, storage is a shelving slalom leading to the back exit. Graphics may be debug glyphs. Do not add keys, switches, artificial wait timers or hidden objectives.

## 6. Enemy continuation across rooms

**One** active hazmat worker starts in dining at **(2,10)** after **3 seconds / 180 NTSC frames**. Hazmat uses passable cardinal tiles and cannot move through furniture or walls. It is the **same persistent entity** across room changes; do not reset its coordinates on room load, destroy it, or clone it.

**Minimal v0.2 pursuit-follow rule:** On Billy passing a doorway while the active worker is still in his departing room, retain the worker's position and schedule a **90-frame (approximately 1.5 s) doorway follow**, using that same source→destination link and corresponding inward entry tile. If Billy returns to the source room before the follow resolves, cancel the queued move and resume the original worker position. If Billy changes multiple rooms quickly, the enemy must progress through intermediate rooms in order rather than teleport across the building. On arrival, choose an adjacent valid empty tile if the preferred doorway spawn is occupied. Preserve the worker's single identity and original spawn timer across all transitions.

`hazmat_side_future` and `hazmat_rear_future` are present as **disabled** future-spawn metadata; do not activate them in v0.2. Enemy chase speed and player speed remain tuneable after emulator testing.

## 7. Other game states and controlled scope

- **CAUGHT:** If Billy shares a tile with the active hazmat, display CAUGHT and allow START to restart **Stage 1 only**, restoring dining layout/player spawn and initial 3-second enemy delay. No finalized lives deduction.
- **STAGE COMPLETE:** Billy reaches storage `X`; show existing temporary completion message. Do not jump into Road 1 before that stage exists.
- **Backtracking:** Always possible through a `D`, including with pursuit active.
- **Music / opening:** Keep the user-approved **Title v1 → Meet the Crew → Arriving at Taco Smell** sequence, Arcade Rock and Funky Gas Attack behavior, Fire to advance and START input. Retired PMG title experiments v2/v2.1 must remain disabled.
- **No new features:** Indoor gas blasting, grease sliding, multiple simultaneous hazmat workers, panic escalation, new artwork, pickups, separate scrolling maps, new scoring or lives systems are beyond the v0.2 milestone.

## 8. Validation and practical acceptance

Run:

```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
```

The **v0.1 validator must still pass** because that map remains as historical data. The v0.2 validator checks 40×22 per map, connectivity, exact doorway and perimeter semantics, all spawns and exit, and reciprocal links.

Codex must add **6502/runtime tests**, not only map checks: correct tile lookup `room*880 + y*40 + x` or safe equivalent; all four transitions and reverse travel; correct y-preserving inward spawn; no unintended repeat transition while a key is held; unique active hazmat and preserved pursuit state; CAUGHT and START restart; Storage X success; no display corruption or overlapping RAM; unchanged opening sequence.

Then hand off an actual **separate playable v0.2 XEX**, reproducible source/build script and Atari800 launch instructions for the user's first full emulator test. **This document is a design deliverable, not proof that v0.2 gameplay is running yet.**

