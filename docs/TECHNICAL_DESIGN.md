# Gas Blasters '82 — Technical Design (Current)

**Updated:** 2026-11-04  
**Status:** Stage 1 v0.5 engine/prototype is implemented on `main` and broadly user-playtested; **game-wide technical architecture remains incomplete**. For authoritative Stage 1 *game rules*, use [STAGE1_DESIGN.md](STAGE1_DESIGN.md). Superseded plans/handoffs are in [archive/stage1](archive/stage1/README.md).

## Platform, runtime and accepted baseline

- Target: **Atari 800XL, stock 64 KB**, native 6502 XEX. Python is **offline build/validation tooling**, never the target runtime.
- Accepted playable Stage 1 XEX: `assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex` (tag `stage1-v0.5`, manifest SHA-256 `b7e1c423b25f7cb10cd90cd063090579eaea4bd27b7310c70e8ea5f02e169753`). The user has played v0.5 and considers blasting good enough for now; this is not final performance or hardware acceptance.
- The original `assets/opening` continuous Title v1 → Meet the Crew → Arrival sequence (ANTIC E illustrations / DLI palette bands + text), with console START and joystick FIRE cutscene transitions, retains **Arcade Rock** and **Funky Gas Attack** POKEY themes. Alternative title PMG v2/v2.1 was **rejected visually**; gameplay PMG is a separate supported technique.

## Stage 1 map, state and AI

- Three **fixed, full-width 40×22 ANTIC 2 character-tile rooms**, two footer/status rows. No scrolling within Taco Smell, no right-side driving HUD here. Room maps/door-link metadata: `assets/maps/taco_smell_stage1_v02.json` plus three matching `.map` files.
- Each room uses x=0–39, y=0–21; fetch 40-column row offsets using safe 16-bit addressing or precomputed tables. `# B T C R K S` are solid; `. D F N G X` passable for Billy. Grease `G` currently has no special physics.
- Four reciprocal door transitions triggered by **Billy's hitbox center** entering a `D` tile (doorway rows y=10/11). Redraw entire destination room, align inward x=1 or x=38 at the matching row, reset fractions and prevent held-input reentry. `X` at Storage (39,10) marks COMPLETE.
- **Three unique persistent hazmat workers**, dining/kitchen/storage encounter identities, scheduled activation, room-follow delay and bounded chase with **shared eight-cell BFS work per dispatch** (not per worker). See version-specific v0.3 rules JSON for timings and `tools/build_stage1_v05.py` for emitted implementation. CAUGHT/COMPLETE/START reset and stunned-contact grace remain.
- Room entry and restart may require whole-screen redraws; full rendering can span video ticks. Future performance testing must include actual ANTIC DMA, OS interrupts and PMG changes.

## Motion and player graphics

- 16-bit Q4 per-axis logical coordinates (1/16 pixel). **Eight-direction walking**, 24 Q4 units/frame cardinal = 1.5 px/frame, 17 units/frame *per axis* diagonal = 1.0625 px/frame. Immediate joystick sampling each observed NTSC video tick, bounded catch-up (at most two collision-tested ticks). No old eight-frame stepping.
- Sprite is an approximately 8×8 logical-pixel **GTIA PMG Player 0** actor in Stage 1; player's hitbox is **inset 6×6 AABB**, swept substep collision/resolution, solid tiles/edges, axis-aware wall sliding and overlapping worker contact.
- Single-line PMG **PMBASE=$B8** block `$B800–$BFFF`; Billy P0 `$BC00–$BCFF` and, in v0.5, blue-jeans/pose P1 `$BD00–$BDFF`. Horizontal positioning advances at 2 logical pixels per PMG color clock, vertically at 1 scanline. The old BFS Y queue was moved to `$9C00` away from PMG. This is intentionally *temporary* low-resolution character art.
- No gameplay PMG changes to the accepted title sequence. The intro's rejected *title* PMG experiments must not be reactivated.

## Blast extension and effect timing

- **Source-of-truth precedence:** The v0.4 movement tuning JSON includes a historical comment proposing four-way gas blasts for *future* v0.5. **That blast proposal is superseded** by the current **eight-direction** v0.5 gas-blast JSON, executable and [Stage 1 gameplay specification](STAGE1_DESIGN.md). Preserve v0.4 JSON for movement values and historical reproducibility; do not treat its old blast comment as active code guidance.
- **Stage 1 only:** FIRE held switches from WALK to eight-direction AIM. Four stable direction frames trigger **one blast per hold**, FIRE-first works, release to rearm. Eight-frame recovery, twenty-frame cooldown, three regenerating charges (one per 120 observed NTSC frames). **Car blasting remains four-way** and is a different future mechanic.
- Three 6-tick expanding waves create a maximum **seven visible cells** using aimed direction vector and perpendicular flank vector. Cached supercover line-of-sight prevents blasts through solid tiles, D/X, walls or diagonal corner gaps. Temporary cloud/impact glyphs restore previous terrain/worker display rather than redraw full rooms each tick.
- Same-room targets are hit once per burst; animate at most **three cardinal/diagonal 8px tile-step pushes**, one per three observed frame ticks. Stop before furniture, door, X, map edge or worker, and require both neighboring orthogonal cells clear for diagonal pushes. Apply **75-tick stun**, four-tick impact flash and 24-tick blocker stagger without chain-pushing.
- GAS footer status and original short ten-tick POKEY gameplay whoosh do **not** replace the road gas-pressure mechanic or opening soundtrack.
- Authority: `assets/gameplay/taco_smell_stage1_v05_blast.json` and [current Stage 1 specification](STAGE1_DESIGN.md).

## Native source, memory and profiling

The authoritative output generator is `tools/build_stage1_v05.py` (uses the v0.4/v0.3 builders via temporary directories and checked binary hooks; does not regenerate historical files in place). The XEX/source listings/manifest/profile are under `assets/stage1_v05/`. Listings document the emitted instructions, **not independently assembled MAC/65 build inputs**.

Version-specific allocation from the existing v0.5 README: motion extension `$0400+`, main core `$1000+`, blast state `$2900+`, static aim/pose/line-of-sight tables `$5B00+`, blast engine `$7800+`, BFS field and queues near `$9800–$9FFF`, maps and font near `$A000+`, and PMG `$B800–$BFFF`. **Recheck actual manifest segment start/end before adding code**; do not infer available RAM solely from these prose ranges. Current static plus RAM allocation is not a general final-game memory map. BASIC must be disabled; OS/ANTIC/DLI/POKEY shadow safety matters.

Codex's original documented build reported 18 passing v0.5 CPU tests, 15 unchanged v0.4 tests, four passing design validators and a sampled **20,689 CPU-cycle** peak for one three-worker/active-blast scenario. These are **py65 CPU-only measurements**, excluding ANTIC DMA/OS interrupts; no physical Atari test or worst-case 60 Hz guarantee follows.

## Test gates and known coverage

Before a shared code change, follow [Stage 1 Regression Checklist](STAGE1_REGRESSION_CHECKLIST.md), validate both map versions/pressure/blast JSON, regenerate XEX, compare manifest hashes, run versioned py65 tests, then inspect in Atari800. The user's v0.4/v0.5 gameplay-feel reports are broad positive feedback, not proof that every effects/door/restart/POKEY edge is verified.

Open issues, refinements and untested scenarios: [STAGE1_DEFERRED_WORK.md](STAGE1_DEFERRED_WORK.md). Earlier versions: [archive](archive/stage1/README.md) and five tagged commits.

## Subsequent stages and technical decisions still open

**Stage 2 v0.1 — r3 driving mechanics implemented, CPU tested and user-approved in Atari800:** The approved [Stage 2 Driving Design](STAGE2_DESIGN.md) specifies a **standalone** straight-road scrolling XEX, free left/right car steering, automatic forward scrolling, UP acceleration, DOWN braking to a positive minimum, combinable diagonal inputs, a left ~2/3 driving pane, and a **stationary** right ~1/3 placeholder HUD. The exact ANTIC mode, split-pane implementation, PMG/sprite strategy, physical pixel boundaries, tuning and memory map are engineering decisions for Codex to document. ANTIC hardware scrolling cannot be blindly applied across rows if the right-side HUD must remain stationary. A standalone native XEX has now been built and CPU tested; the user ran the original in Atari800 and found the car vertically fixed, despite otherwise acceptable basic driving. The approved revised v0.1 design requires smooth speed-dependent physical sprite Y advancement/retreat, stationary HUD, and preservation of original v0.1 assets. **That v0.1 revision is implemented, and r3 was user-playtested and accepted for driving feel on 2026-11-04.** Further upward travel is deferred. Stage 1 v0.5 is unchanged.

Road 1 uses an upward-facing car on a downward-scrolling road, with a separate **left two-thirds road field + right one-third fixed HUD**; the first drive to pharmacy builds gas pressure toward a 100% failure limit, with no Gas-Nix drops yet. Steering, road narrowing/forks, pursuing vehicles, off-road timing and car blasts need their own driving prototypes, performance budget and memory allocation. **Do not generalize Stage 1's fixed rooms or eight-direction blast behavior to driving.**

Pharmacy/grocery interiors may use fixed rooms, scrolling, or a hybrid, unlike the deliberately fixed Taco Smell rooms. Game-wide timing/AI, memory map, lives, scoring, stages, persistence, PAL and packaging/distribution decisions remain unresolved and must not be marked delivered merely because Stage 1 is a working prototype.

## Stage 2 v0.1 standalone implementation

See [Stage 2 build/memory/timing notes](../assets/stage2_v01/README.md).
Native source is `tools/build_stage2_v01.py`; build is deterministic and stdlib-only.
ANTIC 4 uses fixed 27/13-column road/HUD character layout. Eight terrain categories
with four row phases form 32 animated glyphs; 32 precomputed pages produce downward
pixel scrolling. The inactive character bank receives 256 road bytes per tick,
then publishes on the next VBI tick. Static HUD glyphs remain identical in both
banks, avoiding naive whole-raster scrolling and partially visible glyph updates.

Standalone allocation: code/state $2000–$22C4, screen $2400, display list $2800, fonts
$3000/$3400, single-line PMG $3800 (red car P0 at $3C00, white highlights P1 at $3D00),
road phase pages $4000–$5FFF, immutable font $6000, telemetry tables $6400/$6500,
copy pointers $80–$83. This overlaps Stage 1 opening/music/font/art allocations,
so future integration needs explicit resource switching/relocation, not XEX append.

Per-new-RTCLOK dispatch: publish ready font, poll input, update fractional steering
and positive speed, update PMG/telemetry, prepare hidden font. One observed update
per changed clock; no duplicate update or unbounded catch-up. Sampled costs are
4,575 neutral cycles, up to 4,614 combined-control cycles, excluding DMA/OS costs.

Twelve driving CPU tests and the native three-minute simulated idle run pass;
33 Stage 1 regression tests, four validators and opening validation pass unchanged.
Actual Atari800 visual/audio/controller acceptance, physical 800XL and PAL remain
pending. No pressure/distance/arrival/opponents/forks/penalties/car blasts yet.

## Stage 2 v0.1-r2 — speed-linked car Y (CPU tested, Atari800 pending)

The original `assets/stage2_v01/` and its tools remain immutable comparison files.
New source/output: `tools/build_stage2_v01_r2.py`, `assets/stage2_v01_r2/`.
It reuses only the original read-only art generator, retaining all static road,
font, display-list, initial PMG and telemetry segments byte-for-byte.

Speed indexes a clamped Q4 Y table (8→160px, 24→144px, 56→112px). Current Y
changes at most 12/16 scanline per tick, never overshooting. Neutral maintains
target; START restores exact default X/Y and clears fractional Y. Each integer Y
change clears the full old P0/P1 footprints then copies original 16-row images.
No additional interrupts or zero-page state are introduced.

Controller/state now $2000–$23A5 (934 bytes), below the unchanged screen $2400.
Added low/high target tables $6600–$67FF and 32-byte sprite source $6800–$681F.
All other original allocations, PMBASE, colors and fractional X/speed controls
are unchanged; future integration still needs resource relocation/scene switching.

19 revision tests, 12 original driving tests, 33 Stage 1 regressions, four validators
and opening validation pass. CPU-only samples peak at 5,517 cycles for braking
with steering/PMG relocation, versus 4,766 neutral. Actual Atari800 flicker/
cleanliness and feel, PAL and physical 800XL remain untested. Full details and
profile/hash reports: [r2 README](../assets/stage2_v01_r2/README.md). No merge/tag.


## Stage 2 v0.1-r3 — max-speed car-top Y=80 trial (implemented, CPU tested)

The user has playtested r2 in Atari800 and requested more upward motion. The historical **r2 Y maximum-speed target is 112**. For the next **r3** playtest, target **Y=80** at speed Q4=56, while preserving min/default anchors **(8,160)** and **(24,144)**; all coordinates are 16-scanline car **top-edge Y** values within the 192-scanline viewport. Vertical travel increases from 48 to 80 scanlines. The current r2 linear formula cannot keep the default value unchanged when the max changes; use a bounded, continuous, monotonic **piecewise speed-to-Y mapping** through all three anchors and retain the current 12 Q4/tick vertical smoothing initially. Preserve all r2 and v0.1 artifacts, build a distinct r3 prototype, and verify native PMG row clearing/bounds and unchanged road/HUD behavior. See [Stage 2 design — Section 13](STAGE2_DESIGN.md). The separate r3 XEX was built and CPU verified; the user subsequently played it in Atari800 and approved the driving mechanics for continued development.

R3 implementation: `tools/build_stage2_v01_r3.py` emits continuous piecewise
lookup targets through (8,160), (24,144), (56,80). All native instructions and
loaded segments match r2 exactly except Y-target tables $6600/$6700. Memory map
and current-Y approach/PMG cleanup logic are unchanged; old releases/tools are
preserved. Twenty-one r3 CPU tests pass, as do r2/original driving, Stage 1 and
validator regressions. The same sampled 5,517-cycle peak excludes DMA/OS costs.
Longer travel with unchanged smoothing needs 54 neutral settling ticks after
default→max acceleration. See [r3 README](../assets/stage2_v01_r3/README.md).
Codex did not run Atari800 at build time; the user **subsequently completed an Atari800 r3 playtest**. No physical Atari/PAL test, merge or tag claimed.

## Stage 2 v0.1 acceptance, deferred work, and v0.2 next steps (2026-11-04)

The user **accepted the v0.1-r3 driving mechanics** after playing the standalone XEX in Atari800. This is a gameplay-feel milestone, not blanket hardware/regression sign-off. Accepted r3 tuning includes speed-linked car-top Y **160/144/80** at Q4 speed **8/24/56** with current 12-Q4/tick smoothing, positive scrolling, left/right and diagonal controls, and the fixed 27/13-column split. Preserve the r3 artifact, source, manifest, tests and earlier revisions.

**Deferred optional refinement:** consider permitting the car to move beyond Y=80 toward the upper screen during a later tuning/playtest cycle. Do not change Y endpoints, scroll rates or smoothing as part of unrelated v0.2 implementation.

**v0.2 (design kickoff only):** The new runtime systems are an automatically increasing gas-pressure percentage, a distance-to-pharmacy countdown tied to forward travel/speed, and deterministic arrival-versus-100%-pressure failure states. Convert GAS and MI placeholders to live HUD data while retaining the accepted v0.1 renderer/controls. Specify timing/rates, state precedence, presentation and retry consequences before implementation. Keep v0.2 standalone; current v0.1 allocations overlap the Stage 1 XEX and must not be combined without an explicit integration design. See [Stage 2 specification](STAGE2_DESIGN.md#15-v02-design-kickoff--gas-pressure-and-destination-planning-not-implemented).

## Stage 2 v0.2 — initial timing and numerical model (design targets, 2026-11-07)

The user selected a **2:00 target average drive**, provisional **20–100 MPH** speed range, **60 MPH** typical average, **2.0-mile** distance, and **0→100% gas in 2:45**. A constant elapsed-time rise of `100/165` percentage points/second produces HUD values approximately 18%, 36%, 55%, 73%, 91% at 30/60/90/120/150 seconds and 100% at 165 seconds. A final 15-second change of ~9 points is consistent with the same linear rate; **no separate pressure taper algorithm is specified**.

To plan native 6502 implementation, keep pressure and distance calculations at adequate fractional precision, with conversion only for HUD integers; advance gas with elapsed time independently of speed, and distance using modeled MPH integrated over time (MPH × seconds / 3600). Maintain invariant gas 0..100 and miles 0..2.0. The accepted r3 speed engine is Q4 min/default/max **8/24/56**, so **the approved conversion maps Q4 8→20 MPH, 24→60 MPH and 56→100 MPH using piecewise-linear interpolation**, without changing the approved driver response; exact conversion formulas appear below. A desired 60 MPH average now corresponds to the Q4 default **24**, but observed average player behavior is not guaranteed. The 100%-pressure life-loss/retry flow is approved (§17); handling of simultaneous arrival/pressure thresholds and GAME OVER/new-game controls remains open. These figures are **design selections**, not a claim of new code, tests, or XEX.

## Stage 2 v0.2 — approved gas-pressure failure state machine (2026-11-07; design only)

User-approved starting **lives=3**, gas **0%** and pharmacy distance **2.0 miles** per attempt. Model **DRIVING → WARNING (GAS≥75%) → CRITICAL (GAS≥90%) → EXPLODING (GAS=100%) → FAILURE_MESSAGE or GAME_OVER**, with successful arrival as a separate terminal outcome. Threshold states apply to pressure (not arbitrary elapsed time); all pre-75% r3 steering/speed/Y must remain unchanged.

In warning and critical states, progressively increase **visible car jitter** and a mild, then stronger—but still manageable—**steering impairment**. Exact amplitude and control response are tunable. Keep logical car/roadzone/collision position bounded; avoid applying unbounded jitter to world coordinates. Preserve a static HUD except intentional GAS warning flashes. The new animation should be a **simple explosion effect** suitable for v0.2 playtesting, with full visual/audio polish deferred.

At 100%, **freeze world/driver and elapsed-gas/distance clocks**, play explosion, **decrement lives exactly once**, then display **`BILLY BLEW IT!`** if lives remain or **`GAME OVER`** at zero lives. With lives remaining, use a **fresh joystick FIRE edge** (release then press) from the failure message to restart the same Stage 2 attempt with GAS=0, MI=2.0, default accepted-r3 car position/speed and reset elapsed/scroll state, but **do not replenish spent lives**. FIRE remains reserved during normal driving, distinct from console START. At 0 lives, ordinary retry is unavailable; new-game behavior remains unspecified. Guard against duplicate decrements, held FIRE causing accidental instant restart, and simulation progress after failure. Implement and test this state flow **after** remaining v0.2 arrival precedence/MPH conversion/HUD details are designed. No code or test result is implied by this specification.

## Stage 2 v0.2 — approved pharmacy cutscene / success state (2026-11-07; design only)

At `MI=0.0` with `GAS<100%`, resolve a single successful-arrival event, **freeze the road, car controls, elapsed clock, gas pressure, and distance**, and transition to a short **exterior pharmacy-building cutscene** with a readable pharmacy identification. After the cutscene is presented, await a **fresh joystick FIRE edge** (release before press) to advance to a simple **Stage 2 completed** end-of-prototype screen. Successful arrival does not deduct a life or play failure effects. The Stage 3 pharmacy interior is not part of v0.2 and must not be launched or represented as playable.

Implement a deterministic terminal-state guard so outcome displays cannot resume driving or accumulate pressure. Test that a held FIRE cannot skip cutscene and completion in one press. An exterior scene may use different ANTIC and graphic/PMG allocations from the 27/13 driving view; preserve accepted v0.1-r3 art/controls and verify memory/resource transitions rather than appending unreviewed screen data. Simple original artwork is suitable for v0.2; elaborate cutscene effects/audio are open for later visual polish. **Gas wins a same-tick GAS=100/MI=0 tie**, and FIRE replay from GAME OVER and STAGE 2 COMPLETE is approved in the new terminal-state section below. Precise Q4→MPH mapping and HUD formatting are already approved. This is documentation only; no XEX or tests are claimed.

## Stage 2 v0.2 — approved piecewise native speed → MPH mapping (2026-11-07; design only)

The accepted r3 driving controller continues to use current speed `q` (Q4 scanlines/tick) for scroll rate, acceleration/braking and vertical PMG Y. The user **approved** this independent modeled-world MPH conversion for Stage 2 v0.2 distance-to-pharmacy calculation:

| Q4 speed `q` | Modeled MPH |
| ---: | ---: |
| 8 | 20 |
| 24 | 60 |
| 56 | 100 |

Use a **continuous piecewise-linear calculation** with sufficient fixed-point precision: `MPH=(5×q)/2` for **8≤q≤24**, and `MPH=30+(5×q)/4` for **24≤q≤56**. Preserve exact endpoints, clamp out-of-range inputs, and never modify approved r3 Q4 controls, on-screen speed effects or Y mapping to make MPH line up. Check Q4 16/32/40/48 maps to MPH 40/70/80/90 and no boundary discontinuity occurs at 24. Integrate MPH over real simulated driving time to reduce 2.0 remaining miles, without tying distance to screen-pixel scroll rate or HUD rounding. At constant default Q4=24 (=60 MPH), the travel baseline is 2 minutes; pressure reaches approximately 73% at that time. 60 MPH is the selected **balancing reference**, not proof of achieved player average.

The remaining work before v0.2 implementation is mainly **art and warning/jitter tuning**; **HUD rules, same-tick gas-first terminal precedence, and FIRE replay/new-game policy are approved** in Sections 20–21 of the Stage 2 design. No native v0.2 code or tests were written for this design agreement.

## Stage 2 v0.2 — approved 13-column driving HUD (2026-11-07; design only)

Keep the existing ANTIC 4 **27-column left roadway + 13-column right stationary HUD** on the 40-column/24-row display. The user approved these fixed right-panel elements in order: **GAS PRESSURE (whole integer percent plus 10-segment horizontal bar), PHARMACY (2-decimal miles remaining, initially 2.00 MI), SPEED (whole-number 20–100 MPH derived from Q4), LIVES (three small car icons, fewer after failures), SCORE (six digits, inactive 000000)**. This applies to v0.2 and is the intended reusable driving-stage HUD structure, with destination and relevant fields changing in later stages.

Compute gas, distance, and speed using the separate approved high-precision simulation model; **do not use a rendered number as an authoritative state input**. Specifically, no pre-arrival display of `0.00 MI` because rounding down could accidentally imply completion, and no premature `100%` because rounding up would falsely imply explosion. Actual terminal events follow underlying state only. Change character digits/bar glyphs on displayed-state changes; GAS numeric/bar can also flash in warning state. At GAS **75–89%**, blink **only** the gas indicator slowly; at **90–99%**, blink it faster; keep the rest of the HUD fixed, non-jittering and readable. Flash cadence, final glyph/palette allocation and bar fill rounding can be tuned in Atari800; preserve the accepted r3 driving logic and existing left-road font double buffering.

Small three-life car glyphs may use customized character glyphs inside the existing character-cell HUD; do not claim the previous illustrative art can be used byte-for-byte. Avoid spilling beyond **13×24 cells**, changing the fixed 27/13 pane split, introducing new CPU-heavy DLI work or corrupting glyphs during font-bank swaps and arrival/explosion transitions. See [Stage 2 HUD design §20](STAGE2_DESIGN.md). No native v0.2 code or test has been completed by this documentation change.

## Stage 2 v0.2 — approved terminal priority, FIRE transitions and START handling (2026-11-08; design only)

**Precedence:** During a nonterminal active-driving simulation tick, integrate pressure/distance at full precision and evaluate at most one terminal event: **GAS >= 100% causes an explosion first**, even if MI <= 0 on that tick; otherwise **MI <= 0 causes pharmacy success**. Latch the resulting state. A previous-tick success is final and cannot become a later gas failure. Never determine outcomes from rounded HUD values. Deduct **exactly one life** after the explosion effect, then show `BILLY BLEW IT!` with 1–2 lives remaining, or `GAME OVER` with zero; **never show both for the same failure**.

**FIRE outcomes:** From `BILLY BLEW IT!`, a fresh FIRE edge retries Stage 2 with the **remaining 2 or 1 lives**. From `GAME OVER` a fresh FIRE starts a **new three-life Stage 2 game**. From the pharmacy exterior arrival cutscene, FIRE advances to `STAGE 2 COMPLETE`; only a **second, separately armed** FIRE from that completion screen starts another three-life Stage 2 run. No Stage 3 interior/transition in v0.2. Reset GAS=0%, MI=2.00, accepted-r3 default Q4=24 (60 MPH), default car X/Y, elapsed time/road phase/warning state; keep `SCORE 000000` as an inactive placeholder. Normal failed-attempt retries preserve lost lives, while GAME OVER and completion replays restore three.

**Console START:** The accepted **v0.1-r3** build retains its historical START/F4 full demo reset for regression. In **v0.2 player-facing gameplay**, do **not** wire START/F4 to a reset, extra life, or alternate outcome dismissal: doing so would bypass the agreed FIRE/lives state machine. Test fixtures may directly initialize/reset emulated RAM/state through the offline 6502 harness without adding a runtime cheat key. A separate developer-only shortcut must not ship by default.

**Regression tests for Codex:** test identical-tick threshold crossings vs previous-tick arrival; all three life losses and exact mutually exclusive messages; release-to-rearm FIRE for each outcome; no double transitions; fresh-game vs ordinary-retry lives; START ignored during active driving/failure/arrival/game-over/completion; simulation halted throughout terminal screens; 27/13 HUD and accepted r3 control regressions. [Authoritative Stage 2 design §21](STAGE2_DESIGN.md). These are specifications, **not completed automated tests or an Atari800 playtest**.

## Stage 2 v0.2 validation and delivery requirements (design-only, 2026-11-08)

The complete original Codex implementation prompt's validation/deliverables contract is recorded in [Stage 2 design §22](STAGE2_DESIGN.md). Codex must implement and execute: (1) **NTSC 60 Hz / PAL 50 Hz native-clock simulation** of the 165-second gas timeline; (2) **Q4→MPH and integrated-mileage** exact/boundary tests; (3) **75%/90%/100% pressure, lives and terminal tie** state-machine tests; (4) **FIRE release/rearm and START no-bypass** tests; (5) **27/13 HUD, glyph and double-font-bank/PMG** integrity tests; (6) **XEX load/entry/manifest/zero-page/ROM-hardware memory overlap and per-frame 6502 cycle profiling**; and (7) **preservation/regression** of accepted r3/r2/v0.1 driving and applicable Stage 1 tests.

Run Atari800 in **both NTSC and PAL where available** and log actual visual/performance/scene-transition observations. Otherwise mark emulator validation **NOT RUN** and provide a user playtest checklist. Test harness results are not emulator observations. Deliver a new versioned XEX plus native source/listing, reproducible build, test suite, checksum/segment manifest, updated stage/technical/TODO and README documentation, the commit SHA, commands, actual results, memory/performance findings and limitations. Do not tag/merge before user acceptance; physical Atari 800XL test is optional for the v0.2 milestone.

## Stage 2 v0.2 standalone implementation — 2026-11-09

Implemented on `feature/stage2-pressure-destination-v0.2`; user acceptance pending.
The accepted r3 source/XEX and all Stage 1/opening artifacts remain unchanged.
The native extension uses $7000+, state $2900+, fixed-point tables $6900+, scenes
$8000/$8400/$8800/$8C00, road template $9400 and PMG template $9800–$9FFF.
All actual segments are below $A000; RUNAD remains $2000. Private ZP expands
from $80–$83 to $80–$84/$86–$89. No new interrupt handler or DLI is introduced.

Five checked r3 patches redirect RESET/FRAME/TELEMETRY and select private-ZP
steering steps. A 2,000-frame native differential test verifies original
steering/acceleration/scroll/Y/PMG below 75%. Double-buffered road glyphs remain
separate from static HUD/pharmacy/life glyphs. GRACTL hides the car in static
scenes; retries restore PMG bytes, normal colors and default r3 state.

Time units are 1/300 second, driven by nominal 60/50-Hz RTCLOK deltas of 1–255.
Distance uses exact quarter-MPH integration with 4,320,000 units/mile, native
24-bit arithmetic, underflow saturation, and bounded multiply/divide routines.
Events inspect full counters, gas first, then latch; formatting never triggers
outcomes. Only the explosion timer runs after failure. The original one-motion-
update-per-observed-tick policy is retained; missed-time distance uses sampled
speed. A complete 256-tick clock wrap cannot be recovered from its low byte.

Full memory map, native listings, reproducible commands, timing choices and
limitations: [v0.2 technical/build notes](../assets/stage2_v02/README.md).
Actual segment/checksum and CPU performance reports accompany the XEX. CPU
profiling excludes ANTIC DMA/OS interrupts; whole-screen retries can span
frames. **Atari800 and hardware: NOT RUN**; visual stability, input mapping,
audio silence, real-time NTSC/PAL pacing and gameplay feel require user tests.

## Stage 2 v0.2-r1 — GTIA register alias correction

HPOSP0 writes and M0PF reads share $D000. The v0.2 warning code incorrectly read
this address as position feedback, sending both player planes off-screen at 75%.
The separately versioned r1 uses RAM PIX_LO + 48 as its unshaken origin for both
warning directions. No PMG memory, enable/color setup, pressure or driving tuning
changes. Controller grows six bytes; no additional state, ZP or resources.

Regression tests model independent GTIA collision reads/position write latches,
prove the original failure and check continuous car visibility at 74/75/90/99%,
including flash phases, all 16 collision values, speed/Y anchors and edges.
Flat-memory CPU tests alone cannot catch register read/write alias bugs. Full
r1 v0.2 and accepted r3 CPU suites accompany the [versioned fix](../assets/stage2_v02_r1/README.md).
Atari800/hardware visual testing remains NOT RUN in this environment.

## Stage 2 v0.2-r1 user Atari800 acceptance — 2026-11-08

The user re-playtested the corrected standalone v0.2-r1 XEX after the 75% car visibility bug and reported that **everything works as expected**. The user explicitly approved v0.2-r1 acceptance and milestone closeout. The accepted binary is `assets/stage2_v02_r1/GasBlasters82_Stage2_Pressure_Destination_v02_r1.xex`. Codex's existing fixed-build automated evidence remains **27 r1 CPU tests and 21 accepted r3 regression tests passing**; the user's Atari800 playtest provides independent visual/feel acceptance, not a claim of additional automated tests, PAL-specific Atari800 verification or physical 800XL testing. Retain the reported CPU/GTIA-bus test limitations and all versioned artifacts; future v0.3 development can build on this accepted code without retuning r3 controls.
