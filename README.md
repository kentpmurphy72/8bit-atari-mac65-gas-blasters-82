# Gas Blasters '82

A work-in-progress comedy action game for the **Atari 800XL (64 KB)**, written in native **6502 machine code** and distributed as Atari XEX prototypes. Play as Billy Blaster: escape Taco Smell, survive a road trip to a pharmacy for Gas-Nix, and ultimately race home. The full multi-stage game is **not yet implemented**.

## Current playable baseline: Stage 1 v0.5

**Stage 1: Escape Taco Smell** is the accepted *playable prototype* on `main`, preserved at tag [`stage1-v0.5`](https://github.com/kentpmurphy72/8bit-atari-mac65-gas-blasters-82/tree/stage1-v0.5). The user has playtested it and considers **eight-way walking and indoor gas blasting good enough for now**, with balancing and polish deferred. This is **not** a production release or a claim of exhaustive emulator/hardware validation.

- Three fixed, full-width restaurant rooms: Dining, Kitchen, Storage/Rear Exit; backtracking and three persistent hazmat pursuers.
- Smooth eight-way Billy movement, collision/wall slide, and **eight-direction on-foot gas blasts** with a growing cloud, enemy knockback/stun, renewable gas shots and a short sound effect.
- Original continuous **Title → Meet the Crew → Arriving at Taco Smell → Stage 1** sequence and POKEY music.
- Stage 1 stops at its completion screen. **There is no connected Stage 2 driving gameplay in the Stage 1 XEX.**

## Stage 2 v0.2 — playable pressure/destination prototype

[Download the fixed standalone v0.2-r1 XEX](assets/stage2_v02_r1/GasBlasters82_Stage2_Pressure_Destination_v02_r1.xex).
**r1 fixes the car disappearing at 75% pressure:** shake now uses RAM X rather
than reading GTIA’s write-only position register. Original v0.2 artifacts are
preserved; approved gameplay is unchanged.

Built on accepted r3 driving: live gas pressure, a 2.00-mile trip, 75%/90%
warning shake/handling, three lives, green explosion/retry, pharmacy exterior
and two separate FIRE actions for completion/new game. START/F4 is disabled;
FIRE is inert during driving. No Stage 1 integration or Stage 3 is included.

```bash
python3 tools/build_stage2_v02_r1.py
# Install tools/requirements-stage1-test.txt into your virtual environment first.
.venv/bin/python tools/test_stage2_v02_r1.py
.venv/bin/python tools/profile_stage2_v02_r1.py
atari800 -xl -ntsc -nobasic -run assets/stage2_v02_r1/GasBlasters82_Stage2_Pressure_Destination_v02_r1.xex
# Repeat with -pal instead of -ntsc.
```

**Stage 2 v0.2-r1 user-accepted in Atari800 (2026-11-08); CPU tests passed.** The user first reported a car-disappearance bug at 75% GAS, then playtested the corrected r1 XEX and reported **everything worked as expected**. This is **user gameplay acceptance of the standalone v0.2 prototype**, not a claim of PAL-specific coverage, exhaustive regression, or physical 800XL testing. **Codex could not run Atari800 in its own environment**; its original emulator status remains NOT RUN, separate from the user's playtest.
See [build, memory and playtest instructions](assets/stage2_v02_r1/README.md) and
[actual validation results](assets/stage2_v02_r1/validation.md). Earlier dated design
entries below describe the historical v0.1→v0.2 planning boundary.

## Stage 2 v0.1 — driving mechanics accepted (r3, merged into main)

The original v0.1 was user-playtested: basic driving was fine, but the car needed
to move vertically with speed. **v0.1-r2 now implements that refinement** on
`feature/stage2-driving-v0.1`, with CPU tests passing; the user has now playtested r2 in Atari800.
UP increases road speed and moves the car toward a higher position; DOWN brakes
to a positive minimum and moves it lower. Neutral preserves speed/target Y after
brief smoothing. The user playtested r2 in Atari800 and requested a higher maximum-speed
position: **car-top Y=80 instead of r2 Y=112**. The resulting **r3 XEX was user-playtested in Atari800 and its driving mechanics approved for now on 2026-11-04**. Further upward screen travel may be evaluated later, but is deferred. See [Stage 2 design](docs/STAGE2_DESIGN.md).
Original steering, road zones, fixed HUD and exclusions remain. **Next: Stage 2 v0.2 — live gas pressure and miles to the pharmacy, with arrival/failure outcomes.** Initial design balance: **2:00 typical drive, 20–100 MPH (60 MPH typical), 2.0 miles, gas 0→100% by 2:45**. These values are provisional for playtesting. Stage 2 v0.2 now also has **approved three-life gameplay**, progressive shaking/handling difficulty at GAS **75%** and **90%**, and a **100% explosion/failure sequence**: freeze, basic gas explosion, lose one life, display `BILLY BLEW IT!`, then FIRE/trigger to retry Stage 2 with 0% gas, 2.0 miles and default car state while keeping remaining lives; at zero lives show `GAME OVER`. Pharmacy arrival is now designed: at MI=0 while GAS<100, freeze driving, show a **brief cutscene featuring the pharmacy building**, then a fresh **FIRE/trigger** press advances to the **standalone Stage 2 completion screen**. No Stage 3 interior or life loss on success. **The r3-Q4-to-MPH mapping is approved:** internal speed **8→20 MPH, 24→60 MPH, 56→100 MPH**, with piecewise interpolation and unchanged driving feel. **HUD presentation is now approved:** retain the stationary 13-column pane with GAS % and a 10-segment bar, PHARMACY distance to 0.01 mile, whole MPH, three miniature car life icons and a six-digit inactive score; GAS alone flashes progressively at 75%/90%. See [HUD design §20](docs/STAGE2_DESIGN.md). Precise artwork, visual/handling tuning, and **terminal-state rules are now approved:** GAS=100 wins a same-tick tie with arriving at MI=0; FIRE after BILLY BLEW IT! retries with remaining lives, FIRE at GAME OVER starts a new three-life Stage 2 game, and FIRE at STAGE 2 COMPLETE begins a fresh three-life Stage 2 run. The cutscene-to-COMPLETE and COMPLETE-to-new-run actions require distinct presses ([Stage 2 §21](docs/STAGE2_DESIGN.md)). **That planning status is superseded by the v0.2 implementation above**. See [v0.2 balance decisions](docs/STAGE2_DESIGN.md#16-v02-provisional-timing-speed-distance-and-gas-pressure-balance--2026-11-07). The completed Stage 2 chase remains open.

## Run Stage 2 separately

[Download revision 3](assets/stage2_v01_r3/GasBlasters82_Stage2_Driving_v01_r3.xex):

```bash
atari800 -xl -ntsc -nobasic -run assets/stage2_v01_r3/GasBlasters82_Stage2_Driving_v01_r3.xex
```

The [original v0.1 XEX](assets/stage2_v01/GasBlasters82_Stage2_Driving_v01.xex),
[r2 XEX](assets/stage2_v01_r2/GasBlasters82_Stage2_Driving_v01_r2.xex) and all their
artifacts/tools remain unchanged for comparison. Joystick 1 steers and
changes speed; diagonals combine both. START/F4 resets X/Y/speed; FIRE is reserved.
GAS/MI/SCORE/LIVES remain static demo values. No pressure, destination or penalties.

```bash
python3 tools/build_stage2_v01_r3.py
# With the existing py65 dependency installed:
python3 tools/test_stage2_v01_r3.py
python3 tools/test_stage2_v01.py
python3 tools/profile_stage2_v01_r3.py
```

21 r3 tests, 19 preserved r2 tests, 12 original-driving tests, 33 Stage 1 tests, four validators and
opening validation pass. The revision includes a three-minute native simulated
idle test and full PMG row-cleanup checks. **Codex did not run Atari800 during the build; the user subsequently tested r3 in Atari800 and approved its driving feel.**
See [r3 build/tuning/playtest notes](assets/stage2_v01_r3/README.md). Stage 1 remains
unchanged, with no automatic Stage 2 transition. That historical v0.1 driving milestone was subsequently tagged as `stage2-v0.1` and merged into `main`; **the separate v0.2 binary above now awaits acceptance**.

## Run the prototype

Download [`GasBlasters82_Stage1_Playable_v05.xex`](assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex) or use the repository copy. Configure the Atari800 emulator with an appropriate Atari XL OS ROM and BASIC disabled:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex
```

Console **START** (usually F4 in Atari800) advances the title. On the crew and arrival screens, use joystick **FIRE** and release between screens. During Stage 1, use **joystick port 1** for eight-way movement. **Hold FIRE** to stop and aim (eight directions); after a short wind-up one gas blast fires; **release FIRE** to walk and rearm. Press START to restart gameplay. Reach the Storage rear exit to finish.

The authoritative control details and current tuning are in [Stage 1 Design](docs/STAGE1_DESIGN.md). **Car/road blasts are a separate future mechanic and remain four-way.**

## Build and test

The runtime is 6502, not Python. Python 3 is used only to reproducibly emit XEX files, check design data and run tests. Rebuild the latest prototype:

```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/validate_taco_smell_stage1_v02.py
python3 tools/validate_stage1_pressure_v03.py
python3 tools/validate_stage1_blast_v05.py
python3 tools/build_stage1_v05.py
```

For the offline 6502 CPU test harness, install the pinned requirements into a virtual environment, then:

```bash
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements-stage1-test.txt
.venv/bin/python tools/test_stage1_v04.py
.venv/bin/python tools/test_stage1_v05.py
```

On Windows, use the corresponding `.venv\Scripts\python.exe` and `.venv\Scripts\pip.exe`. The [version-specific build README](assets/stage1_v05/README.md) records code allocation, original implementation details, binary SHA-256 and earlier CPU-only test results. These tests **do not replace Atari800 or physical 800XL playtesting**.

## Documentation map

| Document | Purpose |
| --- | --- |
| [Stage 1 Design](docs/STAGE1_DESIGN.md) | **Authoritative current Stage 1 gameplay/controls**; implemented vs provisional |
| [Stage 2 Driving Design](docs/STAGE2_DESIGN.md) | **Authoritative Stage 2 specification**; v0.1-r3 accepted, v0.2 gameplay §§16–21, and Codex verification/delivery requirements §22 |
| [Stage 1 Deferred Work](docs/STAGE1_DEFERRED_WORK.md) | Known limitations, unverified behavior and optional improvements |
| [Stage 1 Regression Checklist](docs/STAGE1_REGRESSION_CHECKLIST.md) | Build, automated and manual emulator test gates |
| [Game Design](docs/GAME_DESIGN.md) | Whole-game concept, restaurants, stage sequence and road rules |
| [Technical Design](docs/TECHNICAL_DESIGN.md) | Current engine, graphics, timing and memory design |
| [Art Assets](docs/ART_ASSETS.md) | Visual inventory and proposed final artwork |
| [Project TODO](docs/TODO.md) | Current progress and outstanding work |
| [Repository Workflow](docs/REPOSITORY_WORKFLOW.md) | Branches, immutable tags, artifacts and Codex responsibilities |
| [Stage 1 Archive](docs/archive/stage1/README.md) | Superseded versioned design specs and Codex handoffs |
| [Codex Rules](AGENTS.md) | Permanent agent development and regression requirements |

## Version history

| Tag | Milestone |
| --- | --- |
| [stage1-v0.1](https://github.com/kentpmurphy72/8bit-atari-mac65-gas-blasters-82/tree/stage1-v0.1) | First playable Taco Smell prototype |
| [stage1-v0.2](https://github.com/kentpmurphy72/8bit-atari-mac65-gas-blasters-82/tree/stage1-v0.2) | Three fixed rooms / room transitions |
| [stage1-v0.3](https://github.com/kentpmurphy72/8bit-atari-mac65-gas-blasters-82/tree/stage1-v0.3) | Three-worker pursuit and initial blast |
| [stage1-v0.4](https://github.com/kentpmurphy72/8bit-atari-mac65-gas-blasters-82/tree/stage1-v0.4) | Approved responsive eight-way movement |
| [stage1-v0.5](https://github.com/kentpmurphy72/8bit-atari-mac65-gas-blasters-82/tree/stage1-v0.5) | Accepted Stage 1 gameplay prototype with eight-way gas blasting |
| [stage2-v0.1](https://github.com/kentpmurphy72/8bit-atari-mac65-gas-blasters-82/tree/stage2-v0.1) | Accepted, user-playtested Stage 2 v0.1-r3 standalone driving prototype (`e0e4422`) |

**Stage 2 v0.2 is user-accepted at the corrected r1 revision.** The tag `stage2-v0.2` is **approved but not yet created** as of this documentation commit; do not list it as an existing immutable tag until verified. Its intended target is the final milestone acceptance commit after this documentation update.

Versioned XEXs, builders, tests and manifests are retained in the repository. The feature branches for these five milestones were removed **after tags were verified**. Future stages use new feature branches, reviewed integration into `main`, and new tags. See [workflow](docs/REPOSITORY_WORKFLOW.md).

**Project status:** Stage 1 v0.5 accepted for continued game development; later stages and complete-game systems are still in development.

### Stage 2 v0.2 final gameplay controls (approved 2026-11-08)

The v0.2 design now resolves the remaining terminal rules: **GAS 100% wins any same-tick tie with reaching 0.0 miles**. A fresh joystick **FIRE** retries after `BILLY BLEW IT!` with remaining lives, starts a new **three-life game** after `GAME OVER`, advances the pharmacy cutscene to `STAGE 2 COMPLETE`, and starts a fresh **three-life Stage 2 prototype run** from the completion screen (a separate press). **After the explosion, display `BILLY BLEW IT!` only when lives remain, otherwise `GAME OVER`.** For v0.2, **console START/F4 is not an in-game reset**: FIRE is the approved gameplay control and tests may reset emulated state through their harness. The older v0.1-r3 build **retains** its original START reset. Earlier dated open questions are superseded by [Stage 2 design §21](docs/STAGE2_DESIGN.md). These controls are now implemented and the corrected **v0.2-r1 standalone XEX has been accepted after the user's Atari800 playtest**. Later road mechanics and actual Stage 3 integration are deferred.
