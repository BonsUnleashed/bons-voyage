"""v1.17 reward rules: where spawners may stand, which chests pay what, and
that every enchanted book can actually be used.

Run ``python gen/test_rewards.py`` from the project root. Builds run in
temporary directories; no instance is touched.
"""
import tempfile
import unittest

import build as release
import designs4 as d4
from audit_access import build_case, design_cases
from loot import (HIDDEN_TREASURY, HOARD, curiosity_loot_json,
                  hidden_treasury_json, hoard_json)
from master import CRYPT_CHEST_LOOT
from hidden_rooms import CACHE_LOOT

TABLES = {
    "crypt": release.crypt_loot_json(),
    "curiosity_cache": curiosity_loot_json(),
    "hidden_treasury": hidden_treasury_json(),
    "waybuilder_hoard": hoard_json(),
    "archaeology": release.loot_json(),
}
TIERS = {CRYPT_CHEST_LOOT, CACHE_LOOT, HIDDEN_TREASURY, HOARD}


def entries(table):
    return [e for pool in table["pools"] for e in pool["entries"]]


def min_rolls(pool):
    rolls = pool["rolls"]
    return rolls if isinstance(rolls, int) else rolls["min"]


def containers(b):
    """Loot containers (chests, barrels) by position; brushable blocks excluded."""
    return {p: be["LootTable"] for p, (state, be) in b.blocks.items()
            if be and "LootTable" in be and not state.startswith("minecraft:suspicious")}


class SpawnerPolicyTests(unittest.TestCase):
    def test_only_the_great_dungeons_hold_spawners(self):
        with tempfile.TemporaryDirectory() as folder:
            for set_name, cfg in release.SETS.items():
                for designs, theme in [(cfg["designs"], cfg["theme"])] + list(cfg.get("extras", [])):
                    for name, fn in designs.items():
                        with self.subTest(set=set_name, design=name, theme=theme):
                            b = build_case(name, fn, theme, cfg["kind"], folder)
                            spawners = [p for p, (s, _) in b.blocks.items() if s == "minecraft:spawner"]
                            if set_name not in release.SPAWNER_SETS:
                                self.assertFalse(spawners, f"{name} is not a great dungeon")

    def test_smugglers_undercroft_has_no_spawner_but_a_hidden_strongroom(self):
        with tempfile.TemporaryDirectory() as folder:
            b = build_case("smugglers_undercroft", d4.smugglers_undercroft, "default", "surface", folder)
            self.assertFalse([p for p, (s, _) in b.blocks.items() if s == "minecraft:spawner"])
            self.assertNotIn("undercroft", release.SPAWNER_SETS)
            tables = sorted(containers(b).values())
            self.assertEqual(tables, [HIDDEN_TREASURY, HIDDEN_TREASURY])
            # The strongroom chest lies behind the bricked-up door, not in the open warren.
            from audit_access import WalkGraph
            closed = WalkGraph(b, ground=d4.smugglers_undercroft.ground)
            closed.secrets -= {(10, 4, 15), (10, 5, 15)}
            reached = closed.flood(closed.outside())
            strongbox = (17, 4, 16)
            self.assertIn(containers(b)[strongbox], (HIDDEN_TREASURY,))
            self.assertFalse(any((strongbox[0] + dx, strongbox[1], strongbox[2] + dz) in reached
                                 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))))


class LootTableTests(unittest.TestCase):
    def test_books_are_enchanted_from_plain_books(self):
        # EnchantRandomlyFunction only converts minecraft:book; an enchanted_book
        # input gets its enchantment in the wrong tag and is useless in an anvil.
        for name, table in TABLES.items():
            with self.subTest(table=name):
                for e in entries(table):
                    self.assertNotEqual(e.get("name"), "minecraft:enchanted_book")
                    if any(f["function"].startswith("minecraft:enchant") for f in e.get("functions", [])):
                        self.assertEqual(e["name"], "minecraft:book")

    def test_every_item_is_namespaced_and_from_a_dependency(self):
        for name, table in TABLES.items():
            with self.subTest(table=name):
                self.assertIn(table["type"], ("minecraft:chest", "minecraft:archaeology"))
                for e in entries(table):
                    if e["type"] == "minecraft:item":
                        self.assertRegex(e["name"], r"^(minecraft|waystones):[a-z0-9_]+$")
                        self.assertGreaterEqual(e.get("weight", 1), 1)

    def test_tiers_rise_with_how_hidden_the_room_is(self):
        cache, treasury, hoard = (TABLES[k]["pools"] for k in ("curiosity_cache", "hidden_treasury", "waybuilder_hoard"))
        # Guaranteed valuable rolls: one in a cache, two behind a secret, two or more in a hoard.
        self.assertEqual(min_rolls(cache[-1]), 1)
        self.assertEqual(min_rolls(treasury[-1]), 2)
        self.assertGreaterEqual(min_rolls(hoard[-1]), 2)
        hoard_only = {"minecraft:enchanted_golden_apple", "minecraft:netherite_scrap", "waystones:warp_stone"}
        for table in ("crypt", "curiosity_cache", "hidden_treasury"):
            self.assertFalse(hoard_only & {e.get("name") for e in entries(TABLES[table])}, table)
        self.assertTrue(hoard_only <= {e.get("name") for e in entries(TABLES["waybuilder_hoard"])})

    def test_records_keep_their_book_and_gain_a_find(self):
        from selected_structures import EXPANSIONS, record_loot
        for ident in EXPANSIONS:
            with self.subTest(record=ident):
                pools = record_loot(ident)["pools"]
                self.assertEqual(pools[0]["entries"][0]["name"], "minecraft:written_book")
                self.assertEqual(min_rolls(pools[-1]), 1)
                self.assertFalse(any(e["type"] == "minecraft:empty" for e in pools[-1]["entries"]))


class ChestTierTests(unittest.TestCase):
    def test_every_container_uses_a_known_tier(self):
        from hidden_rooms import HIDDEN_ROOMS
        with tempfile.TemporaryDirectory() as folder:
            for name, fn, theme, kind in design_cases():
                for hidden in (False, True) if name in HIDDEN_ROOMS else (False,):
                    with self.subTest(design=name, theme=theme, hidden=hidden):
                        b = build_case(name, fn, theme, kind, folder, hidden=hidden)
                        for pos, table in containers(b).items():
                            self.assertIn(table, TIERS, f"{name} {pos}")

    def test_each_great_dungeon_keeps_a_hoard_in_its_deepest_room(self):
        with tempfile.TemporaryDirectory() as folder:
            for set_name in sorted(release.SPAWNER_SETS):
                cfg = release.SETS[set_name]
                for name, fn in cfg["designs"].items():
                    with self.subTest(design=name):
                        b = build_case(name, fn, cfg["theme"], cfg["kind"], folder)
                        hoards = [p for p, t in containers(b).items() if t == HOARD]
                        self.assertTrue(hoards, f"{name}: no hoard")
                        lowest = min(p[1] for p in containers(b))
                        self.assertTrue(any(p[1] == lowest for p in hoards), f"{name}: hoard not on the lowest floor")


if __name__ == "__main__":
    unittest.main(verbosity=2)
