## IMPORTANT CORRECTION (v2.1)

**Do not use the earlier `GasBlasters82_TitleV2_PMG_OpeningSequence.xex` from v2.** Its authoring code set DMACTL to `$2E`, which enables **double-line** PM graphics while storing PM data in the **single-line** layout ($A300 for missiles, $A400-$A7FF for players). This makes ANTIC fetch the wrong graphics bytes and produces stray pixels in the title caption/black area. The old validation test erroneously expected `$2E` too.

**v2.1 uses DMACTL `$3E`**, sets PM data origin to 56 scanlines (32 outside visible PM region + 24 title blank scanlines), and checks both settings in the 6502 simulator. This corrects the mode/layout mismatch but does **not** guarantee aesthetically good highlights or correct real-emulator timing: the first user Atari800 screenshot is needed. The original v1 introduction remains unchanged.

# Gas Blasters ’82 — Title Screen v2.1 (PMG bug fix)

**Status:** Corrected alternate PMG XEX for Atari 800XL 64 KB. **Still awaits a visual test in Atari800.** The 6502 instruction-level simulator, XEX layout, PM DMA setup, scene transition and 11 DLI-band tests pass. The original v1 XEX remains untouched.

## What changed

Only the **title artwork's apparent level of detail**: four one-line-resolution GTIA/ANTIC player sprites and four missiles add approximately 220 finely placed visible color-clock highlights. Highlights cover portions of the existing **logo, Billy, car, and Taco Smell sign**. Players are repositioned and recolored using the existing 16-raster-line DLI cadence. The PMG video buffer is **2,048 bytes at `$A000`** (single-line DMA). The title's existing 160×160 ANTIC E bitmap, all original palette tables, title text, music tables, and cutscenes are **byte-for-byte unchanged**.

**This is intentionally a subtle highlight pass, not an 80s-console resolution upgrade.** The original pixels and overall composition are preserved. The before/after PNG is a design approximation of the pixel overlay, **not an Atari800 screenshot**. We have not yet established whether remaining PMG alignment or OS color timing needs adjustment on the real emulator.

## Which XEX to run

`GasBlasters82_TitleV2_1_PMG_OpeningSequence.xex` is a **separate alternative full-opening build** that starts with Title v2; everything after the title is identical to the approved v1 sequence:

1. Title: **Arcade Rock**; console **START** →
2. Meet the Crew: **Funky Gas Attack**; joystick **FIRE** →
3. Arriving at Taco Smell: same continuous Funky Gas Attack; joystick **FIRE** →
4. Temporary Stage 1: music off; **START** restarts the sequence.

On WSL, after extracting the archive:

```bash
atari800 -xl -nobasic -run ./GasBlasters82_TitleV2_PMG_OpeningSequence.xex
```

The `-nobasic` option is important here: PMG occupies RAM at `$A000-$A7FF` normally hidden under the Atari BASIC ROM when BASIC is enabled. The program disables PMG DMA when it leaves the title, ensuring the other graphics remain unchanged.

## Rebuild from GitHub

From the repository root (Python 3, Pillow installed):

```bash
python3 tools/build_title_v2_pmg.py
python3 tools/validate_title_v2_pmg.py
```

The script relies on the **existing** tracked v1 builder and native XEX/music data:

- `tools/build_opening_sequence.py` (reproduces the original v1 XEX, SHA-256 `08971fa2...`)
- `assets/title/Title_Option3_Original.xex`
- `assets/intro/meet_the_crew_v4.xex`
- `assets/arrival/arrival_v3.xex`
- `assets/music/rock_pokey_registers.bin` and `funk_pokey_registers.bin`
- `assets/title_v2/title_original_160x160_preview.png` for the *illustrative* comparison preview

The builder generates the complete XEX, the exact 2 KB PMG memory image, positions/colors, source reference listing, overlay definition, a manifest, and v1/v2 comparison image. Rebuild reproducibility is SHA-256 checked and all original visual/sound segments besides the hooked code remain identical to v1.

## Technical details and caveats

- PMBASE `$A000`; single-line player DMA via `DMACTL/SDMCTL=$3E` (four players and four missiles); PMG enabled with `GRACTL=$03`.
- Four player graphics blocks at `$A400-$A7FF`; 4×2-bit missile buffer at `$A300-$A3FF`; normal 8-color-clock player widths.
- Player horizontal positions/colors get changed at the title's preexisting DLIs; no extra DLI is required. First three scanlines of each 16-line band contain no sprite pixels to avoid DMA/position settling artifacts. The last text-area DLI resets positions for the first art band on the next frame.
- The title PMG RAM-to-visible-bitmap vertical origin is calculated as scanline `56` (32 initially offscreen PM rows plus 24 blank title display-list scanlines). Rebuild with `--pmg-y-offset N` if an emulator screenshot reveals vertical misalignment.
- Other scenes disable GRACTL and restore the original playfield DMA. POKEY 4-channel playback and title/cutscene input logic are unchanged.
- The 6502 hook logic is a generated extension. The `.asm` file is a readable reference listing; the Python byte emitter produces authoritative bytes. This is **not** a claim that the new features were independently assembled in MAC/65 or verified on physical Atari hardware.

## Validation required from user

In Atari800 5.2.0, check that title glints align with logo/headlights/Billy/sign; confirm that the title doesn't flicker, sprites don't appear on other cutscenes, Arcade Rock still plays, and START→FIRE→FIRE works. A screenshot will let us adjust any PMG timing/placement issues in a v2.1 pass without disturbing v1.
