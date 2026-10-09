"""Build the Waystone Ruins data-only Forge mod jar (v1.1).

Structure templates for 6 surface themes + 4 cave themes + nether/end/drowned,
satellite jigsaw pieces, per-placement weathering processors, discovery
advancements, archaeology loot; validates everything; zips the jar.
"""
import json
import os
import shutil
import zipfile

from core import Build, parse_state
from designs import (SMALL, SMALL_WITH_BARROW, GRAND, UNDER, SATELLITES,
                     NETHER, END, DROWNED, EGYPT_SMALL, EGYPT_GRAND,
                     GREEK_SMALL, GREEK_GRAND, BABYLON_SMALL, BABYLON_GRAND,
                     VIKING_SMALL, VIKING_GRAND, MAYAN_SMALL, MAYAN_GRAND,
                     CHERRY_GRAND, SUNKEN)
import designs2 as d2
import designs3 as d3
import designs4 as d4
import designs5 as d5
from hidden_rooms import HIDDEN_ROOMS, attach as attach_hidden_room
from loot import curiosity_loot_json, hidden_treasury_json, hoard_json
from nbt import read_nbt

# v1.8: the approved 35-design batch (2026-09-02, Justin: "Keep it all!")
EGYPT_SMALL = dict(EGYPT_SMALL, **d2.EGYPT_SMALL2, **d3.EGYPT_SMALL3)
EGYPT_GRAND = dict(EGYPT_GRAND, **d2.EGYPT_GRAND2, **d3.EGYPT_GRAND3)
GREEK_SMALL = dict(GREEK_SMALL, **d2.GREEK_SMALL2, **d3.GREEK_SMALL3)
GREEK_GRAND = dict(GREEK_GRAND, **d2.GREEK_GRAND2, **d3.GREEK_GRAND3)
BABYLON_SMALL = dict(BABYLON_SMALL, **d2.BABYLON_SMALL2, **d3.BABYLON_SMALL3)
BABYLON_GRAND = dict(BABYLON_GRAND, **d2.BABYLON_GRAND2, **d3.BABYLON_GRAND3)
# v1.11: the "viking" school is Norse & Celtic - designs5 adds the Celtic half
VIKING_SMALL = dict(VIKING_SMALL, **d2.VIKING_SMALL2, **d3.VIKING_SMALL3, **d5.CELTIC_SMALL)
VIKING_GRAND = dict(VIKING_GRAND, **d2.VIKING_GRAND2, **d3.VIKING_GRAND3, **d5.CELTIC_GRAND)
MAYAN_SMALL = dict(MAYAN_SMALL, **d2.MAYAN_SMALL2, **d3.MAYAN_SMALL3)
MAYAN_GRAND = dict(MAYAN_GRAND, **d2.MAYAN_GRAND2, **d3.MAYAN_GRAND3)
NETHER = dict(NETHER, **d2.NETHER2, **d3.NETHER3)
END = dict(END, **d2.END2, **d3.END3)
DEFAULT_GRAND_EXTRA = dict(d3.DEFAULT_GRAND3)

VERSION = "1.19.3"
NS = "waystone_ruins"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.path.join(ROOT, "stage")
DIST = os.path.join(ROOT, "dist")

SATELLITE_THEMES = ["default", "mossy", "sandy", "frozen", "red",
                    "egyptian", "greek", "babylon", "viking", "mayan", "cherry"]

SILHOUETTE_VARIANTS = set(SMALL) | {"stoa", "nymphaeum"}

# design name -> school, for the Five Schools advancement
SCHOOL_DESIGNS = {
    "egyptian": ["pylon_gate", "obelisk_avenue", "mastaba",
                 "sphinx_avenue", "hypostyle_hall", "sun_court",
                 "temple_of_ra", "nomarch_tomb", "scribe_house"],
    "greek": ["stoa", "tholos", "amphitheater",
              "odeon", "spring_house", "temple_of_the_way",
              "sanctuary_of_echoes", "wine_villa", "nymphaeum"],
    "babylon": ["processional_gate", "terraced_garden", "ziggurat",
                "tablet_house", "ishtar_gate", "hanging_terrace",
                "temple_of_marduk", "merchant_karum", "underworld_gate"],
    "viking": ["runestones", "stone_ship", "mead_hall",
               "boat_grave_field", "stave_shrine", "jarl_barrow",
               "turf_longhouse", "seer_hut", "drakkar_shed",
               # Celtic half of the Norse & Celtic school (v1.11)
               "henge", "dolmen", "holy_well", "broch", "passage_tomb", "roundhouse"],
    "mayan": ["jungle_altar", "step_temple", "overgrown_court",
              "sacbe_gate", "observatory", "cenote_shrine",
              "serpent_pyramid", "jungle_palace", "chultun_house"],
}
DESIGN_SCHOOL = {d: s for s, ds in SCHOOL_DESIGNS.items() for d in ds}

# name: designs, theme, spacing, separation, salt, exclusion, kind, cave height range
# v1.8: spacing cut ~30% across the board per Justin ("make these more common")
SETS = {
    # wine_villa stays registered (worlds reference it) but left generation
    # at Justin's request (v1.16, 2026-09-18)
    "small_default":       dict(designs=SMALL_WITH_BARROW, theme="default", spacing=20, sep=10, salt=918273645, excl=("minecraft:villages", 4), kind="surface", extras=[(GREEK_SMALL, "greek")], exclude_from_set=["wine_villa"]),
    "small_mossy":         dict(designs=SMALL, theme="mossy",   spacing=20, sep=10, salt=918273646, excl=("minecraft:villages", 4), kind="surface", extras=[(MAYAN_SMALL, "mayan")]),
    "small_sandy":         dict(designs=SMALL, theme="sandy",   spacing=20, sep=10, salt=918273647, excl=("minecraft:villages", 4), kind="surface", extras=[(EGYPT_SMALL, "egyptian")]),
    "small_frozen":        dict(designs=SMALL_WITH_BARROW, theme="frozen",  spacing=20, sep=10, salt=918273648, excl=("minecraft:villages", 4), kind="surface", extras=[(VIKING_SMALL, "viking")]),
    "small_red":           dict(designs=SMALL, theme="red",     spacing=20, sep=10, salt=918273649, excl=("minecraft:villages", 4), kind="surface", extras=[(BABYLON_SMALL, "babylon")]),
    "small_cherry":        dict(designs=SMALL, theme="cherry",  spacing=20, sep=10, salt=918273650, excl=("minecraft:villages", 4), kind="surface"),
    # waybuilder_workshop stays registered (worlds reference it) but left generation
    # at Justin's request (v1.19.2, 2026-10-08: "it is bad")
    "grand_default":       dict(designs=GRAND, theme="default", spacing=32, sep=16, salt=564738291, excl=("minecraft:villages", 6), kind="surface", size=2, extras=[(GREEK_GRAND, "greek"), (DEFAULT_GRAND_EXTRA, "default")], exclude_from_set=["waybuilder_workshop"]),
    "grand_mossy":         dict(designs=GRAND, theme="mossy",   spacing=32, sep=16, salt=564738292, excl=("minecraft:villages", 6), kind="surface", size=2, extras=[(MAYAN_GRAND, "mayan")]),
    "grand_sandy":         dict(designs=GRAND, theme="sandy",   spacing=32, sep=16, salt=564738293, excl=("minecraft:villages", 6), kind="surface", size=2, extras=[(EGYPT_GRAND, "egyptian")]),
    # drakkar_shed likewise retained but out of generation (v1.16)
    "grand_frozen":        dict(designs=GRAND, theme="frozen",  spacing=32, sep=16, salt=564738294, excl=("minecraft:villages", 6), kind="surface", size=2, extras=[(VIKING_GRAND, "viking")], exclude_from_set=["drakkar_shed"]),
    # step_pyramid stays registered (existing worlds reference it) but no longer
    # spawns in badlands — the ziggurat owns that silhouette there
    "grand_red":           dict(designs=GRAND, theme="red",     spacing=32, sep=16, salt=564738295, excl=("minecraft:villages", 6), kind="surface", size=2, extras=[(BABYLON_GRAND, "babylon")], exclude_from_set=["step_pyramid"]),
    "grand_cherry":        dict(designs=CHERRY_GRAND, theme="cherry", spacing=32, sep=16, salt=564738296, excl=("minecraft:villages", 6), kind="surface", size=2),
    "sunken":              dict(designs=SUNKEN, theme="default", spacing=24, sep=12, salt=675849305, excl=("minecraft:villages", 4), kind="sunken"),
    "underground":         dict(designs=UNDER, theme="deep",      spacing=26, sep=13, salt=192837465, excl=None, kind="cave", heights=(-32, 32)),
    "underground_lush":    dict(designs=UNDER, theme="lush",      spacing=26, sep=13, salt=192837466, excl=None, kind="cave", heights=(-32, 32)),
    "underground_dripstone": dict(designs=UNDER, theme="dripstone", spacing=26, sep=13, salt=192837467, excl=None, kind="cave", heights=(-32, 32)),
    "underground_sculk":   dict(designs=UNDER, theme="sculk",     spacing=26, sep=13, salt=192837468, excl=("minecraft:ancient_cities", 2), kind="cave", heights=(-48, 8)),
    "nether":              dict(designs=NETHER, theme="nether",  spacing=26, sep=13, salt=675849302, excl=None, kind="cave", heights=(40, 75)),
    "end":                 dict(designs=END, theme="end",        spacing=34, sep=17, salt=675849303, excl=None, kind="surface"),
    "drowned":             dict(designs=DROWNED, theme="drowned", spacing=18, sep=9, salt=675849304, excl=None, kind="water"),
    # v1.9 mega-dungeons: rare pilgrimage finds, one design per set. Only these
    # and the origin may hold a monster spawner (see SPAWNER_SETS).
    "mega_sandy":          dict(designs=d4.EGYPT_GRAND4, theme="egyptian", spacing=64, sep=32, salt=777100001, excl=("minecraft:villages", 4), kind="surface"),
    "mega_temperate":      dict(designs=d4.GREEK_GRAND4, theme="greek",    spacing=64, sep=32, salt=777100002, excl=("minecraft:villages", 4), kind="surface"),
    "mega_red":            dict(designs=d4.BABYLON_GRAND4, theme="babylon", spacing=64, sep=32, salt=777100003, excl=("minecraft:villages", 4), kind="surface"),
    "mega_frozen":         dict(designs=d4.VIKING_GRAND4, theme="viking",  spacing=64, sep=32, salt=777100004, excl=("minecraft:villages", 4), kind="surface"),
    "mega_mossy":          dict(designs=d4.MAYAN_GRAND4, theme="mayan",    spacing=64, sep=32, salt=777100005, excl=("minecraft:villages", 4), kind="surface"),
    "mega_nether":         dict(designs=d4.NETHER4, theme="nether",        spacing=64, sep=32, salt=777100006, excl=None, kind="cave", heights=(40, 70)),
    "mega_end":            dict(designs=d4.END4, theme="end",              spacing=64, sep=32, salt=777100007, excl=None, kind="surface"),
    "origin":              dict(designs={"the_first_waystone": d4.the_first_waystone}, theme="default", spacing=120, sep=60, salt=777100008, excl=("minecraft:villages", 6), kind="surface"),
    "undercroft":          dict(designs={"smugglers_undercroft": d4.smugglers_undercroft}, theme="default", spacing=40, sep=20, salt=777100009, excl=("minecraft:villages", 4), kind="surface"),
}

# v1.17 (Justin, 2026-09-29): "only the biggest structures should have
# spawners". The great dungeons keep theirs; the build refuses a spawner in
# any other template, which is how the Smugglers' Undercroft lost its drowned.
SPAWNER_SETS = {name for name in SETS if name.startswith("mega_")} | {"origin"}


def spawner_count(root):
    return sum(1 for b in root["blocks"] if root["palette"][b["state"]]["Name"] == "minecraft:spawner")


def check_spawners(sid, root, set_name):
    if spawner_count(root) and set_name not in SPAWNER_SETS:
        raise ValueError(f"{sid}: monster spawner outside the great dungeons ({set_name})")


# culture structure tags for the waystone_ruins_names companion: theme -> tag
CULTURE_TAG = {"egyptian": "school_egyptian", "greek": "school_greek",
               "cherry": "school_greek", "babylon": "school_babylon",
               "viking": "school_viking", "mayan": "school_mayan",
               "nether": "theme_nether", "end": "theme_end"}


def opt(tag):
    return {"id": tag, "required": False}


BIOME_TAGS = {
    "default": ["#minecraft:is_forest", "#minecraft:is_taiga", "#minecraft:is_savanna",
                "#minecraft:is_hill", "minecraft:plains", "minecraft:sunflower_plains",
                "minecraft:meadow", "minecraft:stony_shore", "minecraft:stony_peaks",
                opt("#forge:is_plains"), opt("#forge:is_coniferous"),
                opt("#forge:is_dense/overworld"), opt("#forge:is_sparse/overworld"),
                opt("#forge:is_plateau"), opt("#forge:is_mountain")],
    # Waystones 14.1.21 removed its is_swamp/is_mushroom/is_desert biome tags (1.16.1): their 14.1.9 contents are
    # inlined so the placement is identical under any Waystones version.
    "mossy": ["#minecraft:is_jungle", "minecraft:swamp", "minecraft:mangrove_swamp", "minecraft:mushroom_fields",
              opt("#forge:is_swamp"), opt("#forge:is_mushroom")],
    "sandy": ["minecraft:desert",
              opt("#forge:is_desert"), opt("#forge:is_sandy")],
    "frozen": ["minecraft:snowy_plains", "minecraft:ice_spikes", "minecraft:snowy_taiga",
               "minecraft:grove", "minecraft:snowy_slopes", "minecraft:frozen_peaks",
               "minecraft:jagged_peaks", opt("#forge:is_snowy")],
    "red": ["#minecraft:is_badlands"],
    "cherry": ["minecraft:cherry_grove"],
    "underground": ["#minecraft:is_overworld"],
    "lush": ["minecraft:lush_caves", opt("#forge:is_lush")],
    "dripstone": ["minecraft:dripstone_caves"],
    "sculk": ["minecraft:deep_dark"],
    "nether": ["#minecraft:is_nether"],
    "end": ["minecraft:end_highlands", "minecraft:end_midlands"],
    "drowned": ["#minecraft:is_river"],
}

# 1.19.0: biome mods whose own tags put a biome in the wrong school. Atmospheric tags its rainforests only
# #minecraft:is_forest (so they drew the temperate/Greek set) and files Snowy Scrubland under #forge:is_desert
# (the Egyptian sand set). Rainforests and Kousa Jungle are jungles; Snowy Scrubland is a snowy biome.
# All optional: nothing changes when Atmospheric is absent.
ATMOSPHERIC_JUNGLES = ["atmospheric:rainforest", "atmospheric:sparse_rainforest",
                       "atmospheric:rainforest_basin", "atmospheric:sparse_rainforest_basin",
                       "atmospheric:kousa_jungle"]
BIOME_TAGS["mossy"] += [opt(b) for b in ATMOSPHERIC_JUNGLES]
BIOME_TAGS["frozen"] += [opt("atmospheric:snowy_scrubland")]
# Forge's tag loader applies "remove" to the resolved set, so these also leave the nested #minecraft:is_forest
# and #forge:is_desert references. Kousa Jungle was never in the temperate set.
BIOME_TAG_REMOVALS = {
    "default": [opt(b) for b in ATMOSPHERIC_JUNGLES if b != "atmospheric:kousa_jungle"],
    "sandy": [opt("atmospheric:snowy_scrubland")],
}

THEME_TAG = {"default": "default", "mossy": "mossy", "sandy": "sandy",
             "frozen": "frozen", "red": "red", "cherry": "cherry",
             "deep": "underground", "lush": "lush", "dripstone": "dripstone",
             "sculk": "sculk", "nether": "nether", "end": "end",
             "drowned": "drowned",
             "egyptian": "sandy", "greek": "default", "babylon": "red",
             "viking": "frozen", "mayan": "mossy"}

# theme -> [(input_block, [(prob, output_state), ...]), ...]  first match wins
PROCESSORS = {
    "default": [("minecraft:stone_bricks", [(0.15, "minecraft:cracked_stone_bricks"), (0.12, "minecraft:mossy_stone_bricks")]),
                ("minecraft:cobblestone", [(0.18, "minecraft:mossy_cobblestone")]),
                ("minecraft:cobblestone_wall", [(0.10, "minecraft:air"), (0.15, "minecraft:mossy_cobblestone_wall")])],
    "mossy": [("minecraft:stone_bricks", [(0.30, "minecraft:mossy_stone_bricks")]),
              ("minecraft:cobblestone", [(0.30, "minecraft:mossy_cobblestone")]),
              ("minecraft:mossy_stone_bricks", [(0.08, "minecraft:cracked_stone_bricks")])],
    "sandy": [("minecraft:sandstone", [(0.12, "minecraft:cut_sandstone"), (0.08, "minecraft:smooth_sandstone")]),
              ("minecraft:sandstone_wall", [(0.10, "minecraft:air")])],
    "red": [("minecraft:red_sandstone", [(0.12, "minecraft:cut_red_sandstone"), (0.08, "minecraft:smooth_red_sandstone")]),
            ("minecraft:red_sandstone_wall", [(0.10, "minecraft:air")])],
    "cherry": [("minecraft:polished_diorite", [(0.15, "minecraft:diorite")]),
               ("minecraft:calcite", [(0.08, "minecraft:diorite")]),
               ("minecraft:diorite_wall", [(0.10, "minecraft:air")])],
    "deep": [("minecraft:deepslate_bricks", [(0.18, "minecraft:cracked_deepslate_bricks")]),
             ("minecraft:deepslate_tiles", [(0.15, "minecraft:cracked_deepslate_tiles")]),
             ("minecraft:cobbled_deepslate", [(0.12, "minecraft:tuff")])],
    "nether": [("minecraft:polished_blackstone_bricks", [(0.20, "minecraft:cracked_polished_blackstone_bricks")]),
               ("minecraft:blackstone", [(0.10, "minecraft:basalt[axis=y]")])],
    "end": [("minecraft:end_stone_bricks", [(0.12, "minecraft:end_stone")])],
    "drowned": [("minecraft:stone_bricks", [(0.25, "minecraft:mossy_stone_bricks")]),
                ("minecraft:cobblestone", [(0.25, "minecraft:mossy_cobblestone")])],
}
PROCESSORS["egyptian"] = [
    ("minecraft:smooth_sandstone", [(0.15, "minecraft:sandstone"), (0.08, "minecraft:cut_sandstone")]),
    ("minecraft:sandstone_wall", [(0.10, "minecraft:air")]),
    ("minecraft:gold_block", [(0.25, "minecraft:air")]),   # looted long ago
]
PROCESSORS["greek"] = [
    ("minecraft:quartz_block", [(0.12, "minecraft:calcite"), (0.08, "minecraft:diorite")]),
    ("minecraft:smooth_quartz", [(0.12, "minecraft:calcite")]),
    ("minecraft:diorite_wall", [(0.10, "minecraft:air")]),
]
PROCESSORS["babylon"] = [
    ("minecraft:mud_bricks", [(0.15, "minecraft:packed_mud")]),
    ("minecraft:blue_terracotta", [(0.15, "minecraft:cyan_terracotta"), (0.06, "minecraft:terracotta")]),
    ("minecraft:mud_brick_wall", [(0.10, "minecraft:air")]),
]
PROCESSORS["mayan"] = [
    ("minecraft:cobblestone", [(0.30, "minecraft:mossy_cobblestone"), (0.05, "minecraft:moss_block")]),
    ("minecraft:stone_bricks", [(0.25, "minecraft:mossy_stone_bricks")]),
    ("minecraft:mossy_cobblestone_wall", [(0.10, "minecraft:air")]),
]
PROCESSORS["viking"] = [
    ("minecraft:stone_bricks", [(0.15, "minecraft:cracked_stone_bricks"), (0.12, "minecraft:mossy_stone_bricks")]),
    ("minecraft:cobblestone", [(0.15, "minecraft:mossy_cobblestone")]),
    ("minecraft:spruce_planks", [(0.12, "minecraft:air")]),   # rotted timbers
    ("minecraft:cobblestone_wall", [(0.10, "minecraft:air")]),
]
PROCESSORS["frozen"] = PROCESSORS["default"]
PROCESSORS["lush"] = PROCESSORS["deep"] + [("minecraft:cobbled_deepslate", [(0.15, "minecraft:moss_block")])]
PROCESSORS["dripstone"] = PROCESSORS["deep"] + [("minecraft:cobbled_deepslate", [(0.15, "minecraft:dripstone_block")])]
PROCESSORS["sculk"] = PROCESSORS["deep"] + [("minecraft:cobbled_deepslate", [(0.08, "minecraft:sculk")])]

SHERDS = ["angler", "archer", "arms_up", "blade", "danger", "explorer",
          "friend", "heart", "howl", "plenty", "prize", "shelter"]

KNOWN_NAMESPACES = ("minecraft:", "waystones:")


def jw(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2)


def state_obj(state):
    name, props = parse_state(state)
    o = {"Name": name}
    if props:
        o["Properties"] = props
    return o


def processor_json(theme):
    rules = []
    for block, outs in PROCESSORS[theme]:
        for prob, out in outs:
            # Runtime processors cannot see the builder's protected paths,
            # floors or supports. Destructive decay is baked into the NBT;
            # per-placement variation changes materials only.
            if out == "minecraft:air":
                continue
            rules.append({
                "input_predicate": {"predicate_type": "minecraft:random_block_match",
                                    "block": block, "probability": prob},
                "location_predicate": {"predicate_type": "minecraft:always_true"},
                "output_state": state_obj(out),
            })
    return {"processors": [{"processor_type": "minecraft:rule", "rules": rules}]}


def structure_json(sid, tag_key, kind, size=1, heights=None, theme=None, ground=2):
    j = {
        "type": "minecraft:jigsaw",
        "biomes": f"#{NS}:has_ruins/{tag_key}",
        "spawn_overrides": {},
        "start_pool": f"{NS}:{sid}",
        "size": size,
        "max_distance_from_center": 80,
        "use_expansion_hack": False,
    }
    if kind == "surface":
        j["step"] = "surface_structures"
        # Vanilla single-pool elements have groundLevelDelta=1. Their origin
        # is H + offset - 1, where H is the first free height. Put the actual
        # emitted floor at H-1. Beard terrain shaping would instead target
        # the template's buried base, excavating a moat around deep designs.
        j["terrain_adaptation"] = "none"
        j["start_height"] = {"absolute": -ground}
        j["project_start_to_heightmap"] = "WORLD_SURFACE_WG"
    elif kind == "cave":
        j["step"] = "underground_structures"
        if theme == "nether":
            # nether: heightmaps are unusable (they return the ceiling, see
            # KNOWLEDGE 2026-08-25) - keep the absolute band
            lo, hi = heights
            j["start_height"] = {"type": "minecraft:uniform",
                                 "min_inclusive": {"absolute": lo},
                                 "max_inclusive": {"absolute": hi}}
        else:
            # Legacy ocean-safe branch, retained as source data for old builds.
            # Since 2026-09-18 ocean_placement_v2 overrides these 16 definitions
            # with original land ranges and these caps only under surface fluid.
            # Rebuild that overlay after changes here; do not remove it on update.
            # The old blanket float-proof / land-preservation claim below was wrong.
            # overworld caves: CAPPED ABSOLUTE band, no projection (v1.7.1).
            # v1.7.0 used OCEAN_FLOOR_WG offsets -44..-12, but the biome gate
            # is sampled AT THE START Y - surface-relative anchoring made the
            # cave-biome-gated themed sets (lush/dripstone/sculk) sample the
            # SURFACE biome instead and starve. An absolute band keeps the
            # sampling at cave depths (like the original -32..32) while the
            # -16 ceiling sits below the deepest measured seabed (-14), so
            # floating in ocean water stays impossible.
            lo, hi = (-48, -16) if theme == "sculk" else (-44, -16)
            j["start_height"] = {"type": "minecraft:uniform",
                                 "min_inclusive": {"absolute": lo},
                                 "max_inclusive": {"absolute": hi}}
    elif kind == "water":
        j["step"] = "surface_structures"
        j["start_height"] = {"absolute": -2}
        j["project_start_to_heightmap"] = "OCEAN_FLOOR_WG"
    elif kind == "sunken":
        j["step"] = "surface_structures"
        j["start_height"] = {"absolute": -8}
        j["project_start_to_heightmap"] = "WORLD_SURFACE_WG"
    return j


def pool_json(sids, theme, pristine_sid=None, hidden_sid=None):
    """One pool, one element per silhouette variant — picked per placement.
    Pristine copies use no weathering processors. Optional hidden copies have
    25% weight; grand pools retain exactly 5% pristine and 70% normal."""
    elements = [{
        "weight": (14 if pristine_sid else 3) if hidden_sid else (19 if pristine_sid else 1),
        "element": {
            "element_type": "minecraft:single_pool_element",
            "location": f"{NS}:{sid}",
            "processors": f"{NS}:weathering_{theme}",
            "projection": "rigid",
        },
    } for sid in sids]
    if pristine_sid:
        elements.append({
            "weight": len(sids) if hidden_sid else 1,
            "element": {
                "element_type": "minecraft:single_pool_element",
                "location": f"{NS}:{pristine_sid}",
                "processors": "minecraft:empty",
                "projection": "rigid",
            },
        })
    if hidden_sid:
        elements.append({
            "weight": (5 if pristine_sid else 1) * len(sids),
            "element": {
                "element_type": "minecraft:single_pool_element",
                "location": f"{NS}:{hidden_sid}",
                "processors": f"{NS}:weathering_{theme}",
                "projection": "rigid",
            },
        })
    return {"fallback": "minecraft:empty", "elements": elements}


# 1.19.0 site tolerance, in blocks relative to H (the first free height at the start piece's
# centre; the floor lies at H-1). Up to 1.18 every sample had to be within +-1, which few sites
# in the pack's Tectonic terrain meet: Testo64 (341,006 chunks) held 153 surface ruins and no
# Sumerian & Babylonian one. Measured with the pack's terrain of 2026-10-03 (site probe on
# Testo64's seed, builds/waystone_1_19_0/evidence): candidate sites have a median relief of 10 blocks (grand)
# to 14 (small, badlands), so tolerance alone cannot place every design; the band below is the
# widest one the existing footings carry with a sampling margin.
# FOOTING_REACH: two blocks of footing under every ground-contact column hold while the ground
# lies up to three below H (asserted per template). The grid samples every 4 blocks, so the
# accepted drop SITE_DOWN keeps one block in hand for dips between samples, as the old +-1 rule
# kept two. SITE_UP: the ground may rise three above H; that side of the ruin is partly buried.
# Lithostitched's heightmap_relative value is H - height: the permitted range is [-SITE_UP, SITE_DOWN].
FOOTING_REACH = 3
SITE_DOWN = 2
SITE_UP = 3


# 1.19.3 (Justin, 2026-10-09, "Coarser Bons Voyage spawn grid"): fewer height checks per site; sites
# may land on less flat ground. Each grid keeps its radius and both height filters; only the sample
# spacing grows, from 4 to the divisor of the radius nearest to 6 blocks (a tie takes the coarser one)
# but never coarser than radius / 2, so every grid still samples its corners, its edge midpoints and its
# centre plus at least one ring inside the footprint (Lithostitched walks x and z from -radius in steps of
# distance_between_points, codec range 4..1024). Radius 8 keeps 4 (its step 8 left the footprint sampled
# at the centre only and floated a footing in the qualification), 12 -> 6, 16 -> 8, 20 -> 5, 32 -> 8,
# 36 -> 6, 40 -> 5. The FOOTING_REACH margin above was argued for 4-block spacing;
# projects/voyage_grid_1193_20261009 measured the terrain fit at the new spacing.
def site_step(radius):
    steps = [d for d in range(4, radius // 2 + 1) if radius % d == 0]
    return min(steps, key=lambda d: (abs(d - 6), -d))


def safe_drop(root, ground):
    """How far the ground may fall below H before a block of this template floats.

    The floor layer y=ground lands at H-1, so a ground-contact column whose lowest
    structural block is y_low reaches down to H-1-(ground-y_low) and stays supported
    while H - height <= 1 + ground - y_low. Columns whose lowest structural block is
    higher than ground+1 rest on other columns and are skipped.
    """
    from core import structural
    lows = {}
    for blk in root["blocks"]:
        p = root["palette"][blk["state"]]
        state = p["Name"] + ("[" + ",".join(f"{k}={v}" for k, v in p["Properties"].items()) + "]"
                             if p.get("Properties") else "")
        if not structural(state):
            continue
        x, y, z = blk["pos"]
        if y < lows.get((x, z), y + 1):
            lows[(x, z)] = y
    contact = [y for y in lows.values() if y <= ground + 1]
    return min(1 + ground - y for y in contact) if contact else None


def check_support(sid, root, ground):
    drop = safe_drop(root, ground)
    if drop is not None and drop < FOOTING_REACH:
        raise ValueError(f"{sid}: a ground-contact column floats once the ground is {drop + 1} below H; "
                         f"footings must reach {FOOTING_REACH} (site check accepts {SITE_DOWN} plus a sampling margin)")


def site_modifier(sid, ground, size):
    """Require a moderately graded, dry-enough site around the complete root footprint.

    Lithostitched evaluates the generated start before any blocks are placed.
    The stub is H-ground; offset it to H for both heightmap comparisons. The
    grid includes the center and a margin beyond the rotated square bounds.
    Checking the ocean floor too bounds any water under the footprint to the
    same band, so its bed is never deeper than the footings reach.
    """
    half_width = (max(size[0], size[2]) + 1) // 2
    radius = ((half_width + 2 + 3) // 4) * 4
    return {
        "type": "lithostitched:set_structure_spawn_condition",
        "structure": f"{NS}:{sid}",
        "append": True,
        "spawn_condition": {
            "type": "lithostitched:offset", "offset": [0, ground, 0],
            "condition": {
                "type": "lithostitched:grid", "radius": radius,
                "distance_between_points": site_step(radius), "allowed_count": 0,
                "condition": {
                    "type": "lithostitched:not",
                    "condition": {
                        "type": "lithostitched:all_of",
                        "conditions": [
                            {"type": "lithostitched:height_filter",
                             "range_type": "heightmap_relative",
                             "heightmap": heightmap, "permitted_range": [-SITE_UP, SITE_DOWN]}
                            for heightmap in ("WORLD_SURFACE_WG", "OCEAN_FLOOR_WG")
                        ],
                    },
                },
            },
        },
    }


def satellite_pool_json(theme):
    elements = [{"weight": 4, "element": {"element_type": "minecraft:empty_pool_element"}}]
    for name, weight in (("pillar_fall", 2), ("path_frag", 2), ("gate_stub", 1),
                         ("graves", 2), ("campsite", 1), ("toppled_statue", 1)):
        elements.append({
            "weight": weight,
            "element": {
                "element_type": "minecraft:single_pool_element",
                "location": f"{NS}:{name}_{theme}",
                "processors": f"{NS}:settled_{theme}",
                "projection": "rigid",
            },
        })
    return {"fallback": "minecraft:empty", "elements": elements}


SATELLITE_GROUND = 2


def settled_processor_json(theme):
    """1.19.0: weathering plus gravity for the satellites outside a grand ruin's footprint.

    The site check covers the root footprint only, so on a slope a rigid satellite could
    hang in the air or sink into the bank. Gravity places every block at the column's own
    ground height (WORLD_SURFACE_WG during worldgen) + offset + its template y; with the
    floor at template y=SATELLITE_GROUND, offset -(SATELLITE_GROUND+1) puts the floor on
    the top ground block exactly where the rigid placement put it on flat ground, with the
    footings buried below it.
    """
    j = processor_json(theme)
    j["processors"].append({"processor_type": "minecraft:gravity", "heightmap": "WORLD_SURFACE_WG",
                            "offset": -(SATELLITE_GROUND + 1)})
    return j


# Every Waystones 14.1.21 stone block; a concealed site's own stone is one of these.
WAYSTONE_BLOCKS = ["waystones:waystone", "waystones:mossy_waystone", "waystones:sandy_waystone",
                   "waystones:blackstone_waystone", "waystones:deepslate_waystone",
                   "waystones:end_stone_waystone"]


def waystone_use_criterion(sid):
    """Using (right-clicking) the waystone inside structure sid. Vanilla fires item_used_on_block
    for any block use that consumes the action, empty hand included; location_check tests the
    used block itself, so standing on the surface above a buried chamber does not count."""
    return {
        "trigger": "minecraft:item_used_on_block",
        "conditions": {"location": [{
            "condition": "minecraft:location_check",
            "predicate": {"block": {"blocks": WAYSTONE_BLOCKS}, "structure": f"{NS}:{sid}"},
        }]},
    }


def advancement_json(name, ids, icon, title, desc, frame="task", hidden=False, parent=None,
                     concealed=()):
    """Any one criterion: enter one of ids, or use the stone of one of the concealed sites."""
    criteria = {}
    for i, sid in enumerate(sorted(ids)):
        criteria[f"c{i}"] = {
            "trigger": "minecraft:location",
            "conditions": {"player": [{
                "condition": "minecraft:entity_properties", "entity": "this",
                "predicate": {"location": {"structure": f"{NS}:{sid}"}},
            }]},
        }
    for i, sid in enumerate(sorted(concealed)):
        criteria[f"w{i}"] = waystone_use_criterion(sid)
    return {
        "parent": parent or "minecraft:adventure/root",
        "display": {"icon": {"item": icon}, "title": {"text": title},
                    "description": {"text": desc}, "frame": frame,
                    "show_toast": True, "announce_to_chat": True, "hidden": hidden},
        "criteria": criteria,
        "requirements": [list(criteria.keys())],
    }


def advancement_grouped(groups, icon, title, desc, parent, frame="challenge"):
    """AND across groups, OR within each group — visit one ruin per school."""
    criteria = {}
    requirements = []
    for gname, ids in groups.items():
        keys = []
        for i, sid in enumerate(sorted(ids)):
            k = f"{gname}_{i}"
            criteria[k] = {
                "trigger": "minecraft:location",
                "conditions": {"player": [{
                    "condition": "minecraft:entity_properties", "entity": "this",
                    "predicate": {"location": {"structure": f"{NS}:{sid}"}},
                }]},
            }
            keys.append(k)
        requirements.append(keys)
    return {
        "parent": parent,
        "display": {"icon": {"item": icon}, "title": {"text": title},
                    "description": {"text": desc}, "frame": frame,
                    "show_toast": True, "announce_to_chat": True, "hidden": False},
        "criteria": criteria,
        "requirements": requirements,
    }


def loot_json():
    entries = [{"type": "minecraft:item", "name": f"minecraft:{s}_pottery_sherd", "weight": 3}
               for s in SHERDS]
    entries += [
        {"type": "minecraft:item", "name": "minecraft:brick", "weight": 6},
        {"type": "minecraft:item", "name": "minecraft:bone", "weight": 4},
        {"type": "minecraft:item", "name": "minecraft:flint", "weight": 4},
        {"type": "minecraft:item", "name": "minecraft:candle", "weight": 3},
        {"type": "minecraft:item", "name": "minecraft:string", "weight": 3},
        {"type": "minecraft:item", "name": "minecraft:gold_nugget", "weight": 4},
        {"type": "minecraft:item", "name": "minecraft:emerald", "weight": 4},
        {"type": "minecraft:item", "name": "minecraft:gold_ingot", "weight": 3},
        {"type": "minecraft:item", "name": "minecraft:amethyst_shard", "weight": 3},
        {"type": "minecraft:item", "name": "minecraft:lapis_lazuli", "weight": 3},
        {"type": "minecraft:item", "name": "minecraft:diamond", "weight": 1},
        # A plain book: enchant_randomly only makes a usable enchanted book
        # from minecraft:book (see loot.py); v1.1-v1.16 books were duds.
        {"type": "minecraft:item", "name": "minecraft:book", "weight": 1,
         "functions": [{"function": "minecraft:enchant_randomly",
                        "enchantments": ["minecraft:unbreaking", "minecraft:efficiency",
                                         "minecraft:protection", "minecraft:sharpness",
                                         "minecraft:power", "minecraft:feather_falling",
                                         "minecraft:looting", "minecraft:fortune",
                                         "minecraft:silk_touch"]}]},
    ]
    return {"type": "minecraft:archaeology",
            "pools": [{"rolls": 1, "entries": entries}]}


def crypt_loot_json():
    """Chest loot for the v1.8 undergrounds: modest riches, curated books.

    Since v1.17 this is the open-cellar tier; a chest behind any secret uses
    loot.hidden_treasury_json and a great dungeon's deepest vault hoard_json.
    """
    entries = [
        {"type": "minecraft:item", "name": "minecraft:gold_nugget", "weight": 10,
         "functions": [{"function": "minecraft:set_count", "count": {"min": 2, "max": 6}}]},
        {"type": "minecraft:item", "name": "minecraft:bone", "weight": 8,
         "functions": [{"function": "minecraft:set_count", "count": {"min": 1, "max": 4}}]},
        {"type": "minecraft:item", "name": "minecraft:candle", "weight": 6},
        {"type": "minecraft:item", "name": "minecraft:string", "weight": 6},
        {"type": "minecraft:item", "name": "minecraft:gold_ingot", "weight": 6,
         "functions": [{"function": "minecraft:set_count", "count": {"min": 1, "max": 3}}]},
        {"type": "minecraft:item", "name": "minecraft:emerald", "weight": 5,
         "functions": [{"function": "minecraft:set_count", "count": {"min": 1, "max": 3}}]},
        {"type": "minecraft:item", "name": "minecraft:lapis_lazuli", "weight": 5,
         "functions": [{"function": "minecraft:set_count", "count": {"min": 2, "max": 5}}]},
        {"type": "minecraft:item", "name": "minecraft:amethyst_shard", "weight": 4,
         "functions": [{"function": "minecraft:set_count", "count": {"min": 1, "max": 3}}]},
        {"type": "minecraft:item", "name": "minecraft:name_tag", "weight": 2},
        {"type": "minecraft:item", "name": "minecraft:saddle", "weight": 2},
        {"type": "minecraft:item", "name": "minecraft:diamond", "weight": 2},
        {"type": "minecraft:item", "name": "minecraft:golden_apple", "weight": 1},
        {"type": "minecraft:item", "name": "minecraft:book", "weight": 2,
         "functions": [{"function": "minecraft:enchant_randomly",
                        "enchantments": ["minecraft:unbreaking", "minecraft:efficiency",
                                         "minecraft:protection", "minecraft:sharpness",
                                         "minecraft:power", "minecraft:feather_falling",
                                         "minecraft:looting", "minecraft:fortune",
                                         "minecraft:silk_touch"]}]},
    ]
    return {"type": "minecraft:chest",
            "pools": [{"rolls": {"min": 3, "max": 6}, "entries": entries}]}


def validate_nbt(path, sid, expect_waystone=True, max_size=(48, 48, 48)):
    root = read_nbt(path)
    assert root["DataVersion"] == 3465, f"{sid}: bad DataVersion"
    sx, sy, sz = root["size"]
    assert all(0 < n <= limit for n, limit in zip((sx, sy, sz), max_size)), f"{sid}: size {root['size']}"
    for p in root["palette"]:
        assert p["Name"].startswith(KNOWN_NAMESPACES), f"{sid}: bad block {p['Name']}"
    ws_states = {i for i, p in enumerate(root["palette"]) if p["Name"].startswith("waystones:")}
    ws_blocks = [b for b in root["blocks"] if b["state"] in ws_states]
    if not expect_waystone:
        assert not ws_blocks, f"{sid}: satellite should have no waystone"
        return root
    assert len(ws_blocks) == 2, f"{sid}: expected 2 waystone blocks, got {len(ws_blocks)}"
    halves = {}
    for b in ws_blocks:
        assert b.get("nbt", {}).get("id") == "waystones:waystone", f"{sid}: waystone missing block entity"
        halves[root["palette"][b["state"]]["Properties"]["half"]] = b["pos"]
    assert set(halves) == {"lower", "upper"}, f"{sid}: waystone halves {set(halves)}"
    lo, up = halves["lower"], halves["upper"]
    assert up == [lo[0], lo[1] + 1, lo[2]], f"{sid}: waystone halves misaligned"
    return root


def ascii_preview(root, levels=(2, 3, 4)):
    pal = root["palette"]
    grid = {}
    for b in root["blocks"]:
        x, y, z = b["pos"]
        if y not in levels:
            continue
        name = pal[b["state"]]["Name"]
        if "waystones:" in name:
            ch = "W"
        elif name == "minecraft:air":
            ch = " "
        elif "lantern" in name or "end_rod" in name:
            ch = "*"
        elif "suspicious" in name:
            ch = "$"
        elif "jigsaw" in name:
            ch = "J"
        elif "wall" in name or "slab" in name:
            ch = "+"
        elif "chiseled" in name or "purpur" in name:
            ch = "@"
        elif "stairs" in name:
            ch = ">"
        else:
            ch = "#"
        if (x, z) not in grid or ch == "W":
            grid[(x, z)] = ch
        elif grid[(x, z)] != "W":
            grid[(x, z)] = ch
    sx, _, sz = root["size"]
    return "\n".join("".join(grid.get((x, z), " ") for x in range(sx)) for z in range(sz))


def make_logo(path):
    """64x64 pack.png: gray monolith with a glowing rune diamond."""
    import zlib
    import struct as st
    W = H = 64
    px = [[(0, 0, 0, 0)] * W for _ in range(H)]

    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                px[y][x] = c

    stone, dark = (112, 117, 123, 255), (68, 72, 79, 255)
    glow, glow2 = (96, 205, 224, 255), (44, 128, 168, 255)
    rect(18, 50, 45, 57, dark)
    rect(22, 6, 41, 53, stone)
    rect(22, 6, 41, 9, dark)
    for y in range(6, 54):
        px[y][22] = dark
        px[y][41] = dark
    for i in range(8):
        half = i // 2 + 1
        c = glow if i % 2 else glow2
        rect(32 - half, 20 + i, 31 + half, 20 + i, c)
        rect(32 - half, 35 - i, 31 + half, 35 - i, c)

    raw = b""
    for y in range(H):
        raw += b"\x00" + b"".join(st.pack("4B", *c) for c in px[y])

    def chunk(t, d):
        return st.pack(">I", len(d)) + t + d + st.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", st.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def build_template(dname, fn, theme, kind, struct_dir, expect_waystone=True,
                   seed=0, sid=None, pristine=False, hidden=False):
    b = Build(dname, theme, seed=seed, pristine=pristine)
    ground = getattr(fn, "ground", 2)
    b.ground_y = ground if kind in ("surface", "sunken") else None
    fn(b)
    if kind == "surface":
        attach_hidden_room(b, hidden=hidden)
    from exploration import apply as improve_exploration
    improve_exploration(b)
    if kind in ("surface", "sunken") and ground == 2:
        b.underpin()                                   # basement designs self-support
    if kind == "surface":
        from archaeology import reclaim, validate_archaeology
        reclaim(b, ground)
        b.align_satellite_sockets(ground_y=ground)
        b.dress_tops()
        b.clearance(ground_y=ground + 1)
        # 1.19.0: after every RNG-driven step, so designs that already stand on full
        # footings come out byte-identical
        b.footings(ground)
        validate_archaeology(b, ground)
    if kind == "sunken":
        b.erode(0.08)                                  # extra decay for the buried look
    if kind == "cave" and theme == "dripstone":
        b.drip_decor()
    # Gate the final geometry, including intact and alternate pool variants.
    # Omitted underground voxels remain terrain in this audit, so an absent
    # corridor cannot accidentally count as an open connection. Intentional
    # buried/cave templates without authored room metadata retain their own
    # discovery rules instead of being treated as surface entrances.
    if expect_waystone and (kind == "surface" or (kind == "cave" and getattr(b, "rooms", ()))):
        from audit_access import audit_build
        audit = audit_build(b, ground=ground, surface=kind == "surface")
        if audit["issues"]:
            raise ValueError(f"{dname}/{theme}: access validation failed: " + "; ".join(audit["issues"]))
    sid = sid or f"{dname}_{theme}"
    size, npal, nblocks = b.emit(os.path.join(struct_dir, f"{sid}.nbt"))
    root = validate_nbt(os.path.join(struct_dir, f"{sid}.nbt"), sid, expect_waystone)
    # emit translates ALL axes to zero, including designs with cellars below
    # y=0 and deep designs whose lowest room begins at y=2 or y=3.
    # This build-only metadata is not written into the structure NBT.
    root["_ground_level"] = ground - b.emitted_origin[1]
    if kind == "surface" and expect_waystone:       # satellites settle column by column instead
        check_support(sid, root, root["_ground_level"])
    return sid, root, (size, npal, nblocks)


def main():
    # Only this project's generated staging tree may be removed on rebuild.
    from pathlib import Path
    if Path(STAGE).resolve() != Path(ROOT).resolve() / "stage":
        raise ValueError("refusing to clear a staging directory outside the project")
    if os.path.isdir(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(DIST, exist_ok=True)
    data = os.path.join(STAGE, "data", NS)
    struct_dir = os.path.join(data, "structures")
    os.makedirs(struct_dir, exist_ok=True)

    all_ids = []
    grand_ids, under_ids, far_ids, mega_ids = [], [], [], []
    concealed_ids = []   # selected sites whose waystone lies in the buried chamber (role "hidden")
    culture_tag_ids = {}
    school_ids = {s: [] for s in SCHOOL_DESIGNS}
    preview_lines = []
    summary = []
    previewed_designs = set()

    for set_name, cfg in SETS.items():
        entries = []
        groups = [(cfg["designs"], cfg["theme"])] + list(cfg.get("extras", []))
        for gi, (designs, theme) in enumerate(groups):
            # base designs of grand sets carry weight 2 so the regional schools
            # stay the minority style (~20% instead of a third)
            weight = 2 if set_name.startswith("grand") and gi == 0 else 1
            for dname, fn in designs.items():
                sid, root, stats = build_template(dname, fn, theme, cfg["kind"], struct_dir)
                check_spawners(sid, root, set_name)
                if dname not in previewed_designs:
                    previewed_designs.add(dname)
                    preview_lines.append(f"== {sid} (size {stats[0]}) ==\n{ascii_preview(root)}\n")
                summary.append((sid, *stats))
                pool_sids = [sid]
                site_size = list(root["size"])
                pristine_sid = None
                hidden_sid = None
                if set_name.startswith("small_") and dname in SILHOUETTE_VARIANTS:
                    for v in (2, 3):                   # silhouette variants
                        vsid, vroot, vstats = build_template(
                            dname, fn, theme, cfg["kind"], struct_dir, seed=v,
                            sid=f"{sid}_v{v}")
                        check_spawners(vsid, vroot, set_name)
                        pool_sids.append(vsid)
                        summary.append((vsid, *vstats))
                        assert vroot["_ground_level"] == root["_ground_level"], f"{vsid}: variant floor differs"
                        site_size = [max(a, b) for a, b in zip(site_size, vroot["size"])]
                if set_name.startswith("grand"):       # the one the ages forgot
                    pristine_sid = f"{sid}_pristine"
                    _, proot, pstats = build_template(
                        dname, fn, theme, cfg["kind"], struct_dir,
                        sid=pristine_sid, pristine=True)
                    check_spawners(pristine_sid, proot, set_name)
                    summary.append((pristine_sid, *pstats))
                    assert proot["_ground_level"] == root["_ground_level"], f"{sid}: pristine floor differs"
                    site_size = [max(a, b) for a, b in zip(site_size, proot["size"])]
                if dname in HIDDEN_ROOMS and cfg['kind'] == 'surface':
                    hidden_sid = f'{sid}_hidden'
                    _, hroot, hstats = build_template(
                        dname, fn, theme, cfg['kind'], struct_dir,
                        sid=hidden_sid, hidden=True)
                    check_spawners(hidden_sid, hroot, set_name)
                    summary.append((hidden_sid, *hstats))
                    assert hroot['_ground_level'] == root['_ground_level'], f'{sid}: hidden floor differs'
                    site_size = [max(a,b) for a,b in zip(site_size,hroot['size'])]
                jw(os.path.join(data, "worldgen", "template_pool", f"{sid}.json"),
                   pool_json(pool_sids, theme, pristine_sid=pristine_sid, hidden_sid=hidden_sid))
                jw(os.path.join(data, "worldgen", "structure", f"{sid}.json"),
                   structure_json(sid, THEME_TAG[theme], cfg["kind"],
                                  size=cfg.get("size", 1), heights=cfg.get("heights"),
                                  theme=theme, ground=root["_ground_level"]))
                if cfg["kind"] == "surface":
                    jw(os.path.join(data, "lithostitched", "worldgen_modifier",
                                    f"{sid}_site.json"),
                       site_modifier(sid, root["_ground_level"], site_size))
                if theme in CULTURE_TAG:
                    culture_tag_ids.setdefault(CULTURE_TAG[theme], []).append(sid)
                if dname == "the_first_waystone":
                    culture_tag_ids.setdefault("the_origin", []).append(sid)
                if dname not in cfg.get("exclude_from_set", ()):
                    entries.append({"structure": f"{NS}:{sid}", "weight": weight})
                all_ids.append(sid)
                if set_name.startswith("grand"):
                    grand_ids.append(sid)
                if set_name.startswith("mega_") or set_name == "origin":
                    mega_ids.append(sid)
                if cfg["kind"] == "cave" and theme != "nether":
                    under_ids.append(sid)
                if theme in ("nether", "end"):
                    far_ids.append(sid)
                if dname in DESIGN_SCHOOL:
                    school_ids[DESIGN_SCHOOL[dname]].append(sid)
        placement = {"type": "minecraft:random_spread",
                     "spacing": cfg["spacing"], "separation": cfg["sep"], "salt": cfg["salt"]}
        if cfg["excl"]:
            placement["exclusion_zone"] = {"other_set": cfg["excl"][0],
                                           "chunk_count": cfg["excl"][1]}
        jw(os.path.join(data, "worldgen", "structure_set", f"{set_name}.json"),
           {"structures": entries, "placement": placement})

    # Approved layouts already contain their final archaeology and clearance.
    # Register them in existing regional sets without changing their spacing.
    from selected_structures import SELECTION, EXPANSIONS, build_selected, record_loot, nether_site_modifier
    selected_manifest = []
    for row in SELECTION:
        b = build_selected(row)
        if row['theme'] != 'nether':        # Nether sites keep their density check
            b.footings(2)                   # 1.19.0, see Build.footings
        from audit_access import audit_build
        audit = audit_build(b)
        if audit['issues']:
            raise ValueError(f"{row['sid']}: " + '; '.join(audit['issues']))
        sid, theme = row['sid'], row['theme']
        stats = b.emit(os.path.join(struct_dir, sid + '.nbt'))
        root = validate_nbt(os.path.join(struct_dir, sid + '.nbt'), sid, max_size=(80, 48, 80))
        check_spawners(sid, root, row['set'])
        ground = 2 - b.emitted_origin[1]
        if theme != 'nether':
            check_support(sid, root, ground)
        cfg = SETS[row['set']]
        # Vanilla 1.20.1 emits no pieces at size=0, including the root itself.
        # A single root without sockets needs size=1.
        structure = structure_json(sid, THEME_TAG[theme], cfg['kind'], size=1,
                                   heights=(35-ground+1, 88-ground+1) if theme=='nether' else None,
                                   theme=theme, ground=ground)
        if theme=='nether':
            structure['terrain_adaptation'] = 'none'
            modifier = nether_site_modifier(sid, ground, root['size'])
        else:
            modifier = site_modifier(sid, ground, root['size'])
        jw(os.path.join(data, 'worldgen', 'structure', sid+'.json'), structure)
        # All deterioration is authored. No random processor can erase a clue.
        jw(os.path.join(data, 'worldgen', 'template_pool', sid+'.json'), {
            'fallback':'minecraft:empty', 'elements':[{'weight':1,'element':{
                'element_type':'minecraft:single_pool_element','location':f'{NS}:{sid}',
                'processors':'minecraft:empty','projection':'rigid'}}]})
        jw(os.path.join(data, 'lithostitched', 'worldgen_modifier', sid+'_site.json'), modifier)
        set_path = os.path.join(data, 'worldgen', 'structure_set', row['set']+'.json')
        with open(set_path, encoding='utf-8') as f:
            structure_set = json.load(f)
        structure_set['structures'].append({'structure':f'{NS}:{sid}','weight':1})
        jw(set_path, structure_set)
        all_ids.append(sid);summary.append((sid,*stats))
        if row['set'].startswith('grand_'):grand_ids.append(sid)
        if row['set'].startswith('mega_'):mega_ids.append(sid)
        # 1.19.0: entering a concealed site's surface used to grant What Sleeps Beneath; now its
        # buried stone has to be reached and used.
        if row['role']=='hidden':concealed_ids.append(sid)
        if theme in ('nether','end'):far_ids.append(sid)
        if theme in CULTURE_TAG:culture_tag_ids.setdefault(CULTURE_TAG[theme],[]).append(sid)
        if theme in school_ids:school_ids[theme].append(sid)
        if row['id'] in EXPANSIONS:
            jw(os.path.join(data,'loot_tables','chests',f"selected_{row['id']}_records.json"),record_loot(row['id']))
        selected_manifest.append(dict(row, emittedOrigin=b.emitted_origin, emittedSize=root['size'],
                                      groundLevel=ground, addedRooms=b.added_rooms,
                                      additionalSecrets=b.additional_secrets, caches=b.cache_positions))
    jw(os.path.join(ROOT, 'selected_release.json'), {'version':VERSION,'structures':selected_manifest})

    # 1.19.1 (Justin 2026-10-06: eight Bons Voyage waystones in one field, some side by side): the sets above
    # are independent placement grids. Every set keeps its grid but gets a claim (claims_data.py, rule in
    # src/.../waystoneruins/claims): a candidate is refused when a higher-ranked set of the same realm
    # generates within the claim radius.
    from claims_data import apply as apply_claims
    set_dir = os.path.join(data, 'worldgen', 'structure_set')
    per_set = {f[:-5]: json.load(open(os.path.join(set_dir, f), encoding='utf-8'))
               for f in sorted(os.listdir(set_dir))}
    for name, doc in apply_claims(per_set).items():
        jw(os.path.join(set_dir, f'{name}.json'), doc)

    # satellite templates + pools (no structure/set of their own)
    for theme in SATELLITE_THEMES:
        for dname, fn in SATELLITES.items():
            sid, root, stats = build_template(dname, fn, theme, "surface", struct_dir,
                                              expect_waystone=False)
            check_spawners(sid, root, "satellites")
            assert root["_ground_level"] == SATELLITE_GROUND, f"{sid}: settled offset assumes floor y={SATELLITE_GROUND}"
            summary.append((sid, *stats))
            if dname not in previewed_designs:
                previewed_designs.add(dname)
                preview_lines.append(f"== {sid} (size {stats[0]}) ==\n{ascii_preview(root)}\n")
        jw(os.path.join(data, "worldgen", "template_pool", f"satellites_{theme}.json"),
           satellite_pool_json(theme))
        jw(os.path.join(data, "worldgen", "processor_list", f"settled_{theme}.json"),
           settled_processor_json(theme))

    for theme in sorted(PROCESSORS):
        jw(os.path.join(data, "worldgen", "processor_list", f"weathering_{theme}.json"),
           processor_json(theme))

    for key, values in BIOME_TAGS.items():
        body = {"replace": False, "values": values}
        if key in BIOME_TAG_REMOVALS:
            body["remove"] = BIOME_TAG_REMOVALS[key]
        jw(os.path.join(data, "tags", "worldgen", "biome", "has_ruins", f"{key}.json"), body)

    # 1.16.2 (structure review 2026-09-28): Waystones 14.1.21 attaches its wild waystones through
    # #waystones:has_structure/* tags that list vanilla biomes only; add the pack's modded biomes, every entry
    # optional. Lists come from builds/waystone_1_16_2/biome_lists.py (re-run it after biome mods change).
    wild = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wild_waystone_biomes.json"),
                          encoding="utf-8"))["lists"]
    for variant, ids in wild.items():
        jw(os.path.join(STAGE, "data", "waystones", "tags", "worldgen", "biome", "has_structure", f"{variant}.json"),
           {"replace": False, "values": [opt(b) for b in ids]})

    jw(os.path.join(data, "loot_tables", "archaeology", "ruins.json"), loot_json())
    jw(os.path.join(data, "loot_tables", "chests", "crypt.json"), crypt_loot_json())
    jw(os.path.join(data, "loot_tables", "chests", "curiosity_cache.json"), curiosity_loot_json())
    jw(os.path.join(data, "loot_tables", "chests", "hidden_treasury.json"), hidden_treasury_json())
    jw(os.path.join(data, "loot_tables", "chests", "waybuilder_hoard.json"), hoard_json())

    # culture structure tags for the waystone_ruins_names companion mod
    for tag, ids in culture_tag_ids.items():
        jw(os.path.join(data, "tags", "worldgen", "structure", f"{tag}.json"),
           {"replace": False, "values": [f"{NS}:{sid}" for sid in sorted(set(ids))]})

    adv_dir = os.path.join(data, "advancements")
    jw(os.path.join(adv_dir, "traces.json"), advancement_json(
        "traces", all_ids, "minecraft:mossy_cobblestone", "Traces of the Waybuilders",
        "Discover a ruin of the civilization that raised the waystones"))
    jw(os.path.join(adv_dir, "houses_of_the_way.json"), advancement_json(
        "houses_of_the_way", grand_ids, "minecraft:chiseled_stone_bricks",
        "Houses of the Way", "Find a great temple of the Waybuilders",
        frame="goal", parent=f"{NS}:traces"))
    jw(os.path.join(adv_dir, "beneath.json"), advancement_json(
        "beneath", under_ids, "minecraft:soul_lantern", "What Sleeps Beneath",
        "Unearth a buried crypt of the Waybuilders", frame="goal",
        parent=f"{NS}:traces", concealed=concealed_ids))
    # 1.19.0: one group per school from the same school tags the naming uses, so each school's
    # great dungeon and the Greek school's cherry ruins count (the design-name list missed them).
    school_groups = {s: sorted(set(culture_tag_ids[f"school_{s}"])) for s in SCHOOL_DESIGNS}
    for s, ids in school_ids.items():
        assert set(ids) <= set(school_groups[s]), f"{s}: school tag lost a counted ruin"
    jw(os.path.join(adv_dir, "five_schools.json"), advancement_grouped(
        school_groups, "waystones:waystone", "The Five Schools",
        "Visit all five schools: Benben, Herma, Kudurru, Varða and Sacbe",
        parent=f"{NS}:traces"))
    jw(os.path.join(adv_dir, "far_from_home.json"), advancement_json(
        "far_from_home", far_ids, "minecraft:crying_obsidian", "Far From Home",
        "The Waybuilders walked other worlds before the end", frame="challenge",
        hidden=True, parent=f"{NS}:traces"))
    jw(os.path.join(adv_dir, "the_deep_places.json"), advancement_json(
        "the_deep_places", mega_ids, "minecraft:spawner", "The Deep Places",
        "Descend into a great dungeon of the Waybuilders", frame="goal",
        parent=f"{NS}:traces"))
    jw(os.path.join(adv_dir, "the_origin.json"), advancement_json(
        "the_origin", ["the_first_waystone_default"], "waystones:waystone",
        "Where the Way Began", "Stand before the First Waystone",
        frame="challenge", hidden=True, parent=f"{NS}:the_deep_places"))

    jw(os.path.join(STAGE, "pack.mcmeta"),
       {"pack": {"pack_format": 15,
                 "description": "Waystone Ruins - relics of the civilization that raised the waystones"}})

    os.makedirs(os.path.join(STAGE, "META-INF"), exist_ok=True)
    with open(os.path.join(STAGE, "META-INF", "mods.toml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f'''modLoader="lowcodefml"
loaderVersion="[1,)"
license="MIT"

[[mods]]
modId="{NS}"
version="{VERSION}"
displayName="Waystone Ruins"
authors="Justin, Claude"
description="Stone pedestals, shrines and temples of a lost civilization, built to house waystones. Data-only worldgen mod."
displayTest="IGNORE_ALL_VERSION"
logoFile="pack.png"

[[dependencies.{NS}]]
modId="waystones"
mandatory=true
versionRange="[14,)"
ordering="AFTER"
side="BOTH"

[[dependencies.{NS}]]
modId="lithostitched"
mandatory=true
versionRange="[1.4.11,)"
ordering="AFTER"
side="BOTH"

[[dependencies.{NS}]]
modId="minecraft"
mandatory=true
versionRange="[1.20,1.21)"
ordering="NONE"
side="BOTH"

[[dependencies.{NS}]]
modId="forge"
mandatory=true
versionRange="[47,)"
ordering="NONE"
side="BOTH"
''')
    with open(os.path.join(STAGE, "META-INF", "MANIFEST.MF"), "w", encoding="utf-8", newline="\n") as f:
        f.write("Manifest-Version: 1.0\n")
    make_logo(os.path.join(STAGE, "pack.png"))

    # ---- cross-reference validation
    pools = {f[:-5] for f in os.listdir(os.path.join(data, "worldgen", "template_pool"))}
    structs = {f[:-5] for f in os.listdir(os.path.join(data, "worldgen", "structure"))}
    nbts = {f[:-4] for f in os.listdir(struct_dir)}
    tags = {f[:-5] for f in os.listdir(os.path.join(data, "tags", "worldgen", "biome", "has_ruins"))}
    procs = {f[:-5] for f in os.listdir(os.path.join(data, "worldgen", "processor_list"))}
    for sid in all_ids:
        assert sid in pools and sid in structs and sid in nbts, f"missing files for {sid}"
    for f in os.listdir(os.path.join(data, "worldgen", "structure")):
        j = json.load(open(os.path.join(data, "worldgen", "structure", f)))
        assert j["start_pool"].split(":", 1)[1] in pools, f"{f}: dangling start_pool"
        assert j["biomes"].split("/")[-1] in tags, f"{f}: dangling biome tag"
    for f in os.listdir(os.path.join(data, "worldgen", "template_pool")):
        j = json.load(open(os.path.join(data, "worldgen", "template_pool", f)))
        for e in j["elements"]:
            el = e["element"]
            if el["element_type"] != "minecraft:single_pool_element":
                continue
            assert el["location"].split(":", 1)[1] in nbts, f"{f}: dangling template"
            if not el["processors"].startswith("minecraft:"):
                assert el["processors"].split(":", 1)[1] in procs, f"{f}: dangling processors"
    for f in os.listdir(os.path.join(data, "worldgen", "structure_set")):
        j = json.load(open(os.path.join(data, "worldgen", "structure_set", f)))
        for e in j["structures"]:
            assert e["structure"].split(":", 1)[1] in structs, f"{f}: dangling structure ref"
    # every jigsaw socket's pool and every container's loot table must exist
    loot_dir = os.path.join(data, "loot_tables")
    for sid in nbts:
        root = read_nbt(os.path.join(struct_dir, f"{sid}.nbt"))
        for blk in root["blocks"]:
            nbt = blk.get("nbt") or {}
            if nbt.get("id") == "minecraft:jigsaw" and nbt["pool"].startswith(NS + ":"):
                assert nbt["pool"].split(":", 1)[1] in pools, f"{sid}: dangling jigsaw pool {nbt['pool']}"
            table = nbt.get("LootTable")
            if table:
                ns, rel = table.split(":", 1)
                assert ns == NS and os.path.isfile(os.path.join(loot_dir, rel + ".json")), \
                    f"{sid}: dangling loot table {table}"

    with open(os.path.join(ROOT, "preview.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(preview_lines))

    # Data-only intermediate; build_release.py combines it with the naming class
    # into dist/{NS}-{VERSION}.jar, so the two must never share a file name.
    jar_path = os.path.join(DIST, f"{NS}-{VERSION}-data.jar")
    if os.path.exists(jar_path):
        from datetime import datetime
        archive = os.path.join(DIST, 'previous_builds')
        os.makedirs(archive, exist_ok=True)
        shutil.move(jar_path, os.path.join(archive, f"{NS}-{VERSION}-{datetime.now():%Y%m%d-%H%M%S-%f}.jar.disabled"))
    with zipfile.ZipFile(jar_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(STAGE):
            for fn in sorted(files):
                full = os.path.join(dirpath, fn)
                arc = os.path.relpath(full, STAGE).replace(os.sep, "/")
                z.write(full, arc)

    print(f"OK: {len(all_ids)} structures + {len(SATELLITE_THEMES) * len(SATELLITES)} satellites, "
          f"{len(SETS)} structure sets, {len(PROCESSORS)} processor lists")
    for sid, size, npal, nblocks in summary:
        print(f"  {sid:32s} size={size} palette={npal} blocks={nblocks}")
    print(f"jar: {jar_path} ({os.path.getsize(jar_path)} bytes)")


if __name__ == "__main__":
    main()
