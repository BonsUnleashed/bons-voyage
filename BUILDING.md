# Bons Voyage source

Complete source of the combined Forge 1.20.1 mod, release 1.20.0. The Python
generator produces the structures, loot, tags and advancements; the Java class
integrates school-based naming with Waystones.

## Build

Use Python 3.11 or newer and JDK 17 or newer. The recorded reproducibility checks
use JDK 21 with Java 17 bytecode output. Install Forge 1.20.1-47.4.16 in a separate
server directory, then put Waystones 14.1.21, Balm 7.3.44 and Lithostitched 1.4.11 in
that directory's `mods` folder. These dependencies and Minecraft's libraries are not
included here.

```text
python build_release.py --server "/path/to/forge-server" --jdk "/path/to/jdk"
```

The output is `dist/waystone_ruins-1.20.0.jar`. The generator's intermediate
`waystone_ruins-1.20.0-data.jar` contains data only; ship the combined jar.
Compilation uses the Forge server's installed SRG libraries. With the recorded JDK
and Forge versions the build is byte-identical to the released file.

```text
python -m unittest discover -s gen -p "test*.py"
python gen/audit_access.py --seeds 10 --pristine
```

`gen/selected_sources/` holds the authored structure templates the generator
starts from. `gen/culture_names.py` holds the curated name lists. The Java source
carries the ruin-name pools and never changes the player's global Waystones name
settings.

The naming integration looks a stone's ruin up by structure tag first, then unwraps
Lithostitched's delegating structure wrappers; it always requires the stone to lie
inside a structure piece, and existing names are preserved.

Placement claims (1.19.1): every school and tier keeps its own structure set and grid, but each set's
placement is `waystone_ruins:claimed_spread`. A candidate is refused when a higher-ranked set of the same
realm (overworld, underground, nether, end) generates within the claim radius, so ruins of different sets
never share a site. Ranks and radii: `gen/claims_data.py`; rule: `src/main/java/dev/agentcraft/waystoneruins/claims`.

Retired designs (1.19.2): the Waybuilder Workshop joins wine_villa, drakkar_shed and the badlands
step_pyramid. Each stays registered, so worlds that already contain one load cleanly, but
`exclude_from_set` in `gen/build.py` keeps it out of every structure set, so it never generates.

Coarser site grid (1.19.3): every surface and End ruin's Lithostitched site check keeps its
radius and both height filters; grids of radius 12 and more sample every 5 to 8 blocks instead of
every 4 (the divisor of the radius nearest to 6, at most radius / 2, `site_step` in `gen/build.py`),
so each site costs fewer terrain-height queries; radius-8 grids keep 4. Every grid still covers its
corners, edge midpoints, centre and a ring inside the footprint.

Content polish (1.19.4): school-specific pottery keepsakes in existing curiosity,
hidden treasury and record caches; three existing books gain cross-site hints; six existing brushable
positions use archive, storehouse, ceremonial or shelter finds. Common entries are
exchanged at equal weights, preserving valuable-find probabilities. Ordinary task
and goal discoveries retain toasts without chat announcements; challenges retain
both. No blocks, placement settings, structure IDs or runtime classes change.

Settings, waystone chests and protected stones (1.20.0):

- `config/bons_voyage-common.toml` (read before a world loads; new chunks only):
  `worldgen.spacing_multiplier` (default 1.0, range 0.25 to 4.0) scales every ruin set's spacing, separation and
  claim radius when the structure sets are decoded, so Structurify and datapacks still act on top;
  `waystone_chests.enabled` (default false) and one loot-table list per realm (`surface`, `underground`, `water`,
  `nether`, `end`; vanilla chest tables by default, so items other mods add to them can appear; an empty list uses
  the mod's own `waystone_ruins:chests/waystone_chest/<realm>` table).
- `serverconfig/bons_voyage-server.toml` (per world, synced to clients): `waystones.unbreakable` (default true).
- The default spacing of every set is now the spacing the author's own pack runs (small 17/8, grand 27/14, sunken
  20/10, crypts and Nether 22/11, End 29/14, river 15/7, great dungeons 55/28, origin 103/51, undercroft 34/17).
- Every waystone template carries one chest cell beside its stone, chosen by `gen/waystone_chest.py` (never in the
  column a teleporting player lands in, never in a redesigned stone's clear dais, never cutting a route; 361 of 362
  templates, the sacbe gate excepted). The processor `waystone_ruins:waystone_chest`, first in each of those
  templates' processor lists, returns the cell exactly as it was before while the chests are off (air, the recorded
  decor block, or no block at all), and otherwise picks the chest's loot table from the configured list.
- Stones generate with `origin=dungeon` (still "generated" for Waystones, so naming on first use is unchanged). That
  block state reaches the client, so client and server both refuse a survival player's dig. Stones of ruins
  generated before 1.20.0 (`origin=wilderness`) are protected on the server when they stand inside a ruin. Creative
  players can still break them; player-placed stones are never protected.

## License and attribution

See LICENSE for the MIT terms and NOTICE.md for provenance, the substantial AI
assistance and third-party credits. Required mods and Minecraft assets are not
bundled or relicensed. Test and capture fixtures are not part of this archive or of
the public jar.
