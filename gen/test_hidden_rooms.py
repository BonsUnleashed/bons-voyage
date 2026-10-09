"""Secret availability, deliberate discovery, egress, loot and pool alignment."""
import tempfile
import unittest

import build as release
from audit_access import WalkGraph, build_case, design_cases
from core import Build
from hidden_rooms import HIDDEN_ROOMS, MIN_Y, CACHE_LOOT
from loot import curiosity_loot_json
from nbt import read_nbt


class HiddenRoomTests(unittest.TestCase):
    def cases(self):
        return [c for c in design_cases() if c[0] in HIDDEN_ROOMS]

    def test_hidden_pools_are_one_in_four_and_preserve_pristine_share(self):
        for sids, pristine in [(['a'],None),(['a','b','c'],None),(['a'],'a_pristine')]:
            pool=release.pool_json(sids,'greek',pristine_sid=pristine,hidden_sid='a_hidden')
            weights={e['element']['location'].split(':')[1]:e['weight'] for e in pool['elements']}
            total=sum(weights.values())
            self.assertEqual(weights['a_hidden']/total,.25)
            if pristine:
                self.assertEqual(weights[pristine]/total,.05)

    def test_common_origin_preserves_surface_height_without_excavating_normal_variant(self):
        with tempfile.TemporaryDirectory() as folder:
            for name,fn,theme,kind in self.cases():
                normal=build_case(name,fn,theme,kind,folder)
                normal_nbt=read_nbt(folder+'/'+name+'_'+theme+'.nbt')
                hidden=build_case(name,fn,theme,kind,folder,hidden=True)
                hidden_nbt=read_nbt(folder+'/'+name+'_'+theme+'.nbt')
                self.assertEqual(normal.emitted_origin[1],MIN_Y)
                self.assertEqual(normal.emitted_origin[1],hidden.emitted_origin[1])
                self.assertFalse(any(y<0 for x,y,z in normal.blocks))
                for root in (normal_nbt,hidden_nbt):
                    ground=2-MIN_Y
                    spec=release.structure_json(name+'_'+theme,release.THEME_TAG[theme],kind,theme=theme,ground=ground)
                    self.assertEqual(64+spec['start_height']['absolute']-1+ground,63)
                    self.assertLessEqual(max(root['size']),48)

    def test_seals_hide_caches_until_opened_and_every_room_has_a_return_route(self):
        with tempfile.TemporaryDirectory() as folder:
            for name,fn,theme,kind in self.cases():
                for seed in range(10):
                    with self.subTest(name=name,seed=seed):
                        b=build_case(name,fn,theme,kind,folder,seed=seed,hidden=True)
                        closed=WalkGraph(b,ground=2,open_secrets=False)
                        outside_closed=closed.flood(closed.outside())
                        caches=[p for p,(_,be) in b.blocks.items() if be and be.get('LootTable')==CACHE_LOOT]
                        self.assertEqual(len(caches),1)
                        x,y,z=caches[0]
                        approaches={(x+dx,y,z+dz) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))}
                        self.assertFalse(outside_closed & approaches)
                        opened=WalkGraph(b,ground=2)
                        outside_open=opened.flood(opened.outside())
                        reachable=outside_open & approaches
                        self.assertTrue(reachable)
                        self.assertTrue(opened.flood(reachable) & set(opened.outside()),'one-way trap')
                        for room in b.rooms:
                            self.assertTrue(outside_open & set(opened.room_positions(room)))
                        self.assertFalse(b.blocks[b.hidden_entrance][0].startswith(('minecraft:gravel','minecraft:suspicious','minecraft:sand')))
                        # Reach the original surface waystone without discovering the cellar.
                        ws=[p for p,(s,_) in b.blocks.items() if s.startswith('waystones:') and 'half=lower' in s]
                        self.assertEqual(len(ws),1)
                        x,y,z=ws[0]
                        self.assertTrue(any((x+dx,y+dy,z+dz) in outside_closed for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)) for dy in (-2,-1,0,1)))

    def test_archive_second_seal_requires_a_second_discovery(self):
        name,fn,theme,kind=next(c for c in self.cases() if c[0]=='temple_of_the_way')
        with tempfile.TemporaryDirectory() as folder:
            b=build_case(name,fn,theme,kind,folder,hidden=True)
            b.secret_blocks.difference_update(b.inner_secret)
            graph=WalkGraph(b,ground=2)
            reached=graph.flood(graph.outside())
            self.assertTrue(reached & set(graph.room_positions(b.rooms[0])))
            self.assertFalse(reached & set(graph.room_positions(b.rooms[1])))

    def test_cache_loot_guarantees_a_keepsake_and_a_real_find(self):
        # v1.17 (Justin, 2026-09-29): finding a sealed room must pay. The cache
        # keeps its keepsake, always rolls one real find, and leaves the great
        # dungeons' hoard items (netherite, notch apples, warp stones) to them.
        pools=curiosity_loot_json()['pools']
        self.assertEqual(pools[0]['rolls'],1)
        self.assertTrue(all(e['name'].endswith('_pottery_sherd') for e in pools[0]['entries']))
        find=pools[-1]
        self.assertEqual(find['rolls'],1)
        self.assertFalse(any(e['type']=='minecraft:empty' for e in find['entries']))
        self.assertTrue(any(e.get('name')=='minecraft:diamond' for e in find['entries']))
        names={e.get('name','') for p in pools for e in p['entries']}
        self.assertFalse(names & {'minecraft:netherite_scrap','minecraft:enchanted_golden_apple','waystones:warp_stone'})
        # Books are enchanted from a plain book, or the anvil cannot use them.
        self.assertNotIn('minecraft:enchanted_book',names)

    def test_rooms_are_furnished_and_lit(self):
        with tempfile.TemporaryDirectory() as folder:
            for name,fn,theme,kind in self.cases():
                with self.subTest(name=name):
                    b=build_case(name,fn,theme,kind,folder,hidden=True)
                    below=[s for (x,y,z),(s,_) in b.blocks.items() if y<0]
                    self.assertTrue(any('lantern' in s for s in below),'no lantern light')
                    self.assertTrue(any('candle' in s for s in below),'no candles')
                    self.assertGreaterEqual(sum('decorated_pot' in s for s in below),2)
                    for (x,y,z),(s,_) in b.blocks.items():
                        if 'lantern[hanging=true' in s or s.startswith('minecraft:chain'):
                            above=b.blocks.get((x,y+1,z),('minecraft:air',None))[0]
                            self.assertNotEqual(above,'minecraft:air',f'{name}: hanging fitting at {(x,y,z)} has nothing above')


if __name__=='__main__':
    unittest.main(verbosity=2)
