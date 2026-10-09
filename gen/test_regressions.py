"""Regression checks for terrain anchoring, room access, and safe weathering.

Run ``python gen/test_regressions.py`` from the project root. These checks
operate in memory or temporary directories; they never modify an instance.
Use ``python gen/audit_access.py --seeds 3`` for the complete room route audit.
"""

import tempfile
import unittest

import build as release
from core import Build
from audit_access import WalkGraph, audit_build
from master import ladder_shaft, room


def evaluate_site_condition(condition, position, heights):
    """Evaluate the emitted condition subset against synthetic heightmaps.

    This deliberately consumes the serialized tree rather than reproducing
    site_modifier's construction. Runtime codec semantics were checked against
    the installed Lithostitched 1.4.11 classes; live worldgen remains a separate
    integration check.
    """
    kind = condition["type"].split(":", 1)[-1]
    x, y, z = position
    if kind == "offset":
        dx, dy, dz = condition["offset"]
        return evaluate_site_condition(condition["condition"], (x + dx, y + dy, z + dz), heights)
    if kind == "grid":
        radius = condition["radius"]
        step = condition["distance_between_points"]
        matches = sum(evaluate_site_condition(condition["condition"], (x + dx, y, z + dz), heights)
                      for dx in range(-radius, radius + 1, step)
                      for dz in range(-radius, radius + 1, step))
        return matches <= condition["allowed_count"]
    if kind == "not":
        return not evaluate_site_condition(condition["condition"], position, heights)
    if kind == "all_of":
        return all(evaluate_site_condition(child, position, heights)
                   for child in condition["conditions"])
    if kind == "height_filter":
        if condition["range_type"] != "heightmap_relative":
            raise ValueError("unexpected range type in site condition")
        lo, hi = condition["permitted_range"]
        return lo <= y - heights(condition["heightmap"], x, z) <= hi
    raise ValueError(f"unrecognized site condition {kind}")


class TerrainRegressionTests(unittest.TestCase):
    def test_basement_cover_survives_surface_clearance(self):
        b = Build("buried_cover", "default")
        room(b, 0, 2, 0, 12, 8, 12)
        b.fill(4, 16, 4, 8, 16, 8, "floor")
        b.column(5, 17, 5, 5, "brick")
        authored = dict(b.blocks)
        b.clearance(ground_y=17)
        for pos, block in b.blocks.items():
            if pos[1] < 17:
                self.assertIn(pos, authored, f"clearance excavated buried cover at {pos}")
                self.assertEqual(block, authored[pos])
        self.assertNotIn((1, 12, 1), b.blocks, "basement roof must retain natural terrain above it")
        self.assertNotIn((1, 17, 1), b.blocks, "buried room footprint must not clear the surface perimeter")

    def test_sparse_l_shaped_footprint_does_not_carve_its_empty_corner(self):
        b = Build("l_footprint", "default")
        b.fill(0, 2, 0, 4, 2, 1, "floor")
        b.fill(0, 2, 0, 1, 2, 4, "floor")
        b.column(0, 3, 0, 10, "brick")
        b.clearance(ground_y=3)
        self.assertFalse(any(x >= 2 and z >= 2 for x, _, z in b.blocks),
                         "clearance carved the missing corner of an L-shaped ruin")

    def test_low_columns_do_not_clear_to_the_tallest_tower(self):
        b = Build("mixed_roof_heights", "default")
        b.set(0, 2, 0, "floor")
        b.column(1, 2, 0, 20, "brick")
        b.clearance(ground_y=3)
        low_air = [y for (x, y, z), (state, _) in b.blocks.items()
                   if x == 0 and z == 0 and state == "minecraft:air"]
        self.assertTrue(low_air, "entry floor needs explicit terrain clearance")
        self.assertLessEqual(max(low_air), 5, "low entrance clears a tower-height terrain cliff")

    def test_every_surface_template_anchors_its_floor_to_terrain(self):
        from audit_access import design_cases
        checked = 0
        with tempfile.TemporaryDirectory(prefix="waystone-anchor-") as folder:
            for name, fn, theme, kind in design_cases():
                if kind != "surface":
                    continue
                with self.subTest(design=name, theme=theme):
                    sid, root, _ = release.build_template(name, fn, theme, kind, folder)
                    ground = root["_ground_level"]
                    spec = release.structure_json(sid, release.THEME_TAG[theme], kind,
                                                  theme=theme, ground=ground)
                    # Minecraft's rigid start-piece ground delta is one block.
                    # H is first free terrain Y; the floor block must be H-1.
                    for heightmap_y in (64, 91, 180):
                        origin = heightmap_y + spec["start_height"]["absolute"] - 1
                        self.assertEqual(origin + ground, heightmap_y - 1)
                    self.assertEqual(spec["terrain_adaptation"], "none")
                    self.assertGreaterEqual(ground, 0)
                    self.assertLess(ground, root["size"][1])
                    for block in root["blocks"]:
                        state = root["palette"][block["state"]]
                        if state["Name"] != "minecraft:jigsaw":
                            continue
                        x, _, z = block["pos"]
                        sx, _, sz = root["size"]
                        face = state["Properties"]["orientation"].split("_")[0]
                        self.assertTrue({"west": x == 0, "east": x == sx - 1,
                                         "north": z == 0, "south": z == sz - 1}[face],
                                        f"{sid}: satellite socket overlaps parent bounds")
                    checked += 1
        self.assertGreater(checked, 100, "surface audit silently skipped the design catalog")

    def test_registered_variants_keep_the_same_emitted_ground(self):
        seen = set()
        with tempfile.TemporaryDirectory(prefix="waystone-variants-") as folder:
            for set_name, cfg in release.SETS.items():
                for designs, theme in [(cfg["designs"], cfg["theme"])] + list(cfg.get("extras", [])):
                    for name, fn in designs.items():
                        variants = []
                        if set_name.startswith("small_") and name in release.SILHOUETTE_VARIANTS:
                            variants.extend([(2, False), (3, False)])
                        if set_name.startswith("grand"):
                            variants.append((0, True))
                        if not variants or (name, theme) in seen:
                            continue
                        seen.add((name, theme))
                        _, base, _ = release.build_template(name, fn, theme, cfg["kind"], folder)
                        for seed, pristine in variants:
                            with self.subTest(design=name, theme=theme, seed=seed, pristine=pristine):
                                _, alternate, _ = release.build_template(name, fn, theme, cfg["kind"], folder,
                                                                         seed=seed, pristine=pristine)
                                self.assertEqual(base["_ground_level"], alternate["_ground_level"])

    def test_runtime_weathering_cannot_delete_structural_blocks(self):
        for theme in release.PROCESSORS:
            with self.subTest(theme=theme):
                processors = release.processor_json(theme)
                for processor in processors["processors"]:
                    for rule in processor.get("rules", ()):
                        self.assertNotIn(rule["output_state"]["Name"],
                                         {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"})

    def test_erosion_keeps_exposed_surface_floors_and_authored_stairs(self):
        b = Build("safe_walkway", "default")
        b.ground_y = 12
        b.fill(0, 12, 0, 5, 12, 3, "floor")
        for step in range(4):
            b.stairs(2, 13 + step, step, "south")
        route = dict(b.blocks)
        b.erode(prob=1.0, min_y=0, passes=20)
        for pos, block in route.items():
            self.assertEqual(b.blocks.get(pos), block, f"erosion removed walking surface {pos}")


class SiteSelectionRegressionTests(unittest.TestCase):
    def test_flat_and_gently_graded_dry_sites_are_accepted(self):
        for ground in (2, 3, 14, 26):
            condition = release.site_modifier("fixture", ground, [27, 32, 19])["spawn_condition"]
            for base_y in (64, 120, 200):
                with self.subTest(ground=ground, base_y=base_y):
                    self.assertTrue(evaluate_site_condition(condition, (0, base_y - ground, 0),
                                                            lambda _map, x, z: base_y))
                    self.assertTrue(evaluate_site_condition(condition, (0, base_y - ground, 0),
                                                            lambda _map, x, z: base_y + (1 if x > 0 else 0)))

    def test_cliffs_and_deep_water_are_rejected_before_placement(self):
        condition = release.site_modifier("fixture", 16, [27, 32, 19])["spawn_condition"]
        self.assertFalse(evaluate_site_condition(condition, (0, 64 - 16, 0),
                                                 lambda _map, x, z: 64 + (6 if x > 0 else 0)))
        self.assertFalse(evaluate_site_condition(condition, (0, 64 - 16, 0),
                                                 lambda heightmap, x, z: 60 if heightmap == "OCEAN_FLOOR_WG" else 64))

    def test_a_single_bad_sample_is_enough_to_reject_a_site(self):
        # radius 12; since 1.19.3 the grid samples -12, -6, 0, 6, 12 on each axis
        condition = release.site_modifier("fixture", 2, [15, 12, 15])["spawn_condition"]
        self.assertFalse(evaluate_site_condition(condition, (0, 62, 0),
                                                 lambda _map, x, z: 58 if (x, z) == (6, 0) else 64))

    def test_coarser_grid_keeps_corners_edge_midpoints_and_centre(self):
        for radius, step in {8: 4, 12: 6, 16: 8, 20: 5, 32: 8, 36: 6, 40: 5}.items():
            with self.subTest(radius=radius):
                self.assertEqual(release.site_step(radius), step)
                points = list(range(-radius, radius + 1, step))
                self.assertEqual((points[0], points[-1]), (-radius, radius))
                self.assertIn(0, points)
                self.assertGreaterEqual(step, 4)


class AccessAuditRegressionTests(unittest.TestCase):
    def test_production_build_rejects_a_sealed_surface_waystone(self):
        def sealed(b):
            b.foundation(0, 0, 6, 6)
            room(b, 0, 2, 0, 6, 7, 6)
            b.waystone(3, 3, 3)

        def accessible(b):
            sealed(b)
            b.air(3, 3, 0, 3, 4, 0)

        with tempfile.TemporaryDirectory(prefix="waystone-build-gate-") as folder:
            with self.assertRaisesRegex(ValueError, "access"):
                release.build_template("sealed_fixture", sealed, "default", "surface", folder)
            release.build_template("open_fixture", accessible, "default", "surface", folder)

    def test_one_block_high_room_is_rejected(self):
        b = Build("crawlspace", "default")
        with self.assertRaises((ValueError, AssertionError)):
            room(b, 0, 0, 0, 5, 2, 5)

    def test_missing_underground_voxels_are_solid_terrain(self):
        b = Build("unexcavated_passage", "default")
        room(b, 0, 0, 0, 4, 4, 4)
        room(b, 7, 0, 0, 11, 4, 4)
        b.air(4, 1, 2, 4, 2, 2)
        b.air(7, 1, 2, 7, 2, 2)
        graph = WalkGraph(b, ground=10)
        self.assertNotIn((8, 1, 2), graph.flood([(2, 1, 2)]))
        b.air(5, 1, 2, 6, 2, 2)
        graph = WalkGraph(b, ground=10)
        self.assertIn((8, 1, 2), graph.flood([(2, 1, 2)]))

    def test_one_high_corridor_does_not_connect_rooms(self):
        b = Build("headroom", "default")
        room(b, 0, 0, 0, 4, 4, 4)
        room(b, 6, 0, 0, 10, 4, 4)
        b.air(4, 1, 2, 6, 1, 2)
        graph = WalkGraph(b, ground=10)
        self.assertNotIn((7, 1, 2), graph.flood([(2, 1, 2)]))
        b.air(4, 2, 2, 6, 2, 2)
        graph = WalkGraph(b, ground=10)
        self.assertIn((7, 1, 2), graph.flood([(2, 1, 2)]))

    def test_ladder_route_needs_an_open_landing(self):
        b = Build("buried_ladder", "default")
        room(b, 0, 0, 0, 6, 4, 6)
        ladder_shaft(b, 3, 3, 1, 7, facing="north")
        graph = WalkGraph(b, ground=7)
        self.assertIn((3, 1, 3), graph.flood(graph.outside()))
        b.set(3, 7, 3, "brick")
        graph = WalkGraph(b, ground=7)
        self.assertNotIn((3, 1, 3), graph.flood(graph.outside()))

    def test_only_authored_secret_blocks_may_be_opened(self):
        b = Build("secret_barrier", "default")
        room(b, 0, 0, 0, 4, 4, 4)
        room(b, 4, 0, 0, 8, 4, 4)
        for y in (1, 2):
            b.set(4, y, 2, "minecraft:cracked_stone_bricks")
        graph = WalkGraph(b, ground=10)
        self.assertNotIn((5, 1, 2), graph.flood([(2, 1, 2)]))
        b.secret_blocks = {(4, 1, 2), (4, 2, 2)}
        graph = WalkGraph(b, ground=10)
        self.assertIn((5, 1, 2), graph.flood([(2, 1, 2)]))

    def test_ladder_backing_survives_full_erosion(self):
        b = Build("durable_ladder", "default")
        ladder_shaft(b, 0, 0, 0, 8, facing="east")
        b.erode(prob=1.0, min_y=0, passes=12)
        issues = audit_build(b, ground=0)["issues"]
        self.assertFalse([issue for issue in issues if "backing" in issue], issues)


if __name__ == "__main__":
    unittest.main(verbosity=2)
