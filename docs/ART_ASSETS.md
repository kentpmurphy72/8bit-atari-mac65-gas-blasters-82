# Gas Blasters '82 — Art Assets and Visual Direction

**Version:** 0.1  
**Date:** 2026-10-25  
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

The hero is a **young adult man**, not the older, heavier, mustached character used in an early concept.

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
| Police cars | Pursue and obstruct the player | Confirmed role; look TBD |
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

### Reusable environment categories

- **Restaurant interior:** tables, counters, exits, hazmat-friendly paths.
- **Highway:** vertical-scrolling road, lanes, roadside scenery, traffic, player and friendly/police vehicles.
- **Pharmacy:** aisles, shelves, Gas-Nix product display/collection location.
- **Grocery store:** aisles, shelves, toilet-paper pickup location.
- **House exterior:** yard/driveway/front door, hazmat positions.
- **House interior:** rooms, corridors, officers, bathroom approach.
- **Bathroom:** final destination / victory presentation.

The game currently proposes nine stages per restaurant but may consolidate some locations; create reusable tiles/props where practical.

## 6. Visual gameplay feedback / HUD

**Needed in some form:**
- Visible gas-pressure meter with clearly understood **0–100%** range.
- Strong visual warning at/near **100%** (explosion threshold).
- Recognizable **Gas-Nix** pickup sprite/icon.
- Clear distinction among the player's car, the friends' car and police vehicles.
- Signals for collision/capture, pressure relief and stage completion.
- Restaurant/level introduction and stage transition screens.
- Bathroom success moment and repeat-cycle transition.

**Open:** pressure-meter placement, scores/lives display, exact colors, screen dimensions, font, animation frames and sound-linked effects.

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
| P0 | Police car | Distinct hazard sprite |
| P0 | Gas-Nix pickup | Small clear collectible icon |
| P0 | Road | Scrollable roadway/lane markings |
| P0 | Gas pressure HUD | Meter and critical warning |
| P1 | Taco Smell exterior/interior | Level 1 introductory scene and playable area |
| P1 | Hazmat crew | Small readable enemy sprites |
| P1 | Gas blast effect | Temporary cloud/bomb effect |
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
5. Select car appearances and the friends' visual identity.
6. Decide whether all four restaurants get separate key art and/or tile sets.
7. Simplify the box artwork for a legible cartridge label at real dimensions.
8. Reconcile the cover's “TOILET PAPER SOLD OUT AGAIN!” gag with the need to acquire toilet paper.
9. Decide final package brand/logo use and production dimensions.

## 12. Change log

- **v0.1 — 2026-10-25:** Captures the preferred retro box/cartridge concept, young hero continuity, hazmat figures added at Taco Smell, reduced green-gas effect, removed slogan, four restaurant names, and preliminary production asset list.
