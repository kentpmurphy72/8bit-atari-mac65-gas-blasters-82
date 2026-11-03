# Gas Blasters '82

A work-in-progress comedy action game for the **Atari 800XL (64 KB)**, written in native **6502 machine code** and distributed as Atari XEX prototypes. Play as Billy Blaster: escape Taco Smell, survive a road trip to a pharmacy for Gas-Nix, and ultimately race home. The full multi-stage game is **not yet implemented**.

## Current playable baseline: Stage 1 v0.5

**Stage 1: Escape Taco Smell** is the accepted *playable prototype* on `main`, preserved at tag [`stage1-v0.5`](https://github.com/kentpmurphy72/8bit-atari-mac65-gas-blasters-82/tree/stage1-v0.5). The user has playtested it and considers **eight-way walking and indoor gas blasting good enough for now**, with balancing and polish deferred. This is **not** a production release or a claim of exhaustive emulator/hardware validation.

- Three fixed, full-width restaurant rooms: Dining, Kitchen, Storage/Rear Exit; backtracking and three persistent hazmat pursuers.
- Smooth eight-way Billy movement, collision/wall slide, and **eight-direction on-foot gas blasts** with a growing cloud, enemy knockback/stun, renewable gas shots and a short sound effect.
- Original continuous **Title → Meet the Crew → Arriving at Taco Smell → Stage 1** sequence and POKEY music.
- Stage 1 stops at its completion screen. **There is no connected Stage 2 driving gameplay in the Stage 1 XEX.**

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

Versioned XEXs, builders, tests and manifests are retained in the repository. The feature branches for these five milestones were removed **after tags were verified**. Future stages use new feature branches, reviewed integration into `main`, and new tags. See [workflow](docs/REPOSITORY_WORKFLOW.md).

**Project status:** Stage 1 v0.5 accepted for continued game development; later stages and complete-game systems are still in development.
