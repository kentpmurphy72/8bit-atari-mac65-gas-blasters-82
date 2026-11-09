# v0.2 validation — 2026-11-09

**PASS: 20 v0.2 native 6502 tests + 85 prior CPU tests + five validators.**
These are offline py65/static checks. **Atari800: NOT RUN. Hardware: NOT RUN.**
User gameplay acceptance is pending; no merge or tag is authorized.

XEX: `GasBlasters82_Stage2_Pressure_Destination_v02.xex` (25,873 bytes), entry $2000.
SHA-256: `edfba7efd15fee327991b7a44e21cfa6e6bef29ff1d9330500307e106966b057`.
Native extension: 1691 bytes at $7000–$769A;
r3 driver/state: 934 bytes. New state: $2900–$292A.
All XEX code/data ends at $9FFF, below BASIC; RUNAD is the only load below $2000.
No overlapping segments; private ZP $80–$84/$86–$89. Runtime write audit passes.
Manifest includes every segment, label, patch and checksum.

## Actual commands/results

Run with Python 3 and pinned `py65==1.2.0` installed in your virtual environment.
The build itself needs only stdlib; the tests build temporary artifacts and do
not regenerate accepted versions in place.

| Command (`python3 tools/…`) | Result |
| --- | --- |
| `build_stage2_v02.py` | PASS, reproducible XEX/manifest/listings |
| `test_stage2_v02.py` | 20 PASS; full log in `cpu_tests.log` |
| `test_stage2_v01.py` | 12 PASS |
| `test_stage2_v01_r2.py` | 19 PASS |
| `test_stage2_v01_r3.py` | 21 PASS |
| `test_stage1_v04.py` | 15 PASS |
| `test_stage1_v05.py` | 18 PASS |
| `validate_taco_smell_stage1.py` | PASS |
| `validate_taco_smell_stage1_v02.py` | PASS |
| `validate_stage1_pressure_v03.py` | PASS |
| `validate_stage1_blast_v05.py` | PASS |
| `validate_opening_sequence.py` | PASS, CPU transitions/music-register checks |
| `validate_stage2_v02_preservation.py` | PASS, all 158 accepted asset/tool blobs unchanged |
| `profile_stage2_v02.py` | PASS, measured native cycle budget |
| `git diff --check` | PASS |

Preservation compares all tracked `assets/` and `tools/` files present in accepted
commit `e0e442295eaccfa5484aaa3a751bb926243e2e99`; see `preservation.json` for
individual SHA-256 values. This includes the original opening, every earlier
Stage 1 artifact, and Stage 2 v0.1/r2/r3 source, manifests, XEXs and tests.

## All seven required categories

1. **NTSC/PAL timing:** Full emitted-code runs at 60/50 injected ticks/second
   reach 100% exactly on tick 9900/8250 (165 s). Warning 75% begins at
   123.75 s NTSC / 123.76 s PAL (first available tick), 90% at 148.5 s both.
   Gas is linear, independent of speed; outcome counters freeze. Duplicate ticks,
   RTC low-byte wrap and missed deltas up to 255 are tested.
2. **Mapping/distance:** Every native table entry including clamps is tested.
   Random changing-speed fractional integration matches exact quarter-MPH sums.
   60 MPH arrives on tick 7200/6000 (120 s) with no early 0.00 MI. Native long
   division has randomized arithmetic tests; GAS never displays 100 early;
   distance saturates at zero and ceil hundredths remain positive until arrival.
3. **States/lives:** Exact warning/deadline boundaries, success freeze, gas-first
   same-tick tie, latched success, three green explosion phases, deduction after
   animation, 3→2→1→0, conditional failure/game-over messages and replay resets.
4. **Inputs:** Joystick/diagonal behavior, inert driving FIRE, START ignored,
   fresh-release FIRE on all result states, no held-FIRE skipping. A 2,000-frame
   native differential r3 run matches speed, X/Y, phase/bank and PMG bytes.
5. **HUD/fonts:** Initial values, icon count, rounding, gas-only flashes,
   27/13 boundaries, long road-bank integrity, render-only clamped shake,
   pharmacy building/sign and PMG hide/restore transitions.
6. **Memory/performance:** Deterministic hash, ordered non-overlapping load
   segments/entry, writes confined to declared RAM/registers, preserved static
   data, and measured normal/warning/explosion/arrival/retry CPU scenarios.
7. **Regressions/preservation:** All prior-version suites/validators above pass;
   158 historical files match accepted Git blobs byte for byte.

## CPU performance and material limits

`profile.json` contains all scenarios. The adversarial sweep covers **1,764**
combinations of legal speed, pressure boundary, simultaneous HUD updates and
joystick input. Peak one-tick driving cost: **10,448 cycles**.
The separate 255-missed-PAL-tick critical-warning case costs
**12,313 cycles**, including exact flash-phase catch-up.
Both stay below the 15,000-cycle harness ceiling. Explosion entry:
13,500; explosion/failure transition:
20,292; pharmacy arrival:
24,854; retry/new-game peak:
44,292 cycles.
These are sampled/adversarial **CPU-only** costs, excluding ANTIC DMA and OS
interrupts, not a hardware worst-case proof or actual frame-rate measurement.
Full-screen blits/retries may span frames; inspect visible transition stutter.

Low-byte clock accounting assumes fewer than 256 ticks between observed updates;
nominal 60/50 Hz is used. Faster finishes at higher speed are intended; tuning
of 120/165-second balance and warning strength is provisional. Original temporary
art and silent audio are deliberate. No hazards, Stage 3 or Stage 1 integration.

## Emulator evidence and pending acceptance

**Atari800 NTSC: NOT RUN. Atari800 PAL: NOT RUN. Physical 800XL: NOT RUN.**
No emulator executable was installed. A source checkout was investigated, but
local autotools/SDL development tooling and configured package candidates were
unavailable. Static glyph-memory images were inspected for layout; these are
**not emulator screenshots or proof of ANTIC/GTIA raster behavior**. CPU tests
cannot verify physical input mapping, flicker, tearing, stutter, palette, actual
NTSC/PAL elapsed time or gameplay feel. No audio or joystick emulator test is
claimed. Use the commands and six-step Atari800 checklist in [README](README.md)
and report gameplay acceptance before any merge/tag/branch deletion.
