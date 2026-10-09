"""Bons Voyage 1.19.1 placement claims (data side; the rule itself is java/.../claims/Claims.java).

Up to 1.19.0 every school and tier had its own structure set (29 sets), each its own random_spread grid, and the only
exclusion zone was minecraft:villages: temperate land ran six independent grids, other climates three, and ruins of
different sets landed side by side (Testo65 2026-10-06: nine waystones within 300 blocks of one field, 37 neighbour
pairs under 128 blocks, all from different sets, closest 29 blocks).

1.19.1 keeps all 29 sets (names, salts, spacing, weights, exclusion zones; the pack's Structurify entries keep working)
and changes only their placement type to waystone_ruins:claimed_spread with a claim {group, rank, radius}: a candidate
is refused when a higher-ranked set of the same group generates within `radius` chunks. Ranks keep the big, rare
ruins and drop the abundant ones where two would meet. Radii chosen from the rig-1 replay of the exact 1.19.0 layout
(1024 x 1024 chunks around Justin's field): overworld 16 = about the density of one ruin per 20-chunk cell with the
1.19.0 tier mix largely kept; crypts/Nether 12 keep every rare variant and great dungeon.
A merged-sets alternative (placement_groups.py, one grid per realm) was measured and rejected: one ruin per cell
cuts small/grand/undercroft/great ruins by about 60 % because sunken ruins fit almost everywhere.
"""
import copy

RADIUS = {"overworld": 16, "underground": 12, "nether": 12, "end": 12}

CLAIMS = {}
for t in ("sandy", "temperate", "red", "frozen", "mossy"):
    CLAIMS[f"mega_{t}"] = ("overworld", 7)
for t in ("default", "mossy", "sandy", "frozen", "red", "cherry"):
    CLAIMS[f"grand_{t}"] = ("overworld", 6)
    CLAIMS[f"small_{t}"] = ("overworld", 3)
CLAIMS.update({"origin": ("overworld", 8), "undercroft": ("overworld", 5), "drowned": ("overworld", 4),
               "sunken": ("overworld", 1),
               "underground_sculk": ("underground", 3), "underground_lush": ("underground", 3),
               "underground_dripstone": ("underground", 3), "underground": ("underground", 1),
               "mega_nether": ("nether", 2), "nether": ("nether", 1),
               "mega_end": ("end", 2), "end": ("end", 1)})

TYPE = "waystone_ruins:claimed_spread"


def apply(old_sets):
    """old_sets: {set name: set json}. Returns new {set name: set json}; only placement.type and placement.claim change."""
    assert sorted(old_sets) == sorted(CLAIMS), set(old_sets) ^ set(CLAIMS)
    out = {}
    for name, doc in old_sets.items():
        new = copy.deepcopy(doc)
        p = new["placement"]
        assert p["type"] == "minecraft:random_spread" and p.get("spread_type", "linear") == "linear", (name, p)
        p.pop("spread_type", None)
        p["type"] = TYPE
        group, rank = CLAIMS[name]
        p["claim"] = {"group": group, "rank": rank, "radius": RADIUS[group]}
        out[name] = new
    return out
