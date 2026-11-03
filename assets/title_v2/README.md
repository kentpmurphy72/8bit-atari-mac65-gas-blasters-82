## EMULATOR TEST RESULT — V2.1 REJECTED (2026-11-01)

The user tested `GasBlasters82_TitleV2_1_PMG_OpeningSequence.xex` in Atari800 and supplied a screenshot. The DMA-memory-layout corruption from v2 is improved, but **v2.1 is not a successful visual enhancement**: disconnected high-contrast glints appear across logo, face and car, making the title worse than v1. The P/M art source deliberately generates approximately **220 independent overlay pixels** from `STROKES` and `MISSILE_ROWS`; these do not increase the underlying ANTIC bitmap detail. In addition, the title DLI extension performs 12 indexed table-load + color/position store pairs per 16-line band (four playfield colors, four player X positions, four player colors), which exceeds a single ANTIC E scanline's available CPU time, introducing raster-timing risk. **Neither PMG v2 nor v2.1 should be adopted.** The proven-good title is `assets/opening/GasBlasters82_OpeningSequence_v1.xex`. Keep these PMG builds only as experiments for future reference. A future title revision should prioritize deliberate ANTIC E artwork/palette refinements, with PMG reserved for coherent shapes rather than scattered highlights.

## IMPORTANT CORRECTION (v2.1)

**Do not use the earlier `GasBlasters82_TitleV2_PMG_OpeningSequence.xex` from v2.** Its authoring code set DMACTL to `$2E`, which enables **double-line** PM graphics while storing PM data in the **single-line** layout ($A300 for missiles, $A400-$A7FF for players). This makes ANTIC fetch the wrong graphics bytes and produces stray pixels in the title caption/black area. The old validation test erroneously expected `$2E` too.

**v2.1 uses DMACTL `$3E`**, sets PM data origin to 56 scanlines (32 outside visible PM region + 24 title blank scanlines), and checks both settings in the 6502 simulator. This corrects the mode/layout mismatch but **the user subsequently tested v2.1 in Atari800 and rejected the result**; further screenshots are not a prerequisite to the rejection decision. The original v1 introduction remains unchanged.

# Gas Blasters ’82 — Title Screen v2.1 (PMG bug fix)

**Status:** Retired experimental PMG v2.1 XEX for Atari 800XL 64 KB. **Tested in Atari800 and rejected visually.** The 6502 instruction-level simulator, XEX layout, PM DMA setup, scene transition and 11 DLI-band tests pass. The original v1 XEX remains untouched.

## What changed

Only the **title artwork's apparent level of detail**: four one-line-resolution GTIA/ANTIC player sprites and four missiles add approximately 220 finely placed visible color-clock highlights. Highlights cover portions of the existing **logo, Billy, car, and Taco Smell sign**. Players are repositioned and recolored using the existing 16-raster-line DLI cadence. The PMG video buffer is **2,048 bytes at `$A000`** (single-line DMA). The title's existing 160×160 ANTIC E bitmap, all original palette tables, title text, music tables, and cutscenes are **byte-for-byte unchanged**.

**This is intentionally a subtle highlight pass, not an 80s-console resolution upgrade.** The original pixels and overall composition are preserved. The before/after PNG is a design approximation of the pixel overlay, **not an Atari800 screenshot**. The user evaluated the v2/v2.1 overlays in Atari800 and **rejected them on visual quality grounds**. Other low-level display nuances could be investigated only if this retired experiment is ever revisited.

## Which XEX to run (historical comparison only)

**For actual gameplay, use the approved non-PMG title in** `assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex`. **Do not adopt the PMG v2/v2.1 titles.**

`GasBlasters82_TitleV2_1_PMG_OpeningSequence.xex` is a **retired alternative full-opening build** that starts with Title v2; everything after the title is identical to the approved v1 sequence:

1. Title: **Arcade Rock**; console **START** →
2. Meet the Crew: **Funky Gas Attack**; joystick **FIRE** →
3. Arriving at Taco Smell: same continuous Funky Gas Attack; joystick **FIRE** →
4. Temporary Stage 1: music off; **START** restarts the sequence.

From the repository root, to inspect the **retired v2.1 comparison only**:

```bash
atari800 -xl -ntsc -nobasic -run assets/title_v2/GasBlasters82_TitleV2_1_PMG_OpeningSequence.xex
```

For the **accepted playable Stage 1** instead:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1_v05/GasBlasters82_Stage1_Playable_v05.xex
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

## Historical emulator evaluation — complete

The user tested both alternate title treatments in Atari800: **v2 exhibited stray cyan/white artifacts; v2.1 reduced the DMA mismatch but its disconnected glints still made the title worse than v1**. Both were **rejected**. Retain these XEXs and code as reproducible experiments only; any future title polish should be a **new, independently approved** design and must preserve the accepted v1 opening. No physical Atari hardware validation is claimed.
