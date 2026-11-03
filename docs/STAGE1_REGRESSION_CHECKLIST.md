# Stage 1 — Regression and Release-Gate Checklist

**Target:** `stage1-v0.5` (accepted *playable* baseline). This is a **future repeatable checklist**, not a claim that every item has already passed. Track actual tests separately. Later Stage 2 work must not silently break the shared opening or Stage 1 when integrated.

## 1. Source and build integrity (automated)

- [ ] Checkout the intended branch/tag; confirm repo is clean and **v0.1–v0.5 tagged builds remain unchanged**.
- [ ] Run `python3 tools/validate_taco_smell_stage1.py` (legacy v0.1 map).
- [ ] Run `python3 tools/validate_taco_smell_stage1_v02.py` (three fixed room maps/door links).
- [ ] Run `python3 tools/validate_stage1_pressure_v03.py` (hazmat encounter rules).
- [ ] Run `python3 tools/validate_stage1_blast_v05.py` (eight aims, geometry/corner block, blast resources).
- [ ] Run `python3 tools/build_stage1_v05.py`; compare artifact SHA-256 against `assets/stage1_v05/manifest.json`. **Do not overwrite a historical tag** to hide differences.
- [ ] Run py65 `tools/test_stage1_v04.py` and `tools/test_stage1_v05.py` using `tools/requirements-stage1-test.txt`. For a change affecting common engine or maps, also run `tools/test_stage1_v02.py` and `tools/test_stage1_v03.py`.
- [ ] Check v0.5 XEX segments, PMG/font/maps, Zero Page and OS-reserved memory against manifest. Sample maximum three-worker + cloud dispatch cycles, including worst encounter cases.
- [ ] Confirm no unintended modifications to opening `assets/opening` source, POKEY song tables, v0.4 movement and earlier XEXs.

## 2. Actual Atari800 acceptance (must be tested visually/audibly)

- [ ] Boot **stock XL, 64 KB, NTSC, BASIC disabled** and verify readable title/menu; console **START** initiates Meet the Crew.
- [ ] FIRE moves from Crew → Arrival → Stage 1, with release between presses; story captions remain correct and music transitions/loops cleanly.
- [ ] Billy moves immediately **in all eight directions**, no tile-step pauses; cardinal/diagonal speed feels right; stop, reverse and wall-slide around furniture.
- [ ] Cannot clip furniture, room edges, door jambs or footer; worker hitbox contact remains fair.
- [ ] Both y=10/11 door cells work in each direction between Dining↔Kitchen↔Storage. Preserve y/clear fraction, allow backtracking, no held-input bounce.
- [ ] Three distinct hazmat workers spawn at intended times, chase and follow without duplication; CAUGHT remains reachable without unpreventable catches.
- [ ] **Eight attack directions individually:** Up, Up-Right, Right, Down-Right, Down, Down-Left, Left and Up-Left.
- [ ] FIRE-first aim, direction-first FIRE, direction changes before wind-up, early release cancellation, stable wind-up and one shot per hold all behave as specified.
- [ ] Holding FIRE freezes Billy, not world timing; releasing FIRE resumes smooth walking after recovery, even with cloud still visible.
- [ ] Cloud grows in three visible waves, is blocked by counters/shelves/walls/doors/exit, cannot pass blocked diagonal corners, and leaves no glyph/PMG ghosts.
- [ ] Multiple workers are each hit once per burst; all **eight directional knockback vectors** respect furniture, walls, doors, other workers and diagonal side-cells; BONK/stun/stagger/grace behave.
- [ ] GAS 3/3→0/3, recharge/COOLING/EMPTY, cutoff when holding with zero supply, and recharge across room transitions; restart resets supply.
- [ ] Short gas POKEY effect is audible and stops at CAUGHT/COMPLETE/restart; intro themes remain intact.
- [ ] Reach storage `X`, observe COMPLETE; START restarts from both COMPLETE and CAUGHT. No accidentally connected Stage 2 yet.
- [ ] Repeat several complete escapes under heavy pursuit; look for flicker, frame stalls, audio dropouts, actor glitches and memory corruption.

## 3. Extended platform / future integration

- [ ] Real Atari 800XL / compatible display and joystick test (if available).
- [ ] PAL timing/input/audio/charge behavior is evaluated or explicitly excluded from a release.
- [ ] With later levels integrated, rerun the opening/Stage 1 checks after each shared-engine/music/graphics change.
- [ ] Capture findings in [deferred work](STAGE1_DEFERRED_WORK.md) with *confirmed defect vs improvement vs untested* status.

## Evidence convention

Record test date, commit/tag, emulator or physical Atari model, NTSC/PAL, command/run settings, exact result (PASS/FAIL/NOT RUN) and any screenshots. Existing repository CPU tests and the user's broad v0.5 gameplay acceptance are **different kinds of evidence**; do not substitute one for the other.
