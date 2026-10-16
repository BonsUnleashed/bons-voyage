"""Bons Voyage 1.20.0 (Justin, 2026-10-16, answering a CurseForge comment): the waystone chest and the protected stone.

place(b, kind, theme, ground) authors one chest near the ruin's waystone. The runtime gate (java .../chests/
WaystoneChestProcessor, first in every waystone template's processor list) returns the cell exactly as it was before
1.20.0 while config waystone_chests.enabled is off (the default): air, or the decor block recorded in the chest's
WasBlock tag, or nothing at all for a cell the template never held (WasVoid: the processor drops it, as an absent
voxel is dropped). Switched on, the chest keeps its facing and draws one of the realm's configured loot tables.

The cell: the stone's right side, left side and back (ring 0), the four diagonals (ring 1) or the ring two blocks
out (ring 2), on the stone's level or up to four blocks lower (beside a plinth or pillar, with open air up to the
stone's level); the lowest ring + drop wins. It must:
  * not be in a column Waystones could land a teleporting player in. Waystones tries the stone's facing first, then
    world east, west, south and north (Waystone.resolveDestination, 14.1.21), skipping suffocating cells, so with a
    clear front the arrival is the front column in every rotation; with a blocked front any clear side may be;
  * have held air, a decor block (snow layer, plant, carpet) or, in a buried or river-bed ruin only, nothing; never
    inside a redesigned stone's focal space (its breathing room, kept clear by archaeology.validate_archaeology);
  * stand on a full top surface (full block, top or double slab, upside-down stairs, path; the earth itself in a
    buried ruin), keep its lid free (or under diggable earth in a buried ruin), not lie on an authored route or clue
    and, in ring 2, see the stone through an open cell or be at most four steps from the arrival;
  * leave every position that was reachable before still reachable (audit_access.WalkGraph: from outside for
    surface ruins, from the arrival otherwise), and be reachable itself.
Cells the builder protected (the 3x3 dais of a redesigned stone is protected only against random decay, which ran
before this step) are used only when no unprotected cell of the same ring and drop fits.

retag_origin(b) gives both stone halves origin=dungeon: still "generated" for Waystones (IWaystone.wasGenerated:
village, wilderness or dungeon, so naming on first use is unchanged), and a block-state mark the client also sees,
which lets client and server agree that the stone cannot be broken (java .../protect/WaystoneProtection).
"""
from audit_access import WalkGraph, passable
from core import parse_state
from nbt import Byte

MARKER = "waystone_ruins:chests/waystone_chest/"
REALMS = ("surface", "underground", "water", "nether", "end")

DIRS = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
CW = {"north": "east", "east": "south", "south": "west", "west": "north"}
CCW = {v: k for k, v in CW.items()}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}

# Full-cube blocks the templates use (inventory of the 1.19.4 jar's 171 block names). A chest on a slab, stair or
# plant would hang or sink; containers, workstations and brushable blocks are not floors either.
FULL_FLOOR = {"minecraft:" + n for n in """
andesite basalt blackstone blue_glazed_terracotta blue_terracotta bone_block bookshelf calcite chiseled_deepslate
chiseled_polished_blackstone chiseled_quartz_block chiseled_red_sandstone chiseled_sandstone chiseled_stone_bricks
coarse_dirt cobbled_deepslate cobblestone cracked_deepslate_bricks cracked_deepslate_tiles
cracked_polished_blackstone_bricks cracked_stone_bricks crying_obsidian cut_red_sandstone cut_sandstone
cyan_terracotta dark_oak_planks dark_prismarine deepslate_bricks deepslate_tiles diorite dirt dirt_path
dripstone_block emerald_block end_stone end_stone_bricks gilded_blackstone gold_block grass_block gravel jungle_log
lapis_block moss_block mossy_cobblestone mossy_stone_bricks mud_bricks oak_log obsidian packed_ice packed_mud
polished_andesite polished_basalt polished_blackstone polished_blackstone_bricks polished_deepslate polished_diorite
polished_granite prismarine purpur_block purpur_pillar quartz_block quartz_pillar red_sand red_sandstone
red_terracotta sand sandstone sculk sea_lantern smooth_quartz smooth_red_sandstone smooth_sandstone soul_soil
spruce_log spruce_planks stone stone_bricks stripped_spruce_log terracotta tuff yellow_glazed_terracotta
yellow_terracotta
""".split()}

# Waystones' isSuffocating, approximated by "a full cube that blocks movement".
SOLID = (FULL_FLOOR - {"minecraft:dirt_path"}) | {
    "minecraft:barrel", "minecraft:smithing_table", "minecraft:crafting_table", "minecraft:suspicious_gravel",
    "minecraft:suspicious_sand", "minecraft:spawner"}

# Decor a chest may stand in for; the gate puts it back while the chests are off.
DECOR = {"minecraft:" + n for n in "snow grass fern dead_bush moss_carpet glow_lichen".split()}


def realm(kind, theme):
    if theme == "end":
        return "end"
    if theme == "nether":
        return "nether"
    return {"surface": "surface", "sunken": "surface", "cave": "underground", "water": "water"}[kind]


def retag_origin(b):
    for pos, (state, be) in list(b.blocks.items()):
        if state.startswith("waystones:") and "origin=" in state:
            name, props = parse_state(state)
            props["origin"] = "dungeon"
            b.blocks[pos] = (name + "[" + ",".join(f"{k}={v}" for k, v in props.items()) + "]", be)


def find_waystone(b):
    lower = [(p, s) for p, (s, _) in b.blocks.items() if s.startswith("waystones:") and "half=lower" in s]
    assert len(lower) == 1, f"{b.name}/{b.theme_name}: {len(lower)} lower waystone halves"
    pos, state = lower[0]
    return pos, parse_state(state)[1]["facing"]


def _name(entry):
    return parse_state(entry[0])[0] if entry else None


def _floor(entry):
    """A full top surface the chest can stand on (dirt path: one pixel low, invisible under a chest)."""
    if not entry or entry[1] is not None:
        return False
    name, props = parse_state(entry[0])
    props = props or {}
    if name in FULL_FLOOR:
        return True
    if name.endswith("_slab"):
        return props.get("type") in ("top", "double")
    if name.endswith("_stairs"):
        return props.get("half") == "top"
    return False


class Site:
    """What "no block in the template" means where this ruin generates."""

    def __init__(self, b, kind, ground):
        self.b, self.kind, self.ground = b, kind, ground
        self.surface = kind == "surface"
        xs = [p[0] for p in b.blocks]
        ys = [p[1] for p in b.blocks]
        zs = [p[2] for p in b.blocks]
        self.bounds = (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))

    def inside(self, pos):
        x0, y0, z0, x1, y1, z1 = self.bounds
        return x0 <= pos[0] <= x1 and y0 <= pos[1] <= y1 and z0 <= pos[2] <= z1

    def absent_open(self, pos):
        # open sky above a surface ruin's ground; river water around a river-bed ruin; terrain everywhere else
        return (self.surface and pos[1] > self.ground) or self.kind == "water"

    def floor(self, pos):
        entry = self.b.blocks.get(pos)
        return self.kind == "sunken" if entry is None else _floor(entry)

    def lid(self, pos):
        # a buried ruin is dug out from above: earth over the chest is fine
        return self.open(pos) or (self.kind == "sunken" and self.b.blocks.get(pos) is None)

    def clear(self, pos):
        entry = self.b.blocks.get(pos)
        return self.absent_open(pos) if entry is None else _name(entry) not in SOLID

    def open(self, pos):
        entry = self.b.blocks.get(pos)
        return self.absent_open(pos) if entry is None else passable(entry[0])

    def replaceable(self, pos):
        """How the gate restores the cell while chests are off: 'air', a WasBlock state, 'void', or None."""
        entry = self.b.blocks.get(pos)
        if entry is None:
            # buried (sunken) and river-bed (water) ruins only: elsewhere an absent voxel may be open sky
            return "void" if self.kind in ("sunken", "water") and self.inside(pos) else None
        state, be = entry
        if be is not None:
            return None
        if state == "minecraft:air":
            return "air"
        return state if _name(entry) in DECOR else None


def _rings(lower, facing, front_clear, site):
    """Candidate (column, tier) pairs in preference order, minus every column a player could arrive in."""
    x, y, z = lower
    f, r, l, k = DIRS[facing], DIRS[CW[facing]], DIRS[CCW[facing]], DIRS[OPP[facing]]
    sides = [r, l, k]
    if front_clear:
        arrival = {f}
    else:
        clear = [d for d in (f, r, l, k) if site.clear((x + d[0], y, z + d[1])) and site.clear((x + d[0], y + 1, z + d[1]))]
        arrival = set(clear) or {f}
    ring0 = [d for d in sides if d not in arrival]
    ring1 = [(k[0] + r[0], k[1] + r[1]), (k[0] + l[0], k[1] + l[1]), (f[0] + r[0], f[1] + r[1]), (f[0] + l[0], f[1] + l[1])]
    ring2 = sorted(((dx, dz) for dx in range(-2, 3) for dz in range(-2, 3) if max(abs(dx), abs(dz)) == 2),
                   key=lambda d: (d[0] * d[0] + d[1] * d[1], d != (2 * k[0], 2 * k[1]), d))
    out = [((x + dx, z + dz), 0, (dx, dz)) for dx, dz in ring0]
    out += [((x + dx, z + dz), 1, (dx, dz)) for dx, dz in ring1]
    out += [((x + dx, z + dz), 2, (dx, dz)) for dx, dz in ring2]
    return out, arrival


def _route_cells(b):
    """Authored routes, clues and a redesigned stone's focal space (the 3 x 3 x 5 air over its dais that
    archaeology.validate_archaeology keeps free: "crowded waystone")."""
    cells = set()
    for route in getattr(b, "exploration_routes", ()):
        cells.update((x, route["floor"] + 1, z) for x, z in route["cells"])
        cells.update((x, route["floor"] + 2, z) for x, z in route["cells"])
    for clue in getattr(b, "discovery_clues", ()):
        cells.update(tuple(c) for c in clue["cells"])
    if hasattr(b, "focal_space"):
        fx, g, fz = b.focal_space
        cells.update((x, y, z) for x in range(fx - 1, fx + 2) for z in range(fz - 1, fz + 2) for y in range(g + 1, g + 6))
    return cells


DROPS = (0, -1, -2, -3, -4)
NEAR_STEPS = 4


def _graph(b, site, open_secrets=True):
    return WalkGraph(b, ground=site.ground, surface=site.surface, open_secrets=open_secrets)


def _reach(b, site, start):
    """Reachable positions with the ruin's secret walls opened and, separately, closed (marked by a 1 in the tuple)."""
    out = set()
    for open_secrets in (True, False):
        g = _graph(b, site, open_secrets)
        if site.surface:
            found = g.flood(g.outside())
        else:
            found = g.flood([start]) if start and g.standing(start) else set()
        out.update((p, open_secrets) for p in found)
    return out


def _arrival_steps(b, site, lower, arrival):
    """Walking steps from where a teleported player lands (the arrival column's first standing spot at or below the
    stone's level) to every position within NEAR_STEPS."""
    g = _graph(b, site)
    starts = []
    for dx, dz in arrival:
        for y in range(lower[1], lower[1] - 8, -1):
            pos = (lower[0] + dx, y, lower[2] + dz)
            if g.standing(pos):
                starts.append(pos)
                break
    steps = {p: 0 for p in starts}
    frontier = list(starts)
    for n in range(1, NEAR_STEPS + 1):
        nxt = []
        for p in frontier:
            for q in g.neighbors(p):
                if q not in steps:
                    steps[q] = n
                    nxt.append(q)
        frontier = nxt
    return steps


def choose(b, kind, theme, ground=2):
    """(cell, facing, restore) for this build, or (None, every rejection, None)."""
    site = Site(b, kind, ground)
    lower, facing = find_waystone(b)
    fx, fz = DIRS[facing]
    front = (lower[0] + fx, lower[1], lower[2] + fz)
    front_clear = site.clear(front) and site.clear((front[0], front[1] + 1, front[2]))
    columns, arrival = _rings(lower, facing, front_clear, site)
    routes = _route_cells(b)
    before = _reach(b, site, front)
    near = _arrival_steps(b, site, lower, arrival)
    order = sorted(((tier + abs(dy), tier, abs(dy), protected, i, dy)
                    for i, (_, tier, _) in enumerate(columns) for dy in DROPS for protected in (False, True)))
    reasons = []
    for _, tier, _, protected, i, dy in order:
        (cx, cz), _, (dx, dz) = columns[i]
        cell = (cx, lower[1] + dy, cz)
        x, y, z = cell
        if (cell in b.protected) != protected:
            continue
        restore = site.replaceable(cell)
        if restore is None:
            reasons.append(f"{cell} occupied")
            continue
        if cell in routes:
            reasons.append(f"{cell} on a route")
            continue
        if not site.floor((x, y - 1, z)):
            reasons.append(f"{cell} floor {_name(b.blocks.get((x, y - 1, z)))}")
            continue
        if not all(site.lid((x, yy, z)) for yy in range(y + 1, max(y + 1, lower[1]) + 1)):
            reasons.append(f"{cell} lid or view blocked")
            continue
        approaches = {(x + ax, y + ay, z + az) for ax, az in DIRS.values() for ay in (-1, 0, 1)}
        if tier == 2:
            # the outer ring must see the stone through an open cell between them, or be a short walk away
            between = [(lower[0] + ix, lower[2] + iz) for ix in (-1, 0, 1) for iz in (-1, 0, 1)
                       if (ix, iz) != (0, 0) and abs(ix - dx) <= 1 and abs(iz - dz) <= 1]
            seen = any(site.open((bx, y, bz)) and site.open((bx, y + 1, bz)) for bx, bz in between)
            if not seen and not approaches & set(near):
                reasons.append(f"{cell} out of sight")
                continue
        saved = b.blocks.get(cell)
        b.blocks[cell] = (chest_state(facing), None)
        try:
            after = _reach(b, site, front)
        finally:
            if saved is None:
                del b.blocks[cell]
            else:
                b.blocks[cell] = saved
        lost = {p for p in before - after if p[0] != cell}
        if lost:
            reasons.append(f"{cell} cuts off {len(lost)} positions")
            continue
        if before and not any((a, True) in after for a in approaches):
            reasons.append(f"{cell} unreachable")
            continue
        return cell, facing, restore
    return None, "; ".join(dict.fromkeys(reasons)) or "no candidate", None


def chest_state(facing):
    return f"minecraft:chest[facing={facing},type=single,waterlogged=false]"


# Designs without a waystone chest, and why. Any other design that finds no cell stops the build.
EXEMPT = {
    "sacbe_gate": "the stone stands outside the gate's north wall at the template's edge, facing the wall: every "
                  "cell beside it is a possible arrival cell, a wall, or open ground the template does not define",
}


def place(b, kind, theme, ground=2):
    """Author the waystone chest; returns the cell (None for an EXEMPT design) or raises with every rejection."""
    if b.name in EXEMPT:
        b.waystone_chest = None
        b.waystone_chest_restore = None
        return None
    cell, facing, restore = choose(b, kind, theme, ground)
    if cell is None:
        raise ValueError(f"{b.name}/{b.theme_name}: no waystone chest cell ({facing})")
    be = {"id": "minecraft:chest", "LootTable": MARKER + realm(kind, theme)}
    if restore == "void":
        be["WasVoid"] = Byte(1)
    elif restore != "air":
        name, props = parse_state(restore)
        be["WasBlock"] = {"Name": name, "Properties": dict(props)} if props else {"Name": name}
    b.blocks[cell] = (chest_state(facing), be)
    b.waystone_chest = cell
    b.waystone_chest_restore = restore
    return cell


def loot_json(realm_name):
    """The realm's own table: used when its config list is emptied. Same vanilla tables as the config defaults,
    referenced, so a datapack can replace it (vanilla-table references do not run other mods' loot modifiers)."""
    from_config = {
        "surface": ["simple_dungeon", "abandoned_mineshaft", "ruined_portal"],
        "underground": ["simple_dungeon", "abandoned_mineshaft"],
        "water": ["shipwreck_supply", "shipwreck_treasure"],
        "nether": ["nether_bridge", "ruined_portal"],
        "end": ["end_city_treasure"],
    }[realm_name]
    return {"type": "minecraft:chest", "pools": [{"rolls": 1, "entries": [
        {"type": "minecraft:loot_table", "name": f"minecraft:chests/{t}", "weight": 1} for t in from_config]}]}
