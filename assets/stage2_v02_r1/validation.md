# v0.2-r1 visibility fix — validation results

**PASS: 27 v0.2-r1 tests (20 inherited + seven new) and 21 accepted r3 tests.**
**Atari800: NOT RUN. Physical Atari: NOT RUN. Gameplay acceptance pending.**

XEX: `GasBlasters82_Stage2_Pressure_Destination_v02_r1.xex` (25,879 bytes).
SHA-256: `316ad4e7a1a5a495b23c4929b59a673c7acef0957699415f27b97840fb4f9a31`.
RUNAD remains $2000. Native extension: 1697 bytes,
$7000–$76A0. No new state/ZP/load allocations.
All segments end below $A000. Existing overlapping-free load layout is retained.

## Root cause and regression evidence

The warning shake routine treated `$D000` as readable HPOSP0. On Atari GTIA,
reads there return M0PF missile collision flags. With the usual zero collision
value, subtracting one yielded 255; adding one yielded 1. Both positions put the
car outside its visible road pane. PMG bytes/colors/enables remained correct.

The new CPU-bus shim reproduces that exact defect in the historical v0.2 XEX.
It proves this is a horizontal-position read/write-alias bug. r1 derives the
unshaken origin from RAM `PIX_LO + 48` and applies the unchanged shake/clamp.
The earlier flat-memory py65 harness wrongly provided position readback and
therefore missed the hardware bug. The new shim models the relevant CPU bus
semantics; it does **not** emulate ANTIC/GTIA raster rendering or OS execution.

New visibility regressions execute emitted 6502 and check:

- 74%, 75%, 90%, 99% in both nominal NTSC/PAL clocks, 180 updates per point,
  both shake directions and GAS flash phases. Car remains visible when GAS is
  blank; other labels remain fixed.
- Both PMG planes match the original 16-row car templates at the correct Y,
  with no stale rows. DMACTL $3A, GRACTL 2, PMBASE $38, normal sizes and red/white
  color writes remain intact. Player positions align inside 48–148 and stay out
  of the HUD. Registers are inspected as **write latches**, not fictional CPU
  readback of write-only addresses.
- A 5,760-tick sweep covers all 16 collision-flag values, threshold transitions,
  left/center/right X, minimum/default/maximum speed, and smooth Y relocations.
  Fixed code performs zero CPU reads of the GTIA position/collision aliases.
- The historical v0.2 XEX exhibits the reported off-screen positioning with
  collision reads returning zero; the fixed XEX does not.
- Every XEX segment except $7000 is unchanged, including the entire accepted
  driver/hook segment, all PMG/font/scene data and speed/time/distance tables.
  Native controller grows only six bytes. All 172 prior asset/tool blobs match
  pre-fix commit `e2a615cb6653b7d7b30a0f430706957066f3f35f`.

## Commands actually run

Use the pinned py65 requirements in a virtual environment. Builder is stdlib-only.

| Command (`python3 tools/…`) | Result |
| --- | --- |
| `build_stage2_v02_r1.py` | PASS, deterministic native XEX/listings/manifest |
| `test_stage2_v02_r1.py` | 27 PASS; `cpu_tests.log` |
| `test_stage2_v01_r3.py` | 21 PASS; `r3_regression.log` |
| `profile_stage2_v02_r1.py` | PASS, `profile.json` |
| `git diff --check` | PASS |

The inherited v0.2 cases also verify exact full-duration NTSC/PAL 120-second
arrival and 165-second deadline, warning boundaries, fractional integration,
FIRE/START, life/retry and success latching, memory/write confinement, HUD/font
integrity, a 2,000-frame r3 differential drive and reproducibility. Accepted r3
regression tests run against its immutable original builder/XEX, unchanged.
The all-noncontroller-segments-equal assertion also passes. No gameplay
balancing or pressure behavior change is introduced.

## CPU profile and emulator limits

The 1,764-case one-tick driving sweep peaks at
**10,451 cycles**. The 255-missed-PAL-tick critical-warning
case costs **12,317 cycles**. Both remain below the existing
15,000-cycle CPU test ceiling. Samples exclude ANTIC DMA and OS interrupts;
these are CPU costs, not proof of actual Atari frame rate or raster stability.
Whole-screen transitions still may span frames, as in original v0.2.

No Atari800 executable is installed (`command -v atari800` found none).
Actual NTSC/PAL visual, input, flicker, colors and handling tests are **NOT RUN**;
physical hardware is also untested. Use the launch command and three-step manual
checklist in [README](README.md), especially 74→75%, 90% and 99% while GAS blinks,
edge steering/Y movement, explosion and FIRE retry. No merge or tag; user
acceptance is still required.
