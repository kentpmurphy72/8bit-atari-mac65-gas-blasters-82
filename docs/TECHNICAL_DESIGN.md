# Gas Blasters '82 — Technical Design (Current)

**Updated:** 2026-11-02  
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

Road 1 uses an upward-facing car on a downward-scrolling road, with a separate **left two-thirds road field + right one-third fixed HUD**; the first drive to pharmacy builds gas pressure toward a 100% failure limit, with no Gas-Nix drops yet. Steering, road narrowing/forks, pursuing vehicles, off-road timing and car blasts need their own driving prototypes, performance budget and memory allocation. **Do not generalize Stage 1's fixed rooms or eight-direction blast behavior to driving.**

Pharmacy/grocery interiors may use fixed rooms, scrolling, or a hybrid, unlike the deliberately fixed Taco Smell rooms. Game-wide timing/AI, memory map, lives, scoring, stages, persistence, PAL and packaging/distribution decisions remain unresolved and must not be marked delivered merely because Stage 1 is a working prototype.
