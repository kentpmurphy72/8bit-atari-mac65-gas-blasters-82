# Gas Blasters '82 — Art Assets and Visual Direction

**Version:** 0.15  
**Date:** 2026-10-26  
**Status:** Early art direction / living asset inventory  
**Primary target:** Atari 800XL  
**Companion document:** docs/GAME_DESIGN.md

> This document records the current visual direction and asset needs. The images produced in the design conversation are concept mockups, not finalized production files, print templates, or Atari-compatible in-game graphics.

## 1. Visual identity

**Working direction:** energetic early-1980s arcade packaging with hand-painted/pulp comic illustration, bold typography, exaggerated slapstick action, and readable visual storytelling.

**Tone:** humorous, frantic and cartoonish; the environmental-emergency premise is absurd rather than scary or realistic.

**Recognizable motifs:**
- Title **GAS BLASTERS '82** in prominent vintage arcade lettering.
- Restaurant brand **TACO SMELL** for Level 1.
- Green gas effects as a recurring accent, **not** a huge opaque mass obscuring the art.
- Yellow hazmat suits, black/dark visors, police lights and road action.
- Hero's frightened expression and oversized dynamic running pose.
- Scenes from the trip: restaurant, police chase, pharmacy, grocery store, suburban home.

No pixel-art specification or final color codes have been approved. Packaging concept art may use more colors/detail than the Atari 800XL game itself.

## 2. Current selected packaging concept — Working visual reference

The latest edited concept from the design conversation is the **preferred working direction** for the box front and matching cartridge label. It evolved from the multi-scene comic/pulp cover option.

### Box front composition

**Retain:**
1. Large **GAS BLASTERS '82** title, with yellow **GAS**, bold red **BLASTERS**, and yellow **'82**.
2. A younger male hero running in alarm at center (see character continuity specification below).
3. **Taco Smell** restaurant/sign with **multiple hazmat responders** near the storefront.
4. A police pursuit scene.
5. A pharmacy scene.
6. A grocery/toilet-paper scene.
7. The hero running toward a house at night.
8. A **subdued**, lighter amount of green gas, so the rest of the illustration is easy to see.
9. The vintage box-and-cartridge visual treatment, including the existing retro stripe details.

**Do not include:** the phrase **“TACOS IN ... GAS OUT.”** It was tried and then explicitly removed.

**Existing concept copy:** **“A HIGH-SPEED ESCAPE ADVENTURE”** appears as a small cover line. Treat this as current concept-art copy, not a final product tagline.

The concept mockup includes a toilet-paper sign reading **“SOLD OUT AGAIN!”**; this is visually funny but creates a possible conflict with the gameplay objective of *acquiring* toilet paper. Revisit it when finalizing the cover.

### Cartridge label

The cartridge label should share the same game title, visual style, young protagonist, and key action imagery as the box. It is a **simplified adaptation** of the cover, not a miniature reproduction of every vignette.

**Open:** actual cartridge shell shape, label dimensions, bleed, print resolution, font selections, and production process.

## 3. Main hero — continuity specification

The hero is **Billy Blaster** (**confirmed name**), a **young adult man**, not the older, heavier, mustached character used in an early concept. Use **Billy Blaster** consistently for character art, sprites, opening-story graphics, and production asset names.

**Current established visual cues:**
- Youthful face, shaggy/messy brown hair.
- Red-and-white baseball/trucker-style cap.
- Frantic wide-eyed, worried expression.
- Red jacket or open red plaid overshirt.
- White T-shirt with a taco graphic.
- Blue jeans.
- White sneakers with red accents.
- Energetic, exaggerated running pose.

**Consistency requirement:** the small hero in the **grocery-store scene** and the small hero **running toward/into the house** must look like the same young man shown in the center of the box, with the same cap, outfit, general build and colors. The cartridge hero must also match.

**Still needed:** authoritative character turnaround, pixel-sprite proportions, walk/run poses, driving representation, direction-facing frames, and gas-blast animation.

### Introductory text requirement

The game must display the exact following text in an opening/title introduction or another appropriate **in-game** story moment:

> Meet Billy Blaster. He's got a fast car, great friends, and a stomach that's about to become a national emergency.

If needed for Atari 800XL display limits, split it into successive screens or lines while preserving the complete wording and punctuation. The placement, typography, transitions and character illustration are still to be designed.

## 4. Supporting characters and entities

| Asset / character | Required visual role | Status |
|---|---|---|
| Hazmat crew | Several yellow-suited responders at restaurant; also house exterior | Confirmed roles; design provisional |
| Police officers | Pursuit vehicles and house interior | Confirmed roles; design provisional |
| Friends | Share restaurant meal and occupy separate lead car on road | Confirmed role; appearances TBD |
| Pharmacy staff, patrons, manager | Impede Gas-Nix pickup | Confirmed groups; appearances TBD |
| Grocery staff, shoppers, manager | Impede toilet-paper pickup | Confirmed groups; appearances TBD |
| Player car | Distinct from friend/police cars | Confirmed role; color/model TBD |
| Friends' car | At upper portion of vertical road view; drops Gas-Nix on drives 2 and 3 | Confirmed role; color/model TBD |
| Police cars | Pursue and deliberately bump the player off-road | Confirmed role; look TBD |
| Hazmat vans | Pursue and shove the player off-road | Confirmed role; look TBD |
| Gas-Nix package | Clearly collectible medicine pickup on later road stages | Confirmed purpose; package design TBD |
| Toilet paper | Readable grocery-store objective | Confirmed purpose; look TBD |

Names such as “Hazmat Hank” or “Officer Sniff” were brainstorming suggestions and have **not** been approved as character names.

## 5. Location and environment art

### Restaurant themes — Confirmed names; visual treatments open

| Level | Restaurant | Possible artistic direction (proposed only) |
|---|---|---|
| 1 | **Taco Smell** | Familiar exaggerated fast-food taco shop, sign, booths, hazmat arrival |
| 2 | **Casa de Gas** | Sit-down Mexican restaurant with a distinct entrance and dining layout |
| 3 | **The Bean Machine** | Bean-focused cafeteria / casual restaurant motifs |
| 4 | **The Blazing Burrito** | More dramatic fiery branding, energetic atmosphere |

Each restaurant needs its own recognizable title/location art. Whether it also gets a completely unique tile set, stage palette, enemy skins or gameplay geometry is **open**.

### Driving-stage perspective — Confirmed

Road stages (2, 4, and 6) use a **Spy Hunter-style overhead/top-down view**:

- Draw the player's car **from above**, **nose pointing toward the top of the screen**, near the **bottom of the play area**.
- Create **downward-scrolling roadway and roadside graphics** to imply forward movement.
- Support winding sections that **narrow the paved road from 75% to 40% of the left driving playfield over approximately 4 seconds**, weave left/right at the narrow width, and **widen from 40% to 75% over approximately 4 seconds** when the winding ends. Keep both shoulders **6.25% of driving-playfield width each**, immediately adjacent to the road; remaining space becomes grass. When centered at minimum width, show **23.75% grass / 6.25% shoulder / 40% road / 6.25% shoulder / 23.75% grass**. In a weave, shoulder widths remain fixed to road edges while grass areas may become asymmetrical. These times/widths are design targets awaiting first-prototype validation.
- Design a **center divider island** that scrolls down from the top of the roadway and creates a visually readable **left/right fork** (reference: supplied *Spy Hunter* center-island screenshot). The island is physically distinct from the safe shoulders and grassy off-road zones.
- Show a **flashing GREEN arrow pointing straight UP**, positioned **near the top of the left driving playfield** on the **LEFT or RIGHT side** to indicate the preferred branch through the center-island fork. It begins **ON** and flashes **0.25s ON / 0.25s OFF**, starting **approximately 2 seconds before the divider island first appears at the top of the screen**. Keep flashing after the island becomes visible; **remove the arrow after Billy passes the fork decision point**. Do not render a conventional sideways-pointing left/right arrow: branch selection is conveyed by the side on which the upward arrow appears. Actual pixel coordinates, graphics-mode-dependent frame counts, decision-point collision coordinates, arrow sprite dimensions and island art measurements remain open.
- **Straight-road baseline proportions within the left 2/3 driving playfield (left to right):** **6.25% grass**, **6.25% reduced-traction shoulder**, **75% paved roadway**, **6.25% reduced-traction shoulder**, **6.25% grass**. **Classify the center of Billy's car**, not its outer sprite/tire contact, at the local road boundary. Center in **grass** runs/resumes the off-road timer; center on **shoulder** pauses the timer at its value (with reduced traction); center on **paved road** resets it to zero. At **2.0 seconds of grass time since last paved-road contact**, the car explodes and loses one life. Derive exact pixel boundaries from these percentages **after selecting graphics mode**; no pixel values or sprite sizes are final.
- Create the progressive effects for accumulated **grass** time: **skid (0–0.5s); car shake with reduced steering (0.5–1.0s); warning sound and smoke (1.0–1.5s); critical warning and heavier smoke (1.5–2.0s); explosion (2.0s)**. The timer/effect escalation **pauses** on shoulder and **resets** on paved road. Consider readability of paused warnings, without changing the confirmed timing rules.
- Place the friends' lead car **toward the top** of the driving playfield.
- Draw both **police cars and hazmat vans** pursuing from **behind and alongside** the player, with collision/ramming and displacement animations or cues.
- For the **first prototype**, create **four-direction gas blasts only** (front, back, left, right) to knock back pursuers. Diagonal effects are a **possible later enhancement**, not part of the first prototype.
- In road stages **after** the pharmacy, show **Gas-Nix packages** falling/moving downward from the friends' car toward the player.
- Ensure car silhouettes and pickups remain distinct at actual Atari 800XL display resolution.

**Confirmed:** movement is **free left/right**, not restricted to fixed lanes. Winding sections narrow **75% → 40% in ~4s** and widen **40% → 75% in ~4s**, maintaining **6.25% shoulders**; forks use a **center island** with a **flashing green UP arrow** beginning ~2 seconds before island appearance; flash at **0.25s ON / 0.25s OFF** until Billy passes the decision point. Grass triggers the off-road timer as defined by the car-center rules, rather than an immediate crash. **Still open:** game-feel validation of narrowing, island/arrow pixel shapes and exact coordinates, frame-based timing, decision-point detection, curve severity, car colors, sprite dimensions, graphics modes, and vertical range of movement. The reference establishes the camera perspective, **not** a pixel-perfect replica of *Spy Hunter*.

### Reusable environment categories

- **Restaurant interior:** tables, counters, exits, hazmat-friendly paths.
- **Highway:** confirmed overhead/upward-facing vehicle perspective with downward-scrolling winding roads, occasional two-way forks and indicated route, roadside/shoulder graphics, traffic, and player/friends/police/hazmat-van vehicles. Choosing the wrong branch **adds +1.0 mile once** to the remaining distance, **without slowing the countdown** or causing an immediate wreck. **Branches visually rejoin soon afterward as one normal 75%-width road**, rather than staying split for the entire extra mile. Free lateral steering and four-sided blast knockback are confirmed. Actual display-pixel dimensions await graphics-mode selection.
- **Pharmacy:** aisles, shelves, Gas-Nix product display/collection location.
- **Grocery store:** aisles, shelves, toilet-paper pickup location.
- **House exterior:** yard/driveway/front door, hazmat positions.
- **House interior:** rooms, corridors, officers, bathroom approach.
- **Bathroom:** final destination / victory presentation.

The game currently proposes nine stages per restaurant but may consolidate some locations; create reusable tiles/props where practical.

## 6. Visual gameplay feedback / HUD

**Confirmed driving-stage screen partition:**
- **Left two-thirds:** road/driving playfield, with the **straight-road baseline split of 6.25% grass / 6.25% shoulder / 75% road / 6.25% shoulder / 6.25% grass** within that area.
- **Right one-third:** **fixed HUD/status panel**, displaying **lives, score, miles to the next destination/step, and gas-pressure meter**, plus other necessary indicators. **Wrong fork: add 1.0 mile to the HUD once; mileage then decreases at normal speed** while the gas meter keeps rising. The visual road merge happens before the added mile has elapsed.
- Roads can wind/fork inside the left playfield; winding segments use the confirmed **40% minimum paved-road width and fixed 6.25% shoulders**, while left/right grass margins can differ as the roadway weaves. **Never use the HUD area as extra driving road space.**
- This split applies to road stages (2, 4, and 6); no comparable layout is approved yet for indoor stages.
- The exact HUD pixel dimensions, graphics mode, font and styling remain open; left/right placement and design ratios are confirmed.

**Needed in some form:**
- Visible gas-pressure meter with clearly understood **0–100%** range.
- Strong visual warning at/near **100%** (explosion threshold).
- Recognizable **Gas-Nix** pickup sprite/icon.
- Clear distinction among the player's car, the friends' car and police vehicles.
- Signals for collision/capture, pressure relief and stage completion.
- Distinct **off-road warning** effects (skid, shake, smoke, critical smoke, sound, explosion and lost-life cue) separate from gas-meter warnings.
- Restaurant/level introduction and stage transition screens, including in-game delivery of Billy Blaster's required introduction.
- Bathroom success moment and repeat-cycle transition.

**Open:** exact HUD panel orientation and dimensions, pressure-meter styling, lives/other indicators, exact colors, font, animation frames and sound-linked effects.

Earlier UI sketches were illustrative and are **not** approved pixel-perfect layouts.

## 7. Gas effects — explicit refinement

The cover initially used conspicuous green gas clouds. The selected concept intentionally **reduces their density and visual prominence**.

**For future iterations:**
- Use smaller, lighter, localized green puffs or wisps.
- Keep faces, actions, signs and objectives legible.
- Let gas effects communicate movement and comedy without taking over the composition.
- Avoid assuming the in-game effect must use translucent blending: the final Atari effect will need a hardware-appropriate representation.

## 8. Packaging text and branding

**Preferred text/content:**
- **GAS BLASTERS '82**
- **TACO SMELL** (restaurant signage)
- **A HIGH-SPEED ESCAPE ADVENTURE** (currently shown in concept art)

**Excluded by explicit revision:**
- **TACOS IN ... GAS OUT**

**Platform labeling:** Atari 800XL / Atari 8-bit compatibility is part of the product concept. The mockups include Atari-style branding and logos, but **do not assume an official Atari trademark or logo may be used in a released commercial package without appropriate rights/permission**. Decide final legal/brand treatment before print/release.

**Proposed original-fictional-brand work:** make a readable Gas-Nix box/label that suggests an old-fashioned pharmacy product without copying a real Gas-X package.

## 9. Asset production inventory

These are **planned assets, not completed assets**.

| Priority | Asset | Minimum first-pass need |
|---|---|---|
| P0 | Hero | One recognizable sprite plus movement frames |
| P0 | Player car | Readable road sprite |
| P0 | Friends' car | Distinct road sprite |
| P0 | Police car | Distinct hazard sprite; ramming/PIT-style knockback interaction |
| P0 | Hazmat van | Large readable road enemy able to bump the player toward the shoulder |
| P0 | Gas-Nix pickup | Small clear collectible icon |
| P0 | Road | Downward-scrolling roadway; weaving width transitions 75%→40% in ~4s and 40%→75% in ~4s, constant 6.25% shoulders, variable grass, center-island forks |
| P0 | Off-road recovery and crash FX | Skid, shake, smoke, heavy smoke, warning/critical states, and 2.0s explosion/lost-life cue |
| P0 | Fork arrow | GREEN upward arrow near top on preferred left/right side; starts ~2s before island appears; flashes 0.25s ON / 0.25s OFF and vanishes after Billy passes fork decision point |
| P0 | Driving screen layout | Left 2/3 playfield: nominal 6.25% grass + 6.25% shoulder + 75% road + 6.25% shoulder + 6.25% grass; right 1/3 fixed HUD for lives, score, miles remaining, gas |
| P0 | Gas pressure HUD | Meter and critical warning |
| P1 | Taco Smell exterior/interior | Level 1 introductory scene and playable area |
| P1 | Hazmat crew | Small readable enemy sprites |
| P1 | Gas blast effect | First prototype: front/rear/left/right knockback only; diagonal variants deferred |
| P1 | Pharmacy environment | Playable room/map and medicine location |
| P1 | Grocery environment | Playable room/map and toilet paper |
| P2 | Home exterior/interior/bathroom | Final stage visuals |
| P2 | Restaurants 2–4 | Distinct identity artwork and environment variations |
| P2 | Full packaging art | Refined box/cartridge layouts, print-ready later |

Priorities describe a **proposed prototype sequence**, not a development commitment.

## 10. Source files and art handoff

- The latest packaging image currently exists in the **ChatGPT design conversation**. It should be explicitly exported/added to the repository before Codex or other contributors rely on it.
- Suggested repository area: **assets/cover-art/**.
- Record the chosen image's filename and version once committed; do not assume the Markdown file itself contains the image.
- Preserve original high-resolution art separately from crops, resized labels and possible print-ready versions.
- Do not treat AI-generated mockups as layer-separated/editable source artwork.
- In-game art must eventually be adapted to actual Atari 800XL graphic, palette, sprite and memory constraints. Those technical constraints have **not** yet been selected.

## 11. Open art decisions

1. Lock the protagonist's final model sheet so every scene/sprite matches.
2. Decide visual perspective for indoor sections (overhead or side view).
3. Select 800XL graphics modes, sprite/tile dimensions, palette and animation budget.
4. Draw a distinctive **Gas-Nix** box/pickup.
5. Select car appearances and friends' visual identity; derive exact Atari pixel widths and implement center-of-car boundary checks when the graphics mode and vehicle representation are chosen. **Detection rule and grass/shoulder/road timer transitions are already confirmed**.
6. Decide whether all four restaurants get separate key art and/or tile sets.
7. Simplify the box artwork for a legible cartridge label at real dimensions.
8. Reconcile the cover's “TOILET PAPER SOLD OUT AGAIN!” gag with the need to acquire toilet paper.
9. Decide final package brand/logo use and production dimensions.
10. Create the **center-island two-branch fork** and **flashing green upward arrow** near top on the selected left/right side; **implement the confirmed 0.25s ON / 0.25s OFF cadence, ~2-second pre-island start and removal after Billy passes the decision point**. Determine exact pixel placement, sprite measurements and practical timing/collision implementation. Design a legible **+1.0-mile remaining-distance change** on the wrong fork (specific text/animation still open); draw the two branches **merging soon back into one normal 75%-width road**, independent of the extra mileage. Implement the confirmed **right-side HUD** within the 2/3-left / 1/3-right layout; decide final pixel dimensions.
11. Design police-car and hazmat-van ramming effects and four-sided gas blasts; decide whether diagonal blast sprites are warranted after controller testing.
12. Design a legible in-game opening/introduction presentation for Billy Blaster's required line.
13. Design narrowing/weaving tiles and road-edge transitions for the confirmed **75%→40% (~4s)** and **40%→75% (~4s)** changes; keep shoulders 6.25% each and validate the effect during prototyping.

## 12. Change log

- **v0.15 — 2026-10-27:** Updates wrong-fork visuals to a one-time +1.0-mile HUD penalty with normal distance countdown; branches automatically merge relatively soon into a normal-width road without remaining separate for the extra mile. Exact merge animation timing and any optional HUD message remain open. Supersedes historical v0.5 mileage-slowdown concept.
- **v0.14 — 2026-10-26:** Specifies flashing green UP fork arrow near top on preferred left/right side: start ~2s before island first appears, repeat 0.25s ON/0.25s OFF, remove after Billy passes the fork decision point. Actual pixels, frame conversions and display resources await architecture/prototype.
- **v0.13 — 2026-10-26:** Sets 40% minimum road width, approximately four seconds to narrow and four to widen, unchanged 6.25% shoulders, and 23.75% grass on each side when centered at minimum width. Art and timing remain unimplemented and subject to prototype validation.
- **v0.12 — 2026-10-26:** Specifies car-center zone classification, grass time runs/resumes, shoulder time pauses, paved-road return resets, and two-second exposure/lost-life feedback. Defer pixel coordinates and center representation until graphics mode is chosen.
- **v0.11 — 2026-10-26:** Adds temporary road narrowing during weaving curves with return to normal width; center-island split forks; flashing green upward-pointing advance arrow on left/right side near top, starting about 2 seconds before island first appears. Minimum road width, blink rate and sprite sizes remain open.
- **v0.10 — 2026-10-26:** Confirms 6.25% shoulder next to road and 6.25% grass outside it on each side of the straight-road playfield, retaining a 75% roadway. Collision/pixel implementation remains open.
- **v0.9 — 2026-10-26:** Confirms straight-road visual width (75% of left playfield), 12.5% roadside strips on each side, fixed HUD in right third showing lives/score/miles/gas, and flexible margins for winding/forking roads. Exact shoulder/grass split remains open.
- **v0.8 — 2026-10-26:** Defines shoulder/off-road art cues and escalating two-second warning animation/audio through explosion and one-life penalty, preserving unresolved exact widths.
- **v0.7 — 2026-10-25:** Names the young protagonist Billy Blaster and specifies the exact introductory line to include in-game; layout and timing remain open.
- **v0.6 — 2026-10-25:** Sets first-prototype gas effects to four directions; eight-way art deferred. Protagonist name remains open.
- **v0.5 — 2026-10-25:** Adds police and hazmat vans capable of shoving player off road, directional knockback gas effects on all four sides of the car, and wrong-fork detours with slower distance countdown. Eight-way diagonal effects remain optional pending control decision.
- **v0.4 — 2026-10-25:** Specifies blinking fork-direction arrow near the top of the driving screen, appearing a few seconds before the fork. Precise timing and visual treatment remain open.
- **v0.3 — 2026-10-25:** Adds free lateral steering, winding roads, two-way forks with arrow, off-road crash boundary, and a driving-screen split of 2/3 playfield to 1/3 HUD. Exact presentation remains to be designed.
- **v0.2 — 2026-10-25:** Locks road-stage art direction to an overhead view with upward-facing cars and downward-scrolling roadway; notes lead-car, pursuit, and Gas-Nix pickup placement. Driving-lane layout is still open.
- **v0.1 — 2026-10-25:** Captures the preferred retro box/cartridge concept, young hero continuity, hazmat figures added at Taco Smell, reduced green-gas effect, removed slogan, four restaurant names, and preliminary production asset list.
