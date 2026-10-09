"""Voxel builder + biome theme palettes for Waystone Ruins structure templates."""
import random
from nbt import write_nbt

DATA_VERSION = 3465  # 1.20.1

# 1.19.0: blocks that bear load or form the ruin's body. Everything else (plants, carpets,
# snow layers, torches, lanterns, pots...) merely rests on whatever is below it and never
# gets footings of its own. Shared by Build.footings and build.py's support check.
_NOT_STRUCTURAL = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:structure_void",
                   "minecraft:light", "minecraft:jigsaw"}
_DECOR = ("vine", "carpet", "torch", "lantern", "button", "pressure_plate", "lever", "flower_pot", "candle",
          "snow[", ":snow", "grass", "fern", "flower", "dandelion", "poppy", "orchid", "allium", "azure_bluet",
          "tulip", "oxeye", "cornflower", "lily_of_the_valley", "wither_rose", "sapling", "dead_bush",
          "mushroom[", "brown_mushroom", "red_mushroom", "sweet_berry", "glow_lichen", "sculk_vein", "cobweb",
          "tripwire", "rail", "sign", "banner", "head", "skull", "ladder", "lichen", "petals", "sea_pickle",
          "seagrass", "kelp", "lily_pad", "spore_blossom", "hanging_roots", "moss_carpet", "pointed_dripstone",
          "amethyst_cluster", "bud", "chain", "end_rod", "bell", "scaffolding", "redstone_wire", "decorated_pot")


def structural(state):
    name = state.split("[", 1)[0]
    if name in _NOT_STRUCTURAL:
        return False
    if name in ("minecraft:grass_block", "minecraft:mushroom_stem", "minecraft:brown_mushroom_block",
                "minecraft:red_mushroom_block", "minecraft:snow_block", "minecraft:moss_block",
                "minecraft:mud_bricks", "minecraft:packed_mud", "minecraft:sea_lantern",
                "minecraft:jack_o_lantern"):
        return True
    return not any(d in name for d in _DECOR)

# ---------------------------------------------------------------- themes
# Each role maps to either a blockstate string or a weighted list [(state, w), ...].
# Blockstate strings: "minecraft:stone_bricks" or "ns:block[k=v,k2=v2]".

def _w(*pairs):
    return list(pairs)

THEMES = {
    "default": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:stone_bricks", 6), ("minecraft:cracked_stone_bricks", 2), ("minecraft:mossy_stone_bricks", 2)),
        "cobble": _w(("minecraft:cobblestone", 7), ("minecraft:mossy_cobblestone", 3)),
        "floor": _w(("minecraft:stone_bricks", 4), ("minecraft:cracked_stone_bricks", 2), ("minecraft:cobblestone", 3), ("minecraft:andesite", 1)),
        "chiseled": "minecraft:chiseled_stone_bricks",
        "accent": "minecraft:polished_andesite",
        "stairs": "minecraft:stone_brick_stairs",
        "slab": "minecraft:stone_brick_slab",
        "cobble_slab": "minecraft:cobblestone_slab",
        "wall": _w(("minecraft:cobblestone_wall", 6), ("minecraft:mossy_cobblestone_wall", 4)),
        "brick_wall": "minecraft:stone_brick_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "mossy": {
        "waystone": "waystones:mossy_waystone",
        "brick": _w(("minecraft:mossy_stone_bricks", 6), ("minecraft:stone_bricks", 2), ("minecraft:cracked_stone_bricks", 2)),
        "cobble": _w(("minecraft:mossy_cobblestone", 7), ("minecraft:cobblestone", 3)),
        "floor": _w(("minecraft:mossy_stone_bricks", 4), ("minecraft:mossy_cobblestone", 3), ("minecraft:moss_block", 2), ("minecraft:cracked_stone_bricks", 1)),
        "chiseled": "minecraft:chiseled_stone_bricks",
        "accent": "minecraft:moss_block",
        "stairs": "minecraft:mossy_stone_brick_stairs",
        "slab": "minecraft:mossy_stone_brick_slab",
        "cobble_slab": "minecraft:mossy_cobblestone_slab",
        "wall": _w(("minecraft:mossy_cobblestone_wall", 7), ("minecraft:cobblestone_wall", 3)),
        "brick_wall": "minecraft:mossy_stone_brick_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "sandy": {
        "waystone": "waystones:sandy_waystone",
        "brick": _w(("minecraft:sandstone", 5), ("minecraft:cut_sandstone", 3), ("minecraft:smooth_sandstone", 2)),
        "cobble": _w(("minecraft:sandstone", 6), ("minecraft:cut_sandstone", 4)),
        "floor": _w(("minecraft:sandstone", 4), ("minecraft:cut_sandstone", 3), ("minecraft:smooth_sandstone", 2), ("minecraft:sand", 1)),
        "chiseled": "minecraft:chiseled_sandstone",
        "accent": "minecraft:smooth_sandstone",
        "stairs": "minecraft:sandstone_stairs",
        "slab": "minecraft:sandstone_slab",
        "cobble_slab": "minecraft:sandstone_slab",
        "wall": "minecraft:sandstone_wall",
        "brick_wall": "minecraft:sandstone_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "frozen": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:stone_bricks", 6), ("minecraft:cracked_stone_bricks", 3), ("minecraft:mossy_stone_bricks", 1)),
        "cobble": _w(("minecraft:cobblestone", 8), ("minecraft:mossy_cobblestone", 2)),
        "floor": _w(("minecraft:stone_bricks", 4), ("minecraft:cracked_stone_bricks", 2), ("minecraft:cobblestone", 3), ("minecraft:packed_ice", 1)),
        "chiseled": "minecraft:chiseled_stone_bricks",
        "accent": "minecraft:packed_ice",
        "stairs": "minecraft:stone_brick_stairs",
        "slab": "minecraft:stone_brick_slab",
        "cobble_slab": "minecraft:cobblestone_slab",
        "wall": "minecraft:cobblestone_wall",
        "brick_wall": "minecraft:stone_brick_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": "minecraft:snow[layers=1]",
    },
    "deep": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:deepslate_bricks", 5), ("minecraft:cracked_deepslate_bricks", 3), ("minecraft:deepslate_tiles", 2)),
        "cobble": _w(("minecraft:cobbled_deepslate", 7), ("minecraft:tuff", 3)),
        "floor": _w(("minecraft:deepslate_tiles", 3), ("minecraft:cracked_deepslate_tiles", 2), ("minecraft:cobbled_deepslate", 3), ("minecraft:tuff", 2)),
        "chiseled": "minecraft:chiseled_deepslate",
        "accent": "minecraft:polished_deepslate",
        "stairs": "minecraft:deepslate_brick_stairs",
        "slab": "minecraft:deepslate_brick_slab",
        "cobble_slab": "minecraft:cobbled_deepslate_slab",
        "wall": "minecraft:cobbled_deepslate_wall",
        "brick_wall": "minecraft:deepslate_brick_wall",
        "light": "minecraft:soul_lantern[hanging=false]",
        "hanging_light": "minecraft:soul_lantern[hanging=true]",
        "top_dress": None,
    },
    "red": {
        "waystone": "waystones:sandy_waystone",
        "brick": _w(("minecraft:red_sandstone", 5), ("minecraft:cut_red_sandstone", 3), ("minecraft:smooth_red_sandstone", 2)),
        "cobble": _w(("minecraft:red_sandstone", 6), ("minecraft:cut_red_sandstone", 4)),
        "floor": _w(("minecraft:red_sandstone", 4), ("minecraft:cut_red_sandstone", 3), ("minecraft:terracotta", 2), ("minecraft:red_sand", 1)),
        "chiseled": "minecraft:chiseled_red_sandstone",
        "accent": "minecraft:smooth_red_sandstone",
        "stairs": "minecraft:red_sandstone_stairs",
        "slab": "minecraft:red_sandstone_slab",
        "cobble_slab": "minecraft:red_sandstone_slab",
        "wall": "minecraft:red_sandstone_wall",
        "brick_wall": "minecraft:red_sandstone_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "cherry": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:polished_diorite", 4), ("minecraft:calcite", 4), ("minecraft:diorite", 2)),
        "cobble": _w(("minecraft:diorite", 6), ("minecraft:calcite", 4)),
        "floor": _w(("minecraft:calcite", 4), ("minecraft:polished_diorite", 3), ("minecraft:diorite", 3)),
        "chiseled": "minecraft:chiseled_quartz_block",
        "accent": "minecraft:calcite",
        "pillar": "minecraft:quartz_pillar[axis=y]",
        "stairs": "minecraft:polished_diorite_stairs",
        "slab": "minecraft:polished_diorite_slab",
        "cobble_slab": "minecraft:polished_diorite_slab",
        "wall": "minecraft:diorite_wall",
        "brick_wall": "minecraft:diorite_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "lush": {
        "waystone": "waystones:mossy_waystone",
        "brick": _w(("minecraft:deepslate_bricks", 4), ("minecraft:moss_block", 3), ("minecraft:cracked_deepslate_bricks", 3)),
        "cobble": _w(("minecraft:cobbled_deepslate", 5), ("minecraft:moss_block", 5)),
        "floor": _w(("minecraft:moss_block", 4), ("minecraft:deepslate_tiles", 2), ("minecraft:cobbled_deepslate", 4)),
        "chiseled": "minecraft:chiseled_deepslate",
        "accent": "minecraft:moss_block",
        "stairs": "minecraft:deepslate_brick_stairs",
        "slab": "minecraft:deepslate_brick_slab",
        "cobble_slab": "minecraft:cobbled_deepslate_slab",
        "wall": "minecraft:cobbled_deepslate_wall",
        "brick_wall": "minecraft:deepslate_brick_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "dripstone": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:deepslate_bricks", 4), ("minecraft:dripstone_block", 3), ("minecraft:cracked_deepslate_bricks", 3)),
        "cobble": _w(("minecraft:cobbled_deepslate", 4), ("minecraft:dripstone_block", 4), ("minecraft:tuff", 2)),
        "floor": _w(("minecraft:dripstone_block", 4), ("minecraft:cobbled_deepslate", 3), ("minecraft:tuff", 3)),
        "chiseled": "minecraft:chiseled_deepslate",
        "accent": "minecraft:dripstone_block",
        "stairs": "minecraft:deepslate_brick_stairs",
        "slab": "minecraft:deepslate_brick_slab",
        "cobble_slab": "minecraft:cobbled_deepslate_slab",
        "wall": "minecraft:cobbled_deepslate_wall",
        "brick_wall": "minecraft:deepslate_brick_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "sculk": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:deepslate_bricks", 5), ("minecraft:deepslate_tiles", 3), ("minecraft:cracked_deepslate_bricks", 2)),
        "cobble": _w(("minecraft:cobbled_deepslate", 8), ("minecraft:sculk", 2)),
        "floor": _w(("minecraft:sculk", 3), ("minecraft:deepslate_tiles", 3), ("minecraft:cobbled_deepslate", 4)),
        "chiseled": "minecraft:chiseled_deepslate",
        "accent": "minecraft:sculk",
        "stairs": "minecraft:deepslate_tile_stairs",
        "slab": "minecraft:deepslate_tile_slab",
        "cobble_slab": "minecraft:cobbled_deepslate_slab",
        "wall": "minecraft:deepslate_tile_wall",
        "brick_wall": "minecraft:deepslate_brick_wall",
        "light": "minecraft:soul_lantern[hanging=false]",
        "hanging_light": "minecraft:soul_lantern[hanging=true]",
        "top_dress": None,
    },
    "nether": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:polished_blackstone_bricks", 5), ("minecraft:cracked_polished_blackstone_bricks", 3), ("minecraft:blackstone", 2)),
        "cobble": _w(("minecraft:blackstone", 6), ("minecraft:basalt[axis=y]", 4)),
        "floor": _w(("minecraft:blackstone", 4), ("minecraft:polished_basalt[axis=y]", 3), ("minecraft:soul_soil", 2), ("minecraft:gilded_blackstone", 1)),
        "chiseled": "minecraft:chiseled_polished_blackstone",
        "accent": "minecraft:gilded_blackstone",
        "pillar": "minecraft:basalt[axis=y]",
        "stairs": "minecraft:polished_blackstone_brick_stairs",
        "slab": "minecraft:polished_blackstone_brick_slab",
        "cobble_slab": "minecraft:blackstone_slab",
        "wall": "minecraft:blackstone_wall",
        "brick_wall": "minecraft:polished_blackstone_brick_wall",
        "light": "minecraft:soul_lantern[hanging=false]",
        "hanging_light": "minecraft:soul_lantern[hanging=true]",
        "top_dress": None,
    },
    "end": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:end_stone_bricks", 7), ("minecraft:end_stone", 3)),
        "cobble": _w(("minecraft:end_stone", 7), ("minecraft:end_stone_bricks", 3)),
        "floor": _w(("minecraft:end_stone_bricks", 5), ("minecraft:end_stone", 3), ("minecraft:purpur_block", 2)),
        "chiseled": "minecraft:purpur_block",
        "accent": "minecraft:purpur_block",
        "pillar": "minecraft:purpur_pillar[axis=y]",
        "stairs": "minecraft:end_stone_brick_stairs",
        "slab": "minecraft:end_stone_brick_slab",
        "cobble_slab": "minecraft:end_stone_brick_slab",
        "wall": "minecraft:end_stone_brick_wall",
        "brick_wall": "minecraft:end_stone_brick_wall",
        "light": "minecraft:end_rod[facing=up]",
        "hanging_light": "minecraft:end_rod[facing=down]",
        "top_dress": None,
    },
    "egyptian": {
        "waystone": "waystones:sandy_waystone",
        "brick": _w(("minecraft:sandstone", 4), ("minecraft:cut_sandstone", 3), ("minecraft:smooth_sandstone", 3)),
        "cobble": _w(("minecraft:sandstone", 6), ("minecraft:cut_sandstone", 4)),
        "floor": _w(("minecraft:smooth_sandstone", 4), ("minecraft:cut_sandstone", 3), ("minecraft:sandstone", 2), ("minecraft:sand", 1)),
        "chiseled": "minecraft:chiseled_sandstone",
        "accent": "minecraft:gold_block",
        "pillar": "minecraft:cut_sandstone",
        "stairs": "minecraft:smooth_sandstone_stairs",
        "slab": "minecraft:smooth_sandstone_slab",
        "cobble_slab": "minecraft:sandstone_slab",
        "wall": "minecraft:sandstone_wall",
        "brick_wall": "minecraft:sandstone_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "greek": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:calcite", 5), ("minecraft:smooth_quartz", 3), ("minecraft:quartz_block", 1), ("minecraft:diorite", 1)),
        "cobble": _w(("minecraft:calcite", 5), ("minecraft:diorite", 5)),
        "floor": _w(("minecraft:quartz_block", 1), ("minecraft:calcite", 4), ("minecraft:polished_diorite", 5)),
        "chiseled": "minecraft:chiseled_quartz_block",
        "accent": "minecraft:polished_diorite",
        "pillar": "minecraft:quartz_pillar[axis=y]",
        "stairs": "minecraft:quartz_stairs",
        "slab": "minecraft:quartz_slab",
        "cobble_slab": "minecraft:quartz_slab",
        "wall": "minecraft:diorite_wall",
        "brick_wall": "minecraft:diorite_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "babylon": {
        "waystone": "waystones:sandy_waystone",
        "brick": _w(("minecraft:mud_bricks", 7), ("minecraft:terracotta", 3)),
        "cobble": _w(("minecraft:packed_mud", 6), ("minecraft:mud_bricks", 4)),
        "floor": _w(("minecraft:mud_bricks", 4), ("minecraft:packed_mud", 3), ("minecraft:terracotta", 3)),
        "chiseled": "minecraft:blue_terracotta",
        "accent": "minecraft:blue_terracotta",
        "glaze": _w(("minecraft:blue_terracotta", 6), ("minecraft:cyan_terracotta", 3), ("minecraft:lapis_block", 1)),
        "pillar": "minecraft:mud_bricks",
        "stairs": "minecraft:mud_brick_stairs",
        "slab": "minecraft:mud_brick_slab",
        "cobble_slab": "minecraft:mud_brick_slab",
        "wall": "minecraft:mud_brick_wall",
        "brick_wall": "minecraft:mud_brick_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "mayan": {
        "waystone": "waystones:mossy_waystone",
        "brick": _w(("minecraft:mossy_cobblestone", 4), ("minecraft:cobblestone", 3), ("minecraft:mossy_stone_bricks", 2), ("minecraft:cracked_stone_bricks", 1)),
        "cobble": _w(("minecraft:cobblestone", 5), ("minecraft:mossy_cobblestone", 5)),
        "floor": _w(("minecraft:mossy_cobblestone", 4), ("minecraft:cobblestone", 3), ("minecraft:moss_block", 3)),
        "chiseled": "minecraft:chiseled_stone_bricks",
        "accent": "minecraft:moss_block",
        "pillar": "minecraft:mossy_cobblestone",
        "stairs": "minecraft:cobblestone_stairs",
        "slab": "minecraft:cobblestone_slab",
        "cobble_slab": "minecraft:mossy_cobblestone_slab",
        "wall": "minecraft:mossy_cobblestone_wall",
        "brick_wall": "minecraft:stone_brick_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": None,
    },
    "viking": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:stone_bricks", 4), ("minecraft:cobblestone", 4), ("minecraft:mossy_cobblestone", 2)),
        "cobble": _w(("minecraft:cobblestone", 7), ("minecraft:mossy_cobblestone", 3)),
        "floor": _w(("minecraft:cobblestone", 4), ("minecraft:dirt_path", 4), ("minecraft:coarse_dirt", 2)),
        "chiseled": "minecraft:chiseled_stone_bricks",
        "accent": "minecraft:spruce_log[axis=y]",
        "pillar": "minecraft:spruce_log[axis=y]",
        "plank": "minecraft:spruce_planks",
        "stairs": "minecraft:spruce_stairs",
        "slab": "minecraft:spruce_slab",
        "cobble_slab": "minecraft:cobblestone_slab",
        "wall": "minecraft:cobblestone_wall",
        "brick_wall": "minecraft:stone_brick_wall",
        "light": "minecraft:lantern[hanging=false]",
        "hanging_light": "minecraft:lantern[hanging=true]",
        "top_dress": "minecraft:snow[layers=1]",
    },
    "drowned": {
        "waystone": "waystones:waystone",
        "brick": _w(("minecraft:mossy_stone_bricks", 4), ("minecraft:stone_bricks", 2), ("minecraft:prismarine", 2), ("minecraft:cracked_stone_bricks", 2)),
        "cobble": _w(("minecraft:mossy_cobblestone", 5), ("minecraft:cobblestone", 3), ("minecraft:prismarine", 2)),
        "floor": _w(("minecraft:mossy_cobblestone", 4), ("minecraft:prismarine", 3), ("minecraft:dark_prismarine", 1), ("minecraft:gravel", 2)),
        "chiseled": "minecraft:chiseled_stone_bricks",
        "accent": "minecraft:dark_prismarine",
        "stairs": "minecraft:mossy_stone_brick_stairs",
        "slab": "minecraft:mossy_stone_brick_slab",
        "cobble_slab": "minecraft:mossy_cobblestone_slab",
        "wall": "minecraft:mossy_cobblestone_wall",
        "brick_wall": "minecraft:mossy_stone_brick_wall",
        "light": "minecraft:sea_lantern",
        "hanging_light": "minecraft:sea_lantern",
        "top_dress": None,
    },
}

WAYSTONE_BE = {"id": "waystones:waystone"}  # mod assigns UUID/name on generation

# No banners anywhere: a thousand-year-old ruin keeps its stone, not its cloth.

ARCHAEOLOGY_LOOT = "waystone_ruins:archaeology/ruins"

FULL_SOLID_HINTS = ("bricks", "cobble", "sandstone", "deepslate", "tuff", "andesite",
                    "moss_block", "packed_ice", "sand", "stone", "tiles", "grass_block",
                    "dirt", "calcite", "diorite", "basalt", "purpur", "prismarine",
                    "terracotta", "planks", "spruce_log", "quartz", "mud_brick",
                    "packed_mud", "gold_block")


def parse_state(state: str):
    if "[" in state:
        name, props = state[:-1].split("[", 1)
        pd = dict(kv.split("=", 1) for kv in props.split(","))
        return name, pd
    return state, None


class Build:
    """Sparse voxel build. y=0..1 is buried foundation, y=2 is ground/floor level
    for surface designs. Absent positions leave terrain untouched."""

    def __init__(self, name, theme_name, seed=0, pristine=False):
        self.name = name
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.seed = seed
        self.rng = random.Random(f"{name}:{theme_name}:{seed}")
        self.blocks = {}   # (x,y,z) -> (state_str, be_dict|None)
        self.protected = set()
        self.pristine = pristine   # skips erode/rubble; paired with empty processors
        self.ground_y = 2           # surface floor; None for cave/water builds

    # -- resolution
    def resolve(self, role_or_state):
        v = self.theme.get(role_or_state, role_or_state)
        if isinstance(v, list):
            states = [s for s, _ in v]
            weights = [w for _, w in v]
            return self.rng.choices(states, weights=weights, k=1)[0]
        return v

    # -- primitives
    def set(self, x, y, z, role_or_state, be=None, protect=False):
        state = self.resolve(role_or_state)
        if state is None:
            return
        self.blocks[(x, y, z)] = (state, be)
        if protect:
            self.protected.add((x, y, z))

    def clear(self, x, y, z):
        self.blocks.pop((x, y, z), None)
        self.protected.discard((x, y, z))

    def fill(self, x0, y0, z0, x1, y1, z1, role_or_state, protect=False):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, role_or_state, protect=protect)

    def hollow_box(self, x0, y0, z0, x1, y1, z1, role_or_state):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    edge = x in (x0, x1) or z in (z0, z1) or y in (y0, y1)
                    if edge:
                        self.set(x, y, z, role_or_state)

    def air(self, x0, y0, z0, x1, y1, z1):
        self.fill(x0, y0, z0, x1, y1, z1, "minecraft:air")

    def column(self, x, y0, z, height, role_or_state, cap=None):
        for y in range(y0, y0 + height):
            self.set(x, y, z, role_or_state)
        if cap:
            self.set(x, y0 + height, z, cap)

    def waystone(self, x, y, z, facing="north"):
        # origin=wilderness makes wasGenerated() true, so Waystones assigns a
        # generated name on first activation — origin=unknown (the default when
        # the property is omitted) silently skips naming. Blockstate property,
        # NOT block entity NBT.
        ws = self.theme["waystone"]
        self.set(x, y, z, f"{ws}[half=lower,facing={facing},origin=wilderness,waterlogged=false]",
                 be=dict(WAYSTONE_BE), protect=True)
        self.set(x, y + 1, z, f"{ws}[half=upper,facing={facing},origin=wilderness,waterlogged=false]",
                 be=dict(WAYSTONE_BE), protect=True)
        # ensure headroom above the waystone; keep its supporting block too
        self.set(x, y + 2, z, "minecraft:air", protect=True)
        self.protected.add((x, y - 1, z))

    def foundation(self, x0, z0, x1, z1):
        """Two buried layers under the footprint so slopes don't leave floaters."""
        self.fill(x0, 0, z0, x1, 1, z1, "cobble")

    def suspicious(self, x, y, z):
        """Brushable block wired to the archaeology loot table — sand in the
        desert schools, gravel everywhere else."""
        block = ("minecraft:suspicious_sand" if self.theme_name in ("sandy", "egyptian")
                 else "minecraft:suspicious_gravel")
        self.set(x, y, z, block,
                 be={"id": "minecraft:brushable_block", "LootTable": ARCHAEOLOGY_LOOT},
                 protect=True)
        self.protected.add((x, y - 1, z))

    def pot(self, x, y, z):
        """Decorated pot with random sherd faces — breaks into its sherds."""
        patterns = ["minecraft:brick", "minecraft:brick", "minecraft:brick",
                    "minecraft:archer_pottery_sherd", "minecraft:prize_pottery_sherd",
                    "minecraft:skull_pottery_sherd", "minecraft:heart_pottery_sherd",
                    "minecraft:explorer_pottery_sherd", "minecraft:sheaf_pottery_sherd"]
        sherds = [self.rng.choice(patterns) for _ in range(4)]
        facing = self.rng.choice(("north", "south", "east", "west"))
        self.set(x, y, z,
                 f"minecraft:decorated_pot[facing={facing},cracked=false,waterlogged=false]",
                 be={"id": "minecraft:decorated_pot", "sherds": sherds}, protect=True)
        self.protected.add((x, y - 1, z))

    def satellite_socket(self, x, z, orientation, y=1):
        """Buried jigsaw that may grow a satellite piece (fallen pillars, path
        fragment, gatehouse stub) from waystone_ruins:satellites_<theme>."""
        self.set(x, y, z, f"minecraft:jigsaw[orientation={orientation}]",
                 be={"id": "minecraft:jigsaw", "name": "waystone_ruins:socket",
                     "target": "waystone_ruins:plug",
                     "pool": f"waystone_ruins:satellites_{self.theme_name}",
                     "final_state": self.resolve("cobble"), "joint": "rollable"},
                 protect=True)

    def plug(self, x, z, orientation, y=1):
        """Child-side jigsaw for satellite templates."""
        self.set(x, y, z, f"minecraft:jigsaw[orientation={orientation}]",
                 be={"id": "minecraft:jigsaw", "name": "waystone_ruins:plug",
                     "target": "minecraft:empty", "pool": "minecraft:empty",
                     "final_state": self.resolve("cobble"), "joint": "rollable"},
                 protect=True)

    def shaft(self, x, z, y0, height):
        """Entrance shaft rising from a room ceiling: cobble-lined, air in the
        lower half, gravel-plugged above — digging down drops you in."""
        for i in range(height):
            y = y0 + i
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y, z + dz) not in self.blocks:
                    self.set(x + dx, y, z + dz, "cobble")
            self.set(x, y, z, "minecraft:gravel" if i >= height // 2 else "minecraft:air",
                     protect=True)
            if i >= height // 2:
                if not hasattr(self, "secret_blocks"):
                    self.secret_blocks = set()
                self.secret_blocks.add((x, y, z))

    def breach(self, x0, y0, z0, x1, y1, z1, count=3):
        """Knock a few unprotected blocks out of a shell region (cave cracks)."""
        cand = [p for p in self.blocks
                if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and z0 <= p[2] <= z1
                and p not in self.protected
                and self.blocks[p][0] != "minecraft:air"]
        for p in self.rng.sample(cand, min(count, len(cand))):
            self.blocks[p] = ("minecraft:air", None)

    def drip_decor(self, prob=0.16):
        """Dripstone theme: grow stalagmite/stalactite tips in interior air."""
        adds = {}
        for (x, y, z), (state, _) in list(self.blocks.items()):
            if state != "minecraft:air" or (x, y, z) in self.protected:
                continue
            below = self.blocks.get((x, y - 1, z))
            above = self.blocks.get((x, y + 1, z))
            if below and below[0] != "minecraft:air" and "lantern" not in below[0] \
                    and self.rng.random() < prob:
                adds[(x, y, z)] = ("minecraft:pointed_dripstone[vertical_direction=up,thickness=tip,waterlogged=false]", None)
            elif above and above[0] != "minecraft:air" and "lantern" not in above[0] \
                    and self.rng.random() < prob * 0.8:
                adds[(x, y, z)] = ("minecraft:pointed_dripstone[vertical_direction=down,thickness=tip,waterlogged=false]", None)
        self.blocks.update(adds)

    def stairs(self, x, y, z, facing, half="bottom", shape="straight"):
        base, _ = parse_state(self.resolve("stairs"))
        self.set(x, y, z, f"{base}[facing={facing},half={half},shape={shape},waterlogged=false]",
                 protect=True)

    def steps_row(self, x0, x1, y, z, facing):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            self.stairs(x, y, z, facing)

    # -- weathering
    def erode(self, prob=0.10, min_y=2, passes=2):
        """Peel unprotected blocks top-down for a ruined look. Only blocks with
        nothing (or explicit air) directly above are eligible, so columns lose
        height instead of their midsections and nothing is left floating.
        Lantern support blocks are implicitly protected."""
        if self.pristine:
            return
        supports = set()
        for (x, y, z), (state, _) in self.blocks.items():
            if "lantern" in state:
                supports.add((x, y + 1, z) if "hanging=true" in state else (x, y - 1, z))
        for _ in range(passes):
            for pos in list(self.blocks.keys()):
                x, y, z = pos
                if y < min_y or pos in self.protected or pos in supports:
                    continue
                if self.ground_y is not None and y <= self.ground_y:
                    continue  # weather walls, never punch holes in walking floors
                state = self.blocks[pos][0]
                if state == "minecraft:air" or "waystones:" in state or "snow" in state:
                    continue
                above = self.blocks.get((x, y + 1, z))
                if above is not None and above[0] != "minecraft:air":
                    continue  # something rests on this block
                if self.rng.random() < prob:
                    del self.blocks[pos]

    def dress_tops(self, prob=0.55):
        """Frozen theme: snow layers on exposed solid tops."""
        dress = self.theme.get("top_dress")
        if not dress:
            return
        tops = {}
        for (x, y, z), (state, _) in self.blocks.items():
            if state == "minecraft:air" or "[" in state and "half=upper" in state:
                continue
            if any(p in state for p in ("_slab", "_wall", "stairs", "lantern")):
                continue  # snow can't rest on these; it would render floating
            if any(h in state for h in FULL_SOLID_HINTS):
                if (x, z) not in tops or y > tops[(x, z)]:
                    tops[(x, z)] = y
        for (x, z), y in tops.items():
            above = (x, y + 1, z)
            if above not in self.blocks and self.rng.random() < prob:
                self.blocks[above] = (dress, None)
                below = self.blocks.get((x, y, z))
                if below and below[0].startswith("minecraft:grass_block"):
                    self.blocks[(x, y, z)] = ("minecraft:grass_block[snowy=true]", below[1])

    def underpin(self):
        """Fill the y2 gap under any column whose lowest solid block is y3
        (perimeter walls, tier rims, obelisk bases, fallen drums...). On flat
        terrain that layer is natural ground; on slopes it was an air gap that
        left blocks floating."""
        for (x, y, z), (state, _) in list(self.blocks.items()):
            if y != 3 or state == "minecraft:air":
                continue
            if (x, 2, z) not in self.blocks:
                self.set(x, 2, z, "cobble")
        # Exposed rims and freestanding columns need the same shallow footing
        # as the main floor when the accepted terrain is one block lower.
        for (x, y, z), (state, _) in list(self.blocks.items()):
            if y != 2 or state == "minecraft:air":
                continue
            if state.startswith(("minecraft:vine", "minecraft:light[")):
                continue
            for by in (1, 0):
                if (x, by, z) not in self.blocks:
                    self.set(x, by, z, "cobble")

    def footings(self, ground_y, depth=2):
        """1.19.0: give every ground-contact column `depth` blocks of footing under the floor.

        A column whose lowest solid block is the floor tile (y=ground_y) or a wall base just
        above it is extended down to ground_y-depth through voxels the design leaves unset.
        On flat ground these replace natural ground and stay invisible; on a slope they are
        the foundation. Authored voxels (rooms, explicit air, archaeology) are never touched,
        so buried rooms and passages keep their shape. Columns whose lowest block is higher
        (lintels, roof edges) rest on other columns and are skipped.

        underpin() already does this for ground_y == 2 designs during construction; this
        pass covers deeper designs, the selected layouts and blocks added after underpin
        (satellite sockets, reclaimed rubble). The site check's downhill tolerance relies on
        it: with depth 2 a column stays supported while the ground lies up to three blocks
        below the reference height (build.FOOTING_REACH), and build.py asserts that.
        """
        lows = {}
        for (x, y, z), (state, _) in self.blocks.items():
            if not structural(state):
                continue
            if y < lows.get((x, z), y + 1):
                lows[(x, z)] = y
        added = 0
        for (x, z), low in sorted(lows.items()):
            if low > ground_y + 1:
                continue
            for y in range(ground_y - depth, low):
                if (x, y, z) not in self.blocks:
                    self.set(x, y, z, "cobble")
                    added += 1
        return added

    def align_satellite_sockets(self, ground_y=2):
        """Put connectors outside cornices/vines so rigid children can fit.

        Jigsaw collision checks use the whole template box, including roof
        overhangs. A socket hidden inside that box could never grow a child.
        Short buried paths connect relocated sockets to the original floor.
        """
        if not self.blocks:
            return
        xmin, xmax = min(p[0] for p in self.blocks), max(p[0] for p in self.blocks)
        zmin, zmax = min(p[2] for p in self.blocks), max(p[2] for p in self.blocks)
        sockets = [(p, v) for p, v in self.blocks.items()
                   if (v[1] or {}).get("name") == "waystone_ruins:socket"]
        for (x, y, z), (state, be) in sockets:
            _, props = parse_state(state)
            direction = props["orientation"].split("_")[0]
            tx, tz = {"west": (xmin, z), "east": (xmax, z),
                      "north": (x, zmin), "south": (x, zmax)}[direction]
            if (tx, tz) == (x, z):
                continue
            self.set(x, y, z, be["final_state"])
            for px in range(min(x, tx), max(x, tx) + 1):
                for pz in range(min(z, tz), max(z, tz) + 1):
                    for py in range(y, ground_y + 1):
                        if (px, py, pz) not in self.blocks:
                            self.set(px, py, pz, "cobble", protect=True)
            self.set(tx, y, tz, state, be=be, protect=True)

    def clearance(self, pad=2, ground_y=3):
        """Clear headroom inside the surface building's actual footprint.

        Basement ceilings must never become the bottom of an open excavation.
        Ignore columns that only contain buried rooms, leave the surrounding
        terrain intact, and follow each column's own height. Fill missing air
        UNDER roofs too, so a slope cannot plug an otherwise open doorway.
        Explicit room air below ground is authored by the design itself.
        """
        if not self.blocks:
            return
        tops = {}
        for (x, y, z), (state, _) in self.blocks.items():
            if y < ground_y - 1 or state == "minecraft:air":
                continue
            if state.startswith(("minecraft:vine", "minecraft:light[")):
                continue
            tops[(x, z)] = max(y, tops.get((x, z), y))
        for (x, z), top in tops.items():
            for y in range(ground_y, max(ground_y + 1, top + pad) + 1):
                self.blocks.setdefault((x, y, z), ("minecraft:air", None))

    def rubble(self, x0, z0, x1, z1, count, y=2):
        """Scatter broken bits on the ground plane inside a rect."""
        if self.pristine:
            return
        opts = ["wall", "cobble_slab", "cobble"]
        for _ in range(count):
            x = self.rng.randint(min(x0, x1), max(x0, x1))
            z = self.rng.randint(min(z0, z1), max(z0, z1))
            if (x, y, z) in self.blocks:
                continue
            role = self.rng.choice(opts)
            state = self.resolve(role)
            base, props = parse_state(state)
            if base.endswith("_slab") and props is None:
                state = f"{base}[type=bottom,waterlogged=false]"
            if base.endswith("_wall") and props is None:
                state = f"{base}[up=true]"
            self.blocks[(x, y, z)] = (state, None)

    # -- emit
    def emit(self, path):
        assert self.blocks, f"{self.name}/{self.theme_name}: empty build"
        xs = [p[0] for p in self.blocks]
        ys = [p[1] for p in self.blocks]
        zs = [p[2] for p in self.blocks]
        ox, oy, oz = min(xs), min(ys), min(zs)
        # Pool variants with optional basements reserve one common origin.
        # Empty padding is omitted from blocks, preserving the natural ground.
        oy = min(oy, getattr(self, 'template_min_y', oy))
        self.emitted_origin = (ox, oy, oz)
        size = [max(xs) - ox + 1, max(ys) - oy + 1, max(zs) - oz + 1]

        palette = []
        pindex = {}
        blocks = []
        for (x, y, z), (state, be) in sorted(self.blocks.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
            name, props = parse_state(state)
            key = (name, tuple(sorted(props.items())) if props else None)
            if key not in pindex:
                pindex[key] = len(palette)
                entry = {"Name": name}
                if props:
                    entry["Properties"] = {k: v for k, v in sorted(props.items())}
                palette.append(entry)
            b = {"pos": [x - ox, y - oy, z - oz], "state": pindex[key]}
            if be:
                b["nbt"] = be
            blocks.append(b)

        root = {
            "size": size,
            "entities": [],
            "blocks": blocks,
            "palette": palette,
            "DataVersion": DATA_VERSION,
        }
        write_nbt(path, root)
        return size, len(palette), len(blocks)
