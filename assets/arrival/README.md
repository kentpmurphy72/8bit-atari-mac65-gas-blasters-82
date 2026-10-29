# Arriving at Taco Smell — emulator-tested v3

- `source_art_original.png`: original selected medium-detail (Option 3) source art.
- `arrival_v3.xex`: the mixed ANTIC E/ANTIC 2 XEX the user tested on Atari 800 Emulator 5.2.0.
- `preview.png`: preview from that build.
- `art_160x128_antic_e.bin`: 5120 bytes of actual Atari 2bpp display bitmap data.
- `art_160x128_4colors.png`: exact constrained-color preview.
- `palette_bands.bin/json`: 12 groups of GTIA register values.
- `display_list.bin`, `charset_1kb.bin`, `text_40col_8rows.bin`: native ANTIC artifacts.
- `manifest.json`: original screen conversion/build details.

Approved three-line story (each line fits 40 columns):

```
Billy came for a killer burrito.
The beans came with a warning.
Nobody read it. Especially Billy.
```

**Status:** Standalone bitmap/XEX visually tested; `FIRE TO CONTINUE` is visual only; not integrated into the opening sequence. Build with `python tools/build_arrival_screen.py`.
