"""The 17 ruin designs. Surface convention: template y0-1 = buried foundation,
y2 = floor flush with terrain (structure start_height is absolute -3 with
WORLD_SURFACE_WG projection), features from y3 up. Underground designs are
fully enclosed rooms with explicit interior air, floor at y0."""


# ---------------------------------------------------------------- small surface

def dais(b):
    b.foundation(0, 0, 6, 6)
    b.fill(0, 2, 0, 6, 2, 6, "floor")
    for cx, cz in ((0, 0), (0, 6), (6, 0), (6, 6)):   # trim corners round-ish
        b.clear(cx, 2, cz)
    b.fill(2, 3, 2, 4, 3, 4, "brick")                  # raised 3x3 platform
    for x, z in ((1, 1), (1, 5), (5, 1), (5, 5)):
        b.set(x, 3, z, "wall")
    b.set(1, 4, 1, "light")
    b.waystone(3, 4, 3)
    b.erode(0.07)


def broken_ring(b):
    b.foundation(2, 2, 8, 8)
    b.fill(3, 2, 3, 7, 2, 7, "floor")
    heights = [4, 1, 3, 2, 4, 1, 2, 3]
    ring = [(5, 1), (8, 2), (9, 5), (8, 8), (5, 9), (2, 8), (1, 5), (2, 2)]
    for (x, z), h in zip(ring, heights):
        b.set(x, 1, z, "cobble")                       # each monolith gets footing
        b.column(x, 2, z, h, "brick", cap="brick_wall" if h >= 3 else None)
    b.set(5, 3, 5, "chiseled")
    b.waystone(5, 4, 5)
    b.rubble(1, 1, 9, 9, 7)
    b.erode(0.08)


def arch(b):
    b.foundation(0, 1, 6, 3)
    b.fill(0, 2, 1, 6, 2, 3, "floor")
    # v1.16: five-course piers. The lintel used to sit one block above the
    # waystone and read as a lid; three clear blocks make it a gateway.
    for x in (1, 5):
        b.column(x, 3, 2, 5, "brick", cap="chiseled")
    b.fill(2, 8, 2, 4, 8, 2, "brick")                  # lintel
    b.set(3, 9, 2, "brick_wall")
    b.waystone(3, 3, 2)
    b.erode(0.06)


def gazebo(b):
    b.foundation(0, 0, 6, 6)
    b.fill(0, 2, 0, 6, 2, 6, "floor")
    for x, z in ((1, 1), (1, 5), (5, 1), (5, 5)):
        b.column(x, 3, z, 3, "brick", cap="chiseled")
    b.hollow_box(1, 7, 1, 5, 7, 5, "brick")            # roof ring
    for x in range(2, 5):
        for z in range(2, 5):
            base = b.resolve("slab").split("[")[0]
            b.set(x, 8, z, f"{base}[type=bottom,waterlogged=false]")
    b.waystone(3, 3, 3)
    b.erode(0.05)


def collapsed_shrine(b):
    b.foundation(1, 1, 7, 7)
    b.fill(1, 2, 1, 7, 2, 7, "floor")
    for x in range(1, 8):
        for z in range(1, 8):
            if x in (1, 7) or z in (1, 7):
                h = b.rng.choice((1, 2, 3, 3))
                if z == 7 and x in (3, 4, 5):          # doorway, south
                    continue
                b.column(x, 3, z, h, "brick")
    b.waystone(4, 3, 3)
    b.suspicious(3, 2, 5)
    b.rubble(2, 2, 6, 6, 5)
    b.erode(0.15)


def obelisks(b):
    b.foundation(1, 1, 7, 3)
    b.fill(1, 2, 1, 7, 2, 3, "floor")
    for x in (2, 6):
        b.column(x, 3, 2, 4, "brick", cap="brick_wall")
    b.waystone(4, 3, 2)
    b.erode(0.07)


def cairn(b):
    b.foundation(0, 0, 4, 4)
    b.fill(0, 2, 0, 4, 2, 4, "cobble")
    for cx, cz in ((0, 0), (0, 4), (4, 0), (4, 4)):
        b.clear(cx, 2, cz)
    b.fill(1, 3, 1, 3, 3, 3, "cobble")
    b.waystone(2, 4, 2)
    b.erode(0.06)


def well_shrine(b):
    b.foundation(1, 1, 7, 7)
    b.fill(1, 2, 1, 7, 2, 7, "floor")
    for x in range(1, 8):
        for z in range(1, 8):
            if x in (1, 7) or z in (1, 7):
                b.set(x, 3, z, "wall")
    for x, z in ((1, 1), (1, 7), (7, 1), (7, 7)):
        b.set(x, 3, z, "brick")
        b.set(x, 4, z, "light")
    b.clear(4, 3, 7)                                   # entrance gap, south
    b.fill(3, 3, 3, 5, 3, 5, "brick")
    b.waystone(4, 4, 4)
    b.suspicious(2, 2, 2)
    b.erode(0.07)


def watch_stub(b):
    b.foundation(1, 1, 7, 7)
    b.fill(2, 2, 2, 6, 2, 6, "floor")
    for x in range(1, 8):
        for z in range(1, 8):
            edge = x in (1, 7) or z in (1, 7)
            corner = (x in (1, 7)) and (z in (1, 7))
            if edge and not corner:
                if z == 7 and x == 4:                  # doorway, south
                    continue
                h = b.rng.choice((2, 3, 4, 5, 6))
                b.column(x, 3, z, h, "brick")
    b.waystone(4, 3, 4)
    b.rubble(0, 0, 8, 8, 8)
    b.erode(0.12)


# ---------------------------------------------------------------- grand surface

def colonnade_temple(b):
    b.foundation(0, 0, 14, 10)
    b.fill(0, 2, 0, 14, 2, 10, "floor")
    b.fill(1, 3, 1, 13, 3, 9, "floor")                 # stylobate
    b.steps_row(5, 9, 3, 10, "north")                  # entry steps, south face
    for x in (3, 5, 7, 9, 11):
        for z in (3, 7):
            b.column(x, 4, z, 4, "brick", cap="chiseled")
    b.fill(2, 9, 3, 12, 9, 3, "brick")                 # architraves
    b.fill(2, 9, 7, 12, 9, 7, "brick")
    b.fill(10, 4, 4, 12, 4, 6, "chiseled")             # waystone dais, rear
    b.waystone(11, 5, 5)
    b.suspicious(5, 3, 5)
    b.satellite_socket(7, 10, "south_up")
    b.satellite_socket(7, 0, "north_up")
    b.erode(0.10)
    b.rubble(0, 0, 14, 10, 6)


def step_pyramid(b):
    b.foundation(0, 0, 14, 14)
    tiers = [(2, 0), (3, 1), (4, 2), (5, 3), (6, 4), (7, 5)]
    for y, inset in tiers:
        b.fill(inset, y, inset, 14 - inset, y, 14 - inset, "brick")
    for y, z in ((3, 13), (4, 12), (5, 11), (6, 10), (7, 9)):   # south stair
        for x in (6, 7, 8):
            b.clear(x, y, z)
            b.stairs(x, y, z, "north")
    for x, z in ((5, 5), (9, 5), (5, 9), (9, 9)):      # canopy posts
        b.column(x, 8, z, 4, "brick", cap=None)
    for x in range(5, 10):
        for z in range(5, 10):
            base = b.resolve("slab").split("[")[0]
            b.set(x, 12, z, f"{base}[type=bottom,waterlogged=false]")
    b.set(7, 8, 7, "chiseled", protect=True)
    b.waystone(7, 9, 7)
    b.suspicious(4, 6, 4)
    b.suspicious(10, 6, 10)
    b.satellite_socket(0, 7, "west_up")
    b.satellite_socket(14, 7, "east_up")
    b.erode(0.06, min_y=3)


def courtyard_sanctum(b):
    b.foundation(0, 0, 16, 16)
    b.fill(7, 2, 0, 9, 2, 16, "floor")                 # cross paths
    b.fill(0, 2, 7, 16, 2, 9, "floor")
    for x in range(0, 17):
        for z in range(0, 17):
            if x in (0, 16) or z in (0, 16):
                if z == 16 and x in (7, 8, 9):         # gate, south
                    b.set(x, 2, z, "floor")
                    continue
                b.fill(x, 3, z, x, 4, z, "brick")
                if (x + z) % 2 == 0:
                    b.set(x, 5, z, "brick_wall")
    for cx, cz in ((1, 1), (1, 15), (15, 1), (15, 15)):    # corner turrets
        for x in range(cx - 1, cx + 2):
            for z in range(cz - 1, cz + 2):
                if x in (cx - 1, cx + 1) or z in (cz - 1, cz + 1):
                    b.column(x, 3, z, b.rng.choice((2, 3, 4)), "brick")
    b.fill(6, 3, 6, 10, 3, 10, "floor")                # central shrine platform
    for x, z in ((6, 6), (6, 10), (10, 6), (10, 10)):
        b.column(x, 4, z, 3, "brick", cap=None)
    for x in range(6, 11):
        for z in range(6, 11):
            base = b.resolve("slab").split("[")[0]
            b.set(x, 7, z, f"{base}[type=bottom,waterlogged=false]")
    b.waystone(8, 4, 8)
    b.suspicious(8, 2, 3)
    b.suspicious(3, 2, 8)
    b.satellite_socket(8, 16, "south_up")
    b.satellite_socket(0, 8, "west_up")
    b.erode(0.10)
    b.rubble(1, 1, 15, 15, 10)


def great_hall(b):
    b.foundation(0, 0, 14, 10)
    b.fill(0, 2, 0, 14, 2, 10, "floor")
    b.fill(0, 3, 1, 0, 7, 9, "brick")                  # west gable wall
    b.fill(0, 8, 3, 0, 8, 7, "brick")
    b.fill(0, 9, 4, 0, 9, 6, "brick")
    b.set(0, 10, 5, "brick")
    b.fill(14, 3, 1, 14, 4, 9, "brick")                # ruined east wall
    for x in range(0, 15):                             # side walls + pilasters
        for z in (1, 9):
            top = 6 if x % 3 == 0 else 4
            b.fill(x, 3, z, x, top, z, "brick")
    b.fill(14, 3, 4, 14, 5, 6, "minecraft:air", protect=True)
    b.fill(13, 2, 4, 14, 2, 6, "floor", protect=True)
    for x in (3, 6, 9, 12):                            # interior columns
        for z in (3, 7):
            b.column(x, 3, z, b.rng.choice((1, 2, 3, 3)), "brick")
    b.fill(1, 3, 4, 3, 3, 6, "chiseled")               # apse dais, west
    b.waystone(2, 4, 5)
    b.suspicious(7, 2, 5)
    b.satellite_socket(14, 5, "east_up")
    b.satellite_socket(7, 10, "south_up")
    b.rubble(1, 2, 13, 8, 9)
    b.erode(0.13)


# ---------------------------------------------------------------- underground

def crypt_cell(b):
    b.hollow_box(0, 0, 0, 8, 6, 8, "brick")
    b.air(1, 1, 1, 7, 5, 7)
    b.fill(1, 0, 1, 7, 0, 7, "floor")
    for x, z in ((1, 1), (1, 7), (7, 1), (7, 7)):
        b.column(x, 1, z, 5, "cobble")
    b.set(2, 1, 2, "light")
    b.set(6, 1, 6, "light")
    b.pot(2, 1, 6)
    b.pot(6, 1, 2)
    b.set(4, 1, 4, "chiseled", protect=True)
    b.waystone(4, 2, 4)
    b.rubble(1, 1, 7, 7, 5, y=1)
    b.erode(0.05, min_y=0)
    b.breach(0, 1, 0, 8, 5, 8, count=3)


def pillared_vault(b):
    b.hollow_box(0, 0, 0, 12, 7, 12, "brick")
    b.air(1, 1, 1, 11, 6, 11)
    b.fill(1, 0, 1, 11, 0, 11, "floor")
    for x, z in ((3, 3), (3, 9), (9, 3), (9, 9)):
        b.column(x, 1, z, 6, "brick")
        b.set(x, 1, z, "chiseled")
    b.fill(5, 1, 5, 7, 1, 7, "accent")
    b.set(6, 6, 3, "hanging_light")
    b.set(6, 6, 9, "hanging_light")
    b.pot(2, 1, 10)
    b.pot(10, 1, 2)
    b.waystone(6, 2, 6)
    b.rubble(1, 1, 11, 11, 6, y=1)
    b.erode(0.05, min_y=0)
    b.shaft(2, 2, 7, 9)                                # gravel-plugged way in
    b.breach(0, 1, 0, 12, 6, 12, count=2)


def stair_sanctum(b):
    b.hollow_box(0, 0, 0, 8, 6, 14, "brick")
    b.air(1, 1, 1, 7, 5, 13)
    b.fill(1, 0, 1, 7, 0, 13, "floor")
    for z in (3, 6, 9):
        for x in (2, 6):
            b.column(x, 1, z, 4, "brick")
    b.fill(2, 1, 11, 6, 1, 13, "brick")                # raised alcove, far end
    for x in (3, 4, 5):
        b.stairs(x, 1, 10, "south")
    b.set(2, 2, 11, "light")
    b.set(6, 2, 11, "light")
    b.waystone(4, 2, 12)
    b.suspicious(2, 0, 3)
    b.rubble(1, 1, 7, 9, 4, y=1)
    b.erode(0.05, min_y=0)
    b.breach(0, 1, 0, 8, 5, 14, count=2)


def grand_crypt(b):
    b.hollow_box(0, 0, 0, 16, 9, 16, "brick")
    b.air(1, 1, 1, 15, 8, 15)
    b.fill(1, 0, 1, 15, 0, 15, "floor")
    for x in (4, 8, 12):
        for z in (4, 12):
            b.column(x, 1, z, 8, "brick")
    for z in (8,):
        for x in (4, 12):
            b.column(x, 1, z, 8, "brick")
    b.fill(6, 1, 6, 10, 1, 10, "brick")                # tiered central dais
    b.fill(7, 2, 7, 9, 2, 9, "chiseled")
    b.waystone(8, 3, 8)
    for x, z in ((6, 6), (10, 6), (6, 10), (10, 10)):
        b.set(x, 2, z, "light")
    b.pot(3, 1, 3)
    b.pot(13, 1, 5)
    b.pot(5, 1, 13)
    b.suspicious(5, 0, 5)
    b.suspicious(11, 0, 6)
    b.fill(12, 1, 12, 15, b.rng.choice((2, 3)), 15, "cobble")   # collapsed corner
    b.rubble(1, 1, 15, 15, 12, y=1)
    b.erode(0.06, min_y=0)
    b.shaft(2, 2, 9, 10)                               # gravel-plugged way in
    b.breach(0, 1, 0, 16, 8, 16, count=3)


# ---------------------------------------------------------------- new in v1.1

def barrow(b):
    """Earthen burial mound with a hidden waystone chamber, entrance south."""
    c = 5
    for x in range(0, 11):
        for z in range(0, 11):
            r = int(((x - c) ** 2 + (z - c) ** 2) ** 0.5 + 0.3)
            if r > 5:
                continue
            h = {0: 5, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}[r]
            b.fill(x, 0, z, x, 1, z, "minecraft:dirt")
            for y in range(2, 2 + h):
                b.set(x, y, z, "minecraft:dirt")
            b.set(x, 1 + h, z, "minecraft:grass_block[snowy=false]")
    b.air(4, 3, 4, 6, 5, 6)                            # chamber
    b.fill(4, 2, 4, 6, 2, 6, "cobble")
    b.set(5, 2, 5, "chiseled", protect=True)
    b.waystone(5, 3, 5)
    b.set(4, 3, 4, "light")
    b.pot(6, 3, 6)
    b.air(5, 3, 7, 5, 4, 9)                            # entrance corridor
    for z in (7, 8):
        b.set(4, 3, z, "brick")
        b.set(6, 3, z, "brick")
        b.set(4, 4, z, "brick")
        b.set(6, 4, z, "brick")
    b.set(5, 5, 7, "chiseled")                         # lintel marker


def pillar_fall(b):
    """Satellite: a toppled column lying in the grass."""
    b.foundation(0, 1, 6, 3)
    b.fill(0, 2, 1, 2, 2, 3, "floor")
    b.fill(1, 3, 2, 1, 4, 2, "brick")                  # broken standing base
    b.set(1, 5, 2, "wall")
    for x in (3, 4, 6):                                # fallen drums, with a gap
        b.set(x, 3, 2, "brick")
    b.plug(0, 2, "west_up")
    b.erode(0.08)


def path_frag(b):
    """Satellite: a scrap of ancient paved road."""
    b.foundation(0, 1, 6, 3)
    for x in range(0, 7):
        for z in range(1, 4):
            if b.rng.random() < 0.75:
                b.set(x, 2, z, "floor")
    b.set(6, 3, 1, "wall")                             # stub of a marker post
    b.plug(0, 2, "west_up")


def gate_stub(b):
    """Satellite: a free-standing ruined gateway."""
    b.foundation(0, 0, 4, 4)
    b.fill(0, 2, 0, 4, 2, 4, "floor")
    b.column(1, 3, 2, 3, "brick", cap="chiseled")
    b.column(3, 3, 2, 2, "brick")
    b.plug(0, 2, "west_up")
    b.rubble(0, 0, 4, 4, 3)
    b.erode(0.10)


def drowned_shrine(b):
    """River-bed shrine: full cubes only (waterlogging handles the rest);
    the waystone rides a tall plinth so it breaks the surface."""
    b.foundation(0, 0, 8, 8)
    b.fill(1, 2, 1, 7, 2, 7, "floor")
    ring = [(4, 1), (7, 2), (7, 6), (4, 7), (1, 6), (1, 2)]
    for (x, z), h in zip(ring, (3, 1, 2, 2, 3, 1)):
        b.column(x, 3, z, h, "brick")
    b.fill(3, 3, 3, 5, 3, 5, "brick")                  # plinth, two tiers
    b.set(4, 4, 4, "chiseled", protect=True)
    b.waystone(4, 5, 4)
    b.set(3, 4, 3, "light")
    b.set(5, 4, 5, "light")
    b.suspicious(2, 2, 6)
    b.erode(0.08)


# ------------------------------------------------- v1.2: the regional schools

def pylon_gate(b):
    """Egyptian: two tapered pylon towers flanking a gate, waystone beneath."""
    b.foundation(0, 0, 10, 4)
    b.fill(0, 2, 0, 10, 2, 4, "floor")
    # v1.16: two courses taller so the gate passage clears the waystone by
    # three blocks instead of one.
    for x0 in (0, 7):                                  # tier 1 of each pylon
        b.fill(x0, 3, 0, x0 + 3, 6, 4, "brick")
    b.fill(1, 7, 1, 3, 9, 3, "brick")                  # tapered tier 2
    b.fill(7, 7, 1, 9, 9, 3, "brick")
    b.set(2, 10, 2, "minecraft:gold_block", protect=True)
    b.set(8, 10, 2, "minecraft:gold_block", protect=True)
    b.fill(4, 8, 1, 6, 9, 3, "brick")                  # gate lintel
    b.waystone(5, 3, 2)
    b.erode(0.08)


def obelisk_avenue(b):
    """Egyptian: processional way between obelisk pairs, one cap still gilded."""
    b.foundation(0, 0, 12, 4)
    b.fill(0, 2, 1, 12, 2, 3, "floor")
    for x in (2, 6):
        for z in (0, 4):
            b.column(x, 3, z, 4, "brick", cap=None)
            if (x, z) == (6, 0):
                b.set(x, 7, z, "minecraft:gold_block", protect=True)
            else:
                b.set(x, 7, z, "wall")
    b.set(10, 2, 2, "chiseled", protect=True)
    b.waystone(10, 3, 2)
    b.erode(0.07)


def mastaba(b):
    """Egyptian: flat-topped tomb, hidden waystone chamber, north passage."""
    b.foundation(0, 0, 14, 14)
    b.fill(1, 3, 1, 13, 4, 13, "brick")                # three squat tiers
    b.fill(3, 5, 3, 11, 6, 11, "brick")
    b.fill(5, 7, 5, 9, 7, 9, "brick")
    b.set(7, 8, 7, "minecraft:gold_block", protect=True)
    b.air(6, 3, 6, 8, 5, 8)                            # burial chamber
    b.fill(6, 2, 6, 8, 2, 8, "floor")
    b.waystone(7, 3, 7)
    b.air(7, 3, 1, 7, 4, 5)                            # entrance passage, north
    b.fill(7, 2, 1, 7, 2, 5, "floor")
    b.set(6, 3, 1, "brick")
    b.set(8, 3, 1, "brick")
    b.set(7, 5, 1, "chiseled")
    b.pot(6, 3, 6)
    b.suspicious(6, 2, 8)
    b.suspicious(8, 2, 6)
    b.satellite_socket(7, 14, "south_up")
    b.satellite_socket(0, 7, "west_up")
    b.erode(0.05, min_y=3)


def stoa(b):
    """A roofless portico fragment, its lost length legible in buried footings."""
    from archaeology import (fragment_floor, standing_column, fallen_column,
                             wall_remnant, quiet_waystone)
    b.archaeological = True
    fragment_floor(b, 0, 0, 15, 7)
    # The wall survives at a bonded return, tapering into foundation courses.
    wall_remnant(b, [(x, 0, h) for x, h in enumerate((2, 3, 3, 2, 2, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0))], 2)
    wall_remnant(b, [(0, z, h) for z, h in ((1, 3), (2, 2), (3, 1))], 2)
    survivor = b.rng.choice((2, 5))
    for x in (2, 5, 8, 11, 14):
        height = 4 if x == survivor else b.rng.choice((0, 1, 1, 2))
        standing_column(b, x, 6, 2, height, complete=x == survivor)
    fallen_column(b, 9, 7, 2, 4, direction=(1, 0))
    # A second strip of paving hints at a vanished courtyard, not a cut-off box.
    for x, z in ((3, 8), (4, 8), (4, 9), (5, 9), (6, 9), (7, 10)):
        b.set(x, 2, z, "floor")
    b.suspicious(12, 2, 1)
    quiet_waystone(b, 6, 3, 2, facing="south")


def tholos(b):
    """An open rotunda: one standing sector, broken drums and a grassy center."""
    import math
    from archaeology import standing_column, fallen_column, quiet_waystone
    b.archaeological = True
    for x in range(17):
        for z in range(17):
            radius = math.hypot(x-8, z-8)
            if radius <= 7.2 and (radius < 5.8 or (x//2 + z//2) % 3 != 0):
                b.set(x, 2, z, "floor")
                b.fill(x, 0, z, x, 1, z, "cobble")
    for i in range(8):
        a = i * math.tau/8
        x, z = 8 + round(6*math.cos(a)), 8 + round(6*math.sin(a))
        whole = b.pristine or i in (5, 6)
        standing_column(b, x, z, 2, 5 if whole else b.rng.choice((0, 1, 2, 3)), complete=whole)
    if not b.pristine:
        fallen_column(b, 13, 10, 2, 4, direction=(0, 1))
        fallen_column(b, 2, 9, 2, 3, direction=(0, 1))
    b.suspicious(4, 2, 7)
    quiet_waystone(b, 8, 8, 2)
    b.satellite_socket(8, 0, "north_up")
    b.satellite_socket(8, 16, "south_up")


def amphitheater(b):
    """Greek: tiered seating facing an orchestra floor, waystone center stage."""
    b.foundation(0, 0, 14, 10)
    b.fill(1, 2, 5, 13, 2, 10, "floor")                # orchestra
    tiers = [(5, 3), (4, 4), (3, 5)]
    for z, y in tiers:
        b.fill(2, 3, z, 12, y - 1, z, "brick") if y > 3 else None
        for x in range(2, 13):
            b.stairs(x, y, z, "north")
    b.fill(2, 3, 2, 12, 5, 2, "brick")                 # back wall
    b.set(7, 2, 7, "chiseled", protect=True)
    b.waystone(7, 3, 7)
    b.suspicious(5, 2, 8)
    b.satellite_socket(0, 8, "west_up")
    b.satellite_socket(14, 8, "east_up")
    b.rubble(1, 2, 13, 10, 5)
    b.erode(0.09)


def processional_gate(b):
    """Babylonian: glazed-brick gate in the manner of Ishtar."""
    b.foundation(0, 0, 8, 4)
    b.fill(0, 2, 1, 8, 2, 3, "floor")
    # v1.16: towers and lintel raised two courses for a walk-through passage.
    for x0 in (0, 6):
        b.fill(x0, 3, 0, x0 + 2, 9, 4, "brick")
        b.fill(x0, 6, 0, x0 + 2, 6, 4, "glaze")        # glazed band
    b.fill(3, 8, 1, 5, 8, 3, "brick")                  # lintel
    b.fill(3, 9, 1, 5, 9, 3, "glaze")                  # glazed crown
    b.waystone(4, 3, 2)
    b.erode(0.07)


def terraced_garden(b):
    """Babylonian: two garden terraces, overgrown, waystone on the upper."""
    b.foundation(0, 0, 12, 12)
    b.fill(0, 2, 0, 12, 2, 12, "floor")
    b.fill(0, 3, 0, 12, 4, 6, "brick")                 # upper terrace mass
    for x in range(0, 13):                             # glazed facing, worn
        if b.rng.random() < 0.5:
            b.set(x, 4, 6, "glaze")
    for x in (5, 6, 7):                                # steps up, two rises
        b.stairs(x, 3, 7, "north")
        b.clear(x, 4, 6)
        b.stairs(x, 4, 6, "north")
    for _ in range(14):                                # overgrowth, both levels
        x = b.rng.randint(0, 12)
        upper = b.rng.random() < 0.5
        z = b.rng.randint(0, 5) if upper else b.rng.randint(8, 12)
        y = 5 if upper else 3
        if (x, y, z) in b.blocks:
            continue
        kind = b.rng.choice(("minecraft:moss_block",
                             "minecraft:azalea_leaves[persistent=true]",
                             "minecraft:flowering_azalea_leaves[persistent=true]"))
        b.set(x, y, z, kind)
    b.set(6, 4, 3, "chiseled", protect=True)
    b.waystone(6, 5, 3)
    b.suspicious(3, 2, 9)
    b.satellite_socket(6, 12, "south_up")
    b.erode(0.06)


def ziggurat(b):
    """Babylonian: stepped ziggurat, frontal ramp, glazed shrine at the summit."""
    b.foundation(0, 0, 14, 14)
    tiers = [(3, 1), (5, 3), (7, 5)]                   # (base y, inset), 2 high
    for y0, inset in tiers:
        b.fill(inset, y0, inset, 14 - inset, y0 + 1, 14 - inset, "brick")
        for x in range(inset, 15 - inset):             # glazed crown rows
            for z in (inset, 14 - inset):
                b.set(x, y0 + 1, z, "glaze")
                b.set(z, y0 + 1, x, "glaze")
    ramp = [(13, 3), (12, 4), (11, 5), (10, 6), (9, 7), (8, 8)]
    for z, y in ramp:
        for x in (6, 7, 8):
            b.clear(x, y, z)
            b.clear(x, y + 1, z)                       # walking headroom
            b.clear(x, y + 2, z)
            b.stairs(x, y, z, "north")
            for yy in range(2, y):
                b.set(x, yy, z, "brick")
    b.fill(6, 9, 6, 8, 11, 8, "glaze")                 # summit shrine
    b.air(7, 9, 7, 7, 11, 7)
    b.air(7, 9, 8, 7, 10, 8)                           # shrine door, south
    for x in range(6, 9):
        for z in range(6, 9):
            base = b.resolve("slab").split("[")[0]
            b.set(x, 12, z, f"{base}[type=bottom,waterlogged=false]")
    b.waystone(7, 9, 7)
    b.suspicious(5, 8, 5)
    b.satellite_socket(0, 7, "west_up")
    b.satellite_socket(14, 7, "east_up")
    b.erode(0.05, min_y=3)


def jungle_altar(b):
    """Mayan: small stepped altar swallowed by moss."""
    b.foundation(0, 0, 6, 6)
    b.fill(0, 2, 0, 6, 2, 6, "floor")
    for cx, cz in ((0, 0), (0, 6), (6, 0), (6, 6)):
        b.clear(cx, 2, cz)
    b.fill(1, 3, 1, 5, 3, 5, "brick")
    b.fill(2, 4, 2, 4, 4, 4, "brick")
    for x in (2, 3, 4):
        b.clear(x, 3, 5)
        b.stairs(x, 3, 5, "north")
    b.set(3, 4, 3, "chiseled", protect=True)
    b.waystone(3, 5, 3)
    for _ in range(6):
        x, z = b.rng.randint(0, 6), b.rng.randint(0, 6)
        if (x, 3, z) not in b.blocks and (x, 2, z) in b.blocks:
            b.set(x, 3, z, "minecraft:moss_carpet")
    b.erode(0.09)


def step_temple(b):
    """Mayan: steep step pyramid with an enclosed shrine room at the summit."""
    b.foundation(0, 0, 14, 14)
    for y, inset in ((3, 1), (4, 2), (5, 3), (6, 4), (7, 5)):
        b.fill(inset, y, inset, 14 - inset, y, 14 - inset, "brick")
    for y, z in ((3, 13), (4, 12), (5, 11), (6, 10), (7, 9)):   # south staircase
        for x in (6, 7, 8):
            b.clear(x, y, z)
            b.clear(x, y + 1, z)
            b.clear(x, y + 2, z)
            b.stairs(x, y, z, "north")
    b.hollow_box(5, 8, 5, 9, 10, 9, "brick")           # summit shrine
    b.air(6, 8, 6, 8, 10, 8)
    b.clear(7, 8, 9)                                   # doorway, south
    b.clear(7, 9, 9)
    b.fill(5, 11, 5, 9, 11, 9, "brick")                # roof
    b.fill(6, 12, 6, 8, 12, 8, "brick")                # corbel crown
    b.waystone(7, 8, 7)
    b.set(6, 8, 6, "minecraft:gold_block", protect=True)
    b.pot(8, 8, 6)
    b.suspicious(6, 7, 8)
    b.suspicious(3, 3, 4)
    b.satellite_socket(0, 7, "west_up")
    b.satellite_socket(14, 7, "east_up")
    for _ in range(12):                                # moss creep on terraces
        x, z = b.rng.randint(1, 13), b.rng.randint(1, 13)
        for y in (7, 6, 5, 4, 3):
            if (x, y, z) in b.blocks and (x, y + 1, z) not in b.blocks:
                b.set(x, y + 1, z, "minecraft:moss_carpet")
                break
    b.erode(0.06, min_y=3)


def overgrown_court(b):
    """Mayan: moss-choked ballcourt — two sloped mounds flanking the waystone."""
    b.foundation(0, 0, 14, 10)
    b.fill(0, 2, 0, 14, 2, 10, "floor")
    for z0, z1, sz, face in ((0, 1, 2, "north"), (9, 10, 8, "south")):
        b.fill(1, 3, z0, 13, 4, z1, "brick")           # mound cores
        for x in range(1, 14):
            b.stairs(x, 3, sz, face)                   # inward slopes
    b.set(3, 5, 0, "brick_wall")
    b.set(11, 5, 10, "brick_wall")
    b.set(7, 2, 5, "chiseled", protect=True)
    b.waystone(7, 3, 5)
    b.suspicious(4, 2, 5)
    b.suspicious(10, 2, 5)
    b.satellite_socket(0, 5, "west_up")
    b.satellite_socket(14, 5, "east_up")
    for _ in range(10):
        x, z = b.rng.randint(0, 14), b.rng.randint(3, 7)
        if (x, 3, z) not in b.blocks and (x, 2, z) in b.blocks:
            b.set(x, 3, z, b.rng.choice(("minecraft:moss_carpet", "minecraft:moss_block")))
    b.erode(0.10)


def runestones(b):
    """Viking: kerbed stone circle, carved runestones flanking the waystone."""
    b.foundation(1, 1, 7, 7)
    b.fill(2, 2, 2, 6, 2, 6, "floor")
    for x in range(1, 8):
        for z in range(1, 8):
            edge = x in (1, 7) or z in (1, 7)
            corner = (x in (1, 7)) and (z in (1, 7))
            if edge and not corner and b.rng.random() < 0.7:
                b.set(x, 3, z, "wall")                 # kerb stones
    for x, h in ((2, 3), (6, 2)):                      # carved runestones
        b.column(x, 3, 4, h, "brick", cap=None)
        b.set(x, 3 + h, 4, "chiseled")
    b.set(4, 2, 4, "chiseled", protect=True)
    b.waystone(4, 3, 4)
    b.set(4, 3, 6, "light")
    b.erode(0.08)


def stone_ship(b):
    """Viking: ship-shaped stone setting, grave goods buried amidships."""
    import math
    b.foundation(0, 0, 16, 6)
    for x in range(0, 17):
        w = round(3 * math.sin(math.pi * x / 16))
        if x in (0, 16):
            b.column(x, 2, 3, 4, "brick", cap="chiseled")   # bow and stern
            continue
        for z in (3 - w, 3 + w):
            if w == 0:
                continue
            b.set(x, 2, z, "cobble")
            b.column(x, 3, z, b.rng.choice((1, 1, 2)), "brick")
        for z in range(3 - w + 1, 3 + w):
            if b.rng.random() < 0.5:
                b.set(x, 2, z, "floor")
    b.set(8, 2, 3, "chiseled", protect=True)
    b.waystone(8, 3, 3)
    b.set(2, 2, 3, "cobble")
    b.suspicious(5, 2, 3)
    b.suspicious(11, 2, 3)
    b.satellite_socket(8, 0, "north_up")
    b.satellite_socket(8, 6, "south_up")
    b.erode(0.07)


def mead_hall(b):
    """Viking: ruined longhouse — log frame, half-collapsed roof, cold hearth."""
    b.foundation(0, 0, 16, 8)
    b.fill(1, 2, 1, 15, 2, 7, "floor")
    for z in (1, 7):                                   # log posts + plank walls
        for x in range(1, 16):
            if x % 3 == 1:
                b.column(x, 3, z, 3, "pillar", cap=None)
            else:
                b.fill(x, 3, z, x, 4, z, "plank")
    for gx in (1, 15):                                 # gable ends
        b.fill(gx, 3, 2, gx, 5, 6, "plank")
        b.fill(gx, 6, 3, gx, 6, 5, "plank")
        b.set(gx, 7, 4, "plank")
    # The longhouse needs an entrance even when all of its walls survive.
    b.fill(15, 3, 3, 15, 4, 5, "minecraft:air", protect=True)
    b.fill(14, 2, 3, 16, 2, 5, "floor", protect=True)
    for x in range(2, 10):                             # roof survives on west half
        for z, y, face in ((1, 5, "south"), (2, 6, "south"), (3, 7, "south"),
                           (7, 5, "north"), (6, 6, "north"), (5, 7, "north")):
            b.stairs(x, y, z, face)
        b.set(x, 7, 4, "plank")
    b.set(8, 3, 4, "minecraft:campfire[lit=true,facing=north,signal_fire=false,waterlogged=false]",
          protect=True)
    b.set(2, 2, 4, "chiseled", protect=True)
    b.waystone(2, 3, 4)
    b.pot(13, 3, 6)
    b.suspicious(12, 2, 3)
    b.satellite_socket(0, 4, "west_up")
    b.satellite_socket(16, 4, "east_up")
    b.rubble(9, 2, 15, 6, 7)
    b.erode(0.10)


# ------------------------------------------------ v1.5: native nether pieces

def soul_forge(b):
    """Nether: basalt-pillared forge hall, soul fires still burning."""
    b.hollow_box(0, 0, 0, 10, 7, 10, "brick")
    b.air(1, 1, 1, 9, 6, 9)
    b.fill(1, 0, 1, 9, 0, 9, "floor")
    for x, z in ((2, 2), (2, 8), (8, 2), (8, 8)):
        b.column(x, 1, z, 6, "pillar")
    b.fill(4, 1, 4, 6, 1, 6, "accent")                 # gilded ring
    b.set(5, 1, 5, "chiseled", protect=True)
    b.waystone(5, 2, 5)
    for x, z in ((3, 7), (7, 3)):
        b.set(x, 1, z, "minecraft:soul_campfire[lit=true,facing=north,signal_fire=false,waterlogged=false]",
              protect=True)
    b.pot(1, 1, 5)
    b.rubble(1, 1, 9, 9, 5, y=1)
    b.erode(0.05, min_y=0)
    b.breach(0, 1, 0, 10, 6, 10, count=3)


def bone_vault(b):
    """Nether: rib-vaulted ossuary — something vast was buried here."""
    b.hollow_box(0, 0, 0, 8, 6, 12, "brick")
    b.air(1, 1, 1, 7, 5, 11)
    b.fill(1, 0, 1, 7, 0, 11, "floor")
    for z in (3, 6, 9):                                # bone ribs
        b.fill(1, 1, z, 1, 3, z, "minecraft:bone_block[axis=y]")
        b.fill(7, 1, z, 7, 3, z, "minecraft:bone_block[axis=y]")
        b.fill(2, 4, z, 6, 4, z, "minecraft:bone_block[axis=x]")
    b.set(4, 1, 10, "chiseled", protect=True)
    b.waystone(4, 2, 10)
    b.pot(2, 1, 2)
    b.suspicious(6, 0, 3)
    b.rubble(1, 1, 7, 11, 4, y=1)
    b.erode(0.05, min_y=0)
    b.breach(0, 1, 0, 8, 5, 12, count=2)


def basalt_span(b):
    """Nether: vaulted hall broken by a chasm, a basalt span across it."""
    b.hollow_box(0, 3, 0, 8, 11, 14, "brick")
    b.air(1, 4, 1, 7, 10, 13)
    b.fill(1, 3, 1, 7, 3, 13, "floor")
    b.air(1, 0, 5, 7, 3, 9)                            # chasm cuts the floor
    b.fill(3, 3, 5, 5, 3, 9, "pillar")                 # basalt span
    b.set(4, 4, 12, "chiseled", protect=True)
    b.waystone(4, 5, 12)
    b.set(1, 4, 12, "light")
    b.set(7, 4, 12, "light")
    b.pot(6, 4, 2)
    b.rubble(1, 1, 7, 4, 3, y=4)
    b.erode(0.06, min_y=3)
    b.breach(0, 4, 0, 8, 10, 14, count=2)


# ------------------------------------------------ v1.5: satellite additions

def graves(b):
    """Satellite: a row of humble graves near the ruin."""
    b.foundation(0, 0, 6, 4)
    for x in (1, 3):
        b.set(x, 3, 1, "wall")                         # headstones
        b.fill(x, 2, 1, x, 2, 3, "minecraft:coarse_dirt")
    b.fill(5, 2, 1, 5, 2, 3, "minecraft:coarse_dirt")  # third: stone toppled
    base = b.resolve("cobble_slab").split("[")[0]
    b.set(5, 3, 2, f"{base}[type=bottom,waterlogged=false]")
    b.plug(0, 2, "west_up")
    b.erode(0.06)


def campsite(b):
    """Satellite: a cold camp — someone studied this ruin once."""
    b.foundation(0, 0, 4, 4)
    b.set(2, 2, 2, "cobble")
    b.set(2, 3, 2, "minecraft:campfire[lit=false,facing=north,signal_fire=false,waterlogged=false]",
          protect=True)
    base = b.resolve("cobble_slab").split("[")[0]
    b.set(0, 3, 2, f"{base}[type=bottom,waterlogged=false]")
    b.set(4, 3, 2, f"{base}[type=bottom,waterlogged=false]")
    for x, z in ((1, 1), (3, 3), (1, 3)):
        b.set(x, 2, z, "floor")
    b.plug(0, 2, "west_up")


def toppled_statue(b):
    """Satellite: a fallen figure — pedestal standing, statue in pieces."""
    b.foundation(0, 0, 6, 2)
    b.fill(1, 2, 1, 1, 3, 1, "brick")                  # pedestal
    b.set(3, 3, 1, "chiseled")                         # the head
    b.set(4, 3, 1, "brick")
    b.set(6, 3, 1, "brick")
    b.plug(0, 1, "west_up")
    b.erode(0.08)


SMALL = {
    "dais": dais, "broken_ring": broken_ring, "arch": arch, "gazebo": gazebo,
    "collapsed_shrine": collapsed_shrine, "obelisks": obelisks, "cairn": cairn,
    "well_shrine": well_shrine, "watch_stub": watch_stub,
}
SMALL_WITH_BARROW = dict(SMALL, barrow=barrow)         # default + frozen themes
GRAND = {
    "colonnade_temple": colonnade_temple, "step_pyramid": step_pyramid,
    "courtyard_sanctum": courtyard_sanctum, "great_hall": great_hall,
}
UNDER = {
    "crypt_cell": crypt_cell, "pillared_vault": pillared_vault,
    "stair_sanctum": stair_sanctum, "grand_crypt": grand_crypt,
}
SATELLITES = {
    "pillar_fall": pillar_fall, "path_frag": path_frag, "gate_stub": gate_stub,
    "graves": graves, "campsite": campsite, "toppled_statue": toppled_statue,
}
NETHER = {   # re-skinned vaults + native pieces
    "nether_crypt": crypt_cell, "nether_vault": pillared_vault,
    "nether_hall": stair_sanctum,
    "soul_forge": soul_forge, "bone_vault": bone_vault, "basalt_span": basalt_span,
}
END = {      # surface geometries re-skinned in end stone/purpur with end rods
    "end_ring": broken_ring, "end_gazebo": gazebo, "end_obelisks": obelisks,
}
DROWNED = {"drowned_shrine": drowned_shrine}
EGYPT_SMALL = {"pylon_gate": pylon_gate, "obelisk_avenue": obelisk_avenue}
EGYPT_GRAND = {"mastaba": mastaba}
GREEK_SMALL = {"stoa": stoa}
GREEK_GRAND = {"tholos": tholos, "amphitheater": amphitheater}
BABYLON_SMALL = {"processional_gate": processional_gate}
BABYLON_GRAND = {"terraced_garden": terraced_garden, "ziggurat": ziggurat}
VIKING_SMALL = {"runestones": runestones}
VIKING_GRAND = {"stone_ship": stone_ship, "mead_hall": mead_hall}
MAYAN_SMALL = {"jungle_altar": jungle_altar}
MAYAN_GRAND = {"step_temple": step_temple, "overgrown_court": overgrown_court}
CHERRY_GRAND = {"tholos": tholos}
SUNKEN = {
    "sunken_ring": broken_ring, "sunken_arch": arch, "sunken_obelisks": obelisks,
    "sunken_watch": watch_stub, "sunken_gazebo": gazebo,
}
