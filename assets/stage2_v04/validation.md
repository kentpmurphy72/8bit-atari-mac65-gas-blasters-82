# Stage 2 v0.4 — actual validation results

**35 v0.4 tests, 114 historical regression tests and five validators: PASS.**
**Atari800 NTSC/PAL: NOT RUN. Physical hardware: NOT RUN. User acceptance pending.**

XEX: `GasBlasters82_Stage2_Offroad_v04.xex` (26,710 bytes).
SHA-256: `241554e62bf7be97c5ae505b599e9ababff2f34462c5ba6d13e74d9d2628a9c1`.
RUNAD $2000. Native v0.4 controller: 2387 bytes at
$7000–$7952. All load segments end below $A000.
New state $2A00–$2A10; particles/tuning $2B00–$2B77; runtime PMG P2 $3E00–$3EFF.
No new zero page, interrupt handler or graphics mode. Manifest inventories every
actual segment, native label, state byte and checked driver hook.

## Commands/results

Python 3 with pinned py65 1.2.0 from `tools/requirements-stage1-test.txt`.
Builder uses stdlib only. Complete individual logs accompany the XEX.

| Command (`python3 tools/…`) | Result |
| --- | --- |
| `build_stage2_v04.py` | PASS, reproducible native XEX/listings/manifest |
| `test_stage2_v04.py` | 35 PASS |
| `profile_stage2_v04.py` | PASS, CPU budget |
| `test_stage2_v03.py` | 33 PASS |
| `test_stage2_v02_r1.py` | 27 PASS |
| `test_stage2_v01_r3.py` | 21 PASS |
| `test_stage1_v04.py` | 15 PASS |
| `test_stage1_v05.py` | 18 PASS |
| `validate_taco_smell_stage1.py` | PASS |
| `validate_taco_smell_stage1_v02.py` | PASS |
| `validate_stage1_pressure_v03.py` | PASS |
| `validate_stage1_blast_v05.py` | PASS |
| `validate_opening_sequence.py` | PASS, CPU/POKEY-register checks only |
| `git diff --check` | PASS |

`preservation.json` verifies all **207** historical asset/tool blobs against
pre-implementation branch commit `72bea2618986bbe9226b750cd2118779b620ccbe`. Every accepted
XEX, source, test and manifest remains unchanged. v0.3 geometry, fonts, car PMG,
HUD and pharmacy/result art/tables are byte-identical in the new executable.

## Mandatory Section 28 coverage

1. **Classification and traction:** unshaken center/fractional-floor boundaries
   13/14, 20/21, 86/87, 93/94, both sides; altered GTIA positions/collision flags
   do not influence classification. All nine surface/GAS combinations execute
   actual 12/10/8 minimum steering, without modifying throttle.
2. **Grass time:** full 120-NTSC/100-PAL-tick two-second runs, exact 599 boundary
   in both standards, saturation at 600 and overflow protection, duplicate and
   missed ticks, 1.3+0.7s example across a 3s shoulder pause, left/right sharing,
   pavement reset, terminal freeze and fresh-FIRE reset.
3. **Effects/audio:** stages at 149/150, 299/300, 449/450; all particle shapes,
   bounded combined shake and car visibility at pressure boundaries/speed/Y
   anchors/edges. Erase-before-relocation clears old P2 rows; smoke never enters
   HUD/footer. Brief channel-1 pulses, critical escalation, shoulder scheduling
   pause, pavement/result/retry silence and untouched other channels are checked
   as actual POKEY register writes, not an audio audition.
4. **Outcomes:** complete three-event matrix covers every pairwise/three-way tie,
   GAS→grass→arrival priority and latch; orange/red vs green animation, frozen
   clocks/miles/scroll, one-life loss at animation end, 3→2→1→0, fresh/held FIRE,
   disabled START and pharmacy two-distinct-press new-game flow.
5. **Regression/memory/performance:** applicable existing GAS/MI/MPH tests run on
   v0.4 including full nominal NTSC/PAL 120-second arrival and 165-second GAS
   deadlines, fractional arithmetic and HUD rounding. Direct native pavement
   driving comparisons with v0.3 preserve controls/Y/scroll. All historical suites
   above pass independently; native runtime write auditing confines memory and
   I/O to declared allocations/registers. XEX entry/segments/rebuild/hash pass.

The v0.4 suite reuses 14 applicable baseline gameplay cases and adds 21 off-road,
rendering/memory and integration cases. Historical assertions that deliberately
expect no grass penalty run on their original geometry-only XEX, not incorrectly
on the v0.4 executable whose approved behavior now differs.

## Performance and unrun checks

The **7,056-case** speed/pressure/surface/stage/joystick sweep peaks at
**11,806 CPU cycles** per active update. A 255-missed-PAL-tick
paved critical-pressure catch-up costs **12,791**. Both are below the
15,000-cycle CPU harness ceiling. All representative scenarios are in
`profile.json`. GAS/crash entry costs are
13,963/13,205; result transitions peak at
20,300; retries at
44,423 cycles. Full-screen redraws may span frames, as before.
These are **py65-only** measurements, excluding ANTIC DMA/OS interrupts, not
physical worst-case frame-rate guarantees. Nominal 60/50-Hz and low-byte clock
sampling limitations remain unchanged.

`command -v atari800` found no installed emulator. Actual NTSC/PAL raster,
colors, sound timbre/volume, control mapping and gameplay feel are **NOT RUN**;
physical hardware is untested. PMG/POKEY memory checks are not video/audio
emulation. Exact particle/shake/sound tuning remains provisional. The brief
[manual checklist](README.md) covers both grass sides, shoulder pause, pavement
reset, pressure steering, failure colors/lives/FIRE and pharmacy flow.

No merge, tag or branch deletion; awaiting explicit user gameplay acceptance.
