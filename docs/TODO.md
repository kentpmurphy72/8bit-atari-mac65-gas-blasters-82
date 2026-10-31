# Gas Blasters '82 — Project To-Do List

**Version:** 0.27  
**Date:** 2026-10-30  
**Target:** Atari 800XL  
**Status:** Planning and early design  
**Companion documents:** [Game Design](GAME_DESIGN.md) · [Art Assets](ART_ASSETS.md)

> Living checklist. An unchecked item is not necessarily an approved requirement; some items are proposed work that depends on design decisions. Update this file as tasks are finished or scope changes.

## Status update — 2026-10-30 (following 2026-10-25 audit)

- **48 of 163 checklist items completed (29%).** Another **115 remain open**. The user **ran the integrated opening v1 in Atari800 and said it worked great**, including START/FIRE screen progression and the selected POKEY soundtrack sequence. An optional **Title v2 with 4 PMG players + 4 missiles** is now separately packaged and committed: fine visual highlights in logo/Billy/car/sign only; the title bitmap/music and all subsequent screen assets remain byte-identical. **The alternate v2 XEX has passed 6502 simulation and structural validation but has not yet been displayed in Atari800.** Stage 1 remains a temporary static placeholder, not gameplay.
- **Phase totals:** Game Design 34/46; Technical Architecture 3/15; First Playable Prototype 0/26; Indoor Gameplay 0/12; Graphics & Animation 8/22; Sound & Music 2/12; Build All Four Levels 0/10; Testing & Release 1/14; Ongoing Maintenance 0/6.
- **Repository assets (2026-10-30):** Standalone title/crew/arrival source artwork, XEXs and exact builders remain in `assets/title/`, `assets/intro/`, `assets/arrival/` and `tools/`. POKEY music, original/approximation MP3s and standalone sound-enabled XEXs are in `assets/music/` and **were heard and liked by the user**. The new unified XEX, source, manifest and checks are committed in [`assets/opening/`](../assets/opening/) and `tools/`; **combined visual/music/joystick transitions were tested successfully in the emulator**. The **separate title v2 PMG XEX** and source are tracked under `assets/title_v2/`, with **v2 emulator evaluation still pending**. No playable Stage 1 exists yet.
- **Still empty:** `AGENTS.md` and `docs/TECHNICAL_DESIGN.md`; do not mark them complete merely because the files exist.
- **Partially specified, not complete:** road-stage **four-way blast controls** and jeans-clad-backside/cloud visual concept are agreed upon, but **implementation and playtesting remain open**, as do precise blast timing/range/knockback, indoor controls and blasts, indoor camera, HUD presentation, failure handling, and final art. **Both standalone intro stills** have been inspected in an emulator; this does **not** constitute testing or integration of a playable game.
- **Ongoing maintenance checkboxes remain open intentionally:** documentation updates to date do not make recurring maintenance tasks permanently finished.

This checklist distinguishes **the two user-tested standalone visual XEX files (Meet the Crew v4 and arrival v3)** from testing the **playable game**. The game-wide emulator/hardware-testing tasks remain unchecked; **no physical Atari hardware test is claimed**.

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
- [x] Set winding-road minimum to **40% of left driving playfield**; narrow from normal **75% to 40% in ~4s** and widen back **40% to 75% in ~4s**. Maintain **6.25% shoulders** on each side (centered narrow road leaves **23.75% grass** per side).
- [x] Confirm a **flashing GREEN arrow pointing UP**, appearing **near the top of the driving area** on the **left or right side** to indicate preferred fork; start flashing **~2 seconds before the center island first appears**.
- [x] Confirm fork-arrow warning: **0.25s ON / 0.25s OFF**, begins **~2s before center island first appears**, keeps flashing near top through fork approach and **disappears when Billy passes the fork decision point**. (Exact frame/pixel mapping belongs to Phases 2–3.)
- [x] Confirm wrong-fork penalty is **one-time +1.0 mile to distance remaining**, **no countdown slowdown**, gas pressure continues rising, and no immediate crash.
- [x] Confirm police cars and hazmat vans attempt to bump/PIT-style force the car off the road.
- [x] Confirm gas blasts from the front, rear, left and right push enemy vehicles away.
- [x] Confirm wrong forks add **exactly 1.0 mile once**; continue at **normal countdown speed** while gas pressure rises; fork branches **merge back relatively soon into a single normal-width (75%) road**, without requiring a visually separate extra mile.
- [x] Select four-direction gas blasting for the initial driving prototype.
- [x] Select **four-way gas blasting only** for the current design (front/rear/left/right car windows); **no diagonal attacks** planned, although the concept can be reconsidered if testing later warrants it.
- [x] Confirm driving controls: joystick **steers with Fire released**; **hold Fire + Up/Down/Left/Right** to blast front/rear/left/right; **no steering while Fire held**, car keeps moving/coasting. Two-joystick mode deferred; usability is a separate prototype test.
- [ ] Determine car-to-car collision impulse, recovery window, and gas-blast knockback behavior.
- [x] Fix the HUD in the **right third** of the driving screen; include lives, score, miles remaining and gas meter.
- [ ] Finalize HUD visual presentation and arrangement of lives, score, miles and gas meter (right-third placement is already confirmed).
- [x] Choose a name for the main character: **Billy Blaster**.
- [x] Approve Billy Blaster's introductory line (exact wording captured in GAME_DESIGN.md).
- [x] Decide **Meet the Crew** is the first post–1 PLAYER intro (Billy centered with four friends and exact quote); it now leads to **the separate Taco Smell arrival still** and then Stage 1. Dinner-table scene remains deferred.
- [x] Select **Option 3 (third, medium-detail concept)** for a separate **Arriving at Taco Smell** static screen after Meet the Crew: Billy and four friends walk from their parked car toward the lit restaurant under the evening sky; now realized as an emulator-tested standalone mixed ANTIC E/ANTIC 2 scene.
- [x] Approve exact **three-line Taco Smell arrival story text** for 40 columns: “Billy came for a killer burrito.” / “The beans came with a warning.” / “Nobody read it. Especially Billy.”
- [ ] Choose overhead or side-view gameplay for indoor stages.
- [ ] Define **indoor-stage** movement and joystick/fire-button controls (road-stage control mapping is confirmed).
- [ ] Define remaining gas-blast details (range, cooldown, repeat rate and knockback strength) and effects against **indoor** enemies; four-way road blasts already knock back police/hazmat vehicles.
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
- [ ] Select Atari/ANTIC graphics mode(s) and screen layouts; derive **exact pixel boundaries** for the left 2/3 driving playfield, straight-road zones (**6.25% grass / 6.25% shoulder / 75% road / 6.25% shoulder / 6.25% grass**) and right 1/3 HUD. Specify pixel rounding/alignment and how boundaries update as roads wind or narrow.
- [ ] Develop a preliminary memory map and allocation strategy.
- [ ] Determine how player/missile graphics will be used.
- [ ] Define the game's main loop, input handling, timing, and collision architecture.
- [ ] Define frame-based timing, graphics-mode-specific coordinates, and the measurable decision-point trigger for the approved fork arrow (**~2s pre-island**, **0.25s ON/OFF**, disappears after Billy passes fork); account for video refresh rate and road scrolling.
- [ ] Establish a reusable stage/level data structure.
- [ ] Complete `TECHNICAL_DESIGN.md`.
- [ ] Populate `AGENTS.md` with instructions for Codex.

## Phase 3 — First Playable Prototype
*Goal: Prove that the central game mechanic is fun.*

**Recommended starting point: Stage 2 — First Road Chase.**

- [ ] Display a basic overhead roadway scrolling downward.
- [ ] Implement continuous side-to-side steering (no fixed-lane snapping).
- [ ] Implement road/shoulder/grass zone classification using the **center of Billy's car** and the graphics-mode-specific left/right boundary coordinates at **his current vertical road cross-section**, including winding and narrowed roads (normal baseline: 75% road, 6.25% shoulder per side and 6.25% grass per side).
- [ ] Implement **grass time runs/resumes / shoulder time pauses / paved-road time resets** behavior; at 2.0s accumulated grass time since last road recovery, explode and deduct one life.
- [ ] Implement staged skid, shake/reduced steering, warning/smoke, critical warning/heavy smoke.
- [ ] Prototype winding roads narrowing **75% → 40% over ~4s**, weaving at the narrow width, and widening **40% → 75% over ~4s**, preserving **6.25% shoulders**.
- [ ] **Playtest and validate** the 40% minimum, four-second narrowing/widening, shoulder safety, and recoverability against enemy ramming; tune only if necessary.
- [ ] Prototype a **scrolling center-divider island** creating left/right branches and a green upward arrow near top on the preferred side. Start flashes **~2 seconds before island first appears**; animate **0.25s ON / 0.25s OFF**, keep flashing during fork approach, and remove when Billy passes the fork's decision point. Validate timing, visibility and geometry in the chosen graphics mode.
- [ ] Implement wrong-fork route selection with **one-time +1.0 mile** on wrong-branch choice, **normal-rate** miles countdown and continuing gas-pressure increase; automatically **merge split branches back soon** to one normal 75%-width road, **before** the extra mile is traveled. Prototype/tune visual merge timing and clarity.
- [ ] Draw the player's car facing upward near the bottom of the screen.
- [ ] Implement joystick steering.
- [ ] Add police cars and basic collision detection.
- [ ] Add hazmat vans and enemy lateral ramming/forced-off-road behavior.
- [ ] Implement directional gas blast knockback on all four sides of the player's car.
- [ ] **Prototype and playtest** the approved **hold Fire + cardinal direction** gas-blast mode: no lateral steering while held, car coasts forward, release Fire to resume steering; test safe use during winding roads and police pursuit.
- [ ] Prototype the **jeans-covered backside pop-out + emanating gas-cloud effect** for each of the four car windows; evaluate sprite readability/animation and collision alignment at the selected Atari graphics resolution.
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
- [x] Select **Option 3** as the title-screen visual direction (third ANTIC E + DLI concept): large logo, Billy in red car, sunset, green gas trail, Taco Smell sign, **1 PLAYER / PRESS START**. Separate from the “Meet the Crew” intro; this is **concept selection**, not a final Atari bitmap.
- [x] Build and visually test a **standalone “Meet the Crew” ANTIC E+DLI XEX** in an Atari emulator: v4 has the game logo, roadside Taco Smell sign and placeholder character labels removed, with heading/quote/prompt below the art; **not** a tested full-game screen flow.
- [x] Build a **unified, standalone title → crew → arrival → static Stage 1 placeholder XEX**, featuring actual START/FIRE controls and release-to-rearm logic, original Arcade Rock/Funky Gas Attack POKEY song data, and continuous cutscene music. **User ran the combined v1 XEX in Atari800 and reported it worked great.**
- [x] Build a **separate title v2 PMG detail-enhancement alternate XEX**, retaining the exact title bitmap/menu/music and all other scenes. Includes 4 players/4 missiles, repositioned/recolored by DLI and disabled on cutscenes; source and native data committed under `assets/title_v2/`. **Structural/CPU simulation passed; visual emulator validation still open.**
- [ ] Finalize the protagonist's character design.
- [ ] Create player movement and gas-blast sprite animations.
- [ ] Design player, friends', police, and hazmat-van vehicles.
- [ ] Design hazmat and other enemy sprites.
- [ ] Design Gas-Nix and toilet-paper pickup graphics.
- [ ] Design four distinct restaurant identities and environments.
- [ ] Create pharmacy, grocery, road, house, and bathroom graphics.
- [ ] Create HUD, score, gas-pressure, and miles-to-destination graphics for the dedicated one-third driving panel.
- [ ] Design temporary narrowing/weaving road transitions and return-to-baseline, center-divider island forks, shoulder/off-road cues, left/right-positioned flashing GREEN upward arrow, **early branch merging to a 75%-width road**, and **+1.0-mile HUD wrong-turn feedback**.
- [ ] Create off-road skid, shake, smoke, critical smoke and two-second explosion/lost-life visual effects.
- [ ] Design **four** car-window gas-blast animations, each showing a **jeans-covered backside popping out the window** and a cloud originating from it, with enemy ramming/knockback cues; **no diagonal art planned**.
- [ ] **Implement and validate** the selected **Option 3 title screen** as a hardware-compatible Atari bitmap, palette/DLI strategy, and usable **1 PLAYER / PRESS START** control; separately integrate **Meet the Crew** (exact quote) with actual Fire-to-continue input and the new arrival still before Stage 1, plus game-over and victory screens. The crew intro's standalone XEX exists but is **not integrated**; dinner-table screen still excluded.
- [x] **Convert selected Taco Smell arrival Option 3 into a standalone mixed Atari scene and visually test XEX:** **160×128 ANTIC E artwork** with horizontal DLI palette bands, **eight 40-column ANTIC 2 text rows** and approved three-line story. User verified in **Atari 800 Emulator 5.2.0 (2026-10-29)** and said “looks good.” **Does not include functional Fire input or scene integration; the tested XEX and supporting binaries are now committed under `assets/arrival/`.**
- [ ] **Later polish Meet the Crew text legibility:** consistent glyph sizes/baselines and spacing; clearer line wrapping/left alignment; comfortable separation of **MEET THE CREW**, the exact introductory quote and **FIRE TO CONTINUE**. Preserve the current image composition without game logo, background Taco Smell sign or character-name labels.
- [ ] Finalize box and cartridge artwork for production.

## Phase 6 — Sound and Music
*Goal: Give the game a distinctive 1982 arcade personality.*

- [x] Compose and approve **Arcade Rock** as the original 148-BPM title theme, with potential gameplay reuse; convert into a four-channel POKEY music player and standalone title XEX (emulator music audition pending).
- [x] Compose and approve **Funky Gas Attack** as the original 110-BPM theme for **Meet the Crew** and **Arriving at Taco Smell**; build POKEY-register versions of both standalone XEXs and save MP3/source assets in GitHub (emulator music audition pending).
- [ ] **Audition and tune the new POKEY title/intro/arrival XEX music in Atari800**; verify pitches, balance, drum sounds, looping and START-key mute, then review sound on real Atari hardware if possible.
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
- [ ] Integrate the opening scene flow **Title → Meet the Crew** (Billy's exact quote) **→ Arriving at Taco Smell** (five friends walking from their car) **→ Taco Smell Stage 1**; implement Fire-to-continue and any other necessary transitions/endings. **Do not add the deferred dinner-table cutscene.**
- [ ] Play through a complete four-level cycle.

## Phase 8 — Testing and Release
*Goal: Produce a stable game that works on Atari 800XL hardware.*

- [x] **Test the integrated opening-sequence v1 XEX in Atari800**: user confirmed the single continuous introduction worked great with title START, crew/arrival FIRE, and the temporary Stage 1 screen (2026-10-30).
- [ ] **Test the alternate title v2 PMG XEX in Atari800**: highlight alignment on logo/Billy/car/sign; no flicker or PMG bleed into later scenes; Arcade Rock and input progression unchanged; screenshot and adjust vertical origin if needed.
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

- **v0.27 — 2026-10-30:** Records successful user Atari800 test of the full continuous opening v1. Builds and commits **Title v2 PMG** alternative with 4 single-line players and four missiles ($A000 DMA) adding ~220 controlled highlights to the original title while retaining original bitmaps, GTIA palettes, text, Arcade Rock/Funky Gas Attack, and subsequent scenes. CPU, DLI, scene-state and reproducible SHA validations pass; **awaits separate Atari800 visual test of PMG v2**. Updates checklist to **48/163 complete, 115 open**.
- **v0.26 — 2026-10-30:** Builds and commits a **single native 6502 Atari 800XL opening-sequence XEX** with four states: title (Arcade Rock) → Meet the Crew (Funky Gas Attack) → arrival (same continuously playing Funky Gas Attack) → static Stage 1 screen (silent), with START/FIRE/release debouncing and START replay. Reuses exact approved artwork, texts, and ANTIC E/DLI color bands. XEX, Python byte emitter, reference assembly, manifest and 6502 CPU/DLI validation are in `assets/opening/` and `tools/`. Checks off integrated-prototype build and opens separate full emulator test; **46/161 checked, 115 open**. The user previously played all three standalone music-enhanced XEXs and liked them; the **combined** XEX is not yet tested in Atari800.
- **v0.25 — 2026-10-30:** Approves **Arcade Rock** for title/potential gameplay and **Funky Gas Attack** for both cutscenes. Commits three genuine POKEY music-enabled standalone XEXs, original and register-derived approximation MP3s, four-channel sequencer, event/POKEY register data and reproducible build sources under `assets/music/`, plus original title source under `assets/title/`. **No emulator audio test yet**. Closes the title and cutscene composition/conversion tasks and opens music-audition task; **45/159 completed, 114 open**, Sound & Music 2/12.
- **v0.24 — 2026-10-29:** Adds **27 versioned source and native asset files** for the two emulator-tested intro stills under `assets/intro/`, `assets/arrival/`, and `tools/`: XEX, original full-resolution artwork, raw ANTIC E bitmaps, constrained-color PNGs, palette tables, screen text, custom fonts, display lists, previews, manifests, READMEs and reproducible builders. Both builders reproduced the approved XEX files byte-for-byte. Maintains **43/157 complete (114 open)**; actual Fire controls/scene integration and full-game testing remain open.
- **v0.23 — 2026-10-29:** Marks the **standalone Taco Smell arrival-screen bitmap/XEX and emulator visual test complete**. User approved v3 with **160×128 ANTIC E art + eight ANTIC 2 text rows** and the exact **three-line** burrito/beans warning, including a display-only Fire prompt. Adds completed Phase 1 text-selection item and checks off Phase 5 arrival-XEX visual test; keeps Fire input, screen-to-screen integration and game-wide emulator testing open. **43/157 complete; 114 open**. No source art/XEX binary checked into GitHub.
- **v0.22 — 2026-10-28:** Confirms **one additional static arrival scene** after Meet the Crew and before Stage 1 using the **third medium-detail concept**; restores the earlier deferred parking-lot idea but not the dinner-table scene. Adds completed Game Design selection and open Phase 5 ANTIC E+DLI bitmap/XEX/emulator-validation task. 41/156 complete; no arrival bitmap or XEX committed.
- **v0.21 — 2026-10-28:** Records user-run standalone **Meet the Crew v4 ANTIC E/DLI XEX**, with game logo, background restaurant sign and name labels removed, heading moved into caption area and approved quote shown. Checks off **prototype displayed in emulator**, but retains a new **deferred text-readability polish task** and game integration/working Fire-input tasks. Atari title screen Option 3 remains selected but not implemented. 40/154 complete; no art/XEX files committed.
- **v0.20 — 2026-10-28:** Selects **Option 3 (the third, middle-ground Atari-inspired title illustration)** as the title-screen visual target, with Billy in a red front three-quarter-view car, green gas cloud, sunset, Taco Smell and 1 PLAYER/PRESS START. Keeps this separate from the one-screen Meet the Crew introduction. Adds a checked Phase 5 concept-selection task and leaves real ANTIC E+DLI conversion, title controls and hardware testing open. 39/152 complete.
- **v0.19 — 2026-10-28:** Confirms **one** “Meet the Crew” introduction screen after 1 PLAYER start (Billy centered, friends, exact quote), then Stage 1 Taco Smell. Defers Screen 2 parking-lot and Screen 3 dinner-table cutscenes; no new production requirement for either. Checks off intro placement/scope decision while leaving Atari graphics, caption readability and screen implementation open. 38/151 complete.
- **v0.18 — 2026-10-27:** Confirms four-way-only road gas blasts (no diagonal mode), hold Fire + cardinal direction to blast instead of steer while the car coasts, and the jeans-clad backside popping from the selected window with a gas cloud. Defers two-joystick option, clarifies indoor controls remain open, and replaces the obsolete prototype diagonal task with four-way blast FX implementation. Marks two Phase 1 design decisions complete: 37/151.
- **v0.17 — 2026-10-27:** Finalizes wrong-fork rule: add **+1.0 mile once** only on a wrong turn, retain normal miles-countdown speed and continuing gas pressure, and automatically merge branches soon into a normal 75%-width road before the extra mile is traveled. Supersedes previously recorded slower-mileage behavior; implementation/prototype merge geometry remains open. 35/151 complete.
- **v0.16 — 2026-10-26:** Confirms green fork-arrow cadence (0.25s ON / 0.25s OFF), ~2-second advance warning and disappearance after passing fork decision point. Marks Phase 1 arrow-design task complete and adds a Phase 2 timing/coordinate-mapping task; retains Phase 3 prototype implementation. 34/151 complete.
- **v0.15 — 2026-10-26:** Approves road narrowing from 75% to 40% in ~4 seconds and widening back in ~4 seconds; shoulders stay 6.25% on each side, grass expands to 23.75% on each side when centered and narrow. Marks design task done and adds separate Phase 3 prototype-validation task. 33/150 complete.
- **v0.14 — 2026-10-26:** Moves the Atari graphics-mode and exact pixel-boundary decision out of Phase 1 into the existing Phase 2 graphics/screens task; clarifies Phase 3 car-center collision implementation at Billy's current road cross-section; leaves HUD visual presentation in Phase 1. Removes a redundant open checklist item without changing completed statuses (32/149 done).
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
