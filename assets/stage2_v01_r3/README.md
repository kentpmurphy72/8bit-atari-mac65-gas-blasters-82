# Stage 2 v0.1-r3 — extended high-speed car travel

Native 6502 standalone XEX, stock **64 KB Atari 800XL**, NTSC, BASIC disabled.
Branch: `feature/stage2-driving-v0.1`. **CPU tested; r3 Atari800 acceptance pending.**
This is a v0.1 tuning revision, not v0.2. No merge or tag.

## Run

```bash
atari800 -xl -ntsc -nobasic -run assets/stage2_v01_r3/GasBlasters82_Stage2_Driving_v01_r3.xex
```

For a downloaded XEX in your current directory:

```bash
atari800 -xl -ntsc -nobasic -run ./GasBlasters82_Stage2_Driving_v01_r3.xex
```

The original v0.1 and user-playtested r2 remain unchanged for comparison:
`assets/stage2_v01/` and `assets/stage2_v01_r2/`, including all tools/artifacts.
[See r2 notes](../stage2_v01_r2/README.md) for common controls, display and memory.

## Only gameplay change: upper-speed target mapping

| Speed Q4 | r3 car-top Y | Car center | Comparison |
|---|---:|---:|---|
| Minimum 8 | 160 | 168 | Same as r2 |
| Default 24 | 144 | 152 | Same as r2 |
| Maximum 56 | **80** | **88** | r2 top was 112 |

All Y values are scanlines relative to the 192-line driving viewport. The car is
still 16 scanlines tall; at maximum speed it occupies **Y80–95**. Total travel is
80 scanlines, versus r2's 48. It stays wholly inside the road pane.

Targets interpolate through those exact anchors:

- Speed 8..24: **Y = 168 − speedQ4** (unchanged from r2).
- Speed 24..56: **Y = 192 − 2×speedQ4**.
- Indices outside the speed range clamp to the minimum/maximum target.

Both segments meet at Y144 at speed 24. The slope changes, but the target function
is continuous/monotonic. The actual car still approaches at **12 Q4 units/tick =
0.75 scanline/tick**, with the existing no-overshoot clamp and PMG quantization.
No steering, acceleration, speed caps or smoothing rate was retuned.

**Expected settling:** accelerating from default to maximum takes the same 32
observed ticks. The car then needs **54 more ticks (~0.9 s nominal NTSC)** to reach
Y80, versus r2's 11. Neutral holds speed and the target while that short approach
finishes, then holds the actual position. At an intermediate speed, it holds that
speed's own target, not default Y144. If braking/reversing before smoothing has
finished, the car can initially continue toward the still-ahead target until it
crosses the car's current position. This is the unchanged target-following behavior
with a longer range; evaluate the lag in Atari800 before altering tuning.

## Everything else preserved

Joystick 1 LEFT/RIGHT steers; UP/DOWN changes speed and desired Y; diagonals combine
both; FIRE is reserved and does not lock movement; START/F4 restores default X/Y,
speed, road phase and demo HUD after release/rearm.

Speeds Q4 8/24/56, acceleration/brake ±1, steering Q4 12, fixed right HUD, 27/13
pane split, road/shoulder/grass geometry, car art, PMG colors/setup, font buffering,
positive automatic scrolling and all exclusions are unchanged. No pressure,
arrival, penalties, opponents, curves, forks, attacks or Stage 1 integration.

**Binary proof:** every loaded r3 XEX segment equals r2 byte-for-byte **except the
Y target tables at $6600 and $6700**. The native controller instructions/state
layout, all artwork and display/font/PMG/road segments are identical. Table entries
through default speed are also identical. Both earlier releases and their tools
are unchanged in the repository.

## Build / tests / evidence

Build uses Python 3 standard library only; Python never runs on the Atari:

```bash
python3 tools/build_stage2_v01_r3.py
```

Source: `tools/build_stage2_v01_r3.py`; provisional values: this directory's
`tuning.json`. `driving_6502.asm` is the generated native instruction listing,
not an independent MAC/65 master source. Manifest records exact targets/segments,
SHA-256 and both preserved baseline binary hashes.

With py65 1.2.0 installed using `tools/requirements-stage1-test.txt`:

```bash
python3 tools/test_stage2_v01_r3.py
python3 tools/test_stage2_v01_r2.py
python3 tools/test_stage2_v01.py
python3 tools/profile_stage2_v01_r3.py
```

**Actual results:** 21 r3 tests PASS; 19 unchanged r2 and 12 original v0.1 tests
PASS. Stage 1 regression suites (15+18 tests), four map/pressure/blast validators
and opening CPU/DLI/music validation also PASS. No test failures remain.

Coverage includes exact anchors/slopes, continuity around default, bounds and
monotonicity, smoothing/intermediate target hold, neutral persistence, original
steering/diagonals/FIRE/reset, complete P0/P1 bitmap relocation and old-row clearing,
fixed HUD/fonts, segment safety, baseline preservation and deterministic rebuild.
Each driving suite also executes a three-minute **simulated** native idle run.
These are CPU/data checks, not real Atari800 visual observations.

Memory remains identical to r2: controller/state **$2000–$23A5 (934 bytes)**,
screen $2400, display list $2800, font banks $3000/$3400, PMG $3800–$3FFF (P0 $3C00,
P1 $3D00), road pages $4000–$5FFF, template $6000, telemetry $6400/$6500, Y tables
$6600–$67FF and source car bytes $6800–$681F; temporary zero-page $80–$83. Maximum
speed now draws at PMG rows **112–127** (display origin 32 + logical Y80).

`profile.json` is tied to the binary hash. Sampled peaks: **5,517 CPU cycles** for
combined controls/relocation, **5,474** for neutral settling and **5,460** reset.
These exclude ANTIC DMA/OS interrupts and are not an exhaustive frame budget.

## Recommended Atari800 playtest / known limits

No r3 Atari800, real 800XL or PAL run has been performed here. Actual flicker,
trails, clipping, alignment, responsiveness and feel require user testing.

1. Compare r2 and r3. Hold UP to speed cap, then allow the extra settling time.
   Confirm the car reaches top Y80 and stops drifting while UP remains held.
2. Release at high and intermediate speed. Speed and target persist; after
   smoothing the car must hold position rather than return to default.
3. Brake to minimum: car top should settle to the same Y160, with road still
   moving forward. START should restore exactly the same default Y144/X center.
4. Steer and try all four diagonals at both extremes; keep FIRE held too. Check
   horizontal limits, no HUD trespass and no change to road speed/control feel.
5. Probe around default speed to check smoothness across the mapping slope change.
6. Alternate acceleration/braking before settling. Assess whether the unchanged
   smoothing is too sluggish with the longer travel; report rather than assuming
   the target/smoothing values are final game rules.
7. Watch old car rows, trails, red/white plane alignment, HUD steadiness and road
   artifacts over several minutes and repeated START resets.

This is solely the approved Section 13 Y-range experiment, pending user review.
