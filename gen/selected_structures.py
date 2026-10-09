"""Approved September shortlist: frozen surface plans and authored deep annexes.

The 21 source templates are independent of the proposal gallery. Original
destination coordinates and surface clues are retained. New secrets have
explicit barriers, supported return ladders, and individually named rooms.
"""
from pathlib import Path
import hashlib,json,copy
from core import Build,parse_state
from nbt import read_nbt

SOURCE=Path(__file__).resolve().parent/'selected_sources'
SELECTION=json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
BY_ID={r['id']:r for r in SELECTION}
EXPANSIONS={
 '14': ('Salvage under the relay', ['Gauge workshop','Sorted socket store','Keeper’s sealed inventory','Salvage landing'],
        'The sockets were sorted by width, not by school. Whoever dismantled this relay left the working stone below. A matching gauge survives beside the sealed inventory. This was a careful removal; its reason is not recorded.'),
 '17': ('The second return register', ['Departure archive','Counter washing room','Unmatched returns','Register landing'],
        'One shelf holds departures. The opposing shelf holds returns. The counts disagree. Beside them a later hand has written: Leave a place for those still travelling. The empty spaces are not a list of the dead.'),
 '18': ('Below the oldest flood line', ['Sediment settling room','Gauge comparison chamber','Dry keeper’s record','Inspection landing'],
        'The oldest gauge was kept below the later flood marks. Its divisions match a traveller’s measure, though its carving is local. A dry recess preserves a warning to inspect the lower seal after every flood.'),
 '22': ('Reserves beneath the harvest', ['Seed sorting room','Measure store','Unclaimed reserve','Distribution landing'],
        'Two measures stand beside the same bin: one for households, one for passing travellers. A reserve was sealed below the public granary. The final tally leaves its recipient unnamed.'),
 '25': ('The keeper beneath the press', ['Amphora settling cellar','Lamp oil store','Keeper’s private refuge','Press cellar landing'],
        'Rough repairs interrupt the fine stonework. A household kept the lamps supplied after the press fell silent. Their refuge protects the approach to the old waystone; nothing here suggests they could make another.'),
 '54': ('The cool examination rooms', ['Ash sorting chamber','Heat gauge workshop','Rejected sample archive','Cooling vestibule'],
        'Ash samples were kept apart from travellers’ belongings. Some passed the gauge; others were sealed away with their labels reversed. The surviving notes describe local precautions, not the fate of every route.'),
 '64': ('The household below the palace', ['Stewards’ archive','Water ration room','Common Measure chamber','Later household refuge','Threshold assembly room','Keeper’s last inventory'],
        'The grand entrance was closed, but the route beneath the palace remained in use. Household pottery rests beside older measuring stones. Several keepers repaired the threshold; none signed as its builder.'),
 '65': ('The unfinished lower procession', ['Offering preparation room','Masons’ rest chamber','Name washing room','Unfinished memorial gallery','Procession turning hall','Uncarved name vault'],
        'The procession turns before the final chamber. Some tablets carry names; others have never been cut. A keeper’s note asks that blank stones stay blank until their travellers return. The interruption is left unexplained.'),
}

def load_source(row):
    path=SOURCE/(row['sid']+'.nbt')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],path
    root=read_nbt(str(path));b=Build(row['name'],row['theme'],seed=17)
    b.width,b.depth=row['size'];b.climate=row['climate'];b.ground_y=2
    ox,oy,oz=row['origin']
    for blk in root['blocks']:
        p=root['palette'][blk['state']];state=p['Name']
        if p.get('Properties'):state+='['+','.join(f'{k}={v}' for k,v in p['Properties'].items())+']'
        x,y,z=blk['pos'];b.set(x+ox,y+oy,z+oz,state,be=copy.deepcopy(blk.get('nbt')))
    b.rooms=[tuple(r) for r in row['rooms']]
    b.secret_blocks={tuple(p) for p in row['secret_blocks']}
    b.hidden_route=copy.deepcopy(row['hidden_route'])
    b.added_rooms=[];b.additional_secrets=[];b.cache_positions=[]
    return b

def palette(b):
    if b.theme_name=='egyptian':return 'sandstone','cut_sandstone','chiseled_sandstone'
    if b.theme_name=='nether':return 'polished_blackstone_bricks','blackstone','chiseled_polished_blackstone'
    if b.theme_name=='greek':return 'stone_bricks','calcite','chiseled_quartz_block'
    return 'stone_bricks','cracked_stone_bricks','chiseled_stone_bricks'

def fill(b,box,state):
    x0,y0,z0,x1,y1,z1=box
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            for z in range(z0,z1+1):b.set(x,y,z,state)

def room(b,name,box,style,index):
    x0,y0,z0,x1,y1,z1=box;wall,floor,accent=palette(b)
    fill(b,box,'minecraft:'+wall)
    fill(b,(x0,y0,z0,x1,y0,z1),'minecraft:'+floor)
    b.air(x0+1,y0+1,z0+1,x1-1,y1-1,z1-1)
    # Bonded pilasters and a shallow corbel over the side walls.
    for x in (x0+1,x1-1):
        fill(b,(x,y1-1,z0+1,x,y1-1,z1-1),'minecraft:'+wall)
    cx,cz=(x0+x1)//2,(z0+z1)//2
    for x,z in [(x0+2,z0+2),(x1-2,z1-2)]:
        b.set(x,y0+1,z,'minecraft:'+accent)
        b.set(x,y0+2,z,'minecraft:soul_lantern[hanging=false,waterlogged=false]' if b.climate=='nether' else 'minecraft:lantern[hanging=false,waterlogged=false]')
    # Each room's surviving fittings express its job, with center aisles clear.
    if style=='archive':
        for z in range(z0+2,z1-1,2):
            b.set(x0+1,y0+1,z,'minecraft:chiseled_bookshelf[facing=east,slot_0_occupied=false,slot_1_occupied=false,slot_2_occupied=false,slot_3_occupied=false,slot_4_occupied=false,slot_5_occupied=false]')
            b.set(x1-1,y0+1,z,'minecraft:decorated_pot[cracked=false,facing=north,waterlogged=false]',be={'id':'minecraft:decorated_pot','sherds':['minecraft:brick']*4})
    elif style=='workshop':
        b.set(x0+1,y0+1,cz,'minecraft:stonecutter[facing=east]')
        b.set(x1-1,y0+1,cz,'minecraft:crafting_table')
        for x in range(x0+2,x1-1,2):b.set(x,y0,z0+1,'minecraft:'+accent)
    elif style=='water':
        # A sealed, shallow settling trough; water never intersects the route.
        fill(b,(x0+1,y0,z0+1,x0+2,y0,z1-1),'minecraft:'+wall)
        for z in range(z0+2,z1-1):b.set(x0+1,y0+1,z,'minecraft:water[level=0]')
        fill(b,(x0+2,y0+1,z0+1,x0+2,y0+1,z1-1),'minecraft:'+wall)
        for z in (z0+1,z1-1):b.set(x0+1,y0+1,z,'minecraft:'+wall)
    elif style=='refuge':
        for z in range(z0+2,z1-1):b.set(x1-1,y0+1,z,'minecraft:smooth_stone_slab[type=bottom,waterlogged=false]')
        b.set(x0+1,y0+1,cz,'minecraft:crafting_table')
    elif style=='memorial':
        for z in range(z0+2,z1-1,3):
            for x in (x0+1,x1-1):fill(b,(x,y0+1,z,x,y0+2,z),'minecraft:'+accent)
    else:
        for x in range(x0+2,x1-1,3):
            for z in (z0+1,z1-1):
                b.set(x,y0+1,z,'minecraft:'+floor);b.pot(x,y0+2,z)
    b.rooms.append(tuple(box));b.added_rooms.append(dict(name=name,bounds=list(box),style=style))

def passage(b,points,floor,width=1):
    wall,_,accent=palette(b);cells=set();r=width//2
    for (ax,az),(bx,bz) in zip(points,points[1:]):
        assert ax==bx or az==bz
        line=[(x,az) for x in range(min(ax,bx),max(ax,bx)+1)] if az==bz else [(ax,z) for z in range(min(az,bz),max(az,bz)+1)]
        cells.update((x+dx,z+dz) for x,z in line for dx in range(-r,r+1) for dz in range(-r,r+1))
    # Only supply the corridor shell outside room interiors, so its roof does
    # not put a low lintel through a taller chamber or overwrite a side fitting.
    for x,z in cells:
        for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
            inside=any(a<xx<d and c<zz<f and y0==floor for a,y0,c,d,_,f in b.rooms)
            if not inside:
                for y in range(floor,floor+5):b.blocks.setdefault((xx,y,zz),('minecraft:'+wall,None))
        b.set(x,floor,z,'minecraft:'+accent)
        b.air(x,floor+1,z,x,floor+3,z)
        if not any(a<x<d and c<z<f and y0==floor for a,y0,c,d,_,f in b.rooms):b.set(x,floor+4,z,'minecraft:'+wall)

def seal(b,positions,name,clue):
    accent=palette(b)[2]
    for p in positions:b.set(*p,'minecraft:'+accent);b.secret_blocks.add(tuple(p))
    b.additional_secrets.append(dict(name=name,blocks=[list(p) for p in positions],clue=clue))

def shaft(b,x,z,bottom,top,name,facing='north'):
    wall,_,accent=palette(b)
    back=1 if facing=='north' else -1
    for y in range(bottom,top):
        for xx,zz in ((x-1,z),(x+1,z),(x,z+back)):
            # Backing is structural. Side walls stop two blocks above the
            # bottom landing, permitting an exit into the lower room.
            if zz==z+back or y>=bottom+2:b.set(xx,y,zz,'minecraft:'+wall)
        b.set(x,y,z,f'minecraft:ladder[facing={facing},waterlogged=false]')
    b.air(x,top+1,z,x,top+2,z)
    seal(b,[(x,top,z)],name,'A fitted engraved floor cap repeats the chamber’s measuring mark; a ladder returns to this same opening.')

def cache(b,pos,ident,records=False):
    x,y,z=pos;b.set(x,y,z,'minecraft:barrel[facing=up,open=false]',be={'id':'minecraft:barrel','LootTable':f'waystone_ruins:chests/selected_{ident}_records' if records else 'waystone_ruins:chests/curiosity_cache'})
    b.cache_positions.append(dict(position=list(pos),records=records))

def small_annex(b,row):
    ident=row['id'];title,names,_=EXPANSIONS[ident];wy=row['stone'][1];floor=wy-8
    # 1.18: each working site has its own circulation plan. Coordinates stay
    # inside the original annex envelope and the upper arrival stone stays put.
    plans={
        '14': ([(2,2,22,9),(2,11,10,16),(2,18,10,22),(12,11,22,22)],
               [[(17,17),(17,6),(6,6),(6,13)],[(6,13),(6,20)]], (6,17)),
        '17': ([(2,2,22,9),(2,11,9,15),(2,17,10,22),(12,11,22,22)],
               [[(17,17),(17,6),(6,6),(6,13)],[(17,19),(6,19)]], (11,19)),
        '18': ([(2,2,10,16),(12,2,22,10),(2,18,10,22),(12,12,22,22)],
               [[(17,17),(17,6),(6,6),(6,13)],[(17,19),(6,19)]], (11,19)),
        '22': ([(2,2,9,14),(11,2,22,10),(2,16,9,22),(11,12,22,22)],
               [[(17,17),(17,6),(6,6),(6,12)],[(6,12),(6,19)]], (6,15)),
        '25': ([(2,2,22,10),(2,12,10,17),(2,19,10,22),(12,12,22,22)],
               [[(17,17),(17,6),(6,6),(6,14),(17,14)],[(6,14),(6,20)]], (6,18)),
        '54': ([(2,2,10,12),(12,2,22,9),(2,14,10,22),(12,11,22,22)],
               [[(17,17),(17,6),(6,6)],[(6,6),(6,18)]], (6,13)),
    }
    footprints,routes,(seal_x,seal_z)=plans[ident]
    boxes=[(a,floor,c,d,floor+5,f) for a,c,d,f in footprints]
    styles={'14':['workshop','store','archive','workshop'],'17':['archive','water','archive','store'],
            '18':['water','workshop','archive','water'],'22':['store','workshop','store','store'],
            '25':['water','store','refuge','store'],'54':['store','workshop','archive','store']}[ident]
    for i,box in enumerate(boxes):room(b,names[i],box,styles[i],i)
    for route in routes:passage(b,route,floor)
    seal(b,[(seal_x,floor+y,seal_z) for y in (1,2,3)],'The sealed '+names[2].lower(),
         'A measuring line continues under a fitted three-course doorway plug into the private room.')
    b.annex_secret={(seal_x,floor+y,seal_z) for y in (1,2,3)}
    b.annex_layout={'id':ident,'footprints':footprints,'routes':routes,'seal':[seal_x,seal_z]}
    cx,_,cz=row['stone'];sx=max(14,cx+2);sz=max(14,cz+1)
    shaft(b,sx,sz,floor+1,wy-1,'The lower inspection cap')
    # The ladder stands against a narrow service pier within the landing.
    passage(b,[(sx,sz),(17,sz),(17,17)],floor)
    # Passage excavation must not erase the ladder itself.
    for y in range(floor+1,wy-1):b.set(sx,y,sz,'minecraft:ladder[facing=north,waterlogged=false]')
    # Records are at the back of the sealed room; the public cache is on the
    # landing, clear of the stair and all loop junctions.
    a,_,c,d,_,f=boxes[2]
    cache(b,((a+d)//2,floor+1,f-1),ident,records=True)
    cache(b,(20,floor+1,20),ident)

def large_annex(b,row):
    ident=row['id'];_,names,_=EXPANSIONS[ident];floor=row['stone'][1]-1
    if ident=='64':
        boxes=[(5,floor,9,17,floor+6,21),(5,floor,23,17,floor+6,31),
               (39,floor,9,51,floor+6,23),(39,floor,27,51,floor+6,39),(21,floor,5,35,floor+6,18)]
        styles=['archive','water','workshop','refuge','store']
        routes=[[(28,25),(28,12)],[(11,15),(28,15),(45,15)],[(11,15),(11,27)],[(45,15),(45,33)]]
        lower=(20,floor-8,39,36,floor-2,51);sx,sz=31,32;lower_route=[(sx,sz),(sx,44)]
        wall_secret=(45,25)
    else:
        boxes=[(4,floor,18,14,floor+6,30),(4,floor,34,14,floor+6,46),
               (34,floor,18,44,floor+6,30),(34,floor,34,44,floor+6,46),(17,floor,17,31,floor+6,30)]
        styles=['store','refuge','water','memorial','memorial']
        routes=[[(24,38),(24,24)],[(9,24),(24,24),(39,24)],[(9,24),(9,40)],[(39,24),(39,40)]]
        lower=(16,floor-8,52,32,floor-2,66);sx,sz=26,45;lower_route=[(sx,sz),(sx,59)]
        wall_secret=(39,32)
    for i,box in enumerate(boxes):room(b,names[i],box,styles[i],i)
    for route in routes:passage(b,route,floor,width=3)
    # Seal a whole three-wide passage; there is no route around its sides.
    x,z=wall_secret
    seal(b,[(xx,y,z) for xx in range(x-1,x+2) for y in range(floor+1,floor+4)],'The later partition','Fine engraved blocks interrupt a rougher wall; the same motif survives beside the open turning hall.')
    room(b,names[5],lower,'archive' if ident=='64' else 'memorial',5)
    passage(b,lower_route,lower[1],width=1)
    shaft(b,sx,sz,lower[1]+1,floor,'The keeper’s lower seal',facing='south')
    cache(b,((lower[0]+lower[3])//2,lower[1]+1,lower[5]-2),ident,records=True)
    cache(b,(boxes[3][3]-2,floor+1,boxes[3][5]-2),ident)

def build_selected(row):
    b=load_source(row)
    if row['id'] in EXPANSIONS:
        (large_annex if int(row['id'])>60 else small_annex)(b,row)
    return b

def record_loot(ident):
    from loot import supplies_pool,find_pool
    title,_,story=EXPANSIONS[ident]
    pages=[json.dumps({'text':story},ensure_ascii=False)]
    # SNBT permits quote/backslash escapes, but not JSON's \uXXXX escapes.
    tag='{title:'+json.dumps(title[:32],ensure_ascii=False)+',author:"An unnamed keeper",pages:['+','.join(json.dumps(p,ensure_ascii=False) for p in pages)+']}'
    # v1.17: the keeper's store behind the sealed room holds a real find, not
    # one to three single nuggets.
    return {'type':'minecraft:chest','pools':[
        {'rolls':1,'entries':[{'type':'minecraft:item','name':'minecraft:written_book','functions':[{'function':'minecraft:set_nbt','tag':tag}]}]},
        {'rolls':1,'entries':[{'type':'minecraft:item','name':'minecraft:explorer_pottery_sherd'},{'type':'minecraft:item','name':'minecraft:shelter_pottery_sherd'}]},
        supplies_pool({'min':2,'max':3}),
        find_pool()]}

def nether_site_modifier(sid,ground,size):
    """Use 3D terrain density, since Nether heightmaps return the roof.

    The jigsaw origin is stubY-1; require stone one block below the authored
    surface and open terrain one block above it. Absolute start heights keep
    this surface above the lava sea. The complete rotated footprint is sampled.
    Codec/semantics verified against installed Lithostitched 1.4.11 bytecode.
    """
    radius=((max(size[0],size[2])+1)//2+3)//4*4
    condition={'type':'lithostitched:all_of','conditions':[
        {'type':'lithostitched:offset','offset':[0,ground-2,0],'condition':{
            'type':'lithostitched:sample_noise_router','target':'final_density','min_inclusive':0.00001}},
        {'type':'lithostitched:offset','offset':[0,ground,0],'condition':{
            'type':'lithostitched:sample_noise_router','target':'final_density','max_inclusive':-0.00001}}]}
    return {'type':'lithostitched:set_structure_spawn_condition','structure':'waystone_ruins:'+sid,
            'append':True,'spawn_condition':{'type':'lithostitched:grid','radius':radius,
             'distance_between_points':4,'allowed_count':0,
             'condition':{'type':'lithostitched:not','condition':condition}}}
