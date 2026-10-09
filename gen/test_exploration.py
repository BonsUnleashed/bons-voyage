"""Gameplay invariants for the 1.18 architectural changes."""
import tempfile
import unittest
from audit_access import WalkGraph, build_case, design_cases, audit_build
from exploration import SHOWCASES
from hidden_rooms import HIDDEN_ROOMS
from selected_structures import SELECTION, build_selected


class ExplorationTests(unittest.TestCase):
    def test_clues_only_mark_real_hidden_variants_and_survive_reclamation(self):
        with tempfile.TemporaryDirectory() as out:
            for name,fn,theme,kind in design_cases():
                if name not in HIDDEN_ROOMS:continue
                for seed in range(5):
                    plain=build_case(name,fn,theme,kind,out,seed=seed)
                    hidden=build_case(name,fn,theme,kind,out,seed=seed,hidden=True)
                    self.assertFalse(getattr(plain,'discovery_clues',[]))
                    self.assertTrue(hidden.discovery_clues)
                    for cue in hidden.discovery_clues:
                        self.assertGreaterEqual(len(cue['cells']),4)
                        for pos in cue['cells']:
                            self.assertIn(pos,hidden.protected)
                            self.assertIn(pos,hidden.blocks)
                            self.assertNotEqual(hidden.blocks[pos][0],'minecraft:air')

    def test_showcase_routes_and_arrival_landmarks_survive_all_variants(self):
        with tempfile.TemporaryDirectory() as out:
            for name,fn,theme,kind in design_cases():
                if name not in SHOWCASES:continue
                for seed,pristine in [(i,False) for i in range(10)]+[(0,True)]:
                    with self.subTest(name=name,seed=seed,pristine=pristine):
                        b=build_case(name,fn,theme,kind,out,seed=seed,pristine=pristine)
                        self.assertTrue(b.arrival_landmark)
                        g=WalkGraph(b,ground=getattr(fn,'ground',2))
                        reached=g.flood(g.outside())
                        closed=WalkGraph(b,ground=getattr(fn,'ground',2),open_secrets=False)
                        reached |= closed.flood(closed.outside())
                        for route in b.exploration_routes:
                            for x,z in route['cells']:
                                p=(x,route['floor']+1,z)
                                if b.blocks.get(p,('',None))[0].startswith('waystones:'):continue
                                self.assertTrue(p in reached,(name,'route cell unreachable',p,b.blocks.get(p)))

    def test_six_annex_plans_are_distinct_and_records_stay_behind_their_seals(self):
        layouts=[]
        for row in SELECTION:
            if row['id'] not in ('14','17','18','22','25','54'):continue
            b=build_selected(row)
            self.assertFalse(audit_build(b)['issues'])
            layouts.append(tuple(tuple(q) for q in b.annex_layout['footprints']))
            # Open the surface cap and arrival descent, but leave only the
            # deeper archive plug shut: its records must still be inaccessible.
            archive=set(b.annex_secret)
            b.secret_blocks.difference_update(archive)
            closed=WalkGraph(b); before=closed.flood(closed.outside())
            sealed_room=b.added_rooms[2]['bounds']
            self.assertFalse(before.intersection(closed.room_positions(sealed_room)),row['id'])
            b.secret_blocks.update(archive)
            opened=WalkGraph(b); after=opened.flood(opened.outside())
            self.assertTrue(after.intersection(opened.room_positions(sealed_room)),row['id'])
            for item in b.cache_positions:
                x,y,z=item['position']
                self.assertTrue(any((x+dx,y,z+dz) in after for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))),row['id'])
        self.assertEqual(len(set(layouts)),6)


if __name__=='__main__': unittest.main(verbosity=2)
