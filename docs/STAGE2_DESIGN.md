# Gas Blasters '82 — Stage 2: Drive to the Pharmacy

**Document:** Stage 2 Gameplay and Technical Design  
**Milestone:** v0.1 — Basic Driving Prototype  
**Date:** 2026-11-08  
**Target:** Atari 800XL, stock 64 KB, native 6502 Atari XEX  
**Working branch:** `feature/stage2-pressure-destination-v0.2` (accepted v0.1 preserved on `main` at tag `stage2-v0.1`)  
**Status:** **v0.1 driving mechanics accepted after user Atari800 playtest of r3 (2026-11-04).** r3 is the current playable driving baseline; future extra upward car travel and polish are deferred. **v0.2 gas pressure and pharmacy destination is the next design milestone, not yet implemented.** Initial two-minute drive, 20–100 MPH speed range, 2-mile destination and 2:45 gas-failure deadline are provisional balancing targets (Section 16). **Approved pressure-warning, shake, three-lives, explosion, and FIRE-retry behavior is recorded in Section 17. The pharmacy-arrival cutscene and FIRE-to-complete flow are confirmed in Section 18; the exact native-speed-to-MPH mapping is approved in Section 19, the fixed HUD presentation is approved in Section 20, and terminal tie/replay controls are approved in Section 21.**
**Repository destination:** `docs/STAGE2_DESIGN.md`  

## 1. Purpose and authority

This document specifies the **first playable driving prototype** for Stage 2 of *Gas Blasters '82*. It is intentionally narrower than the full Stage 2 gameplay concept. The immediate question is whether driving Billy's car feels smooth, responsive, and fun on the Atari 800XL. **User playtest (2026-11-04):** the initial v0.1 road/steering demo was fine but the car remained vertically stationary. A new v0.1 revision must move the car up-screen when accelerating and down-screen when braking, in addition to changing road-scroll rate.

- `docs/GAME_DESIGN.md` is authoritative for overall story, road geometry proportions, off-road rules, police/hazmat behavior, forks, and four-way car gas blasts.
- `docs/STAGE1_DESIGN.md` and tag `stage1-v0.5` describe the accepted restaurant prototype; **do not change Stage 1** as part of this work.
- `docs/TECHNICAL_DESIGN.md`, `docs/REPOSITORY_WORKFLOW.md`, `AGENTS.md`, and existing XEX build tooling govern platform, safety, workflow, and evidence requirements.
- This document is authoritative for what **v0.1 must implement**, what it **must not yet implement**, and what prototype parameters remain adjustable.

**Decision labels:** **Confirmed** = approved design choice. **v0.1 target** = required for this prototype, but implementation/feel can be tuned. **Provisional** = Codex may choose a practical initial value, document it, and solicit playtest feedback. **Deferred** = explicitly excluded from v0.1.

## 2. Story context and player objective

Billy Blaster has escaped Taco Smell and is driving toward a pharmacy where he hopes to obtain **Gas-Nix**, a fictional gas-relief medicine. The complete Stage 2 will challenge him to reach the pharmacy before gas pressure rises to 100%. A separate vehicle carries Billy's friends; they will drop Gas-Nix on *later* road stages, **not** during this first pharmacy drive.

**v0.1 gameplay objective:** Control Billy's upward-facing car on a continually downward-scrolling, initially straight highway. Test the sense of speed, lateral steering, road scale, and HUD readability. This is a **free-driving demo**: no destination arrival, gas-based failure, or opponents yet. A restart control and continuously running demo are sufficient to evaluate feel.

## 3. Release scope

| Element | v0.1 requirement | Status |
| --- | --- | --- |
| Standalone XEX runnable in Atari800 | Yes; do not integrate into opening/Stage 1 XEX | v0.1 target |
| Top-down road with downward scrolling | Smooth and continuous; visible lane-marking motion | Confirmed |
| Billy's car | Recognizable upward-facing sprite, starting low and moving up/down with speed | Confirmed, revised v0.1 |
| Steering | Smooth free left/right movement; no lane snapping | Confirmed |
| Forward motion | Automatically advances even with joystick neutral | Confirmed: Option A |
| Speed control | Up accelerates and moves car up-screen; Down brakes and moves car down-screen; speed remains positive | Confirmed: Option A + v0.1 refinement |
| Road zones | Straight road, shoulders, grass, and visible lane markings | v0.1 target |
| Speed-linked vertical positioning | Actual car sprite Y changes smoothly with speed, within bounded visible limits | Confirmed, revised v0.1 |
| Display partition | About left 2/3 gameplay, right 1/3 fixed HUD | Confirmed |
| HUD fields | GAS %, MI / distance, SCORE, LIVES as **static placeholders** | v0.1 target |
| Optional HUD telemetry | Live SPEED and/or current ZONE if feasible | Provisional |
| START | Reset demo state safely | v0.1 target |
| Gas pressure simulation, pharmacy arrival | No | Deferred to v0.2 |
| Winding/narrowing roads, shoulder penalties, off-road explosion | No active penalties yet | Deferred to v0.3+ |
| Police, hazmat vans, collisions, forks, car blasts | No | Deferred to v0.3+ |
| Friends' lead car, Gas-Nix drops | No; no Gas-Nix is available yet | Deferred |

**Scope guardrail:** Focus engineering effort on a usable, smooth **driving loop**, not an integrated game or elaborate effects. Testable road-zone geometry may be represented now, but grass/shoulder behaviors must not silently introduce unapproved penalties in v0.1.

## 4. Screen design and road layout

### 4.1 View and player positioning — confirmed

- Overhead view, aesthetically inspired by the 1983 arcade *Spy Hunter*, without copying its assets.
- Billy's car points **up**. The **road scrolls down**, communicating forward travel.
- Billy's car starts near the lower portion of the road viewport (approximately 75–85% down) but **must not remain locked at that Y**. As speed rises the sprite advances **toward the top of the screen**; as speed falls the sprite retreats **toward the bottom**. This is smooth, bounded, physical sprite movement, not merely faster/slower background scrolling. At constant speed, including neutral input, it settles at and holds its speed-related Y. Exact top/bottom positions are tuning choices; keep the entire sprite visible.
- HUD remains fixed and readable on the right while the left pane scrolls.
- The car should be visually distinguishable from pavement, shoulders, and grass at normal Atari800 viewing size. Placeholder original pixel art is acceptable.

### 4.2 Playfield/HUD allocation — confirmed proportions

The whole display allocates **approximately 2/3 to driving** (left) and **1/3 to HUD** (right). Example if the selected mode has 40 character columns: **27 columns road pane / 13 columns HUD** (67.5% / 32.5%). The exact horizontal resolution/mode is a **technical choice**, not a newly approved canonical pixel division.

The straight road's target cross-section is measured **inside the driving pane**, *not* across the whole screen:

| Zone, left to right | Target fraction of driving pane |
| --- | ---: |
| Left grass | 6.25% |
| Left shoulder | 6.25% |
| Paved road | 75.00% |
| Right shoulder | 6.25% |
| Right grass | 6.25% |
| **Total** | **100.00%** |

For v0.1, approximate these proportions to the chosen hardware pixel/cell resolution and record the chosen **actual integer pixel/cell boundaries**. When pixel-level alignment is possible, keep the zone sizes as close to the target as practical. Do **not** make the road narrower merely to imitate a reference screenshot.

- Pavement: visually distinct from the shoulders; draw scrolling dashed centerline and/or lane markers.
- Shoulders: narrow, clearly recognizable transition strips along each road edge.
- Grass: visible on both outsides of the shoulders; distinct texture/color.
- Lane markers and roadside details visibly move downward to show speed. Avoid excessive clutter and flicker.
- At v0.1 the road is straight, stationary in horizontal position, and has a constant width. Winding geometry comes later.

**Future geometry constraint (not for implementation now):** Road narrows from 75% to 40% of the driving pane over about four seconds, may weave, then widens over about four seconds; shoulders stay 6.25% each. At centered 40% width, grass grows to 23.75% per side. Zone classification in later versions uses the **car center at its current road cross-section**.

### 4.3 HUD — v0.1

A readable, always-visible right panel with labels and sample values such as:

```text
 GAS BLASTERS
      '82

 GAS     00%
 MI      5.0
 SCORE 000000
 LIVES     3

 SPD      1

 TO PHARMACY
   (DEMO)
```

These numbers are **illustrative only**, not accepted starting lives, mileage, gas rate, scoring rules, or an active game timer. Mark HUD demo/placeholder status clearly, such as `(DEMO)`, to avoid confusing playtesters. If space is tight, prefer legible **GAS, MI, SCORE, LIVES** over decorations. A live SPD readout is optional and useful for tuning, but the four requested values may remain static in v0.1.

## 5. Controls and movement — confirmed Option A

**Joystick port 1** controls the car. **FIRE is reserved** in v0.1; avoid attaching a new unrelated action to it, because later versions use hold-FIRE plus direction for four-way gas blasts.

| Input | v0.1 behavior |
| --- | --- |
| Neutral | Maintain positive speed, road scroll rate, and the current speed-linked car Y position (after any brief smoothing) |
| Left | Steer smoothly left; no lane snapping |
| Right | Steer smoothly right; no lane snapping |
| Up | Increase forward speed/road scroll rate and smoothly move car toward the top of the viewport |
| Down | Decrease speed/road scroll rate and smoothly move car toward the bottom; retain positive minimum, never reverse |
| Up+Left or Up+Right | Change speed and steer simultaneously |
| Down+Left or Down+Right | Brake and steer simultaneously |
| FIRE | No gameplay action in v0.1; reserved |
| Console START | Reset car X and Y, speed, scrolling state and HUD demo state |

Implementation expectations:

1. **Immediate, smooth lateral response** at a stable tick rate, without forced delay, excessive acceleration lag, whole-cell jumps, or erratic subpixel rounding.
2. Keep horizontal position using **fractional/fixed-point arithmetic** where appropriate; choose the representation after assessing the selected display mode and hardware sprite granularity. Make steering independent of integer character-cell steps.
3. Keep the car wholly within the **left driving pane**; it may enter shoulders or grass in v0.1, with no explosion or life loss yet. Avoid moving into HUD or off-screen.
4. Combine **world/road scrolling** with **speed-linked car vertical movement**. Up/Down change forward speed, affecting both road-scroll rate and the car's target screen Y. Use a stable mapping from speed to bounded target Y, with smooth interpolation; do not jump between fixed positions, and do not continuously translate Y when speed is constant. DOWN is braking, not reversing.
5. Use nonzero minimum speed, a controlled maximum, and modest acceleration/braking. **Exact numeric rates, vertical range, speed-to-Y mapping and smoothing are provisional**; Codex must document tuning in the prototype README. At min speed car is low, at max speed car is high; neutral maintains its existing position after smoothing.
6. Scrolling should be visually continuous across row/tile wrap, with no tearing, blank-row flashes or duplicated/lost markings. Vertical car relocation also must not leave ghost pixels/PMG rows, flicker, streak, or clip.
7. Evaluate driving on diagonal joystick inputs as combined steering/speed control, not a diagonal blast.

**Provisional tuning targets (not final game rules):** start at a comfortable middle speed; vary up/down gradually enough to perceive acceleration and braking during a short test. Codex should define speed in clear units (e.g., fractional scroll pixels per NTSC frame), record min/default/max and delta, and justify any sprite quantization limitations. Do not claim Stage 1's walking-speed constants govern a vehicle.

## 6. Atari 800XL implementation guidance

- **Native 6502** instructions only, stock **64 KB** Atari 800XL, NTSC as initial timing/reference mode, BASIC disabled. XEX must actually run; Python is permitted only for offline building, validation, and tests, consistent with the repository workflow.
- **Graphics:** Choose an ANTIC display mode and screen-buffer arrangement that supports a readable right HUD and convincing downward road motion. **ANTIC fine vertical scrolling may be used where practical**, but do **not** naively scroll the entire raster and assume the HUD at the right stays fixed. ANTIC applies vertical row scrolling across the scanline; implement a correct split-pane strategy (such as bounded road-column software updates, selective buffer compositing, or another proven technique). Describe the tradeoff and show it working.
- **Car rendering:** Prefer GTIA Player/Missile Graphics if practical; use a clean original sprite and correct DMA/PMBASE setup. If PMG is used, move its actual bitmap rows for vertical motion and clear old rows; horizontal HPOSP registers alone cannot move the car vertically. PMG is a possibility, **not a requirement** if another native technique demonstrably produces smoother, more reliable movement. Avoid the previously rejected title-screen PMG sparkle experiment; that was a different visual effect.
- **Timing:** Synchronize updates to a stable video tick and avoid unbounded work per frame. Document observed movement and scrolling in NTSC terms. Ensure joystick sampling, visual update and speed adjustment are deterministic and testable.
- **Memory/safety:** Produce an explicit memory allocation/segment map covering code, screen buffers, PMG (if used), display list, font/tile data, and state. Check collision with OS-reserved areas, hardware/shadow registers, BASIC/ROM mapping and the actual Stage 1 v0.5 manifest **before any future integration**. A standalone prototype may use a separate allocation, but must identify it.
- **Build/source:** Provide a reproducible offline build, a human-readable source/listing representing the emitted 6502, and a deterministic XEX artifact with manifest/checksum. Do not represent a generated listing as a MAC/65-assemblable master source unless it genuinely assembles. Use repository conventions and avoid adding unnecessary dependencies.
- **Preservation:** Do not change Stage 1 v0.5 XEX, its builder, title/crew/arrival screens, original POKEY music, immutable tags, or existing accepted files. No new title music is required for this standalone demonstration.

## 7. Proposed deliverables and repository placement

Codex should implement on the **existing** `feature/stage2-driving-v0.1` branch, where the first v0.1 prototype is already committed. Recheck live Git refs and preserve the earlier prototype before changing anything.

| Deliverable | Suggested location | Notes |
| --- | --- | --- |
| Current Stage 2 spec | `docs/STAGE2_DESIGN.md` | This document; active design, not historical archive |
| Versioned XEX | `assets/stage2_v01/GasBlasters82_Stage2_Driving_v01.xex` | Standalone, runnable Atari XEX |
| Build utility | `tools/build_stage2_v01.py` | Reproducible offline build |
| Tests / validator | `tools/test_stage2_v01.py` | Automated checks, plus other utilities if necessary |
| Prototype README | `assets/stage2_v01/README.md` | Controls, build/run, tuning, memory, known limitations |
| Manifest | `assets/stage2_v01/manifest.json` | SHA-256, load segments, build metadata, measured test status |
| Other generated source/assets | `assets/stage2_v01/` | Original art/tables/listings as needed |

Paths are conventions proposed to match existing Stage 1 versioning; Codex may suggest a necessary adjustment but should not overwrite older versioned deliverables. Keep root README and `docs/TODO.md` accurate: Stage 2 should be described as **v0.1 driving only**, not a completed chase.

## 8. Acceptance criteria — Stage 2 v0.1

The prototype is ready for the user's first emulator playtest when:

1. The standalone XEX loads and displays the road/HUD in Atari800 with BASIC disabled, without visible startup corruption or crashes.
2. The gameplay/HUD width split is clearly about 2/3 versus 1/3, and the HUD remains fixed while the **left** road area visibly scrolls downward.
3. Pavement, two shoulders, two grass strips, and lane markings are all discernible; actual zone boundaries are documented against the design percentages.
4. Billy's upward-facing car starts near the lower portion of the road and steers smoothly left/right without lane snapping. **Holding UP visibly moves the car toward the top; holding DOWN visibly moves it back toward the bottom.** Motion is smooth and related to current speed, not a constant-Y illusion.
5. Neutral joystick maintains forward speed **and corresponding car Y**; UP increases scrolling speed and car's forward screen placement; DOWN slows both without reversing; diagonals combine lateral steering and speed/Y.
6. The entire car remains visible inside all four boundaries of the left driving pane, never entering the HUD. No trails, residual sprite pixels, flicker or corruption during vertical movement.
7. Scrolling loops cleanly for a **multi-minute idle run** without missing rows, runaway artifacts, freezes or obvious flicker.
8. GAS %, MI/distance, SCORE and LIVES display readable **placeholder values**; no false implication that actual gas, mileage, lives, or scoring systems work yet.
9. START resets the standalone prototype cleanly and repeatedly.
10. A reproducible build, actual native XEX, README, source representation, manifest/hash, segment/memory report and automated tests are committed to the feature branch; test report differentiates **automated CPU/structural checks** from **actual Atari800 run** and from **user playtest**.
11. The accepted Stage 1 v0.5 artifacts and original opening remain unchanged. No merge to `main` or milestone tag before user review and approval.

### Suggested human playtest

- Drive left/right at default speed; evaluate immediate response and whether it feels as smooth as Stage 1's approved character movement.
- Hold UP, release, then DOWN, release: confirm smoother/faster scrolling **and upward car motion**, then slower scrolling **and downward car motion**; releasing the joystick must preserve speed and Y without springing back.
- Drive onto the shoulder and grass on both sides; no penalties yet; check road scale and clipping.
- Try diagonal Up+Left, Up+Right, Down+Left, Down+Right; ensure controls combine correctly.
- Hold left/right continuously against the viewport boundary; car remains visible and HUD does not flicker.
- Observe the road and HUD for several minutes, then restart repeatedly with START.

## 9. Next milestones and preserved full-stage rules

**v0.2 — pressure and destination (next milestone; design work commencing):** Use the accepted r3 driving baseline; change GAS % from placeholder to an active meter that starts near 0% and steadily rises toward a 100% explosion/failure threshold. Change MI from placeholder to remaining miles to the pharmacy, decreasing with forward travel and reflecting the speed selected by the player. Reaching the pharmacy before pressure reaches 100% produces a distinct success state. Reaching 100% first produces a distinct failure state. A simple START-based restart/reset must make repeated trials possible. Initial gas growth and distance/speed balancing targets are now documented in **Section 16**; the exact mapping to existing native speed units, failure consequences for lives, HUD presentation and restart/success screen details remain **open v0.2 design questions**; do not treat a suggested numeric value as canon. This **is not implemented in v0.1**.

**v0.3+ — driving challenges:** curving/narrowing road, road/shoulder/grass handling, **grass timer that runs/resumes on grass, pauses on shoulder, resets on paved road**, 2.0-second accumulated-grass explosion costing one life, stage warnings, police/hazmat ramming, forks with a flashing upward green arrow, wrong branch adding **exactly 1.0 mile once**, and four-direction car gas blasts using **hold FIRE + direction while steering is suspended**. Those are established future design constraints, not v0.1 deliverables.

**Later road stages:** Friends drive ahead and drop Gas-Nix after it has been acquired in the pharmacy; **no medicine drops on this first road chase**.

## 10. Open technical/feel choices for Codex to document (not silently elevate to game canon)

- ANTIC graphics mode, horizontal pixel/cell allocation, and method for keeping HUD stationary while the road moves.
- Concrete road/shoulder/grass boundaries after resolution rounding.
- Car sprite size, single- or double-line PMG choice if PMG is used, exact spawn Y, bounded low/high Y positions and the speed-to-Y/smoothing implementation.
- Steering speed in fixed-point units, speed caps, acceleration/deceleration rates, and scroll update granularity.
- Exact presentation of the placeholder HUD at the selected text resolution.
- Memory allocations, test methodology, and any actual emulator limitations discovered.

**Definition of done:** A player can meaningfully test the **feel of driving** a recognizable car on a continuously scrolling road, with reliable speed controls and HUD. It is **not** the completed pharmacy chase.
## 11. Original v0.1 implementation evidence — 2026-11-03

The separate XEX is now built at `assets/stage2_v01/GasBlasters82_Stage2_Driving_v01.xex`.
Source: `tools/build_stage2_v01.py`; native CPU tests: `tools/test_stage2_v01.py`.
Build/run commands, full memory map, tuning and playtest plan are in
[the prototype README](../assets/stage2_v01/README.md); manifest, CPU-only profile
and validation report are alongside it. These engineering defaults are provisional:

- ANTIC 4, 27 road / 13 HUD columns; 108-color-pixel road pane (216 logical pixels).
  Character-set animation uses a double-buffered 256-byte road page with static
  HUD glyphs; no raster-wide hardware scrolling.
- Zones [0,7), [7,14), [14,94), [94,101), [101,108): 6.48/6.48/74.07/6.48/6.48%,
  rounding the approved target to color pixels. Center classification is telemetry only.
- Original two-plane PMG car, 8 color pixels ×16 scanlines, top y=144 / center y=152,
  near 79% viewport height. Steering Q4=12 color-pixel units/tick.
- Scroll Q4 min/default/max=8/24/56 scanlines/tick, acceleration/brake ±1 per tick.
  GAS/MI/SCORE/LIVES stay static demo values; speed/zone alone update.
- 12 driving tests pass, including three simulated minutes; 33 accepted Stage 1
  tests, four validators and opening validation also pass. Sampled loop peak
  4,614 CPU cycles excludes DMA/OS interrupts. Atari800 and hardware tests **not run**.

All earlier XEX/source assets are unchanged. This standalone allocation overlaps
Stage 1's runtime memory and must not be loaded as a naive concatenated stage.
No merge/tag or acceptance of feel, final art or full Stage 2 gameplay is implied.


## 12. Approved v0.1 refinement — speed-dependent vertical car movement (2026-11-04)

**Playtest result:** User ran the original Stage 2 v0.1 in Atari800. Basic driving was fine, but its car remained vertically stationary while acceleration/braking only changed road-scroll rate. **That behavior is no longer the approved target.** Create a *second v0.1 prototype* (not v0.2) with the following corrected behavior:

1. Hold **UP**: speed increases toward a cap, downward road-scroll rate increases, and Billy's actual car sprite moves gradually **upward** (smaller screen Y) toward a speed-dependent position.
2. Hold **DOWN**: speed decreases toward a **positive minimum**, road scroll slows and the sprite moves **downward** (larger screen Y). DOWN must never reverse the car.
3. Release to **neutral**: current speed, road-scroll rate and target Y persist. Once any short smoothing completes, the car stays at that vertical position. Do not spring back to its default Y just because UP was released.
4. **Left/right** steering remains smooth across the new full Y range. **Diagonal** input combines steering with acceleration/braking. **START** restores default speed, car X/Y, road state and demo HUD. **FIRE** remains reserved.
5. Map current speed to a **bounded desired car Y**, smoothly interpolate/quantize to that Y, and make min/max positions visually distinct. Entire car stays within the top/bottom of the driving viewport; no unbounded accumulation of Y during held UP/DOWN and no teleportation.
6. The car sprite must **physically move vertically in the Atari display**, not just change HUD values. If using PMG, clear/relocate the old bitmap rows when Y changes; avoid residue, flicker, trails, clipping and corrupting the road/HUD.
7. Preserve the approved v0.1 straight road, 2/3-road / 1/3-fixed-HUD split, placeholders, road zones, and all later-feature exclusions. Stage 1 remains unchanged.
8. **Preserve original versioned v0.1 assets and tooling** as the comparison baseline. Emit the replacement as a separately named revision within the **v0.1 milestone**, e.g. `assets/stage2_v01_r2/GasBlasters82_Stage2_Driving_v01_r2.xex`, with its own build/test evidence; do not overwrite the first `assets/stage2_v01/` XEX/manifest/source.

**Focused automated and Atari800 checks:** UP reaches high car Y and maximum positive scroll speed; release holds Y and speed; DOWN reaches low car Y and minimum positive speed; release holds; car stays bounded at both extremes; diagonal/left/right work at high and low Y; START resets Y and speed; no PMG ghosting, HUD motion or rendering artifacts. CPU-level tests cannot establish actual visual cleanliness; have the user playtest the newly built XEX. **The revision is implemented and CPU tested as v0.1-r2; actual Atari800/user acceptance remains pending.**

### Section 12 implementation evidence — v0.1-r2 (2026-11-04)

Separate output: `assets/stage2_v01_r2/GasBlasters82_Stage2_Driving_v01_r2.xex`;
source: `tools/build_stage2_v01_r2.py`. The original v0.1 folder, manifest, binary,
builder and tests are unchanged, as are Stage 1 and opening/music.

Provisional speed-to-Y mapping: min/default/max speed Q4 8/24/56 maps to car-top
scanlines 160/144/112. Current 16-bit Q4 Y approaches that target at <=12 units
(0.75 scanline) per tick, clamped to avoid overshoot. Neutral holds speed and the
corresponding target; no return-to-default logic. PMG clears both old 16-row planes
and redraws both unchanged car images at the new integer Y.

19 revision tests and 12 original tests pass, including native three-minute idle
coverage, exact complete PMG bitmap checks, bounds, extreme/partial speed holds,
diagonals and resets. Stage 1 regressions (15+18), four validators and opening
validation also pass. Sampled revised-loop max is 5,517 CPU cycles, excluding
DMA/OS interrupts. **Not Atari800 tested here.** See [r2 README](../assets/stage2_v01_r2/README.md)
for memory, build/run commands, smoothing/quantization limits and focused playtest.


## 13. Stage 2 v0.1-r3 — extend high-speed vertical car travel (approved for playtest 2026-11-04)

**User feedback after testing r2 in Atari800:** The speed-linked vertical car movement is now present, but the car should be able to travel **farther up-screen** at maximum speed. Keep v0.1 driving scope intact; this is a **provisional tuning experiment**, not a final game rule or Stage 2 v0.2.

| Speed setting | Speed Q4 | r2 car-top Y (historical) | Proposed r3 car-top Y | r3 car-center Y |
| --- | ---: | ---: | ---: | ---: |
| Minimum | 8 | 160 | **160** (unchanged) | 168 |
| Default | 24 | 144 | **144** (unchanged) | 152 |
| Maximum | 56 | 112 | **80** | 88 |

Coordinates are **car-top logical scanlines** in the existing 192-scanline viewport, with Y increasing downward; the car image remains 16 scanlines tall. At maximum speed the sprite occupies Y **80–95**, leaving the upper 80 scanlines in front of the car. Total vertical movement becomes **80 scanlines**, up from **48** in r2.

**Approved r3 constraints:**

1. **Change only the high-speed vertical travel target** (car-top Y=112 → 80), plus the Y mapping necessary to reach it. Keep the current min/default car Y=160/144, speed Q4 min/default/max=8/24/56, scroll speed, accel/brake increments, automatic forward travel, steering, diagonals, FIRE reservation, START reset, stationary HUD and all other v0.1 behavior intact.
2. r2 used `targetY = 168 - speedQ4`; this cannot produce the new max Y while retaining default Y=144. Instead map speed **monotonically and continuously** through the three exact anchor points **(8,160), (24,144), (56,80)**, e.g. with piecewise interpolation. Avoid discontinuities or snapping at the default-speed transition; clamp targets to the intended range.
3. **Initially retain r2 Y smoothing of 12 Q4 units/tick (0.75 scanline/tick)**. This may cause a short additional settling period at high speed; evaluate in Atari800. Do not quietly modify steering, acceleration, road scrolling, or default-speed placement as a side effect.
4. Physically relocate the car PMG bitmap safely, clearing stale rows and ensuring no trailing pixels, flicker, sprite clipping, or HUD corruption. The entire sprite must remain in the driving viewport at all speeds.
5. Preserve the original v0.1 and **r2** XEX, build tools, source listings, manifests, tuning, and tests as immutable comparison baselines. Emit a separately versioned r3 prototype, suggested `assets/stage2_v01_r3/GasBlasters82_Stage2_Driving_v01_r3.xex`, with `tools/build_stage2_v01_r3.py`, `tools/test_stage2_v01_r3.py`, its own README, tuning, manifest/checksum, and observed test evidence.
6. Run automated tests for precise Y endpoints, mapping continuity/monotonicity, min/max bounds, smooth intermediate positions, neutral holds, steering and diagonals, START reset, PMG old-row clearing, stationary HUD and preservation of earlier artifacts. The user will separately judge the actual driving feel in Atari800.

**Status update (2026-11-04): r3 Y=80 has now been user-playtested in Atari800 and its driving mechanics accepted for the v0.1 milestone.** Further upward screen travel remains deferred/optional. Merge, tag, or branch deletion still require separate authorization; this documentation approval is not a Git integration action.

### Section 13 implementation evidence — v0.1-r3 (2026-11-04)

Built separately at `assets/stage2_v01_r3/GasBlasters82_Stage2_Driving_v01_r3.xex`;
source/test/profile utilities use the same `_v01_r3` suffix.

The target table uses Y=168−speedQ4 for speed 8..24, and Y=192−2×speedQ4 for
speed 24..56, clamped outside the range. Exact min/default/max anchors are
160/144/80. Both pieces meet at default; native smoothing remains 12 Q4/tick.
Only the $6600/$6700 table segments differ from r2's loaded binary: all native
instructions, art, font/display buffers, road and other data are identical.
Original v0.1/r2 source and artifacts remain unchanged.

All 21 r3, 19 preserved r2, 12 original driving and 33 Stage 1 CPU tests pass,
plus four design validators and opening validation. Profiled neutral settling
after default-to-max acceleration takes 54 additional ticks (~0.9s NTSC), as
expected with retained smoothing. Sampled peak is 5,517 CPU cycles, excluding
DMA/OS overhead. These are the **original build-time** CPU results, not proof of emulator operation; the user **subsequently played r3 in Atari800 and approved its driving mechanics on 2026-11-04**. Physical hardware verification remains open.
See [r3 build/playtest notes](../assets/stage2_v01_r3/README.md) for commands,
comparison links, scope limits and the user-review checklist. No merge/tag.

## 14. v0.1 milestone acceptance and deferred driving polish — 2026-11-04

**User acceptance:** After testing `assets/stage2_v01_r3/GasBlasters82_Stage2_Driving_v01_r3.xex` in Atari800, the user described the driving mechanics as **good for now** and **approved moving forward**. This accepts the **Stage 2 v0.1 free-driving mechanics**, not the whole Stage 2 pharmacy chase, finished artwork, exact balancing, all emulator edge cases, PAL or physical Atari 800XL validation.

**Accepted playable baseline:** `v0.1-r3` (car-top Y mapping at min/default/max speed Q4 8/24/56: **160/144/80** scanlines). Retain the straight, downward-scrolling road, fixed HUD, freely steerable upward-facing car, positive automatic forward motion, UP/DOWN speed control, speed-linked vertical screen placement, joystick diagonals and START reset. All pre-r3 versioned files remain as historical prototypes.

**Explicitly deferred:** The player may later be allowed to travel **even farther toward the top of the screen than current max-speed car-top Y=80**. This is an **optional future driving-feel refinement**, **not** an immediate requirement and **not** a blocker for v0.2. When reconsidered, assess forward visibility, threat reaction time, speed-to-Y mapping, smoothing/lag and sprite/viewport bounds, and require another user playtest before revising the approved values. Avoid silently retuning r3 during v0.2 development.

**Acceptance evidence distinction:** User reports a successful **Atari800 driving-feel playtest and approval**. Codex's recorded r3 CPU tests and manifest remain build/test evidence; neither statement implies exhaustive manual regression or testing on physical hardware.

**Next version control checkpoint — recommendation only, NOT executed:** Once the documentation-only acceptance commit is reviewed, preserve the accepted commit under an immutable `stage2-v0.1` tag; integrate the feature branch into `main`; verify the tag and `main` match the accepted baseline; then create `feature/stage2-pressure-destination-v0.2` from updated `main`. The old v0.1 feature branch can be deleted after verifying integration and the immutable tag. Do not perform these operations without the user's explicit authorization.

## 15. v0.2 design kickoff — Gas pressure and destination (planning; not implemented)

**Objective:** Turn the accepted v0.1 driving demo into a simple **race to the pharmacy**, retaining its driving controls and presentation. The objective is to reach the pharmacy before Billy's gas pressure hits 100%.

| System | Agreed behavior to design | Still to decide/tune before coding |
| --- | --- | --- |
| Gas pressure | Live `GAS %` starts at **0%**; linear elapsed-time growth reaches **100% at 2:45** (~18 percentage points per 30 s); see Sections 16–17 | Exact warning animation and control-impairment tuning after playtest |
| Distance | Live `MI` starts at **2.0 miles** and counts down using the approved **8→20, 24→60, 56→100 Q4-to-MPH mapping** (Section 19); a steady 60 MPH drive takes 2:00 | HUD rounding/display resolution and live update cadence |
| Success | Reach **MI=0.0** with GAS below **100%**, freeze driving and show a **brief cutscene featuring the pharmacy building**; use a fresh **FIRE/trigger** press to continue to the standalone v0.2 **completion screen** (Stage 3 is not implemented); see Section 18 | Exact exterior artwork, cutscene wording/duration and finish-state presentation are playtest/art details |
| Failure | At **100%** before arrival: freeze driving, basic gas explosion animation, deduct **one life**, display **`BILLY BLEW IT!`**; see Section 17 | Animation duration/style and simultaneous arrival-versus-failure precedence |
| Restart | After failure, **joystick FIRE/trigger** retries Stage 2 when lives remain: GAS **0%**, MI **2.0**, default car speed/position; retained lives persist across retries | Game-over restart/exit policy; whether console START remains available for debug resetting |
| HUD | Fixed right 13-column pane with GAS % + 10-segment bar, pharmacy miles (two decimals), whole MPH, three miniature lives/car icons, and six-digit SCORE placeholder; Section 20 | Exact pixel/glyph art and warning flash frequency remain playtest/implementation tuning |

**Important design boundaries:** No Gas-Nix pickups or drops are available before the pharmacy. No police, hazmat vans, road forks, winding/narrowing roads, off-road explosion timer or four-way car gas blasts in v0.2 unless separately approved. Do not integrate Stage 2 into the accepted Stage 1 XEX yet. Keep v0.1-r3 mechanics and artifacts stable; implement v0.2 as a separately versioned standalone prototype. Gas growth should reflect the passage of game time rather than decreasing merely because the player accelerates; higher forward speed should allow faster destination progress, creating a meaningful race against pressure. The **initial numerical rates are selected for playtesting in Section 16** and remain subject to balancing, not silently fixed as final production rules.

**Remaining implementation/playtest tuning before the Codex handoff:** exact warning/shake intensity and durations and **arrival cutscene artwork/timing details**. **Simultaneous success/failure precedence and game-over replay policy are approved in Section 21.** HUD layout and numeric presentation are now approved (Section 20); exact pixel/glyph drawing and warning-flash frequency remain implementation/playtest tuning. **Sections 16–20 record agreed provisional balancing and confirmed speed mapping, failure/retry, arrival, and HUD flows; v0.2 remains design-only and unimplemented.**

## 16. v0.2 provisional timing, speed, distance and gas-pressure balance — 2026-11-07

**Design conversation decision:** Begin with the **desired typical play duration**, then choose speeds, distance and pressure deadline. These are **approved initial playtest targets**, not immutable final game rules and not evidence that v0.2 has been implemented.

| Parameter | Agreed initial target | Notes |
| --- | --- | --- |
| Typical Stage 2 driving time | **2:00 (120 seconds)** | Aim for a normal successful drive, excluding menus/retries |
| Minimum car speed | **20 MPH** | Positive forward movement; never reverse |
| Maximum car speed | **100 MPH** | Arcade-speed upper bound |
| Typical average driving speed | **60 MPH** | Desired balancing reference, not proof of actual player average |
| Pharmacy distance | **2.0 miles** | Initially displayed as miles remaining; adjustable after playtest |
| Gas pressure at start | **0%** | Matches earlier near-zero opening intention |
| Approximate gas growth | **18 percentage points per 30 seconds** | Linear elapsed-time pressure model |
| Pressure-failure deadline | **2:45 (165 seconds)** | Exactly 100% at this time if Billy hasn't arrived |
| Typical pressure on arrival | **~73% at 2:00** | About 45 seconds of pressure margin at 60 MPH average |

### Timeline and numeric interpretation

For the first v0.2 playtest, model underlying gas pressure as a **linear rise from 0% at elapsed 0 seconds to 100% at elapsed 165 seconds**. Exact conceptual rate: `100 / 165 ≈ 0.60606 percentage points per second`, or **~18.18 points per 30 seconds**. Show integer HUD values rounded appropriately, e.g.:

| Elapsed drive time | Approximate displayed GAS % |
| --- | ---: |
| 0:00 | 0% |
| 0:30 | 18% |
| 1:00 | 36% |
| 1:30 | 55% |
| 2:00 | 73% |
| 2:30 | 91% |
| 2:45 | **100% — failure if not arrived** |

The final **15-second** interval adds approximately **9 percentage points**, rather than the ~18 of a full 30-second interval. This is **half the time at the same linear rate**, *not* a new decelerating growth rule or nonlinear taper. If actual slower pressure growth near the end is desired later, treat that as a new balancing decision. Pressure depends on elapsed gameplay time and **does not slow down because Billy accelerates**.

### Distance and native-speed considerations

- At a constant modeled 60 MPH, traveling **2.0 miles takes exactly 2:00**. This gives a mathematical pacing anchor, not a promise every run finishes in two minutes.
- Hypothetical constant-speed travel times before accounting for acceleration or future hazards: **20 MPH → 6:00** (gas failure first); **60 MPH → 2:00**; **80 MPH → 1:30**; **100 MPH → 1:12**. The v0.2 straight-road demo may allow faster finishes than two minutes until traffic and hazards are introduced.
- The accepted v0.1-r3 controller uses internal **Q4 scroll-speed units** (minimum/default/maximum **8/24/56**), not MPH. The user **subsequently approved the exact three-anchor mapping** Q4 **8→20 MPH, 24→60 MPH and 56→100 MPH**, with continuous piecewise-linear interpolation (authoritative detail in Section 19). **Do not alter r3 steering, acceleration, scrolling feel, vertical car Y or tuning** when calculating/displaying MPH.
- Conceptual distance accumulation: **miles traveled = modeled MPH × elapsed seconds / 3600** (integrated over changing speeds); remaining miles must never go below zero. Use sufficient fixed-point precision, independent of displayed HUD rounding. The winning arrival event requires reaching 0 miles while pressure is still **below 100%**; deterministic precedence on a frame where both thresholds cross remains to be specified.
- A 2:45 gas deadline at a 2:00 target completion time leaves an approximate **45-second margin**. This is a starting balance point for playtesting; do not assume it guarantees difficulty once hazards are added.

### Open decisions (do not silently invent)

The **100%-pressure life loss, basic explosion sequence, FIRE retry, warning thresholds and three starting lives are approved in Section 17**, the pharmacy arrival cutscene/FIRE continuation in Section 18, the **piecewise Q4→MPH mapping** in Section 19, and the **HUD layout/precision** in Section 20. Remaining design questions are precise shake/visual/audio and arrival-art tuning, game-over reset/exit, simultaneous arrival/failure precedence, and final glyph/flash implementation details before a full Codex implementation prompt. **Future levels may have gradually longer durations, with a shorter final home stage**, but no exact progression has yet been approved. This section defines the **v0.2 balance baseline only**.

## 17. v0.2 gas-pressure warnings, explosion, lives, and retry — approved 2026-11-07

**Approval scope:** The following are **confirmed Stage 2 v0.2 gameplay requirements**, while the precise animation and handling parameters remain **provisional** for tuning. These rules apply to pressure reaching 100% during the **first road chase to the pharmacy**, not necessarily every indoor level or future road stage.

### Starting state and warning escalation

- **Starting lives: 3.** Display the live remaining lives in the fixed right HUD, replacing its old illustrative `LIVES 3` placeholder with actual state. A life is deducted **once per gas-pressure explosion**; never decrement repeatedly while the animation/message is shown.
- **Start of each attempt:** GAS **0%**, distance **2.0 miles** to the pharmacy, Billy's accepted v0.1-r3 **default speed and car position**. Gas continues to rise linearly in elapsed driving time toward **100% in 165 seconds** as specified in Section 16.
- At **75% GAS**, enter the **warning** state: GAS indicator flashes, Billy's car **begins shaking**, and steering/handling becomes **slightly harder**. The shake is visible on the car itself and escalates with pressure; preserve the car inside the driving viewport and player steering authority.
- At **90% GAS**, enter the **critical** state: more urgent GAS warning, **significantly more violent car shaking**, and **greater yet still controllable** handling impairment compared with 75%. Avoid instant/unfair lane jumps or making the vehicle impossible to steer. These pressure thresholds are confirmed; exact screen shake amplitude, control disturbance, flash cadence, audio, and response curves are **provisional** playtest-tuning parameters, not independently approved constants.
- Both warning effects should be **pressure-driven**. Do not silently retune the accepted r3 baseline steering, normal speed/acceleration or Y behavior at pressure below 75%. Implementation must prevent visual shake from moving the effective car/collision position off-screen or into the HUD. Separate true car position from visual jitter where practical; if steering is deliberately affected, keep the effect modest and predictable.
- Under the linear 165-second model, 75% occurs at **123.75 seconds (2:03.75)** and 90% at **148.5 seconds (2:28.5)**. A player finishing near the **2:00 typical target** may arrive without seeing the warnings; the warnings are intentionally aimed at slower/at-risk runs and should be assessed in testing.

### 100% pressure: loss sequence (confirmed order)

1. **Freeze the active drive** when gas pressure reaches **100% before successful pharmacy arrival**: stop driving input/world-scrolling and suspend pressure/distance accumulation.
2. Play a **basic, readable gas explosion animation** for the v0.2 playtest, conveying an exaggerated green gas eruption. Elaborate cloud artwork, screen-shake choreography and sound are **deferred polish**; no final effects are required to validate the loop.
3. **Deduct exactly one life**, clamp remaining lives to zero, and update the live LIVES HUD.
4. Show the exact failure message **`BILLY BLEW IT!`** once the explosion effect finishes.
5. If **one or more lives remain**, wait for a fresh **joystick FIRE / trigger-button press** to restart **Stage 2 itself** (not Stage 1). On retry, restore GAS **0%**, MI **2.0**, default car **speed and X/Y position**, road/scroll initial state and attempt elapsed timer, while **retaining the reduced life count**. Re-arm input after release to avoid a held button instantly dismissing the message or causing multiple retries.
6. If **no lives remain**, display the exact message **`GAME OVER`** rather than permitting an ordinary life-preserving retry. A fresh **FIRE** press on GAME OVER starts an entirely new Stage 2 game with **three lives** (Section 21); an ordinary retry with remaining lives does not restore lost lives.

**Trigger-button distinction:** FIRE is reserved/inert **during ordinary v0.2 driving** (until later four-way gas blasts); it is the restart control **on the failure screen when lives remain**. The previously supported console START reset in v0.1 is a different control and should not be silently substituted for the user's specified trigger-button restart. Whether START also operates as an explicit debug reset during active driving can be finalized with the prototype control design.

**Success flow is approved in Section 18:** Arriving at 0.0 miles with pressure still **below 100%** freezes driving and leads to a short pharmacy-building cutscene, then a **FIRE-to-continue** standalone completion screen. **Section 21 approves gas-pressure failure taking precedence if arrival and 100% occur on the same simulation tick**, plus FIRE replay from STAGE 2 COMPLETE.

### v0.2 acceptance tests to plan (not yet implemented)

- 3 starting lives; live HUD counts down **3 → 2 → 1 → 0** on three separate failures, never twice on one failure; no fourth retry from a zero-life state.
- On 75%, warning flashes, car shakes mildly, controllability decreases slightly; on 90%, shaking is visibly more violent and handling harder yet manageable; below 75%, r3 driving feel remains intact. Long-running tests must verify car/HUD boundaries and non-accumulating shake offsets.
- At 100%, active simulation freezes **before** basic animation; after animation exactly one life is deducted and **`BILLY BLEW IT!`** appears if lives remain, **`GAME OVER`** if none remain. No HUD/time/distance drift during failure display.
- FIRE restart requires a fresh press and restores distance, gas, speed, position and elapsed-time state while retaining the reduced lives; success and GAME OVER must not accidentally trigger a normal retry.
- Retain deterministic 6502 CPU tests and Stage 1/r3 regression checks; distinguish simulated tests from the user's actual Atari800 playtests. No implementation or XEX is asserted by these design decisions.

## 18. v0.2 pharmacy arrival and completion cutscene — approved 2026-11-07

**User-approved objective and presentation:** Billy reaches the pharmacy by bringing the `MI` counter to **0.0 miles before GAS reaches 100%**. Instead of a plain result message, successful arrival triggers a **brief, recognizable pharmacy-building cutscene**, followed by the player's **joystick FIRE/trigger press** to continue. This is a design requirement for the standalone Stage 2 v0.2 prototype; **the pharmacy interior (Stage 3) is not implemented or integrated**.

### Successful arrival sequence (confirmed)

1. While driving, accumulate elapsed time, gas pressure and distance traveled according to the approved v0.2 balance model. When the remaining distance reaches **zero while GAS is below 100%**, resolve a **single success event**. Clamp displayed remaining miles at **0.0**; do not let it become negative.
2. **Freeze the active driving simulation**: stop road scrolling and input-driven car movement; stop gas growth and distance/time accumulation. Billy cannot explode from rising pressure *after* successful arrival has already been recognized. Lives remain unchanged.
3. Transition to a **short arrival cutscene clearly showing the exterior of a pharmacy building**. A legible sign should identify the location as a pharmacy; original Atari 8-bit-appropriate art is sufficient. A simple scene transition and short caption/text may accompany the image, but the exact illustration, copy, palette, music and duration are **not yet fixed**. This is a cutscene, not a controllable Stage 3 interior.
4. Once the scene is ready, wait for a **fresh joystick FIRE/trigger press** to continue (require release-to-rearm so a held button cannot immediately dismiss the scene). **Console START is not the primary continuation control**. FIRE's meaning here is an outcome-screen action, distinct from future road-stage hold-FIRE gas blasts.
5. For **v0.2 standalone testing**, FIRE advances to a clear **STAGE 2 COMPLETE** / **PHARMACY REACHED** end-of-prototype state. This confirms success and ends the playable Stage 2 demo. **Do not launch Stage 3, fake a playable pharmacy, reset gas for Stage 3, or create a new automatic stage transition.** A future integration milestone may replace the completion placeholder with a real Stage 3 handoff.
6. The success cutscene/end screen **must not deduct lives**, play the gas explosion, show `BILLY BLEW IT!`, or re-enable road simulation. FIRE on the standalone STAGE 2 COMPLETE screen **starts a new three-life Stage 2 prototype run**, approved in Section 21. It must be a second fresh press, distinct from FIRE used to leave the arrival cutscene.

### Technical and playtest notes

- Keep the already accepted r3 road, steering, speed-dependent car Y, HUD partition and native Atari 800XL 6502 constraints intact. The short pharmacy exterior cutscene can use a separate display mode/screen if required; **do not assume the road scene's 27/13 column split must be reused for the full-screen cutscene**, but document all screen, PMG, font, palette, music and memory transitions.
- If artwork or screen modes require a new memory allocation, preserve the accepted opening/Stage 1 resources and keep v0.2 standalone until integration is deliberately planned. **Original artwork and an economical, readable arrival transition are preferable to complex animation for the first prototype.** No actual image or XEX is generated by this design entry.
- Acceptance tests: crossing `MI=0.0` with GAS<100 produces a *single* arrival event; all runtime counters freeze; pharmacy building visibly appears with readable identification; fresh FIRE advances to the completion screen without an explosion or life loss; holding FIRE does not skip multiple screens; success never falls through to a failure state; Stage 3 is not run. Distinguish automated CPU checks from actual Atari800 cutscene review.
- **Resolved in Section 21:** if reaching MI=0 and GAS=100 happens in the same simulation tick, gas pressure wins and causes a failure. Q4→MPH mapping and HUD numeric presentation/update principles are approved in Sections 19–20; FIRE new-game/replay controls for GAME OVER and STAGE 2 COMPLETE are approved in Section 21. Exact glyphs, warning-flash frequency, cutscene art and duration can be refined through playtesting.

**Milestone status:** The **arrival flow and pharmacy-building cutscene are approved design**, but **v0.2 is not implemented or user-playtested**. Do not mark Stage 2 complete on the TODO checklist yet.

## 19. v0.2 approved native-speed-to-MPH mapping — 2026-11-07

**User approval:** Map the approved Stage 2 v0.1-r3 driving controller's existing internal **Q4 scroll-speed value** to a modeled MPH value for the v0.2 distance countdown, **without changing how the car accelerates, brakes, steers, scrolls or moves vertically on-screen**. The following three anchors are **confirmed design decisions**; pacing and distance balancing remain provisional for actual playtesting.

| Controller speed (Q4 units) | Modeled car speed | Meaning |
| ---: | ---: | --- |
| **8** | **20 MPH** | Accepted positive minimum |
| **24** | **60 MPH** | Accepted default-speed setting; pacing reference |
| **56** | **100 MPH** | Accepted maximum speed |

For all intermediate speeds, use **continuous, monotonic piecewise-linear interpolation** through the anchors:

- For Q4 speed `q` in **[8, 24]**: `MPH = 20 + (q - 8) × (40 / 16) = (5 × q) / 2`.
- For Q4 speed `q` in **[24, 56]**: `MPH = 60 + (q - 24) × (40 / 32) = 30 + (5 × q) / 4`.
- Clamp out-of-range lookup inputs to the valid mapping **20–100 MPH**; never introduce reverse travel. These formulas agree **exactly at q=24**, yielding 60 MPH, and have no speed discontinuity.

**Intermediate examples:** Q4 **16→40 MPH**, **32→70 MPH**, **40→80 MPH**, **48→90 MPH**. Because the two intervals have different slopes, **do not replace this with a single linear formula across 8–56**: it would not preserve the default 60 MPH at Q4=24.

**Keep physics and presentation separate:** Q4 speed is still authoritative for road scrolling, input/acceleration and physical car Y. MPH is a derived, fractional-precision value for **distance progression** and any future HUD MPH readout; using the MPH conversion must not change approved r3 acceleration/smoothing or introduce a new speed-control scheme. Driving at constant default Q4=24/60 MPH for **2.0 miles** yields the **2:00 reference run**. Accelerating aggressively may finish sooner; the two-minute average remains a balancing goal, not a speed governor.

**Native implementation acceptance criteria (future Codex task):** exact anchor/intermediate arithmetic; deterministic monotonic values and clamping; fractional-precision distance accumulation `miles = Σ(MPH × Δt_seconds / 3600)` independent of displayed rounding; no premature display of successful arrival from rounding alone; no regression in r3 control feel, vertical movement, scroll, or fixed HUD. Verify emulator timing and road/distance behavior during a subsequent playable v0.2 run. This is **design-only**: no v0.2 implementation or tests have been performed by this document update.

## 20. v0.2 approved driving HUD layout and behavior — 2026-11-07

**User approval:** Adopt the proposed **1980s arcade-style HUD** for v0.2 with the **existing fixed 13-character-column right pane** alongside the accepted **27-column scrolling driving playfield** (40 columns total). Keep the HUD stationary, readable, and visually separated from the road; retain its fundamental layout for later road stages by changing destination and applicable data, rather than redesigning it for each stage. This is an **approved functional/presentation design**, not final pixel art, font data or proof of actual Atari800 rendering.

### Visual hierarchy, top to bottom

| HUD section | Approved display | Runtime behavior |
| --- | --- | --- |
| **GAS PRESSURE** (top, most prominent) | Large **whole-number GAS %** and **10-segment horizontal bar** | Start **0%**, rise on elapsed driving time, update integer percentage when its displayed value changes; bar gives approximate 10% increments. The bar and percentage flash at warning thresholds, but **not** the entire HUD. |
| **PHARMACY** | Miles remaining as **`2.00 MI`** initially, with **two decimal places** | Decrease based on modeled MPH and elapsed time; reach **`0.00 MI`** on **actual arrival**, not due merely to display rounding. The destination label may change for later road legs. |
| **SPEED** | Whole-number MPH, e.g. **`60 MPH`**, range **20–100** | Derive from the approved piecewise Q4→MPH conversion (Section 19); refresh the visible digits as displayed MPH changes. **Do not display raw Q4 speed** or modify driving controls. |
| **LIVES** | **Three miniature car icons** at stage start | One car icon disappears after each explosion; states **3 → 2 → 1 → 0**. Lives persist across same-stage retries. Icons must fit in the 13-column pane at native Atari character/glyph resolution. |
| **SCORE** (bottom) | **Six-digit numeric value**, initially **`000000`** | Fixed placeholder for v0.2; no speculative scoring logic. Reserve width for real score rules in a later milestone. |

**Illustrative 13-column text schematic** (spacing, dividers and glyph sizes are **not** exact native screen-cell placements):

```text
 GAS PRESSURE
 [#######---] 
      68%
   PHARMACY
    1.25 MI
     SPEED
     60 MPH
     LIVES
   [CAR][CAR][CAR]
     SCORE
    000000
```

**Schematic caution:** At 68% gas, seven of ten segments filled is an illustrative rounded presentation; the exact threshold-to-segment fill policy remains a playtest/implementation detail. The finished layout must fit exactly within the current **13-column × 24-character-row** HUD area; the miniature car icons should be custom character glyphs or an equivalently economical Atari-compatible symbol. The HUD mockup does not authorize changing the existing display split or screen mode.

### Approved warning behavior

- **GAS 0–74%:** stable percentage/bar, normal presentation and the already accepted r3 driving feel.
- **GAS 75–89%:** GAS bar and numeric percentage **flash slowly**; the car shakes mildly and steering becomes a little harder (Section 17). Leave other HUD labels and values stationary and readable.
- **GAS 90–99%:** GAS bar and numeric percentage **flash faster** to convey urgency; the car shakes substantially more and handling is harder but remains controllable (Section 17). Do not flash, shake or obscure the entire HUD.
- **GAS 100%:** trigger the already approved explosion/failure sequence (Section 17); retain a coherent final GAS indication during failure as practical, and keep the warning animation from causing extra life decrements.
- Evaluate threshold state from the **underlying gas value**, not from a rounded HUD percentage; avoid displaying **100% before the true failure threshold**. If rounded presentation would otherwise prematurely show 100%, clamp the *pre-failure display* to at most 99%. This is a representation rule only; simulation timing is unchanged.

### Data, precision, timing and scope

- **Gas percentage:** calculate continuously with the approved 0→100% over 165 seconds model, show whole numbers and repaint only when an integer value changes or the warning flash changes phase. Keep gas in a stable location.
- **Distance:** maintain high-precision remaining miles internally, then show **two decimal places**; prevent premature **0.00** due to rounding by showing **0.01 MI** until actual completion if needed. Do not declare arrival from formatted text; only the internal distance threshold triggers the pharmacy cutscene.
- **Speed:** compute MPH from Q4 using Section 19 at sufficient fractional precision for distance calculations; display only **whole MPH**. Repaint when the visible value changes, without changing original speed/Y/scroll behavior.
- **Lives and score:** render exactly the current remaining lives with the three-slot icon display, and keep SCORE numeric but **not active** in v0.2. Do not create new score increments, gas-remedy indicators, road-zone telemetry, timers or additional data fields in the HUD as incidental changes.
- **Technical constraints:** Keep stationary right-side glyphs intact across road-font bank swaps, flashing and screen transitions; do not let the independently scrolling left roadway overwrite the HUD. Favor byte/character-cell updates only where visible values change. The exact glyph/palette choices, bar-segment fill pattern at fractional thresholds, separator rows and **slow/fast flash cadence** are implementation parameters to document and then playtest in Atari800, not separately specified numerical constants here.

### Planned acceptance checks (not yet implemented)

1. Road remains within 27 left columns; all five HUD sections stay fully visible and static inside **13 right columns**, including at min/max car position and during long scrolling runs.
2. The initial right HUD reads GAS **0%**, **2.00 MI**, **60 MPH** (default Q4=24), **three** miniature car life icons and SCORE **000000**. The examples in the mockup are illustrative, **not** initial game values.
3. MPH follows the exact approved Q4 mapping, gas percentage/bar follow elapsed time, miles visibly decrease with time and speed, and numeric rounding never falsely ends the drive.
4. At 75% and 90% warning thresholds only the GAS indicator flashes, with increasingly urgent cadence, while other HUD elements remain readable. Flash effects cannot change actual gas percentage/lives or car bounds.
5. After each explosion, one car icon disappears and remains absent through a FIRE retry. After success, no life is removed.
6. Preserve score as a six-digit placeholder and leave all postponed road hazards, attacks, and Stage 3 integration unimplemented. Check actual Atari800 legibility and emulated performance separately from CPU and deterministic build tests.

**Now approved in Section 21:** same-tick arrival versus 100% gas precedence, and FIRE behavior after GAME OVER / STAGE 2 COMPLETE. Exact visual effects and arrival-cutscene art remain subject to later tuning. **The v0.2 XEX has not yet been built or playtested.**

## 21. v0.2 confirmed terminal precedence and FIRE replay rules — 2026-11-08

**Approved by user:** Gas pressure **wins an exact same-tick tie** with reaching the pharmacy. **FIRE on GAME OVER** begins a completely new Stage 2 game with three lives; **FIRE on STAGE 2 COMPLETE** begins a fresh Stage 2 prototype run with three lives. These choices complete the major v0.2 gameplay loop design. All behavior remains **design-only; no v0.2 XEX has yet been built or playtested**.

### Deterministic outcome precedence

- Use the underlying unrounded gas/distance state, never the displayed HUD text. On each active driving tick, if **GAS reaches 100%**, trigger the gas explosion and life-loss path even if **MI simultaneously reaches 0**. Do **not** show the pharmacy cutscene on that tick.
- Otherwise, **MI reaching zero while GAS remains strictly below 100%** means successful arrival; freeze the simulation and show the pharmacy-building cutscene as in Section 18.
- Latch the first terminal outcome so only one event can occur per attempt. Never deduct more than one life for one explosion. Previously latched arrivals do not become explosions later.

### FIRE behavior by outcome

| Screen/state | Fresh joystick FIRE action | Lives after FIRE | Reset |
| --- | --- | --- | --- |
| **BILLY BLEW IT!** with lives remaining | Retry **Stage 2** | **Preserve** the remaining 2 or 1 lives | GAS 0%, MI 2.0, accepted r3 default speed/position, road phase, warning state and timer |
| **GAME OVER** with **0 lives** | Start a **completely new Stage 2 game** | **Restore 3 starting lives** | All initial Stage 2 game/attempt state |
| **STAGE 2 COMPLETE** | Start a **fresh Stage 2 prototype run** | **Restore 3 starting lives** | All initial Stage 2 game/attempt state |

**Two distinct FIRE presses on success:** FIRE first advances the pharmacy-building arrival cutscene to **STAGE 2 COMPLETE**. Only a *subsequent fresh press* from **STAGE 2 COMPLETE** starts another run. Require a release-to-rearm between presses, so holding FIRE cannot accidentally skip both screens. A similarly held FIRE must not skip the explosion message, duplicate restarts or deduct extra lives.

**Frozen terminal states:** While on the cutscene, completion, failure or game-over screen, road movement, gas growth and distance must remain frozen. The v0.2 replay is **not** a Stage 3 transition; the standalone Stage 2 prototype is intentionally replayable. The complete full-game handoff to Stage 3 belongs to a later integration milestone.

**Future Codex acceptance tests:** Simultaneous GAS=100/MI=0 chooses explosion only; GAS<100/MI=0 chooses pharmacy only; one life lost per failed attempt; regular FIRE retry preserves reduced lives; GAME OVER and COMPLETE FIRE restore three lives; separate cutscene/complete FIRE edges; no drift, double-fires or automatic multi-screen skips. Preserve Stage 1 v0.5 and accepted Stage 2 v0.1-r3 binaries. Exact art, warning flash and shake strength remain for playtest tuning.

## 21. v0.2 final approved tie handling and FIRE new-game controls — 2026-11-08

**Authoritative resolution of earlier open questions in Sections 15–20:** The user has now approved both **gas-first same-tick precedence** and **FIRE-controlled replay/new-game behavior**. References in prior dated design notes to these being undecided are **superseded by this Section 21**. Visual tuning and cutscene art remain adjustable during coding/playtesting; the gameplay rules below are confirmed.

### Simultaneous pharmacy arrival vs. 100% gas

- In each active driving simulation tick, integrate gas growth (elapsed-time based) and distance progression (speed based) at full internal precision, independently of rounded HUD text.
- If **GAS reaches 100% or higher on the same tick MI reaches 0.0 or below, GAS WINS**. Freeze driving, play the basic gas explosion animation, deduct **exactly one life**, and show `BILLY BLEW IT!` when lives remain or `GAME OVER` when none remain. **Do not** trigger the pharmacy arrival cutscene on that tick.
- Pharmacy success is recognized **only when actual GAS is still below 100%** at the instant MI crosses zero. Once success is latched, freeze the timer/pressure and never retroactively explode the car.
- Latch exactly one terminal outcome per attempt. Do not double-deduct lives or restart simulated driving until FIRE explicitly begins a new attempt/game.

### Approved outcome-screen FIRE behavior

| Current screen/state | FIRE / joystick trigger | Next attempt lives |
| --- | --- | --- |
| **`BILLY BLEW IT!`** with lives remaining | Retry **Stage 2** in the **same game**. Reset GAS, MI, car, speed, elapsed timer, scroll and warning/explosion flags; **preserve reduced lives**. | **2 or 1**, unchanged |
| **`GAME OVER`** after lives reach 0 | Start an entirely **new Stage 2 game** with all gameplay state reset. No zero-life continuation. | **3** |
| **Pharmacy arrival cutscene** | Advance to standalone **`STAGE 2 COMPLETE`** screen. No Stage 3 launch or new drive yet. | Unchanged |
| **`STAGE 2 COMPLETE`** | Start a **fresh Stage 2 prototype game/run** with full reset. | **3** |
| Normal v0.2 driving | FIRE is reserved; future four-way gas blasts are not implemented yet. | Unchanged |

**Reset values:** A newly started driving attempt restores GAS=**0%**, MI=**2.00**, Q4 speed=**24** / **60 MPH**, default accepted-r3 car position, original scroll phase, elapsed attempt timer=0, no active warning/shake/explosion, and the inactive six-digit SCORE placeholder `000000`. **Fresh games** restore lives=**3**; a **normal failure retry** keeps the lives remaining. The new three-life game after `STAGE 2 COMPLETE` is intentional for standalone v0.2 testing; future Stage 3 integration will replace that prototype behavior.

**Button rearm:** A fresh FIRE press is required **after release** for **each** screen transition. Holding FIRE cannot skip the failure screen, both pharmacy cutscene and completion screen, or instantly restart twice. Console START is not a substitute for these approved trigger-button interactions; any retained START debug reset should be documented separately.

### Implementation acceptance tests (not yet executed)

1. GAS reaches 100% and MI reaches 0 on **the same native tick** → explosion, one-life deduction, no arrival. MI reaches zero while GAS<100 on an **earlier tick** → pharmacy cutscene; frozen gas cannot subsequently trigger explosion.
2. Three failed attempts yield lives **3 → 2 → 1 → 0**; FIRE retries from `BILLY BLEW IT!` with lives **2 then 1**, but FIRE from `GAME OVER` starts a brand-new game with **3** lives.
3. Pharmacy cutscene FIRE proceeds to `STAGE 2 COMPLETE`; a **second, separate fresh FIRE press** starts a three-life Stage 2 prototype run. No ordinary FIRE during driving resets gameplay.
4. Terminal states are latched; no extra life losses, held-FIRE multi-screen skips, premature rounding-based arrival or explosion, or automatic Stage 3 integration.

**Status:** Design approval only. The current v0.2 branch remains documentation-only until Codex implements the playable XEX; no new gameplay tests or Atari800 playtest are claimed. **Next:** final specification consistency review, then a concise Codex v0.2 implementation handoff. Do not merge/tag/delete the v0.2 branch until the user approves the playable prototype.
