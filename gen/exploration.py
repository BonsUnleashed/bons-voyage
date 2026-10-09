"""1.18 authored discovery cues, arrival courts and regional circulation.

Runs after the original design/hidden room, before reclamation and validation.
No runtime hooks, new blocks, pools or loot changes. Coordinates are authored
against the existing buildings; protected cells keep the route through decay.
"""
import math

SCHOOLS = {'egyptian': 'Egyptian', 'greek': 'Greek',
           'babylon': 'Sumerian & Babylonian', 'viking': 'Norse & Celtic',
           'mayan': 'Mayan & Aztec'}
SHOWCASES = {'temple_of_the_way', 'temple_of_ra', 'temple_of_marduk',
             'stave_shrine', 'broch', 'serpent_pyramid'}


def fixed(b, x, y, z, state):
    b.set(x, y, z, state, protect=True)


def paving(b, cells, y, material):
    for x, z in cells:
        pos = (x, y, z)
        old = b.blocks.get(pos, ('', None))
        if pos in getattr(b, 'secret_blocks', ()) or old[1]:
            continue
        fixed(b, x, y, z, material)


def lane(b, cells, floor, material, height=3):
    """Explicit, supported walk cells; never erase a functional block or seal."""
    cells = list(cells)
    if material is None:
        # Keep the authored floor without imposing a different pavement.
        b.protected.update((x,floor,z) for x,z in cells)
    else:
        paving(b, cells, floor, material)
    for x, z in cells:
        for y in range(floor+1, floor+height+1):
            old = b.blocks.get((x,y,z), ('', None))
            if old[1] or (x,y,z) in getattr(b, 'secret_blocks', ()):
                continue
            if old[0].startswith(('waystones:', 'minecraft:ladder')):
                continue
            fixed(b,x,y,z,'minecraft:air')
    b.exploration_routes = getattr(b, 'exploration_routes', []) + [
        {'floor': floor, 'cells': cells}]


def rect_path(x0,z0,x1,z1):
    return sorted({(x,z) for x in range(x0,x1+1) for z in range(z0,z1+1)
                   if x in (x0,x1) or z in (z0,z1)})


def clue(b, name, cells):
    """Record actual protected cues for release review and independent checks."""
    b.discovery_clues = getattr(b, 'discovery_clues', []) + [
        {'name': name, 'cells': list(cells)}]
    b.protected.update(cells)


def hidden_cues(b):
    if not getattr(b, 'has_hidden_room', False):
        return
    n = b.name
    if n == 'stoa':
        border = [(10,0),(11,0),(12,0),(10,1),(10,2),(11,2),(12,2)]
        paving(b,border,2,'minecraft:cyan_terracotta')
        for x in (10,12): fixed(b,x,2,0,'minecraft:chiseled_quartz_block')
        # Matching measured strip in the cellar, without disturbing its mosaic.
        paving(b,[(10,2),(11,2),(12,2)],-5,'minecraft:cyan_terracotta')
        clue(b,'A measured paving border surrounds the fitted cellar cap',
             [(x,2,z) for x,z in border]+[(11,2,1),(12,2,1)])
    elif n == 'temple_of_the_way':
        paving(b,[(21,10),(22,10),(23,10),(21,11),(21,12),(22,12)],2,'minecraft:cyan_terracotta')
        clue(b,'The cella pavement encloses a fitted inspection cap',
             [(21,2,10),(22,2,10),(21,2,11),(22,2,11)])
        # Recessed doorway jambs beside the existing cracked plug, not in it.
        for z in (9,11):
            for y in range(-4,-1): fixed(b,15,y,z,'minecraft:chiseled_quartz_block')
        for x in range(11,20): fixed(b,x,-5,10,'minecraft:cyan_terracotta')
        clue(b,'Carved jambs and a floor line continue through the blocked archive door',
             [(15,-3,9),(15,-3,11),(16,-5,10),(14,-5,10)])
    elif n == 'jungle_altar':
        for x,z in ((4,4),(5,4),(6,4),(4,5),(4,6)):
            fixed(b,x,2,z,'minecraft:red_terracotta')
        for x,z in ((4,4),(6,4)): fixed(b,x,2,z,'minecraft:chiseled_stone_bricks')
        clue(b,'A paired carved border and brushable deposit mark the service opening',
             [(4,2,4),(6,2,4),(4,2,5),(5,2,5),(5,2,6)])
    elif n == 'holy_well':
        # A dry inspection strip beside the spring, ending at the existing cap.
        paving(b,[(6,z) for z in range(3,8)],2,'minecraft:polished_andesite')
        for z in (5,7): fixed(b,7,2,z,'minecraft:chiseled_stone_bricks')
        clue(b,'A dry inspection strip ends between paired marks at the lower cistern cap',
             [(6,2,4),(6,2,5),(7,2,5),(7,2,6),(7,2,7)])


def greek_court(b):
    # Justin removed the added stone-brick road: retain the original pale floor.
    lane(b,[(x,z) for x in range(1,19) for z in (8,9,10)],2,None)
    # A loop around the exposed precinct, returning through two broken wall bays.
    lane(b,rect_path(5,5,18,13),2,'minecraft:polished_diorite')
    # Thin surviving mosaic edges make the arrival axis readable from either end.
    paving(b,[(x,z) for x in range(6,19) for z in (7,11)],2,'minecraft:cyan_terracotta')
    for x,z in ((4,7),(4,11)):
        fixed(b,x,3,z,'minecraft:chiseled_quartz_block')
    b.arrival_landmark = 'The open west approach framed by the court and paired stone bases'


def egyptian_thresholds(b):
    # Two partial screens make forecourt / column hall / sanctuary thresholds.
    for x,extent in ((13,(2,12)),(7,(3,11))):
        for z in range(extent[0],extent[1]+1):
            if 6 <= z <= 8: continue
            for y in range(9,12): fixed(b,x,y,z,'minecraft:cut_sandstone')
            fixed(b,x,12,z,'minecraft:chiseled_sandstone')
        paving(b,[(x,z) for z in (6,7,8)],8,'minecraft:polished_granite')
    lane(b,[(x,z) for x in range(4,20) for z in (6,7,8)],8,'minecraft:smooth_sandstone')
    paving(b,[(x,7) for x in range(4,20)],8,'minecraft:cut_sandstone')
    # Reapply threshold stripes after clearing the walking route.
    paving(b,[(x,z) for x in (7,13) for z in (6,7,8)],8,'minecraft:polished_granite')
    b.arrival_landmark = 'Three successive thresholds through the column hall'


def mesopotamian_courts(b):
    # Offset partitions: approach east of the first, west of the second.
    # All remain inside the old footprint and under its existing roof.
    for z,xs in ((10,range(2,11)),(7,range(8,17))):
        for x in xs:
            for y in range(8,11): fixed(b,x,y,z,'minecraft:mud_bricks')
            fixed(b,x,11,z,'minecraft:blue_glazed_terracotta[facing=south]')
    path = [(x,z) for x in (11,12,13) for z in range(9,14)]
    path += [(x,z) for x in range(5,14) for z in (8,9)]
    path += [(x,z) for x in (5,6) for z in range(5,10)]
    path += [(x,6) for x in range(5,11)]
    lane(b,path,7,'minecraft:packed_mud')
    # Branch toward a records niche; the archive hatch keeps its seal and ladder.
    lane(b,[(15,z) for z in range(8,13)],7,'minecraft:mud_bricks')
    from interiors import bookshelf
    for y in (8,9): bookshelf(b,16,y,12,'west',filled=(0,2,4))
    b.arrival_landmark = 'The glazed seat and offset courts with a records alcove'


def northern_hall(b):
    # Keep the hearth as the center; two short aisles connect the door and stone.
    cells = rect_path(4,4,8,6) + [(6,7),(6,8),(6,9),(3,5)]
    lane(b,cells,2,'minecraft:stone_bricks')
    for x in (5,7):
        for z in (3,7):
            fixed(b,x,3,z,'minecraft:spruce_stairs[facing='+('south' if z==3 else 'north')+',half=bottom,shape=straight,waterlogged=false]')
    for z in (3,7):
        for y in range(3,6): fixed(b,8,y,z,'minecraft:stripped_spruce_log[axis=y]')
    # Low side cabinets are outside the circulation ring.
    fixed(b,9,3,4,'minecraft:chiseled_bookshelf[facing=west,slot_0_occupied=false,slot_1_occupied=false,slot_2_occupied=false,slot_3_occupied=false,slot_4_occupied=false,slot_5_occupied=false]')
    b.arrival_landmark = 'The hearth framed by benches and timber posts, with two routes to the south door'


def celtic_ring(b):
    cells = [(x,z) for x in range(1,14) for z in range(1,14)
             if 4.0 < math.hypot(x-7,z-7) <= 5.65]
    lane(b,cells,2,'minecraft:stone_bricks')
    # Inward doors on both sides connect the annular passage to the central hall.
    lane(b,[(x,7) for x in range(2,6)]+[(x,7) for x in range(9,13)],2,'minecraft:polished_andesite')
    lane(b,[(7,z) for z in range(10,15)],2,'minecraft:polished_andesite')
    lane(b,[(x,z) for x in (6,7,8) for z in (5,6)],2,'minecraft:stone_bricks')
    b.arrival_landmark = 'The central hearth and inward openings to a circular wall passage'


def mesoamerican_terraces(b):
    for inset,floor in ((2,9),(4,11)):
        lane(b,rect_path(inset,inset,20-inset,20-inset),floor,'minecraft:mossy_stone_bricks')
        # Paired measuring stones flank each terrace's junction with the grand stair.
        for x in (8,12): fixed(b,x,floor+1,21-inset,'minecraft:chiseled_stone_bricks')
    # The west bank backs the existing east-facing ladder: keep it intact.
    # The dry north/east bank instead frames the pool and connects the arrival.
    lane(b,[(x,8) for x in range(7,13)]+[(12,z) for z in range(9,14)],2,'minecraft:dark_prismarine')
    # Waystones resolves arrival 1.5 blocks above its lower block. The raised
    # plinth needs a taller bay than a walking player: recess the old cornice
    # and ceiling at the south landing, under the solid pyramid tier at y=8.
    for y in (6,7): fixed(b,7,y,8,'minecraft:air')
    b.arrival_landmark = 'The jade-framed sacred well, with a dry route toward the ascent'


def apply(b):
    {'temple_of_the_way':greek_court, 'temple_of_ra':egyptian_thresholds,
     'temple_of_marduk':mesopotamian_courts, 'stave_shrine':northern_hall,
     'broch':celtic_ring, 'serpent_pyramid':mesoamerican_terraces}.get(b.name,lambda _:None)(b)
    hidden_cues(b)
