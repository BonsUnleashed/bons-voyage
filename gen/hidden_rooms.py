"""Occasional underground discoveries attached to selected surface ruins.

Every candidate keeps the same export origin, even without its hidden room.
The empty reserved space contains no air blocks and leaves terrain untouched.
Solid capstones hide climbable shafts; clues and cache rewards reward inspection.

v1.17: each room is furnished in its school's manner and rises to a four-high
ceiling at y0 (the surface keeps its y1 footing): the stoa's painted store
with its herm, the temple's treasury and tablet archive, a Maya offering
chamber and a Celtic well of offerings. Caches use the richer curiosity table
in loot.py; the treasury adds a hidden-treasury chest before the second seal.
"""
from master import room, passage, ladder_shaft, weak_wall
from interiors import (candles, hanging_lantern, frieze, cornice, mosaic,
                       wall_skull, floor_skull, lichen, roots, shelf, bookshelf,
                       written_book, lectern, chest)
from loot import HIDDEN_TREASURY

CACHE_LOOT = 'waystone_ruins:chests/curiosity_cache'


def cache(b, x, y, z, facing='north'):
    chest(b, x, y, z, facing, CACHE_LOOT)


def sealed_shaft(b, x, z, bottom, ground, facing='north'):
    """A stable stone seal above an intact ladder, with room to step off at both ends."""
    ladder_shaft(b,x,z,bottom,ground-1,facing=facing)
    # Gravel over a ladder can fall and destroy its archaeology loot. Stone stays
    # in place until the curious player deliberately opens the engraved seal.
    b.set(x,ground,z,'chiseled',protect=True)
    if not hasattr(b,'secret_blocks'):
        b.secret_blocks=set()
    b.secret_blocks.add((x,ground,z))
    b.fill(x,ground+1,z,x,ground+2,z,'minecraft:air',protect=True)
    b.hidden_entrance=(x,ground,z)


def offering_cellar(b):
    """The stoa's store beneath its vanished end bay: amphora racks, a painted
    Doric band, and a herm - the Greek road-god's pillar, the waystone's own
    ancestor - between its candle stands."""
    box=(7,-5,0,15,0,6)
    room(b,*box,shell='brick')
    sealed_shaft(b,11,1,-4,2,facing='south')     # the ladder hugs the north wall
    # Pebble mosaic: an Aegean-blue border round a white checker and a rosette.
    mosaic(b,8,1,14,5,-5,'minecraft:cyan_terracotta','minecraft:calcite',
           alt='minecraft:polished_diorite',center='minecraft:chiseled_quartz_block')
    b.suspicious(9,-5,2)                         # a lifted tessera
    # The herm stands against the east wall between two candle stands.
    b.fill(14,-4,3,14,-3,3,'minecraft:quartz_pillar[axis=y]',protect=True)
    b.set(14,-2,3,'minecraft:chiseled_quartz_block',protect=True)
    for z in (2,4):
        b.set(14,-4,z,'minecraft:chiseled_quartz_block',protect=True)
        candles(b,14,-3,z,3)
    # Triglyphs and painted metopes, then a quartz cornice under the vault.
    frieze(b,box,-2,'minecraft:terracotta','minecraft:chiseled_quartz_block',period=2)
    cornice(b,box,-1,'minecraft:quartz_stairs','minecraft:chiseled_quartz_block')
    # Amphora racks along the south wall: jars on the floor and on a stone shelf.
    shelf(b,[(x,5) for x in range(9,14)],-3,'minecraft:quartz_slab')
    for x in (9,10,12,13):
        b.pot(x,-4,5)
    for x in (9,11,13):
        b.pot(x,-2,5)
    b.pot(8,-4,1)
    b.pot(8,-4,5)
    cache(b,8,-4,3,facing='east')
    for x in (10,12):
        hanging_lantern(b,x,-2,3)


ARCHIVE_REGISTER=written_book('Register of the Way','A keeper of the archive',[
    'Each waystone was raised with two names: the place where it stood, and the traveller who first asked for it. The first names are cut above. The second are kept here.',
    'When a stone falls silent, its second name comes down to these shelves. We read it aloud once, then set it among the others.',
    'The shelves are not full. We leave the space for those still travelling.',
])


def temple_archive(b):
    """A treasury beneath the cella, and behind its cracked west wall the tablet
    archive; the cache waits in the second room."""
    treasury=(15,-5,8,23,0,15)
    archive=(6,-5,5,14,0,13)
    room(b,*treasury,shell='brick')              # rooms[0]: reached first
    room(b,*archive,shell='brick')               # rooms[1]: behind the second seal
    sealed_shaft(b,22,11,-4,2,facing='west')     # the ladder hugs the east wall
    # The corridor is fully excavated through both walls; the treasury side is
    # a patch of cracked masonry between two bronze tripods.
    passage(b,13,-4,10,16,10,height=3,lining='brick')
    weak_wall(b,15,-4,10,15,-2,10,cracked='minecraft:cracked_stone_bricks')
    b.inner_secret={(15,y,10) for y in range(-4,-1)}
    for box,(x0,z0,x1,z1) in ((treasury,(16,9,22,14)),(archive,(7,6,13,12))):
        mosaic(b,x0,z0,x1,z1,-5,'minecraft:cyan_terracotta','minecraft:calcite',
               alt='minecraft:polished_diorite',center='minecraft:chiseled_quartz_block')
    # ---- the treasury: votive gold on a plinth, vessels on the shelves
    for z in (9,11):
        b.set(16,-4,z,'minecraft:cauldron',protect=True)
    b.set(19,-4,11,'minecraft:quartz_pillar[axis=y]',protect=True)
    b.set(19,-3,11,'minecraft:gold_block',protect=True)
    for z in (9,13):
        b.set(22,-4,z,'minecraft:chiseled_quartz_block',protect=True)
        candles(b,22,-3,z,4)
    chest(b,19,-4,14,'north',HIDDEN_TREASURY)
    shelf(b,[(17,14),(18,14),(20,14),(21,14)],-3,'minecraft:quartz_slab')
    for x in (17,18,20,21):
        b.pot(x,-2,14)
    for x in (17,21):
        b.pot(x,-4,14)
    b.pot(17,-4,9)
    b.suspicious(20,-5,12)
    frieze(b,treasury,-2,'minecraft:terracotta','minecraft:chiseled_quartz_block',period=2)
    cornice(b,treasury,-1,'minecraft:quartz_stairs','minecraft:chiseled_quartz_block')
    for x in (17,21):
        hanging_lantern(b,x,-2,12)
    # ---- the archive: floor-to-cornice shelves of tablets, a reading lectern
    for x in range(8,13):
        for y in (-4,-3,-2):
            bookshelf(b,x,y,6,'south',filled=(0,1,2,3,4,5) if (x+y)%3 else (0,2,3,5))
    for z in range(7,12):
        for y in (-4,-3,-2):
            bookshelf(b,7,y,z,'east',filled=(0,1,3,4,5) if (z+y)%2 else (0,1,2,3,4,5))
    b.fill(7,-4,6,7,-2,6,'minecraft:quartz_pillar[axis=y]',protect=True)
    lectern(b,10,-4,8,'south',book=ARCHIVE_REGISTER)
    for x in (9,11):
        b.set(x,-4,8,'minecraft:quartz_slab[type=top,waterlogged=false]',protect=True)
        candles(b,x,-3,8,2)
    # Patterned tablets and jars in the south row, the cache in its corner.
    for x,kind in ((8,'tablet'),(9,'pot'),(10,'tablet'),(11,'pot')):
        if kind=='pot':
            b.pot(x,-4,12)
        else:
            b.set(x,-4,12,'minecraft:chiseled_quartz_block',protect=True)
    cache(b,12,-4,12,facing='north')
    b.suspicious(12,-5,9)
    frieze(b,archive,-2,'minecraft:terracotta','minecraft:chiseled_quartz_block',period=2)
    cornice(b,archive,-1,'minecraft:quartz_stairs','minecraft:chiseled_quartz_block')
    hanging_lantern(b,10,-2,10)


def votive_chamber(b):
    """A buried offering room: a stela with a jade mask, skulls and copal
    candles on the altar, a lily pool where roots break through the vault."""
    box=(0,-5,0,6,0,6)
    room(b,*box,shell='brick')
    sealed_shaft(b,5,5,-4,2,facing='north')      # the ladder hugs the south wall
    # The surface hint lies on the far corner, off the main altar stair.
    b.suspicious(5,2,6)
    b.set(4,2,6,'chiseled')
    # The stela: carved stone in the north wall round a jade mask.
    b.fill(2,-4,0,4,-2,0,'minecraft:chiseled_stone_bricks',protect=True)
    b.set(3,-3,0,'minecraft:emerald_block',protect=True)
    # Cinnabar band, glyph blocks at the corners and centres, a mossy cornice.
    frieze(b,box,-2,'minecraft:red_terracotta','minecraft:chiseled_stone_bricks',period=2)
    cornice(b,box,-1,'minecraft:mossy_stone_brick_stairs','minecraft:chiseled_stone_bricks')
    # The altar before the stela: two skulls flank a candle stone.
    for x in (2,4):
        b.set(x,-4,1,'minecraft:mossy_stone_bricks',protect=True)
        floor_skull(b,x,-3,1,rotation=0)
    b.set(3,-4,1,'minecraft:chiseled_stone_bricks',protect=True)
    candles(b,3,-3,1,4)
    # A shallow offering pool along the west wall, lilies on the still water.
    slab=b.resolve('cobble_slab').split('[')[0]
    for x in (1,2):
        for z in (2,3,4):
            b.set(x,-5,z,f'{slab}[type=bottom,waterlogged=true]',protect=True)
    for x,z in ((1,3),(2,2)):
        b.set(x,-4,z,'minecraft:lily_pad',protect=True)
    for x,z in ((2,4),(4,2)):
        roots(b,x,-1,z)
    lichen(b,5,-3,3,'east')
    lichen(b,1,-3,5,'west')
    b.pot(1,-4,1)
    b.pot(5,-4,3)
    b.suspicious(4,-5,4)
    cache(b,5,-4,1,facing='west')
    hanging_lantern(b,3,-2,3)


def old_cistern(b):
    """The spring's older chamber: a kerbed pool with the pilgrims' gold still
    on its floor, carved heads watching the water from all four walls."""
    box=(0,-5,0,8,0,8)
    room(b,*box,shell='cobble')
    sealed_shaft(b,7,6,-4,2,facing='west')       # the ladder hugs the east wall
    # A paved walk round a kerbed 3x3 pool; the walk is part of the floor course.
    b.fill(1,-5,1,7,-5,7,'cobble')
    for x in range(2,7):
        for z in range(2,7):
            if x in (2,6) or z in (2,6):
                corner=x in (2,6) and z in (2,6)
                b.set(x,-4,z,'minecraft:chiseled_stone_bricks' if corner else 'minecraft:stone_bricks',protect=True)
    b.fill(3,-5,3,5,-5,5,'minecraft:mossy_stone_bricks',protect=True)
    b.set(4,-5,4,'minecraft:gold_block',protect=True)     # what the pilgrims left
    b.fill(3,-4,3,5,-4,5,'minecraft:water',protect=True)
    # Drystone walls with a stone lintel course; heads keep watch from each
    # wall and candles burn on the kerb's corner stones. (The room fills the
    # well's whole footprint, so wall niches would reach outside the template.)
    cornice(b,box,-1,'minecraft:stone_brick_stairs','minecraft:chiseled_stone_bricks')
    for x,z,facing in ((4,1,'south'),(4,7,'north'),(1,4,'east'),(7,4,'west')):
        wall_skull(b,x,-2,z,facing)
    for x in (2,6):
        for z in (2,6):
            candles(b,x,-3,z,3)
    for x,z in ((3,3),(5,5)):
        hanging_lantern(b,x,-2,z)
    for x,z,wall in ((1,2,'west'),(7,3,'east'),(3,7,'south')):
        lichen(b,x,-3,z,wall)
    for x,z in ((1,6),(6,7),(2,1)):
        b.set(x,-4,z,'minecraft:moss_carpet',protect=True)
    b.pot(1,-4,1)
    b.pot(7,-4,1)
    b.suspicious(6,-5,1)
    cache(b,1,-4,7,facing='east')


HIDDEN_ROOMS={
    'stoa':offering_cellar,
    'temple_of_the_way':temple_archive,
    'jungle_altar':votive_chamber,
    'holy_well':old_cistern,
}

# All four layouts have their lowest solid course at -5. Normal variants use
# the same origin without writing any underground blocks in the reserved space.
MIN_Y=-5


def attach(b, hidden=False):
    if b.name not in HIDDEN_ROOMS:
        if hidden:
            raise ValueError(f'{b.name}: no hidden-room design')
        return
    b.template_min_y=MIN_Y
    if hidden:
        HIDDEN_ROOMS[b.name](b)
        b.has_hidden_room=True
