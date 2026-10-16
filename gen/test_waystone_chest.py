"""1.20.0 gates: the optional waystone chest, the protected stone and the new default spacing.

Run ``python -m unittest discover -s gen -p "test*.py"`` from the project root. Builds run in temporary
directories; no instance is touched.
"""
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build as release
import waystone_chest as wc
from audit_access import build_case, design_cases
from core import parse_state
from hidden_rooms import HIDDEN_ROOMS

JAVA_CONFIG = Path(__file__).resolve().parent.parent / "src/main/java/dev/agentcraft/waystoneruins/VoyageConfig.java"

# The pack's Structurify values for every Bons Voyage set on 2026-10-16 (config/structurify.json, override true),
# which 1.20.0 makes the mod's own defaults.
PACK_SPACING = {"small": (17, 8), "grand": (27, 14), "sunken": (20, 10), "underground": (22, 11), "nether": (22, 11),
                "end": (29, 14), "drowned": (15, 7), "mega": (55, 28), "origin": (103, 51), "undercroft": (34, 17)}


def family(set_name):
    for prefix in ("small", "grand", "mega", "underground"):
        if set_name.startswith(prefix):
            return prefix
    return set_name


def variants():
    """Every waystone design at seed 0, its pristine copy and, where it has one, its hidden variant."""
    for name, fn, theme, kind in design_cases():
        yield name, fn, theme, kind, dict(seed=0)
        yield name, fn, theme, kind, dict(seed=0, pristine=True)
        if name in HIDDEN_ROOMS and kind == "surface":
            yield name, fn, theme, kind, dict(seed=0, hidden=True)


def marker_chests(b):
    return {p: be for p, (s, be) in b.blocks.items()
            if s.startswith("minecraft:chest") and be and be.get("LootTable", "").startswith(wc.MARKER)}


def no_chest(b, kind, theme, ground=2):
    b.waystone_chest = None
    b.waystone_chest_restore = None


class WaystoneChestTests(unittest.TestCase):
    def test_every_waystone_build_has_one_gated_chest_beside_its_stone(self):
        with tempfile.TemporaryDirectory() as folder:
            for name, fn, theme, kind, opts in variants():
                with self.subTest(design=name, theme=theme, **opts):
                    b = build_case(name, fn, theme, kind, folder, **opts)
                    chests = marker_chests(b)
                    if name in wc.EXEMPT:
                        self.assertEqual(chests, {})
                        continue
                    self.assertEqual(len(chests), 1)
                    (x, y, z), be = next(iter(chests.items()))
                    self.assertEqual(be["LootTable"], wc.MARKER + wc.realm(kind, theme))
                    (wx, wy, wz), facing = wc.find_waystone(b)
                    self.assertEqual(parse_state(b.blocks[(x, y, z)][0])[1]["facing"], facing)
                    self.assertLessEqual(max(abs(x - wx), abs(z - wz)), 2)
                    self.assertIn(y - wy, wc.DROPS)
                    fx, fz = wc.DIRS[facing]
                    self.assertNotEqual((x, z), (wx + fx, wz + fz), "a chest in the arrival column")
                    site = wc.Site(b, kind, getattr(fn, "ground", 2))
                    self.assertTrue(site.floor((x, y - 1, z)))

    def test_switched_off_the_gate_restores_exactly_the_previous_cell(self):
        with tempfile.TemporaryDirectory() as folder:
            for name, fn, theme, kind, opts in variants():
                if name in wc.EXEMPT:
                    continue
                with self.subTest(design=name, theme=theme, **opts):
                    on = build_case(name, fn, theme, kind, folder, **opts)
                    with patch.object(wc, "place", no_chest):
                        off = build_case(name, fn, theme, kind, folder, **opts)
                    cell = on.waystone_chest
                    be = on.blocks[cell][1]
                    self.assertEqual({p: v for p, v in on.blocks.items() if p != cell},
                                     {p: v for p, v in off.blocks.items() if p != cell})
                    if "WasVoid" in be:
                        self.assertNotIn(cell, off.blocks)
                        self.assertIn(kind, ("sunken", "water"))
                    elif "WasBlock" in be:
                        was = be["WasBlock"]
                        props = was.get("Properties")
                        state = was["Name"] + ("[" + ",".join(f"{k}={v}" for k, v in props.items()) + "]" if props else "")
                        self.assertEqual(parse_state(off.blocks[cell][0]), parse_state(state))
                        self.assertIsNone(off.blocks[cell][1])
                    else:
                        self.assertEqual(off.blocks[cell], ("minecraft:air", None))

    def test_stone_halves_generate_with_origin_dungeon(self):
        from selected_structures import SELECTION, build_selected
        from polish import apply as polish_content
        builds = []
        with tempfile.TemporaryDirectory() as folder:
            for name, fn, theme, kind in design_cases():
                builds.append(build_case(name, fn, theme, kind, folder))
        for row in SELECTION:
            b = build_selected(row)
            if row["theme"] != "nether":
                b.footings(2)
            polish_content(b)
            release.add_waystone_chest(b, release.SETS[row["set"]]["kind"], row["theme"], 2, audit=True, surface=True)
            self.assertIsNotNone(b.waystone_chest, row["sid"])
            builds.append(b)
        for b in builds:
            stones = [s for s, _ in b.blocks.values() if s.startswith("waystones:")]
            self.assertEqual(len(stones), 2, b.name)
            for s in stones:
                self.assertEqual(parse_state(s)[1]["origin"], "dungeon", b.name)

    def test_realm_tables_match_the_java_config_defaults(self):
        source = JAVA_CONFIG.read_text(encoding="utf-8")
        java = {realm: re.findall(r'"(minecraft:chests/[a-z_/]+)"', body)
                for realm, body in re.findall(r'DEFAULT_LOOT\.put\("(\w+)", List\.of\(([^;]*)\)\);', source)}
        self.assertEqual(sorted(java), sorted(wc.REALMS))
        for realm in wc.REALMS:
            table = wc.loot_json(realm)
            self.assertEqual(table["type"], "minecraft:chest")
            refs = [e["name"] for pool in table["pools"] for e in pool["entries"]]
            self.assertTrue(all(e["type"] == "minecraft:loot_table" for pool in table["pools"] for e in pool["entries"]))
            self.assertEqual(refs, java[realm], realm)
        # no table that draws an exploration map (a structure search when the chest is opened)
        for refs in java.values():
            self.assertFalse([r for r in refs if "underwater_ruin" in r or "shipwreck_map" in r or "cartographer" in r])

    def test_default_spacing_is_the_pack_setting(self):
        for set_name, cfg in release.SETS.items():
            with self.subTest(set=set_name):
                self.assertEqual((cfg["spacing"], cfg["sep"]), PACK_SPACING[family(set_name)])

    def test_the_gate_runs_first_in_every_waystone_processor_list(self):
        for theme in release.PROCESSORS:
            listed = release.gated(release.processor_json(theme))["processors"]
            self.assertEqual(listed[0], release.CHEST_GATE)
            self.assertEqual(listed[1:], release.processor_json(theme)["processors"])
        pool = release.pool_json(["a"], "default", pristine_sid="p", hidden_sid="h")
        self.assertEqual([e["element"]["processors"] for e in pool["elements"]],
                         ["waystone_ruins:weathering_default", release.CHEST_GATE_LIST, "waystone_ruins:weathering_default"])
        self.assertNotIn(release.CHEST_GATE, release.settled_processor_json("default")["processors"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
