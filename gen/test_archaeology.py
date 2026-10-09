"""Regression checks for collapsed architecture and surface reclamation."""
import tempfile
import unittest

import build as release
from archaeology import (AIR, full_cube, state_at, standing_column, supported_lintel,
                         validate_archaeology, reclaim, creep)
from audit_access import build_case, design_cases
from core import Build, parse_state
from master import crack_seams, collapse_wedge, room


class ArchaeologyTests(unittest.TestCase):
    def test_broken_support_is_rejected_even_when_beam_connects_sideways(self):
        b = Build('bearing', 'greek')
        b.archaeological = True
        for x in (0, 3):
            standing_column(b, x, 0, 2, 4, complete=True)
        supported_lintel(b, (0, 0), (3, 0), 8, 2)
        validate_archaeology(b, 2)
        b.clear(0, 5, 0)
        with self.assertRaisesRegex(ValueError, 'bearing'):
            validate_archaeology(b, 2)

    def test_floating_pediment_is_rejected_by_production_gate(self):
        def floating(b):
            b.archaeological = True
            b.fill(0, 2, 0, 6, 2, 6, 'floor')
            b.waystone(3, 3, 3)
            b.set(0, 9, 0, 'brick')
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'disconnected masonry'):
                release.build_template('floating', floating, 'greek', 'surface', folder)

    def test_cosmetic_cracks_do_not_remove_load_bearings_or_stairs(self):
        b = Build('cracked_bearing', 'default')
        b.fill(0, 2, 0, 4, 8, 0, 'brick')
        b.stairs(1, 9, 0, 'north')
        before = dict(b.blocks)
        crack_seams(b, 0, 0, 4, 0, 2, 9, count=100)
        for pos in before:
            self.assertNotEqual(state_at(b, pos), AIR)
        self.assertEqual(b.blocks[(1, 9, 0)], before[(1, 9, 0)])

    def test_collapse_cannot_leave_stone_above_the_cut(self):
        b = Build('collapse', 'default')
        b.fill(0, 2, 0, 10, 10, 0, 'brick')
        collapse_wedge(b, 5, 10, 0, 5, 'east', (0, 2, 10, 3))
        for x in range(11):
            occupied = [y for y in range(2, 11) if state_at(b, (x,y,0)) != AIR]
            self.assertEqual(occupied, list(range(2, max(occupied)+1)))

    def test_reclamation_keeps_buried_rooms_and_protected_blocks(self):
        b = Build('buried_vegetation', 'greek')
        room(b, 0, 2, 0, 12, 6, 12)
        b.fill(13, 2, 0, 24, 2, 12, 'floor')
        b.suspicious(20, 2, 4)
        before = dict(b.blocks)
        reclaim(b, 2)
        for pos, block in before.items():
            if pos[0] <= 12 or pos in b.protected:
                self.assertEqual(b.blocks[pos], block, pos)

    def test_plants_attach_only_to_valid_full_block_faces(self):
        for theme in ('greek', 'default', 'cherry', 'mossy', 'mayan'):
            b = Build('reclaimed_faces', theme)
            b.fill(0, 1, 0, 15, 2, 15, 'floor')
            b.column(1, 3, 1, 4, 'brick')
            b.set(2, 3, 1, b.resolve('slab') + '[type=bottom,waterlogged=false]')
            reclaim(b, 2)
            creep(b, 2, probability=1)
            self.assertTrue(any('moss' in s or 'grass' in s for s, _ in b.blocks.values()))
            for (x,y,z), (s, _) in b.blocks.items():
                name, props = parse_state(s)
                if name in {'minecraft:fern', 'minecraft:grass', 'minecraft:moss_carpet'}:
                    self.assertTrue(full_cube(state_at(b, (x,y-1,z))), (theme,(x,y,z)))
                if name == 'minecraft:vine':
                    for face, delta in {'north':(0,-1), 'south':(0,1), 'east':(1,0), 'west':(-1,0)}.items():
                        if props[face] == 'true':
                            dx,dz = delta
                            self.assertTrue(full_cube(state_at(b, (x+dx,y,z+dz))), (theme,(x,y,z)))

    def test_dry_and_cold_schools_do_not_get_temperate_plants(self):
        for theme in ('sandy', 'egyptian', 'red', 'babylon', 'frozen', 'viking', 'nether', 'end'):
            b = Build('dry', theme)
            b.fill(0, 1, 0, 15, 2, 15, 'floor')
            reclaim(b, 2)
            self.assertFalse(any(s.startswith(('minecraft:fern','minecraft:grass','minecraft:vine', 'minecraft:moss_carpet')) for s, _ in b.blocks.values()))

    def test_redesigned_ruins_keep_sky_and_waystone_breathing_room(self):
        names = {'stoa', 'nymphaeum', 'tholos', 'temple_of_the_way', 'sanctuary_of_echoes'}
        checked = 0
        with tempfile.TemporaryDirectory() as folder:
            for name, fn, theme, kind in design_cases():
                if name not in names:
                    continue
                for seed, pristine in [(n, False) for n in range(5)] + [(0, True)]:
                    with self.subTest(name=name, theme=theme, seed=seed, pristine=pristine):
                        b = build_case(name, fn, theme, kind, folder, seed, pristine)
                        ground = getattr(fn, 'ground', 2)
                        validate_archaeology(b, ground)
                        floor = {(x,z) for (x,y,z),(s,_) in b.blocks.items() if y == ground and full_cube(s)}
                        covered = {(x,z) for (x,y,z),(s,_) in b.blocks.items() if y >= ground+4 and full_cube(s)}
                        self.assertLess(len(floor & covered)/len(floor), 0.30)
                        for (x,y,z),(s,_) in b.blocks.items():
                            if s.startswith('waystones:') and 'half=lower' in s and name != 'sanctuary_of_echoes':
                                self.assertEqual(y, ground+1, 'the waystone must sit at walking grade')
                                self.assertTrue(all(state_at(b,(x,yy,z)) == AIR for yy in range(y+2, max(p[1] for p in b.blocks)+1)))
                        checked += 1
        self.assertEqual(checked, 36)


if __name__ == '__main__':
    unittest.main(verbosity=2)
