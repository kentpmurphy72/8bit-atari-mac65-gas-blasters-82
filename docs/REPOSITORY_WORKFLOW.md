# Repository Workflow — Git, Tags, Artifacts and Codex

**Applies to:** Gas Blasters '82 Atari 800XL 6502 project.  
**Current branch policy:** `main` is the integrated baseline. Work on one focused feature branch at a time, submit reviewed changes, then integrate. **Stage 1 v0.5 has already been merged to `main`.**

## Source of truth and ownership

- **Game design:** `docs/GAME_DESIGN.md` covers the whole game; `docs/STAGE1_DESIGN.md` is authoritative for **current Stage 1**; `docs/STAGE2_DESIGN.md` is authoritative for **accepted Stage 2 v0.1 driving and upcoming v0.2 pressure/destination design**; `docs/TECHNICAL_DESIGN.md` covers implementation; `docs/ART_ASSETS.md` covers final art plans; machine JSON and the actual executable define concrete version-specific values.
- **ChatGPT/design work:** Specify requirements, update authoritative docs, list open decisions, and give a clear acceptance checklist. When asked, make documentation-only GitHub commits.
- **Codex/implementation:** Branch, implement native 6502 code and reproducible Python offline tooling, build a distinct playable XEX, test, provide exact commit/commands/results; **never claim an Atari800/real-hardware test without running it**.
- **User:** Evaluate actual game feel in Atari800 and decide acceptance. Do not assume acceptance of provisional numbers implies final art or exhaustive test coverage.

## Branch and merge convention

| Item | Example | Rule |
| --- | --- | --- |
| Default | `main` | Integrated, working baseline; don't experiment directly on it |
| Feature | `feature/stage2-driving-v0.1` | One clear milestone; branch from current `main` unless a deliberate earlier baseline is specified |
| Small fix | `fix/stage1-cloud-cleanup` | Focused bug fix based on main; document test result |
| Prototype tag | `stage1-v0.5` | Immutable reference to the **exact reviewed final prototype commit** |
| Artifact | `assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex` | New versioned folder/file for a milestone; do not overwrite historical XEXs |
| Build/test | `tools/build_stage1_v05.py`, `tools/test_stage1_v05.py` | Reproducible offline implementation and regression harness |

Before integrating: review the diff, preserve title/music/memory baselines, run validators + CPU tests, record actual emulator coverage and get user acceptance for gameplay changes. Merge/fast-forward into `main` without squashing away milestone history when tags depend on ancestry. Create the immutable tag at the **specific final prototype commit** (usually the feature branch tip), push and verify it resolves to the expected commit, then delete the merged feature branch. Do **not** retarget a published tag.

Historical Stage 1 tags (already created and verified):

| Tag | SHA | Outcome |
| --- | --- | --- |
| `stage1-v0.1` | `6e9ab07d57823464255e376e27af91847ef2c039` | Initial prototype |
| `stage1-v0.2` | `86c5e392388bb9688cde50d9ff5d9af92f8b47ce` | Fixed rooms |
| `stage1-v0.3` | `09e3d12308019826faabff7c12a6be461cb0dab7` | Hazmat pressure |
| `stage1-v0.4` | `f8b4926c81d4c6f7397883bafe3fed62e3c4a6c1` | Responsive movement |
| `stage1-v0.5` | `ea9a2f9745d590e46a3b89803fa7f7830788088a` | Eight-way blast baseline |

The tags and full history survive the deletion of the five old feature branches. Historical numbered designs and Codex handoffs reside in [Stage 1 Archive](archive/stage1/README.md); versioned code and XEX artifacts stay in `assets/` and `tools/`, not moved into the docs archive.

## Stage 2 v0.1 → v0.2 milestone boundary (verified 2026-11-08)

- **Accepted baseline:** Stage 2 v0.1-r3 driving feel was user-playtested in Atari800 and approved on 2026-11-04. This accepts the standalone driver, **not** a full pressure/destination chase, exhaustive regression, PAL or physical hardware test.
- **Git refs verified:** immutable tag `stage2-v0.1` and branch `main` both resolve to **`e0e442295eaccfa5484aaa3a751bb926243e2e99`**. The feature branch `feature/stage2-pressure-destination-v0.2` was created from that baseline and carries the v0.2 design updates. Do not repeat a completed tag/merge/branch-creation instruction.
- **Current v0.2 status:** the approved [Stage 2 design §§16–21](STAGE2_DESIGN.md) was implemented as a standalone v0.2 XEX and corrected in **v0.2-r1** after a user-discovered 75%-gas car visibility bug. **The user tested corrected r1 in Atari800 and accepted it on 2026-11-08.** Preserve original v0.2, r1, all older driving and Stage 1 XEX/source/manifest assets. User playtest mode was not specified; do not assert PAL or physical-hardware verification.
- **v0.2 closeout verified:** `stage2-v0.2` preserved at `8e46ef91246bd913d99d1156b081bc59c4ac2eda`; its feature branch was deleted. **v0.3 geometry-only implementation is now user-playtested and accepted (2026-11-11)**. User explicitly authorized a final acceptance-documentation commit, immutable `stage2-v0.3` tag, fast-forward integration into `main`, and feature-branch retirement **after actual remote ref verification**. This approval is not proof that the tag or branch deletion already occurred.

## Changes that cross stages

- Preserve or explicitly update approved opening, stage controls, camera regions, POKEY music, ANTIC/DLI setup and the **Atari 64 KB memory map**.
- Keep four-direction **car** blasting distinct from eight-direction **on-foot** blasting.
- When common code changes, rerun the [Stage 1 regression checklist](STAGE1_REGRESSION_CHECKLIST.md). Change `GAME_DESIGN.md`, per-stage docs, and TODO only where actual behavior/decisions change. **Do not stamp a feature as tested before user/emulator verification**.
- Keep temporary build outputs out of Git unless they are named deliverables with manifests; generated .xex artifacts for approved/versioned prototypes are intentional repository assets.
- Before creating a new branch, inspect `git branch -r` and `git tag -l` to avoid duplicate names. Do not create a Stage 2 branch as a side effect of documentation cleanup.

## Version terminology

**Designed** = documented, not executable. **Implemented** = native XEX built. **CPU tested** = offline 6502 harness passed. **User playtested** = tested gameplay feel in Atari800 by user. **Regression verified** = relevant end-to-end manual test checklist passed with evidence. **Hardware verified** = physical 800XL run. **Prototype accepted** does not imply production-ready.

See [project README](../README.md) and [Codex rules](../AGENTS.md).
