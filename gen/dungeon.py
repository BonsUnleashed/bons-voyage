"""v1.9 dungeon machinery: spawners and maze carving."""


def spawner(b, x, y, z, mob):
    """A monster spawner - the vanilla dungeon heartbeat."""
    b.set(x, y, z, "minecraft:spawner",
          be={"id": "minecraft:mob_spawner",
              "SpawnData": {"entity": {"id": "minecraft:" + mob}}},
          protect=True)
    b.protected.add((x, y - 1, z))


def maze_carve(b, x0, y, z0, cells_x, cells_z, height=3):
    """Recursive-backtracker maze: 1-wide corridors on a (2n+1) grid, carved
    as air through a solid mass the caller has already filled. Returns the
    (x, z) of the cell farthest from the entrance cell (0, 0) - put the
    prize there. Corridor cell (i, j) sits at (x0 + 2i + 1, z0 + 2j + 1)."""
    def cpos(i, j):
        return x0 + 2 * i + 1, z0 + 2 * j + 1

    visited = {(0, 0)}
    if cells_x < 1 or cells_z < 1 or height < 2:
        raise ValueError("maze needs positive dimensions and two-block headroom")
    entrance_x, entrance_z = cpos(0, 0)
    b.air(entrance_x, y, entrance_z, entrance_x, y + height - 1, entrance_z)
    stack = [(0, 0)]
    dist = {(0, 0): 0}
    far, far_d = (0, 0), 0
    while stack:
        ci, cj = stack[-1]
        nbrs = [(ci + di, cj + dj)
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= ci + di < cells_x and 0 <= cj + dj < cells_z
                and (ci + di, cj + dj) not in visited]
        if not nbrs:
            stack.pop()
            continue
        ni, nj = b.rng.choice(nbrs)
        cx, cz = cpos(ci, cj)
        nx, nz = cpos(ni, nj)
        for ax, az in ((cx, cz), ((cx + nx) // 2, (cz + nz) // 2), (nx, nz)):
            for dy in range(height):
                b.set(ax, y + dy, az, "minecraft:air")
        visited.add((ni, nj))
        dist[(ni, nj)] = dist[(ci, cj)] + 1
        if dist[(ni, nj)] > far_d:
            far, far_d = (ni, nj), dist[(ni, nj)]
        stack.append((ni, nj))
    return cpos(*far)
