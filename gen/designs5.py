"""v1.11: the Celtic half of the Norse & Celtic school (theme "viking",
frozen biomes). Drystone and earth rather than timber: a henge, a portal
dolmen, a clootie well, an Iron-Age broch, a cruciform passage tomb and a
conical-roofed roundhouse. All surface designs with the walking level at
template y2 (no basements), so they use the standard underpin/clearance path.
"""
import math

from master import hidden_light, loot_chest, sarcophagus


def _ring(cx, cz, r_lo, r_hi):
    """Integer cells whose centre distance from (cx, cz) lies in (r_lo, r_hi]."""
    cells = []
    R = int(math.ceil(r_hi)) + 1
    for x in range(cx - R, cx + R + 1):
        for z in range(cz - R, cz + R + 1):
            d = math.hypot(x - cx, z - cz)
            if r_lo < d <= r_hi:
                cells.append((x, z))
    return cells


def _slab(b, x, y, z, role="cobble_slab", half="bottom"):
    base = b.resolve(role).split("[")[0]
    b.set(x, y, z, f"{base}[type={half},waterlogged=false]")


# ================================================================ SMALL

def henge(b):
    """Celtic small: a ring of standing stones, two lintels still up, a
    recumbent altar stone on the south side, kerb of bank stones."""
    C = 6
    b.foundation(0, 0, 12, 12)
    for x, z in _ring(C, C, -1, 4.6):                  # trodden inner floor
        if b.rng.random() < 0.6:
            b.set(x, 2, z, "floor")
    for x, z in _ring(C, C, 5.6, 6.6):                 # low bank / kerb
        if b.rng.random() < 0.45:
            b.set(x, 2, z, "cobble")
            b.set(x, 3, z, "wall")
    # ten stones on the circle; north and east pairs carry lintels
    stones = [(C + round(5 * math.cos(a)), C + round(5 * math.sin(a)))
              for a in (math.radians(k * 36) for k in range(10))]
    for x, z in stones:
        if (x, z) in ((5, 1), (7, 1), (11, 5), (11, 7)):
            continue
        h = b.rng.choice((2, 3, 3, 4))
        b.set(x, 2, z, "cobble")
        b.column(x, 3, z, h, "brick", cap="chiseled" if h >= 3 and b.rng.random() < 0.5 else None)
    for (x0, z0), (x1, z1) in (((5, 1), (7, 1)), ((11, 5), (11, 7))):   # trilithons
        for x, z in ((x0, z0), (x1, z1)):
            b.set(x, 2, z, "cobble")
            b.column(x, 3, z, 4, "brick")
        b.fill(x0, 7, z0, x1, 7, z1, "brick")
    b.fill(5, 3, 10, 7, 3, 10, "brick")                # recumbent altar stone
    b.set(6, 3, 10, "chiseled")
    b.set(C, 2, C, "chiseled", protect=True)
    b.waystone(C, 3, C)
    b.set(4, 3, 8, "light")
    b.suspicious(8, 2, 8)
    b.rubble(1, 1, 11, 11, 4)
    b.erode(0.07)


def dolmen(b):
    """Celtic small: portal tomb - three uprights under one great capstone,
    the waystone sheltered beneath, a scatter of cairn stones around."""
    b.foundation(0, 0, 8, 8)
    b.fill(1, 2, 1, 7, 2, 7, "floor")
    for x, z in _ring(4, 4, 3.4, 4.6):                 # remnant cairn ring
        if 0 <= x <= 8 and 0 <= z <= 8 and b.rng.random() < 0.5:
            b.set(x, 2, z, "cobble")
    for x, z, h in ((2, 3, 3), (2, 5, 3), (6, 4, 3)):  # uprights
        b.column(x, 3, z, h, "brick")
    b.fill(1, 6, 2, 6, 6, 5, "brick", protect=True)    # capstone
    b.set(1, 6, 2, "chiseled", protect=True)
    b.set(4, 2, 4, "chiseled", protect=True)
    b.waystone(4, 3, 4, facing="south")
    b.pot(3, 3, 5)
    b.suspicious(5, 2, 3)
    b.set(7, 3, 7, "light")
    b.rubble(0, 0, 8, 8, 6)
    b.erode(0.06)


def holy_well(b):
    """Celtic small: a clootie well - stone-lined spring under a small
    gateway, a rag tree beside it, the waystone across the pool."""
    b.foundation(0, 0, 8, 8)
    b.fill(1, 2, 1, 7, 2, 7, "floor")
    b.fill(3, 2, 3, 5, 2, 5, "brick")                  # basin rim
    b.set(4, 2, 4, "minecraft:water", protect=True)    # the spring
    for x, z in ((3, 3), (4, 3), (5, 3), (3, 4), (5, 4), (3, 5), (5, 5)):
        b.set(x, 3, z, "brick")                        # low wellhead wall
    for x in (3, 5):                                   # gateway over the north side
        b.column(x, 4, 3, 2, "brick")
    b.fill(3, 6, 3, 5, 6, 3, "brick")
    b.set(4, 6, 3, "chiseled")
    b.column(1, 3, 1, 4, "pillar")                     # the rag tree
    leaves = "minecraft:spruce_leaves[distance=7,persistent=true,waterlogged=false]"
    for dx, dy, dz in ((0, 4, 0), (1, 3, 0), (0, 3, 1), (1, 4, 1), (-0, 5, 1), (1, 5, 0)):
        if 0 <= 1 + dx <= 8 and 0 <= 1 + dz <= 8:
            b.set(1 + dx, 3 + dy, 1 + dz, leaves)
    b.set(7, 2, 4, "chiseled", protect=True)
    b.waystone(7, 3, 4, facing="west")
    b.set(2, 3, 6, "light")
    b.suspicious(6, 2, 6)
    b.pot(6, 3, 2)
    b.erode(0.06)


# ================================================================ GRAND

def broch(b):
    """Celtic grand: Iron-Age drystone tower, thick double wall, one low
    door on the south, hearth and waystone within, top courses tumbled."""
    C, H = 7, 10
    b.foundation(0, 0, 14, 14)
    for x, z in _ring(C, C, -1, 4.0):
        b.set(x, 2, z, "floor")
    for x, z in _ring(C, C, 4.0, 6.5):                 # wall mass, y3..H
        top = H - (b.rng.choice((0, 0, 1, 2)) if math.hypot(x - C, z - C) > 5.6 else 0)
        b.fill(x, 2, z, x, top, z, "brick")
    for x, z in _ring(C, C, 5.6, 6.5):                 # outer batter: cobble skin low down
        b.fill(x, 2, z, x, 4, z, "cobble")
    # scarcement ledge inside at y6 (slabs on the wall face)
    for x, z in _ring(C, C, 3.4, 4.0):
        _slab(b, x, 6, z, "cobble_slab", "top")
    # four window slits high up
    for a in (45, 135, 225, 315):
        x = C + round(5 * math.cos(math.radians(a)))
        z = C + round(5 * math.sin(math.radians(a)))
        b.set(x, 7, z, "minecraft:air")
    # south door: floor + two-high opening straight through the wall
    for z in range(11, 15):
        b.set(C, 2, z, "floor", protect=True)
        b.fill(C, 3, z, C, 4, z, "minecraft:air", protect=True)
    b.set(C, 5, 12, "chiseled")                        # door lintel
    b.set(C, 3, C, "minecraft:campfire[lit=false,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    b.set(C, 2, 4, "chiseled", protect=True)
    b.waystone(C, 3, 4, facing="south")
    hidden_light(b, C, 6, C, level=10)
    b.pot(5, 3, 9)
    b.pot(9, 3, 9)
    b.suspicious(9, 2, 5)
    b.satellite_socket(0, C, "west_up")
    b.satellite_socket(14, C, "east_up")
    b.erode(0.10, min_y=7)
    b.rubble(0, 0, 14, 14, 6)


def passage_tomb(b):
    """Celtic grand: kerbed earthen mound over a stone-lined passage and a
    cruciform chamber; carved stones flank the entrance, the waystone stands
    in the north recess."""
    C, R = 10, 9
    b.foundation(1, 1, 19, 19)
    for x in range(0, 21):                             # the mound
        for z in range(0, 21):
            d = math.hypot(x - C, z - C)
            if d > R:
                continue
            h = max(1, round((R - d) * 0.75))
            b.fill(x, 0, z, x, 1, z, "minecraft:dirt")
            for y in range(2, 2 + h):
                b.set(x, y, z, "minecraft:dirt" if y < 1 + h else "minecraft:moss_block")
            if d > R - 2.5 and b.rng.random() < 0.3:
                b.set(x, 2 + h, z, "minecraft:moss_carpet")
    for x, z in _ring(C, C, 8.6, 9.6):                 # kerbstones
        b.set(x, 2, z, "brick")
        if b.rng.random() < 0.5:
            b.set(x, 3, z, "wall")
    # stone shell around chamber + passage, then hollow the interior
    chamber = [(8, 3, 8, 12, 6, 12),                   # main chamber
               (9, 3, 6, 11, 5, 7),                    # north recess
               (13, 3, 9, 14, 5, 11),                  # east recess
               (6, 3, 9, 7, 5, 11)]                    # west recess
    passage = (10, 3, 13, 10, 4, 19)
    for x0, y0, z0, x1, y1, z1 in chamber + [passage]:
        b.fill(x0 - 1, y0 - 1, z0 - 1, x1 + 1, y1 + 1, z1 + 1, "brick")
    for x0, y0, z0, x1, y1, z1 in chamber + [passage]:
        b.fill(x0, y0 - 1, z0, x1, y0 - 1, z1, "floor", protect=True)
        b.fill(x0, y0, z0, x1, y1, z1, "minecraft:air", protect=True)
    b.set(9, 5, 20, "minecraft:air", protect=True)
    b.fill(C, 2, 20, C, 2, 20, "floor", protect=True)   # threshold
    b.fill(C, 3, 20, C, 4, 20, "minecraft:air", protect=True)
    b.set(9, 3, 20, "chiseled", protect=True)          # carved entrance stones
    b.set(11, 3, 20, "chiseled", protect=True)
    b.set(C, 5, 20, "chiseled")                        # roof-box lintel
    b.set(C, 2, 6, "chiseled", protect=True)
    b.waystone(C, 3, 6, facing="south")
    loot_chest(b, 6, 3, 10, facing="east")
    sarcophagus(b, 13, 3, 9, axis="z")
    b.pot(8, 3, 12)
    b.pot(12, 3, 8)
    b.suspicious(C, 2, 15)
    hidden_light(b, C, 6, C, level=9)
    hidden_light(b, C, 4, 16, level=7)
    b.satellite_socket(0, C, "west_up")
    b.satellite_socket(20, C, "east_up")
    b.erode(0.04, min_y=3)


def roundhouse(b):
    """Celtic grand: post-and-plank roundhouse under a steep conical roof,
    inner post ring, long hearth, waystone against the north wall."""
    C = 7
    b.foundation(0, 0, 14, 14)
    for x, z in _ring(C, C, -1, 5.5):
        b.set(x, 2, z, "floor")
    for x, z in _ring(C, C, 5.5, 6.5):                 # wattle wall on a stone footing
        b.set(x, 2, z, "cobble")
        b.fill(x, 3, z, x, 5, z, "plank")
    for k in range(12):                                # wall posts
        a = math.radians(k * 30)
        x, z = C + round(6 * math.cos(a)), C + round(6 * math.sin(a))
        b.column(x, 3, z, 3, "pillar")
    for k in range(6):                                 # inner roof posts
        a = math.radians(k * 60 + 30)
        x, z = C + round(3 * math.cos(a)), C + round(3 * math.sin(a))
        b.column(x, 3, z, 5, "pillar")
    for k in range(7):                                 # conical roof, ring by ring
        y = 6 + k
        lo, hi = (5.5, 7.5) if k == 0 else (6.5 - k - 1, 6.5 - k)
        for x, z in _ring(C, C, lo, hi):
            b.set(x, y, z, "plank")
    b.set(C, 12, C, "plank")
    # south door through wall
    for z in range(12, 15):
        b.set(C, 2, z, "floor", protect=True)
        b.fill(C, 3, z, C, 4, z, "minecraft:air", protect=True)
    for x in range(5, 10):                             # hearth line
        b.set(x, 2, C, "minecraft:coarse_dirt")
        if x % 2 == 1:
            b.set(x, 3, C, "minecraft:campfire[lit=false,facing=north,signal_fire=false,waterlogged=false]", protect=True)
    for x, z in _ring(C, C, 4.5, 5.5):                 # sleeping platforms along the wall
        if (x, z) not in ((C, 12), (C, 13)) and b.rng.random() < 0.7:
            _slab(b, x, 3, z, "slab", "top")
    b.set(C, 2, 3, "chiseled", protect=True)
    b.waystone(C, 3, 3, facing="south")
    loot_chest(b, 4, 3, 9, facing="east")
    b.pot(10, 3, 9)
    b.suspicious(9, 2, 5)
    hidden_light(b, C, 7, C, level=10)
    b.satellite_socket(0, C, "west_up")
    b.satellite_socket(14, C, "east_up")
    b.erode(0.09, min_y=6)


CELTIC_SMALL = {"henge": henge, "dolmen": dolmen, "holy_well": holy_well}
CELTIC_GRAND = {"broch": broch, "passage_tomb": passage_tomb, "roundhouse": roundhouse}

ALL5 = dict(CELTIC_SMALL, **CELTIC_GRAND)

# cutaway render heights (template y; blocks above are stripped in the _cutaway view)
broch.cutaway = 6
passage_tomb.cutaway = 6
roundhouse.cutaway = 6
