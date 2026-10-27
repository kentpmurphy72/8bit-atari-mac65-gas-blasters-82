# Gas Blasters '82 — Project To-Do List

**Version:** 0.13  
**Date:** 2026-10-26  
**Target:** Atari 800XL  
**Status:** Planning and early design  
**Companion documents:** [Game Design](GAME_DESIGN.md) · [Art Assets](ART_ASSETS.md)

> Living checklist. An unchecked item is not necessarily an approved requirement; some items are proposed work that depends on design decisions. Update this file as tasks are finished or scope changes.

## Status update — 2026-10-26 (following 2026-10-25 audit)

- **32 of 150 checklist items completed (21%).** Another **118 remain open**. Grass entry is detected by **Billy's car center**; grass time **runs/resumes**, shoulder time **pauses**, and return to paved road **resets** the two-second timer. Percent-based zone widths are approved; exact pixel boundaries remain to be derived after graphics-mode selection. These are documented design rules, not implemented code.
- **Phase totals:** Game Design 26/45; Technical Architecture 3/14; First Playable Prototype 0/25; Indoor Gameplay 0/12; Graphics & Animation 3/16; Sound & Music 0/10; Build All Four Levels 0/10; Testing & Release 0/12; Ongoing Maintenance 0/6.
- **Evidence reviewed:** current Game Design and Art Assets documents, repository files and available commit history. The repository contains the foundational design files and initial directory structure, but does not yet contain a committed playable game implementation.
- **Still empty:** `AGENTS.md` and `docs/TECHNICAL_DESIGN.md`; do not mark them complete merely because the files exist.
- **Partially specified, not complete:** four-way gas blast behavior is agreed upon for road stages, but the single-joystick control mapping and indoor blast behavior are open; the indoor camera, HUD placement, gameplay failure handling, and final art are also not decided.
- **Ongoing maintenance checkboxes remain open intentionally:** documentation updates to date do not make recurring maintenance tasks permanently finished.

This audit preserves the existing checked states and should not be interpreted as proof that emulator or physical hardware testing has taken place.

## Phase 1 — Game Design
*Goal: Finalize the fundamental gameplay rules.*

- [x] Establish game concept and storyline.
- [x] Select four restaurant levels: Taco Smell, Casa de Gas, The Bean Machine, and The Blazing Burrito.
- [x] Establish the provisional nine-stage sequence per restaurant.
- [x] Define four-level progression with continuous looping.
- [x] Establish Gas-Nix as the gas-relief medicine.
- [x] Define the first road chase's rising gas-pressure mechanic.
- [x] Define Gas-Nix pickups dropped by friends on later road stages.
- [x] Confirm overhead, upward-facing-car, downward-scrolling-road perspective for driving stages (Spy Hunter-style).
- [x] Confirm unrestricted left/right steering, rather than fixed lanes.
- [x] Confirm winding roads and occasional two-way forks with on-screen direction arrows.
- [x] Confirm winding sections **temporarily narrow while weaving** and **restore normal 75% width** afterward.
- [x] Confirm forks form around a **center divider island** which scrolls downward from the top.
- [x] Confirm that driving too far off the road causes a crash.
- [x] Confirm driving-stage screen allocation: 2/3 road/playfield and 1/3 status HUD (gas, miles to destination, score).
- [x] Confirm 2.0-second continuous off-road limit, safe low-traction shoulder, warnings, return-to-road reset, explosion and one-life loss.
- [x] Confirm straight-road width: left 2/3 driving playfield containing 75% roadway and 12.5% combined shoulder/grass on **each side**; winding roads/forks can alter local margins.
- [x] Confirm each roadside strip consists of **6.25% shoulder next to the road and 6.25% outer grass** (fractions of the left driving playfield); grass is the two-second crash-danger zone.
- [x] Confirm **car-center zone detection**, **grass timer runs/resumes**, **shoulder pauses** at current value and **paved road resets** timer to zero.
- [ ] Choose Atari graphics mode and derive **exact pixel boundaries** from the approved 6.25% / 6.25% / 75% / 6.25% / 6.25% proportions; implement car-center checks at each roadway cross-section.
- [ ] Decide **minimum roadway width** and transition speed for winding/narrowed sections, then validate in the prototype.
- [x] Confirm a **flashing GREEN arrow pointing UP**, appearing **near the top of the driving area** on the **left or right side** to indicate preferred fork; start flashing **~2 seconds before the center island first appears**.
- [ ] Tune flashing-green-arrow blink cadence/disappearance and precise pixel timing around the confirmed ~2-second pre-island warning.
- [x] Confirm wrong forks incur slower miles countdown and continued rising gas pressure, rather than an immediate crash.
- [x] Confirm police cars and hazmat vans attempt to bump/PIT-style force the car off the road.
- [x] Confirm gas blasts from the front, rear, left and right push enemy vehicles away.
- [ ] Set wrong-fork slowdown/detour length and rejoining behavior.
- [x] Select four-direction gas blasting for the initial driving prototype.
- [ ] Evaluate eight-direction blasting only after playtesting the four-way prototype.
- [ ] Design one-button joystick steering-versus-gas-aiming controls and prototype usability.
- [ ] Determine car-to-car collision impulse, recovery window, and gas-blast knockback behavior.
- [x] Fix the HUD in the **right third** of the driving screen; include lives, score, miles remaining and gas meter.
- [ ] Determine exact pixel dimensions, graphics mode and HUD presentation.
- [x] Choose a name for the main character: **Billy Blaster**.
- [x] Approve Billy Blaster's introductory line (exact wording captured in GAME_DESIGN.md).
- [ ] Decide where and how to show Billy Blaster's required introduction within the game.
- [ ] Choose overhead or side-view gameplay for indoor stages.
- [ ] Define player movement and joystick/fire-button controls.
- [ ] Define how gas blasts work against enemies.
- [ ] Determine whether using gas powers reduces gas pressure.
- [ ] Define gas-pressure behavior inside buildings.
- [ ] Define exactly what happens when gas pressure reaches 100%.
- [ ] Determine lives, scoring, bonuses, and high-score rules.
- [ ] Finalize stage completion and failure conditions.
- [ ] Determine how difficulty increases across restaurants and repeated cycles.
- [ ] Review the nine stages and decide whether any should be combined or eliminated.

## Phase 2 — Technical Architecture
*Goal: Establish how we'll develop the game for the Atari 800XL.*

- [x] Create the GitHub repository and initial folder structure.
- [x] Create Game Design Document v0.1.
- [x] Create Art Assets Document v0.1.
- [ ] Configure and document the MAC/65 assembly development environment.
- [ ] Select emulator and debugging tools.
- [ ] Establish the assembly, build, and execution workflow.
- [ ] Decide on cartridge, disk, or other distribution format.
- [ ] Select Atari graphics modes and screen layouts.
- [ ] Develop a preliminary memory map and allocation strategy.
- [ ] Determine how player/missile graphics will be used.
- [ ] Define the game's main loop, input handling, timing, and collision architecture.
- [ ] Establish a reusable stage/level data structure.
- [ ] Complete `TECHNICAL_DESIGN.md`.
- [ ] Populate `AGENTS.md` with instructions for Codex.

## Phase 3 — First Playable Prototype
*Goal: Prove that the central game mechanic is fun.*

**Recommended starting point: Stage 2 — First Road Chase.**

- [ ] Display a basic overhead roadway scrolling downward.
- [ ] Implement continuous side-to-side steering (no fixed-lane snapping).
- [ ] Implement three zones with baseline widths: 75% normal road, 6.25% low-traction shoulder per side and 6.25% grass per side; classify by **car center** using the road edges at the player's current vertical position.
- [ ] Implement **grass time runs/resumes / shoulder time pauses / paved-road time resets** behavior; at 2.0s accumulated grass time since last road recovery, explode and deduct one life.
- [ ] Implement staged skid, shake/reduced steering, warning/smoke, critical warning/heavy smoke.
- [ ] Prototype narrowed roads weaving left/right, then **widening back to the normal 75% baseline width**.
- [ ] Prototype a **scrolling center-divider island** that creates left/right branches, with a **flashing GREEN upward arrow near top on the preferred side** beginning ~2 seconds before the island first appears.
- [ ] Implement a wrong-fork detour with miles counting down more slowly while gas pressure continues rising.
- [ ] Draw the player's car facing upward near the bottom of the screen.
- [ ] Implement joystick steering.
- [ ] Add police cars and basic collision detection.
- [ ] Add hazmat vans and enemy lateral ramming/forced-off-road behavior.
- [ ] Implement directional gas blast knockback on all four sides of the player's car.
- [ ] Test the four-direction aiming-versus-steering control scheme on a one-button joystick.
- [ ] Consider an optional diagonal (eight-way) extension after four-way playtesting.
- [ ] Divide the driving screen into **left 2/3 playfield** (straight-road baseline 75% road + 12.5% shoulder/grass per side) and **right 1/3 HUD**.
- [ ] Add the gas-pressure meter to the HUD.
- [ ] Display **lives**, miles remaining to the next destination, and score in the right-side HUD.
- [ ] Make gas pressure rise automatically over time.
- [ ] Trigger an explosion/failure when pressure reaches 100%.
- [ ] Define and detect successful arrival at the pharmacy.
- [ ] Add a simple stage-restart mechanism.
- [ ] Add a friends' car near the top of the screen.
- [ ] Prototype Gas-Nix drops and pickups for later road stages.
- [ ] Test and adjust driving speed, pressure increase, and difficulty.

**Milestone:** A playable road chase with working gas pressure, a win condition, and a failure condition.

## Phase 4 — Indoor Gameplay
*Goal: Build the reusable engine for the restaurant, pharmacy, grocery store, and house.*

- [ ] Implement the chosen indoor perspective.
- [ ] Create a basic room and obstacle layout.
- [ ] Implement player movement and wall collisions.
- [ ] Create the gas-blast attack.
- [ ] Implement basic enemy movement and pursuit.
- [ ] Add enemy interactions with gas blasts.
- [ ] Implement item collection.
- [ ] Add exits and stage-completion conditions.
- [ ] Prototype the Taco Smell escape.
- [ ] Prototype the pharmacy Gas-Nix retrieval.
- [ ] Prototype the grocery-store toilet-paper retrieval.
- [ ] Prototype the final bathroom objective.

**Milestone:** At least one complete, playable indoor stage.

## Phase 5 — Graphics and Animation
*Goal: Develop graphics suited to Atari 800XL hardware.*

- [x] Develop initial box and cartridge cover concepts.
- [x] Select a preferred packaging-art direction.
- [x] Establish the younger protagonist's general appearance.
- [ ] Finalize the protagonist's character design.
- [ ] Create player movement and gas-blast sprite animations.
- [ ] Design player, friends', police, and hazmat-van vehicles.
- [ ] Design hazmat and other enemy sprites.
- [ ] Design Gas-Nix and toilet-paper pickup graphics.
- [ ] Design four distinct restaurant identities and environments.
- [ ] Create pharmacy, grocery, road, house, and bathroom graphics.
- [ ] Create HUD, score, gas-pressure, and miles-to-destination graphics for the dedicated one-third driving panel.
- [ ] Design temporary narrowing/weaving road transitions and return-to-baseline, center-divider island forks, shoulder/off-road cues, left/right-positioned flashing GREEN upward arrow and wrong-fork detour feedback.
- [ ] Create off-road skid, shake, smoke, critical smoke and two-second explosion/lost-life visual effects.
- [ ] Design four-sided gas blast effects and ramming/knockback cues; optional diagonal art after mechanic approval.
- [ ] Design title, stage introduction (including Billy Blaster's exact quote), game-over, and victory screens.
- [ ] Finalize box and cartridge artwork for production.

## Phase 6 — Sound and Music
*Goal: Give the game a distinctive 1982 arcade personality.*

- [ ] Compose title-screen music.
- [ ] Create POKEY sound effects for gas blasts.
- [ ] Create vehicle and police-pursuit sounds.
- [ ] Create Gas-Nix pickup sound.
- [ ] Add escalating gas-pressure warning sounds.
- [ ] Create explosion and failure effects (including timed off-road crash).
- [ ] Create escalating normal/critical off-road warning sounds during the two-second countdown.
- [ ] Create stage-completion sounds.
- [ ] Create the final bathroom victory effect.
- [ ] Test sound effects alongside gameplay.

## Phase 7 — Build All Four Levels
*Goal: Turn the prototypes into a complete arcade game.*

- [ ] Complete all required Taco Smell stages.
- [ ] Create Casa de Gas stages and restaurant artwork.
- [ ] Create The Bean Machine stages and restaurant artwork.
- [ ] Create The Blazing Burrito stages and restaurant artwork.
- [ ] Implement progression between stages and levels.
- [ ] Implement the loop from Level 4 back to Level 1.
- [ ] Apply difficulty adjustments between levels and cycles.
- [ ] Complete scoring, lives, and game-over logic.
- [ ] Add intro, transition, and ending sequences; display Billy Blaster's approved line in-game with exact wording.
- [ ] Play through a complete four-level cycle.

## Phase 8 — Testing and Release
*Goal: Produce a stable game that works on Atari 800XL hardware.*

- [ ] Test the game in an Atari 8-bit emulator.
- [ ] Test on a real Atari 800XL, if available.
- [ ] Verify performance, memory use, and frame timing.
- [ ] Test joystick controls and collision detection.
- [ ] Balance difficulty across all four levels.
- [ ] Check gameplay for unfair or unavoidable situations.
- [ ] Fix gameplay, graphics, and sound defects.
- [ ] Test continuous looping and high scores.
- [ ] Prepare the final game image and distribution package.
- [ ] Write player instructions and controls.
- [ ] Prepare promotional screenshots and packaging artwork.
- [ ] Release Gas Blasters '82 v1.0.

## Ongoing Project Maintenance

- [ ] Keep `GAME_DESIGN.md` current as gameplay decisions are finalized.
- [ ] Keep `ART_ASSETS.md` updated with approved assets.
- [ ] Maintain `TECHNICAL_DESIGN.md` as Codex makes architectural decisions.
- [ ] Update this checklist as tasks are completed or requirements change.
- [ ] Record significant design changes in the documents' change logs.
- [ ] Keep source code, art, and documentation synchronized in GitHub.

## Change Log

- **v0.13 — 2026-10-26:** Checks off car-center grass detection and run/pause/reset timer behavior (grass/shoulder/paved road). Splits the old mixed checklist item so graphics-mode-dependent pixel boundaries remain open. 32/150 completed; no implementation claimed.
- **v0.12 — 2026-10-26:** Confirms winding roadway temporarily narrows then returns to 75% baseline; forks feature scrolling central island with flashing green UP arrow on left/right near top ~2 seconds before island enters screen. Two design decisions checked; minimum narrowed road width remains open; total 31/149 tasks complete.
- **v0.11 — 2026-10-26:** Approves equal 6.25% shoulder / 6.25% grass subdivision on both sides of a 75% baseline road; marks the proportion decision complete while leaving pixel-level collision and partial shoulder recovery open. Checklist now 29/146 completed.
- **v0.10 — 2026-10-26:** Confirms the straight-section 75% road plus 12.5% roadside per side within a fixed left two-thirds driving playfield, and selects right-third HUD with lives/score/miles/gas. Splits remaining geometry and pixel sizing into open items. Now 28/145 completed; no code implementation claimed.
- **v0.9 — 2026-10-26:** Confirms two-second off-road explosion/one-life rule, low-traction shoulder and progressive warnings, and updates phase/checklist counts (26/143). Exact road/shoulder widths remain open; added prototype, art and sound tasks.
- **v0.8 — 2026-10-25:** Audited all 138 tasks against documented decisions and repository commits. Verified 25 already-complete items; no additional tasks were marked complete. Added phase totals and evidence/limitations summary.
- **v0.7 — 2026-10-25:** Confirms Billy Blaster as the main character and records the exact in-game introduction text; presentation and implementation are still to do.
- **v0.6 — 2026-10-25:** Confirms four-direction gas blasting as initial prototype scope, defers diagonal tests, and tracks naming the main character as an open design task.
- **v0.5 — 2026-10-25:** Confirms wrong forks cause slower mileage countdown (gas still rises), police/hazmat vans bump the player off-road, and four-sided gas blasts repel enemies. Adds eight-direction feasibility/control decision and new prototype tasks.
- **v0.4 — 2026-10-25:** Confirms a blinking advance-warning arrow near the top of the driving screen a few seconds before forks; adds timing and blink-cadence tuning tasks.
- **v0.3 — 2026-10-25:** Confirms unrestricted lateral driving, off-road crashes, winding/forking roads with route arrow, and 2/3 driving + 1/3 HUD screen layout; adds outstanding detailed-design and prototype work.
- **v0.2 — 2026-10-25:** Records the confirmed Spy Hunter-style overhead driving perspective; adds open lane-width/steering decision and clarifies driving-prototype tasks.
- **v0.1 — 2026-10-25:** Initial project checklist reflecting the game-design and art-direction discussions to date.
