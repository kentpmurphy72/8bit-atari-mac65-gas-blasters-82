#!/usr/bin/env python3
"""Validate Stage 1 v0.5 gas-blast tuning contract (offline stdlib only).

This checks design data consistency; it does NOT prove that a 6502 XEX implements it.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "assets" / "gameplay"
r = json.loads((DIR / "taco_smell_stage1_v05_blast.json").read_text(encoding="utf-8"))
m = json.loads((DIR / "taco_smell_stage1_v04_movement.json").read_text(encoding="utf-8"))
e = json.loads((DIR / "taco_smell_stage1_v03_rules.json").read_text(encoding="utf-8"))
rooms = json.loads((ROOT / "assets/maps/taco_smell_stage1_v02.json").read_text(encoding="utf-8"))

assert r["schema_version"] == 5
assert r["baseline_branch"] == "feature/stage1-movement-v0.4"
assert r["implementation_branch"] == "feature/stage1-blast-v0.5"
assert r["timing"]["frames_per_second_nominal"] == m["frame_clock"]["nominal_frames_per_second"]
assert r["controls"]["directional_attack_count"] == 4
assert r["controls"]["walk_while_fire_held"] is False
assert r["controls"]["eight_way_walk_when_released"] is True
assert r["controls"]["release_to_rearm"] is True
assert r["controls"]["fire_pressed_during_cooldown_or_empty"].find("never queue") >= 0
assert r["controls"]["windup_frames"] >= 2
assert r["controls"]["cutscene_fire_unchanged"] and r["controls"]["road_blast_unaffected"]

anim = r["animation"]
waves = anim["cloud_waves"]
assert len(waves) == 3
assert waves[0]["offset_frames"] == 0
assert all(w["duration_frames"] >= 1 for w in waves)
assert sum(w["duration_frames"] for w in waves) == anim["cloud_live_frames"]
assert [w["max_depth_tiles"] for w in waves] == [1, 2, 3]
assert [w["half_width_tiles"] for w in waves] == [0, 1, 1]
for i, wave in enumerate(waves):
    assert wave["offset_frames"] == sum(w["duration_frames"] for w in waves[:i])
assert anim["max_depth_tiles"] == 3
assert [anim["width_by_depth"][str(i)] for i in (1, 2, 3)] == [0, 1, 1]
assert anim["solid_occlusion"] and anim["no_room_leak"] and anim["no_solid_overdraw"]
assert set(anim["solid_tiles"]) == {k for k, v in rooms["terrain"].items() if v["solid"]}
assert anim["sfx"]["duration_frames"] <= anim["cloud_live_frames"]

combat = r["combat"]
assert combat["max_knockback_tiles"] == 3
assert combat["knockback_frames_per_tile"] >= 2
assert combat["collision_solid"] and combat["collision_other_worker"]
assert combat["enemies_cannot_be_forced_through_doors_or_exit"] is True
assert combat["stun_frames"] >= e["blast"]["stun_frames"]
assert combat["impact_flash_frames"] > 0
assert combat["enemy_hit_limit"] and combat["knockback_persist"]

supply = r["resource"]
assert supply["enabled"] is True
assert supply["start_charges"] == supply["max_charges"] == 3
assert supply["cost_per_successful_discharge"] == 1
assert supply["regenerate_one_charge_every_frames"] > supply["cooldown_frames_from_discharge"] >= 1
assert supply["recovery_frames_from_discharge"] >= r["controls"]["windup_frames"] // 2
assert supply["regenerate_while_moving"] and supply["regenerate_while_aiming"]
assert "restart" in supply["refill_policy"]
assert r["preservation"]["player_movement"] and r["preservation"]["opening"]
assert len(e["hazmat"]["units"]) == 3
assert rooms["display"]["tile_columns"] == 40 and rooms["display"]["tile_rows"] == 22

print("PASS: Stage 1 v0.5 has 4 aim directions, 3 timed cloud waves, occlusion,")
print("      3 animated knockback tiles, 3 regenerating charges, and intact v0.4/v0.3 baselines.")
print("NOTE: This validates JSON, NOT the resulting 6502 gameplay or Atari800 presentation.")
