# Gas Blasters '82 — continuous opening sequence v1

**Status (updated 2026-11-03):** Native Atari 800XL standalone opening proof of concept with passing binary/CPU-flow/DLI/music checks. **The user subsequently ran the continuous opening XEX in Atari800 on 2026-10-30 and said it worked great.** The original XEX still ends in a **static Stage 1 placeholder**; the newer **Stage 1 v0.5** executable includes the same approved opening followed by playable restaurant escape. Full regression and physical-hardware verification remain open.

## Game flow

| Screen | Music | Advance |
|---|---|---|
| Title screen (Option 3) | Arcade Rock, 148 BPM, looping | Console **START** (PC/WSL Atari800 default: F4) |
| Meet the Crew | Funky Gas Attack, 110 BPM, looping | Joystick 1 **FIRE** (see Atari800 joystick mapping) |
| Arriving at Taco Smell | Funky Gas Attack **continues without restarting** | Joystick 1 **FIRE** |
| Stage 1 — Taco Smell / Restaurant Escape | Music off; temporary 40-column placeholder | Console **START** to replay intro |

Controls are **release-armed**: after changing screens, release and press again to advance; holding the button doesn't automatically skip scenes. **For this historical v1 XEX only**, Stage 1 is a nonplayable placeholder. The **current Stage 1 v0.5 XEX** includes playable three-room gameplay after these cutscenes; future stages and the complete game are not yet implemented.

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

**Test status:** A successful user Atari800 playtest of the opening sequence is already recorded. A detailed visual/audio regression, real Atari 800XL check and later-stage integration are still open. This original v1 proof of concept does **not** itself contain the playable restaurant stage; use [current Stage 1 design](../../docs/STAGE1_DESIGN.md) for that.
