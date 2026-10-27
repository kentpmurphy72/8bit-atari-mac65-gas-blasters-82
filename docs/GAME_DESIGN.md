# Gas Blasters '82 — Game Design Document

**Version:** 0.12  
**Date:** 2026-10-26  
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

**Main character name — Confirmed:** **Billy Blaster**. He is the young protagonist featured in the approved packaging direction.

**Required introductory line — Confirmed (exact wording):**

> Meet Billy Blaster. He's got a fast car, great friends, and a stomach that's about to become a national emergency.

**In-game placement:** Include this line somewhere the player can encounter it **within the game**, preferably as part of the opening/title introduction or a short pre-Stage-1 story sequence. The final screen, timing and presentation are **open**. It may be split across multiple screens or text lines to accommodate Atari 800XL text/graphics limitations, but retain the exact wording, capitalization, apostrophes and punctuation in the combined text. Do not treat instruction-manual text alone as satisfying the in-game requirement.


### Stage 1 — Restaurant escape

The player and friends have eaten a huge meal at the current level's restaurant. An apparent gas leak is traced to the player, and a hazmat team arrives. The player's objective is to escape the building using movement, evasion and secret gas powers.

**Confirmed:** friends are part of the restaurant outing; hazmat personnel try to catch the player; the player escapes toward a car.  
**Open:** perspective (top-down/maze or side-view), floor plan, enemy patterns, and how gas attacks operate.

### Stage 2 — First road chase: race to the pharmacy

Two cars leave the restaurant: the player's car and a separate car driven by friends. Police pursue the player. **The view is overhead, with the player's car pointing upward near the bottom of the screen as the road scrolls downward** (see Section 5.6).

**Confirmed mechanic:** the gas meter begins **near 0%**, then steadily rises as the player heads toward the pharmacy. The player must reach the pharmacy **before the meter reaches 100%**, the explosion threshold.

**Important:** Gas-Nix is **not yet available**. Friends do **not** drop Gas-Nix on this first drive, because it has not been acquired yet.

**Confirmed road features:** free left/right steering, winding road, occasional two-way fork with an on-screen arrow indicating the intended route, and recoverable shoulder/off-road driving with a **2.0-second off-road countdown** before an explosion costs one life. Driving uses approximately two-thirds of the screen; a separate one-third HUD shows gas pressure, distance in miles to the next destination, score, and other necessary indicators.

**Confirmed:** If the player takes the **wrong fork**, it is a **detour, not an immediate crash**. The **miles-to-destination counter continues counting down, but more slowly**, while **gas pressure keeps rising**, making the detour costly. Police cars and hazmat vans intentionally try to **ram/PIT-style shove** the player off the road; being pushed beyond the shoulder begins the same **2.0-second recovery countdown**, not an instant crash. The player can use **gas blasts from all four sides of the car** to push pursuing vehicles away.

**Open:** road speed/distance and precise distance penalty for incorrect forks, how detours rejoin the intended road, gas growth rate, exact outcome of a **100% gas-pressure explosion** (distinct from off-road failure), respawn after an off-road explosion, and eight-direction gas-blast control mapping.

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

### 5.3 Gas-blasting abilities — Four-sided vehicle blasts confirmed; details open

The player has secret gas powers to evade hazmat personnel and police.

**Confirmed for the first playable prototype:** implement **four-direction gas blasting only** (front, rear, left, right). A blast **pushes enemy cars and hazmat vans away**, helping prevent ramming and attempted forced off-road crashes. Four-way blasting is the initial implementation scope; it does not permanently exclude diagonals.

**Eight directions are technically possible on the Atari 800XL**: its digital joystick detects the four cardinal directions plus their four diagonal combinations. However, **diagonal gas-blast directions are still under consideration**, not an approved gameplay rule.

**Critical control-design issue:** the Atari's typical one-button joystick is also responsible for steering. Eight-direction aiming and car steering cannot be independent at the same instant with only that one stick unless the game defines a mode/priority scheme. One possible **proposal**, not yet approved, is **hold Fire + point joystick to aim**, temporarily suspending steering while the car coasts; release Fire to resume steering. Alternatives include Fire + direction affecting both steering and aiming, a retained aim direction, or a simpler four-way blast scheme.

**Open:** whether to add diagonals *after testing the four-way prototype*; exact Fire/joystick input mapping for steering and blast selection; blast range, animation, duration, cooldown and knockback; effects on player pressure; whether Gas-Nix weakens gas attacks; and how gas blasts work during indoor stages.

### 5.4 Friends' lead car — Confirmed concept

- Friends accompany the player at the restaurant.
- Two vehicles depart the restaurant.
- Friends are in a separate car ahead of the player during road stages.
- Their car appears toward the top of the road screen.
- Beginning **after** the pharmacy stage, they drop Gas-Nix for the player to collect.

**Open:** what friends do in the first chase besides drive ahead; how the medicine is transferred to their car; whether the friends' car can be harmed or blocked.

### 5.5 Enemies and obstacles

**Confirmed enemy groups by setting:** hazmat crew (restaurant and home exterior); police and **hazmat vans** (road), police (home interior); pharmacy staff/patrons/manager; grocery shoppers/employees/manager.

**Confirmed driving enemy behavior:** police cars and hazmat vans **deliberately ram or attempt PIT-style side collisions** to push the player off the road. The player can counter them using gas-blast knockback. If a resulting shove carries Billy **beyond the shoulder**, he has **two continuous seconds** to return to the road before his car **explodes and one life is lost**. A shove or brief shoulder excursion is not an immediate crash.

**Open:** AI positioning and attack patterns, collision impulses, recovery opportunity before off-road failure, enemy knockback strengths and limits. Other enemy behaviors and roadblocks remain **proposed**; no specific enemy names or spawn rates are final.

### 5.6 Driving perspective, movement, road layout, and HUD — Confirmed design

**Confirmed for all three road-chase stages (Stages 2, 4, and 6):**
- **Overhead/top-down view**, inspired by the driving presentation of *Spy Hunter*.
- The player's vehicle **faces and appears to drive upward**, positioned **toward the bottom of the driving playfield**.
- The **road and roadside scenery scroll downward** to convey forward travel.
- **Unrestricted side-to-side steering:** the car moves freely left or right, **not** between fixed discrete lanes. The playable environment has three distinct areas: road (normal handling and timer reset), shoulder (reduced traction; timer paused), and beyond-shoulder grass (timer runs toward a **2.0-second explosion threshold**; see Section 5.7).
- **Winding-road sequences** become **temporarily narrower** than the established **75%-of-driving-playfield straight-road baseline**, while the road center **weaves left and right**. Once a winding sequence ends, the road **widens back to its normal baseline width**. The **minimum narrowed width**, narrowing/expansion speed and curve severity are open for playtesting; do not assume 75% is maintained throughout winding sections.
- **Road forks are formed by a divider island that enters from the top of the road screen and scrolls downward through the center of the road**, splitting traffic around a **left branch** and a **right branch**, visually inspired by the supplied *Spy Hunter* screenshot. **Approximately 2 seconds before the island first appears on screen**, a **flashing green arrow pointing straight UP** appears **near the top of the driving playfield**, on the **left or right side** to identify the preferred branch. The arrow's **position**, not a rotated left/right arrowhead, signals which branch to take. **Taking the wrong fork does not instantly crash the car**: it wastes travel time, slows the miles-remaining countdown and allows pressure to keep building. Exact arrow flash cadence/disappearance, island dimensions, detour penalty and road rejoining remain open.
- Police cars and hazmat vans pursue, deliberately **bumping/PIT-style shoving** the player's car toward the road edge. **Four-sided car gas blasts** push these vehicles back. Diagonal blasting is possible but **unconfirmed**.
- Friends travel ahead, with their lead car **near the top of the driving playfield**.
- On road chases after the pharmacy, the friends drop **Gas-Nix**; pickups move down toward the player's car as the road scrolls.

**Confirmed driving-stage screen allocation and straight-road proportions:**
- **Left 2/3 of the total screen:** driving playfield, containing roadway, both roadside strips, traffic and hazards.
- **Right 1/3 of the total screen:** dedicated fixed **HUD/status panel**, with at minimum **lives**, **score**, **miles remaining to the next destination**, and **gas-pressure meter**. Miles decrease at a reduced rate on wrong-fork detours.
- For a **straight-road baseline**, percentages are of the **left driving playfield**, not the entire screen:
  - **Left grass: 6.25%**.
  - **Left shoulder: 6.25%**.
  - **Road: 75%**.
  - **Right shoulder: 6.25%**.
  - **Right grass: 6.25%**.
- As the road **winds left/right**, its center shifts within the left playfield **and the paved road temporarily narrows**. Local left/right roadside widths need **not** remain identical at each screen row. When the winding sequence ends, the road returns to its **75% normal straight-road width**. Center-island forks locally divide the road into branches. The HUD stays fixed at the right.
- **Each 12.5% roadside strip is divided evenly:** **6.25% shoulder adjacent to the roadway** and **6.25% grass farther out**. On the shoulder, handling is degraded and the grass timer **pauses**; reaching grass makes that timer **run/resume** toward two seconds. The **center of Billy's car** determines which zone it occupies at its current vertical position. Returning to the paved road **resets the timer to zero**. Compute concrete boundary coordinates from these approved percentages **after selecting the Atari graphics mode**; actual display-pixel locations remain open.
- Atari 800XL display mode, concrete screen-pixel allocations and HUD styling are still open; the percentages are game-design proportions rather than an approved memory/display-list implementation.

**Still open for driving:** precise display-pixel boundary coordinates and their graphics-mode-dependent representation (center-of-car classification is confirmed), **minimum width and transitions during winding/narrowed segments**, curve severity, center-island dimensions/fork generation and placement, arrow blink rate/when it disappears (its ~2-second lead relative to first island appearance and placement are confirmed), wrong-fork slowdown/detour tuning, restart/respawn after an off-road explosion, precise player vertical-position freedom, acceleration/braking, speed, enemy/traffic collisions, input mapping, gas-bomb controls, and whether the HUD includes lives or stage details. *Spy Hunter* is a perspective/gameplay reference, **not** a requirement to duplicate all its mechanics.

**Still open for indoor stages:** overhead maze versus side-view action. A single Atari joystick with one fire button is the expected hardware input, but the complete mapping is **not finalized**.

### 5.7 Off-road recovery, shoulder handling and two-second explosion — Confirmed

Applies to all driving stages (Stages 2, 4 and 6), including situations where pursuing police cars or hazmat vans shove the player sideways.

- **Zone-detection reference point:** Compare the **center of Billy's car** against the road/shoulder/grass boundaries at the car's current vertical position. Grass contact by an outer tire or sprite edge **does not start the timer** while the center remains on the shoulder or road. Applies to both left and right sides, straight sections, and winding sections.
- **Road:** Normal traction and steering. Entering the paved road **resets the off-road timer to zero** and clears its staged off-road warnings.
- **Shoulder:** Reduced traction/steering response, but the off-road timer **pauses** at its current elapsed value. Merely reaching the shoulder **does not clear or reset** the timer.
- **Grass beyond the shoulder:** Reduced control. The timer **runs or resumes** from its stored value. Upon reaching **2.0 accumulated seconds spent in grass since Billy was last on the paved road**, the car **explodes** and the player **loses one life**.
- **Recovery example:** After 1.3 seconds in grass, Billy moves onto the shoulder: the timer pauses at 1.3 seconds. Returning to grass resumes from 1.3; reaching the paved road resets it to 0. These are not cumulative off-road seconds across the entire stage—only across excursions **since the last paved-road recovery**.
- **Pixel boundaries:** Start with the approved **6.25% grass / 6.25% shoulder / 75% road / 6.25% shoulder / 6.25% grass** distribution inside the left driving 2/3. **Derive exact display-coordinate boundaries when the Atari graphics mode, playfield width, and car representation are selected**; the graphics mode is not currently final. On curves, classify the car center using the local road geometry rather than assuming one fixed straight-road x boundary.
- **Separate system:** The grass countdown is independent of the rising gastrointestinal gas-pressure meter and its 100% threshold.
- **Progressive on-screen/audio feedback** follows the accepted initial timing targets:

| Accumulated grass time since last paved-road recovery | Response |
|---|---|
| 0.0–0.5 s | Car starts skidding; correction is still possible. |
| 0.5–1.0 s | Car shakes; steering responsiveness decreases. |
| 1.0–1.5 s | Warning sound begins; smoke appears. |
| 1.5–2.0 s | Critical warning; smoke gets heavier. |
| 2.0 s | **Vehicle explosion and one-life penalty.** |

**Confirmed:** two-second grass threshold, loss of one life, **center-of-car grass detection**, safe-but-slippery shoulder **pausing** the timer, grass **running/resuming** it, paved-road **reset** to zero, harder grass steering, and progressive skid/shake/smoke/warning feedback. Warning bands are initial balance targets and may be tuned after playtesting.

**Not yet finalized:** exact **Atari display-pixel boundary coordinates** (dependent on graphics mode), how to represent/test the vehicle center in the selected sprite/graphics system, specific steering/traction percentages, other collision math, audio/animation details, and respawn/restart behavior after losing a life.

## 6. Player goals, failure and progression

**Confirmed:** get through the restaurant, pharmacy, grocery store and home sequence; manage gas pressure; reach the bathroom; finish four restaurant levels; repeat from Taco Smell.

**Confirmed:** **2.0 seconds of accumulated grass time since the last paved-road recovery** results in a car explosion and **one life lost**. Time on shoulder pauses the grass timer; reaching the paved road resets it.

**Open:** number of starting lives, continues, checkpoints, score, high-score table, bonus points, difficulty increases after looping, respawn after off-road explosions, and consequences of capture versus gas pressure reaching 100%.

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
| Main character | **Billy Blaster** (young male protagonist); exact introductory quote required within the game |
| Lead restaurant | **Taco Smell** (replaces early working name Taco Hell) |
| Level sequence | Taco Smell → Casa de Gas → The Bean Machine → The Blazing Burrito → repeat |
| Stage count | Nine per level **for now**; may be reduced |
| Pharmacy objective | **Gas-Nix gas relief**; not laxatives |
| Driving perspective | **Confirmed overhead/top-down**; car points upward near bottom of driving area; road scrolls downward; friends' car ahead near top; police pursue |
| Driving controls/roads | **Free lateral steering**; temporary road narrowing during weaving curves, returning to 75% normal width; timed off-road danger beyond shoulder; **center-island forks** with a **flashing green upward arrow** near top on left/right branch side **~2s before island first appears** |
| Off-road penalty | Classify using **center of car**; grass accumulates toward **2.0s** explosion/one-life loss; shoulder reduces traction and **pauses** timer; paved road **resets** timer; progressive skid/shake/smoke/audio warnings |
| Wrong fork | No automatic crash; a time-costly detour slows miles-to-go countdown while pressure keeps increasing |
| Road enemies / defense | Police cars and hazmat vans try to bump the player's car off-road; gas blasts from all **four sides** push vehicles away |
| Gas-blast prototype | **Four-way blasting selected for initial prototype** (front, rear, left, right); steering/aim input mapping still open |
| Diagonal gas blasts | Hardware supports 8-way joystick input; **future 8-way extension remains optional** |
| Driving screen layout | **Left 2/3** driving playfield; straight-road baseline (left to right) **6.25% grass / 6.25% shoulder / 75% road / 6.25% shoulder / 6.25% grass**; **right 1/3** fixed HUD for lives, score, miles remaining, and gas meter; road centers can shift in curves/forks |
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
7. **Driving details:** What graphics-mode-dependent pixel coordinates and sprite center representation should we use to implement the confirmed zone rules, and how does respawning after a timed off-road explosion work; how narrow should winding roads become and how quickly should they widen; what flash cadence/disappearance should green arrows use (with a ~2s pre-island appearance confirmed); what center-island size and collision behavior should forks use; how slow does mileage fall on wrong-fork detours, and how/when do they rejoin; what steering, collision/ramming impulse, gas-blast knockback and pickup rules apply?
8. **Blaster controls:** how should four-way gas blast aiming coexist with steering on one joystick and Fire button? Evaluate possible diagonal extension only after the prototype.
9. **Progression:** how do restaurants/cycles become visually and mechanically distinct?
10. **Score/lives:** scoring, bonuses, and continuation rules.
11. **Intro implementation:** where and how should Billy Blaster's required introduction appear in-game without changing its wording?
12. **Hardware plan:** graphics, sound, memory, development and testing.

## 10. Change log

- **v0.12 — 2026-10-26:** Confirms center-of-car grass detection, shoulder pauses the off-road timer, grass runs/resumes it, and paved road resets it; two seconds of grass exposure since last paved-road recovery costs one life. Pixel boundaries to be derived from approved percentages when graphics mode is selected; no mode/pixel values chosen.
- **v0.11 — 2026-10-26:** Confirms narrowed winding-road stretches that weave and widen back to the 75% baseline; fork splits via center divider island; blinking **green upward-pointing** route arrow near top on preferred left/right side starts roughly 2 seconds **before the island first appears**. Minimum winding width, arrow blink cadence and island dimensions remain open.
- **v0.10 — 2026-10-26:** Confirms each straight-road roadside strip is divided into 6.25% shoulder next to pavement and 6.25% grass beyond, measured as fractions of the left driving playfield. Grass triggers the two-second danger timer; car-overlap detection and behavior on partial shoulder recovery remain open.
- **v0.9 — 2026-10-26:** Confirms left two-thirds driving area with 75% road and 12.5% combined shoulder/grass on each side for straight segments; fixes HUD in right third and adds lives to score/miles/gas. Curves and forks may shift the road; precise shoulder/grass split and collision boundaries remain open.
- **v0.8 — 2026-10-26:** Approves two-second continuous off-road countdown, safe but low-traction shoulder, progressive skid/shake/smoke/audio cues, reset on safe return to road, and car explosion costing one life. Road/shoulder geometry and respawn remain open.
- **v0.7 — 2026-10-25:** Confirms the protagonist's name as Billy Blaster and requires the exact introductory line to appear in-game, with presentation/placement to be determined.
- **v0.6 — 2026-10-25:** Selects four-direction vehicle gas blasting for the first prototype; diagonal blasting remains an optional later experiment. Records that the main character has not yet been named.
- **v0.5 — 2026-10-25:** Wrong fork becomes detour: miles count down slower while gas builds, with no automatic crash. Police cars and hazmat vans attempt to force the player off-road; four-sided gas blasts knock enemies away. Atari joystick can detect eight directions, but adding diagonal blasts and mapping aiming to one stick remain design decisions.
- **v0.4 — 2026-10-25:** Confirms road-fork arrow appears near the top of the screen, blinks, and warns the player a few seconds before the road divides. Exact lead time, blink rate, and wrong-fork consequences remain open.
- **v0.3 — 2026-10-25:** Confirms unrestricted horizontal steering, off-road crash threshold, winding roads and two-way forks with direction arrows; reserves two-thirds of driving screen for roadway and one-third for gas meter, miles to destination, score and other HUD information. HUD placement and detailed rules remain open.
- **v0.2 — 2026-10-25:** Confirms Spy Hunter-style overhead driving for Stages 2, 4, and 6: upward-facing player car near bottom, downward-scrolling road, lead friends' car near top, pursuing police, and falling Gas-Nix pickups on later drives. Lane and control details remain open.
- **v0.1 — 2026-10-25:** Initial documented concept. Establishes four restaurants, provisional nine stages each, loop after Level 4, Gas-Nix replacing laxatives, first drive racing a rising meter, later drives collecting Gas-Nix from friends, and the bathroom objective.
