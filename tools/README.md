# Atari 800XL screen asset builders

These are reproducible source conversion/build scripts for the two standalone Atari 800XL intro-screen prototypes. The 6502 XEX code and native art data are generated from the full-resolution `source_art_original.png` images.

## Dependencies

Python 3 with `numpy`, `opencv-python`, and `Pillow` installed. These are **build-time only** tools, not dependencies on the Atari.

## Build

From repository root:

```bash
python tools/build_clean_intro.py
python tools/build_arrival_screen.py
```

Both build scripts emit their artifacts into their corresponding `assets/{intro,arrival}/generated_atari_assets/` directories. The test-ready XEX for each scene is also versioned at `assets/intro/meet_the_crew_v4.xex` and `assets/arrival/arrival_v3.xex`.

The on-screen `FIRE TO CONTINUE` prompt is **visual only** in these demo executables. Scene progression and integration into the playable game remain future work.

**Historical caution:** Meet the Crew v4 and arrival v3 are the tested builds. Do not mistake the generated full-bitmap alternate XEX for an emulator-tested choice.
