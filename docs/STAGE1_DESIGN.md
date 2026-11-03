# Stage 1 — Taco Smell: Current Gameplay Specification

**Baseline:** `stage1-v0.5` on `main` (stock Atari 800XL, 64 KB; native 6502 XEX).  
**Status:** Implemented and *user-playtested* playable prototype. User reports movement feels smooth and the gas blast is good enough for now. **Not** a final game-balance, visual-quality, complete-regression or real-hardware sign-off.  
**Sources of truth for numeric values:** `assets/gameplay/taco_smell_stage1_v04_movement.json`, `assets/gameplay/taco_smell_stage1_v03_rules.json`, `assets/gameplay/taco_smell_stage1_v05_blast.json`, `assets/maps/taco_smell_stage1_v02.json` and the shipped `assets/stage1_v05/manifest.json`. The executable builder is `tools/build_stage1_v05.py`.

This document supersedes all numbered Stage 1 *design proposals* for **current behavior**. The historical specifications and handoffs live in [the archive](archive/stage1/README.md), and each earlier XEX/source snapshot remains in its Git tag. Keep road driving / vehicle blast requirements distinct from on-foot gameplay.

**Version precedence note:** The **v0.4 movement JSON** still contains a historical design comment anticipating four-way indoor blasts in a future v0.5. That comment **was superseded** by the implemented **v0.5 eight-way blast JSON/XEX**. Use v0.4 JSON only for its current **movement/collision values**; use v0.5 JSON for **all indoor blast directions and combat rules**. Do not rewrite historical v0.4 data to conceal this progression. The v0.5 manifest/profile's `emulator_tested: false` values are **original build-time evidence**; the user subsequently played v0.5 in Atari800 and accepted the broad blast feel, not exhaustive regression/hardware verification.

## Player goal and game flow

1. **Title** (console START) → **Meet the Crew** (FIRE) → **Arriving at Taco Smell** (FIRE) → restaurant escape.
2. Billy must evade the hazmat workers, pass from the Dining room through Kitchen and Storage, then reach the **rear exit `X`** at Storage's right edge to complete Stage 1.
3. **CAUGHT** is the failure screen; console START restarts Stage 1, resetting relevant game state. The COMPLETE screen ends the prototype; **no stage-to-stage transition into driving has been built here**.
4. The approved title/intro visuals and **Arcade Rock** / **Funky Gas Attack** POKEY music remain the opening baseline.

## Rooms, map and doors — implemented

- Three **independent, full-screen 40×22** 8×8-character terrain grids: Dining (room 0), Kitchen (room 1), Storage/Rear Exit (room 2). Display uses 40 columns for gameplay; **two bottom status rows**. No room scrolling. Linked doorways allow travel **forwards and backwards**, with two 8×8 doorway cells at y=10/11 for each link.
- The room changes as Billy's **inset 6×6 collision-box center** enters a `D` tile. The next room spawns him at its inward x=1 or x=38 tile, keeps doorway y, clears fractional remainder and avoids immediate bounce. Winning requires Billy's center to enter Storage `X` (39,10).
- The default tile classifier remains: **solid** `# B T C R K S`; **traversable** `. D F N G X`. Door and exit are valid Billy navigation, but **opaque to gas clouds** and cannot be crossed by forced worker knockback. `G` grease is ordinary passable floor in this prototype: **no slip mechanic**.
- Map authority: [room metadata](../assets/maps/taco_smell_stage1_v02.json), `assets/maps/taco_smell_stage1_v02_{dining,kitchen,storage}.map`, and [preview](../assets/maps/taco_smell_stage1_v02_preview.svg). The original 48×22 scrolling layout was an abandoned **v0.1 historical experiment**, not the current map.

## Billy's movement and contact — implemented, positively playtested

- With FIRE released, Billy has immediate **eight-way joystick walking**, including normalized diagonals, without inertia or the old eight-frame/whole-tile gate.
- Position uses 16-bit **Q4 (1/16-pixel)** per axis. Nominal NTSC cardinal speed is **24/16 = 1.5 logical pixels/frame**, diagonal speed **17/16 = 1.0625 pixels/frame per axis**. All rates are prototype values; NTSC video timing is the reference.
- The visible temporary character is an **8×8 PMG sprite**. Player collision uses an **inset 6×6 axis-aligned rectangle**, X/Y swept substeps, precise solid-tile checks and **wall sliding**. Contact with a worker uses hitbox overlap, not only matching tile centers.
- Hardware rendering: Atari **GTIA Player 0** is Billy's body; sprite positioning advances by roughly two logical pixels horizontally and one scanline vertically. The logical Q4 position is finer than hardware PMG pixels. User accepted movement *feel*, not final sprite artwork or precision.
- Existing workers are rendered in the character layer and retain their own grid-based movement.

## Hazmat pressure — implemented, gameplay tuning provisional

Three unique workers persist across room movement, with spawn identities and timers from `assets/gameplay/taco_smell_stage1_v03_rules.json`. Their room-specific encounter beats are Dining pursuer, Kitchen interceptor and Storage exit blocker. Approximate specified activation is Dining at 60 frames and Kitchen/Storage at 30 frames from entry, with nominal movement cadence of 12/10/10 frames and door-follow delay of 45 frames. **Treat JSON and the v0.5 XEX as authoritative if any narrative timing differs.** Bounded incremental search (shared eight BFS cells per dispatch) protects responsiveness.

Workers may be stunned, knocked backward or briefly staggered by gas. They must never duplicate, travel across nonadjacent rooms, or catch Billy while properly stunned. CAUGHT/restart/room transitions preserve their intended identities and state, except a full restart resets them. Gameplay difficulty remains a balancing topic, not a signed-off final design.

## Gas blasting — eight directions on foot, implemented and tentatively accepted

| Input or action | Current behavior |
| --- | --- |
| Joystick without FIRE | Smooth eight-way walking |
| Hold FIRE | Stop walking; enter directional aiming stance |
| FIRE + any cardinal **or diagonal** aim | Start a **4-video-frame** stable-direction wind-up |
| Press FIRE before giving direction | Valid: later direction during same hold starts the wind-up |
| Change direction before blast | Restart the wind-up for the newly aimed direction |
| No direction, or release before wind-up | No attack or gas consumption; early release resumes walking |
| Stay holding after discharge | One blast only; **release FIRE to rearm** |
| Release after a blast | Resume walking once **8-frame post-discharge recovery** is over |
| Press during cooldown / without charges | Feedback but **no queued/delayed attack** |

The eight attack directions are Up, Up-Right, Right, Down-Right, Down, Down-Left, Left, Up-Left. **Diagonal firing is independent**, not rounded to a cardinal direction. Car blasts in later road stages remain **four-way only**.

### Attack effect and collision

- Billy visibly pivots his jeans-clad backside toward the aim, including temporary two-phase/eight-way gameplay PMG pose. **Player 0** forms the body; **Player 1** supplies a blue-jeans accent. These are temporary art assets.
- Cloud unfolds in **three cumulative six-frame waves**: 1 cell, then 4, then **7 reachable cells** across three forward depths. It is a growing cone, **not** a one-tile projectile. Each room's solids and D/X occlude. **Diagonal supercover** visibility prevents gas leaking through blocked wall corners.
- Each reached same-room worker is hit **at most once per burst**. An affected worker may be pushed **up to three cardinal or diagonal tile steps**, animated at one step per three frames and stopping before furniture, wall, room edge, D/X, or another worker. Diagonal pushes also require both orthogonally adjacent corner cells clear.
- Typical hit response: **75-frame worker stun**, **four-frame BONK/impact flash** when blocked; another worker blocking the push is staggered for **24 frames** instead of chain-pushed. Keep stun-expiry contact grace.
- Prototype supply: begin with **3/3 GAS shots**, spend one per discharge, regenerate **one every 120 NTSC frames**, cooldown **20 frames** from discharge, walking recovery **8 frames**. Supply persists through rooms, resets on restart; there is no permanent empty soft-lock. Status text resides in the existing two footer rows.
- A short (~10-frame) **original Stage-1-only POKEY gas sound** plays without altering the approved title/cutscene compositions.

Prototype numeric contract: [gas tuning JSON](../assets/gameplay/taco_smell_stage1_v05_blast.json); current builder/test specifics: [v0.5 artifact README](../assets/stage1_v05/README.md).

## Technical implementation and evidence

The XEX is emitted reproducibly from `tools/build_stage1_v05.py`, which layers v0.5 blast/PMG logic onto the existing v0.4 movement and v0.3 engine in checked, versioned segments. The output is `assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex`; the manifest records **SHA-256 b7e1c423b25f7cb10cd90cd063090579eaea4bd27b7310c70e8ea5f02e169753**. Single-line PMG memory uses PMBASE `$B8`, P0 `$BC00`, P1 `$BD00`. Cloud/actor dirty restoration avoids full redraw for every blast animation tick. See [technical design](TECHNICAL_DESIGN.md).

The implementation README records **18 v0.5 CPU tests**, **15 unchanged v0.4 tests**, plus four validators passing in Codex's prior build. A sampled three-worker/active-blast dispatch had a maximum **20,689 CPU cycles** in the py65 profiling scenario; **ANTIC DMA, OS interrupts and worst-case frames were not included**.

**What the user actually approved:** v0.4 movement was reported smooth with working diagonals; after playing v0.5, the gas blasting was reported **good for now** and further refinement deferred. That **does not prove** every cloud occlusion, frame pacing, enemy contact edge, visual detail, sound effect or physical 800XL condition was manually tested. Use the [regression checklist](STAGE1_REGRESSION_CHECKLIST.md) to establish those independently.

## Not yet done / explicitly out of scope

No Stage 2 driving in this XEX, no Game-Wide scoring/lives/pressure rules, no final restaurant art, no indoor grease-slipping, no item pickup or later indoor location, no PAL or physical 800XL acceptance. Review [deferred improvements and coverage gaps](STAGE1_DEFERRED_WORK.md) rather than interpreting the prototype as production-complete.

**Change history:** v0.1 initial scrolling trial → v0.2 fixed rooms → v0.3 pursuit/first blast → v0.4 smooth walking → v0.5 eight-way blasts. Historical proposals and Codex handoffs are filed in the [Stage 1 archive](archive/stage1/README.md); versioned commits are available through immutable Git tags.
