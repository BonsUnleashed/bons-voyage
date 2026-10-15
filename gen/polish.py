"""1.19.4 content-only polish; never alter geometry or consume design RNG."""
import copy

from loot import curiosity_loot_json, hidden_treasury_json, item

SCHOOL_SHERDS = {
    'egyptian': ('prize', 'sheaf'),
    'greek': ('friend', 'heart'),
    'babylon': ('plenty', 'sheaf'),
    'viking': ('archer', 'shelter'),
    'mayan': ('explorer', 'prize'),
}
THEME_SCHOOL = dict((s, s) for s in SCHOOL_SHERDS)
THEME_SCHOOL['cherry'] = 'greek'

# Explicit authored cells, not a name/nearest-room heuristic. No added digs.
ARCHAEOLOGY_CELLS = {
    'temple_of_marduk': {(7, 2, 8): 'archive'},
    'temple_of_the_way': {(12, -5, 9): 'archive'},
    'stoa': {(9, -5, 2): 'storehouse'},
    'jungle_altar': {(5, 2, 6): 'ceremonial', (4, -5, 4): 'ceremonial'},
    'turf_longhouse': {(15, 2, 4): 'shelter'},
}

# Replace equal-weight common entries only. All valuables and total weights
# remain exact, so the probability of every untouched find is unchanged.
COMMON_REPLACEMENTS = {
    'archive': {'brick': 'paper', 'flint': 'ink_sac'},
    'storehouse': {'brick': 'iron_nugget', 'bone': 'string'},
    'ceremonial': {'brick': 'orange_dye', 'flint': 'green_dye'},
    'shelter': {'brick': 'candle', 'flint': 'stick'},
}


def school_keepsake(school):
    return {'rolls': 1, 'entries': [item(s + '_pottery_sherd')
                                  for s in SCHOOL_SHERDS[school]]}


def school_cache(school):
    table = curiosity_loot_json()
    table['pools'][0] = school_keepsake(school)
    return table


def archaeology_table(base, purpose):
    table = copy.deepcopy(base)
    replacements = COMMON_REPLACEMENTS[purpose]
    for entry in table['pools'][0]['entries']:
        name = entry['name'].removeprefix('minecraft:')
        if name in replacements:
            entry['name'] = 'minecraft:' + replacements[name]
    return table


def school_treasury(school):
    table = hidden_treasury_json()
    table['pools'].append(school_keepsake(school))
    return table


def apply(b):
    """Retarget only block-entity loot references; safe to call repeatedly."""
    school = THEME_SCHOOL.get(b.theme_name)
    cells = ARCHAEOLOGY_CELLS.get(b.name, {})
    for pos, (state, be) in list(b.blocks.items()):
        if not be:
            continue
        table = be.get('LootTable')
        target = None
        if school and table == 'waystone_ruins:chests/curiosity_cache':
            target = 'waystone_ruins:chests/curiosity_cache_' + school
        if school and table == 'waystone_ruins:chests/hidden_treasury':
            target = 'waystone_ruins:chests/hidden_treasury_' + school
        if (pos in cells and state.startswith('minecraft:suspicious_')
                and table == 'waystone_ruins:archaeology/ruins'):
            target = 'waystone_ruins:archaeology/' + cells[pos]
        if target:
            b.blocks[pos] = (state, dict(be, LootTable=target))