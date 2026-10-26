# Gas Blasters '82 — Game Design Document

**Version:** 0.2  
**Date:** 2026-10-25  
**Status:** Early design / living document  
**Primary target:** Atari 800XL (Atari 8-bit family)  
**Purpose:** Record the current concept for design discussions and eventual Codex implementation.

> This is a working design, not an implementation specification. Do not treat proposed mechanics, placeholder values, or unanswered questions as finalized requirements.

## 1. Decision status conventions

- **Confirmed** — explicitly chosen in the design discussion.
- **Provisional** — current structure or working direction, expected to be evaluated.
- **Proposed** — an idea worth considering, but not approved.
- **Open** — no decision yet.

When this document changes, preserve the distinction. A new idea discussed in chat does not automatically become a confirmed requirement.

## 2. High concept

**Gas Blasters '82** is a humorous, arcade-style action/escape game for the Atari 800XL. After an enormous meal of burritos and refried beans, the player is blamed for an apparent gas leak at a Mexican restaurant. A hazmat team is dispatched. The player escapes, drives through police pursuits, obtains gas-relief medicine and toilet paper, and ultimately tries to get home and reach the bathroom before a catastrophic gastrointestinal explosion.

Gas is both the player's problem and a potential defense: the player has secret gas powers that can help evade pursuers. An increasing **gas-pressure meter** creates urgency, especially during driving stages.

**Core fantasy:** Dodge pursuers, manage mounting pressure, collect relief, and make it to the bathroom.

**Tone:** Silly, slapstick, colorful, and deliberately reminiscent of early-1980s arcade games. The comedy should support clear, responsive gameplay rather than interrupt it.

## 3. Terminology and overall progression

- **Level:** One complete restaurant-themed adventure.
- **Stage:** One distinct section inside a level.
- **Cycle:** Completion of all four levels in order.

### Four restaurant-themed levels — Confirmed

| Level | Restaurant |
|---|---|
| 1 | **Taco Smell** |
| 2 | **Casa de Gas** |
| 3 | **The Bean Machine** |
| 4 | **The Blazing Burrito** |

Every level currently uses the same nine-stage sequence (provisional). After completing Level 4, **the game loops to Level 1** (confirmed). A complete cycle therefore contains **up to 36 stages**, pending any consolidation.

The precise differences in layouts, enemies, difficulty and presentation between restaurants are not yet settled. Increasing challenge between levels/cycles is **proposed**, not confirmed.

### Nine-stage template — Provisional

| Stage | Working name | Location / objective | Design status |
|---|---|---|---|
| 1 | Restaurant Escape | Escape the restaurant without capture by the hazmat crew | Confirmed objective |
| 2 | Road Chase I | Drive to the pharmacy before gas pressure reaches 100% | Confirmed core mechanic |
| 3 | Pharmacy Panic | Obtain **Gas-Nix**, a fictional gas-relief medicine | Confirmed objective |
| 4 | Road Chase II | Drive to the grocery store; collect Gas-Nix dropped by friends | Confirmed core mechanic |
| 5 | Grocery Mayhem | Obtain toilet paper while evading people trying to stop you | Confirmed objective |
| 6 | Road Chase III | Drive home; collect more Gas-Nix dropped by friends | Confirmed core mechanic |
| 7 | Home Exterior | Get past hazmat personnel stationed outside the house | Confirmed objective |
| 8 | Home Interior | Avoid police officers waiting inside the house | Confirmed objective |
| 9 | Final Countdown | Reach the bathroom before the final catastrophe | Confirmed objective |

Stage titles are working labels. It remains possible to **merge or remove stages** after prototyping; nine is not a locked scope requirement.

## 4. Story and stage flow

### Stage 1 — Restaurant escape

The player and friends have eaten a huge meal at the current level's restaurant. An apparent gas leak is traced to the player, and a hazmat team arrives. The player's objective is to escape the building using movement, evasion and secret gas powers.

**Confirmed:** friends are part of the restaurant outing; hazmat personnel try to catch the player; the player escapes toward a car.  
**Open:** perspective (top-down/maze or side-view), floor plan, enemy patterns, and how gas attacks operate.

### Stage 2 — First road chase: race to the pharmacy

Two cars leave the restaurant: the player's car and a separate car driven by friends. Police pursue the player. **The view is overhead, with the player's car pointing upward near the bottom of the screen as the road scrolls downward** (see Section 5.6).

**Confirmed mechanic:** the gas meter begins **near 0%**, then steadily rises as the player heads toward the pharmacy. The player must reach the pharmacy **before the meter reaches 100%**, the explosion threshold.

**Important:** Gas-Nix is **not yet available**. Friends do **not** drop Gas-Nix on this first drive, because it has not been acquired yet.

**Open:** road speed/distance, traffic patterns, gas growth rate, police attack behavior, precise explosion penalty, and whether road gas bombs offer relief.

### Stage 3 — Pharmacy: obtain Gas-Nix

The player enters a pharmacy to find **Gas-Nix**, a fictional over-the-counter-style **gas-relief medicine**. Staff, patrons and the store manager attempt to prevent the player from getting it.

**Confirmed:** this objective is gas relief, **not laxatives**.  
**Open:** pharmacy layout, how the item is picked up, whether a supply quantity matters, and how the friends receive enough Gas-Nix to dispense on later drives.

### Stage 4 — Second road chase: to the grocery store

The friends' car drives ahead near the **top of the vertically oriented road screen**, dropping Gas-Nix packages. The player maneuvers to collect them while evading police and traffic.

**Confirmed mechanic:** gas pressure continues to rise; **collecting Gas-Nix helps the player control/reduce pressure** and survive to the grocery store.

**Open:** drop frequency, package lifetime, reduction per pickup, whether the friends' car moves between lanes, and collision behavior.

### Stage 5 — Grocery store: obtain toilet paper

The player must acquire toilet paper while avoiding employees, shoppers and/or a store manager trying to stop the player.

**Confirmed:** toilet paper is required for the journey home.  
**Open:** grocery layout, number of items to collect, and exact enemy roster.

### Stage 6 — Third road chase: drive home

The player drives home under continued police pursuit. Friends again drop Gas-Nix from their lead vehicle to help manage rising pressure.

**Confirmed:** same basic pickup-and-pressure mechanic as Stage 4, en route home.  
**Proposed:** make this pursuit harder than Stage 4.

### Stage 7 — Outside the house

Hazmat personnel have staked out the player's home. Evade them and get inside.

### Stage 8 — Inside the house

Police officers are waiting inside. Avoid them with the player's secret gas powers and navigate toward the bathroom.

### Stage 9 — The final bathroom dash

Reach the bathroom before the impending explosion/implosion. Successful completion ends the current restaurant level. On completion of Level 4, loop back to Level 1.

**Open:** whether Stages 7–9 should be combined, how the final countdown works, and what happens if time expires after reaching home.

## 5. Core gameplay systems

### 5.1 Gas-pressure meter — Partially confirmed

**Confirmed:**
- The gas level is represented as a percentage.
- In the **first road chase**, it starts near zero and rises toward 100%.
- Reaching **100% represents an explosion/failure threshold**.
- After the pharmacy, collecting Gas-Nix helps keep the meter under control during the grocery and home road chases.

**Not yet decided:** pressure rules in every indoor stage; starting pressure for later drives; exact rise rate; audiovisual warnings; whether an explosion costs a life, restarts a stage or ends the game.

### 5.2 Gas-Nix pickups — Confirmed concept

- **Gas-Nix** is the official working name of the fictional gas-relief medicine.
- Obtained during the pharmacy stage.
- Friends drop Gas-Nix packages ahead of the player's car on the second and third road chases.
- Collection helps control the player's gas level.

**Balancing values are not specified**; do not hardcode speculative percentages as canonical game rules.

### 5.3 Gas-blasting abilities — Core concept, detailed behavior open

The player has secret gas powers to evade hazmat personnel and police. The original concept includes gas blasts in on-foot areas and gas bombs during vehicle pursuits.

**Open:** attack direction, duration, stun vs. knockback, cooldown, whether attacks decrease pressure, whether gas power varies with pressure, and whether Gas-Nix weakens attack strength. These are possibilities discussed during brainstorming, **not approved mechanics**.

### 5.4 Friends' lead car — Confirmed concept

- Friends accompany the player at the restaurant.
- Two vehicles depart the restaurant.
- Friends are in a separate car ahead of the player during road stages.
- Their car appears toward the top of the road screen.
- Beginning **after** the pharmacy stage, they drop Gas-Nix for the player to collect.

**Open:** what friends do in the first chase besides drive ahead; how the medicine is transferred to their car; whether the friends' car can be harmed or blocked.

### 5.5 Enemies and obstacles

**Confirmed enemy groups by setting:** hazmat crew (restaurant and home exterior); police (road and home interior); pharmacy staff/patrons/manager; grocery shoppers/employees/manager.

**Proposed:** distinct pursuit behaviors, roadblocks, variable speeds, and environmental interactions. No specific enemy names, AI algorithms or spawn rates are final.

### 5.6 Perspective, camera, and controls — Driving view confirmed

**Confirmed for all three road-chase stages (Stages 2, 4, and 6):**
- **Overhead/top-down view**, inspired by the driving presentation of *Spy Hunter*.
- The player's vehicle **faces and appears to drive upward**, positioned **toward the bottom of the screen**.
- The **road and roadside scenery scroll downward** to convey forward travel.
- The player steers **left and right** to navigate around other vehicles and toward pickups.
- Police vehicles pursue from behind and may appear beside the player.
- Friends travel ahead, with their lead car **near the top of the screen**.
- On road chases after the pharmacy, the friends drop **Gas-Nix**; pickups move down toward the player's car as the road scrolls.

**Still open for driving:** fixed lanes versus free horizontal movement; number/width of lanes; whether road width changes; precise player vertical-position freedom, acceleration/braking, speed, collision rules, input mapping, and gas-bomb controls. *Spy Hunter* is a perspective/gameplay reference, **not** a requirement to duplicate its entire control scheme.

**Still open for indoor stages:** overhead maze versus side-view action. A single Atari joystick with one fire button is the expected hardware input, but the complete mapping is **not finalized**.

## 6. Player goals, failure and progression

**Confirmed:** get through the restaurant, pharmacy, grocery store and home sequence; manage gas pressure; reach the bathroom; finish four restaurant levels; repeat from Taco Smell.

**Open:** lives, continues, checkpoints, score, high-score table, bonus points, difficulty increases after looping, and consequences of capture versus pressure reaching 100%.

We should avoid mixing two incompatible loss systems (pressure meter and separate countdown timer) until we deliberately choose how they interact.

## 7. Atari 800XL development scope

**Confirmed target:** Atari 800XL, with an intent to suit Atari 8-bit hardware.

**Current development context:** user has started a GitHub repository and a Codex discussion; MAC/65 and 6502 assembly are the intended learning/development direction.

**Not locked:** assembly toolchain/build method, disk vs. cartridge distribution, exact minimum RAM beyond the 800XL target, ANTIC graphics mode, player/missile graphics usage, memory map, sound design, and emulator test workflow. These belong in **docs/TECHNICAL_DESIGN.md** after decisions are made.

**Recommended prototype (proposed):** build a small vertical road chase with gas-meter rise, an explosion threshold, and—on a later-stage variant—Gas-Nix pickups. This tests the central mechanic before building all 36 stages.

## 8. Current decisions and explicitly rejected/obsolete ideas

| Topic | Current decision |
|---|---|
| Game title | **Gas Blasters '82** |
| Lead restaurant | **Taco Smell** (replaces early working name Taco Hell) |
| Level sequence | Taco Smell → Casa de Gas → The Bean Machine → The Blazing Burrito → repeat |
| Stage count | Nine per level **for now**; may be reduced |
| Pharmacy objective | **Gas-Nix gas relief**; not laxatives |
| Driving perspective | **Confirmed overhead/top-down**; car points upward near screen bottom; road scrolls downward; friends' car ahead near top; police pursue from behind/alongside |
| First driving stage | Near-zero pressure rising toward 100%; reach pharmacy before explosion |
| Later driving stages | Friends' car drops Gas-Nix to manage pressure |
| Friends | At restaurant; drive in separate lead car |
| Ultimate goal | Reach bathroom after getting toilet paper and returning home |

## 9. Open questions — prioritized

1. **Indoor perspective:** overhead maze or side-view action?
2. **Pressure outside driving:** does the meter keep rising indoors, pause, or follow stage-specific rules?
3. **Pressure vs. gas attacks:** do attacks relieve pressure, and at what cost?
4. **Pressure failure:** what exactly happens at 100% (life lost, stage restart, game over)?
5. **Pharmacy handoff:** how do friends receive Gas-Nix for subsequent drives?
6. **Stage count:** should exterior/home/bathroom stages be combined?
7. **Driving details:** fixed lanes or unrestricted side-to-side movement? How many lanes, what road width, and what steering/acceleration/collision rules? Gas bomb timing and pickup behavior also remain open.
8. **Progression:** how do restaurants/cycles become visually and mechanically distinct?
9. **Score/lives:** scoring, bonuses, and continuation rules.
10. **Hardware plan:** graphics, sound, memory, development and testing.

## 10. Change log

- **v0.2 — 2026-10-25:** Confirms Spy Hunter-style overhead driving for Stages 2, 4, and 6: upward-facing player car near bottom, downward-scrolling road, lead friends' car near top, pursuing police, and falling Gas-Nix pickups on later drives. Lane and control details remain open.
- **v0.1 — 2026-10-25:** Initial documented concept. Establishes four restaurants, provisional nine stages each, loop after Level 4, Gas-Nix replacing laxatives, first drive racing a rising meter, later drives collecting Gas-Nix from friends, and the bathroom objective.
