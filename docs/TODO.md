# Gas Blasters '82 — Project To-Do List

**Version:** 0.49  
**Date:** 2026-11-08  
**Target:** Atari 800XL  
**Status:** Stage 1 v0.5 implemented and accepted as a playable prototype; remaining full game in design/development  
**Companion documents:** [Game Design](GAME_DESIGN.md) · [Art Assets](ART_ASSETS.md)

> Living checklist. An unchecked item is not necessarily an approved requirement; some items are proposed work that depends on design decisions. Update this file as tasks are finished or scope changes.

- **PMG regression and v2.1 hotfix — 2026-10-30:** The first real Atari800 test of the alternate PMG title **v2 failed visually** (stray cyan/white pixels overlapping text/background). Bug confirmed: DMACTL set to $2E **double-line** although 2 KB PMG data was built for **single-line**. The v2 validator mistakenly expected $2E as well. A separate v2.1 XEX and corrected source now use $3E, an adjusted 56-line vertical origin, and explicit tests for correct DMACTL and cleared PM rows over the text. **v2.1 was tested in Atari800 on 2026-11-01 and was visually rejected:** scattered PMG highlights still degrade the logo, Billy and car. The overlay intentionally adds about 220 disconnected pixels; a heavy DLI handler also has insufficient cycle headroom for one scanline. Do not adopt v2/v2.1; preserve the accepted v1 title. No checklist completion change. **Known-good v1 is unaffected**. Checklist completion count is unchanged until the corrected PMG screen passes visually.
## Stage 2 v0.2-r1 car visibility repair

- User-reported Atari800 defect: car disappears at 75% pressure. Cause: shake
  read GTIA $D000 collision flags as if they were HPOSP0 position feedback.
- Fixed in a separate [v0.2-r1 XEX](../assets/stage2_v02_r1/README.md), using RAM X
  and the existing amplitudes/clamp. All previous XEX/source/test files remain.
- New alias-aware CPU visibility checks cover 74/75/90/99%, shaking/HUD flashes,
  PMG bytes, DMA/enables/colors/positions, road edges and speed-linked Y.
  Full v0.2/r3 regression results are recorded with the fixed artifact.
- Still pending: Atari800 NTSC/PAL visual confirmation and gameplay acceptance;
  no new balance/art decisions, merge or tag. Broader completion counts unchanged.

## Stage 2 v0.2 implementation evidence — 2026-11-09

- **Implemented and CPU verified:** standalone v0.2 pressure/destination XEX,
  exact fractional MPH/mileage and nominal NTSC/PAL timing, warning shake and
  steering, fixed HUD, three-life explosion/retry loop, pharmacy exterior,
  completion/new-game FIRE sequence and disabled START.
- [Versioned XEX/source/build/playtest notes](../assets/stage2_v02/README.md),
  [actual test results](../assets/stage2_v02/validation.md), manifest and measured
  CPU profile are committed together on the existing v0.2 feature branch.
- Historical Stage 1/opening and original Stage 2 v0.1/r2/r3 artifacts are
  preserved. No Stage 3, enemies, road hazards, blasting or integration added.
- **Still open:** user Atari800 NTSC/PAL playtest and acceptance, actual raster/
  controller/audio checks, shake/flash/handling and timing balance. Atari800 and
  physical hardware **NOT RUN**. Broad Phase 3 acceptance checkboxes and totals
  remain unchanged until gameplay acceptance; this evidence supersedes older
  design-only status statements without marking the whole chase complete.

## Stage 2 v0.2 Codex prompt coverage and validation contract — 2026-11-08

- **Audit:** Original detailed Codex v0.2 prompt's gameplay requirements already reside in [Stage 2 §§16–21](STAGE2_DESIGN.md). Mandatory automated validation categories and **full deliverable/reporting criteria** are explicitly specified in [Stage 2 §22](STAGE2_DESIGN.md), with technical/workflow/AGENTS references. This is **docs only**, not test execution.
- **Required next-implementation evidence:** standalone native XEX, source/listing, deterministic build/tests, checksum/segment manifest; 60/50 Hz clock and 165s pressure tests; exact Q4-to-MPH/distance tests; gas/life/arrival/FIRE state tests; HUD/font/PMG safety; memory/per-frame cycles; Stage 1/r3/r2/v0.1 regressions; actual Atari800 NTSC/PAL results if possible or explicit **NOT RUN**; manual Atari800 checklist. Do not mark Phase 3 work complete without evidence or tag/merge before user acceptance.

## Stage 2 v0.2 design review and cleanup — 2026-11-08

- **Current authority:** [Stage 2 design §§16–21](STAGE2_DESIGN.md) is the complete v0.2 functional specification. Tag `stage2-v0.1` and `main` are verified at `e0e4422`; v0.2 remains a **documentation-only feature branch**, with no playable XEX yet.
- **Outcome clarity:** GAS=100 wins a simultaneous MI=0 tie; each gas explosion costs exactly one life, followed by **BILLY BLEW IT! only when lives remain** or **GAME OVER at zero lives**. FIRE is the normal retry/new-game/continue control. In v0.2, **console START/F4 is disabled as a gameplay reset**; the accepted v0.1-r3 START reset is preserved only in that historical executable. Use test-harness resets for deterministic automated tests, not a gameplay cheat.
- **Status:** Final cleanup only; no code, executable, life-count checklist item or acceptance state changed. Exact art, flicker and shake tuning remain playtest tasks. Any older dated status paragraphs below are historical snapshots and do **not** supersede approved §§16–21.

## Stage 2 v0.2 last two gameplay decisions approved — 2026-11-08

- **Gas wins a simultaneous tick:** GAS 100% and MI=0 in the same update → explosion, one life deducted, never pharmacy success. An earlier successful arrival freezes pressure and cannot later explode. Terminal outcomes latch once.
- **FIRE state transitions:** after `BILLY BLEW IT!`, retry with reduced lives; after `GAME OVER`, start a **new three-life Stage 2 game**; after the pharmacy cutscene, FIRE advances to `STAGE 2 COMPLETE`; after that completion screen, a fresh FIRE starts another **three-life Stage 2 prototype game**. Require release/fresh press per screen.
- These **approved core gameplay rules supersede earlier dated open-decision notes** below. Remaining steps: final spec consistency review and Codex implementation/test of standalone v0.2. **No v0.2 XEX or gameplay changes in this documentation commit**. See [Stage 2 design §21](STAGE2_DESIGN.md).

## Stage 2 v0.2 HUD presentation approved — 2026-11-07

- **User-approved fixed Atari 800XL driving HUD** in the existing **27-road / 13-HUD character-column** split: top GAS **whole % + 10-segment bar**, PHARMACY remaining **2.00→0.00 MI** in two decimals, SPEED **whole MPH** (20–100 via approved Q4 mapping), **three miniature car life icons** (disappear when lives lost), and **six-digit SCORE** placeholder `000000`. Preserve the same layout for future driving stages with destination updates; avoid raw Q4/ZONE telemetry in playable v0.2.
- **Warnings and precision:** At **75–89%**, slowly flash **only** GAS bar and percentage; at **90–99%**, flash them faster. Don't shake or obscure the stationary HUD. Update digits as the shown value changes; keep internal simulation precision independent from display rounding. Do **not** show `0.00 MI` before actual arrival or `100%` before genuine pressure failure. Car icons reflect **3→2→1→0** remaining lives across retries.
- **Still for playtesting:** precise glyph/palette and flash-cadence tuning (Codex/Atari800). **The same-tick gas-first rule and GAME OVER/COMPLETE FIRE replay behavior were approved in §21.** See [Stage 2 design §20](STAGE2_DESIGN.md). No XEX or HUD code has been implemented or validated; leave checkboxes unchanged.

## Stage 2 v0.2 native-speed-to-MPH mapping approved — 2026-11-07

- **Confirmed:** preserve the accepted r3 Q4 driving mechanics; interpret speed **Q4 8→20 MPH**, **24→60 MPH** (default), **56→100 MPH**. Convert between these anchors using continuous **piecewise-linear interpolation**; examples Q4 16→40, 32→70, 40→80, 48→90 MPH. Details and equations in [Stage 2 design §19](STAGE2_DESIGN.md).
- **Distance:** use modeled MPH with elapsed time to reduce the **2.0-mile** pharmacy countdown, at sufficient precision independent of visible HUD rounding. Steady default speed Q4 24/60 MPH implies a **2:00** trip, but typical user completion remains subject to balancing and actual playtest.
- **Current status:** The same-tick gas-first precedence and GAME OVER/COMPLETE FIRE controls were approved in §21; only shake/steering, cutscene art, character glyph and flash-cadence tuning remain for implementation/playtesting. HUD precision is approved in §20. No code implementation or new Phase 3 checklist completion is implied.

## Stage 2 v0.2 pharmacy arrival approved — 2026-11-07

- **Confirmed successful arrival:** when the remaining miles reach **0.0 while gas is below 100%**, freeze driving and the gas/distance timer, show a **brief exterior cutscene featuring the pharmacy building**, and wait for a fresh **joystick FIRE/trigger press** to continue. A successful arrival does not deduct lives or trigger a gas explosion.
- **Standalone v0.2 handoff:** FIRE advances from the arrival cutscene to an obvious **Stage 2 completion screen** only. The Stage 3 pharmacy interior is **not implemented**; do not auto-transition into it. Cutscene artwork/copy/duration can be tuned for legibility in Atari800.
- **Design decisions complete:** same-tick gas-first precedence and completion/GAME OVER FIRE replay are approved (§21); MPH conversion (§19) and HUD layout/precision/update behavior (§20) are approved. See [Stage 2 design §18](STAGE2_DESIGN.md). **Documentation only, no v0.2 XEX yet**; leave implementation checkboxes open.

## Stage 2 v0.2 approved failure, warnings and retry — 2026-11-07

- **Confirmed by user:** **3 starting lives**; at **75% gas**, start car shake and flashing warning with mildly harder steering; at **90%**, significantly more violent shake and stronger but controllable steering difficulty. Precise jitter/handling/flash values remain playtest tuning choices. Keep approved r3 movement unchanged below 75%.
- **100% gas sequence:** freeze driving/simulation → play a **basic** gas-explosion animation → **deduct exactly one life** → show exact **`BILLY BLEW IT!`** if lives remain. A fresh **joystick FIRE/trigger** press then retries Stage 2, resetting GAS to **0%**, MI to **2.0**, car speed/position and attempt timing, while retaining remaining lives. When no lives remain, show exact **`GAME OVER`**, with no ordinary retry. Elaborate audiovisual effects deferred.
- **Current status:** All functional consequences, same-tick priority, FIRE new-game behavior, speed mapping and HUD presentation are approved in [Stage 2 design §§17–21](STAGE2_DESIGN.md). Exact shake/handling animation and cutscene appearance remain for tuning. **None of these v0.2 systems has been implemented**; keep Phase 3 items unchecked until built and user-playtested.

## Stage 2 v0.2 initial balance selections — 2026-11-07

- **Agreed provisional pacing:** typical drive **2:00**, **20–100 MPH** car speed, **60 MPH** average target, **2.0 miles** to pharmacy. Constant modeled 60 MPH over 2 miles is 120 seconds; player times will vary.
- **Agreed provisional gas growth:** starts **0%**, rises about **18 percentage points every 30 seconds** (linear exact rate 100/165 points/second), reaches **100% at 2:45**. Approximate HUD: 0/18/36/55/73/91/100% at elapsed 0/30/60/90/120/150/165 seconds. The final 15 seconds add ~9 points because that interval is half as long; no nonlinear taper rule has been chosen.
- **Current status:** Gas growth, distance/MPH mapping, HUD, pharmacy cutscene, explosion/life logic and terminal controls are all approved in [Stage 2 §§16–21](STAGE2_DESIGN.md). Exact art/flash/shake settings remain for Atari800 tuning. **No v0.2 XEX has been built** and implementation checklist items remain open.
- **Branch status:** the accepted `stage2-v0.1` milestone is now in `main`; `feature/stage2-pressure-destination-v0.2` is the active design/development branch. This update is documentation only.

## Stage 2 v0.1 accepted; Stage 2 v0.2 next — 2026-11-04

- **Accepted by user after Atari800 playtest:** `assets/stage2_v01_r3/GasBlasters82_Stage2_Driving_v01_r3.xex` is the approved **v0.1 driving-feel baseline** (not a complete pharmacy chase, full regression, PAL or hardware sign-off). Original v0.1/r2 XEXs and builder/test artifacts remain preserved.
- **Deferred:** Billy may later advance farther than the current **car-top Y=80 maximum-speed position**. Do not alter that approved v0.1-r3 tuning just to start v0.2. Revisit only with deliberate design review and user playtesting.
- **Next development milestone:** implement **v0.2 gas pressure and destination** using the now-approved [Stage 2 design §§16–21](STAGE2_DESIGN.md). Exact numbers, life loss, pharmacy arrival and FIRE controls are settled as design; **none is implemented in v0.1**. This 2026-11-04 entry records when v0.1 was accepted.
- **Milestone bookkeeping:** Six already implemented and now accepted Phase 3 checklist items are checked below (road rendering, free lateral steering, car drawing, joystick steering, pane/HUD layout and START reset). The remaining Stage 2 chase systems are still open. **77/175 completed, 98 open; Phase 3 now 6/26.**
- **Git checkpoint now complete and verified:** immutable `stage2-v0.1` and `main` both resolve to `e0e4422`; v0.2 design continues on `feature/stage2-pressure-destination-v0.2`. Do not tag/merge/delete v0.2 until its playable prototype is accepted.

## Stage 2 v0.1-r3 higher vertical travel — 2026-11-04

- **User has playtested r2 in Atari800** and wants more upper-screen travel at maximum speed. v0.1 is not yet gameplay-accepted.
- **Approved tuning experiment, now built/CPU tested:** move maximum-speed car-top **Y=112 → 80**, holding minimum/default Y=160/144 and speeds Q4 8/24/56. Increase vertical travel from 48 to 80 scanlines; revise the speed-to-Y mapping through the three anchors, with existing Y smoothing retained initially. See [Stage 2 design §13](STAGE2_DESIGN.md).
- **Implemented:** separate `assets/stage2_v01_r3/GasBlasters82_Stage2_Driving_v01_r3.xex` with build/test/manifest/profile. Original v0.1 and r2 are byte-for-byte preserved; only Y target tables change in the loaded r3 binary. All 21 r3, 19 r2, 12 original and 33 Stage 1 CPU tests, four validators and opening validation pass. **Next: user Atari800 r3 playtest**, especially high position and longer settling. No merge/tag or v0.2 work; checkbox totals unchanged.

## Stage 2 v0.1 user playtest and refinement — 2026-11-04

- The user **played the original v0.1 in Atari800**. Basic driving was fine, but the car stayed vertically stationary while speed/scroll rate changed; **v0.1 gameplay acceptance is pending**.
- Approved design: accelerating moves the actual car **up** the visible road; braking moves it **down**; neutral retains speed and its corresponding car Y. Continue scrolling speed changes, smooth lateral/diagonal steering and strict screen bounds. See [Stage 2 design](STAGE2_DESIGN.md), Section 12.
- Codex should generate a **second versioned v0.1 XEX**, retaining the initial XEX/manifest/source unchanged. v0.2 pressure/destination and v0.3+ hazards remain out of scope. The separately versioned v0.1-r2 refinement is now implemented and CPU tested; Atari800 review is pending.

## Stage 2 v0.1-r2 implementation evidence — 2026-11-04

- Built `assets/stage2_v01_r2/GasBlasters82_Stage2_Driving_v01_r2.xex` on the same
  feature branch: speed-linked bounded Q4 Y, neutral target hold and real P0/P1
  row clearing/relocation. Original driving controls/rendering/tuning preserved.
- 19 r2 tests, 12 original driving tests, 33 Stage 1 tests, four validators and
  opening validation pass. PMG row bytes are checked throughout acceleration,
  braking, steering at extremes, reversal and reset; idle is simulated three minutes.
- Original v0.1 assets/tools and Stage 1/opening/music unchanged. See
  [r2 notes](../assets/stage2_v01_r2/README.md) for build/run/tuning and manual checks.
- Atari800 r2 playtest, hardware/PAL and approval remain open. Still v0.1 only;
  no pressure/destination implementation, no merge/tag or completion-count change.

## Stage 2 v0.1 design update — 2026-11-03

- **Design approved; standalone implementation now CPU tested, playtest pending:** [STAGE2_DESIGN.md](STAGE2_DESIGN.md) is now the active first-driving-prototype specification. Option A controls are automatic forward motion, smooth free left/right steering, UP acceleration, DOWN braking to a positive minimum, and combined diagonal inputs. v0.1 targets a downward-scrolling straight road, distinct grass/shoulder/pavement zones, car sprite, and fixed right HUD with GAS/MI/SCORE/LIVES **placeholders**.
- **Implementation branch:** existing `feature/stage2-driving-v0.1`. The standalone XEX is now built and CPU tested; user Atari800 review identified fixed-Y behavior and the v0.1-r2 refinement is built/CPU tested, awaiting user review; gas pressure, pharmacy arrival, police, forks, off-road penalties and vehicle blasts remain later work. **The broader road-chase milestone remains open; v0.1 implementation evidence is recorded below.**

## Stage 2 v0.1 implementation evidence — 2026-11-03

- Standalone native XEX built on existing `feature/stage2-driving-v0.1`: scrolling
  straight road, smooth steering, automatic positive motion, UP/DOWN speed control,
  combined inputs, bounded car, fixed placeholder HUD with live SPD/ZONE and START reset.
- Twelve driving CPU tests pass, including 10,800 simulated video ticks (three nominal
  minutes); 33 retained Stage 1 CPU tests, all four design validators and opening
  validation pass. Original Stage 1/opening/art/music/XEXs remain unchanged.
- Source/build/run/tuning/memory/profile: [assets/stage2_v01/README.md](../assets/stage2_v01/README.md).
  **Atari800/user playtest is not run**, physical 800XL/PAL also pending.
- This implements the narrow v0.1 free-driving demo only. The broader Phase 3 road
  chase milestone/checklist below is not declared complete; pressure, distance,
  destination, opponents, curves, forks and penalties remain later work. Historical
  completion totals below are retained; no merge/tag or gameplay acceptance claimed.

## Status update — 2026-11-02

- **71 of 175 checklist items completed (41%), 104 open.** Stage 1 is **built, on `main`, tagged `stage1-v0.5`, and accepted as a playable prototype**. The user confirmed smooth v0.4 movement and, after playing v0.5, said gas blasting is **good enough for now**, with tuning deferred. This does **not** certify all edge cases or real hardware.
- **Phase totals:** Game Design 34/46; Technical Architecture 4/15; First Playable Prototype (driving) 0/26; Indoor Gameplay 13/17; Graphics & Animation 9/23; Sound & Music 4/14; Build All Four Levels 1/10; Testing & Release 6/18; Ongoing Maintenance 0/6.
- **Current Stage 1 source of truth:** [STAGE1_DESIGN.md](STAGE1_DESIGN.md); [deferred issues and polish](STAGE1_DEFERRED_WORK.md); [regression checklist](STAGE1_REGRESSION_CHECKLIST.md). Historical proposals and handoffs are [archived](archive/stage1/README.md), with five immutable Git tags and all versioned XEX/build tools preserved.
- **What remains open:** final polish/balance, detailed end-to-end regression, physical Atari 800XL and PAL coverage; later driving/pharmacy/grocery/home stages; full-game systems and Stage 2 handoff. Stage 1 gas shots are a renewable indoor charge mechanic and **not** the road pressure meter; indoor blasts aim in eight directions and **car blasts remain four-way**.
- **Title assets:** original continuous opening v1 remains approved. Alternate title PMG v2/v2.1 were visually tested and rejected; preserve for history but do not adopt. Original POKEY songs remain approved; do not claim physical hardware testing.
- **Maintenance tasks remain open intentionally**, because future documentation and synchronization are recurring responsibilities.

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
- [ ] Choose camera/perspective for **future** indoor stages (pharmacy/grocery/house); Taco Smell Stage 1 is already implemented as three overhead fixed-room screens.
- [ ] Finalize **indoor controls for future locations** and tune Stage 1 further if needed; Stage 1 v0.5 eight-way walking/blasting has been implemented and broadly user-playtested, but exhaustive regression/polish is still open. Car blasting remains four-way.
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
- [x] Populate `AGENTS.md` with current Codex branching, 6502 build, regression and validation instructions; update as the game evolves.

## Phase 3 — First Playable Prototype
*Goal: Prove that the central game mechanic is fun.*

**Stage 2 v0.1 basic driving is user-accepted (r3).** The **next** scope is v0.2 gas pressure / distance / destination, as outlined in [STAGE2_DESIGN.md](STAGE2_DESIGN.md), Section 15. The fuller checklist below spans the remaining Stage 2 mechanics; only wholly delivered/accepted items are checked. Phase 3 remains incomplete.

- [x] Display a basic overhead roadway scrolling downward.
- [x] Implement continuous side-to-side steering (no fixed-lane snapping).
- [ ] Implement road/shoulder/grass zone classification using the **center of Billy's car** and the graphics-mode-specific left/right boundary coordinates at **his current vertical road cross-section**, including winding and narrowed roads (normal baseline: 75% road, 6.25% shoulder per side and 6.25% grass per side).
- [ ] Implement **grass time runs/resumes / shoulder time pauses / paved-road time resets** behavior; at 2.0s accumulated grass time since last road recovery, explode and deduct one life.
- [ ] Implement staged skid, shake/reduced steering, warning/smoke, critical warning/heavy smoke.
- [ ] Prototype winding roads narrowing **75% → 40% over ~4s**, weaving at the narrow width, and widening **40% → 75% over ~4s**, preserving **6.25% shoulders**.
- [ ] **Playtest and validate** the 40% minimum, four-second narrowing/widening, shoulder safety, and recoverability against enemy ramming; tune only if necessary.
- [ ] Prototype a **scrolling center-divider island** creating left/right branches and a green upward arrow near top on the preferred side. Start flashes **~2 seconds before island first appears**; animate **0.25s ON / 0.25s OFF**, keep flashing during fork approach, and remove when Billy passes the fork's decision point. Validate timing, visibility and geometry in the chosen graphics mode.
- [ ] Implement wrong-fork route selection with **one-time +1.0 mile** on wrong-branch choice, **normal-rate** miles countdown and continuing gas-pressure increase; automatically **merge split branches back soon** to one normal 75%-width road, **before** the extra mile is traveled. Prototype/tune visual merge timing and clarity.
- [x] Draw the player's car facing upward near the bottom of the screen.
- [x] Implement joystick steering.
- [ ] Add police cars and basic collision detection.
- [ ] Add hazmat vans and enemy lateral ramming/forced-off-road behavior.
- [ ] Implement directional gas blast knockback on all four sides of the player's car.
- [ ] **Prototype and playtest** the approved **hold Fire + cardinal direction** gas-blast mode: no lateral steering while held, car coasts forward, release Fire to resume steering; test safe use during winding roads and police pursuit.
- [ ] Prototype the **jeans-covered backside pop-out + emanating gas-cloud effect** for each of the four car windows; evaluate sprite readability/animation and collision alignment at the selected Atari graphics resolution.
- [x] Divide the driving screen into **left 2/3 playfield** (straight-road baseline 75% road + 12.5% shoulder/grass per side) and **right 1/3 HUD**.
- [ ] Add the gas-pressure meter to the HUD.
- [ ] Display **lives**, miles remaining to the next destination, and score in the right-side HUD.
- [ ] Make gas pressure rise automatically over time.
- [ ] Trigger an explosion/failure when pressure reaches 100%.
- [ ] Define and detect successful arrival at the pharmacy.
- [x] Add a simple stage-restart mechanism.
- [ ] Add a friends' car near the top of the screen.
- [ ] Prototype Gas-Nix drops and pickups for later road stages.
- [ ] Test and adjust driving speed, pressure increase, and difficulty.

**Milestone:** A playable road chase with working gas pressure, a win condition, and a failure condition.

## Phase 4 — Indoor Gameplay
*Goal: Build the reusable engine for the restaurant, pharmacy, grocery store, and house.*

- [x] **Draft and validate a formal Taco Smell restaurant tile-map spec**: overhead 48×22 layout; connected dining/kitchen/storage; exact tile and entity coordinates; solid/walkable collisions; exit and two chokepoints; machine validator confirms 751 reachable floor cells. **Provisional layout only — Stage 1 gameplay, art and Atari800 playtesting remain open.**
- [x] **Design three room-sized Stage 1 v0.2 maps and transitions**: Dining/Kitchen/Storage are independent 40×22 fixed screens, four reciprocal door links, backtracking, one persistent pursuer, usable map/JSON, and new validator. This is **design only**; Codex needs to implement/playtest the v0.2 XEX.
- [x] **Specify Stage 1 v0.3 gameplay-pressure prototype**: three persistent hazmat encounters and original four-way blast experiment. **Historical design and playable XEX tagged `stage1-v0.3`**; superseded by v0.5 mechanics.
- [x] **Specify Stage 1 v0.4 responsive movement prototype**: native Q4 eight-way walking, normalized diagonal, wall slides, inset 6×6 hitbox and gameplay PMG. **Built and user-playtested successfully; archived spec and tag `stage1-v0.4`**.
- [x] **Specify Stage 1 v0.5 eight-way indoor gas blasting**: FIRE-held cardinal/diagonal aim, backside pose, three expanding cloud waves, 3-step knockback, BONK/stun, 3 renewable charges, recovery/cooldown and POKEY effect. **Built, on main, tagged `stage1-v0.5` and broadly user-playtested; fine-tuning deferred**.
- [x] **Stage 1:** Implement three fixed-screen overhead restaurant rooms. Future indoor cameras remain open.
- [x] **Stage 1:** Implement Dining/Kitchen/Storage terrain and solid/passable tile collision from canonical v0.2 maps.
- [x] **Stage 1:** Implement user-approved smooth eight-way Q4 movement, inset hitbox, furniture collision and wall slides.
- [x] **Stage 1:** Implement eight-direction FIRE-held gas blasts, expanding cloud, cooldown and regenerating charges; user accepted feel provisionally.
- [x] **Stage 1:** Implement three persistent room-linked hazmat pursuers with bounded BFS processing.
- [x] **Stage 1:** Implement stun, animated eight-direction knockback, corner/worker collision and impact feedback.
- [ ] Implement item collection.
- [x] **Stage 1:** Implement storage X exit, CAUGHT/COMPLETE states and START restart.
- [x] **Stage 1:** Build, integrate and user-playtest the accepted v0.5 playable Taco Smell escape.
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
- [x] **Experiment with alternative title PMG v2/v2.1 overlays:** Both compiled and passed CPU/structural checks, but **the user visually tested and rejected both in Atari800**. Preserve original v1 as the accepted title. Historical XEX/source in `assets/title_v2/`.
- [ ] Finalize the protagonist's character design.
- [ ] **Polish production-quality player walking and gas-blast sprite animations** across eventual indoor stages; Stage 1 v0.5 already has temporary eight-way gameplay PMG movement/backside poses and expanding cloud effects.
- [ ] Design player, friends', police, and hazmat-van vehicles.
- [ ] Design hazmat and other enemy sprites.
- [ ] Design Gas-Nix and toilet-paper pickup graphics.
- [ ] Design four distinct restaurant identities and environments.
- [ ] Create pharmacy, grocery, road, house, and bathroom graphics.
- [ ] Create HUD, score, gas-pressure, and miles-to-destination graphics for the dedicated one-third driving panel.
- [ ] Design temporary narrowing/weaving road transitions and return-to-baseline, center-divider island forks, shoulder/off-road cues, left/right-positioned flashing GREEN upward arrow, **early branch merging to a 75%-width road**, and **+1.0-mile HUD wrong-turn feedback**.
- [ ] Create off-road skid, shake, smoke, critical smoke and two-second explosion/lost-life visual effects.
- [ ] Design **four** car-window gas-blast animations, each showing a **jeans-covered backside popping out the window** and a cloud originating from it, with enemy ramming/knockback cues; **no diagonal art planned**.
- [x] **Implement accepted Option 3 Atari title and opening input for the Stage 1 prototype:** Original ANTIC E/DLI title, console START and both cutscene FIRE transitions are integrated into the playable v0.5 XEX and broadly user-tested in Atari800. (The separate completed Stage 1 integration task below covers game-flow wiring.)
- [ ] **Finalize full-game opening/result presentation:** Polish title and Meet the Crew typography/visuals as needed, and produce game-wide failure/game-over/victory/end-of-cycle screens and transitions. The selected v1 title and existing START/FIRE controls already work; do not revive visually rejected PMG title v2/v2.1 or add the deferred dinner-table scene.
- [x] **Convert selected Taco Smell arrival Option 3 into a standalone mixed Atari scene and visually test XEX:** **160×128 ANTIC E artwork** with horizontal DLI palette bands, **eight 40-column ANTIC 2 text rows** and approved three-line story. User verified in **Atari 800 Emulator 5.2.0 (2026-10-29)** and said “looks good.” **Does not include functional Fire input or scene integration; the tested XEX and supporting binaries are now committed under `assets/arrival/`.**
- [ ] **Later polish Meet the Crew text legibility:** consistent glyph sizes/baselines and spacing; clearer line wrapping/left alignment; comfortable separation of **MEET THE CREW**, the exact introductory quote and **FIRE TO CONTINUE**. Preserve the current image composition without game logo, background Taco Smell sign or character-name labels.
- [ ] Finalize box and cartridge artwork for production.

## Phase 6 — Sound and Music
*Goal: Give the game a distinctive 1982 arcade personality.*

- [x] Compose and approve **Arcade Rock** as the original 148-BPM title theme, convert to a four-channel POKEY player and standalone title XEX. **User auditioned it successfully in Atari800 on 2026-10-30.**
- [x] Compose and approve **Funky Gas Attack** as the original 110-BPM crew/arrival theme, with two POKEY standalone XEXs and source/MP3 assets. **User auditioned both successfully in Atari800 on 2026-10-30.**
- [x] **Audition standalone title/crew/arrival POKEY music in Atari800:** The user listened to all three XEXs on 2026-10-30 and said they sound great; original Arcade Rock/Funky Gas Attack melodies are approved.
- [ ] **Perform final POKEY audio QA:** Evaluate fine pitch/mix/looping/mute behavior, interactions with gameplay SFX, PAL timing if supported and a real Atari 800XL where available; no physical-hardware audio validation has been recorded.
- [x] **Implement Stage 1 gas-blast POKEY prototype sound:** v0.5 includes a brief original ~10-frame gas-whoosh effect; user broadly accepted gas blasting, but the individual sound is **not** separately verified by an itemized audio playtest.
- [ ] **Finalize gas-blast sound effects for the full game:** Tune/replace indoor whoosh if necessary, produce distinct four-window **car** effects and verify audio timing/mixing alongside music and pressure warnings.
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
- [x] **Stage 1 prototype:** Integrate Title → Meet the Crew → Arrival → Taco Smell escape with START/FIRE and original POKEY music. Dinner-table scene intentionally excluded; full-game transitions still open.
- [ ] Play through a complete four-level cycle.

## Phase 8 — Testing and Release
*Goal: Produce a stable game that works on Atari 800XL hardware.*

- [x] **Test the integrated opening-sequence v1 XEX in Atari800**: user confirmed the single continuous introduction worked great with title START, crew/arrival FIRE, and the temporary Stage 1 screen (2026-10-30).
- [x] **Playtest Stage 1 v0.2 basic room-to-room design in Atari800:** User confirmed room transitions work and reported stage too easy/short; this is **not** exhaustive validation of every room/AI/door edge.
- [x] **Playtest Stage 1 v0.3 in Atari800 (game-feel evaluation)**: user completed the prototype trial; pressure feels somewhat better, but Billy is slow/cumbersome and gas-blast mechanics are terrible. **This is a usability verdict, not proof that every detailed v0.3 mechanic was exhaustively validated.**
- [x] **Playtest v0.4 Billy movement feel in Atari800**: user confirmed smooth movement and diagonal walking work well. **Only movement feel was explicitly accepted; full door/enemy/collision/audio regression remains for subsequent prototype validation.**
- [x] **Playtest Stage 1 v0.5 gameplay feel in Atari800:** User reported gas blasting **good for now**; extensive eight-way/knockback/collision/audio/PMG/performance regression remains open in `STAGE1_REGRESSION_CHECKLIST.md`.
- [x] **Test/reject title PMG v2 and v2.1 in Atari800:** User screenshots showed unwanted highlight/artifacts; retain original non-PMG title v1, preserve alternate artifacts only as history.
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

- **v0.37 — 2026-11-03:** Split mixed-status work into completed **Option 3 title implementation**, **Atari800 POKEY audition**, and **Stage 1 blast SFX prototype**, while retaining separate open full-game title/result art, detailed audio QA and final gas-SFX tasks. Correct rejected title PMG and approved music statuses. **71/175 completed (41%), 104 open**. This is documentation-only; not a new emulator/hardware test or gameplay change.

- **v0.36 — 2026-11-02:** Stage 1 cleanup: v0.5 merged/tagged and **user-playtested with acceptable gas blasting**, authoritative [STAGE1_DESIGN.md](STAGE1_DESIGN.md), deferred issues, regression checklist, root README and Codex workflow; v0.1–v0.5 design proposals/handoffs archived with redirects. Corrected Stage 1 implementation/intro/title-v2 test statuses and preserved future-stage tasks. **68/172 complete, 104 open**; no gameplay changes or physical 800XL sign-off.

- **2026-11-01 v0.5 implementation update:** Built native eight-direction hold-to-aim gas cones over unchanged v0.4 movement, two-plane jeans/body poses, three-wave cloud restoration, animated collision-aware knockback/BONK/stagger, renewable charges, HUD and short POKEY whoosh. All 18 v0.5 CPU tests, 15 unchanged v0.4 tests and four validators pass. Recorded CPU-only representative profile; preserved all earlier XEXs. Atari800 pose/cloud/audio/fun acceptance remains pending, no merge and no checklist-total changes.


- **v0.35 — 2026-11-01:** Confirms **eight-way indoor gas blasting for Stage 1 v0.5**, matching Billy's eight-direction walking. Updated Codex guidance, spec, numeric JSON, validator, cloud/knockback diagonal vectors and corner-blocking tests. **Four-way driving/car blasts remain unchanged**. Checklist remains **56/172 complete, 116 open**; this changes a design requirement, not an implementation milestone, and no v0.5 XEX was built.

- **v0.34 — 2026-11-01:** User played Codex's **v0.4** XEX and approved smooth Billy walking and diagonal controls. Preserves that baseline and defines v0.5's signature gas-blast redesign: hold FIRE with eight-way aiming (FIRE-first supported), butt-pivot/jeans pose, 3-wave expanding cloud, 3-tile animated knockback, furniture/worker collision gags, stun, three renewable charges, cooldown, HUD and short POKEY effect. JSON, design specification, validator and Codex handoff committed. Marks v0.4 **movement-feel** test complete, not exhaustive v0.4 regression, and adds pending v0.5 Atari800 test. **56/172 complete, 116 open**; v0.5 XEX not built here.

- **v0.33 — 2026-11-01:** Records user's completed v0.3 Atari800 playtest: pressure improved slightly, **movement slow/cumbersome, indoor blast terrible**. Adds **Stage 1 v0.4 movement spec**, numeric rules JSON and Codex handoff: smooth fractional movement, 8-way walking, normalized diagonal speed, wall-slide, pixel-aware collisions, 3-room topology/3-worker pursuit preserved, temporary inactive gameplay FIRE and v0.5 blast redesign. Marks v0.3 experiential playtest complete but not all detailed mechanics verified; adds pending v0.4 test. **54/170 complete, 116 open**. No v0.4 XEX built here.

- **v0.32 — 2026-11-01:** User played room-to-room Stage 1 v0.2 in Atari800 and said it works but is too easy and too short; transitions were not an issue. Kept fixed rooms and prepared **v0.3 gameplay-pressure design** with three total hazmat workers, faster follow, first indoor directional blast, stun/knockback/cooldown, gameplay tuning JSON, validator and Codex handoff. No v0.3 binary has been built or played. **52/168 complete, 116 open**, with design milestone completed and v0.3 emulator test still open.

- **v0.31 — 2026-11-01:** Taco Smell Stage 1 v0.2 design changed from horizontally scrolling 48×22 v0.1 map to **three non-scrolling 40×22 rooms** and two footer rows. Created canonical room maps/JSON, four reciprocal transitions, one persistent pursuer, validator, preview, Codex handoff. Pharmacy may scroll and grocery scrolling aisle chase may involve police/hazmat/townspeople. Preserved v0.1 on the existing feature branch; **no v0.2 XEX is built**. Added `AGENTS.md` and partial `TECHNICAL_DESIGN.md`, retained game-wide technical task as open. **51/166 complete, 115 open**.

- **v0.30 — 2026-11-01:** Creates and commits Codex-ready **Taco Smell Stage 1 tile-map contract** (`docs/archive/stage1/STAGE1_TILEMAP_SPEC.md`, `assets/maps/taco_smell_stage1_v01.map`, JSON metadata and technical preview, and `tools/validate_taco_smell_stage1.py`). Validated 48×22 dimensions, two room passages, spawns, exit and cardinal reachability of all 751 traversable tiles. Marks map-design artifact complete; no playable stage XEX exists. **49/164 complete, 115 open**; Indoor Gameplay 1/13.

- **v0.29 — 2026-11-01:** User tested the corrected PMG v2.1 in Atari800 and supplied a screenshot; although the original single-line DMA glitch is reduced, ~220 isolated overlay highlights across the title degrade the artwork. The v2.1 DLI extension also contains excessive per-band register operations for one bitmap scanline, leaving additional raster-timing risk. Both PMG versions are **not accepted**. Keep v1 as the working baseline and pursue a deliberate pixel-art/palette enhancement instead; no checklist completion count changes.

- **v0.28 — 2026-10-30:** Fixes broken PMG v2 DMACTL single-line mismatch ($2E→$3E), adjusts 24 blank-line vertical origin and strengthens the visual-text-clearance test; corrected v2.1 binary/source committed, pending real Atari800 visual evaluation. Earlier v2 screenshot exhibited stray pixels. v1 unaffected.

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
