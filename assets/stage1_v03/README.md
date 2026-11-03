# Gas Blasters '82 — Stage 1 Playable Prototype v0.3

> **Historical prototype status (2026-11-03):** This `v0.3` milestone is preserved at immutable Git tag `stage1-v0.3`. Its work and history were integrated into `main` via the accepted `stage1-v0.5` baseline; the original feature branches were deleted after tagging. Three persistent hazmat workers; the user playtested it and found movement slow and gas blasting unsatisfying. **Any older “not merged” or “emulator test pending” language below records the original build-time status, not current repository status.** For implemented current behavior, see [Stage 1 Design](../../docs/STAGE1_DESIGN.md). This versioned artifact and build instructions are retained unchanged except for this note.


Native 6502 Atari XEX for a stock **64 KB Atari 800XL**, BASIC disabled. Built on
`feature/stage1-pressure-v0.3` from the user-tested v0.2 branch plus v0.3 design
files from main. **Not merged; Atari800 playtesting is pending.** Enemy timings
and combat values are prototype defaults, not a finalized difficulty balance.

## Run and controls

From the repository root, with Atari800's XL OS ROM configured:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1_v03/GasBlasters82_Stage1_Playable_v03.xex
```

After downloading the XEX into the current directory:

```bash
atari800 -xl -ntsc -nobasic -run ./GasBlasters82_Stage1_Playable_v03.xex
```

- **Title: console START, normally F4** (possibly Fn+F4 on a laptop). Joystick
  FIRE does not advance the title. Release before pressing.
- **Meet the Crew / Arrival: joystick port 1 FIRE.** Original input debounce,
  title/cutscene art, captions, DLI palettes and POKEY songs are preserved.
- **Move:** joystick port 1, one cardinal direction. Original up/down/left/right
  priority handles simultaneous directions; no diagonal corner cutting.
- **Gas blast:** hold FIRE with a direction already selected. Billy stops moving
  while FIRE is held. One shot per new press; release before another shot.
  No-direction presses do not shoot. Pressing during cooldown consumes that
  press; it will not fire automatically when cooldown ends.
- **START/F4** restarts Stage 1, including from CAUGHT or STAGE COMPLETE. Reload
  the XEX to replay the introduction. FIRE carried over from Arrival must be
  released before the first indoor shot.

## Gameplay

Unchanged 40×22 dining, kitchen and storage rooms, full-width ANTIC 2 rendering,
plus two footer lines. Both doorway rows work forward/backward, preserving y
and placing Billy one tile inside the destination. Storage X=(39,10) completes
Stage 1; no Road 1 follows. No new map geometry, grease physics, score/lives,
indoor pressure meter, cutscenes, music or PMG title experiments.

| Persistent worker | Initial room / tile | Activation | Movement interval |
|---|---|---|---|
| hazmat_front | Dining (2,10) | 60 NTSC frame ticks after stage begins | 12 frame ticks |
| hazmat_kitchen | Kitchen (29,11) | 30 ticks after first kitchen entry | 10 ticks |
| hazmat_storage | Storage (30,10) | 30 ticks after first storage entry | 10 ticks |

Each activates only once per restart, even if Billy revisits rooms. Its position,
activation countdown, stun and follow state persist. Off-screen workers follow
one adjacent link at a time after **45 ticks**; returning to their source cancels
pending travel. Stun pauses movement and room-follow countdowns. Occupied doorway
entries select a valid neighboring tile, avoiding Billy and other workers. Only
a worker occupying Billy's originally preferred entry gets **15 ticks of contact
grace**; this is per-worker, not room-wide immunity.

A blast is a **three-tile ray**, stopped by solids, bounds and room/exit triggers.
It affects the nearest active worker in that room, including an already stunned
one. Knockback is **up to two tiles**, stopped by solids, bounds, door/exit tiles
and another worker. The target receives **60 ticks of stun**, harmless on contact.
If stun ends while overlapping Billy, one player movement opportunity is allowed
before resolving contact; holding FIRE does not extend this grace indefinitely.
Cooldown is **72 ticks** per fired shot. A cloud glyph lasts **eight ticks**, then
underlying terrain/actors return. Unstunned contact causes CAUGHT; result states
freeze gameplay. Restart clears all worker, stun, grace, blast and cooldown state.

Temporary monochrome glyphs distinguish Billy (running figure), mobile worker
(helmet), stunned worker (crossed/dazed figure) and gas (cloud pattern).

## Reproducible build and tests

Build uses Python 3 standard library only; no Python runs on Atari:

```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
python3 tools/validate_stage1_pressure_v03.py
python3 tools/build_stage1_v03.py
```

Test/profile dependency is py65 1.2.0, already pinned in the retained requirements:

```bash
python3 -m venv /tmp/gas-stage1-tests
/tmp/gas-stage1-tests/bin/pip install -r tools/requirements-stage1-test.txt
/tmp/gas-stage1-tests/bin/python tools/test_stage1_v03.py
/tmp/gas-stage1-tests/bin/python tools/test_stage1_v02.py
/tmp/gas-stage1-tests/bin/python tools/test_stage1.py
python3 tools/validate_opening_sequence.py --output /tmp/gas-opening-v03-validation
/tmp/gas-stage1-tests/bin/python tools/profile_stage1_v03.py
```

Authoritative 6502 emitter: `tools/build_stage1_v03.py`, derived from the retained
v0.2 emitter. Generated reference listing: `stage1_6502.asm` (not a separately
MAC/65-assembled source). Maps/doors come from v0.2 JSON/maps; encounter and blast
constants derive from `assets/gameplay/taco_smell_stage1_v03_rules.json`.
`manifest.json` records SHA-256, labels, segments, tuning and the search budget.
`profile.json` records repeatable CPU-only measurements for this exact XEX hash.
All v0.1/v0.2 source, tests, XEXs, maps and the opening-v1 assets remain unchanged.

## Navigation, rendering and measured costs

A **single shared reverse BFS field** covers Billy's current room, with at most
**eight dequeued cells per main-loop iteration total**, regardless of actor count.
Workers move using known field directions. During field construction or an
outdated goal, a deterministic, cardinal, collision-checked fallback keeps their
movement timers active. Completed fields are reused while Billy stays at their
goal; a moved goal starts a new bounded search. Room changes invalidate old search
state. No worker launches a separate BFS or waits for a complete search to move.
This is provisional pursuit AI; stale goals and crowded corridors need playtests.

Normal rendering restores the previous four actor cells and at most three gas
cells, then overlays current workers, Billy, gas and footer. A whole-room copy is
limited to room entry/restart. Elapsed RTCLOK/VBI ticks drive spawn, follow, stun,
cooldown, visual and movement timers, with wraparound and saturating subtraction.
Billy retains the v0.2 eight-observed-frame movement cadence.

CPU-only samples (py65, **excluding ANTIC DMA and OS interrupts**):

| Sample | CPU cycles |
|---|---:|
| Stage initialization and complete room draw | 22,319 |
| Maximum normal iteration, three workers, 45-frame sample | 21,020 |
| Three-worker blast-hit iteration | 13,381 |
| Occupied room transition, full redraw/search initialization | 42,195 |

The three workers' observed move intervals in that sample are exactly **12, 10,
10 frame ticks**. A room transition can span multiple video frames. These samples
are not a worst-case timing proof or an Atari800 frame-rate claim. Actual input
latency, catch frequency, enemy fairness and clear time remain unmeasured in an
Atari emulator; no 70–105 second stage-duration claim is made.

Memory stays below $C000 with BASIC disabled: stage code/state $1000–$1E45;
opening controller $2000 and retained artwork/music through $97FF; messages at
$2800; shared 880-byte BFS scratch $9800–$9B6F; maps $A000–$AA4F; row tables at
$AA80/$AB10/$AB40; charset $AC00–$AFFF; screen $B000–$B3BF; queues at $B400 and
$B900 (880 bytes each); zero-page pointers $80–$8B. The manifest has exact loaded
segment extents. No OS ROM, BASIC ROM, hardware register or stack region is used
for stage data. The opening controller still receives only two dispatch patches.

## Validation results and Atari800 checklist

Automated results:

- **23 v0.3 6502 CPU tests pass**: unique timed spawns; all doorway rows and backtracking;
  multi-worker follow/cancellation/occupancy; movement cadence and bounded search;
  navigation around obstacles in all rooms; FIRE edge/no-direction/cooldown;
  all four aim directions and priority; range/nearest target/current-room filtering;
  solid occlusion; blocked knockback; stun/contact/separation; conditional entry
  grace; visual cleanup; restart and win; clock wrap; memory guards/non-overlap;
  deterministic builds and preserved opening/v0.1/v0.2 bytes.
- **16 retained v0.2 tests and nine retained v0.1 tests pass.**
- Both map validators and the v0.3 pressure-rule validator pass.
- Existing opening validator passes (48,650 CPU instructions, palettes, controls,
  song switching and continuity). Its output is kept outside the checkout.

Still to test in Atari800 (and later actual 800XL hardware):

1. Title START/F4, both cutscene FIRE controls, unchanged visuals and music.
2. Keyboard/physical joystick response while all workers are active and during
   room changes; no screen corruption or stuck old actor/cloud glyphs.
3. Dining spawn at ~1s; first-entry interceptors; 45-frame follow and cancellation;
   persistent workers on backtracking, with no duplicates or room skipping.
4. FIRE+direction range, no movement while held, one shot per press, visible effect,
   knockback collision, 1s stun, 1.2s cooldown and fair stun-expiry contact.
5. Catches, repeated START restarts and storage X success without Road 1.
6. NTSC clear times and challenge. PAL remains unverified.

Please report **total clear time (and per-room times if possible), catches/restarts,
blast use, responsiveness, and which room feels least challenging**, including
whether storage provides a strong final encounter. Tune for useful evasive choices
and fun rather than padding the stage with delays.
