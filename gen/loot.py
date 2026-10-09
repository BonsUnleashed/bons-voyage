"""Chest loot for Waystone Ruins (v1.17): what the Waybuilders left behind.

Rewards follow how hard a room is to find:
  chests/crypt             open cellars and unsealed dungeon floors (v1.8, build.py)
  chests/curiosity_cache   the small sealed rooms and the annex caches
  chests/hidden_treasury   any chest behind a secret: a hatch, seal or weak wall
  chests/waybuilder_hoard  the deepest vault of each great dungeon

The Waybuilders valued metal, pigment, crystal, writing and the dust their
stones are made of, so the pools lean on those and on Waystones' own travel
items rather than on food or gear.

Enchanted books start from minecraft:book. EnchantRandomlyFunction converts
only a plain book (it tests Items.BOOK); started from minecraft:enchanted_book
it writes the enchantment into the item's own "Enchantments" tag, and an anvil
reads "StoredEnchantments", so the book cannot be applied. v1.1 to v1.16
shipped their books that way.
"""

HIDDEN_TREASURY = "waystone_ruins:chests/hidden_treasury"
HOARD = "waystone_ruins:chests/waybuilder_hoard"

CURATED_ENCHANTS = ["minecraft:unbreaking", "minecraft:efficiency",
                    "minecraft:protection", "minecraft:sharpness",
                    "minecraft:power", "minecraft:feather_falling",
                    "minecraft:looting", "minecraft:fortune",
                    "minecraft:silk_touch"]

# The keepsake every sealed cache guarantees: travel, shelter and gift motifs.
KEEPSAKE_SHERDS = ["explorer", "shelter", "sheaf", "archer",
                   "prize", "friend", "heart", "plenty"]

# The four trail-ruin templates: archaeology's own finds, and "Wayfinder"
# names the Waybuilders' trade outright.
RUIN_TRIMS = {"wayfinder": 2, "raiser": 1, "shaper": 1, "host": 1}


def item(name, weight=1, count=None):
    """One weighted entry; count is an int or an inclusive (min, max) pair."""
    entry = {"type": "minecraft:item",
             "name": name if ":" in name else "minecraft:" + name,
             "weight": weight}
    if count is not None:
        value = count if isinstance(count, int) else {"min": count[0], "max": count[1]}
        entry["functions"] = [{"function": "minecraft:set_count", "count": value}]
    return entry


def curated_book(weight):
    return {"type": "minecraft:item", "name": "minecraft:book", "weight": weight,
            "functions": [{"function": "minecraft:enchant_randomly",
                           "enchantments": CURATED_ENCHANTS}]}


def levelled_book(weight, levels=(20, 30)):
    """A table-grade book: several enchantments, no treasure enchantments."""
    return {"type": "minecraft:item", "name": "minecraft:book", "weight": weight,
            "functions": [{"function": "minecraft:enchant_with_levels",
                           "levels": {"min": levels[0], "max": levels[1]},
                           "treasure": False}]}


def mending_book(weight):
    return {"type": "minecraft:item", "name": "minecraft:book", "weight": weight,
            "functions": [{"function": "minecraft:enchant_randomly",
                           "enchantments": ["minecraft:mending"]}]}


def trims(scale):
    return [item(f"{name}_armor_trim_smithing_template", weight * scale)
            for name, weight in RUIN_TRIMS.items()]


def keepsake_pool():
    return {"rolls": 1, "entries": [item(f"{s}_pottery_sherd") for s in KEEPSAKE_SHERDS]}


def supplies_pool(rolls):
    """The working stock of a sealed store: metal, pigment, crystal, light, paper."""
    return {"rolls": rolls, "entries": [
        item("gold_nugget", 5, (4, 9)),
        item("gold_ingot", 4, (1, 3)),
        item("iron_ingot", 4, (1, 3)),
        item("emerald", 4, (1, 3)),
        item("lapis_lazuli", 4, (3, 7)),
        item("amethyst_shard", 3, (2, 5)),
        item("waystones:warp_dust", 4, (2, 5)),
        item("candle", 3, (2, 4)),
        item("paper", 2, (2, 5)),
    ]}


def find_pool():
    """The one real find a cache or keeper's store always holds."""
    return {"rolls": 1, "entries": [
        item("emerald", 10, (3, 6)),
        item("gold_ingot", 8, (3, 6)),
        item("diamond", 6, (1, 2)),
        curated_book(8),
        item("waystones:warp_scroll", 6, (1, 2)),
        item("waystones:return_scroll", 6, (1, 2)),
        item("golden_apple", 4),
        item("name_tag", 3),
        item("wayfinder_armor_trim_smithing_template", 3),
        item("music_disc_relic", 1),
        item("sniffer_egg", 1),
    ]}


def curiosity_loot_json():
    """Sealed-room caches: a keepsake, a store's worth of supplies, one real find."""
    return {"type": "minecraft:chest", "pools": [
        keepsake_pool(),
        supplies_pool({"min": 3, "max": 4}),
        find_pool(),
    ]}


def hidden_treasury_json():
    """A chest behind a secret: a full store plus two valuables."""
    return {"type": "minecraft:chest", "pools": [
        {"rolls": {"min": 3, "max": 5}, "entries": [
            item("gold_nugget", 6, (4, 10)),
            item("gold_ingot", 8, (1, 4)),
            item("iron_ingot", 6, (2, 5)),
            item("emerald", 7, (1, 4)),
            item("lapis_lazuli", 6, (3, 8)),
            item("amethyst_shard", 4, (2, 5)),
            item("waystones:warp_dust", 5, (2, 6)),
            item("candle", 3, (1, 3)),
            item("bone", 2, (1, 4)),
            item("name_tag", 2),
            item("saddle", 2),
        ]},
        {"rolls": 2, "entries": [
            item("diamond", 8, (1, 3)),
            item("emerald", 10, (4, 8)),
            item("gold_ingot", 8, (4, 8)),
            curated_book(10),
            item("golden_apple", 6),
            item("waystones:warp_scroll", 6, (1, 2)),
            item("waystones:return_scroll", 5, (1, 2)),
            *trims(2),
            item("music_disc_relic", 1),
            item("sniffer_egg", 1),
        ]},
    ]}


def hoard_json():
    """The deepest vault of a great dungeon: the Waybuilders' own hoard."""
    return {"type": "minecraft:chest", "pools": [
        {"rolls": {"min": 4, "max": 6}, "entries": [
            item("gold_ingot", 8, (2, 6)),
            item("emerald", 8, (2, 6)),
            item("iron_ingot", 6, (3, 7)),
            item("lapis_lazuli", 6, (4, 10)),
            item("amethyst_shard", 4, (3, 6)),
            item("waystones:warp_dust", 6, (3, 8)),
            item("diamond", 4, (1, 2)),
            item("golden_carrot", 4, (2, 5)),
            item("experience_bottle", 4, (2, 5)),
        ]},
        {"rolls": {"min": 2, "max": 3}, "entries": [
            item("diamond", 10, (2, 4)),
            levelled_book(10),
            mending_book(3),
            item("golden_apple", 8, (1, 2)),
            item("enchanted_golden_apple", 2),
            item("waystones:warp_stone", 3),
            item("waystones:warp_scroll", 6, (1, 3)),
            item("waystones:return_scroll", 5, (1, 2)),
            *trims(3),
            item("music_disc_relic", 2),
            item("sniffer_egg", 2),
            item("netherite_scrap", 2),
            item("gold_block", 3),
            item("emerald_block", 2),
        ]},
    ]}
