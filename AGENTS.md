# Gas Blasters '82 — Standing Codex / Agent Instructions

**Project target:** Atari **800XL stock 64 KB**; runtime must be native **6502 machine code** in an Atari XEX. Python helpers may build, validate and test binaries offline; no Python runs inside the Atari game.

## Read-first sources (current, not historical)

1. [Root README](README.md) — what's playable, launch/build steps and current baseline.
2. [Whole-game design](docs/GAME_DESIGN.md) for stage sequence / car rules; [current Stage 1 design](docs/STAGE1_DESIGN.md) for accepted restaurant controls and gameplay; [Stage 2 design](docs/STAGE2_DESIGN.md) for the approved driving v0.1 scope and acceptance gates. Do **not** implement obsolete v0.1–v0.5 handoff text as a new task.
3. [Technical design](docs/TECHNICAL_DESIGN.md), [art inventory](docs/ART_ASSETS.md), [Stage 1 regression tests](docs/STAGE1_REGRESSION_CHECKLIST.md), [deferred work](docs/STAGE1_DEFERRED_WORK.md) and [project TODO](docs/TODO.md).
4. [Repository workflow](docs/REPOSITORY_WORKFLOW.md) — branch naming, immutable tags, artifact versions, reporting and responsibilities.

**Stage 1 is an accepted playable prototype at `stage1-v0.5` on `main`.** The user approved v0.4 smooth diagonal movement and said v0.5 indoor gas blasting is **good enough for now**, with polish deferred. Historical Stage 1 feature branches were **merged/tagged/deleted**; **do not recreate them**. Original source/XEX and proposed rules remain accessible via the tags and [docs archive](docs/archive/stage1/README.md). A separate Stage 2 branch may already exist; inspect live refs before creating or rebasing anything.

## Engineering rules

- **Respect platform boundaries:** no 65816-only instructions; no unreviewed RAM/zero-page writes overlapping the 64 KB Atari memory map, OS/CIO, ANTIC/DLI, GTIA PMG, POKEY, screen, font, buffers, enemy queues or load segments. Inspect the *actual* XEX manifest and measured timing.
- **Preserve accepted opening:** Title v1 → Meet the Crew → Arrival → Stage 1, original art/captions/START/FIRE input and Arcade Rock / Funky Gas Attack audio. Title PMG alternatives v2/v2.1 were visually rejected; gameplay PMG is different and permitted.
- **Preserve Stage 1 baseline:** three non-scrolling 40×22 rooms, reciprocal doors/backtracking, 3 hazmat identities/AI, Q4 eight-way walking/wall sliding, 6×6 hitboxes, **eight-way on-foot gas blasts**, GAS footer, CAUGHT/COMPLETE/START. Car-road gas blasts are **four-way**. Tuning changes require explicit scope and user playtest.
- **Version everything:** use focused `feature/<stage>-<purpose>-v0.x` or `fix/<scope>` branches from current `main` unless specified. Keep every historical XEX/source/manifest intact; generate new versioned outputs. Never overwrite or retarget public prototype tags.
- **Tests are evidence, not claims:** run the relevant map/pressure/blast validators, prior accepted version CPU tests, current version CPU tests, segment/hashing/profile checks and full Atari800 visual/audio/manual regression where possible. Distinguish **design complete / implemented / py65 verified / Atari800 user-playtested / hardware-tested**. Do not claim hands-on emulator results from py65 alone.
- **Deliver clearly:** commit SHA/branch, exact XEX path and reproducible command, actual automated pass/fail results, anything unrun, gameplay changes, known limitations and what the user should test. Do not merge gameplay changes into main or delete a work branch without authorization.
- **Keep docs aligned:** when actual behavior changes, revise the authoritative stage spec, whole-game/technical/art docs if affected, TODO and regression plan. Move obsolete handoffs into history rather than leaving them as active instructions.

## Current milestone discipline

Stage 1 v0.5 is **functionally complete for prototype purposes**, not a final production-ready stage. Its fine-tuning remains in [deferred work](docs/STAGE1_DEFERRED_WORK.md). Stage 2 original v0.1 was user-playtested; its separately versioned **v0.1-r2 speed-linked vertical-car refinement is implemented and CPU tested, with Atari800/user acceptance pending**. Preserve `assets/stage2_v01/` and its tools; use `assets/stage2_v01_r2/README.md` for the current build, tuning, memory map and outstanding playtest checks. Develop it on the existing `feature/stage2-driving-v0.1` branch, using [STAGE2_DESIGN.md](docs/STAGE2_DESIGN.md) as the v0.1 requirements source. Do not change Stage 1 as an incidental effect; do not merge, tag or delete the Stage 2 branch before review and user authorization.
