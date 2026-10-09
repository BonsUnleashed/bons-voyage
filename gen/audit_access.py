"""Player-sized route audit for authored ruins (stdlib only).

Run ``python gen/audit_access.py`` from the project root. The audit places
surface designs in flat solid terrain, opens only explicitly marked secret
barriers, and checks that every authored room and waystone has a route from
outside. It uses the production template pipeline, including final clearance.
Missing blocks below ground stay solid: omitted template voxels are not air.

This is a conservative voxel audit, not a Minecraft physics engine. It models
two-block headroom, one-block jumps and ladders; it does not model swimming,
crouching, breaking ordinary masonry, or mining into an inaccessible room.
"""

from collections import deque
from functools import lru_cache
import argparse
import json
import tempfile
from unittest.mock import patch

from core import Build, parse_state


CARDINAL = ((1, 0), (-1, 0), (0, 1), (0, -1))
NON_COLLIDING = {
    "air", "cave_air", "void_air", "light", "ladder", "vine", "glow_lichen",
    "torch", "wall_torch", "soul_torch", "soul_wall_torch", "redstone_torch",
    "grass", "short_grass", "tall_grass", "fern", "large_fern", "dead_bush",
    "snow", "moss_carpet", "tripwire", "tripwire_hook", "rail", "powered_rail",
    "redstone_wire", "lily_pad", "brown_mushroom", "red_mushroom",
    "crimson_roots", "warped_roots", "nether_sprouts", "hanging_roots",
}


@lru_cache(maxsize=None)
def passable(state):
    name, properties = parse_state(state)
    block = name.split(":", 1)[-1]
    if block in NON_COLLIDING or block.endswith(("_button", "_pressure_plate")):
        return True
    # Wooden doors/trapdoors can be opened without breaking the structure.
    if block.endswith(("_door", "_trapdoor")) and not block.startswith("iron_"):
        return True
    return False


class WalkGraph:
    def __init__(self, build, ground=2, surface=True, open_secrets=True):
        self.build = build
        self.ground = ground
        self.surface = surface
        self.secrets = set(getattr(build, "secret_blocks", ())) if open_secrets else set()
        positions = build.blocks
        self.x0 = min(x for x, _, _ in positions) - 1
        self.x1 = max(x for x, _, _ in positions) + 1
        self.y0 = min(y for _, y, _ in positions) - 1
        self.y1 = max(max(y for _, y, _ in positions) + 2, ground + 2)
        self.z0 = min(z for _, _, z in positions) - 1
        self.z1 = max(z for _, _, z in positions) + 1
        self._standing = {}

    def state(self, pos):
        if pos in self.secrets:
            return "minecraft:air"
        block = self.build.blocks.get(pos)
        if block:
            state, be = block
            if state.startswith("minecraft:jigsaw"):
                return (be or {}).get("final_state", "minecraft:cobblestone")
            return state
        return "minecraft:air" if self.surface and pos[1] > self.ground else "minecraft:stone"

    def open(self, pos):
        return passable(self.state(pos))

    def ladder(self, pos):
        return self.state(pos).startswith("minecraft:ladder")

    def standing(self, pos):
        if pos in self._standing:
            return self._standing[pos]
        x, y, z = pos
        within = self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1 and self.z0 <= z <= self.z1
        below = (x, y - 1, z)
        value = (within and self.open(pos) and self.open((x, y + 1, z))
                 and (not self.open(below) or self.ladder(pos) or self.ladder(below)))
        self._standing[pos] = value
        return value

    def outside(self):
        y = self.ground + 1
        for x in range(self.x0, self.x1 + 1):
            for z in (self.z0, self.z1):
                if self.standing((x, y, z)):
                    yield (x, y, z)
        for z in range(self.z0 + 1, self.z1):
            for x in (self.x0, self.x1):
                if self.standing((x, y, z)):
                    yield (x, y, z)

    def neighbors(self, pos):
        x, y, z = pos
        for dx, dz in CARDINAL:
            for dy in (0, 1, -1):
                target = (x + dx, y + dy, z + dz)
                if not self.standing(target):
                    continue
                # A jump needs headroom above the starting position; a descent
                # needs room over the lower landing while crossing its edge.
                if dy == 1 and not self.open((x, y + 2, z)):
                    continue
                if dy == -1 and not self.open((x + dx, y + 1, z + dz)):
                    continue
                yield target
        for dy in (-1, 1):
            target = (x, y + dy, z)
            if self.standing(target) and (self.ladder(pos) or self.ladder(target)):
                yield target

    def flood(self, starts):
        visited = {p for p in starts if self.standing(p)}
        pending = deque(visited)
        while pending:
            pos = pending.popleft()
            for neighbor in self.neighbors(pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    pending.append(neighbor)
        return visited

    def room_positions(self, room):
        x0, y0, z0, x1, y1, z1 = room
        return [(x, y, z) for y in range(y0 + 1, y1)
                for x in range(x0 + 1, x1) for z in range(z0 + 1, z1)
                if self.standing((x, y, z))]


def audit_build(build, ground=2, surface=True):
    issues = []
    rooms = list(getattr(build, "rooms", ()))
    graph = WalkGraph(build, ground=ground, surface=surface)
    candidates = [graph.room_positions(room) for room in rooms]
    for room, positions in zip(rooms, candidates):
        if not positions:
            issues.append(f"room {room} has no supported two-block-high standing space")

    if surface:
        reached = graph.flood(graph.outside())
    else:
        # A wall can divide an authored room. Seed one connected main chamber,
        # rather than granting access to every isolated pocket in its bounds.
        remaining = set(max(candidates, key=len)) if candidates else set()
        reached = set()
        while remaining:
            component = graph.flood([min(remaining)])
            remaining.difference_update(component)
            if len(component) > len(reached):
                reached = component
    for room, positions in zip(rooms, candidates):
        if positions and not reached.intersection(positions):
            issues.append(f"room {room} is disconnected from {'the surface' if surface else 'the main room'}")

    for (x, y, z), (state, _) in build.blocks.items():
        if not state.startswith("waystones:") or "half=lower" not in state:
            continue
        # Reaching an adjacent column is sufficient to use a waystone on a
        # modest pedestal. The vertical range permits its normal raised dais.
        approaches = {(x + dx, y + dy, z + dz)
                      for dx, dz in CARDINAL for dy in (-2, -1, 0, 1)}
        if not reached.intersection(approaches):
            issues.append(f"waystone {(x, y, z)} has no reachable adjacent standing position")

    for (x, y, z), (state, _) in build.blocks.items():
        if state.startswith("minecraft:chest"):
            approaches = {(x + dx, y + dy, z + dz)
                          for dx, dz in CARDINAL for dy in (-1, 0, 1)}
            if not reached.intersection(approaches):
                issues.append(f"chest {(x, y, z)} has no reachable adjacent standing position")
            if not graph.open((x, y + 1, z)):
                issues.append(f"chest {(x, y, z)} has obstructed lid headroom")
        if not state.startswith("minecraft:ladder"):
            continue
        _, props = parse_state(state)
        dx, dz = {"north": (0, 1), "south": (0, -1), "east": (-1, 0), "west": (1, 0)}[props["facing"]]
        if graph.open((x + dx, y, z + dz)):
            issues.append(f"ladder {(x, y, z)} has no solid backing")
    return {"name": build.name, "theme": build.theme_name, "rooms": len(rooms),
            "reached_positions": len(reached), "issues": issues}


def build_case(name, fn, theme, kind, folder, seed=0, pristine=False, hidden=False):
    """Capture the finished in-memory build from the real emission pipeline."""
    import build as release
    b = Build(name, theme, seed=seed, pristine=pristine)
    with patch.object(release, "Build", return_value=b):
        release.build_template(name, fn, theme, kind, folder, seed=seed, pristine=pristine, hidden=hidden)
    return b


def design_cases():
    from build import SETS
    seen = set()
    for cfg in SETS.values():
        for designs, theme in [(cfg["designs"], cfg["theme"])] + list(cfg.get("extras", [])):
            for name, fn in designs.items():
                key = (name, theme)
                if key in seen:
                    continue
                seen.add(key)
                yield name, fn, theme, cfg["kind"]


def main():
    from hidden_rooms import HIDDEN_ROOMS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="Optional design names to audit")
    parser.add_argument("--json", action="store_true", help="Print structured results")
    parser.add_argument("--seeds", type=int, default=1, help="Number of deterministic layout seeds")
    parser.add_argument("--pristine", action="store_true", help="Also audit the intact design at seed 0")
    args = parser.parse_args()
    if args.seeds < 1:
        parser.error("--seeds must be positive")
    cases = list(design_cases())
    unknown = set(args.names) - {name for name, _, _, _ in cases}
    if unknown:
        parser.error(f"unknown designs: {', '.join(sorted(unknown))}")
    results = []
    with tempfile.TemporaryDirectory(prefix="waystone-access-") as folder:
        for name, fn, theme, kind in cases:
            if args.names and name not in args.names:
                continue
            variants = [(seed, False, False) for seed in range(args.seeds)]
            if args.pristine:
                variants.append((0, True, False))
            if name in HIDDEN_ROOMS and kind == 'surface':
                variants.extend((seed, False, True) for seed in range(args.seeds))
            for seed, pristine, hidden in variants:
                b = build_case(name, fn, theme, kind, folder, seed=seed, pristine=pristine, hidden=hidden)
                if kind != "surface" and not getattr(b, "rooms", ()):
                    continue
                result = audit_build(b, ground=getattr(fn, "ground", 2), surface=kind == "surface")
                result["seed"] = seed
                result["pristine"] = pristine
                result['hidden'] = hidden
                results.append(result)
    failed = [result for result in results if result["issues"]]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in failed:
            print(f"FAIL {result['name']}/{result['theme']} seed={result['seed']} pristine={result['pristine']}")
            for issue in result["issues"]:
                print(f"  {issue}")
        print(f"Audited {len(results)} templates ({sum(r['rooms'] for r in results)} rooms); {len(failed)} failed.")
    return bool(failed)


if __name__ == "__main__":
    raise SystemExit(main())
