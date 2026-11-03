> **HISTORICAL ARCHIVE.** Superseded by the [current accepted Stage 1 design](../../STAGE1_DESIGN.md). The original proposal/handoff may mention deleted feature branches, unbuilt XEXs or outdated acceptance status.

# Gas Blasters '82 — Stage 1 v0.4: Billy Movement and Control Specification

**Date:** 2026-11-01  
**Status:** Codex implementation target; speed and hitbox values are **prototype defaults**, awaiting Atari800 playtesting.  
**Scope:** Fix Billy's slow, cumbersome controls. This milestone **does not redesign the terrible v0.3 gas blast**; that becomes v0.5.

## Playtest feedback and decision

The user **played v0.3** in Atari800. The additional gameplay pressure feels somewhat better, but **Billy moves too slowly and awkwardly** and **the gas-blast mechanics are unsatisfactory**. The current v0.3 6502 loop moves Billy one character-cell step only once every **8 observed NTSC frames**. That is nominally one 8-pixel tile per 8 frames, causing visually jerky movement and poor steering precision.

**v0.4 goal:** Billy should respond immediately to the joystick, glide smoothly across individual tiles, and slide naturally along table/wall edges. We are improving *control feel*, not finishing Stage 1, polishing art, retuning all enemies, or starting Road 1.

The source of truth for numeric movement defaults is [`assets/gameplay/taco_smell_stage1_v04_movement.json`](../../../assets/gameplay/taco_smell_stage1_v04_movement.json). All values are adjustable after testing.

## 1. Runtime baseline and unchanged scope

Use the **actual working v0.3** code and runnable XEX on `feature/stage1-pressure-v0.3`: `tools/build_stage1_v03.py`, `tools/test_stage1_v03.py`, `assets/stage1_v03/`. V0.3 already contains three hazmat worker entities, bounded shared BFS pursuit, transitions, 6502 sprite glyphs and a first gas-blast experiment.

**Keep:** Three distinct **40×22** fixed-screen dining, kitchen and storage rooms, two bottom status rows, all four bidirectional doorway transitions, backtracking, v0.3's three unique pursuit workers and their activation timings, the CAUGHT/START restart state, Storage X stage completion, and user-approved Title v1 → Meet the Crew → Arrival with original Arcade Rock/Funky Gas Attack music and unchanged pre-game START/FIRE behavior.

**Do not change:** the maps; room entrances; game-wide driving mechanics; Road 1; gas meter; stage pacing target; customer AI; hazard count; music; cutscenes; lives; scores. Keep the existing `feature/stage1-pressure-v0.3` branch and XEX as the regression baseline. v0.4's prototype should live on **`feature/stage1-movement-v0.4`**, created from v0.3 plus current main's design docs.

## 2. Coordinate system and target speed

- Retain 8×8 **logical-pixel** tiles within a **320×176** logical-pixel, 40×22 room. Note that final pixel-to-hardware PMG mapping must be verified in the actual ANTIC mode.
- New player position = top-left of Billy's visible 8×8 sprite, with **4 fractional bits** per axis (one unit = 1/16 logical pixel). Use 16-bit or wider coordinates; **not** only tile x/y integers. Read tile positions as needed from the pixel-space center.
- **Cardinal walking:** 24/16 = **1.5 logical pixels per observed NTSC frame** (prototype initial value).
- **Diagonal walking:** allow Atari joystick diagonals. Each axis moves 17/16 = **1.0625 logical pixels/frame**, giving approximately the same total speed as cardinal movement. No diagonal gas attacks.
- Starting and stopping are **immediate**. Direction can reverse or change without waiting for another eight-frame movement tick. No simulated acceleration or slippery inertia.
- A 60-frame straight walk therefore covers nominally **90 logical pixels**, versus ~60 under v0.3's old 8-frames-per-tile stepping, before walls or game-state interruptions. A 60-frame diagonal walk covers ~63.75 pixels on each axis.
- Drive movement from **new video frames** (VBI/RTCCLOK or safe equivalent), not from the number of main-loop calls. A long frame/room redraw must not permit obstacle tunneling; bounded catch-up steps are acceptable. Prove in tests that player input is read even while pathfinding work is ongoing.

**Important:** A hidden fractional coordinate with Billy still visually snapping to 8×8 character cells is **not** an acceptable result. Actual on-screen motion must have sub-tile positions.

## 3. Pixel collision, diagonal corners and wall sliding

Billy's visible sprite occupies an **8×8** logical-pixel box. Use an inset **6×6** collision AABB: pixel bounds `[spriteX+1, spriteX+7)` and `[spriteY+1, spriteY+7)`. Treat those bounds as **half-open**, with fractions in the same coordinate system. A solid tile is an 8×8 rectangle; any overlap with a solid tile blocks the movement that produced it. Solid tiles: `# B T C R K S`. Walkable: `. D F N G X`.

For every movement tick:
1. Resolve the requested X component against all overlapped tiles, **without** ever jumping over walls (per-pixel or swept/substep collision). If blocked, stop X at the last safe offset.
2. Resolve Y similarly against the actual resulting X. If only one component was obstructed, allow movement along the other axis at the cardinal target rate for **natural wall sliding**. Recheck the motion at that adjusted rate.
3. Block illegal diagonal corner passage: no moving between diagonally touching solid tiles if Billy's 6×6 box could not fit. Do not clip into shelving, counters, tables or map edges.
4. Keep the sprite fully inside the 320×176 gameplay viewport, except via **defined doorway triggers**. Do not allow movement into the two bottom status rows.

**Example:** Billy holding up-right against a kitchen counter should continue moving up if the right component is blocked, rather than getting stuck. Reversing should respond on the *next available observed frame*, not after an eight-frame wait.

## 4. Doorways and room changes

Keep the exact v0.2 room-link metadata; two-tile-high doorways remain `y=10/11`.

- Trigger door transition when **Billy's collision-box center** first enters the doorway tile `D` (not when a visual sprite corner grazes an adjacent doorway).
- Redraw the destination room and reset Billy's coordinates to the top-left of the **inward destination tile**: x=1 (8 logical pixels) or x=38 (304 pixels), preserve the doorway y (10 or 11), and clear fractional coordinates.
- Prevent retriggering/back-bounce from one held input. Backtracking intentionally remains possible.
- In storage, entering X at **(39,10)** by Billy's **collision-box center** triggers STAGE COMPLETE as before. Front/service doors `F/N` are not outside-map portals.
- All enemy room-follow logic continues to see Billy's **integer center tile**; switching to pixel-space controls must not strand workers or duplicate an encounter.

## 5. Enemies, catching and CPU budget

**Do not rebalance** v0.3 worker activation, tile-based movement speed, three unique IDs or 45-frame room follow in this movement-focused iteration. A faster Billy may change difficulty; record it as a playtest finding and tune it later, rather than masking control improvements with AI changes.

Replace same-tile player/enemy contact with **overlapping inset AABBs**: Billy's **6×6** hitbox against each active, non-stunned worker's **6×6** box centered within that worker's 8×8 grid tile. Preserve v0.3 grace and stunned behavior when it applies. Check contact after player/enemy updates, not only when a tile boundary changes. A collision with an unstunned worker invokes existing CAUGHT.

The v0.3 main loop already uses a shared, budgeted reverse BFS and had CPU-only simulated cost samples—not a proven real-hardware frame budget. **Do not** trade responsive movement for expensive full-screen redraws. Prefer a hardware gameplay sprite for Billy **if safe** or a clipped software sprite that restores covered background cells. The previously rejected **PMG title v2/v2.1** does not forbid PMG for *gameplay*, but title assets and DLI timing must remain untouched. Build/tests must verify RAM, interrupts, rendering and no visible sprite flicker or character corruption in Atari800.

## 6. FIRE / blast experiment deliberately deferred to v0.5

v0.3's FIRE+direction blast felt terrible to the user. For this **isolated movement test**, **disable indoor gas blasting** in the v0.4 runtime: do not fire, knock back, stun or show a blast cloud; **holding FIRE must NOT immobilize Billy**. Do not reinterpret this as cancelling Billy's signature gas power or changing any road gas attack controls. Preserve the original v0.3 XEX and source separately for future redesign.

v0.5 will explicitly revisit **four cardinal attack directions, aiming, input timing, animation, area/impact, knockback, stun and player feedback**, after we validate basic movement. **FIRE to advance the cutscenes must remain unchanged.**

## 7. Tests, acceptance, and user playtest

Run the old v0.1/v0.2 map validators and the v0.3 rules validator unchanged. Execute prior Python/py65 6502 tests against prior **unchanged versioned builds**, while adding **new v0.4 runtime tests** rather than requiring old v0.3 blast expectations to hold in v0.4.

Required automated tests:
- 1.5 px/frame cardinal movement, normalized diagonal (~1.5 px/frame vector speed), and reversal on the next observed frame.
- The **visible renderer** changes pixel position within a tile; no "fake subpixel" logic with tile-jump graphics.
- Wall sliding when one axis is blocked; no diagonal corner clipping; correct motion next to all solid types and bounds.
- Correct door-center trigger, four room transitions in both directions, 1-tile-inward 8-pixel-aligned spawn and no automatic door bounce; storage exit still wins.
- All three original unique hazmat entities and pursuit, contact fairness using AABBs, grace/stun, CAUGHT and START restart, fractional coordinate reset on respawn.
- Holding FIRE in Stage 1 v0.4 is inert **and does not freeze walking**; Title START and intro FIRE/music remain byte-identical.
- No 6502 memory collision, display/DLI/PMG side effects, frame stalls or out-of-bounds read/writes. Provide CPU-cycle samples and note that py65 alone is not Atari800.

**Pass/fail criteria in Atari800:** Movement visibly progresses through sub-tile pixel positions, responds promptly, navigates around tables without snagging, reverses instantly, and gives consistent diagonal speed. It must not clip through terrain or make enemy contact unfair. Check smoothness, ghosting, input lag and speed in each room. User decides whether feel is good enough to move to **gas-blast v0.5**; gameplay polish beyond that is deferred.

**Not a v0.4 deliverable yet:** This is the specification for Codex, not a completed XEX or claim of a tested renderer.
