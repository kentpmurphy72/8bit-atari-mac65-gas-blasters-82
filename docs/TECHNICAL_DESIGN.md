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

**Stage 2 v0.1 — first XEX implemented/CPU tested and user-playtested; vertical movement revision pending:** The approved [Stage 2 Driving Design](STAGE2_DESIGN.md) specifies a **standalone** straight-road scrolling XEX, free left/right car steering, automatic forward scrolling, UP acceleration, DOWN braking to a positive minimum, combinable diagonal inputs, a left ~2/3 driving pane, and a **stationary** right ~1/3 placeholder HUD. The exact ANTIC mode, split-pane implementation, PMG/sprite strategy, physical pixel boundaries, tuning and memory map are engineering decisions for Codex to document. ANTIC hardware scrolling cannot be blindly applied across rows if the right-side HUD must remain stationary. A standalone native XEX has now been built and CPU tested; the user ran the original in Atari800 and found the car vertically fixed, despite otherwise acceptable basic driving. The approved revised v0.1 design requires smooth speed-dependent physical sprite Y advancement/retreat, stationary HUD, and preservation of original v0.1 assets. **The revision is not yet implemented.** Stage 1 v0.5 is unchanged.

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


## Stage 2 v0.1-r3 — max-speed car-top Y=80 proposal (not implemented)

The user has playtested r2 in Atari800 and requested more upward motion. The historical **r2 Y maximum-speed target is 112**. For the next **r3** playtest, target **Y=80** at speed Q4=56, while preserving min/default anchors **(8,160)** and **(24,144)**; all coordinates are 16-scanline car **top-edge Y** values within the 192-scanline viewport. Vertical travel increases from 48 to 80 scanlines. The current r2 linear formula cannot keep the default value unchanged when the max changes; use a bounded, continuous, monotonic **piecewise speed-to-Y mapping** through all three anchors and retain the current 12 Q4/tick vertical smoothing initially. Preserve all r2 and v0.1 artifacts, build a distinct r3 prototype, and verify native PMG row clearing/bounds and unchanged road/HUD behavior. See [Stage 2 design — Section 13](STAGE2_DESIGN.md). Actual implementation, CPU verification and emulator acceptance for r3 remain pending.
