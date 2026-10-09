"""Interior furnishing for sealed rooms and secret crypts (v1.17).

Structure NBT receives no neighbour updates, so every fitting is authored in
a state that stands on its own: lanterns hang from a chain under a solid
ceiling or sit on a solid block, candles stand on full blocks or top slabs,
cornice stairs are straight with solid corner blocks (inner-corner stair
shapes would have to be baked), wall skulls and lichen name their wall, and
niches carry their own back block so no raw terrain shows through.
Every helper takes the Build `b` first and never overwrites a protected
position (ladders, seals, archaeology, waystones, containers).
"""
import json

from nbt import Byte


def free(b, pos):
    return pos not in b.protected


def put(b, x, y, z, state, be=None):
    """Set a fitting unless the cell already holds something protected."""
    if free(b, (x, y, z)):
        b.set(x, y, z, state, be=be, protect=True)
        return True
    return False


def candles(b, x, y, z, count=3, color=None):
    name = f"minecraft:{color}_candle" if color else "minecraft:candle"
    return put(b, x, y, z, f"{name}[candles={count},lit=true,waterlogged=false]")


def hanging_lantern(b, x, y, z, chain=1, soul=False):
    """A lantern at y hanging on `chain` links from the ceiling block above."""
    for dy in range(1, chain + 1):
        put(b, x, y + dy, z, "minecraft:chain[axis=y,waterlogged=false]")
    kind = "soul_lantern" if soul else "lantern"
    return put(b, x, y, z, f"minecraft:{kind}[hanging=true,waterlogged=false]")


def standing_lantern(b, x, y, z, soul=False):
    kind = "soul_lantern" if soul else "lantern"
    return put(b, x, y, z, f"minecraft:{kind}[hanging=false,waterlogged=false]")


def wall_cells(box):
    """Shell cells facing into a room box, with the outward direction of each."""
    x0, _, z0, x1, _, z1 = box
    for x in range(x0 + 1, x1):
        yield x, z0, (0, -1)
        yield x, z1, (0, 1)
    for z in range(z0 + 1, z1):
        yield x0, z, (-1, 0)
        yield x1, z, (1, 0)


def frieze(b, box, y, field, mark, period=3):
    """A painted band round the inside walls: `field`, with `mark` repeating
    every `period` cells symmetrically about each wall's centre.

    Doorways, weak walls, niches and ladder backings are left alone.
    """
    walls = {}
    for x, z, out in wall_cells(box):
        walls.setdefault(out, []).append((x, z))
    for cells in walls.values():
        cells.sort()
        mid = (len(cells) - 1) / 2
        for i, (x, z) in enumerate(cells):
            pos = (x, y, z)
            if pos in b.protected or b.blocks.get(pos, ("minecraft:air",))[0] == "minecraft:air":
                continue
            b.set(x, y, z, mark if int(abs(i - mid) + 0.5) % period == 0 else field)


def cornice(b, box, y, stairs, corner):
    """Upside-down stairs round the ceiling, backs to the walls, solid corners.

    `box` is the room's shell box; the cornice runs along its interior edge.
    `stairs` is a stair block id (no properties).
    """
    x0, _, z0, x1, _, z1 = box
    xa, xb, za, zb = x0 + 1, x1 - 1, z0 + 1, z1 - 1
    for x in range(xa + 1, xb):
        put(b, x, y, za, f"{stairs}[facing=north,half=top,shape=straight,waterlogged=false]")
        put(b, x, y, zb, f"{stairs}[facing=south,half=top,shape=straight,waterlogged=false]")
    for z in range(za + 1, zb):
        put(b, xa, y, z, f"{stairs}[facing=west,half=top,shape=straight,waterlogged=false]")
        put(b, xb, y, z, f"{stairs}[facing=east,half=top,shape=straight,waterlogged=false]")
    for x, z in ((xa, za), (xb, za), (xa, zb), (xb, zb)):
        put(b, x, y, z, corner)


def mosaic(b, x0, z0, x1, z1, y, border, field, alt=None, center=None):
    """A floor panel: border band, checker field, optional centre stone."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x in (x0, x1) or z in (z0, z1):
                state = border
            else:
                state = alt if alt and (x + z) % 2 else field
            b.set(x, y, z, state)
    if center:
        b.set((x0 + x1) // 2, y, (z0 + z1) // 2, center)


def niche(b, x, y, z, out, back, content="minecraft:air"):
    """Recess a wall cell; the block behind it becomes the niche's own back."""
    if not free(b, (x, y, z)):
        return False
    dx, dz = out
    b.set(x + dx, y, z + dz, back)
    b.set(x, y, z, content, protect=True)
    return True


def wall_skull(b, x, y, z, facing, kind="skeleton"):
    """A carved head on the wall; `facing` points away from its wall."""
    return put(b, x, y, z, f"minecraft:{kind}_wall_skull[facing={facing}]")


def floor_skull(b, x, y, z, rotation=0, kind="skeleton"):
    return put(b, x, y, z, f"minecraft:{kind}_skull[rotation={rotation}]")


def lichen(b, x, y, z, wall):
    """Glow lichen growing on the named neighbouring face (north/south/...)."""
    faces = ",".join(f"{f}={'true' if f == wall else 'false'}"
                     for f in ("down", "east", "north", "south", "up", "west"))
    return put(b, x, y, z, f"minecraft:glow_lichen[{faces},waterlogged=false]")


def roots(b, x, y, z):
    """Hanging roots under the ceiling block at y+1."""
    return put(b, x, y, z, "minecraft:hanging_roots[waterlogged=false]")


def shelf(b, cells, y, slab):
    """Top-half slabs along `cells` [(x, z)]: a shelf with room beneath."""
    for x, z in cells:
        put(b, x, y, z, f"{slab}[type=top,waterlogged=false]")


def bookshelf(b, x, y, z, facing, filled=(0, 1, 2, 3, 4, 5), book=None):
    """A chiseled bookshelf whose books are real items, not painted spines.

    The block state and the stored items agree, so taking a book yields one.
    `book` optionally replaces the last filled slot with a given item stack.
    """
    props = ",".join(f"slot_{i}_occupied={'true' if i in filled else 'false'}" for i in range(6))
    items = [{"Slot": Byte(i), "id": "minecraft:book", "Count": Byte(1)} for i in filled]
    if book is not None and filled:
        items[-1] = dict(book, Slot=Byte(filled[-1]))
    return put(b, x, y, z, f"minecraft:chiseled_bookshelf[facing={facing},{props}]",
               be={"id": "minecraft:chiseled_bookshelf", "Items": items, "last_interacted_slot": -1})


def written_book(title, author, pages):
    """An item stack (block-entity form) of a signed book with plain-text pages."""
    return {"id": "minecraft:written_book", "Count": Byte(1),
            "tag": {"title": title, "author": author, "resolved": Byte(1),
                    "pages": [json.dumps({"text": p}, ensure_ascii=False) for p in pages]}}


def lectern(b, x, y, z, facing, book=None):
    """A lectern, optionally holding a readable book the player may take."""
    if book is None:
        return put(b, x, y, z, f"minecraft:lectern[facing={facing},has_book=false,powered=false]")
    return put(b, x, y, z, f"minecraft:lectern[facing={facing},has_book=true,powered=false]",
               be={"id": "minecraft:lectern", "Book": book, "Page": 0})


def chest(b, x, y, z, facing, table, waterlogged=False):
    """A loot chest with its support and lid space protected."""
    b.set(x, y, z, f"minecraft:chest[facing={facing},type=single,waterlogged={'true' if waterlogged else 'false'}]",
          be={"id": "minecraft:chest", "LootTable": table}, protect=True)
    b.protected.add((x, y - 1, z))
