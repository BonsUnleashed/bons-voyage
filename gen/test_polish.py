"""Content-only release gates for the four approved 1.19.4 changes."""
import copy
import json
import tempfile
import unittest

import build
from audit_access import build_case, design_cases
from loot import curiosity_loot_json, hidden_treasury_json
from polish import (SCHOOL_SHERDS, THEME_SCHOOL, ARCHAEOLOGY_CELLS,
                    COMMON_REPLACEMENTS, school_cache, school_treasury, archaeology_table, apply)
from selected_structures import EXPANSIONS, BY_ID, record_loot


class PolishTests(unittest.TestCase):
    def test_school_caches_preserve_supplies_and_valuables(self):
        base = curiosity_loot_json()
        for school, sherds in SCHOOL_SHERDS.items():
            table = school_cache(school)
            self.assertEqual(table['pools'][1:], base['pools'][1:])
            self.assertEqual(table['pools'][0]['rolls'], 1)
            self.assertEqual({e['name'] for e in table['pools'][0]['entries']},
                             {'minecraft:' + s + '_pottery_sherd' for s in sherds})
        self.assertEqual(THEME_SCHOOL['cherry'], 'greek')
        for school in SCHOOL_SHERDS:
            table = school_treasury(school)
            self.assertEqual(table['pools'][:-1], hidden_treasury_json()['pools'])
            self.assertEqual(table['pools'][-1], school_cache(school)['pools'][0])

    def test_record_caches_use_their_actual_school(self):
        for ident in EXPANSIONS:
            school = THEME_SCHOOL.get(BY_ID[ident]['theme'])
            if school:
                self.assertEqual(record_loot(ident)['pools'][1],
                                 school_cache(school)['pools'][0])

    def test_archaeology_preserves_every_untouched_probability(self):
        base = build.loot_json()
        pristine = copy.deepcopy(base)
        for purpose, replacements in COMMON_REPLACEMENTS.items():
            table = archaeology_table(base, purpose)
            self.assertEqual(table['type'], 'minecraft:archaeology')
            self.assertEqual(table['pools'][0]['rolls'], 1)
            old = base['pools'][0]['entries']
            new = table['pools'][0]['entries']
            self.assertEqual(sum(e['weight'] for e in old), sum(e['weight'] for e in new))
            for a, b in zip(old, new):
                if a['name'].removeprefix('minecraft:') not in replacements:
                    self.assertEqual(a, b)
                else:
                    self.assertEqual(a['weight'], b['weight'])
        self.assertEqual(base, pristine)

    def test_real_cells_retarget_without_geometry_or_rng_changes(self):
        found = set()
        with tempfile.TemporaryDirectory() as folder:
            for name, fn, theme, kind in design_cases():
                if name not in ARCHAEOLOGY_CELLS:
                    continue
                b = build_case(name, fn, theme, kind, folder,
                               hidden=name in ('stoa', 'temple_of_the_way', 'jungle_altar'))
                before = copy.deepcopy(b.blocks)
                rng = b.rng.getstate()
                apply(b)
                self.assertEqual(rng, b.rng.getstate())
                self.assertEqual({p: s for p, (s, _) in before.items()},
                                 {p: s for p, (s, _) in b.blocks.items()})
                for pos, purpose in ARCHAEOLOGY_CELLS[name].items():
                    self.assertIn(pos, b.blocks, (name, pos))
                    self.assertEqual(b.blocks[pos][1]['LootTable'],
                                     'waystone_ruins:archaeology/' + purpose)
                    found.add(purpose)
                once = copy.deepcopy(b.blocks)
                apply(b)
                self.assertEqual(b.blocks, once)
        self.assertEqual(found, set(COMMON_REPLACEMENTS))

    def test_ordinary_toasts_and_challenge_announcements(self):
        for frame in ('task', 'goal', 'challenge'):
            a = build.advancement_json('test', ['test'], 'minecraft:stone', 'Test', 'Test', frame=frame)
            self.assertTrue(a['display']['show_toast'])
            self.assertEqual(a['display']['announce_to_chat'], frame == 'challenge')
        a = build.advancement_grouped({'school': ['test']}, 'minecraft:stone', 'Test', 'Test', 'test')
        self.assertTrue(a['display']['announce_to_chat'])

    def test_book_hints_point_to_other_sites_not_their_own_seals(self):
        from hidden_rooms import ARCHIVE_REGISTER
        from designs3 import MARDUK_TABLET
        from designs4 import SMUGGLERS_TALLY
        for book, hint in ((ARCHIVE_REGISTER, 'covered walks'),
                           (MARDUK_TABLET, "merchants' house"),
                           (SMUGGLERS_TALLY, 'long roof of turf')):
            self.assertIn(hint, json.loads(book['tag']['pages'][-1])['text'])


if __name__ == '__main__':
    unittest.main(verbosity=2)