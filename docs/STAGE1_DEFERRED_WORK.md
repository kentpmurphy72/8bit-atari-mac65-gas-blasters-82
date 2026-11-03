# Stage 1 — Known Limitations, Validation Gaps and Deferred Improvements

**Status:** Stage 1 **v0.5 accepted as playable prototype**; not a final polished game. This is a backlog, **not** a list of confirmed software defects. Do not silently implement these items while working on other stages.

## Known implementation / scope limitations

| Area | Current behavior | Future criterion |
| --- | --- | --- |
| Scope | Stage 1 ends at its COMPLETE screen, **no Stage 2 handoff** in the XEX | Connect future driving stage when ready |
| Art | Temporary 8×8 PMG Billy and blue-jeans aim poses; coarse horizontal hardware step | More readable character, eight-direction butt posing, better effects |
| World | Three fixed 40×22 Taco Smell screens; no scrolling here | Retain fixed-room architecture; later interiors may use scrolling as needed |
| Gameplay | No lives/scoring system, item collection, grease-slip effect or whole-game pressure mechanic | Implement only when game design calls for them |
| Pacing | Early v0.2 felt too easy/short; v0.5 pacing has **not been specifically signed off** | Playtest multiple complete escapes, tune hazmat pressure vs recovery |
| Balance | Three regenerating charges, 20-frame cooldown, 75-frame stun, fixed worker timings | Tune difficulty, shot availability and stun without losing fun |
| Performance | CPU-only profile excludes DMA/VBI and worst-case corner scenarios | Frame-time, flicker and responsiveness profiling in Atari800 and hardware |

## Unverified rather than known broken

- **Eight-way blast geometry:** manually inspect diagonal corners, visibility through door gaps, sprite/cloud priority, hit-once bookkeeping, multi-worker impact, room changes while effects are active and ghost-free cleanup. Automated tests do not constitute visual signoff.
- **Input usability:** one-press FIRE-first aim, diagonal directional stability, release-to-walk recovery, cooldown feedback under busy pursuit, 120-tick refill cadence and holding FIRE with no charge.
- **Visual/sound presentation:** butt pose legibility, three cloud waves, BONK feedback, GAS footer readability and sound balance alongside title/intro music; v0.5 gas was broadly accepted, but this is **not** a detailed issue-by-issue acceptance report.
- **Platform coverage:** actual Atari800 graphics/audio/performance audit for v0.5 is incomplete in the repository; physical Atari 800XL, PAL timing, long-running resets/room loops and emulator-to-hardware comparisons are still open.
- **Build reproducibility:** rebuild deterministically, compare emitted SHA-256 to the manifest, run py65 tests and inspect binary segment layout before changes. Earlier tests reported passing but are not claimed re-run by this documentation update.

## Enhancements to consider later (prioritize based on playtesting)

1. **Blast feel:** adjust wind-up, recovery, cooldown, cloud fullness/shape, sound, gas refill and knockback impact. Keep all eight on-foot directions.
2. **Enemy challenge:** retune the three hazards, chokepoints, chase speed, follow delay and stun fairness. Avoid turning fixed rooms into a frustrating wait or an instant win.
3. **Art clarity:** enhance Billie/Billy sprite readability, blue-jeans gag, cloud palette/animation, impact symbols and hazmat identity without harming ANTIC/PMG timing.
4. **Audio:** balance short original blast noise and possible indoor music, keeping accepted Arcade Rock and Funky Gas Attack unchanged.
5. **Stage integration:** add a transition to the eventual Stage 2 road chase only when its driving engine is ready.
6. **Completion/presentation:** improve title/arrival text spacing and end-screen feedback if emulator testing justifies the change.

## How to report issues

For every observed defect: record XEX tag / SHA, emulator and region (NTSC/PAL), room, coordinates if available, joystick/FIRE sequence, expected vs actual result, repeatability and video/screenshot if useful. Distinguish **confirmed bug**, **tuning preference**, and **unverified test coverage**. Open a focused issue or new task; avoid editing old tagged prototypes.

See [current Stage 1 behavior](STAGE1_DESIGN.md), [regression gates](STAGE1_REGRESSION_CHECKLIST.md), and [repository workflow](REPOSITORY_WORKFLOW.md).
