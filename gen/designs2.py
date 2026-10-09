"""v1.8 designs: the master-builder batch. Seventeen new culture structures
using the technique reference (facade depth, gradients, baked stair shapes,
authentic collapse, hidden lighting). Same conventions as designs.py:
surface templates have y0-1 foundation, y2 floor, features y3+; every design
places exactly one waystone; ruin passes are skipped when b.pristine.
"""
from master import (grad_wall, string_course, cornice, pilasters, corbel_arch,
                    battered_wall, column_stump, crack_seams, collapse_wedge,
                    vine_creep, hidden_light, merlons, glazed_frieze, gable_roof, room,
                    gable_ends)


# ================================================================ EGYPTIAN

def hypostyle_hall(b):
    """Egyptian grand: forest of papyrus columns between battered walls,
    hieroglyph string courses, half the roof fallen, sand drifting in."""
    W, D = 22, 16
    b.foundation(0, 0, W, D)
    b.fill(0, 2, 0, W, 2, D, "floor")
    # battered side walls with hieroglyph band at eye level
    for z in (0, D):
        grad_wall(b, 1, 3, z, W - 1, 7, z, "brick", "cobble", "cobble")
        for x in range(1, W):
            b.set(x, 4, z, "chiseled")                 # hieroglyph course
    string_course(b, 1, 0, W - 1, D, 7, "accent" if b.pristine else "brick")
    # entrance pylon stubs, east face
    b.fill(0, 3, 1, 0, 6, 5, "brick")
    b.fill(0, 3, D - 5, 0, 6, D - 1, "brick")
    b.fill(0, 3, 6, 0, 5, 6, "minecraft:air")
    # papyrus columns: 2x2 shafts, capital flare
    for cx in (4, 9, 14, 19):
        for cz in (4, 8, 12):
            if b.pristine or b.rng.random() < 0.75:
                h = 6 if b.pristine else b.rng.choice((6, 6, 4, 3))
                for dx in (0, 1):
                    for dz in (0, 1):
                        b.column(cx + dx, 3, cz + dz, h, "brick")
                if h == 6:                             # papyrus-bell capital
                    slab = b.resolve("slab").split("[")[0]
                    for px in range(cx - 1, cx + 3):
                        for pz in range(cz - 1, cz + 3):
                            b.set(px, 9, pz, f"{slab}[type=bottom,waterlogged=false]")
                    for dx in (0, 1):
                        for dz in (0, 1):
                            b.set(cx + dx, 9, cz + dz, "chiseled")
            else:
                column_stump(b, cx, 3, cz, 6)
    # surviving roof patch over the west third
    if not b.pristine:
        for x in range(1, 7):
            for z in range(1, D):
                if b.rng.random() < 0.7:
                    base = b.resolve("slab").split("[")[0]
                    b.set(x, 10, z, f"{base}[type=bottom,waterlogged=false]")
    else:
        for x in range(1, W):
            for z in range(1, D):
                base = b.resolve("slab").split("[")[0]
                b.set(x, 10, z, f"{base}[type=bottom,waterlogged=false]")
    # sanctuary: granite-dark contrast, gold, waystone
    b.fill(W - 3, 3, 6, W - 1, 3, 10, "minecraft:polished_granite")
    b.set(W - 2, 4, 8, "minecraft:gold_block", protect=True)
    b.waystone(W - 2, 4, 7)
    hidden_light(b, W - 4, 5, 8)
    hidden_light(b, 10, 5, 8)
    # sand drift through the entrance
    if not b.pristine:
        for x in range(0, 6):
            for z in range(5, 9):
                if b.rng.random() < 0.5 - x * 0.08 and (x, 3, z) not in b.blocks:
                    b.set(x, 3, z, "minecraft:sand")
        crack_seams(b, 1, 0, W - 1, D, 3, 7, count=3)
        collapse_wedge(b, b.rng.randint(8, 14), 7, D, 4, "east", (6, 2, 16, D - 2))
    b.suspicious(3, 2, 3)
    b.suspicious(12, 2, 12)
    b.pot(W - 3, 4, 10)
    b.satellite_socket(11, 0, "north_up")
    b.satellite_socket(0, 8, "west_up")
    b.erode(0.05, min_y=3)
    b.rubble(1, 1, W - 1, D - 1, 8)


def sphinx_avenue(b):
    """Egyptian small: paired guardian sphinxes flanking a processional way."""
    b.foundation(0, 0, 14, 6)
    b.fill(0, 2, 2, 14, 2, 4, "floor")
    stair = b.resolve("stairs").split("[")[0]
    for sx in (2, 8):
        for sz, mirror in ((0, "south"), (6, "north")):
            # plinth
            b.fill(sx, 2, sz, sx + 3, 2, sz, "accent")
            # lion body: haunches + chest + forepaws
            b.fill(sx + 1, 3, sz, sx + 2, 3, sz, "brick")
            b.set(sx, 3, sz, f"{stair}[facing=west,half=bottom,shape=straight,waterlogged=false]")
            b.set(sx + 3, 3, sz, f"{stair}[facing=east,half=bottom,shape=straight,waterlogged=false]")
            b.set(sx + 2, 4, sz, "brick")              # chest
            b.set(sx + 3, 4, sz, "chiseled")           # head (nemes)
            b.set(sx + 3, 5, sz, f"{stair}[facing=west,half=bottom,shape=straight,waterlogged=false]")
    b.set(13, 2, 3, "chiseled", protect=True)
    b.waystone(13, 3, 3)
    hidden_light(b, 7, 4, 3)
    b.suspicious(5, 2, 3)
    if not b.pristine:
        crack_seams(b, 0, 0, 14, 6, 3, 5, count=2)
    b.erode(0.06)


def sun_court(b):
    """Egyptian grand: open solar court — cavetto-corniced walls, twin
    obelisks, offering altar under the sky."""
    W = D = 18
    b.foundation(0, 0, W, D)
    b.fill(0, 2, 0, W, 2, D, "floor")
    for x in range(0, W + 1):                          # perimeter, gate south
        for z in range(0, D + 1):
            if x in (0, W) or z in (0, D):
                if z == D and 7 <= x <= 11:
                    continue
                grad_wall(b, x, 3, z, x, 6, z, "brick", "cobble", "cobble")
    cornice(b, 0, 0, W, D, 6)
    pilasters(b, 1, 0, W - 1, 3, 5, period=4, depth_dz=1, role="accent")
    pilasters(b, 1, D, W - 1, 3, 5, period=4, depth_dz=-1, role="accent")
    # twin obelisks on plinths
    for ox in (5, 13):
        b.fill(ox - 1, 3, 8, ox + 1, 3, 10, "accent")
        b.column(ox, 4, 9, 7, "brick")
        stair = b.resolve("stairs").split("[")[0]
        for f, dx, dz in (("east", -1, 0), ("west", 1, 0), ("south", 0, -1), ("north", 0, 1)):
            b.set(ox + dx, 11, 9 + dz, f"{stair}[facing={f},half=bottom,shape=straight,waterlogged=false]")
        b.set(ox, 11, 9, "chiseled")
        b.set(ox, 12, 9, "minecraft:gold_block" if (b.pristine or ox == 5) else "wall", protect=True)
    # altar + waystone at court center
    b.fill(8, 3, 3, 10, 3, 5, "minecraft:polished_granite")
    b.waystone(9, 4, 4)
    b.set(9, 3, 6, "minecraft:lava_cauldron" if b.pristine else "minecraft:cauldron", protect=True)
    b.suspicious(3, 2, 14)
    b.suspicious(15, 2, 3)
    b.pot(2, 3, 2)
    b.satellite_socket(9, D, "south_up")
    b.satellite_socket(0, 9, "west_up")
    if not b.pristine:
        collapse_wedge(b, 4, 6, 0, 3, "east", (2, 1, 8, 3))
        crack_seams(b, 0, 0, W, D, 3, 6, count=3)
    b.erode(0.07)
    b.rubble(1, 1, W - 1, D - 1, 7)


# ================================================================ GREEK

def temple_of_the_way(b):
    """A lost temple precinct, one monumental bay above its exposed plan."""
    from archaeology import (fragment_floor, standing_column, supported_lintel,
                             fallen_column, wall_remnant, quiet_waystone)
    b.archaeological = True
    fragment_floor(b, 0, 0, 26, 18)
    # Column bases reconstruct the original peristyle; only one bay has its beam.
    for z in (4, 14):
        for x in (4, 8, 12, 16, 20, 24):
            whole = b.pristine or (z == 4 and x in (4, 8))
            standing_column(b, x, z, 2, 6 if whole else b.rng.choice((0, 1, 2, 3)), complete=whole)
    supported_lintel(b, (4, 4), (8, 4), 10, 2)
    for x in range(4, 9):
        b.set(x, 11, 4, "chiseled" if x in (4, 8) else "brick", protect=True)
    if b.pristine:
        for z in (4, 14):
            for x in (4, 8, 12, 16, 20):
                supported_lintel(b, (x, z), (x+4, z), 10, 2)
    # Cella corners keep more height than the exposed middle of either wall.
    for z in (6, 12):
        wall_remnant(b, [(x, z, h) for x, h in zip(range(10, 24), (1,1,0,0,1,1,0,1,2,2,3,4,4,3))], 2)
    wall_remnant(b, [(23, z, h) for z, h in zip(range(7, 12), (3,2,2,3,3))], 2)
    # Small surviving mosaic panels imply a rich interior without a busy carpet.
    for x in (7, 8, 9, 10, 12, 13):
        b.set(x, 2, 7, "minecraft:cyan_terracotta")
    if not b.pristine:
        fallen_column(b, 16, 15, 2, 5)
        fallen_column(b, 11, 2, 2, 4)
        fallen_column(b, 25, 8, 2, 4, direction=(0, 1))
    b.suspicious(20, 2, 11)
    quiet_waystone(b, 18, 9, 2, facing="west")
    # An axial approach through the vanished doorway stays at walking grade.
    b.fill(0, 2, 8, 16, 2, 10, "floor", protect=True)
    b.satellite_socket(0, 9, "west_up")
    b.satellite_socket(26, 9, "east_up")


def odeon(b):
    """Greek small: intimate half-round theater cut into a slope."""
    import math
    b.foundation(0, 0, 12, 8)
    b.fill(1, 2, 0, 11, 2, 4, "floor")                 # orchestra
    for r, y in ((4, 3), (5, 4), (6, 5)):              # curved tiers
        for deg in range(0, 181, 6):
            a = math.radians(deg)
            x = 6 + round(r * math.cos(a))
            z = 4 + round(r * math.sin(a) * 0.8)
            if 0 <= x <= 12 and 0 <= z <= 8 and z >= 3:
                if b.pristine or b.rng.random() < 0.8:
                    stair = b.resolve("stairs").split("[")[0]
                    b.set(x, y, z, f"{stair}[facing=north,half=bottom,shape=straight,waterlogged=false]")
                    for yy in range(3, y):
                        b.set(x, yy, z, "brick")
    b.set(6, 2, 2, "chiseled", protect=True)
    b.waystone(6, 3, 2)
    hidden_light(b, 6, 4, 4)
    b.suspicious(3, 2, 2)
    b.erode(0.06)


def spring_house(b):
    """Greek small: fountain house — a spring basin behind a column porch."""
    b.foundation(0, 0, 8, 8)
    b.fill(0, 2, 0, 8, 2, 8, "floor")
    # v1.16: the chamber is two courses taller. Its ceiling used to sit
    # directly on the waystone's head; now there are two clear blocks.
    b.fill(1, 3, 5, 7, 8, 8, "brick")                  # back chamber
    b.air(2, 3, 5, 6, 7, 7)
    slab = b.resolve("slab").split("[")[0]
    b.fill(2, 3, 6, 6, 3, 7, f"{slab}[type=bottom,waterlogged=true]")   # water basin
    for x in (1, 4, 7):                                # porch columns
        if b.pristine or x != 4:
            b.column(x, 3, 2, 5, "pillar", cap="chiseled")
        else:
            column_stump(b, x, 3, 2, 5)
    b.fill(1, 9, 1, 7, 9, 8, "minecraft:air")          # keep silhouette open
    if b.pristine:
        gable_roof(b, 1, 4, 7, 8, 9, axis="x", overhang=0)
    b.set(4, 3, 6, "chiseled", protect=True)
    b.waystone(4, 4, 6)
    b.pot(2, 3, 5)
    b.erode(0.07)


# ================================================================ BABYLONIAN

def ishtar_gate(b):
    """Babylonian grand: glazed processional gate — twin towers, corbel arch,
    aurochs frieze in gold on blue, stepped merlons."""
    W, D = 16, 6
    b.foundation(0, 0, W, D)
    b.fill(0, 2, 0, W, 2, D, "floor")
    for x0 in (0, 11):                                 # towers with batter
        grad_wall(b, x0, 3, 0, x0 + 4, 10, D, "brick", "cobble", "cobble")
        merlons(b, x0, 0, x0 + 4, D, 11, role="glaze")
    b.fill(5, 3, 0, 10, 8, D, "brick")                 # gate mass
    corbel_arch(b, 7, 3, 1, 4, axis="x")
    corbel_arch(b, 7, 3, D - 1, 4, axis="x")
    for z in range(2, D - 1):                          # passage
        b.fill(7, 3, z, 8, 6, z, "minecraft:air")
    # glazed faces with gold motifs
    glazed_frieze(b, 1, 0, 14, 5, 7, rosette_every=3)
    glazed_frieze(b, 1, D, 14, 5, 7, rosette_every=3)
    # The arch must cross the full gate mass, including both decorated faces.
    b.fill(7, 3, 0, 8, 6, D, "minecraft:air", protect=True)
    b.fill(7, 2, 0, 8, 2, D, "floor", protect=True)
    merlons(b, 5, 0, 10, D, 9, role="glaze")
    b.set(9, 3, 3, "chiseled", protect=True)
    b.waystone(9, 4, 3)
    hidden_light(b, 7, 5, 3)
    b.suspicious(2, 2, 3)
    b.pot(13, 3, 2)
    b.satellite_socket(0, 3, "west_up")
    b.satellite_socket(W, 3, "east_up")
    if not b.pristine:
        crack_seams(b, 0, 0, W, D, 3, 9, count=3)
        collapse_wedge(b, 13, 10, D, 4, "east", (11, 1, 15, 5))
    b.erode(0.06, min_y=3)
    b.rubble(0, 0, W, D, 6)


def hanging_terrace(b):
    """Babylonian grand: two irrigated garden terraces over a vaulted
    undercroft — the hanging gardens in miniature."""
    W, D = 18, 14
    b.foundation(0, 0, W, D)
    b.fill(0, 2, 0, W, 2, D, "floor")
    # undercroft: corbel-arched bays along the south face
    room(b, 0, 2, 0, W, 5, 7, shell="brick")
    for ax in range(2, W - 1, 4):
        corbel_arch(b, ax, 3, 7, 2, axis="x")
    # upper terrace mass + parapets
    b.fill(0, 6, 0, W, 6, 7, "cobble")
    merlons(b, 0, 0, W, 0, 7, role="glaze", period=4)
    # irrigation channel down the terrace, water in the pristine one
    slab = b.resolve("slab").split("[")[0]
    for x in range(2, W - 2):
        b.set(x, 6, 3, f"{slab}[type=bottom,waterlogged={'true' if b.pristine else 'false'}]")
    # date palms in a grid on both levels
    for px, pz, py in ((3, 1, 7), (8, 2, 7), (13, 1, 7), (5, 10, 3), (11, 11, 3), (15, 9, 3)):
        h = b.rng.randint(3, 5)
        for i in range(h):
            b.set(px, py + i, pz, "minecraft:jungle_log[axis=y]")
        b.set(px, py + h, pz, "minecraft:jungle_leaves[persistent=true,waterlogged=false]")
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            b.set(px + dx, py + h - 1, pz + dz, "minecraft:jungle_leaves[persistent=true,waterlogged=false]")
    # stair from lower garden to terrace
    for i, z in enumerate((10, 9, 8)):
        for x in (8, 9):
            stair = b.resolve("stairs").split("[")[0]
            b.set(x, 3 + i, z, f"{stair}[facing=north,half=bottom,shape=straight,waterlogged=false]", protect=True)
            for yy in range(2, 3 + i):
                b.set(x, yy, z, "brick")
    b.set(9, 7, 5, "chiseled", protect=True)
    b.waystone(9, 8, 5)
    hidden_light(b, 5, 7, 4)
    b.suspicious(3, 2, 11)
    b.pot(15, 7, 2)
    b.satellite_socket(0, 11, "west_up")
    b.satellite_socket(W, 11, "east_up")
    if not b.pristine:
        vine_creep(b, prob_low=0.2, prob_high=0.06)
        crack_seams(b, 0, 0, W, 7, 3, 6, count=2)
    b.erode(0.06, min_y=3)


def tablet_house(b):
    """Babylonian small: an edubba, the "tablet house" - a roofed schoolroom
    whose back wall is shelved with clay tablets, opening through one door
    onto a walled exercise court where the waystone stands.

    v1.16 rebuild: the first version was a lone wall and a floor, which read
    as nothing. This is a building: room, door, shelves, benches, court."""
    b.foundation(0, 0, 10, 8)
    b.fill(0, 2, 0, 10, 2, 8, "floor")
    # the schoolroom, z 0..4: three-course walls under a flat mud roof
    for x in range(0, 11):
        b.fill(x, 3, 0, x, 5, 0, "brick")
        b.fill(x, 3, 4, x, 5, 4, "brick")
    for z in range(1, 4):
        b.fill(0, 3, z, 0, 5, z, "brick")
        b.fill(10, 3, z, 10, 5, z, "brick")
    b.fill(0, 6, 0, 10, 6, 4, "cobble")                # packed-mud roof
    b.air(5, 3, 4, 5, 4, 4)                            # door to the court
    for x in (2, 8):                                   # window slits
        b.air(x, 4, 0, x, 4, 0)
    # tablet shelves stacked along the back wall, randomly emptied by looters
    for x in range(1, 10):
        for y in (3, 4):
            slots = ",".join(f"slot_{i}_occupied={'true' if b.rng.random() < 0.55 else 'false'}"
                             for i in range(6))
            b.set(x, y, 1, f"minecraft:chiseled_bookshelf[facing=south,{slots}]")
    slab = b.resolve("slab").split("[")[0]
    for x in (1, 2, 3, 7, 8, 9):                       # pupils' benches
        b.set(x, 3, 3, f"{slab}[type=bottom,waterlogged=false]")
    b.set(5, 5, 2, "hanging_light")
    # the court, z 5..8: low walls, a gap to the outside, packed-mud floor
    for z in range(5, 9):
        b.set(0, 3, z, "wall")
        b.set(10, 3, z, "wall")
    for x in range(1, 10):
        if x != 5:
            b.set(x, 3, 8, "wall")
    b.fill(3, 2, 5, 7, 2, 7, "minecraft:packed_mud")   # exercise yard
    b.set(5, 2, 6, "chiseled", protect=True)
    b.waystone(5, 3, 6)
    b.pot(1, 3, 7)
    b.pot(9, 3, 5)
    b.suspicious(2, 2, 5)
    if not b.pristine:
        crack_seams(b, 0, 0, 10, 4, 3, 5, count=2)
    b.erode(0.08, min_y=3)


# ================================================================ VIKING

def stave_shrine(b):
    """Viking grand: small stave temple — tiered steep roofs, crossed gable
    beams, dragon finial stubs, stone plinth."""
    W, D = 12, 10
    b.foundation(0, 0, W, D)
    b.fill(1, 2, 1, W - 1, 2, D - 1, "cobble")         # stone plinth
    # stave walls: log posts + plank infill + mid-height wale
    # v1.16: plank walls rise to the eave course (y6) so the roof rests on
    # them, and the gable triangles are closed.
    for x in range(2, W - 1):
        for z in (2, D - 2):
            if x % 3 == 2:
                b.column(x, 3, z, 4, "pillar")
            else:
                b.fill(x, 3, z, x, 6, z, "plank")
                b.set(x, 4, z, "minecraft:stripped_spruce_log[axis=x]")
    for z in range(3, D - 2):
        for x in (2, W - 2):
            b.fill(x, 3, z, x, 6, z, "plank")
    b.air(6, 3, D - 2, 6, 4, D - 2)                    # door, south
    gable_roof(b, 2, 2, W - 2, D - 2, 6, axis="x", overhang=1, sway=0)
    gable_ends(b, (2, W - 2), 2, 2, W - 2, D - 2, 6, 6)
    # raised ridge tier, seated on the lower roof; pristine or lucky
    if b.pristine or b.rng.random() < 0.5:
        for x in range(4, W - 3):
            b.set(x, 10, 4, "plank")
            b.set(x, 10, D - 4, "plank")
            b.set(x, 11, 5, "plank")
        gable_roof(b, 4, 4, W - 4, D - 4, 11, axis="x", overhang=0)
    # crossed gable beams + finials
    for gx in (1, W - 1):
        b.set(gx, 7, 3, "minecraft:stripped_spruce_log[axis=z]")
        b.set(gx, 7, D - 3, "minecraft:stripped_spruce_log[axis=z]")
        b.set(gx, 8, 4, "minecraft:dark_oak_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
        b.set(gx, 8, D - 4, "minecraft:dark_oak_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
    # interior: hearth line, side benches, waystone shrine at the north end
    slab = "minecraft:spruce_slab"
    for x in range(3, W - 2):
        b.set(x, 3, 3, f"{slab}[type=top,waterlogged=false]")
        if x != 6:                                     # v1.16: the south bench ran across the door
            b.set(x, 3, D - 3, f"{slab}[type=top,waterlogged=false]")
    b.set(6, 2, 5, "minecraft:campfire[lit=false,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    # v1.16: the waystone stood IN the north wall line (z=2), buried in
    # planks. It now stands inside at the west end, facing the hearth.
    b.set(3, 2, 5, "chiseled", protect=True)
    b.waystone(3, 3, 5, facing="east")
    hidden_light(b, 6, 5, 5)
    b.pot(W - 3, 3, D - 3)
    b.suspicious(4, 1, 6)
    b.satellite_socket(W, 5, "east_up")
    b.satellite_socket(0, 5, "west_up")
    if not b.pristine:
        crack_seams(b, 1, 1, W - 1, D - 1, 2, 3, count=1)
    b.erode(0.08)
    b.rubble(1, 1, W - 1, D - 1, 4)


def boat_grave_field(b):
    """Viking small: two ship-settings and a runestone on a windswept rise."""
    import math
    b.foundation(0, 0, 14, 10)
    for (cx, cz, L, ang) in ((4, 3, 9, 0), (10, 7, 7, 1)):
        for i in range(L + 1):
            t = i / L
            w = 1.6 * math.sin(math.pi * t)
            along = i - L / 2
            for s in (-1, 1):
                x = cx + round(along if ang == 0 else along * 0.7)
                z = cz + round(s * w if ang == 0 else s * w + along * 0.4)
                if 0 <= x <= 14 and 0 <= z <= 10:
                    b.set(x, 2, z, "cobble")
                    if i in (0, L):
                        b.set(x, 3, z, "wall")
    b.fill(3, 2, 2, 5, 2, 4, "minecraft:coarse_dirt")
    b.suspicious(4, 1, 3)
    b.column(12, 2, 2, 2, "brick")                     # runestone
    b.set(12, 4, 2, "chiseled")
    b.set(7, 2, 5, "chiseled", protect=True)
    b.waystone(7, 3, 5)
    b.erode(0.06)


def jarl_barrow(b):
    """Viking grand: great turf mound, timber-lined passage, ship-prow
    chamber where the jarl sleeps beside the waystone."""
    C, R = 9, 8
    b.foundation(1, 1, 17, 17)
    for x in range(0, 19):
        for z in range(0, 19):
            d = ((x - C) ** 2 + (z - C) ** 2) ** 0.5
            if d > R:
                continue
            h = max(1, round((R - d) * 0.9))
            b.fill(x, 0, z, x, 1, z, "minecraft:dirt")
            for y in range(2, 2 + h):
                b.set(x, y, z, "minecraft:dirt" if y < 1 + h else "minecraft:moss_block")
            if d > R - 2 and b.rng.random() < 0.3:
                b.set(x, 2 + h, z, "minecraft:moss_carpet")
    # chamber + passage south
    b.air(7, 3, 6, 11, 6, 10)
    b.fill(7, 2, 6, 11, 2, 10, "cobble")
    for x in (7, 11):                                  # timber lining
        for z in range(6, 11):
            b.column(x, 3, z, 3, "pillar")
    b.air(9, 3, 11, 9, 4, 17)
    b.fill(9, 2, 11, 9, 2, 17, "minecraft:dirt_path")
    for z in range(11, 17):
        b.set(8, 3, z, "plank")
        b.set(10, 3, z, "plank")
        b.set(8, 4, z, "plank")
        b.set(10, 4, z, "plank")
        b.set(9, 5, z, "minecraft:stripped_spruce_log[axis=z]")
    # ship prow rising from the chamber floor
    b.set(9, 3, 7, "minecraft:dark_oak_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
    b.set(9, 4, 6, "minecraft:dark_oak_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
    b.set(9, 3, 6, "minecraft:dark_oak_planks")
    b.set(9, 2, 8, "chiseled", protect=True)
    b.waystone(9, 3, 8, facing="south")
    hidden_light(b, 8, 5, 8, level=10)
    b.pot(7, 3, 10)
    b.suspicious(10, 1, 7)
    b.suspicious(8, 1, 9)
    b.erode(0.0)                                       # mounds don't peel


# ================================================================ MAYAN

def observatory(b):
    """Mayan grand: round observatory tower on a twin platform, spiral
    interior, roof comb fragments — El Caracol remembered."""
    import math
    W = D = 18
    b.foundation(0, 0, W, D)
    b.fill(1, 2, 1, W - 1, 2, D - 1, "floor")
    b.fill(2, 3, 2, W - 2, 4, D - 2, "brick")          # lower platform
    string_course(b, 2, 2, W - 2, D - 2, 4, "accent")
    b.fill(4, 5, 4, W - 4, 5, D - 4, "brick")          # upper platform
    for i, z in enumerate((D - 1, D - 2, D - 3)):      # south stair, balustrades
        for x in (8, 9, 10):
            stair = b.resolve("stairs").split("[")[0]
            b.set(x, 3 + i, z, f"{stair}[facing=north,half=bottom,shape=straight,waterlogged=false]", protect=True)
            for yy in range(3, 3 + i):
                b.set(x, yy, z, "brick")
        b.set(7, 3 + i, z, "accent")
        b.set(11, 3 + i, z, "accent")
    # round tower
    cx = cz = W // 2
    for y in range(6, 12):
        r = 3.6 if y < 10 else 2.6
        for deg in range(0, 360, 5):
            a = math.radians(deg)
            x = cx + round(r * math.cos(a))
            z = cz + round(r * math.sin(a))
            keep = b.pristine or y < 9 or b.rng.random() < 0.55
            if keep:
                b.set(x, y, z, "brick")
    b.air(cx - 1, 6, cz - 1, cx + 1, 10, cz + 1)       # hollow core
    corbel_arch(b, cx, 6, cz + 3, 2, axis="x")         # south door
    # Rounded wall rasterization is two blocks thick at the south entrance.
    b.fill(cx, 6, cz + 2, cx + 1, 8, cz + 4, "minecraft:air", protect=True)
    b.fill(cx, 5, cz + 2, cx + 1, 5, cz + 5, "floor", protect=True)
    for y, dx, dz in ((7, 4, 0), (8, 0, 4), (9, -4, 0)):   # spiral window slits
        b.set(cx + dx, y, cz + dz, "minecraft:air")
    b.set(cx, 5, cz, "chiseled", protect=True)
    b.waystone(cx, 6, cz)
    hidden_light(b, cx, 9, cz, level=11)
    b.suspicious(5, 5, 5)
    b.pot(W - 5, 5, 5)
    b.satellite_socket(0, 9, "west_up")
    b.satellite_socket(W, 9, "east_up")
    if not b.pristine:
        vine_creep(b, prob_low=0.35, prob_high=0.1, cutoff=7)
        for _ in range(14):
            x, z = b.rng.randint(2, W - 2), b.rng.randint(2, D - 2)
            for y in (5, 4, 3):
                if (x, y, z) in b.blocks and (x, y + 1, z) not in b.blocks:
                    b.set(x, y + 1, z, "minecraft:moss_carpet")
                    break
    b.erode(0.06, min_y=3)
    b.rubble(1, 1, W - 1, D - 1, 8)


def sacbe_gate(b):
    """Mayan small: a raised white causeway fragment ending in a corbel
    gateway — the sacred road to nowhere now."""
    b.foundation(0, 0, 14, 6)
    for x in range(0, 11):                             # raised causeway
        for z in (2, 3, 4):
            if b.pristine or b.rng.random() < 0.8:
                b.set(x, 2, z, "minecraft:calcite" if b.rng.random() < 0.5 else "floor")
    b.fill(11, 2, 1, 13, 2, 5, "floor")
    b.fill(11, 3, 1, 13, 7, 2, "brick")                # gate mass north
    b.fill(11, 3, 4, 13, 7, 5, "brick")                # gate mass south
    b.fill(11, 7, 3, 13, 7, 3, "brick")                # cap
    corbel_arch(b, 12, 3, 3, 3, axis="x")
    b.set(12, 2, 0, "chiseled", protect=True)
    b.waystone(12, 3, 0, facing="south")
    b.suspicious(5, 1, 3)
    if not b.pristine:
        vine_creep(b, prob_low=0.3, prob_high=0.1, cutoff=5)
    b.erode(0.08)


def cenote_shrine(b):
    """Mayan grand: sacred pool ringed by steps and stelae; offerings sleep
    under the water."""
    W = D = 16
    b.foundation(0, 0, W, D)
    b.fill(0, 2, 0, W, 2, D, "floor")
    # the cenote: sunken 2 deep, waterlogged-slab surface ring
    b.fill(5, 1, 5, 11, 2, 11, "minecraft:water", protect=True)
    b.fill(5, 0, 5, 11, 0, 11, "minecraft:gravel")
    slab = b.resolve("slab").split("[")[0]
    for x in range(4, 13):                             # step ring down
        for z in range(4, 13):
            edge = x in (4, 12) or z in (4, 12)
            if edge:
                b.set(x, 2, z, f"{slab}[type=bottom,waterlogged=false]")
    # stelae ring
    for sx, sz in ((2, 2), (14, 2), (2, 14), (14, 14), (8, 1), (8, 15)):
        b.fill(sx, 3, sz, sx, 4 + (1 if b.rng.random() < 0.5 else 0), sz, "brick")
        b.set(sx, 3, sz, "chiseled")
    # altar platform east with waystone
    b.fill(13, 3, 7, 15, 3, 9, "brick")
    b.set(14, 4, 8, "chiseled", protect=True)
    b.waystone(14, 5, 8, facing="west")
    hidden_light(b, 8, 3, 8, level=9)
    b.suspicious(8, 0, 8)
    b.suspicious(6, 0, 10)
    b.pot(3, 3, 8)
    b.satellite_socket(8, 0, "north_up")
    b.satellite_socket(0, 8, "west_up")
    if not b.pristine:
        vine_creep(b, prob_low=0.3, prob_high=0.08)
        for _ in range(10):
            x, z = b.rng.randint(1, W - 1), b.rng.randint(1, D - 1)
            if (x, 3, z) not in b.blocks and (x, 2, z) in b.blocks and b.blocks[(x, 2, z)][0] != "minecraft:water":
                b.set(x, 3, z, b.rng.choice(("minecraft:moss_carpet", "minecraft:fern")))
    b.erode(0.07)


# ================================================================ NETHER / END

def gilded_reliquary(b):
    """Nether: a looted reliquary vault — gold band mined to scars, chains
    hanging, a crying-obsidian heart no thief could shift."""
    b.hollow_box(0, 0, 0, 12, 8, 12, "brick")
    b.air(1, 1, 1, 11, 7, 11)
    b.fill(1, 0, 1, 11, 0, 11, "floor")
    for x, z in ((3, 3), (3, 9), (9, 3), (9, 9)):
        b.column(x, 1, z, 7, "pillar")
    # the gold band at door-head height, half looted
    for x in range(1, 12):
        for z in (1, 11):
            b.set(x, 4, z, "accent" if b.rng.random() < 0.5 else
                  "minecraft:cracked_polished_blackstone_bricks")
    for z in range(1, 12):
        for x in (1, 11):
            b.set(x, 4, z, "accent" if b.rng.random() < 0.5 else
                  "minecraft:cracked_polished_blackstone_bricks")
    # chains from the ceiling, broken lengths
    for _ in range(6):
        x, z = b.rng.randint(2, 10), b.rng.randint(2, 10)
        for i in range(b.rng.randint(1, 3)):
            b.set(x, 7 - i, z, "minecraft:chain[axis=y,waterlogged=false]")
    b.fill(5, 1, 5, 7, 1, 7, "minecraft:crying_obsidian")
    b.set(6, 2, 6, "minecraft:crying_obsidian", protect=True)
    b.waystone(6, 3, 6)
    b.set(3, 1, 6, "minecraft:soul_campfire[lit=true,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    b.pot(10, 1, 10)
    b.suspicious(2, 0, 9)
    b.rubble(1, 1, 11, 11, 6, y=1)
    b.erode(0.05, min_y=0)
    b.breach(0, 1, 0, 12, 7, 12, count=3)


def void_belfry(b):
    """End: a leaning purpur belfry with floating fragments — its bell long
    since fallen into the void."""
    b.foundation(4, 4, 10, 10)
    b.fill(4, 2, 4, 10, 2, 10, "floor")
    for y in range(3, 16):                             # tower shaft, eroding up
        keep_p = 1.0 if y < 8 else (0.85 if y < 12 else 0.6)
        for x in range(5, 10):
            for z in range(5, 10):
                edge = x in (5, 9) or z in (5, 9)
                corner = x in (5, 9) and z in (5, 9)
                if edge and (b.pristine or b.rng.random() < keep_p):
                    b.set(x, y, z, "pillar" if corner else "brick")
    b.air(6, 3, 6, 8, 14, 8)
    b.air(7, 3, 9, 7, 4, 9)                            # door
    # end rod pinnacles + belfry openings
    for x, z in ((5, 5), (9, 5), (5, 9), (9, 9)):
        b.set(x, 16, z, "minecraft:end_rod[facing=up]", protect=True)
        b.set(x, 15, z, "brick")
    for y in (12, 13):
        for x, z in ((7, 5), (7, 9), (5, 7), (9, 7)):
            b.clear(x, y, z)
    # floating fragments around the tower
    for fx, fy, fz in ((1, 8, 2), (12, 11, 3), (2, 13, 12), (12, 6, 12)):
        b.fill(fx, fy, fz, fx + 1, fy + 1, fz + 1, "cobble")
        if b.rng.random() < 0.5:
            b.set(fx, fy + 2, fz, "minecraft:amethyst_cluster[facing=up,waterlogged=false]")
    b.set(7, 2, 7, "chiseled", protect=True)
    b.waystone(7, 3, 7)
    b.set(6, 3, 6, "minecraft:crying_obsidian")
    b.pot(8, 3, 5)
    b.erode(0.05, min_y=3)


# design registries (merged by build.py after Justin's per-design approval)
EGYPT_SMALL2 = {"sphinx_avenue": sphinx_avenue}
EGYPT_GRAND2 = {"hypostyle_hall": hypostyle_hall, "sun_court": sun_court}
GREEK_SMALL2 = {"odeon": odeon, "spring_house": spring_house}
GREEK_GRAND2 = {"temple_of_the_way": temple_of_the_way}
BABYLON_SMALL2 = {"tablet_house": tablet_house}
BABYLON_GRAND2 = {"ishtar_gate": ishtar_gate, "hanging_terrace": hanging_terrace}
VIKING_SMALL2 = {"boat_grave_field": boat_grave_field}
VIKING_GRAND2 = {"stave_shrine": stave_shrine, "jarl_barrow": jarl_barrow}
MAYAN_SMALL2 = {"sacbe_gate": sacbe_gate}
MAYAN_GRAND2 = {"observatory": observatory, "cenote_shrine": cenote_shrine}
NETHER2 = {"gilded_reliquary": gilded_reliquary}
END2 = {"void_belfry": void_belfry}

ALL2 = {}
for d in (EGYPT_SMALL2, EGYPT_GRAND2, GREEK_SMALL2, GREEK_GRAND2,
          BABYLON_SMALL2, BABYLON_GRAND2, VIKING_SMALL2, VIKING_GRAND2,
          MAYAN_SMALL2, MAYAN_GRAND2, NETHER2, END2):
    ALL2.update(d)
