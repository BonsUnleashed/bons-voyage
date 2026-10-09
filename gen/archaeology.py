"""Authored collapse, supported masonry and climate-aware reclamation.

Build the surviving courses, rather than perforating a complete building.
Missing fabric is expressed by foundation traces, fallen drums and open sky.
These are build-time helpers; there is no runtime growth or physics code.
"""
from collections import deque
import random

from core import FULL_SOLID_HINTS, parse_state

AIR = "minecraft:air"
GREEN_THEMES = {"default", "greek", "cherry", "mossy", "mayan"}
DRY_THEMES = {"sandy", "egyptian", "red", "babylon"}


def full_cube(state):
    name, _ = parse_state(state)
    if any(part in name for part in ("stairs", "_slab", "_wall", "waystones:",
                                     "lantern", "pot", "chest", "suspicious")):
        return False
    return any(hint in name for hint in FULL_SOLID_HINTS)


def state_at(b, pos):
    return b.blocks.get(pos, (AIR, None))[0]


def standing_column(b, x, z, ground, height, complete=False):
    """Drums rise consecutively from a footing; only whole columns get capitals."""
    b.set(x, ground, z, "accent", protect=True)
    for y in range(ground + 1, ground + height + 1):
        b.set(x, y, z, "pillar")
    if complete:
        b.set(x, ground + height + 1, z, "chiseled")


def wall_remnant(b, points, ground):
    """(x, z, height) profile: a battered wall with no holes beneath its crown."""
    for x, z, height in points:
        b.set(x, ground, z, "cobble")
        for dy in range(1, height + 1):
            b.set(x, ground + dy, z, "brick" if dy > 1 else "cobble")


def supported_lintel(b, start, end, y, ground):
    """A short stone beam seated directly on two complete, protected supports."""
    x0, z0 = start
    x1, z1 = end
    if (x0 != x1 and z0 != z1) or not 1 <= abs(x1-x0)+abs(z1-z0) <= 4:
        raise ValueError("stone lintels need two aligned supports at most four blocks apart")
    for x, z in (start, end):
        for yy in range(ground, y):
            if not full_cube(state_at(b, (x, yy, z))):
                raise ValueError(f"{b.name}: lintel has an incomplete support at {(x, yy, z)}")
            b.protected.add((x, yy, z))
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for z in range(min(z0, z1), max(z0, z1) + 1):
            b.set(x, y, z, "brick", protect=True)
    if not hasattr(b, "masonry_spans"):
        b.masonry_spans = []
    b.masonry_spans.append((start, end, y, ground))


def fallen_column(b, x, z, ground, length, direction=(1, 0)):
    """Horizontal drums, one fracture and a detached capital on the soil."""
    dx, dz = direction
    if abs(dx) + abs(dz) != 1:
        raise ValueError("fallen column direction must be cardinal")
    pillar, props = parse_state(b.resolve("pillar"))
    shaft = f"{pillar}[axis={'x' if dx else 'z'}]" if props and 'axis' in props else pillar
    for i in range(length + 1):
        px, pz = x + dx*i, z + dz*i
        pos = (px, ground + 1, pz)
        if state_at(b, pos) != AIR or pos in b.protected:
            continue
        if i == length // 2:
            # A half drum in the break instead of a mathematically straight log.
            block = b.resolve("cobble_slab").split("[")[0] + "[type=bottom,waterlogged=false]"
        else:
            block = "chiseled" if i == length else shaft
        if state_at(b, (px, ground, pz)) == AIR:
            b.set(px, ground, pz, "cobble")
        b.set(*pos, block)


def quiet_waystone(b, x, z, ground, facing="north"):
    """A flush socket and a generous clear space, with no enclosing altar."""
    b.fill(x-1, ground, z-1, x+1, ground, z+1, "floor", protect=True)
    b.set(x, ground, z, "chiseled", protect=True)
    b.fill(x-1, ground+1, z-1, x+1, ground+5, z+1, AIR, protect=True)
    b.waystone(x, ground+1, z, facing=facing)
    b.focal_space = (x, ground, z)


def fragment_floor(b, x0, z0, x1, z1, ground=2):
    """An irregular floor edge; unplaced corners retain the local terrain."""
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            edge = min(x-x0, x1-x, z-z0, z1-z)
            # Large scallops in the outer course, never random interior holes.
            if edge == 0 and ((x//3 + z//2) % 3 != 0):
                continue
            b.set(x, ground, z, "floor")
            if ground == 2:
                b.fill(x, 0, z, x, 1, z, "cobble")


def reclaim(b, ground):
    """Soil tongues and low growth follow exposed masonry, leaving routes clear.

    Only surface flooring is exchanged; basement roofs, supports, archaeology,
    steps and protected focal spaces are untouched. Plants are seated on full
    cubes and vines have actual attachment faces. Arid schools get sediment.
    """
    if b.pristine or b.theme_name not in GREEN_THEMES | DRY_THEMES:
        return
    rng = random.Random(f"reclaim:{b.name}:{b.theme_name}:{getattr(b, 'seed', 0)}")
    tops = {}
    for (x, y, z), (state, _) in b.blocks.items():
        if full_cube(state) or '_stairs' in state or '_slab' in state:
            tops[(x, z)] = max(y, tops.get((x, z), y))
    eligible = []
    floor_names = {parse_state(s)[0] for s, _ in b.theme['floor']} if isinstance(b.theme['floor'], list) else {parse_state(b.theme['floor'])[0]}
    for (x, y, z), (state, be) in sorted(b.blocks.items()):
        if y != ground or be or (x, y, z) in b.protected or not full_cube(state):
            continue
        if parse_state(state)[0] not in floor_names:
            continue
        if state_at(b, (x, y+1, z)) != AIR or (x, y+1, z) in b.protected:
            continue
        if tops.get((x, z)) != ground:
            continue  # no vegetation in a roofed room or under an earthen mound
        eligible.append((x, z))
    if not eligible:
        return
    footprint = {(x, z) for (x, y, z), (s, _) in b.blocks.items() if y == ground and s != AIR}
    edges = [(x, z) for x, z in eligible if any((x+dx, z+dz) not in footprint
             for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    # Soil also accumulates beside fallen architecture inside an open courtyard.
    authored = getattr(b, 'archaeological', False)
    center_count = max(3, len(eligible)//40) if authored else max(2, len(eligible)//65)
    centers = rng.sample(edges or eligible, min(len(edges or eligible), center_count))
    if authored:
        sheltered = [(x, z) for x, z in eligible if any(
            full_cube(state_at(b, (x+dx, ground+1, z+dz)))
            for dx, dz in ((1,0),(-1,0),(0,1),(0,-1)))]
        centers += rng.sample(sheltered or eligible, min(len(sheltered or eligible), max(1, len(eligible)//100)))
    green = b.theme_name in GREEN_THEMES
    wet = b.theme_name in {"mossy", "mayan"}
    for x, z in eligible:
        distance = min(abs(x-cx)+abs(z-cz) for cx, cz in centers)
        radius = 5 if authored else 4 if wet else 3
        if distance > radius or rng.random() > 0.96 - distance*(0.12 if authored else 0.17):
            continue
        if green:
            soil = rng.choices(["minecraft:moss_block", "minecraft:grass_block[snowy=false]", "minecraft:coarse_dirt"], [5 if wet else 3, 4, 2])[0]
        else:
            # Full sediment blocks stay supported; no falling sand above cellars.
            soil = "minecraft:packed_mud" if b.theme_name == "babylon" else "minecraft:red_sand" if b.theme_name == "red" else "minecraft:sand"
            if not full_cube(state_at(b, (x, ground-1, z))):
                continue
        b.set(x, ground, z, soil)
        if green and rng.random() < (0.55 if wet else 0.38):
            plant = rng.choice(["minecraft:fern", "minecraft:grass", "minecraft:moss_carpet"])
            b.set(x, ground+1, z, plant)
    if not green:
        return
    # Moss spreads over sheltered stone feet as low mats, not a uniform green coat.
    for (x, y, z), (state, be) in sorted(list(b.blocks.items())):
        if not ground <= y <= ground+2 or be or not full_cube(state) or (x, y, z) in b.protected:
            continue
        if tops.get((x, z)) != y:
            continue
        if min(abs(x-cx)+abs(z-cz) for cx, cz in centers) > 4:
            continue
        above = (x, y+1, z)
        if above not in b.protected and state_at(b, above) == AIR and rng.random() < 0.36:
            b.set(*above, "minecraft:moss_carpet")
    creep(b, ground=ground, centers=centers, rng=rng, probability=0.55 if wet else 0.33)


def creep(b, ground, centers=None, rng=None, probability=0.30):
    """Short connected trails on the shaded side of real full-block faces."""
    rng = rng or b.rng
    tops = {}
    for (x, y, z), (s, _) in b.blocks.items():
        if full_cube(s) or '_slab' in s or '_stairs' in s:
            tops[(x, z)] = max(y, tops.get((x, z), y))
    for (x, y, z), (state, be) in sorted(list(b.blocks.items())):
        if not ground+1 <= y <= ground+4 or be or not full_cube(state):
            continue
        if centers and min(abs(x-cx)+abs(z-cz) for cx, cz in centers) > 5:
            continue
        for dx, dz, face in ((0, -1, 'south'), (-1, 0, 'east')):
            pos = (x+dx, y, z+dz)
            if tops.get((x+dx, z+dz), ground) > y:
                continue  # keep room air and covered passages clear of new vines
            if pos in b.protected or state_at(b, pos) != AIR or rng.random() > probability:
                continue
            b.set(*pos, 'minecraft:vine[' + ','.join(f'{f}={str(f == face).lower()}' for f in ('east', 'north', 'south', 'up', 'west')) + ']')


def validate_archaeology(b, ground):
    """Catch disconnected masonry and lost lintel bearings in authored ruins.

    Connectivity is a voxel sanity check, not an engineering simulation.
    Explicit lintel bearings additionally enforce short, grounded stone spans.
    """
    if not getattr(b, 'archaeological', False):
        return
    solids = {p for p, (s, be) in b.blocks.items() if p[1] >= ground and not be
              and (full_cube(s) or '_slab' in s or '_stairs' in s)}
    connected = {p for p in solids if p[1] == ground}
    queue = deque(connected)
    while queue:
        x, y, z = queue.popleft()
        for dx, dy, dz in ((1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)):
            p = (x+dx, y+dy, z+dz)
            if p in solids and p not in connected:
                connected.add(p)
                queue.append(p)
    if solids - connected:
        raise ValueError(f'{b.name}: disconnected masonry {sorted(solids-connected)[:6]}')
    for start, end, y, floor in getattr(b, 'masonry_spans', []):
        for x, z in (start, end):
            for yy in range(floor, y+1):
                if not full_cube(state_at(b, (x, yy, z))):
                    raise ValueError(f'{b.name}: lost lintel bearing at {(x, yy, z)}')
    if hasattr(b, 'focal_space'):
        x, g, z = b.focal_space
        for xx in range(x-1, x+2):
            for zz in range(z-1, z+2):
                for y in range(g+1, g+6):
                    s = state_at(b, (xx, y, zz))
                    if s != AIR and not s.startswith('waystones:'):
                        raise ValueError(f'{b.name}: crowded waystone at {(xx,y,zz)}')
