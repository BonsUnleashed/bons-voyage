"""v1.9 batch 3: the deep dungeons. Modest roofed surfaces over extreme
multi-level undergrounds - decoy tombs, a carved labyrinth, buried ship
halls, stacked archives - full of staged secrets (false floors, weak walls,
plugged shafts), monster spawners, and crypt loot. Each design declares
fn.ground (walking level) and fn.section (z slice for the ant-farm render).
"""
from master import (grad_wall, string_course, cornice, pilasters, corbel_arch,
                    battered_wall, column_stump, crack_seams, collapse_wedge,
                    vine_creep, hidden_light, merlons, glazed_frieze, gable_roof,
                    room, loot_chest, ladder_shaft, weak_wall, false_floor,
                    sarcophagus, slab_roof, passage, secret_hatch)
from dungeon import spawner, maze_carve
from interiors import candles, hanging_lantern, lectern, written_book
from loot import HIDDEN_TREASURY, HOARD


def attrs(ground, section):
    def deco(fn):
        fn.ground = ground
        fn.section = section
        return fn
    return deco


# ================================================================ EGYPTIAN

@attrs(24, 8)
def valley_sepulcher(b):
    """Egyptian mega-tomb: a small mortuary chapel over three descending
    levels - a hall of false doors, a pillared deep hall with its guardian,
    and the true vault behind crumbling masonry."""
    G = 24
    W, D = 24, 16
    # ---- L3: true vault (y2..7), west end
    room(b, 2, 2, 5, 10, 7, 11, shell="brick")
    sarcophagus(b, 4, 3, 7, axis="x")
    b.set(4, 3, 10, "chiseled", protect=True)
    b.waystone(4, 4, 10, facing="east")
    b.fill(8, 3, 6, 8, 3, 7, "minecraft:gold_block")
    loot_chest(b, 3, 3, 6, facing="south", table=HOARD)
    loot_chest(b, 9, 3, 10, facing="west", table=HOARD)
    b.pot(9, 3, 6)
    b.suspicious(6, 2, 9)
    hidden_light(b, 6, 5, 8, level=8)
    # ---- L2: pillared deep hall (y8..14), center
    room(b, 8, 9, 3, 20, 14, 13, shell="brick")
    for x, z in ((11, 6), (11, 10), (17, 6), (17, 10)):
        b.column(x, 10, z, 4, "brick")
    spawner(b, 14, 10, 8, "husk")
    b.pot(9, 10, 4)
    b.pot(19, 10, 12)
    b.suspicious(12, 9, 11)
    # decoy sarcophagus - empty, looted long ago
    sarcophagus(b, 15, 10, 4, axis="x")
    # The west alcove descends through the floor to the true vault.
    secret_hatch(b, 9, 8, 3, 9, facing="north")
    # ---- L1: hall of false doors (y16..22), east
    room(b, 12, 16, 4, 22, 22, 12, shell="brick")
    for z in (5, 8, 11):                                # three ornate false doors
        b.fill(21, 17, z, 21, 19, z, "chiseled")
        b.set(21, 18, z, "accent")
    secret_hatch(b, 13, 8, 10, 16, facing="east", lining="brick")
    b.pot(14, 17, 5)
    b.pot(20, 17, 11)
    hidden_light(b, 17, 20, 8, level=8)
    # ---- surface chapel (yG..): battered walls, slab roof
    b.fill(13, G, 5, 21, G, 11, "floor")
    for x in range(14, 21):
        for z in (6, 10):
            b.fill(x, G + 1, z, x, G + 3, z, "brick")
    b.fill(14, G + 1, 7, 14, G + 3, 9, "brick")
    b.air(20, G + 1, 8, 21, G + 2, 8)                   # east door
    slab_roof(b, 14, 6, 20, 10, G + 4)
    cornice(b, 14, 6, 20, 10, G + 3)
    b.set(15, G + 1, 8, "chiseled")                     # offering stone
    secret_hatch(b, 17, 8, 17, G, facing="north")
    if not b.pristine:
        crack_seams(b, 13, 5, 21, 11, G + 1, G + 3, count=2)
    b.erode(0.06, min_y=G + 1)


# ================================================================ GREEK

@attrs(18, 17)
def labyrinth_of_the_bull(b):
    """Greek mega-dungeon: a lone round shrine above; beneath, a true carved
    labyrinth whose farthest turn holds the bull's chamber, its keeper, and
    the prize it guards."""
    G = 18
    S = 33                                              # labyrinth footprint
    # ---- labyrinth level (y3..9): solid mass, maze carved through it
    b.fill(1, 2, 1, S - 1, 2, S - 1, "floor")
    b.fill(1, 3, 1, S - 1, 8, S - 1, "brick")
    b.fill(1, 9, 1, S - 1, 9, S - 1, "brick")           # ceiling
    far = maze_carve(b, 2, 3, 2, 14, 14, height=3)
    fx, fz = far
    # the bull's chamber at the farthest cell: enlarge and furnish
    b.air(max(2, fx - 2), 3, max(2, fz - 2), min(S - 2, fx + 2), 6, min(S - 2, fz + 2))
    b.fill(max(2, fx - 2), 2, max(2, fz - 2), min(S - 2, fx + 2), 2, min(S - 2, fz + 2), "floor")
    spawner(b, fx, 3, fz, "vindicator")
    b.set(fx - 1, 3, fz - 1, "chiseled", protect=True)
    b.waystone(fx - 1, 4, fz - 1)
    loot_chest(b, fx + 1, 3, fz + 1, facing="north", table=HOARD)
    loot_chest(b, fx + 2, 3, fz - 2, facing="west", table=HOARD)
    b.suspicious(fx, 2, fz + 1)
    hidden_light(b, fx, 6, fz, level=7)
    # scattered maze dressing: bones of those who tried
    for _ in range(10):
        x, z = b.rng.randint(3, S - 3), b.rng.randint(3, S - 3)
        if (x, 3, z) in b.blocks and b.blocks[(x, 3, z)][0] == "minecraft:air":
            b.set(x, 3, z, "minecraft:skeleton_skull[rotation=%d]" % b.rng.randint(0, 15))
    # ---- entry undercroft and a lined L-shaped passage to the maze ladder
    room(b, 10, 11, 10, 22, 16, 22, shell="brick")      # entry undercroft
    b.pot(11, 12, 11)
    b.pot(21, 12, 21)
    hidden_light(b, 16, 14, 16, level=9)
    passage(b, 12, 12, 11, 12, 3)
    passage(b, 12, 12, 3, 3, 3)
    ladder_shaft(b, 3, 3, 3, 11, facing="east", lining="brick")
    # ---- surface shrine (yG..): small round temple over the undercroft
    import math
    cx = cz = 16
    for x in range(cx - 5, cx + 6):
        for z in range(cz - 5, cz + 6):
            if ((x - cx) ** 2 + (z - cz) ** 2) ** 0.5 <= 5.2:
                b.set(x, G, z, "floor")
    for i in range(8):
        a = i * math.tau / 8
        px = cx + round(4.2 * math.cos(a))
        pz = cz + round(4.2 * math.sin(a))
        if b.pristine or b.rng.random() < 0.7:
            b.column(px, G + 1, pz, 3, "pillar", cap="chiseled")
    for x in range(cx - 3, cx + 4):                     # shallow cone roof
        for z in range(cz - 3, cz + 4):
            if abs(x - cx) + abs(z - cz) <= 4:
                slab = b.resolve("slab").split("[")[0]
                b.set(x, G + 5, z, f"{slab}[type=bottom,waterlogged=false]")
    b.set(cx, G + 1, cz, "chiseled")                    # altar over the secret
    secret_hatch(b, cx - 1, cz, 12, G, facing="north", lining="brick")
    if not b.pristine:
        crack_seams(b, cx - 5, cz - 5, cx + 5, cz + 5, G + 1, G + 3, count=2)
    b.erode(0.07, min_y=G + 1)


# ================================================================ BABYLONIAN

@attrs(20, 9)
def archive_of_names(b):
    """Babylonian mega-archive: a ruined ziggurat stub above three buried
    floors of shelves and tablets, ending at the thrice-sealed Name Vault."""
    G = 20
    W, D = 26, 18
    # ---- L3: the Name Vault (y2..6)
    room(b, 4, 2, 6, 12, 6, 12, shell="brick")
    b.fill(6, 3, 8, 10, 3, 10, "glaze")
    b.set(8, 4, 9, "minecraft:gold_block", protect=True)
    b.set(6, 3, 9, "chiseled", protect=True)
    b.waystone(6, 4, 9, facing="east")
    loot_chest(b, 11, 3, 7, facing="west", table=HOARD)
    b.pot(5, 3, 11)
    hidden_light(b, 8, 5, 9, level=8)
    # Triple seal: supported two-high corridor crossing the vault wall.
    passage(b, 11, 3, 9, 18, 9, lining="brick")
    for sx in (13, 15, 17):
        weak_wall(b, sx, 3, 9, sx, 4, 9, cracked="minecraft:packed_mud")
    # ---- L2: the stacks (y8..13)
    room(b, 4, 8, 3, 22, 13, 15, shell="brick")
    for z in range(5, 14, 3):                           # shelf rows
        for x in range(6, 21):
            if x % 5 != 0:                              # aisle gaps
                b.set(x, 9, z, "minecraft:chiseled_bookshelf[facing=south,slot_0_occupied=true,slot_1_occupied=true,slot_2_occupied=true,slot_3_occupied=false,slot_4_occupied=true,slot_5_occupied=false]")
                b.set(x, 10, z, "minecraft:bookshelf")
    spawner(b, 13, 9, 9, "skeleton")
    loot_chest(b, 21, 9, 4, facing="west", table=HIDDEN_TREASURY)
    b.pot(5, 9, 14)
    b.suspicious(18, 8, 12)
    hidden_light(b, 13, 12, 9, level=8)
    ladder_shaft(b, 18, 9, 3, 8, facing="north", lining="brick")
    # ---- L1: reading hall (y15..19)
    room(b, 6, 15, 5, 20, 19, 13, shell="brick")
    for x, z in ((9, 8), (13, 8), (17, 8)):
        b.set(x, 16, z, "minecraft:lectern[facing=south,has_book=false,powered=false]")
    glazed_frieze(b, 7, 5, 19, 17, 17, rosette_every=4)
    b.pot(7, 16, 12)
    loot_chest(b, 19, 16, 6, facing="west", table=HIDDEN_TREASURY)
    ladder_shaft(b, 13, 12, 9, 15, facing="north", lining="brick")
    # ---- surface: ziggurat stub with roofed cella (yG..)
    b.fill(6, G, 4, 20, G + 1, 14, "brick")
    for x in range(6, 21):
        b.set(x, G + 1, 4, "glaze")
        b.set(x, G + 1, 14, "glaze")
    b.fill(9, G + 2, 6, 17, G + 2, 12, "brick")
    b.fill(10, G + 3, 7, 16, G + 6, 11, "brick")        # cella
    b.air(11, G + 3, 8, 15, G + 5, 10)
    b.air(13, G + 3, 11, 13, G + 4, 11)                 # south door
    slab_roof(b, 10, 7, 16, 11, G + 7)
    merlons(b, 9, 6, 17, 12, G + 3, role="glaze")
    # A capstone inside the cella opens onto a continuous return ladder.
    secret_hatch(b, 13, 9, 16, G + 2, facing="north", lining="brick")
    # Three approachable steps up the ziggurat's south side.
    for z, y in ((15, G), (14, G + 1), (13, G + 2)):
        for x in (12, 13, 14):
            b.fill(x, G - 1, z, x, y - 1, z, "brick", protect=True)
            b.set(x, y, z, f"{b.resolve('stairs').split('[')[0]}[facing=north,half=bottom,shape=straight,waterlogged=false]", protect=True)
            b.fill(x, y + 1, z, x, y + 3, z, "minecraft:air", protect=True)
    b.fill(13, G + 3, 11, 13, G + 4, 12, "minecraft:air", protect=True)
    if not b.pristine:
        crack_seams(b, 6, 4, 20, 14, G, G + 5, count=3)
        collapse_wedge(b, b.rng.randint(8, 18), G + 2, 4, 3, "east", (7, G + 2, 19, 6))
    b.erode(0.05, min_y=G + 2)


# ================================================================ VIKING

@attrs(22, 8)
def hall_of_the_drowned_king(b):
    """Viking mega-barrow: a collapsed hall above; below, the feast that
    never ended, and deeper still, the king's whole ship in its grave."""
    G = 22
    W, D = 30, 14
    # ---- L2: ship burial chamber (y3..12)
    room(b, 3, 3, 3, 27, 12, 11, shell="cobble")
    for x in range(6, 25):                              # hull: keel + rising ends
        b.set(x, 4, 7, "minecraft:dark_oak_planks")
        w = 1 if 8 <= x <= 22 else 0
        for dz in range(-w, w + 1):
            b.set(x, 4, 7 + dz, "minecraft:dark_oak_planks")
        if 9 <= x <= 21:
            b.set(x, 5, 5, "minecraft:dark_oak_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
            b.set(x, 5, 9, "minecraft:dark_oak_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
    for i, x in enumerate((5, 4)):                      # stern rise
        b.set(x, 5 + i, 7, "minecraft:dark_oak_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]")
    for i, x in enumerate((25, 26)):                    # prow rise
        b.set(x, 5 + i, 7, "minecraft:dark_oak_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]")
    b.column(15, 5, 7, 4, "minecraft:stripped_spruce_log[axis=y]")   # mast stub
    b.set(26, 7, 7, "chiseled", protect=True)
    b.waystone(26, 8, 7, facing="west")                 # at the prow
    sarcophagus(b, 14, 5, 7, axis="x")                  # the king amidships
    loot_chest(b, 12, 5, 6, facing="east", table=HOARD)
    loot_chest(b, 18, 5, 8, facing="west", table=HOARD)
    b.fill(20, 5, 6, 21, 5, 6, "minecraft:gold_block")
    b.suspicious(10, 4, 7)
    spawner(b, 7, 4, 5, "stray")
    hidden_light(b, 15, 10, 7, level=8)
    # ---- L1: buried feasting hall (y14..20)
    room(b, 6, 14, 3, 24, 20, 11, shell="cobble")
    for x in range(8, 23):                              # long tables
        for z in (5, 9):
            slab = "minecraft:spruce_slab"
            b.set(x, 15, z, f"{slab}[type=top,waterlogged=false]")
    for z in (5, 9):                                    # benches
        for x in range(8, 23, 2):
            b.set(x, 15, z - 1 if z == 5 else z + 1, "minecraft:spruce_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % ("south" if z == 5 else "north"))
    b.fill(7, 15, 6, 7, 15, 8, "minecraft:spruce_planks")   # high seat
    b.set(7, 16, 7, "minecraft:spruce_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]")
    for x in range(9, 22, 4):                           # cold hearths down the aisle
        b.set(x, 15, 7, "minecraft:campfire[lit=false,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    b.pot(23, 15, 4)
    b.pot(23, 15, 10)
    loot_chest(b, 8, 15, 4, facing="south", table=HIDDEN_TREASURY)
    hidden_light(b, 15, 18, 7, level=9)
    # L1 -> L2: behind the high seat
    passage(b, 5, 15, 8, 8, 8)
    weak_wall(b, 6, 15, 8, 6, 16, 8, cracked="minecraft:mossy_cobblestone")
    ladder_shaft(b, 5, 8, 4, 14, facing="east")
    # ---- surface: collapsed hall footprint + runestone (yG..)
    b.fill(8, G, 4, 22, G, 10, "floor")
    for x in range(8, 23):
        for z in (4, 10):
            h = b.rng.choice((1, 1, 2, 3))
            b.column(x, G + 1, z, h, "cobble")
    for gx in (8, 22):
        b.fill(gx, G + 1, 5, gx, G + 2, 9, "cobble")
    b.column(25, G, 7, 2, "brick")                      # runestone outside
    b.set(25, G + 2, 7, "chiseled")
    b.fill(15, G + 1, 10, 16, G + 2, 10, "minecraft:air", protect=True)
    secret_hatch(b, 12, 8, 15, G, facing="north")
    b.erode(0.08, min_y=G + 1)
    b.rubble(8, 4, 22, 10, 8, y=G)


# ================================================================ MAYAN

@attrs(22, 12)
def mouth_of_the_underworld(b):
    """Mayan mega-descent: a corbel gate above the road to Xibalba - a
    waterfall cenote, the ballcourt of the dead, and the jade vault."""
    G = 22
    W = D = 24
    # ---- L3: jade vault (y2..7)
    room(b, 14, 2, 14, 22, 7, 22, shell="brick")
    b.fill(17, 3, 17, 19, 3, 19, "minecraft:emerald_block")
    b.set(18, 4, 18, "chiseled", protect=True)
    b.waystone(18, 5, 18)
    loot_chest(b, 15, 3, 21, facing="north", table=HOARD)
    loot_chest(b, 21, 3, 15, facing="south", table=HOARD)
    b.pot(15, 3, 15)
    hidden_light(b, 16, 6, 16, level=8)
    # ---- L2: ballcourt of the dead (y9..14)
    room(b, 4, 9, 8, 20, 14, 20, shell="brick")
    for z0, sz, face in ((9, 11, "south"), (19, 17, "north")):
        for x in range(6, 19):
            b.stairs(x, 10, sz, face)
    spawner(b, 12, 10, 14, "skeleton")
    b.suspicious(6, 9, 18)
    b.pot(19, 10, 9)
    hidden_light(b, 12, 13, 14, level=8)
    # L2 -> L3: false floor at the court's scoring stone
    b.set(17, 10, 17, "chiseled")
    secret_hatch(b, 19, 18, 3, 9, facing="west")
    # ---- L1: waterfall cenote chamber (y15..20)
    room(b, 6, 15, 4, 18, 20, 16, shell="brick")
    b.fill(10, 15, 8, 14, 15, 12, "minecraft:water")
    b.fill(10, 14, 8, 14, 14, 12, "minecraft:gravel")
    b.set(12, 19, 10, "minecraft:water")                # the falling thread
    b.pot(7, 16, 5)
    loot_chest(b, 17, 16, 15, facing="north", table=HIDDEN_TREASURY)
    hidden_light(b, 12, 18, 10, level=9)
    # L1 -> L2: behind a glyph panel
    weak_wall(b, 12, 16, 16, 13, 17, 16, cracked="minecraft:chiseled_stone_bricks")
    passage(b, 12, 16, 15, 12, 17, lining="brick")
    ladder_shaft(b, 12, 17, 10, 15, facing="north", lining="brick")
    # ---- surface: corbel gate + platform (yG..)
    b.fill(6, G, 4, 18, G, 16, "floor")
    b.fill(9, G + 1, 6, 15, G + 5, 8, "brick")
    corbel_arch(b, 11, G + 1, 7, 3, axis="x")
    b.fill(11, G + 1, 6, 12, G + 3, 8, "minecraft:air", protect=True)
    for x in range(9, 16):                              # roof comb over the gate
        if x % 2 == 1:
            b.set(x, G + 6, 7, "brick")
    b.set(12, G + 1, 12, "chiseled")                    # plaza altar
    # gate passage floor opens downward
    secret_hatch(b, 12, 7, 16, G, facing="north")
    if not b.pristine:
        vine_creep(b, prob_low=0.35, prob_high=0.1, cutoff=G + 2)
    b.erode(0.06, min_y=G + 1)


# ================================================================ NETHER / END

def forge_of_souls(b):
    """Nether mega-forge: three stacked halls - the gilded forge floor, a
    gallery of chains, and the deep reliquary where the fires began."""
    W, D, H = 24, 20, 26
    b.hollow_box(0, 0, 0, W, H, D, "brick")
    b.rooms = [(0, 0, 0, W, 8, D), (0, 8, 0, W, 16, D), (0, 16, 0, W, H, D)]
    # ---- deep reliquary (y1..7)
    b.air(1, 1, 1, W - 1, 7, D - 1)
    b.fill(1, 0, 1, W - 1, 0, D - 1, "floor")
    b.fill(10, 1, 8, 14, 1, 12, "minecraft:crying_obsidian")
    b.set(12, 2, 10, "chiseled", protect=True)
    b.waystone(12, 3, 10)
    spawner(b, 5, 1, 5, "blaze")
    loot_chest(b, 21, 1, 17, facing="north", table=HOARD)
    loot_chest(b, 2, 1, 17, facing="east", table=HOARD)
    b.pot(21, 1, 2)
    # ---- chain gallery (y9..15)
    b.fill(1, 8, 1, W - 1, 8, D - 1, "floor")
    b.air(1, 9, 1, W - 1, 15, D - 1)
    b.air(9, 8, 8, 15, 8, 12)                           # gallery floor opens over the heart
    for _ in range(14):
        x, z = b.rng.randint(2, W - 2), b.rng.randint(2, D - 2)
        for i in range(b.rng.randint(2, 5)):
            b.set(x, 15 - i, z, "minecraft:chain[axis=y,waterlogged=false]")
    for x, z in ((3, 3), (W - 3, 3), (3, D - 3), (W - 3, D - 3)):
        b.column(x, 9, z, 6, "pillar")
    b.suspicious(4, 8, 16)
    # ---- forge floor (y17..25)
    b.fill(1, 16, 1, W - 1, 16, D - 1, "floor")
    b.air(1, 17, 1, W - 1, 25, D - 1)
    for x, z in ((6, 5), (18, 5), (6, 15), (18, 15)):
        b.fill(x - 1, 17, z - 1, x + 1, 17, z + 1, "accent")
        b.set(x, 17, z, "minecraft:soul_campfire[lit=true,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    b.fill(11, 17, 9, 13, 18, 11, "minecraft:gilded_blackstone")
    b.set(12, 19, 10, "minecraft:chain[axis=y,waterlogged=false]")
    b.pot(2, 17, 2)
    loot_chest(b, W - 2, 17, D - 2, facing="north")
    # inter-level shafts (open - the forge invites you down)
    b.air(3, 8, 10, 3, 16, 10)
    ladder_shaft(b, 3, 10, 1, 16, facing="east", lining="brick")
    hidden_light(b, 12, 6, 10, level=7)
    hidden_light(b, 12, 13, 10, level=7)
    b.breach(0, 17, 0, W, 25, D, count=3)
    b.erode(0.04, min_y=17)


@attrs(14, 11)
def vault_of_first_flight(b):
    """End mega-vault: a cloister of the first fliers over an obsidian-cored
    vault - shulker-guarded, void-lit, holding the waystone they carried
    across the dark."""
    G = 14
    W = D = 22
    # ---- the vault (y2..9)
    room(b, 5, 2, 5, 17, 9, 17, shell="brick")
    b.fill(9, 3, 9, 13, 5, 13, "minecraft:obsidian")
    b.air(10, 4, 10, 12, 5, 12)
    b.set(11, 4, 11, "minecraft:crying_obsidian", protect=True)
    b.set(11, 3, 12, "chiseled", protect=True)
    b.waystone(11, 4, 12, facing="north")
    spawner(b, 7, 3, 7, "shulker")
    loot_chest(b, 16, 3, 6, facing="west", table=HOARD)
    loot_chest(b, 6, 3, 16, facing="east", table=HOARD)
    b.pot(16, 3, 16)
    hidden_light(b, 11, 7, 11, level=9)
    # ---- surface cloister (yG..)
    b.fill(4, G, 4, 18, G, 18, "floor")
    for x in range(5, 18, 3):
        for z in (5, 17):
            b.column(x, G + 1, z, 4, "pillar", cap="chiseled")
    for z in range(8, 15, 3):
        b.column(5, G + 1, z, 4, "pillar")
        b.column(17, G + 1, z, 4, "pillar")
    b.fill(5, G + 5, 5, 17, G + 5, 17, "brick")         # roof ring
    b.air(8, G + 5, 8, 14, G + 5, 14)                   # open oculus
    for x, z in ((5, 5), (17, 5), (5, 17), (17, 17)):
        b.set(x, G + 6, z, "minecraft:end_rod[facing=up]", protect=True)
    b.set(11, G + 1, 11, "chiseled")                    # the oculus altar
    secret_hatch(b, 14, 12, 3, G, facing="west", lining="brick")
    # Open the obsidian shrine at the front so its inner waystone is usable.
    passage(b, 11, 4, 8, 11, 10, lining="brick")
    for fx, fy, fz in ((1, G + 3, 2), (20, G + 7, 4), (2, G + 9, 19), (20, G + 2, 19)):
        b.fill(fx, fy, fz, fx + 1, fy + 1, fz + 1, "cobble")
    b.erode(0.05, min_y=G + 1)


# ================================================== the Waybuilders' secret

@attrs(26, 13)
def the_first_waystone(b):
    """The deepest secret in the mod: an unassuming ring of standing stones
    over three buried levels - the Hall of Five Doors, the Pattern Chamber,
    and the rough-hewn First Waystone itself."""
    G = 26
    W = D = 26
    # ---- L3: the First Waystone (y2..8)
    room(b, 7, 2, 7, 19, 8, 19, shell="brick")
    for x, z in ((9, 9), (17, 9), (9, 17), (17, 17)):
        b.column(x, 3, z, 5, "cobble")
    b.fill(11, 3, 11, 15, 3, 15, "cobble")              # rough dais
    b.fill(12, 4, 12, 14, 4, 14, "chiseled")
    b.set(13, 7, 13, "chiseled", protect=True)          # the proto-monolith crown
    b.waystone(13, 5, 13)
    spawner(b, 8, 3, 13, "silverfish")                  # the stone remembers
    loot_chest(b, 18, 3, 8, facing="west", table=HOARD)
    loot_chest(b, 8, 3, 18, facing="east", table=HOARD)
    b.fill(16, 3, 16, 16, 3, 17, "minecraft:gold_block")
    b.suspicious(13, 2, 10)
    hidden_light(b, 13, 7, 10, level=8)
    # ---- L2: Pattern Chamber (y10..15)
    room(b, 6, 10, 6, 20, 15, 20, shell="brick")
    for r in (2, 4, 6):                                 # concentric chiseled rings
        for x in range(13 - r, 13 + r + 1):
            for z in range(13 - r, 13 + r + 1):
                if max(abs(x - 13), abs(z - 13)) == r and (x + z) % 2 == 0:
                    b.set(x, 10, z, "chiseled")
    loot_chest(b, 7, 11, 13, facing="east", table=HIDDEN_TREASURY)
    b.pot(19, 11, 7)
    b.pot(7, 11, 19)
    hidden_light(b, 13, 14, 13, level=9)
    b.air(13, 8, 13, 13, 8, 13)                         # oculus down to L3 dais
    ladder_shaft(b, 10, 10, 3, 10, facing="east", lining="brick")
    # ---- L1: Hall of Five Doors (y17..24)
    room(b, 5, 17, 5, 21, 24, 21, shell="brick")
    doors = [
        (13, 5, "z", ("minecraft:smooth_sandstone", "minecraft:gold_block")),        # egyptian
        (21, 13, "x", ("minecraft:quartz_block", "minecraft:cyan_terracotta")),      # greek
        (13, 21, "z", ("minecraft:mud_bricks", "minecraft:blue_terracotta")),        # babylon
        (5, 13, "x", ("minecraft:spruce_planks", "minecraft:dark_oak_planks")),      # viking
        (9, 5, "z", ("minecraft:mossy_cobblestone", "minecraft:chiseled_stone_bricks")),  # mayan
    ]
    for dx, dz, axis, (mat, acc) in doors:
        for dy in range(18, 21):                        # dressed door frames
            if axis == "z":
                b.set(dx - 1, dy, dz, mat)
                b.set(dx + 1, dy, dz, mat)
            else:
                b.set(dx, dy, dz - 1, mat)
                b.set(dx, dy, dz + 1, mat)
        b.set(dx, 21, dz, acc)
        # Cut the doorway itself, then line the alcove behind its frame.
        ax_, az_ = (dx, dz - 2 if dz == 5 else dz + 2) if axis == "z" else (dx - 2 if dx == 5 else dx + 2, dz)
        passage(b, dx, 18, dz, ax_, az_, lining="brick")
    b.pot(13, 18, 3)
    loot_chest(b, 23, 18, 13, facing="west", table=HIDDEN_TREASURY)
    b.suspicious(13, 17, 23)
    b.pot(3, 18, 13)
    # the mayan door (9,5) is the true one: shaft behind it
    passage(b, 9, 11, 4, 9, 7, lining="brick")
    ladder_shaft(b, 9, 4, 11, 17, facing="south", lining="brick")
    hidden_light(b, 13, 22, 13, level=9)
    # ---- surface: a plain ring of standing stones (yG..)
    b.fill(7, G, 7, 19, G, 19, "floor")
    import math
    for i in range(9):
        a = i * math.tau / 9
        px = 13 + round(5.2 * math.cos(a))
        pz = 13 + round(5.2 * math.sin(a))
        b.column(px, G + 1, pz, b.rng.choice((2, 3, 3, 4)), "cobble")
    b.set(13, G + 1, 13, "chiseled")                    # the center stone
    secret_hatch(b, 12, 13, 18, G, facing="east")      # beside the center stone
    b.erode(0.07, min_y=G + 1)


# ============================================================ generic flavor

SMUGGLERS_TALLY = written_book("Tally of the Undercroft", "The last tally-man", [
    "Goods come in by the cistern road and go out by night. Nobody has kept the watch above since its stone went quiet.",
    "The cells up front are for show. Brick up the east door again after every count.",
    "Last count: the strongbox full, the casks sealed. Whoever reads this, we did not come back for it.",
])


@attrs(16, 7)
def smugglers_undercroft(b):
    """Default theme: a broken watch stub hiding a smuggler warren - zigzag
    tunnels, stashed goods, a flooded cell, and a dead end that lies.

    v1.17: no spawner (only the great dungeons keep one). The decoy cell's
    east wall is a bricked-up door to the strongroom that holds the real
    stash and the smugglers' tally; the flooded cell is a chained lock-up."""
    G = 16
    # ---- warren (y3..8): hand-dug tunnels between three cells
    room(b, 2, 3, 2, 9, 8, 9, shell="cobble")           # stash cell
    room(b, 12, 3, 6, 18, 8, 12, shell="cobble")        # flooded cell
    room(b, 4, 3, 12, 10, 8, 17, shell="cobble")        # decoy cell
    room(b, 12, 3, 13, 18, 7, 17, shell="brick")        # strongroom, behind the decoy
    passage(b, 8, 4, 7, 13, 7, height=3)              # through both room walls
    passage(b, 6, 4, 8, 6, 13)
    passage(b, 9, 4, 15, 13, 15)                      # decoy -> strongroom
    weak_wall(b, 10, 4, 15, 10, 5, 15, cracked="minecraft:cracked_stone_bricks")
    # stash cell: one stash chest, casks, the tally table
    loot_chest(b, 3, 4, 3, facing="south", table=HIDDEN_TREASURY)
    for x, y, z, state in ((8, 4, 8, "minecraft:barrel[facing=up,open=false]"),
                           (8, 5, 8, "minecraft:barrel[facing=up,open=false]"),
                           (7, 4, 8, "minecraft:barrel[facing=west,open=false]"),
                           (8, 4, 3, "minecraft:barrel[facing=south,open=false]")):
        b.set(x, y, z, state, protect=True)
    b.set(3, 4, 6, "minecraft:spruce_planks", protect=True)
    b.set(3, 4, 7, "minecraft:spruce_slab[type=top,waterlogged=false]", protect=True)
    candles(b, 3, 5, 6, 2)
    candles(b, 8, 6, 8, 1)
    b.pot(3, 4, 8)
    for x, z in ((3, 8), (8, 3)):
        b.set(x, 7, z, "minecraft:cobweb")
    hanging_lantern(b, 4, 6, 4)
    # flooded cell: a chained lock-up under a lantern, a cask adrift
    slab = b.resolve("slab").split("[")[0]
    b.fill(13, 4, 7, 17, 4, 11, f"{slab}[type=bottom,waterlogged=true]")
    b.suspicious(13, 3, 7)
    for z in (8, 10):
        for y in (6, 7):
            b.set(17, y, z, "minecraft:chain[axis=y,waterlogged=false]", protect=True)
    b.set(13, 4, 11, "minecraft:barrel[facing=north,open=false]", protect=True)
    hanging_lantern(b, 15, 7, 9, chain=0)              # clear of heads on the slabs
    # decoy cell: empty pots, broken crates, and one wall of the wrong stone
    b.pot(5, 4, 13)
    b.pot(9, 4, 16)
    b.set(5, 4, 16, "minecraft:spruce_slab[type=bottom,waterlogged=false]", protect=True)
    b.set(6, 4, 16, "minecraft:barrel[facing=east,open=false]", protect=True)
    b.set(9, 7, 13, "minecraft:cobweb")
    hanging_lantern(b, 7, 6, 14)
    # strongroom: the real stash, the tally on its lectern, the takings in gold
    loot_chest(b, 17, 4, 16, facing="north", table=HIDDEN_TREASURY)
    lectern(b, 15, 4, 14, "south", book=SMUGGLERS_TALLY)
    b.set(17, 4, 14, "minecraft:gold_block", protect=True)
    for x, state in ((14, "minecraft:barrel[facing=up,open=false]"), (16, "minecraft:barrel[facing=up,open=false]")):
        b.set(x, 4, 16, state, protect=True)
        candles(b, x, 5, 16, 3)
    hanging_lantern(b, 15, 6, 15, chain=0)             # a three-high room: flush to the vault
    # ---- surface: broken watch stub (yG..)
    b.fill(4, G, 4, 12, G, 12, "floor")
    for x in range(5, 12):
        for z in range(5, 12):
            edge = x in (5, 11) or z in (5, 11)
            if edge and b.rng.random() < 0.75:
                b.column(x, G + 1, z, b.rng.choice((1, 2, 3, 4)), "brick")
    b.set(8, G + 1, 8, "chiseled", protect=True)
    b.waystone(8, G + 2, 8)
    # Deliberate doorway and one shared hatch/ladder column: the old ladder
    # sat beside the shaft and ended against an intact ceiling/floor.
    b.fill(8, G + 1, 11, 9, G + 2, 11, "minecraft:air", protect=True)
    secret_hatch(b, 6, 6, 4, G, facing="east")
    b.rubble(4, 4, 12, 12, 6, y=G)
    b.erode(0.09, min_y=G + 1)


forge_of_souls.section = 10    # ant-farm view of the three stacked halls

EGYPT_GRAND4 = {"valley_sepulcher": valley_sepulcher}
GREEK_GRAND4 = {"labyrinth_of_the_bull": labyrinth_of_the_bull}
BABYLON_GRAND4 = {"archive_of_names": archive_of_names}
VIKING_GRAND4 = {"hall_of_the_drowned_king": hall_of_the_drowned_king}
MAYAN_GRAND4 = {"mouth_of_the_underworld": mouth_of_the_underworld}
NETHER4 = {"forge_of_souls": forge_of_souls}
END4 = {"vault_of_first_flight": vault_of_first_flight}
DEFAULT_GRAND4 = {"the_first_waystone": the_first_waystone, "smugglers_undercroft": smugglers_undercroft}

ALL4 = {}
for d in (EGYPT_GRAND4, GREEK_GRAND4, BABYLON_GRAND4, VIKING_GRAND4,
          MAYAN_GRAND4, NETHER4, END4, DEFAULT_GRAND4):
    ALL4.update(d)
