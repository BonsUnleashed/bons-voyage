"""v1.8 batch 2: roofed structures with extensive - sometimes hidden -
undergrounds. Surface designs that carry a basement declare `ground`: the
template y of the walking level (release build offsets start_height by it;
default 2 = no basement). Hidden access patterns rotated across the batch:
gravel-plugged shafts, suspicious-block false floors, weak-wall breaches,
behind-the-idol stairs. A few waystones are themselves the buried secret.
"""
from master import (grad_wall, string_course, cornice, pilasters, corbel_arch,
                    battered_wall, column_stump, crack_seams, collapse_wedge,
                    vine_creep, hidden_light, merlons, glazed_frieze, gable_roof,
                    room, loot_chest, ladder_shaft, weak_wall, false_floor,
                    sarcophagus, slab_roof, passage, secret_hatch, gable_ends)
# v1.17: secret crypts are furnished (interiors.py) and every chest behind a
# hatch or weak wall draws on the hidden-treasury table.
from interiors import (candles, hanging_lantern, frieze, niche, lichen, roots,
                       floor_skull, bookshelf, lectern, written_book, wall_cells,
                       cornice as inner_cornice)
from loot import HIDDEN_TREASURY


def ground(g):
    """Decorator: mark a design's walking level (template y)."""
    def deco(fn):
        fn.ground = g
        return fn
    return deco


# ================================================================ EGYPTIAN

@ground(8)
def temple_of_ra(b):
    """Egyptian grand: fully roofed hypostyle sanctuary; beneath it, a crypt
    reached through a false floor in the holy of holies.

    v1.17: the crypt is a painted burial hall four blocks high - papyrus
    columns, a glyph frieze, black jackal guardians at the sarcophagus,
    canopic jars, lamp niches, and a blue ceiling of yellow stars."""
    G = 8
    W, D = 20, 14
    crypt = (5, 2, 4, 15, G - 1, 10)
    # ---- crypt level (y2..G-1): the burial hall
    room(b, *crypt, shell="brick")
    b.fill(6, 2, 5, 14, 2, 9, "minecraft:smooth_sandstone")      # dressed pavement,
    for x in range(6, 15):                                        # a cut border on the long sides
        for z in (5, 9):
            b.set(x, 2, z, "minecraft:cut_sandstone")
    for x, z in ((7, 6), (7, 8), (13, 6), (13, 8)):
        b.column(x, 3, z, 3, "pillar", cap="chiseled")          # papyrus shafts, carved capitals
    sarcophagus(b, 9, 3, 6, axis="x")
    for x in (8, 12):                                            # jackal guardians in black stone
        b.set(x, 3, 6, "minecraft:polished_blackstone", protect=True)
        b.set(x, 4, 6, "minecraft:chiseled_polished_blackstone", protect=True)
    loot_chest(b, 6, 3, 9, facing="east", table=HIDDEN_TREASURY)
    loot_chest(b, 14, 3, 5, facing="west", table=HIDDEN_TREASURY)
    for x in (7, 8, 12, 13):                                     # canopic jars behind the bier
        b.pot(x, 3, 5)
    b.pot(14, 3, 9)
    b.suspicious(10, 2, 8)
    for x in (8, 12):                                            # lamp niches in both long walls
        for z, out in ((4, (0, -1)), (10, (0, 1))):
            niche(b, x, 4, z, out, "brick", content="minecraft:candle[candles=3,lit=true,waterlogged=false]")
    frieze(b, crypt, 5, "minecraft:cyan_terracotta", "minecraft:chiseled_sandstone", period=2)
    inner_cornice(b, crypt, 6, "minecraft:smooth_sandstone_stairs", "minecraft:chiseled_sandstone")
    for x in (8, 12):
        hanging_lantern(b, x, 5, 7)
    # ---- surface temple
    b.fill(0, G - 1, 0, W, G - 1, D, "cobble")         # platform underside
    # The crypt's own ceiling in that course: night blue with scattered stars
    # (a fixed hash, so every variant shares the same sky).
    import zlib
    for x in range(6, 15):
        for z in range(5, 10):
            star = zlib.crc32(f"{x},{z}".encode()) % 6 == 0
            b.set(x, G - 1, z, "minecraft:yellow_terracotta" if star else "minecraft:blue_terracotta")
    b.fill(0, G, 0, W, G, D, "floor")
    for z in (0, D):
        grad_wall(b, 0, G + 1, z, W, G + 5, z, "brick", "cobble", "cobble", ground_y=G)
        for x in range(0, W + 1):
            b.set(x, G + 3, z, "chiseled")             # hieroglyph course
    grad_wall(b, 0, G + 1, 1, 0, G + 5, D - 1, "brick", "cobble", "cobble", ground_y=G)
    b.fill(W, G + 1, 1, W, G + 5, D - 1, "brick")
    b.air(W, G + 1, 6, W, G + 3, 8)                    # east entrance
    pilasters(b, 1, 0, W - 1, G + 1, G + 4, period=4, depth_dz=1, role="accent")
    for cx in (5, 10, 15):                             # interior columns
        for cz in (4, 10):
            b.column(cx, G + 1, cz, 5, "brick", cap="chiseled")
    slab_roof(b, 0, 0, W, D, G + 7)                    # the roof survives
    cornice(b, 0, 0, W, D, G + 6)
    # sanctuary: granite dais, waystone, and the false floor over the crypt
    b.fill(1, G + 1, 5, 3, G + 1, 9, "minecraft:polished_granite")
    b.waystone(2, G + 2, 7, facing="east")
    b.set(2, G + 2, 9, "minecraft:gold_block", protect=True)
    secret_hatch(b, 10, 8, 3, G, facing="south")       # clear of the sarcophagus
    hidden_light(b, 10, G + 4, 7)
    b.satellite_socket(W, 7, "east_up", y=G - 1)
    b.satellite_socket(10, 0, "north_up", y=G - 1)
    if not b.pristine:
        crack_seams(b, 0, 0, W, D, G + 1, G + 5, count=3)
        collapse_wedge(b, b.rng.randint(4, 16), G + 7, 0, 3, "east", (2, G, W - 2, 3))
    b.erode(0.04, min_y=G + 5)
    b.rubble(1, 1, W - 1, D - 1, 5, y=G)


@ground(10)
def nomarch_tomb(b):
    """Egyptian: modest roofed chapel above; a deep shaft below it drops to
    the nomarch's burial suite. The waystone was sealed in with him."""
    G = 10
    # ---- burial suite (y2..7): two rooms
    room(b, 2, 2, 2, 10, 7, 8, shell="brick")
    room(b, 10, 2, 3, 16, 6, 7, shell="brick")         # canopic annex
    b.air(10, 3, 5, 10, 4, 5)                          # connecting door
    sarcophagus(b, 5, 3, 5, axis="x")
    b.set(4, 3, 3, "chiseled", protect=True)
    b.waystone(4, 4, 3, facing="south")                # the buried waystone
    loot_chest(b, 15, 3, 4, facing="south", table=HIDDEN_TREASURY)
    b.pot(14, 3, 6)
    b.pot(3, 3, 7)
    b.suspicious(8, 2, 4)
    hidden_light(b, 7, 5, 5, level=8)
    # ---- chapel above
    b.fill(3, G, 3, 9, G, 9, "floor")
    for x in range(3, 10):
        for z in (3, 9):
            b.fill(x, G + 1, z, x, G + 3, z, "brick")
    for z in range(4, 9):
        b.fill(3, G + 1, z, 3, G + 3, z, "brick")
        b.fill(9, G + 1, z, 9, G + 3, z, "brick")
    b.air(9, G + 1, 5, 9, G + 2, 7)                    # east door
    slab_roof(b, 3, 3, 9, 9, G + 4, overhang=1)
    b.set(6, G + 1, 4, "chiseled")                     # offering stela
    b.set(6, G + 2, 4, "chiseled")
    # the hidden way down: shaft under a suspicious floor slab
    secret_hatch(b, 6, 7, 3, G, facing="north")
    if not b.pristine:
        crack_seams(b, 3, 3, 9, 9, G + 1, G + 3, count=2)
    b.erode(0.06, min_y=G + 1)


def scribe_house(b):
    """Egyptian small: a roofed scribe's dwelling with a floor-hatch cellar
    still holding the household jars."""
    b.foundation(0, 0, 10, 8)
    # cellar dug into the foundation layers
    room(b, 2, -1, 2, 7, 2, 6, shell="cobble")
    b.pot(3, 0, 3)
    b.pot(6, 0, 5)
    loot_chest(b, 3, 0, 5, facing="east")
    b.fill(0, 2, 0, 10, 2, 8, "floor")
    for x in range(1, 10):
        for z in (1, 7):
            b.fill(x, 3, z, x, 5, z, "brick")
    for z in range(2, 7):
        b.fill(1, 3, z, 1, 5, z, "brick")
        b.fill(9, 3, z, 9, 5, z, "brick")
    b.air(5, 3, 7, 5, 4, 7)                            # south door
    slab_roof(b, 1, 1, 9, 7, 6)
    b.set(3, 3, 2, "minecraft:chiseled_bookshelf[facing=south,slot_0_occupied=true,slot_1_occupied=true,slot_2_occupied=false,slot_3_occupied=true,slot_4_occupied=false,slot_5_occupied=false]")
    ladder_shaft(b, 4, 4, 0, 2, facing="north")        # open hatch to cellar
    b.air(4, 3, 4, 4, 3, 4)
    b.set(6, 2, 3, "chiseled", protect=True)
    b.waystone(6, 3, 3)
    hidden_light(b, 5, 5, 4)
    b.suspicious(2, 2, 6)
    b.erode(0.07, min_y=3)


# ================================================================ GREEK

@ground(7)
def sanctuary_of_echoes(b):
    """A roofless oracle precinct, with a hidden stair behind a broken idol."""
    from archaeology import fragment_floor, standing_column, supported_lintel, wall_remnant, fallen_column
    b.archaeological = True
    G = 7
    W, D = 22, 12
    # ---- oracle chamber below
    room(b, 12, 2, 3, 20, G - 1, 9, shell="brick")
    b.fill(15, 3, 5, 17, 3, 7, "minecraft:calcite")
    b.set(16, 3, 6, "chiseled", protect=True)
    b.waystone(16, 4, 6)                               # the oracle's waystone
    loot_chest(b, 13, 3, 4, facing="east")
    b.pot(19, 3, 8)
    hidden_light(b, 14, 5, 6, level=9)
    # ---- temple above
    b.fill(0, G - 1, 0, W, G - 1, D, "cobble")
    fragment_floor(b, 0, 0, W, D, ground=G)
    cols = [(x, z) for x in range(3, W - 1, 3) for z in (2, D - 2)]
    for x, z in cols:
        whole = b.pristine or (z == 2 and x in (3, 6, 9))
        standing_column(b, x, z, G, 5 if whole else b.rng.choice((0, 1, 2, 3)), complete=whole)
    supported_lintel(b, (3, 2), (6, 2), G+7, G)
    supported_lintel(b, (6, 2), (9, 2), G+7, G)
    # Continuous low wall courses describe the cella; its timber roof is gone.
    for z in (4, D - 4):
        wall_remnant(b, [(x, z, max(0, 4-abs(x-17)//2)) for x in range(3, W-2)], G)
    b.fill(2, G, 5, W-3, G, 7, "floor", protect=True)
    if not b.pristine:
        fallen_column(b, 11, 1, G, 4)
    # cult statue (abstracted) with the hidden stair behind it
    b.fill(W - 5, G + 1, 5, W - 5, G + 4, 7, "minecraft:calcite")
    b.set(W - 5, G + 5, 6, "chiseled")
    # A full flight beside the idol, clear of the oracle's pedestal below.
    # Each step rises one block; clear through the platform, including heads.
    stair = b.resolve("stairs").split("[")[0]
    for i, x in enumerate(range(19, 13, -1)):
        y = G - i
        b.fill(x, y + 1, 8, x, G + 3, 8, "minecraft:air", protect=True)
        b.set(x, y, 8, f"{stair}[facing=east,half=bottom,shape=straight,waterlogged=false]", protect=True)
        if y > 2:
            b.fill(x, 2, 8, x, y - 1, 8, "brick", protect=True)
    passage(b, 13, 3, 8, 13, 7)
    b.suspicious(5, G, 3)
    b.satellite_socket(0, 6, "west_up", y=G - 1)


def wine_villa(b):
    """Greek small: a roofed farm villa over a barrel-vaulted wine cellar -
    the amphorae aged better than the family."""
    b.foundation(0, 0, 12, 9)
    room(b, 2, -1, 2, 10, 2, 7, shell="cobble")
    for x in (3, 5, 7, 9):
        b.pot(x, 0, 3)
    loot_chest(b, 9, 0, 6, facing="north")
    b.suspicious(4, -1, 5)
    b.fill(0, 2, 0, 12, 2, 9, "floor")
    for x in range(1, 12):
        for z in (1, 8):
            b.fill(x, 3, z, x, 4, z, "brick")
    for z in range(2, 8):
        b.fill(1, 3, z, 1, 4, z, "brick")
        b.fill(11, 3, z, 11, 4, z, "brick")
    b.air(6, 3, 8, 6, 4, 8)
    gable_roof(b, 1, 1, 11, 8, 5, axis="x", overhang=1)
    ladder_shaft(b, 3, 5, 0, 2, facing="east")
    b.set(8, 3, 3, "chiseled", protect=True)
    b.waystone(8, 4, 3)
    hidden_light(b, 6, 4, 5)
    b.erode(0.08, min_y=3)


@ground(6)
def nymphaeum(b):
    """An open spring court above a hidden grotto; the timber roof is long gone."""
    from archaeology import (fragment_floor, standing_column, supported_lintel,
                             fallen_column, wall_remnant, quiet_waystone)
    b.archaeological = True
    G = 6
    # grotto below: irregular pool room
    room(b, 3, 1, 2, 13, G - 1, 9, shell="cobble")
    slab = b.resolve("slab").split("[")[0]
    b.fill(5, 1, 4, 11, 1, 7, f"{slab}[type=bottom,waterlogged=true]")
    b.set(8, 2, 5, "minecraft:sea_lantern", protect=True)
    b.pot(4, 2, 3)
    loot_chest(b, 12, 2, 8, facing="west", table=HIDDEN_TREASURY)
    # Preserve the grotto cover. The edge paving extends into a former forecourt.
    b.fill(2, G-1, 1, 14, G-1, 10, "cobble")
    fragment_floor(b, 0, -1, 16, 12, ground=G)
    b.fill(3, G, 2, 13, G, 9, "floor")
    # A single seated architrave bay, then stumps along the former colonnade.
    for x in (3, 6, 9, 12):
        whole = x in (3, 6)
        standing_column(b, x, 2, G, 4 if whole else b.rng.choice((0, 1, 2)), complete=whole)
    supported_lintel(b, (3, 2), (6, 2), G+6, G)
    # Back wall is now a tapering bonded corner rather than an altar cabinet.
    wall_remnant(b, [(x, 10, h) for x, h in zip(range(2, 15), (3,4,4,3,2,2,1,1,0,0,1,1,0))], G)
    wall_remnant(b, [(2, z, h) for z, h in ((7,1), (8,2), (9,3))], G)
    # Water survives in the floor-level catch basin, with a worn spill channel.
    for x in range(3, 7):
        b.set(x, G, 8, f"{slab}[type=bottom,waterlogged=true]", protect=True)
    b.set(6, G, 7, f"{slab}[type=bottom,waterlogged=true]", protect=True)
    fallen_column(b, 11, 0, G, 4)
    quiet_waystone(b, 8, 6, G, facing="south")
    # the way down: gravel-plugged shaft behind the shrine
    secret_hatch(b, 12, 7, 2, G, facing="west")
    # Conceal the discovery behind scattered footings, never beneath the altar.
    b.suspicious(14, G, 9)
    # Sparse footing strips seat the rim where it lies beyond the underground room.
    for (x, y, z), (state, _) in list(b.blocks.items()):
        if y == G and state != "minecraft:air":
            for yy in (G-1, G-2):
                if (x, yy, z) not in b.blocks:
                    b.set(x, yy, z, "cobble")


# ================================================================ BABYLONIAN

MARDUK_TABLET = written_book("Tablet of the Stone Road", "A scribe of the house", [
    "In the house of the god the roads are counted. Each stone that answers is written on clay; each stone that falls silent is written again, and the old tablet broken.",
    "The unbroken tablets are kept below, where the heat cannot crack them. There are more here than there are roads.",
])


@ground(7)
def temple_of_marduk(b):
    """Babylonian grand: a roofed high temple on a buttressed platform; its
    tablet vault below is reached through a capstone inside the temple.

    v1.17: the vault is furnished - a wall of tablet shelves, the scribes'
    tables with their lamps, a lectern holding one readable tablet, and a
    glazed band with sunburst rosettes round the walls."""
    G = 7
    W, D = 18, 14
    vault = (4, 2, 4, 14, G - 1, 10)
    room(b, *vault, shell="brick")                     # tablet vault
    for x in range(5, 14):                             # the tablet wall: two tiers of shelves
        for y in (3, 4):
            bookshelf(b, x, y, 5, "south", filled=(0, 1, 2, 3, 4, 5) if (x + y) % 3 else (0, 2, 3, 5))
    for z in range(6, 10):                             # bitumen-dark pavement, baked-brick border
        for x in range(5, 14):
            edge = x in (5, 13) or z == 9
            b.set(x, 2, z, "minecraft:mud_bricks" if edge else "minecraft:packed_mud")
    lectern(b, 9, 3, 7, "south", book=MARDUK_TABLET)
    for x in (7, 11):                                  # scribes' tables with their lamps
        b.set(x, 3, 7, "minecraft:mud_brick_slab[type=top,waterlogged=false]", protect=True)
        candles(b, x, 4, 7, 3)
    loot_chest(b, 13, 3, 9, facing="west", table=HIDDEN_TREASURY)
    b.pot(5, 3, 9)
    b.pot(5, 3, 8)
    b.suspicious(7, 2, 8)
    frieze(b, vault, 5, "glaze", "minecraft:yellow_glazed_terracotta[facing=south]", period=3)
    for x in (7, 11):
        hanging_lantern(b, x, 5, 8, chain=0)            # flush under the platform, clear of heads
    # platform with alternating buttress bays
    b.fill(0, G - 1, 0, W, G - 1, D, "cobble")
    b.fill(0, G, 0, W, G, D, "floor")
    for x in range(0, W + 1):
        depth = 1 if (x // 3) % 2 == 0 else 0
        for z in (0 + depth, D - depth):
            grad_wall(b, x, G + 1, z, x, G + 5, z, "brick", "cobble", "cobble", ground_y=G)
    b.air(8, G + 1, D - 1, 10, G + 3, D)               # south gate
    glazed_frieze(b, 1, D, W - 1, G + 3, G + 4, rosette_every=4)
    merlons(b, 0, 0, W, D, G + 6, role="glaze")
    slab_roof(b, 1, 1, W - 1, D - 1, G + 6)
    # cella: waystone before the god's empty seat
    b.fill(7, G + 1, 2, 11, G + 2, 3, "glaze")
    b.set(9, G + 3, 2, "minecraft:gold_block", protect=True)
    b.set(9, G + 1, 5, "chiseled", protect=True)
    b.waystone(9, G + 2, 5, facing="south")
    # A hatch inside the temple connects directly to the vault. The old
    # east-face opening was buried below grade and stopped outside its wall.
    secret_hatch(b, 12, 8, 3, G, facing="north", lining="brick")
    hidden_light(b, 9, G + 4, 7)
    b.satellite_socket(9, 0, "north_up", y=G - 1)
    b.satellite_socket(0, 7, "west_up", y=G - 1)
    if not b.pristine:
        crack_seams(b, 0, 0, W, D, G + 1, G + 5, count=3)
        collapse_wedge(b, b.rng.randint(3, 15), G + 6, 0, 3, "east", (2, G, W - 2, 3))
    b.erode(0.05, min_y=G + 3)
    b.rubble(1, 1, W - 1, D - 1, 5, y=G)


def merchant_karum(b):
    """Babylonian small: a roofed trading post with a sealed goods cellar -
    the ledgers say something down there was never collected."""
    b.foundation(0, 0, 11, 9)
    room(b, 2, -1, 2, 9, 2, 7, shell="cobble")
    loot_chest(b, 3, 0, 3, facing="south", table=HIDDEN_TREASURY)
    loot_chest(b, 8, 0, 6, facing="north", table=HIDDEN_TREASURY)
    b.pot(3, 0, 6)
    b.fill(0, 2, 0, 11, 2, 9, "floor")
    for x in range(1, 11):
        for z in (1, 8):
            b.fill(x, 3, z, x, 5, z, "brick")
    for z in range(2, 8):
        b.fill(1, 3, z, 1, 5, z, "brick")
        b.fill(10, 3, z, 10, 5, z, "brick")
    b.air(5, 3, 1, 6, 4, 1)                            # north door
    glazed_frieze(b, 2, 1, 9, 4, 4, rosette_every=5)
    b.fill(5, 3, 1, 6, 4, 1, "minecraft:air", protect=True)
    slab_roof(b, 1, 1, 10, 8, 6)
    secret_hatch(b, 7, 4, 0, 2)
    b.set(5, 2, 5, "chiseled", protect=True)
    b.waystone(5, 3, 5)
    hidden_light(b, 5, 5, 4)
    b.erode(0.07, min_y=3)


@ground(12)
def underworld_gate(b):
    """Babylonian grand: a modest surface shrine over a long vaulted stair
    plunging to the Gate of the Underworld - and the waystone beyond it.
    The stair mouth is plugged with gravel; the dead prefer quiet."""
    G = 12
    # ---- the deep gate chamber (y2..8)
    room(b, 2, 2, 2, 14, 8, 12, shell="brick")
    for x0 in (4, 10):
        b.fill(x0, 3, 6, x0 + 1, 7, 8, "glaze")        # the twin gate piers
    corbel_arch(b, 7, 3, 7, 4, axis="x")
    b.set(8, 3, 10, "chiseled", protect=True)
    b.waystone(8, 4, 10, facing="north")               # beyond the gate
    loot_chest(b, 3, 3, 11, facing="east")
    b.pot(13, 3, 3)
    b.suspicious(8, 2, 5)
    hidden_light(b, 8, 6, 7, level=7)
    # ---- a full one-block-rise flight, from the crypt to the south porch
    steps = [(z, 3 + z - 12) for z in range(12, 22)]
    stair = b.resolve("stairs").split("[")[0]
    for z, y in steps:
        for x in (7, 8):
            b.fill(x, y + 1, z, x, y + 3, z, "minecraft:air", protect=True)
            b.set(x, y, z, f"{stair}[facing=south,half=bottom,shape=straight,waterlogged=false]", protect=True)
            for yy in range(2, y):
                b.set(x, yy, z, "brick")
        for wx in (6, 9):
            b.fill(wx, y, z, wx, y + 3, z, "brick")
        b.fill(7, y + 4, z, 8, y + 4, z, "brick")
    # ---- surface shrine
    b.fill(4, G, 20, 12, G, 26, "floor")
    for x in range(5, 12):
        for z in (21, 25):
            b.fill(x, G + 1, z, x, G + 3, z, "brick")
    merlons(b, 5, 21, 11, 25, G + 4, role="glaze")
    slab_roof(b, 5, 21, 11, 25, G + 4)
    b.set(10, G + 1, 23, "chiseled")                   # cenotaph beside the stair
    glazed_frieze(b, 5, 21, 11, G + 2, G + 2, rosette_every=3)
    b.fill(7, G + 1, 21, 8, G + 3, 25, "minecraft:air", protect=True)
    # Re-open the stair through the porch floor after constructing the shrine.
    for z, y in steps:
        for x in (7, 8):
            b.fill(x, y + 1, z, x, y + 3, z, "minecraft:air", protect=True)
            b.set(x, y, z, f"{stair}[facing=south,half=bottom,shape=straight,waterlogged=false]", protect=True)
    hidden_light(b, 8, G + 3, 23)
    if not b.pristine:
        crack_seams(b, 4, 20, 12, 26, G + 1, G + 3, count=2)
    b.erode(0.06, min_y=G + 1)


# ================================================================ VIKING

def turf_longhouse(b):
    """Viking grand: an intact turf-roofed longhouse - roof to the ground,
    smoke hole over a long hearth - with a root cellar under the floor."""
    W, D = 20, 10
    b.foundation(0, 0, W, D)
    room(b, 3, -1, 3, 9, 2, 7, shell="cobble")         # standing-height root cellar
    loot_chest(b, 4, 0, 4, facing="east")
    b.pot(8, 0, 6)
    b.fill(1, 2, 1, W - 1, 2, D - 1, "floor")
    for x in range(2, W - 1):                          # low stave walls
        for z in (2, D - 2):
            if x % 3 == 2:
                b.column(x, 3, z, 2, "pillar")
            else:
                b.fill(x, 3, z, x, 4, z, "plank")
    for gx in (2, W - 2):
        b.fill(gx, 3, 3, gx, 4, D - 3, "plank")
    b.air(W - 2, 3, 4, W - 2, 4, 5)                    # east door
    # full turf roof with sway, eaves on the ground. v1.16: the eave course
    # starts at y3 so the wall-line course (y5) rests on the y4 wall top;
    # it used to hover two blocks above the walls.
    gable_roof(b, 2, 1, W - 2, D - 1, 3, axis="x", overhang=1, sway=1)
    gable_ends(b, (2, W - 2), 2, 1, W - 2, D - 1, 3, 4)
    for (x, y, z), (state, _) in list(b.blocks.items()):
        if "stairs" in state and y >= 4 and b.rng.random() < 0.75:
            if (x, y + 1, z) not in b.blocks:
                b.set(x, y + 1, z, "minecraft:moss_carpet")
    for x in range(9, 12):                             # smoke hole over hearth
        for y in (7, 8):                               # ridge sags to 7 mid-run
            b.clear(x, y, 5)
    for (x, y, z), (state, _) in list(b.blocks.items()):   # the turf ridge stays whole
        if z == 5 and "_slab" in state and y >= 7:
            b.protected.add((x, y, z))
    for x in range(8, 13):                             # hearth line
        b.set(x, 2, 5, "minecraft:coarse_dirt")
        if x % 2 == 0:
            b.set(x, 3, 5, "minecraft:campfire[lit=false,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    slabp = "minecraft:spruce_slab"
    for x in range(3, W - 2):                          # sleeping platforms
        b.set(x, 3, 3, f"{slabp}[type=top,waterlogged=false]")
        b.set(x, 3, D - 3, f"{slabp}[type=top,waterlogged=false]")
    ladder_shaft(b, 5, 5, 0, 2, facing="north")        # cellar hatch
    b.air(5, 3, 5, 5, 3, 5)
    b.set(3, 3, 5, "chiseled", protect=True)
    b.waystone(3, 4, 5, facing="east")
    hidden_light(b, 10, 5, 5, level=10)
    b.suspicious(15, 2, 4)
    b.satellite_socket(W, 5, "east_up")
    b.erode(0.05, min_y=3)


@ground(6)
def seer_hut(b):
    """Viking small: a turf-roofed seer's hut; beneath the floorboards, the
    völva's ritual pit with the waystone she consulted."""
    G = 6
    pit = (3, 1, 2, 11, G - 1, 8)
    room(b, *pit, shell="cobble")                      # ritual pit
    b.set(7, 2, 5, "chiseled", protect=True)
    b.waystone(7, 3, 5)                                # the hidden waystone
    for x, z in ((4, 3), (10, 7), (4, 7), (10, 3)):
        b.set(x, 2, z, "minecraft:soul_lantern[hanging=false,waterlogged=false]", protect=True)
    # v1.17: the völva's pit is furnished. Timber posts and a band of rune
    # stones line the walls, a rune circle is set in the floor round the
    # stone, her high seat faces it across a seeing-bowl and the bones she
    # read; amethyst grows where she kept her crystals.
    frieze(b, pit, 3, "cobble", "chiseled", period=2)
    for x, z, _ in wall_cells(pit):
        if (x + z) % 3 == 0:
            b.fill(x, 2, z, x, 4, z, "minecraft:spruce_log[axis=y]")
    for x, z in ((5, 5), (7, 3), (7, 7), (6, 4), (8, 4), (6, 6), (8, 6)):
        b.set(x, 1, z, "minecraft:chiseled_stone_bricks")
    b.set(5, 2, 5, "minecraft:spruce_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]", protect=True)
    loot_chest(b, 4, 2, 5, facing="east", table=HIDDEN_TREASURY)
    b.set(10, 2, 6, "minecraft:water_cauldron[level=3]", protect=True)
    b.pot(10, 2, 4)
    b.set(10, 2, 5, "minecraft:bone_block[axis=y]", protect=True)
    floor_skull(b, 10, 3, 5, rotation=4)
    for x, z in ((5, 3), (9, 7)):
        b.set(x, 2, z, "minecraft:amethyst_cluster[facing=up,waterlogged=false]", protect=True)
    candles(b, 5, 3, 7, 2, color="black")
    b.set(5, 2, 7, "minecraft:spruce_planks", protect=True)
    for x, z in ((6, 3), (8, 7), (9, 4)):
        roots(b, x, 4, z)
    b.suspicious(7, 1, 3)
    # hut above. v1.16: two-course walls, the roof rectangle drawn on the
    # walls themselves so its eave course meets the wall top, gables closed.
    b.fill(3, G, 2, 11, G, 8, "floor")
    for x in range(4, 11):
        for z in (3, 7):
            b.fill(x, G + 1, z, x, G + 2, z, "plank")
    for gx in (4, 10):
        b.fill(gx, G + 1, 4, gx, G + 2, 6, "plank")
    b.air(10, G + 1, 5, 10, G + 2, 5)
    gable_roof(b, 4, 3, 10, 7, G + 2, axis="x", overhang=1)
    gable_ends(b, (4, 10), 4, 3, 10, 7, G + 2, G + 2)
    for (x, y, z), (state, _) in list(b.blocks.items()):
        if "stairs" in state and y >= G + 2 and b.rng.random() < 0.7:
            if (x, y + 1, z) not in b.blocks:
                b.set(x, y + 1, z, "minecraft:moss_carpet")
    secret_hatch(b, 8, 5, 2, G, facing="west")         # beside the ritual stone
    b.set(5, G + 1, 4, "minecraft:campfire[lit=false,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    if not b.pristine:
        crack_seams(b, 3, 2, 11, 8, G, G + 1, count=1)
    b.erode(0.07, min_y=G + 1)


def drakkar_shed(b):
    """Viking grand: a roofed boathouse, doors fallen, the ribs of an unsunk
    longship still on the stocks inside."""
    W, D = 18, 10
    b.foundation(0, 0, W, D)
    b.fill(1, 2, 1, W - 1, 2, D - 1, "minecraft:coarse_dirt")
    b.fill(2, 2, 3, W - 2, 2, 7, "floor")
    for x in range(1, W):                              # walls, open west gable
        for z in (1, D - 1):
            if x % 4 == 1:
                b.column(x, 3, z, 3, "pillar")
            else:
                b.fill(x, 3, z, x, 4, z, "plank")
    b.fill(W - 1, 3, 2, W - 1, 5, D - 2, "plank")
    gable_roof(b, 1, 1, W - 1, D - 1, 6, axis="x", overhang=1)
    # the ship: keel line + rising stem/stern + rib stubs
    for x in range(4, 14):
        b.set(x, 3, 5, "minecraft:dark_oak_planks")
    for i, x in enumerate((3, 2)):
        b.set(x, 4 + i, 5, "minecraft:dark_oak_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]")
    for i, x in enumerate((14, 15)):
        b.set(x, 4 + i, 5, "minecraft:dark_oak_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]")
    for x in (5, 8, 11):
        b.set(x, 4, 4, "minecraft:dark_oak_fence[north=false,south=false,east=false,west=false,waterlogged=false]")
        b.set(x, 4, 6, "minecraft:dark_oak_fence[north=false,south=false,east=false,west=false,waterlogged=false]")
    b.set(2, 2, 2, "chiseled", protect=True)
    b.waystone(2, 3, 2, facing="south")
    loot_chest(b, W - 3, 3, 3, facing="south")
    b.suspicious(9, 1, 5)
    hidden_light(b, 9, 5, 5, level=10)
    b.satellite_socket(0, 5, "west_up")
    if not b.pristine:
        crack_seams(b, 1, 1, W - 1, D - 1, 3, 4, count=2)
    b.erode(0.08, min_y=3)


# ================================================================ MAYAN

@ground(8)
def serpent_pyramid(b):
    """Mayan grand: a roofed summit shrine on a stepped pyramid whose core
    hides an inner stair winding down to a sacred well."""
    G = 8
    W = D = 20
    # ---- inner well chamber below grade (v1.17: four high, furnished)
    well = (6, 2, 6, 14, G - 1, 14)
    room(b, *well, shell="brick")
    b.fill(9, 2, 9, 11, 2, 11, "minecraft:water")
    b.fill(9, 1, 9, 11, 1, 11, "minecraft:gravel")
    b.set(7, 3, 7, "chiseled", protect=True)
    b.waystone(7, 4, 7, facing="south")                # the well waystone
    for x, z in ((6, 7), (7, 6)):                      # jade panels in the walls beside it
        b.fill(x, 4, z, x, 5, z, "minecraft:dark_prismarine", protect=True)
    frieze(b, well, 5, "minecraft:red_terracotta", "minecraft:chiseled_stone_bricks", period=2)
    inner_cornice(b, well, 6, "minecraft:mossy_stone_brick_stairs", "minecraft:chiseled_stone_bricks")
    for x in (8, 12):                                  # candle posts at the pool's corners
        for z in (8, 12):
            b.set(x, 3, z, "minecraft:mossy_cobblestone_wall[east=none,north=none,south=none,up=true,waterlogged=false,west=none]", protect=True)
            candles(b, x, 4, z, 3)
    b.set(10, 3, 13, "minecraft:chiseled_stone_bricks", protect=True)   # offering stone at the water
    floor_skull(b, 10, 4, 13, rotation=8)
    loot_chest(b, 13, 3, 13, facing="north", table=HIDDEN_TREASURY)
    b.pot(13, 3, 7)
    b.suspicious(10, 1, 10)
    for x, z in ((9, 10), (11, 9), (10, 12)):          # the jungle's roots through the vault
        roots(b, x, 6, z)
    lichen(b, 13, 4, 10, "east")
    lichen(b, 7, 4, 11, "west")
    for x in (8, 12):
        hanging_lantern(b, x, 5, 10)
    # ---- pyramid tiers from grade
    for t, (y0, inset) in enumerate(((G, 1), (G + 2, 3), (G + 4, 5), (G + 6, 7))):
        b.fill(inset, y0, inset, W - inset, y0 + 1, W - inset, "brick")
        for x in range(inset, W - inset + 1):          # talud-tablero frame
            b.set(x, y0 + 1, inset, "accent")
            b.set(x, y0 + 1, W - inset, "accent")
    # grand stair south with serpent balustrades
    stair = b.resolve("stairs").split("[")[0]
    for i in range(8):
        y = G + i
        z = W - 1 - i
        for x in (9, 10, 11):
            b.fill(x, y + 1, z, x, y + 3, z, "minecraft:air", protect=True)
            b.set(x, y, z, f"{stair}[facing=north,half=bottom,shape=straight,waterlogged=false]", protect=True)
            if y > G:
                b.fill(x, G, z, x, y - 1, z, "brick", protect=True)
        for bx in (8, 12):
            b.fill(bx, y, z, bx, y + 1, z, "accent")
    for bx in (8, 12):                                 # serpent heads at base
        b.set(bx, G, W, "accent")
        b.set(bx, G + 1, W, f"{stair}[facing=south,half=bottom,shape=straight,waterlogged=false]")
    # summit shrine, roofed, with the inner stair down
    b.hollow_box(7, G + 8, 7, 13, G + 11, 13, "brick")
    b.air(8, G + 8, 8, 12, G + 10, 12)
    b.air(10, G + 8, 13, 10, G + 9, 13)                # south door
    b.fill(10, G + 8, 13, 10, G + 10, 13, "minecraft:air", protect=True)
    b.fill(8, G + 7, 8, 12, G + 7, 11, "floor", protect=True)
    b.fill(8, G + 12, 8, 12, G + 12, 12, "brick")      # roof
    for x in range(8, 13):                             # roof comb, perforated
        for y in range(G + 13, G + 15):
            if (x + y) % 2 == 0:
                b.set(x, y, 10, "brick")
    # the secret: floor slab in the shrine opens the descent
    secret_hatch(b, 8, 9, 3, G + 7, facing="east")     # continuous return route
    b.suspicious(4, G, 4)
    b.satellite_socket(0, 10, "west_up", y=G - 1)
    b.satellite_socket(W, 10, "east_up", y=G - 1)
    if not b.pristine:
        vine_creep(b, prob_low=0.3, prob_high=0.08, cutoff=G + 4)
        for _ in range(16):
            x, z = b.rng.randint(1, W - 1), b.rng.randint(1, W - 1)
            for y in range(G + 7, G - 1, -1):
                if (x, y, z) in b.blocks and (x, y + 1, z) not in b.blocks:
                    b.set(x, y + 1, z, "minecraft:moss_carpet")
                    break
    b.erode(0.05, min_y=G + 2)


@ground(6)
def jungle_palace(b):
    """Mayan grand: a roofed range palace - corbel-vaulted rooms round a
    court - with a tunnel under the throne to a treasury."""
    G = 6
    W, D = 22, 14
    room(b, 14, 2, 4, 20, G - 1, 10, shell="brick")    # treasury
    loot_chest(b, 19, 3, 5, facing="west", table=HIDDEN_TREASURY)
    loot_chest(b, 19, 3, 9, facing="west", table=HIDDEN_TREASURY)
    b.pot(15, 3, 9)
    b.suspicious(17, 2, 7)
    hidden_light(b, 17, 4, 7, level=8)
    # palace platform + two roofed ranges
    b.fill(0, G - 1, 0, W, G - 1, D, "cobble")
    b.fill(0, G, 0, W, G, D, "floor")
    for z0, z1 in ((1, 4), (D - 4, D - 1)):
        b.fill(1, G + 1, z0, W - 1, G + 4, z0, "brick")
        b.fill(1, G + 1, z1, W - 1, G + 4, z1, "brick")
        for x in range(1, W):                          # corbel-vault roofline
            b.set(x, G + 5, z0 + 1 if z0 < 5 else z0, "brick")
            stair = b.resolve("stairs").split("[")[0]
        b.fill(1, G + 5, z0, W - 1, G + 5, z1, "brick")
        b.fill(2, G + 6, z0 + 1, W - 2, G + 6, z1 - 1, "brick")
        for dx in range(3, W - 2, 4):                  # corbel doorways
            corbel_arch(b, dx, G + 1, z0 if z0 > 5 else z1, 2, axis="x")
    string_course(b, 1, 1, W - 1, D - 1, G + 4, "accent")
    # throne against the north range + hidden tunnel beneath
    b.fill(9, G + 1, 3, 11, G + 1, 3, "accent")
    b.set(10, G + 2, 3, f"{b.resolve('stairs').split('[')[0]}[facing=south,half=bottom,shape=straight,waterlogged=false]")
    passage(b, 10, 3, 5, 15, 5)                       # cross the treasury wall
    secret_hatch(b, 10, 5, 3, G, facing="south")       # beside the throne step
    b.set(10, G + 1, 8, "chiseled", protect=True)
    b.waystone(10, G + 2, 8)                           # court waystone
    hidden_light(b, 10, G + 3, 6)
    b.satellite_socket(0, 7, "west_up", y=G - 1)
    b.satellite_socket(W, 7, "east_up", y=G - 1)
    if not b.pristine:
        vine_creep(b, prob_low=0.35, prob_high=0.1, cutoff=G + 3)
        collapse_wedge(b, b.rng.randint(4, 18), G + 6, D - 3, 3, "east", (2, G, W - 2, D - 4))
        crack_seams(b, 1, 1, W - 1, D - 1, G + 1, G + 4, count=3)
    b.erode(0.06, min_y=G + 2)
    b.rubble(1, 1, W - 1, D - 1, 7, y=G)


@ground(7)
def chultun_house(b):
    """Mayan small: a roofed hut over a bottle-shaped chultun cistern; the
    capstone in the floor is not like the other stones."""
    G = 7
    # bottle cistern: narrow neck, wide belly
    room(b, 4, 1, 3, 10, 4, 9, shell="cobble")         # standing-height belly
    b.air(7, 4, 6, 7, G - 1, 6)                        # neck
    b.fill(6, 4, 5, 8, 4, 7, "cobble")
    b.air(7, 4, 6, 7, 4, 6)
    loot_chest(b, 5, 2, 4, facing="east", table=HIDDEN_TREASURY)
    b.pot(9, 2, 8)
    b.suspicious(7, 1, 5)
    # hut above
    b.fill(3, G, 2, 11, G, 10, "floor")
    for x in range(4, 11):
        for z in (3, 9):
            b.fill(x, G + 1, z, x, G + 2, z, "brick")
    for gx in (4, 10):
        b.fill(gx, G + 1, 4, gx, G + 2, 8, "brick")
    b.air(10, G + 1, 6, 10, G + 2, 6)
    # v1.16: roof drawn on the wall rectangle with its eave at the wall top
    # (it floated two blocks clear of the walls), gable triangles closed.
    gable_roof(b, 4, 3, 10, 9, G + 2, axis="x", overhang=1)
    gable_ends(b, (4, 10), 4, 3, 10, 9, G + 2, G + 2, role="brick")
    secret_hatch(b, 7, 6, 2, G, facing="north")        # the capstone
    b.set(5, G + 1, 5, "chiseled", protect=True)
    b.waystone(5, G + 2, 5)
    hidden_light(b, 7, G + 2, 7)
    if not b.pristine:
        vine_creep(b, prob_low=0.25, prob_high=0.08, cutoff=G + 2)
    b.erode(0.07, min_y=G + 1)


# ============================================================= NETHER / END

def chained_sepulcher(b):
    """Nether: a two-level sepulcher - the upper hall's floor has failed in
    one bay, dropping into a bone-lined undercroft."""
    b.hollow_box(0, 0, 0, 12, 12, 14, "brick")
    b.rooms = [(0, 0, 0, 12, 6, 14), (0, 6, 0, 12, 12, 14)]
    b.fill(1, 6, 1, 11, 6, 13, "floor")                # upper floor
    b.air(1, 7, 1, 11, 11, 13)
    b.air(1, 1, 1, 11, 5, 13)
    b.fill(1, 0, 1, 11, 0, 13, "floor")
    b.air(7, 6, 8, 10, 6, 12)                          # the failed bay
    ladder_shaft(b, 10, 10, 1, 6, facing="west")       # a return from the lower hall
    for x, z in ((3, 3), (9, 3), (3, 11)):
        b.column(x, 1, z, 5, "pillar")
    for z in (4, 8, 12):
        b.fill(1, 1, z, 1, 3, z, "minecraft:bone_block[axis=y]")
        b.fill(11, 1, z, 11, 3, z, "minecraft:bone_block[axis=y]")
    for _ in range(7):
        x, z = b.rng.randint(2, 10), b.rng.randint(2, 12)
        for i in range(b.rng.randint(1, 3)):
            b.set(x, 11 - i, z, "minecraft:chain[axis=y,waterlogged=false]")
    sarcophagus(b, 5, 1, 6, axis="z", lid="chiseled")
    b.set(6, 7, 3, "chiseled", protect=True)
    b.waystone(6, 8, 3)                                # upper hall waystone
    loot_chest(b, 2, 1, 12, facing="east")
    b.pot(10, 1, 2)
    b.suspicious(8, 0, 10)
    b.set(3, 7, 11, "minecraft:soul_campfire[lit=true,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    hidden_light(b, 6, 9, 7, level=9)
    b.rubble(1, 1, 11, 13, 8, y=1)
    b.erode(0.04, min_y=7)
    b.breach(0, 7, 0, 12, 11, 14, count=3)


@ground(4)
def shard_monastery(b):
    """End: a roofed purpur cloister; below its floor, a reliquary crypt
    holds what the monks refused to let fall into the void."""
    W, D = 16, 14
    # crypt below
    room(b, 4, 0, 4, 12, 3, 10, shell="brick")
    b.fill(7, 1, 6, 9, 1, 8, "minecraft:obsidian")
    b.set(8, 2, 7, "minecraft:crying_obsidian", protect=True)
    loot_chest(b, 5, 1, 9, facing="east")
    b.pot(11, 1, 5)
    # cloister
    b.fill(2, 4, 2, W - 2, 4, D - 2, "floor")
    for x in range(3, W - 2, 3):
        for z in (3, D - 3):
            b.column(x, 5, z, 4, "pillar", cap="chiseled")
    for z in (5, 7, 9):
        b.column(3, 5, z, 4, "pillar")
        b.column(W - 3, 5, z, 4, "pillar")
    b.fill(3, 9, 3, W - 3, 9, D - 3, "brick")          # roof ring
    b.fill(5, 10, 5, W - 5, 10, D - 5, "brick")        # raised center roof
    for x, z in ((3, 3), (W - 3, 3), (3, D - 3), (W - 3, D - 3)):
        b.set(x, 10, z, "minecraft:end_rod[facing=up]", protect=True)
    b.air(6, 5, 6, W - 6, 8, D - 6)                    # open court under center
    b.set(8, 4, 7, "chiseled", protect=True)
    b.waystone(8, 5, 7)
    ladder_shaft(b, 5, 5, 1, 4, facing="east")         # crypt access, open
    for fx, fy, fz in ((0, 7, 1), (W - 1, 12, 2), (1, 11, D - 1)):
        b.fill(fx, fy, fz, fx + 1, fy + 1, fz + 1, "cobble")
    hidden_light(b, 8, 7, 7, level=11)
    b.suspicious(10, 4, 10)
    b.erode(0.05, min_y=5)


# ================================================== the Waybuilders themselves

def waybuilder_workshop(b):
    """Default theme grand: the mason's lodge where waystones were cut - a
    roofed workshop over a pattern-vault holding the Waybuilders' secrets."""
    W, D = 16, 12
    b.foundation(0, 0, W, D)
    room(b, 3, -1, 3, 13, 2, 9, shell="brick")         # pattern vault
    loot_chest(b, 4, 0, 4, facing="south")
    loot_chest(b, 12, 0, 8, facing="north")
    b.pot(4, 0, 8)
    b.suspicious(8, -1, 6)
    b.set(8, 0, 4, "chiseled", protect=True)           # half-cut waystone blank
    b.fill(0, 2, 0, W, 2, D, "floor")
    for x in range(1, W):
        for z in (1, D - 1):
            b.fill(x, 3, z, x, 5, z, "brick")
    for z in range(2, D - 1):
        b.fill(1, 3, z, 1, 5, z, "brick")
        b.fill(W - 1, 3, z, W - 1, 5, z, "brick")
    b.air(8, 3, D - 1, 9, 4, D - 1)                    # south doors
    pilasters(b, 2, 1, W - 2, 3, 5, period=5, depth_dz=1, role="accent")
    gable_roof(b, 1, 1, W - 1, D - 1, 6, axis="x", overhang=1)
    # the shop floor: workbenches, a crane post, waystone blanks in progress
    b.set(3, 3, 3, "minecraft:grindstone[face=floor,facing=north]", protect=True)
    b.set(5, 3, 3, "minecraft:smithing_table")
    for cy in range(3, 7):                             # crane post
        b.set(11, cy, 6, "minecraft:spruce_log[axis=y]")
    b.set(11, 7, 6, "minecraft:chain[axis=y,waterlogged=false]")
    b.set(12, 3, 3, "chiseled")                        # blanks
    b.set(13, 3, 4, "chiseled")
    b.set(4, 3, 8, "chiseled", protect=True)
    b.waystone(4, 4, 8, facing="east")                 # the first waystone?
    ladder_shaft(b, 12, 6, 0, 2, facing="west")
    b.air(12, 3, 6, 12, 3, 6)
    hidden_light(b, 8, 5, 6)
    b.satellite_socket(0, 6, "west_up")
    b.satellite_socket(W, 6, "east_up")
    if not b.pristine:
        crack_seams(b, 1, 1, W - 1, D - 1, 3, 5, count=2)
        collapse_wedge(b, b.rng.randint(3, 13), 6, 1, 3, "east", (2, 2, W - 2, 4))
    b.erode(0.06, min_y=3)
    b.rubble(1, 1, W - 1, D - 1, 5)


EGYPT_SMALL3 = {"scribe_house": scribe_house}
EGYPT_GRAND3 = {"temple_of_ra": temple_of_ra, "nomarch_tomb": nomarch_tomb}
GREEK_SMALL3 = {"wine_villa": wine_villa, "nymphaeum": nymphaeum}
GREEK_GRAND3 = {"sanctuary_of_echoes": sanctuary_of_echoes}
BABYLON_SMALL3 = {"merchant_karum": merchant_karum}
BABYLON_GRAND3 = {"temple_of_marduk": temple_of_marduk, "underworld_gate": underworld_gate}
VIKING_SMALL3 = {"seer_hut": seer_hut}
VIKING_GRAND3 = {"turf_longhouse": turf_longhouse, "drakkar_shed": drakkar_shed}
MAYAN_SMALL3 = {"chultun_house": chultun_house}
MAYAN_GRAND3 = {"serpent_pyramid": serpent_pyramid, "jungle_palace": jungle_palace}
NETHER3 = {"chained_sepulcher": chained_sepulcher}
END3 = {"shard_monastery": shard_monastery}
DEFAULT_GRAND3 = {"waybuilder_workshop": waybuilder_workshop}

ALL3 = {}
for d in (EGYPT_SMALL3, EGYPT_GRAND3, GREEK_SMALL3, GREEK_GRAND3,
          BABYLON_SMALL3, BABYLON_GRAND3, VIKING_SMALL3, VIKING_GRAND3,
          MAYAN_SMALL3, MAYAN_GRAND3, NETHER3, END3, DEFAULT_GRAND3):
    ALL3.update(d)


# cutaway render heights (template y; blocks above are stripped in the _cutaway view)
temple_of_ra.cutaway = 14
nomarch_tomb.cutaway = 7
scribe_house.cutaway = 5
sanctuary_of_echoes.cutaway = 6
wine_villa.cutaway = 4
nymphaeum.cutaway = 5
temple_of_marduk.cutaway = 6
merchant_karum.cutaway = 4
underworld_gate.cutaway = 8
turf_longhouse.cutaway = 6
seer_hut.cutaway = 5
drakkar_shed.cutaway = 6
serpent_pyramid.cutaway = 7
jungle_palace.cutaway = 5
chultun_house.cutaway = 4
chained_sepulcher.cutaway = 8
shard_monastery.cutaway = 5
waybuilder_workshop.cutaway = 6
