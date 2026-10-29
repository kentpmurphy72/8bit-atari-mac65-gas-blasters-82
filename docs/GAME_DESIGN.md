# Gas Blasters '82 — Game Design Document

**Version:** 0.22  
**Date:** 2026-10-29  
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

**Confirmed introduction scope and placement (current design):** After the player selects **1 PLAYER / starts the game**, show **one static introductory screen — Screen 1: “Meet the Crew.”** It features **Billy Blaster prominently in the center** with his four friends around him, along with the complete required introductory line above. The existing arcade-style Version 2 artwork is the **visual reference**, not a finalized Atari bitmap or production asset; names on that concept art (Dave, Tracy, Mike, Jen) remain **placeholders**, not confirmed character names.

**Updated opening flow:** **Title Screen (selected title Option 3)** / 1 PLAYER start → **“Meet the Crew” intro (tested standalone v4 proof of concept)** → **“Arriving at Taco Smell” still image (selected arrival Option 3)** → **Stage 1: Taco Smell restaurant escape**. The title screen is distinct from both cutscenes. Its previously selected design retains the GAS BLASTERS '82 logo, purple/orange sunset, Billy in his red car, green gas trail and TACO SMELL sign with **1 PLAYER / PRESS START**. **The new arrival image is a second, separate scene:** Billy and the same four friends walk from their parked car across the parking area toward Taco Smell's lit entrance. The **medium-detail, third arrival concept** is selected as its visual target, with recognizable crew outfits (Billy's red cap/plaid jacket and taco T-shirt), a parked car at left, sunset/trees, and a readable Taco Smell sign/building at right. Treat the arrival as a static illustration following the crew introduction; do **not** require a dinner-table cutscene. The previously deferred parking-lot idea is now **back in scope**, superseding the older one-screen-only flow. The **original Billy Blaster introduction quote stays on Meet the Crew**; the **arrival screen instead displays a separate approved three-line burrito/beans warning** (below). These pre-game images are not intended to repeat every level loop. The arrival scene now has a **standalone ANTIC E + DLI XEX visually tested by the user in Atari 800 Emulator 5.2.0 on 2026-10-29**. This proves the particular standalone scene renders in that emulator, **not** that the complete title-to-game sequence or graphics architecture is implemented.

**Presentation and implementation notes:** Display the **exact quote in-game** without altering its wording, punctuation or sequence; use readable text lines/area on that **same single intro screen** as needed for Atari limitations.

**Current Screen 1 prototype — tested in Atari 800 emulator on 2026-10-28:** The user loaded and visually inspected the latest **“Meet the Crew” v4 clean-text XEX**, using a **mixed ANTIC E bitmap + 40-column text treatment and DLI color bands**. The image now **omits the GAS BLASTERS '82 logo and background TACO SMELL roadside sign**, since those belong on the **separate title screen**, and **removes the placeholder name labels beneath the five characters**. Billy remains centered, surrounded by four friends; the sunset, cars and setting remain, and Billy's Taco Smell T-shirt is part of his established outfit. The **“MEET THE CREW” heading was moved lower**, with a separate caption area and a **FIRE TO CONTINUE** prompt. The screenshot shows the scene rendered in the emulator, but **the caption lettering, alignment/spacing and general readability still need another polish pass**, intentionally deferred while core game design continues. The user described the visual result as acceptable for now (“doesn't look bad”).

**Approved arrival-screen story text (exact three-line version; each line at most 40 columns):**

> Billy came for a killer burrito.
> The beans came with a warning.
> Nobody read it. Especially Billy.

**Arrival-screen prototype — emulator-tested 2026-10-29:** The user loaded the **v3 three-line arrival XEX** in **Atari 800 Emulator v5.2.0**, inspected the result and responded **“looks good.”** This standalone screen uses **160×128 ANTIC E 2-bit artwork** of Billy and the four friends approaching Taco Smell, followed by **eight 40-column ANTIC mode 2 text rows** (64 scanlines). The layout is one blank row, **ARRIVING AT TACO SMELL** heading, one blank row, the exact three story lines (32/30/33 characters, each indented four columns), one blank row, and a centered **FIRE TO CONTINUE >** prompt. There are **12 sixteen-scanline palette bands / 11 DLIs** in the prototype. This is a visual approval for the standalone arrival scene only, not a final engine choice. The on-screen FIRE prompt **does not yet respond to input**. The tested **v3 XEX, full-resolution source artwork, native 2bpp image, palette tables, text rows, display list, custom font and preview** are versioned under [`assets/arrival/`](../assets/arrival/), with a reproducible build script in [`tools/build_arrival_screen.py`](../tools/build_arrival_screen.py).

**Not yet complete:** The XEX is a **standalone visual proof of concept**; the **FIRE TO CONTINUE** prompt has not been wired to actual input/scene advance, the selected title screen and restaurant gameplay are not connected, and the final graphics mode/palette, font, memory/loading plan and timing have not been adopted as production architecture. The tested **Meet the Crew v4** executable and native artwork/build data are checked in under [`assets/intro/`](../assets/intro/), with its build script in [`tools/build_clean_intro.py`](../tools/build_clean_intro.py). Both build scripts have been verified to reproduce their corresponding tested XEX files byte-for-byte, but that does **not** make the noninteractive prototypes production-ready. The exact quote remains required in the finished game.


### Stage 1 — Restaurant escape

The player and friends have eaten a huge meal at the current level's restaurant. An apparent gas leak is traced to the player, and a hazmat team arrives. The player's objective is to escape the building using movement, evasion and secret gas powers.

**Confirmed:** friends are part of the restaurant outing; hazmat personnel try to catch the player; the player escapes toward a car.  
**Open:** perspective (top-down/maze or side-view), floor plan, enemy patterns, and how gas attacks operate.

### Stage 2 — First road chase: race to the pharmacy

Two cars leave the restaurant: the player's car and a separate car driven by friends. Police pursue the player. **The view is overhead, with the player's car pointing upward near the bottom of the screen as the road scrolls downward** (see Section 5.6).

**Confirmed mechanic:** the gas meter begins **near 0%**, then steadily rises as the player heads toward the pharmacy. The player must reach the pharmacy **before the meter reaches 100%**, the explosion threshold.

**Important:** Gas-Nix is **not yet available**. Friends do **not** drop Gas-Nix on this first drive, because it has not been acquired yet.

**Confirmed road features:** free left/right steering, winding road, occasional two-way fork with an on-screen arrow indicating the intended route, and recoverable shoulder/off-road driving with a **2.0-second off-road countdown** before an explosion costs one life. Driving uses approximately two-thirds of the screen; a separate one-third HUD shows gas pressure, distance in miles to the next destination, score, and other necessary indicators.

**Confirmed:** If the player takes the **wrong fork**, it is a **detour, not an immediate crash**. **Add exactly 1.0 mile once** to the HUD miles-remaining value when Billy commits to the wrong branch. The miles counter then decreases at its **normal rate**—there is **no additional slowdown**. **Gas pressure continues rising** throughout the extra travel. The branches **automatically merge back into one road relatively soon after the fork**, returning to the **normal 75%-width roadway** rather than keeping Billy on a visually separate branch for the whole added mile. The extra mile is a **remaining-distance penalty**, not a requirement to display an entire one-mile stretch of separate roadway. The exact on-screen merge distance/timing remains a prototype-tuning detail. Police cars and hazmat vans intentionally try to **ram/PIT-style shove** the player off the road; grass entry starts/resumes the same **2.0-second timer**, not an instant crash. Billy can use **gas blasts from all four sides of the car** to push pursuing vehicles away.

**Open:** road travel speed and how game miles map to elapsed time, exact **visual merge timing/geometry** after a fork, gas growth rate, exact outcome of a **100% gas-pressure explosion** (distinct from off-road failure), respawn after an off-road explosion, and blast duration/knockback tuning (the four-way hold-Fire driving controls are confirmed). The wrong-turn penalty is **confirmed at +1.0 mile only**, with normal countdown speed.

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

### 5.3 Gas-blasting abilities — Four-way window blasts and one-joystick controls confirmed

Billy has secret gas powers to evade hazmat personnel and police. **Driving stages use exactly four gas-blast directions: front, rear, left and right** (no diagonal blasts in the current design). The vehicle's front, rear and side windows are the gag's natural blast outlets. A blast knocks pursuing police cars and hazmat vans away from Billy's car, helping counter intentional ramming and off-road shoves.

**Confirmed one-button joystick control scheme for road stages:**
- **Fire released:** joystick controls normal steering.
- **Hold Fire:** switch to **gas-blast mode**. While Fire is held, the joystick **does not steer the car**. The vehicle keeps moving/coasting forward along the scrolling roadway, and hazards continue normally.
- **Hold Fire + Up:** gas blast out the **front** window.
- **Hold Fire + Down:** gas blast out the **rear** window.
- **Hold Fire + Left:** gas blast out the **left-side** window.
- **Hold Fire + Right:** gas blast out the **right-side** window.
- **Release Fire:** return to normal steering. This intentional choice between **steering and defending** is part of the gameplay.

**Confirmed visual gag:** each directional blast briefly shows a **jeans-covered backside sticking out of the corresponding window/edge of the car**, followed by a **gas cloud emanating from the backside** in the selected cardinal direction. The butt and cloud should be comedic, readable from the top-down Atari perspective, and kept visually clear even for the front-window blast. A simple pop-out pose and cloud burst are the initial art direction, not a requirement for detailed anatomy.

**Scope decisions:** four-way blasting is the chosen design, not merely a temporary step toward eight-way. **No diagonal blast mechanics or art are planned.** The Atari joystick can physically register diagonal inputs, but that does **not** imply diagonal attacks; how to resolve simultaneous direction inputs in blast mode is a small implementation/test detail. A **second joystick dedicated to blasting is deferred**; start with one joystick and one Fire button. Either idea may be revisited only if later playtesting justifies a deliberate change.

**Still open for prototype tuning:** responsiveness/feel while unable to steer, blast duration and repetition while holding Fire, range, cooldown, strength and enemy knockback; sprite placement, animation frame count, cloud appearance and memory budget; interactions with player gas pressure and Gas-Nix; and indoor-stage blast controls/effects.

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
- **Winding-road sequences:** the paved roadway gradually narrows from the **normal 75% width** to **40% of the driving playfield** over **approximately 4 seconds** of gameplay while the road weaves left/right. It may remain at or near 40% during the winding stretch (duration still open); when the winding section ends, it **gradually widens from 40% back to 75% over approximately 4 seconds**. The **6.25%-wide shoulders remain constant on both sides of the road**; the remaining roadside width is grass. With the narrow road centered, the cross-section is **23.75% grass / 6.25% shoulder / 40% road / 6.25% shoulder / 23.75% grass**. The 4-second transitions and 40% minimum are **approved initial design targets** to validate through prototype playtesting.
- **Road forks are formed by a divider island that enters from the top of the road screen and scrolls downward through the center of the road**, splitting traffic around a **left branch** and a **right branch**, visually inspired by the supplied *Spy Hunter* screenshot. **Approximately 2 seconds before the island first appears on screen**, a **flashing green arrow pointing straight UP** appears **near the top of the driving playfield**, on the **left or right side** to identify the preferred branch. The arrow's **position**, not a rotated left/right arrowhead, signals which branch to take. The arrow initially shows **ON for 0.25 seconds**, then **OFF for 0.25 seconds**, repeating (a **0.5-second blink cycle**, or **2 flashes/second**). It stays near the top of the driving playfield and **continues flashing after the island first appears**, disappearing **once Billy passes the fork's decision point**. **Taking the wrong fork does not instantly crash the car**: it **adds exactly 1.0 mile once** to the HUD distance remaining, after which miles count down at the **normal rate** while pressure keeps rising. The divided roadway **automatically merges back soon after the fork into a single normal-width (75%) road**, well before Billy has driven the extra mile; the penalty is on the destination distance, **not** the length of the visually split road. Exact merge timing/geometry remain for prototype tuning. Exact pixel coordinates, frame counts for the chosen video system, and the geometry/test defining passage beyond the fork decision point remain technical/prototype work; island dimensions are also open.
- Police cars and hazmat vans pursue, deliberately **bumping/PIT-style shoving** the player's car toward the road edge. **Four-direction gas blasts only** push these vehicles back: **hold Fire + Up/Down/Left/Right** to blast front/rear/left/right. **Steering is suspended while Fire is held**; the car continues/coasts forward. Each blast shows a **jeans-clad backside protruding from that window** with a gas cloud emanating from it.
- Friends travel ahead, with their lead car **near the top of the driving playfield**.
- On road chases after the pharmacy, the friends drop **Gas-Nix**; pickups move down toward the player's car as the road scrolls.

**Confirmed driving-stage screen allocation and straight-road proportions:**
- **Left 2/3 of the total screen:** driving playfield, containing roadway, both roadside strips, traffic and hazards.
- **Right 1/3 of the total screen:** dedicated fixed **HUD/status panel**, with at minimum **lives**, **score**, **miles remaining to the next destination**, and **gas-pressure meter**. A wrong fork **adds 1.0 mile once** to miles remaining; afterward miles decrease at the **normal rate**.
- For a **straight-road baseline**, percentages are of the **left driving playfield**, not the entire screen:
  - **Left grass: 6.25%**.
  - **Left shoulder: 6.25%**.
  - **Road: 75%**.
  - **Right shoulder: 6.25%**.
  - **Right grass: 6.25%**.
- As the road **winds left/right**, its center shifts within the left playfield while width decreases from **75% to 40% in ~4 seconds**, then widens **40% to 75% in ~4 seconds** as the winding ends. At the 40% minimum the shoulders remain **6.25% each**, and grass occupies the remaining **23.75% per side when centered**. Because the road weaves, actual left/right grass strips may differ; preserve shoulders adjacent to the changing road edges. Center-island forks locally divide the road into branches. The HUD stays fixed at the right.
- **Each 12.5% roadside strip is divided evenly:** **6.25% shoulder adjacent to the roadway** and **6.25% grass farther out**. On the shoulder, handling is degraded and the grass timer **pauses**; reaching grass makes that timer **run/resume** toward two seconds. The **center of Billy's car** determines which zone it occupies at its current vertical position. Returning to the paved road **resets the timer to zero**. Compute concrete boundary coordinates from these approved percentages **after selecting the Atari graphics mode**; actual display-pixel locations remain open.
- Atari 800XL display mode, concrete screen-pixel allocations and HUD styling are still open; the percentages are game-design proportions rather than an approved memory/display-list implementation.

**Still open for driving:** precise display-pixel boundary coordinates and their graphics-mode-dependent representation (center-of-car classification is confirmed), **playtesting/adjustment of the approved 40%-minimum and ~4-second narrowing/widening**, duration of winding sections at minimum width, curve severity, center-island dimensions/fork generation and placement, precise arrow pixel placement, frame timing and detecting passage beyond the confirmed decision-point disappearance trigger (~2-second lead, 0.25s ON/OFF cadence and disappearance rule are confirmed), wrong-fork merge timing/visual geometry (the +1.0-mile one-time penalty and normal countdown speed are confirmed), restart/respawn after an off-road explosion, precise player vertical-position freedom, acceleration/braking, speed, enemy/traffic collisions, blast-mode feel and timing (hold-Fire mapping is confirmed), gas-blast range/cooldown/knockback, and whether the HUD includes additional stage details. *Spy Hunter* is a perspective/gameplay reference, **not** a requirement to duplicate all its mechanics.

**Still open for indoor stages:** overhead maze versus side-view action and indoor joystick/Fire mapping. **Road-stage hold-Fire-to-blast mapping is confirmed**, with no steering while Fire is held.

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
| Title-screen art direction | **Selected Option 3 (third/latest ANTIC E + DLIs concept):** blocky Atari-style illustrated logo, sunset/skyline, Billy smiling in red car from front three-quarter view, green gas trail, Taco Smell roadside sign and bottom **1 PLAYER / PRESS START** menu. A visual target; hardware conversion and runnable screen remain open |
| Opening sequence | After title/1 PLAYER start: **Meet the Crew** (original exact Billy quote), then **Arriving at Taco Smell** (approved medium-detail scene with separate three-line warning text, standalone v3 XEX emulator-tested), then **Stage 1**. **Dinner-table screen deferred** |
| Intro proof of concept (not completed game integration) | **Meet the Crew v4 standalone XEX** tested in Atari emulator (font cleanup deferred). **Arrival v3 standalone 160×128 ANTIC E + eight 40-column text rows XEX** tested 2026-10-29 and visually accepted, with exact three-line burrito warning. **Both FIRE TO CONTINUE prompts are display-only**; scenes not yet linked to each other or Stage 1. **Both tested XEX binaries and original artwork are committed** under `assets/intro/` and `assets/arrival/`, with build tools under `tools/` |
| Lead restaurant | **Taco Smell** (replaces early working name Taco Hell) |
| Level sequence | Taco Smell → Casa de Gas → The Bean Machine → The Blazing Burrito → repeat |
| Stage count | Nine per level **for now**; may be reduced |
| Pharmacy objective | **Gas-Nix gas relief**; not laxatives |
| Driving perspective | **Confirmed overhead/top-down**; car points upward near bottom of driving area; road scrolls downward; friends' car ahead near top; police pursue |
| Driving controls/roads | **Free lateral steering**; weaving roadway narrows **75% → 40% over ~4s**, restores **40% → 75% over ~4s**, shoulders stay **6.25% wide** on each side; timed grass danger; **center-island forks** with green upward arrow on preferred side **~2s before island first appears**, blinking **0.25s ON / 0.25s OFF** until Billy passes the fork decision point |
| Off-road penalty | Classify using **center of car**; grass accumulates toward **2.0s** explosion/one-life loss; shoulder reduces traction and **pauses** timer; paved road **resets** timer; progressive skid/shake/smoke/audio warnings |
| Wrong fork | No automatic crash; **add +1.0 mile once** to remaining distance on wrong branch; resume **normal countdown rate** with gas pressure still rising; branches automatically **merge soon into one 75%-width road**, independent of the added mile |
| Road enemies / defense | Police cars and hazmat vans try to bump the player's car off-road; gas blasts from all **four sides** push vehicles away |
| Gas-blast driving controls | **Four-way only:** joystick steers when Fire released; **hold Fire + Up/Down/Left/Right** for front/rear/left/right blast; **no steering while Fire held**, car coasts forward |
| Gas-blast visual | **Jeans-covered backside briefly protrudes from the matching car window**; greenish gas cloud emanates from it and knocks enemies back; exact sprite/FX details await art and prototype |
| Diagonal/two-joystick options | **Not planned** for the current design; may be deliberately reconsidered later if tests warrant |
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
7. **Driving details:** What graphics-mode-dependent pixel coordinates and sprite center representation should we use to implement the confirmed zone rules, and how does respawning after a timed off-road explosion work; how will the **40% minimum width and four-second narrowing/widening** perform in prototype testing, and how long should a winding section remain narrow; how do we translate the confirmed ~2s pre-island arrow, 0.25s ON/OFF flashes and decision-point disappearance into display-frame counts, exact coordinates and a measurable fork decision boundary; what center-island size and collision behavior should forks use; how soon and with what visual geometry should the fork branches merge back into one normal-width road, with the +1.0-mile one-time penalty and unchanged countdown rate already confirmed; what steering, collision/ramming impulse, gas-blast knockback and pickup rules apply?
8. **Blaster implementation:** test the confirmed **hold-Fire + cardinal direction** blast mode (steering disabled, car coasts), settle diagonal joystick-input handling without diagonal attacks, blast cadence/range/knockback, and jeans-clad backside/window/cloud sprite readability. Indoor gas mechanics remain open.
9. **Progression:** how do restaurants/cycles become visually and mechanically distinct?
10. **Score/lives:** scoring, bonuses, and continuation rules.
11. **Title and opening-sequence implementation:** the **Option 3 Atari-inspired title**, the **Meet the Crew quote screen**, and the **medium-detail Taco Smell arrival screen** are separate approved scenes. **Both intro stills have been displayed from standalone XEX files in the Atari emulator**, with the **arrival v3 three-line text and 160×128 ANTIC E / eight 40-column-row layout visually accepted on 2026-10-29**. The crew v4 font legibility still needs later cleanup. Next implement the title's **1 PLAYER / PRESS START** control, wire the actual **FIRE TO CONTINUE** inputs, load the two scenes in sequence and transition into Stage 1. Validate the integrated pipeline and refine fonts/graphics as needed. The dinner-table cutscene is out of scope.
12. **Hardware plan:** graphics, sound, memory, development and testing.

## 10. Change log

- **v0.22 — 2026-10-29:** Commits both approved **standalone emulator-tested screen packages** to the repo, including `assets/intro/meet_the_crew_v4.xex` and `assets/arrival/arrival_v3.xex`, each original full-resolution PNG and native Atari art/charset/text/palette/DLI/preview data. Adds reproducible build scripts under `tools/`; both scripts were checked locally to regenerate the exact tested XEX bytes. No Fire handling or full-game scene integration added; existing task completion counts unchanged.
- **v0.21 — 2026-10-29:** Records user-tested and visually accepted **Taco Smell arrival v3 standalone XEX** (Atari 800 Emulator 5.2.0). Uses **160×128 ANTIC E artwork + eight 40-column text rows**, **12 palette bands/11 DLIs**, heading and static Fire prompt. Confirms exact **three-line** story: “Billy came for a killer burrito.” / “The beans came with a warning.” / “Nobody read it. Especially Billy.” Hardware-specific screen prototype only; no Fire input, full-game integration or GitHub binary commit implied. Meet the Crew v4's text polish remains deferred.
- **v0.20 — 2026-10-28:** Reintroduces **one Taco Smell arrival still** after Meet the Crew and before Stage 1, selecting the **third, medium-detail arrival concept** (all five friends walking from their parked car to the lit Taco Smell entrance at sunset). The prior "directly to Stage 1" rule is superseded; the dinner-table scene remains deferred. True ANTIC E+DLI conversion, standalone XEX and emulator testing are still open; title-screen Option 3 is a separate art choice.
- **v0.19 — 2026-10-28:** Records user-tested **“Meet the Crew” v4 standalone ANTIC E + DLI mixed graphics/text XEX**. Logo, background Taco Smell sign and placeholder character-name labels removed; heading moved below artwork with quote and FIRE TO CONTINUE beneath. User accepts visual as a working draft but **caption typography/spacing remain to be refined later**. No game integration, working Fire button, or repository asset upload implied; title-screen Option 3 remains a separate choice.
- **v0.18 — 2026-10-28:** Selects **Option 3, the third middle-ground Atari-inspired title-screen composition** from the ANTIC E + DLIs concept review: large logo, purple/orange sunset, Billy in a red front three-quarter-view car with thumbs-up, green gas trail, Taco Smell sign and 1 PLAYER / PRESS START. Separate from the one-screen Meet the Crew introduction. Selection is a visual/design decision; native Atari bitmap conversion, DLI timings and title controls remain implementation work.
- **v0.17 — 2026-10-28:** Confirms a **single** post–1 PLAYER introductory screen featuring Billy centered with his crew and the exact approved quote, followed directly by the Taco Smell restaurant-escape stage. Defers earlier parking-lot (Screen 2) and dinner-table (Screen 3) cutscene ideas, without permanently rejecting them. Version 2 illustration remains art direction; ANTIC E XEX has been user-launched but production technique and controls remain open.
- **v0.16 — 2026-10-27:** Selects four-way car gas blasting as the current design with no diagonal attacks, confirms one-joystick **hold Fire + Up/Down/Left/Right** blast mode that suspends steering while car coasts, and approves a brief jeans-clad backside popping out the selected car window with gas cloud emanating from it. Two-joystick control is deferred; exact visual implementation and blast tuning remain prototype work. Historical diagonal-evaluation proposals below are superseded.
- **v0.15 — 2026-10-27:** Replaces the earlier wrong-fork mileage slowdown with a **one-time +1.0-mile remaining-distance penalty** when the wrong branch is chosen; normal countdown speed resumes while gas pressure continues rising. Fork branches automatically merge back relatively soon into a single normal 75%-width road, **before the extra mile is traveled**. Exact visual merge timing/geometry left to prototype. Earlier v0.5 slowdown descriptions below are historical, superseded by this version.
- **v0.14 — 2026-10-26:** Approves green fork-arrow flash cadence (0.25s ON / 0.25s OFF), continuing through island approach until Billy passes the fork decision point; retains arrow start ~2 seconds before island first enters screen. Defers pixel positions, frame-based timing and physical decision-point coordinates to architecture/prototype.
- **v0.13 — 2026-10-26:** Confirms winding roads narrow 75% → 40% over approximately four seconds and widen back 40% → 75% over approximately four seconds; fixed 6.25% shoulders, 23.75% grass per side at the centered minimum. These are approved targets pending prototype validation, not implemented behavior.
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
