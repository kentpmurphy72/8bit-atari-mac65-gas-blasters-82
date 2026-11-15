# Codex handoff — Stage 2 v0.4: Off-Road Consequences

**Branch:** `feature/stage2-offroad-consequences-v0.4` (already created from accepted `stage2-v0.3` / `main`, commit `c0c68285c1fc947c89520a5123e462bd98509e1e`).
**Status:** User-approved **design** only; implement and test. **Do not merge, tag, delete the branch, or claim user playtest acceptance.**

Read `AGENTS.md`, `docs/STAGE2_DESIGN.md` **§28** (authoritative), `docs/GAME_DESIGN.md` §5.7, `docs/TECHNICAL_DESIGN.md`, `docs/REPOSITORY_WORKFLOW.md` and the accepted `assets/stage2_v03/` baseline. Preserve all historical 6502/XEX/manifest assets.

Implement a **standalone native Atari 800XL 64KB 6502 XEX** under `assets/stage2_v04/`:

1. Classify the **unshaken logical car center** (8-pixel PMG left +4) into fixed 108-pixel cross-section: grass [0,14), shoulder [14,21), road [21,87), shoulder [87,94), grass [94,108). Pavement/shoulder/grass steering step = **12/10/8 Q4**; use the **stronger** of this and existing 75%/90% GAS steering penalty (never multiply).
2. Independent grass timer in **1/300-s units**: +5 NTSC/+6 PAL per grass driving frame; pause on shoulder; **reset on pavement**; explosion at **600 units = 2s**. Warning stages: skid (0–0.5s), bounded shake (0.5–1s), smoke + POKEY warning (1–1.5s), heavy smoke + critical POKEY warning (1.5–2s). Preserve car visibility and stationary HUD.
3. Make the off-road explosion **orange/red**, unlike green GAS pressure. Freeze drive/scroll/GAS/MI, lose **one life**, then reuse `BILLY BLEW IT!`/`GAME OVER` and fresh-FIRE restart, preserving remaining lives on retry; reset grass/GAS/MI/speed/car/scroll/warnings each attempt. GAME OVER/new successful run restores three lives; preserve two-FIRE pharmacy completion and START/F4 non-bypass.
4. Resolve simultaneous outcomes from **unrounded** state: **GAS 100% → grass 600 → pharmacy arrival**. Latch only one result; no double life loss. Keep the accepted geometry, controls, 27/13 HUD, pharmacy, and gas behavior. Do **not** add winding roads, forks, enemy cars, car blasts or Stage 3.

Ship reproducible offline builder, readable native source/listing, versioned XEX, manifest/sha256 and segments, CPU tests, cycle/memory profile, validation evidence and docs updates. Test all four center-x transitions, PAL/NTSC clock, pause/reset/resume, warning overlap, terminal ties, 3→0 lives, FIRE/START, older XEX hashes and Stage 1/2 regressions. Run Atari800 in NTSC/PAL if available; otherwise **explicitly report NOT RUN** and provide Kent a concise manual Atari800 playtest checklist.

**Reply with:** feature branch/commit, runnable XEX path, build/test commands, actual test pass/fail counts, RAM/zero-page/cycle results, missing emulator/hardware coverage, limitations, and what Kent should test. Await his acceptance before any release actions.
