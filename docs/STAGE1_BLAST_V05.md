# Gas Blasters '82 — Stage 1 v0.5: Gas-Blast Gameplay Redesign

**Date:** 2026-11-01  
**Status:** Codex-ready *design and tuning proposal*, **not** a built or tested v0.5 XEX.  
**Atari target:** Stock Atari 800XL / 64 KB, native 6502.  
**Baseline:** The user has **played v0.4** and reports Billy's movement is **good, smooth, and diagonals work**. Protect it.

## 1. Purpose and why we are doing this

Gas blasting should become the **signature joke and gameplay tool**, not a tiny projectile or an awkward input sequence. The user found v0.3's first blast **terrible**; v0.4 deliberately made gameplay FIRE inert to validate movement independently. Stage 1 v0.5 restores an **enjoyable eight-direction gas blast** with a readable Billy pose, a growing cloud, real knockback and short recovery. The first settings are **prototype defaults** to tune by feel, not settled game-balance decisions.

The authoritative machine-readable values and state descriptions are in [v0.5 blast rules](../assets/gameplay/taco_smell_stage1_v05_blast.json). In conflicts, treat the JSON as the numeric source; resolve semantic ambiguity with this doc. [Codex v0.5 handoff](CODEX_STAGE1_V05_HANDOFF.md) defines the build boundary.

**Keep the known-good:** v0.4 Q4 smooth movement, immediate turns, eight-direction walking and 6×6 inset hitboxes; three fixed 40×22 dining/kitchen/storage rooms, all four doorway transitions; three persistent v0.3 hazmat workers, their schedule, enemy AI, room following, CAUGHT/START and X exit; the original Title v1 / Meet the Crew / Arrival and POKEY songs.

**Keep earlier versions immutable:** v0.4 code/XEX on `feature/stage1-movement-v0.4`; v0.3 and earlier binaries/builders remain available. New implementation goes on `feature/stage1-blast-v0.5` *branched from v0.4*, with current main's design files brought across. No merge into main without a user playtest.

## 2. One Atari joystick + FIRE — controls

| Input | Expected gameplay |
| --- | --- |
| Joystick only | Billy moves smoothly in 8 directions, exactly as in approved v0.4 |
| **Hold FIRE** | Billy stops, takes an aim / wind-up stance; **joystick direction now aims** |
| FIRE held + **any of 8 joystick directions** | Aim Up, Up-Right, Right, Down-Right, Down, Down-Left, Left or Up-Left. Billy visibly turns and begins a **4-frame wind-up** |
| FIRE pressed **before** direction | Still works: aim can be chosen later *during the same hold*; the next four stable directional frames produce the blast |
| Change cardinal or diagonal aim before discharge | Switch stance, reset the four-frame wind-up; final stable chosen direction is used |
| Release FIRE before wind-up completes | Cancel and **resume walking immediately**, no gas consumed |
| Remain holding FIRE after blast | Remain in aimed stance; **no repeated attack** while held |
| Release FIRE after blast | Billy can walk again once the **8-frame recovery counted from discharge** has ended; rearm the next press |

**Diagonal aim is fully supported.** A diagonal joystick input is its **own attack direction** and must not be rounded to Up/Down/Left/Right. Each of the eight directions has its own cloud/knockback vector and visible pose. No joystick direction while holding FIRE cannot launch a new blast. Both "FIRE then direction" and "direction then FIRE" must work. If FIRE is pressed during cooldown or with empty charges, display feedback and **do not queue a surprise automatic blast** even if cooldown finishes before the button is released.

A burst happens once after a stable direction is selected; **not** on the FIRE release. This resolves v0.3's awkward requirement to already have a direction chosen on the initial FIRE press. Holding FIRE always blocks walking; release resumes the v0.4 8-way movement behavior once any active recovery has elapsed. Road-stage four-way blast controls are separate and remain unchanged.

## 3. Billy's funny pose and the cloud

The effect must clearly communicate the gag: **Billy pivots so his jeans-clad backside points into any of eight intended blast directions (including diagonals)**, then an exaggerated **expanding gas cloud erupts behind him**. His body faces the opposite way from the cloud direction. Do not depict a pellet or narrow laser-like ray.

- **Wind-up (4 video ticks):** Billy pivots, backside pops out, a cheek/jeans visual visibly differentiates the blast stance from normal walking. Support **eight cardinal/diagonal orientations** with at least two distinguishable animation phases; mirror/rotate only if a recognizable jeans-clad backside remains visible.
- **Burst (18 ticks):** three growing cloud waves of **6 frames each** for **any of eight aim directions**. Wave 1 reaches one step forward; wave 2 reaches two steps with flanks; wave 3 reaches three steps with flanks. Maximum **seven 8×8 terrain cells**, clipped by obstacles and diagonal corner blocking.
- **Recovery:** an **8-frame** post-discharge recovery before movement resumes. Visually retain the pose for its initial recovery; blast cloud may continue for its full 18 frames while Billy is already free to move.
- **Feedback:** cloud shape should clearly grow, waver and dissipate (not instantly vanish or leave ghost tiles); briefly change animation on a successful hit or furniture bonk. The two existing bottom status rows may show **GAS 3/3**, **COOLING**, **EMPTY**, etc.
- **Sound:** add a brief **original POKEY airy/noisy fart-whoosh** (~10 frames) on discharge. Do not modify the approved title/cutscene music data or trigger an opening-audio regression.

**Implementation notes tied to the real v0.4 renderer:** Billy is a gameplay **GTIA Player 0** sprite using single-line PMG, **PMBASE=$B8**, player-0 glyph plane `$BC00–$BCFF`. It is intentionally low resolution (two logical pixels per PMG bit horizontally). The other PMG planes are currently available but must be memory-checked; **Codex may** add an in-game Player 1 butt overlay or temporally change player-0 pose frames. For the cloud, prefer temporary ANTIC character overlays plus careful background/actor restoration (or another demonstrably safe design). Do **not** fake the effect with an unchanged single-character shot, change the accepted title display, or re-enable retired *title* PMG experiments.

## 4. Cloud geometry and targets

The cloud is a **forward cone**, tied to Billy's chosen **cardinal or diagonal** aim. Take the tile containing Billy's 6×6 hitbox center as origin. Each aim has a unit tile-step vector **f=(dx,dy)**, where each component is -1, 0 or +1 and they are not both zero. The lateral basis is **p=(-dy,dx)**. For depth d and flank k, the candidate tile is **origin + d·f + k·p**. Wave 1 is (d=1,k=0); wave 2 is (d=2,k=-1/0/+1); wave 3 is (d=3,k=-1/0/+1). This defines **seven unique target tiles** in all eight orientations. For diagonals, d represents a **diagonal tile step**, not an additional movement-speed multiplier. Allow only tiles with a valid unobstructed **supercover line of sight** from Billy: solid tiles and D/X are opaque, and every diagonal step also requires both adjacent orthogonal side-cells to be passable. Do not allow cloud expansion through diagonal corners, walls, furniture or door openings.

**Blockers:** `# B T C R K S` occlude; no gas effect through walls/counters/shelves/tables or out of the room. A doorway/exit (`D` or `X`) is a hard **cloud boundary**: no cloud travel into another room, no trigger of doorway or level win via gas. The `G` grease tile remains inert and walkable. Keep the room's camera fixed.

**Enemy hits:** All eligible hazmat workers **in the same room** and actually reached by a cloud wave can be affected, **once each per burst**. If two are within the same expanding cloud, both should react. Enemies on the edge of a cell use their current actual tile/hitbox; no hidden off-screen damage. A stunned worker can be refreshed by a new legitimate blast; do not apply a burst twice to the same worker when the cloud expands.

## 5. Impact — make the attack satisfying

For each affected worker:

1. Display a strong hit response immediately (dazed/knocked-back pose, optional flash).
2. **Animate** knockback **up to three tile steps along the chosen cardinal or diagonal attack vector**, at **one step every three frames**. Do **not** instantly teleport the worker to its eventual tile.
3. Before each tile-step, check the **destination** against solid furniture, room boundaries, **D/X** and other occupied workers. For diagonal knockback, also check the **two orthogonal side-cells** next to the diagonal step; both must be clear and legal to prevent cutting a corner. Never push workers through doors, the exit or solid corners.
4. On a **furniture or wall collision**, stop at the last legal tile and show a short **4-frame BONK / impact flash**. Apply full **75-frame stun** regardless of travel distance. Stunned workers are harmless to Billy, preserving existing grace rules.
5. On collision with **another worker**, stop before overlap; show the impact on both. The blocking worker receives **24-frame stagger** (cannot move or catch during stagger) but **is not chain-pushed** in v0.5. Enemy occupancy and identifiers remain stable.
6. If the player is still in contact with an enemy as stun ends, honor existing one-movement-opportunity grace; never create an unavoidable immediate catch from a successful blast.

Worker paths and identities must persist across rooms as v0.3/v0.4 already do. Impact/knockback should not destroy the shared bounded BFS performance budget. All knockback and effect timers use observed NTSC frame ticks, not main-loop dispatch count.

## 6. Timing, "gas supply" and balance

A little limitation makes the blast matter, but a hard finite supply could soft-lock an escape. Use a **regenerating three-charge reservoir** as the initial *experiment*:

- Begin Stage 1 with **3/3** shots; spend **one charge per actual successful discharge** (a discharge can miss enemies and still consumes a charge).
- Regenerate **one charge every 120 video frames** (~2 seconds), up to 3/3, even while Billy moves or aims. Charge counter persists across room transitions.
- Set a short **20-frame cooldown** measured from discharge; holding FIRE does **not** repeat a blast regardless of cooldown; a *new* press is required.
- A discharge has an **8-frame recovery** before Billy may walk on release. A FIRE press with **zero charges** produces only visible EMPTY feedback and no damage/effect, never traps the player permanently.
- Stage restart resets the reservoir, cooldown, animation, cloud, hit bookkeeping and workers to their initial values. Caught and win states freeze stage gameplay as before.

These numbers are deliberately adjustable; if the player feels forced to wait for gas instead of using skill, lower the cost / speed refill. **Do not** implement the road-trip gas-pressure meter indoors: these are prototype burst charges only.

## 7. Atari800 and 6502 quality gates

Preserve the previous **smooth movement** test results first. Build a **separate XEX** and source set on v0.5's branch, with replayable 6502 tests. Run:

```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
python3 tools/validate_stage1_pressure_v03.py
python3 tools/validate_stage1_blast_v05.py
```

**Automated acceptance** must cover: FIRE-before-direction, simultaneous FIRE+direction, **all eight cardinal/diagonal aims**, idle/no-direction aim, stable aim 4 frames, aim change cancels wind-up, one blast per hold, release/rearm and recovery, charge/cooldown/refill semantics, 3 cloud waves and block/door occlusion, multi-worker single-hit tracking, up-to-3-cell animated push, collision with furniture and other worker without overlap, all 3-worker AI/state and frame wrap, inset AABB contact while stunned, all room doors and storage exit, no leaked cloud graphics or PMG trails, unchanged opening/music, safe XEX segments and measured CPU budget.

**Atari800 playtest questions:** Can Billy aim without wrestling with the joystick? Is the butt pose actually recognizable? Is the cloud large, funny and satisfying? Are knockback and furniture bonks visibly powerful? Does release-to-walk feel responsive? Does gas run out too quickly? Is any sprite flickering, stale cloud or sound corrupting the scene? Does moving through three rooms remain fun? Record what happened, not just whether tests passed.

**Non-goals:** No fourth room, road gameplay, pharmacy/grocery, changed restaurant layout or scrolling, more enemies, final character illustration, score/lives redesign, global pressure meter, new audio track, or fixed 70–105s completion countdown.

**Status:** This v0.5 design **does not** authorize edits to existing v0.4 binaries/source and **is not a claim** that v0.5 animations or controls already work in an emulator.
