# Meet the Crew — emulator-tested v4

- `source_art_original.png`: original selected high-resolution scene artwork (game logo/background restaurant sign/name labels removed).
- `meet_the_crew_v4.xex`: the mixed ANTIC E/ANTIC 2 XEX the user tested on Atari 800 Emulator 5.2.0.
- `preview.png`: preview from the tested build.
- `art_160x128_antic_e.bin`: 5120 bytes of actual Atari 2bpp display bitmap data.
- `art_160x128_4colors.png`: exact constrained-color preview.
- `palette_bands.bin/json`: 12 groups of GTIA register values.
- `display_list.bin`, `charset_1kb.bin`, `text_40col_8rows.bin`: native ANTIC artifacts.
- `manifest.json`: original screen conversion/build details.

Approved quote: “Meet Billy Blaster. He's got a fast car, great friends, and a stomach that's about to become a national emergency.”

**Status:** Standalone bitmap/XEX visually tested; typography and actual Fire button action are not finalized; not integrated into Stage 1. Build with `python tools/build_clean_intro.py`.
