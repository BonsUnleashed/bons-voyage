"""Master-builder helpers (v1.8): realism techniques from the 2026-09-02
research pass, layered on top of core.Build. Every helper takes the Build
instance `b` first; none mutate protected positions.

Key techniques encoded:
- weighted palette mixes with VERTICAL gradient (wet/mossy feet, clean tops)
- facade depth: pilasters, quoins, string courses, cornices (half=top stairs)
- baked stair shapes at roof corners (structure NBT gets no neighbor updates)
- authentic ruin passes: crack seams from opening corners, collapse wedges
  with mass-balanced rubble, column stumps + fallen drums
- hidden lighting via minecraft:light[level=n]
"""


def wset(b, x, y, z, pairs):
    """Set from an explicit weighted list [(state, w), ...]."""
    states = [s for s, _ in pairs]
    weights = [w for _, w in pairs]
    b.set(x, y, z, b.rng.choices(states, weights=weights, k=1)[0])


def grad_wall(b, x0, y0, z0, x1, y1, z1, clean, weathered, wet, ground_y=2):
    """Fill a wall volume with a height-graded mix: `wet` dominates in the
    two courses above ground, fades out by ground+4; `weathered` is constant
    low-rate noise; `clean` is the body. Noise clustered 2x1 so patches read
    as single weathered stones, not static."""
    import zlib
    salt = zlib.crc32(b.name.encode())
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                h = y - ground_y
                wet_w = max(0.0, 0.40 - 0.13 * h)
                # cluster noise on (x//2, y, z//2) so variants come in patches;
                # deterministic (crc32) so builds are reproducible
                key = f"{x // 2},{y},{z // 2}".encode()
                seed_roll = (zlib.crc32(key, salt) % 1000) / 1000.0
                if seed_roll < wet_w:
                    b.set(x, y, z, wet)
                elif seed_roll < wet_w + 0.22:
                    b.set(x, y, z, weathered)
                else:
                    b.set(x, y, z, clean)


def string_course(b, x0, z0, x1, z1, y, state):
    """Contrasting horizontal band (chiseled course) around a rectangle."""
    for x in range(min(x0, x1), max(x0, x1) + 1):
        b.set(x, y, min(z0, z1), state)
        b.set(x, y, max(z0, z1), state)
    for z in range(min(z0, z1), max(z0, z1) + 1):
        b.set(min(x0, x1), y, z, state)
        b.set(max(x0, x1), y, z, state)


def cornice(b, x0, z0, x1, z1, y, stairs_role="stairs"):
    """Upside-down stair cornice overhanging +1 around a rectangle top."""
    base = b.resolve(stairs_role).split("[")[0]
    xa, xb = min(x0, x1), max(x0, x1)
    za, zb = min(z0, z1), max(z0, z1)
    for x in range(xa, xb + 1):
        b.set(x, y, za - 1, f"{base}[facing=south,half=top,shape=straight,waterlogged=false]")
        b.set(x, y, zb + 1, f"{base}[facing=north,half=top,shape=straight,waterlogged=false]")
    for z in range(za, zb + 1):
        b.set(xa - 1, y, z, f"{base}[facing=east,half=top,shape=straight,waterlogged=false]")
        b.set(xb + 1, y, z, f"{base}[facing=west,half=top,shape=straight,waterlogged=false]")
    # baked outer corners
    b.set(xa - 1, y, za - 1, f"{base}[facing=south,half=top,shape=outer_right,waterlogged=false]")
    b.set(xb + 1, y, za - 1, f"{base}[facing=south,half=top,shape=outer_left,waterlogged=false]")
    b.set(xa - 1, y, zb + 1, f"{base}[facing=north,half=top,shape=outer_left,waterlogged=false]")
    b.set(xb + 1, y, zb + 1, f"{base}[facing=north,half=top,shape=outer_right,waterlogged=false]")


def pilasters(b, x0, z, x1, y0, y1, period=4, depth_dz=-1, role="accent"):
    """Protruding vertical strips along a wall run parallel to X at depth z;
    strips sit at z+depth_dz (i.e. +1 out of the wall face)."""
    for x in range(min(x0, x1), max(x0, x1) + 1):
        if (x - min(x0, x1)) % period == 0:
            for y in range(y0, y1 + 1):
                b.set(x, y, z + depth_dz, role)


def corbel_arch(b, x, y0, z, height, axis="x", role="brick", stairs_role="stairs"):
    """Cut a corbel-arched opening (2 wide) through a wall at (x..x+1, z):
    straight jambs, two step-in rows of half=top stairs, slab cap. Returns
    nothing; caller is responsible for the wall mass around it."""
    base = b.resolve(stairs_role).split("[")[0]
    if axis == "x":
        cells = [(x, z), (x + 1, z)]
        f1, f2 = "east", "west"
    else:
        cells = [(x, z), (x, z + 1)]
        f1, f2 = "south", "north"
    for cx, cz in cells:
        for y in range(y0, y0 + height):
            b.set(cx, y, cz, "minecraft:air", protect=True)
    ytop = y0 + height
    (ax, az), (bx, bz) = cells
    b.set(ax, ytop, az, f"{base}[facing={f1},half=top,shape=straight,waterlogged=false]")
    b.set(bx, ytop, bz, f"{base}[facing={f2},half=top,shape=straight,waterlogged=false]")
    slab = b.resolve("slab").split("[")[0]
    b.set(ax, ytop + 1, az, f"{slab}[type=top,waterlogged=false]")
    b.set(bx, ytop + 1, bz, f"{slab}[type=top,waterlogged=false]")


def battered_wall(b, x0, z0, x1, z1, y0, height, inset_every=3, role="brick",
                  stairs_role="stairs"):
    """Egyptian battered (sloping) mass: rectangle that steps in 1 on all
    sides every `inset_every` rows, exterior slope faced with bottom stairs."""
    base = b.resolve(stairs_role).split("[")[0]
    inset = 0
    for i in range(height):
        y = y0 + i
        xa, xb = min(x0, x1) + inset, max(x0, x1) - inset
        za, zb = min(z0, z1) + inset, max(z0, z1) - inset
        if xa > xb or za > zb:
            break
        b.fill(xa, y, za, xb, y, zb, role)
        if (i + 1) % inset_every == 0 and xa + 1 < xb and za + 1 < zb:
            # face the setback row with outward stairs on the NEXT row's rim
            for x in range(xa + 1, xb):
                b.set(x, y + 1, za, f"{base}[facing=south,half=bottom,shape=straight,waterlogged=false]")
                b.set(x, y + 1, zb, f"{base}[facing=north,half=bottom,shape=straight,waterlogged=false]")
            for z in range(za + 1, zb):
                b.set(xa, y + 1, z, f"{base}[facing=east,half=bottom,shape=straight,waterlogged=false]")
                b.set(xb, y + 1, z, f"{base}[facing=west,half=bottom,shape=straight,waterlogged=false]")
            inset += 1


def column_stump(b, x, y0, z, full_h, pillar_role="pillar", cap_role="chiseled"):
    """A column that may be whole, broken mid-height, or a base drum — with
    fallen drums laid along a random direction (mass balance)."""
    roll = b.rng.random()
    slab = b.resolve("slab").split("[")[0]
    if roll < 0.30:                                     # survives whole
        b.column(x, y0, z, full_h, pillar_role, cap=cap_role)
        return
    if roll < 0.70:                                     # broken at 1/3..2/3
        h = max(1, int(full_h * b.rng.uniform(0.33, 0.66)))
        b.column(x, y0, z, h, pillar_role)
        b.set(x, y0 + h, z, f"{slab}[type=bottom,waterlogged=false]")
    else:                                               # base drum only
        b.set(x, y0, z, pillar_role)
    # fallen drums: 2-4 segments with a break gap
    dx, dz = b.rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
    ax = "x" if dx else "z"
    p = b.resolve(pillar_role).split("[")[0]
    n = b.rng.randint(2, 4)
    step = 1
    for i in range(1, n + 1):
        px, pz = x + dx * (i + step), z + dz * (i + step)
        if i == n // 2 + 1:
            step += 1                                   # the break gap
        if (px, y0, pz) not in b.blocks:
            b.set(px, y0, pz, f"{p}[axis={ax}]")


def crack_seams(b, x0, z0, x1, z1, y0, y1, count=2, cracked_role=None):
    """Random-walk vertical-ish crack seams: convert blocks along the walk to
    weathered masonry. Missing courses must be authored with their collapse;
    a cosmetic crack must never punch out a roof or column's bearing."""
    for _ in range(count):
        x = b.rng.randint(min(x0, x1), max(x0, x1))
        z = b.rng.randint(min(z0, z1), max(z0, z1))
        for y in range(y0, y1 + 1):
            pos = (x, y, z)
            if pos in b.blocks and pos not in b.protected \
                    and b.blocks[pos][0] != "minecraft:air":
                from archaeology import full_cube
                if full_cube(b.blocks[pos][0]):
                    b.set(x, y, z, cracked_role or "cobble")
            if b.rng.random() < 0.5:
                x += b.rng.choice((-1, 0, 1))
            else:
                z += b.rng.choice((-1, 0, 1))


def collapse_wedge(b, x, ytop, z, depth, direction, rubble_rect):
    """A breach widens toward the crown, with no surviving fabric over its cut.

    Remove only exposed unprotected courses. A protected bearing or roof above
    prevents the cut below it. Rubble uses the actual surface ground level.
    """
    removed = 0
    dx, dz = (1, 0) if direction in ("east", "west") else (0, 1)
    for i in range(depth):
        y = ytop - i
        half = depth - i - 1
        for k in range(-half, half + 1):
            pos = (x + dx * k, y, z + dz * k)
            ground = b.ground_y if b.ground_y is not None else 2
            above = b.blocks.get((pos[0], y+1, pos[2]), ("minecraft:air", None))[0]
            if y > ground and pos in b.blocks and pos not in b.protected \
                    and b.blocks[pos][0] != "minecraft:air" and above == "minecraft:air":
                del b.blocks[pos]
                removed += 1
    if removed:
        b.rubble(*rubble_rect, count=max(2, int(removed * 0.4)), y=ground+1)


def vine_creep(b, prob_low=0.30, prob_high=0.08, cutoff=5):
    """Face-flagged vines on exterior solid faces; probability falls with
    height. Only attaches to faces where the neighbor cell is empty."""
    from archaeology import full_cube
    adds = {}
    for (x, y, z), (state, _) in list(b.blocks.items()):
        if state == "minecraft:air" or "waystones:" in state:
            continue
        if not full_cube(state) or y <= (b.ground_y if b.ground_y is not None else 1):
            continue
        p = prob_low if y < cutoff else prob_high
        for dx, dz, face in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
            npos = (x + dx, y, z + dz)
            if npos in b.blocks or npos in adds:
                continue
            if b.rng.random() < p:
                props = ",".join(f"{f}={'true' if f == face else 'false'}"
                                 for f in ("east", "north", "south", "up", "west"))
                adds[npos] = (f"minecraft:vine[{props}]", None)
    b.blocks.update({k: v for k, v in adds.items() if k not in b.blocks})


def hidden_light(b, x, y, z, level=12):
    """Invisible light block — the structure-NBT-native way to light ruins."""
    b.set(x, y, z, f"minecraft:light[level={level},waterlogged=false]", protect=True)


def merlons(b, x0, z0, x1, z1, y, role="brick", slab_role="slab", period=3):
    """Stepped Mesopotamian merlons around a parapet rectangle: 2-wide,
    block+slab shoulders, 1 gap."""
    slab = b.resolve(slab_role).split("[")[0]
    def run(points):
        for i, (x, z) in enumerate(points):
            m = i % period
            if m == 0:
                b.set(x, y, z, role)
                b.set(x, y + 1, z, f"{slab}[type=bottom,waterlogged=false]")
            elif m == 1:
                b.set(x, y, z, role)
    xa, xb = min(x0, x1), max(x0, x1)
    za, zb = min(z0, z1), max(z0, z1)
    run([(x, za) for x in range(xa, xb + 1)])
    run([(x, zb) for x in range(xa, xb + 1)])
    run([(xa, z) for z in range(za + 1, zb)])
    run([(xb, z) for z in range(za + 1, zb)])


def glazed_frieze(b, x0, z, x1, y0, y1, field="glaze",
                  rosette="minecraft:gold_block", rosette_every=3):
    """Babylonian glazed band along X at depth z: blue field with gold
    rosettes every few blocks on the middle row."""
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in range(y0, y1 + 1):
            mid = (y0 + y1) // 2
            if y == mid and (x - min(x0, x1)) % rosette_every == 0:
                b.set(x, y, z, rosette)
            else:
                b.set(x, y, z, field)


def gable_roof(b, x0, z0, x1, z1, y0, axis="x", stairs_role="stairs",
               ridge_slab=True, overhang=1, sway=0):
    """Stair gable roof over a rectangle. axis = ridge direction. sway=1
    dips the middle third of the ridge by one block (Viking longhouse).
    Overhang extends the roof beyond the walls."""
    base = b.resolve(stairs_role).split("[")[0]
    slab = b.resolve("slab").split("[")[0]
    xa, xb = min(x0, x1) - (overhang if axis == "z" else 0), max(x0, x1) + (overhang if axis == "z" else 0)
    za, zb = min(z0, z1) - (overhang if axis == "x" else 0), max(z0, z1) + (overhang if axis == "x" else 0)
    if axis == "x":
        length = range(xa - overhang, xb + overhang + 1)
        width_a, width_b = za, zb
    else:
        length = range(za - overhang, zb + overhang + 1)
        width_a, width_b = xa, xb
    span = width_b - width_a
    rises = (span + 1) // 2
    for li in length:
        # sway: middle third of the run drops 1
        lo = min(length)
        hi = max(length)
        t = (li - lo) / max(1, hi - lo)
        drop = 1 if (sway and 0.33 < t < 0.67) else 0
        for i in range(rises + 1):
            y = y0 + i - drop
            wa, wb = width_a + i, width_b - i
            if wa > wb:
                break
            if wa == wb and ridge_slab:
                p = (li, y, wa) if axis == "x" else (wa, y, li)
                b.set(*p, f"{slab}[type=bottom,waterlogged=false]")
                continue
            f1, f2 = ("south", "north") if axis == "x" else ("east", "west")
            p1 = (li, y, wa) if axis == "x" else (wa, y, li)
            p2 = (li, y, wb) if axis == "x" else (wb, y, li)
            b.set(*p1, f"{base}[facing={f1},half=bottom,shape=straight,waterlogged=false]")
            b.set(*p2, f"{base}[facing={f2},half=bottom,shape=straight,waterlogged=false]")


def gable_ends(b, ends, x0, z0, x1, z1, y0, wall_top, axis="x", overhang=1,
               role="plank"):
    """Close the triangular gable above each end wall of a gable_roof run.

    Pass the same rectangle, y0 and overhang as the gable_roof call; `ends`
    are the x lines (axis x) or z lines (axis z) of the end walls and
    `wall_top` the highest wall course. Fills up to the underside of the roof
    and never overwrites an existing block, so call it after the roof. A roof
    whose eave course sits at wall_top rests on the wall at the wall line;
    without this fill the ends stayed open triangles (v1.16)."""
    if axis == "x":
        wa, wb = min(z0, z1) - overhang, max(z0, z1) + overhang
    else:
        wa, wb = min(x0, x1) - overhang, max(x0, x1) + overhang
    for end in ends:
        for w in range(wa, wb + 1):
            roof_y = y0 + min(w - wa, wb - w)
            for y in range(wall_top + 1, roof_y):
                pos = (end, y, w) if axis == "x" else (w, y, end)
                if pos not in b.blocks:
                    b.set(*pos, role)
            # The roof course on the end line is what the overhang beyond it
            # hangs from; keep erosion from orphaning those eave stairs.
            roof = (end, roof_y, w) if axis == "x" else (w, roof_y, end)
            if roof in b.blocks:
                b.protected.add(roof)


# ---------------------------------------------------------------- v1.8 batch 2

CRYPT_CHEST_LOOT = "waystone_ruins:chests/crypt"


def room(b, x0, y0, z0, x1, y1, z1, shell="brick", floor="floor"):
    """Enclosed underground room: shell box, air interior, dressed floor."""
    if x1 - x0 < 2 or z1 - z0 < 2 or y1 - y0 < 3:
        raise ValueError(f"{b.name}: room needs a two-block-high walkable interior")
    if not hasattr(b, "rooms"):
        b.rooms = []
    b.rooms.append((x0, y0, z0, x1, y1, z1))
    b.hollow_box(x0, y0, z0, x1, y1, z1, shell)
    b.air(x0 + 1, y0 + 1, z0 + 1, x1 - 1, y1 - 1, z1 - 1)
    b.fill(x0 + 1, y0, z0 + 1, x1 - 1, y0, z1 - 1, floor)


def loot_chest(b, x, y, z, facing="north", table=CRYPT_CHEST_LOOT):
    """Chest wired to a loot table (defined in the release build): the crypt
    table by default; a chest behind a secret passes loot.HIDDEN_TREASURY and
    a great dungeon's deepest vault loot.HOARD (v1.17)."""
    b.set(x, y, z, f"minecraft:chest[facing={facing},type=single,waterlogged=false]",
          be={"id": "minecraft:chest", "LootTable": table}, protect=True)
    b.protected.add((x, y - 1, z))


def ladder_shaft(b, x, z, y0, y1, facing="north", lining="cobble"):
    """Climbable shaft with ladders on the wall behind (facing = ladder face)."""
    dx, dz = {"north": (0, 1), "south": (0, -1), "east": (-1, 0), "west": (1, 0)}[facing]
    for y in range(y0, y1 + 1):
        b.set(x, y, z, f"minecraft:ladder[facing={facing},waterlogged=false]", protect=True)
        b.set(x + dx, y, z + dz, lining, protect=True)
    b.set(x, y1 + 1, z, "minecraft:air", protect=True)
    b.set(x, y1 + 2, z, "minecraft:air", protect=True)


def passage(b, x0, y, z0, x1, z1, height=2, lining="cobble"):
    """A level, supported corridor, including both room-wall crossings.

    Keep the floor and headroom intact through weathering; only dress missing
    side/ceiling cells, so a corridor ending in a room cannot seal that room.
    """
    if (x0 != x1 and z0 != z1) or height < 2:
        raise ValueError("passage must be straight with at least two blocks of headroom")
    along_x = x0 != x1
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for z in range(min(z0, z1), max(z0, z1) + 1):
            b.set(x, y - 1, z, "floor", protect=True)
            b.fill(x, y, z, x, y + height - 1, z, "minecraft:air", protect=True)
            for dy in range(height):
                for side in (-1, 1):
                    p = (x, y + dy, z + side) if along_x else (x + side, y + dy, z)
                    if p not in b.blocks:
                        b.set(*p, lining)
            if (x, y + height, z) not in b.blocks:
                b.set(x, y + height, z, lining)


def secret_hatch(b, x, z, bottom_y, floor_y, facing="north", lining="cobble"):
    """A brushable capstone above one continuous ladder, usable both ways."""
    ladder_shaft(b, x, z, bottom_y, floor_y - 1, facing=facing, lining=lining)
    false_floor(b, x, floor_y, z)
    b.fill(x, floor_y + 1, z, x, floor_y + 2, z, "minecraft:air", protect=True)


def weak_wall(b, x0, y0, z0, x1, y1, z1, cracked="minecraft:cracked_stone_bricks"):
    """A conspicuous patch of cracked masonry hiding a passage: the classic
    break-through wall. Distinct texture is the tell."""
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                b.set(x, y, z, cracked)
                if not hasattr(b, "secret_blocks"):
                    b.secret_blocks = set()
                b.secret_blocks.add((x, y, z))
                b.protected.add((x, y, z))


def false_floor(b, x, y, z):
    """One suspicious block set into a floor - dig it to drop into what is
    below. Pair with a shaft or chamber underneath."""
    b.suspicious(x, y, z)
    if not hasattr(b, "secret_blocks"):
        b.secret_blocks = set()
    b.secret_blocks.add((x, y, z))


def sarcophagus(b, x, y, z, axis="x", lid="chiseled"):
    """A 3-long stone sarcophagus with a slab lid; head block distinct."""
    dx, dz = (1, 0) if axis == "x" else (0, 1)
    for i in range(3):
        b.set(x + dx * i, y, z + dz * i, "accent" if i else lid)
    slab = b.resolve("slab").split("[")[0]
    for i in range(3):
        b.set(x + dx * i, y + 1, z + dz * i, f"{slab}[type=bottom,waterlogged=false]")


def slab_roof(b, x0, z0, x1, z1, y, overhang=1):
    """Flat slab roof with a one-block overhang lip."""
    slab = b.resolve("slab").split("[")[0]
    for x in range(min(x0, x1) - overhang, max(x0, x1) + overhang + 1):
        for z in range(min(z0, z1) - overhang, max(z0, z1) + overhang + 1):
            b.set(x, y, z, f"{slab}[type=bottom,waterlogged=false]")
