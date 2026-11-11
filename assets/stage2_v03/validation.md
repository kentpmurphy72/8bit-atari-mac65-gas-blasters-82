# Stage 2 v0.3 geometry — validation (2026-11-11)

**PASS: 33 v0.3 tests + 112 historical regression tests + five validators.**
**Atari800 NTSC/PAL: NOT RUN. Physical 800XL: NOT RUN. User acceptance pending.**

Artifact: `GasBlasters82_Stage2_Road_Geometry_v03.xex`, 25,879 bytes.
SHA-256: `e6c222eb15fa19cf991c0076ebff2d13cae74d0fb0af933f8b66023179e23178`.
Entry $2000 via RUNAD. All segment boundaries and sizes match accepted r1;
maximum loaded address is $9FFF. No added code, state, RAM, ZP, interrupt or
hardware-register usage. Both native code segments are byte-identical to r1.

## Commands executed and results

Use Python 3 in a venv with `tools/requirements-stage1-test.txt` installed.
Builder itself requires standard library only.

| Command (`python3 tools/…`) | Result |
| --- | --- |
| `build_stage2_v03.py` | PASS, reproducible XEX/listings/preview/manifest |
| `test_stage2_v03.py` | 33 PASS (`cpu_tests.log`) |
| `test_stage2_v02_r1.py` | 27 PASS |
| `test_stage2_v01_r3.py` | 21 PASS |
| `test_stage2_v01_r2.py` | 19 PASS |
| `test_stage2_v01.py` | 12 PASS |
| `test_stage1_v04.py` | 15 PASS |
| `test_stage1_v05.py` | 18 PASS |
| `validate_taco_smell_stage1.py` | PASS |
| `validate_taco_smell_stage1_v02.py` | PASS |
| `validate_stage1_pressure_v03.py` | PASS |
| `validate_stage1_blast_v05.py` | PASS |
| `validate_opening_sequence.py` | PASS (CPU transitions/POKEY register checks) |
| `profile_stage2_v03.py` | PASS, no additional native work |
| `git diff --check` | PASS |

See `validation.json` for exact regression command results and timings. Individual
historical suite logs and the full v0.3 log accompany the XEX. `preservation.json`
checks all **186** pre-existing asset/tool Git blobs against branch starting commit
`3720777bc44e8dbe6a0477bdc8dcdc67574bf708`. Original v0.2/r1, accepted Stage 1/opening and all
historical source/builders/tests/manifests/XEXs remain unchanged.

## Geometry / graphics / memory evidence

- Exact 14/7/66/7/14 bands cover all 108 pixels without gaps or overlap, with
  symmetric half-open ranges [0,14), [14,21), [21,87), [87,94), [94,108).
  Offline lookup rejects out-of-range coordinates. All 108 lookup entries match
  the canonical geometry, independent of displayed texture/centerline pixels.
- An independent absolute-pixel oracle decodes all **110,592** combinations of
  32 phases × 32 source rows × 108 pixels. Grass/shoulder texture and pavement/
  centerline pixels match the new boundaries, including partial characters.
- The unchanged native CPU font-copy/publication path is executed for every
  phase and both character banks; screen glyphs and restart template use the
  same new categories. Exactly eight categories/32 glyphs fit existing memory.
- Only $2400/$9400 road screen columns, first 256 bytes of $3000/$3400/$6000
  fonts, and $4000 road pages differ. HUD cells/static glyph bytes, PMG bytes,
  palettes, all scene data, speed/time/distance tables, native code and display
  lists are identical. XEX hash/rebuild, load overlap and entry checks pass.
- Inherited tests audit native runtime writes and PMG/screen/font isolation.
  The r1 visibility tests retain the GTIA register-read-alias model at
  74%, 75%, 90%, 99%, shaking/flashing, road edges, and speed-linked Y anchors.

## Gameplay / timing regression evidence

The suite inherits **all 27 r1 test cases**, adapting its version-specific
artifact comparisons and profiler to the geometry-only XEX, then adds **six**
geometry/differential cases. It verifies full nominal NTSC/PAL 120-second
60-MPH arrival and 165-second gas deadlines, fractional speed/distance,
75%/90% warnings, GAS-first ties, 3→2→1→0 lives, freeze/outcomes, fresh/held FIRE,
disabled START and pharmacy/COMPLETE/new-game flow. Native controls are also
compared with accepted r3 for 2,000 frames.

The new direct r1 differential runs in both nominal clock standards through
random/diagonal driving, pressure warnings, gas failure/freeze/retry, arrival,
completion and new game. State, logical X/Y/speed, phase/bank, HUD, PMG and
hardware write-latch values agree. Grass/shoulder/pavement driving for over
three seconds introduces no traction change, grass timer or off-road life loss.
No runtime zone classification, crash, winding road, fork or enemy is activated.

## CPU performance and emulator limits

Native executable bytes and all copy addresses are unchanged. The 1,764-case
one-tick sweep peaks at **10,451 CPU cycles**;
255-missed-PAL-tick critical case is **12,317 cycles**,
below the existing 15,000-cycle harness ceiling. Complete scenario data is in
`profile.json`. These measurements exclude ANTIC DMA and OS interrupts; they
are not actual raster/frame-rate proof. Existing low-byte RTC and nominal
60/50-Hz clock assumptions and multi-frame scene/retry redraws are unchanged.

`command -v atari800` found no executable, so actual Atari800 NTSC/PAL, visual,
audio/input/raster/performance and physical hardware tests are **NOT RUN**.
The generated `layout_preview.png` was inspected for layout but is software
byte decoding with approximate RGB, **not an Atari800 screenshot**. User must
judge narrower-road steering space, colors, stable scrolling/HUD/PMG, no new
off-road penalties, pressure visibility, retry geometry and pharmacy flow in
Atari800. Use the four-step [playtest checklist](README.md).

No additional branch, merge, tag or branch deletion. Awaiting user acceptance.
