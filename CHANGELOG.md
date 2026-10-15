# Bons Voyage 1.19.4

- School-specific pottery keepsakes in curiosity caches, hidden treasuries and school-affiliated record caches. Existing treasury rewards are preserved, with one pottery keepsake added.
- Three existing lore books now offer subtle clues to discoveries in other ruins.
- Selected archive, storehouse, ceremonial and shelter archaeology sites have more appropriate common finds. Valuable-find probabilities are unchanged.
- Ordinary discovery advancements still show personal notifications but no longer announce in chat. Challenge advancements retain both.

Structure layouts, placement rules, generation frequency and dependencies are unchanged. New template details appear in newly generated ruins. Already-generated books and containers are not rewritten; unopened record caches can use the updated loot tables.

For Minecraft 1.20.1, Forge 47.4.16+. Requires Waystones 14.1.21+, Balm 7.3.44+ and Lithostitched 1.4.11+ on client and server.

Validation: 49 generator tests passed. Release comparison verified unchanged block geometry, placement data and Java classes. No fresh in-game validation is claimed for this content-only update.

Developed with AI assistance. See NOTICE.md for attribution.

# Bons Voyage 1.19.3

First public release. Minecraft 1.20.1, Forge 47.4.16 or newer.

- **Faster world generation.** Ruins check the ground at fewer points while they look
  for a site, about half as many in fresh terrain, and still sit as flat as before.
- **The Waybuilder Workshop no longer generates.** Its id stays registered, so worlds
  that already hold one keep loading.
- **One ruin per site.** Ruins of different kinds no longer land side by side. Each
  structure set keeps its own spacing, and a site now gives way when a larger Bons
  Voyage ruin generates nearby. In the test world no two surface ruins stood closer
  than about 150 blocks, and no spot had more than five within 300 blocks (before: up
  to 14). Grand temples, great dungeons and the First Waystone keep their rarity.
  New chunks only.
- **New school names.** The five schools are now Benben, Herma, Kudurru, Varða and
  Sacbe, each named for a stone its builders raised to mark the world. The Five Schools
  advancement uses the new names. Structure ids are unchanged, so worlds and datapacks
  that refer to them keep working.

## 1.19.0 (private pack build)

- **Surface ruins fit more terrain.** The site check accepts ground from two blocks
  below to three above the reference height. Every ground-contact column of every
  surface template carries two blocks of footing, and the attached pieces of grand
  ruins settle on their own ground instead of hanging at the main building's level.
  Surface ruins pass about 40 percent more candidate sites than before.
- **School names work everywhere.** Ruins wrapped by Lithostitched's structure
  modifiers were getting generic Waystones names. Newly activated stones now draw
  from their school's pool. Existing names are preserved.
- **Atmospheric biomes are covered.** Its rainforests and Kousa Jungle host the
  Sacbe school, Snowy Scrubland the Varða school, and wild
  waystones reach all of its biomes.
- **Two advancements fixed.** The Five Schools now counts every school's great
  dungeon and the Herma school's cherry ruins. What Sleeps Beneath needs the buried
  waystone used, not a walk across the surface.
- **World-generation cost measured.** With only Forge, Waystones, Balm and
  Lithostitched installed, generation ran at the same speed with and without the
  mod in a six-run test.
- **One jar.** Structures and naming ship together, with the MIT license, the
  Python generator, the Java source and the build script.

Earlier versions (1.0 to 1.19.2, August to October 2026) were private pack builds.
Placement changes apply to newly generated chunks; names, tags and advancements
apply after a restart.
