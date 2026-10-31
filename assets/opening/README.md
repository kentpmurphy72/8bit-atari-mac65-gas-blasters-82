# Gas Blasters '82 — continuous opening sequence v1

**Status:** Native Atari 800XL standalone proof of concept. Binary/CPU-flow/DLI/music register tests pass, but **the combined XEX has not yet been tested by the user in the Atari800 emulator or on physical hardware**.

## Game flow

| Screen | Music | Advance |
|---|---|---|
| Title screen (Option 3) | Arcade Rock, 148 BPM, looping | Console **START** (PC/WSL Atari800 default: F4) |
| Meet the Crew | Funky Gas Attack, 110 BPM, looping | Joystick 1 **FIRE** (see Atari800 joystick mapping) |
| Arriving at Taco Smell | Funky Gas Attack **continues without restarting** | Joystick 1 **FIRE** |
| Stage 1 — Taco Smell / Restaurant Escape | Music off; temporary 40-column placeholder | Console **START** to replay intro |

Controls are **release-armed**: after changing screens, release and press again to advance; holding the button doesn't automatically skip scenes. The main game is not implemented. The placeholder is an intentionally static screen, not playable.

## Load under WSL with Atari800

```bash
atari800 -xl -nobasic -run ./GasBlasters82_OpeningSequence_v1.xex
```

The visual art, captions, and underlying POKEY register songs come directly from the previously committed screen and music demos. The actual .XEX is an Atari DOS-compatible segmented executable with load/run address ($02E0 = $2000).

## Rebuild from repository

Python 3 standard library only (no assembler package required). From repository root:

```bash
python3 tools/build_opening_sequence.py
python3 tools/validate_opening_sequence.py
```

Input assets are the previously committed `assets/title/Title_Option3_Original.xex`, `assets/intro/meet_the_crew_v4.xex`, `assets/arrival/arrival_v3.xex`, and `assets/music/{rock,funk}_pokey_registers.bin`. Both Python files are **offline development utilities**, not Atari runtime dependencies. The generated `generated_6502.asm` is a reference listing of the exact byte emitter, not an independently MAC/65-assembled source. The Python builder is the authoritative, reproducible source for the integrated binary.

The graphics remain identical to the approved standalone XEX files; each picture stays in its own RAM range below `$A000`, and display-list pointers are switched without copying graphics during runtime. DLI palettes and custom character set are reused. The POKEY driver uses four audio channels and NTSC RTCLOK timing, with music tables stored channel-major after converting the previous step-major register stream.

## Validation / limits

Automated checks: 22 XEX segments, no overlapping RAM regions, original bitmap identity, relocated ANTIC display-list pointers, GTIA color table/DLI updates, 6502 instruction-level simulated START/FIRE transitions and debouncing, song tempo switch, continuity across cutscenes, music muting on Stage 1 and START replay.

**Next:** Listen and view the combined XEX in the actual Atari800 5.2.0 emulator. Check both transitions for correct visuals/palette colors and music, especially on a real Atari 800XL keyboard/joystick mapping. This proof of concept does **not** claim a fully playable restaurant stage or complete hardware testing.
