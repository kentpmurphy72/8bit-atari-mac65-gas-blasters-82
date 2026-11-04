# Gas Blasters '82 — Stage 2: Drive to the Pharmacy

**Document:** Stage 2 Gameplay and Technical Design  
**Milestone:** v0.1 — Basic Driving Prototype  
**Date:** 2026-11-03  
**Target:** Atari 800XL, stock 64 KB, native 6502 Atari XEX  
**Working branch:** `feature/stage2-driving-v0.1`  
**Status:** Original v0.1 built and user-playtested in Atari800; driving feel requires speed-linked vertical car movement. The separately versioned v0.1-r2 revision is now implemented and CPU tested; its Atari800 acceptance is pending.
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

**v0.2 — pressure and destination:** gas pressure starts near 0%, rises toward 100%; miles count down to the pharmacy; successful arrival must precede the threshold. Determine gas growth and travel-speed-to-mile tuning, 100%-failure consequences, and a restart policy during v0.2 design. This **is not working in v0.1**.

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
