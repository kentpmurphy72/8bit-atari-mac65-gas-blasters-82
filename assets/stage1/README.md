# Gas Blasters '82 — Stage 1 Playable Prototype v0.1

Native 6502 Atari XEX, for a stock 64 KB Atari 800XL with BASIC disabled.
Built on `feature/stage1-playable-v0.1`; not merged. Atari800 and hardware
playtesting are pending. Map/layout and movement/enemy timing remain provisional.

## Launch in Atari800

From the repository root, with Atari800 and legally supplied XL OS ROMs configured:

```bash
atari800 -xl -ntsc -nobasic -run assets/stage1/GasBlasters82_Stage1_Playable_v01.xex
```

The build targets the existing NTSC opening. PAL functionality and timing are
unverified. Configure Atari800 joystick port 1 (keyboard or physical joystick)
using the emulator's joystick settings; keyboard bindings vary by installation.
Console START is normally F4.

## Controls and flow

- Title: console START; crew: joystick-1 FIRE; arrival: joystick-1 FIRE.
  Original release-before-press behavior, art, captions, palettes and songs remain.
- Stage: joystick port 1, four cardinal directions. Tile steps repeat every eight
  observed frames, with up/down/left/right priority if several directions are held.
- Billy is the narrow running-person glyph; hazmat is the broad helmeted glyph.
  Obstacles use filled patterns; walkable floor is blank, grease is ordinary floor,
  and the rear exit is a cross-shaped marker. These are temporary monochrome graphics.
- One hazmat worker appears after 180 observed frames (about 3 seconds NTSC), and
  waits at least 16 frames between pursuit searches. It uses cardinal breadth-first
  pursuit, never solids, processing eight search cells per frame to keep input active.
- Contact shows CAUGHT; reaching (47,10) shows STAGE COMPLETE. Both freeze gameplay.
- Release and press START to restart the stage, including from either result state.
  No lives deducted; no road stage launched. FIRE has no gameplay effect.
- Reload the XEX to replay the introduction. The old placeholder's START-to-title
  action is replaced with Stage 1 restart; all earlier screen controls are retained.

## Rebuild and validate

Build uses Python 3 standard library only, reading the immutable opening-v1 XEX
and the authoritative map/JSON. It never regenerates or overwrites opening assets.

```bash
python3 tools/validate_taco_smell_stage1.py
python3 tools/build_stage1.py
python3 -m venv /tmp/gas-stage1-tests
/tmp/gas-stage1-tests/bin/pip install -r tools/requirements-stage1-test.txt
/tmp/gas-stage1-tests/bin/python tools/test_stage1.py
python3 tools/validate_opening_sequence.py --output /tmp/gas-opening-validation
```

`tools/build_stage1.py` is the authoritative 6502 byte-emitter source using the
repository's existing emitter. `stage1_6502.asm` is the generated instruction
listing, not an independently MAC/65-assembled file. The opening controller source
is retained in `tools/build_opening_sequence.py`. No Python executes on the Atari.
The manifest records addresses, sizes, labels, hashes and pending emulator status.

## Memory and rendering

- $1000–$17FF: new stage controller budget (actual extent in manifest).
- $2000–$97FF: original opening controller/art/music/display data. Only the first
  three bytes of HANDLE_INPUT and DRAW_STAGE are replaced with dispatch jumps.
- $9800–$9C1F: 1,056-byte BFS parent-direction scratch (replaces placeholder).
- $A000–$A41F: 1,056 semantic tiles; high bit is the JSON `solid` flag.
- $A500–$A5AB: map/screen/scratch row-address tables (with gaps).
- $A600–$A69F: status messages.
- $AC00–$AFFF: temporary 1 KB character set, including retained caption lettering.
- $B000–$B3BF: 40×24 ANTIC 2 screen, 30×22 map window, blank ten-column strip,
  two status rows. Camera is clamp(Billy.x−14, 0, 18).
- $B400–$B81F / $B900–$BD1F: BFS x/y FIFO arrays, maximum 1,056 entries each.
- $80–$8B: temporary zero-page pointers, BASIC must remain disabled.

Stage display uses ANTIC character mode 2 and GTIA text colors. Original art and
font data remain intact, and stage DLIs are disabled while OS VBI/frame clock
remains active. A full viewport redraw occurs every eight observed frames or on
result transitions. BFS is incremental (eight dequeued cells per observed frame); each
search tracks Billy’s position when it started, then moves one tile along that
route. Distant searches take longer, so enemy tuning is deliberately provisional.
Movement cadence, redraw cost and responsiveness need emulator measurement; the build does not claim fixed per-frame execution or 70–105s pacing.

## Validation performed

- Existing map validator passes: 48×22, 751 walkable cells, 43-step shortest exit route.
- Nine py65 tests execute the delivered XEX's real 6502 opcodes: all tile/boundary
  collision rules; joystick-driven exit route; spawn delay, CAUGHT, restart/debounce
  and frozen results; six pursuit targets across all zones with shortest-path
  distance decreasing on every step; camera/terrain rendering; deterministic
  rebuild and byte-identical baseline preservation; original opening flow/music.
- Existing opening validator passes separately, including 48,650 simulated CPU
  instructions and DLI palette checks. It writes only to a temporary directory.
- Tests use a CPU emulator, not ANTIC/GTIA/POKEY or a full Atari machine.

## Atari800 acceptance checklist (pending)

1. Compare title and both cutscenes against opening v1: pictures, text, palettes,
   title song, continuous Funk theme, and held/released START/FIRE behavior.
2. Enter Stage 1: confirm readable map/status, distinct actors and no display corruption.
3. Test all four joystick directions, held directions, blocked moves and perimeter
   entrances. Traverse both passages and observe horizontal camera at either edge.
4. Wait for hazmat, evade around tables/equipment/shelves, check pursuit/catch,
   and measure responsiveness when BFS runs across the restaurant.
5. Confirm CAUGHT freezes movement and START restarts with fresh spawn delay.
6. Reach rear X: confirm STAGE COMPLETE freezes movement, with no Road 1 jump;
   START restarts without returning through cutscenes.
7. Repeat several restarts; check timing, display stability and stock 64 KB loading.
8. Real-hardware validation remains outstanding after emulator testing.

Gas blasting, grease physics, reinforcements, extra enemies and advanced art are
intentionally absent. Opening v1 remains unchanged and separately runnable.
