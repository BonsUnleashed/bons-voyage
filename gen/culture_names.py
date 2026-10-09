"""Waybuilder name pools - the single source of truth for every curated
waystone name in the pack (v2.1, 2026-09-08: + pseudo-language names in each
culture's tongue, doubling both halves).

Two consumers:
  * companion/build_companion.py  -> the `ruin` list of each culture is baked
    into waystone_ruins_names.jar and applied to waystones standing inside a
    structure carrying that culture's tag (school_*, theme_*).
  * gen/waystone_pool.py          -> LORE + ANTIQUITY + every culture's `wild`
    list become `customWaystoneNames` in waystones-common.toml on both
    instances, so wild waystones anywhere draw from the same schemes.

The `ruin` and `wild` halves of a culture are DISJOINT so the companion can
never hand out a name the config pool has already used. Every name is unique
across the whole module (asserted at import).

Registers, per Justin 2026-09-08: Waybuilder lore, cross-cultural antiquity,
and the five schools - Egyptian, Greek, Sumerian & Babylonian, Norse & Celtic (was
"Viking"), Mayan & Aztec - plus Nether/End for the far ruins. Generic high fantasy,
compound place names, cozy pastoral, frontier and neutral wayside names were
all removed from the pool.

Each culture list follows the same recipe: evocative English built on that
culture's own nouns ("The <cultural noun> <travel noun>") and pseudo-language
place names in that culture's phonology, roughly half and half.
"""

# ---------------------------------------------------------------- Waybuilder lore
LORE = [
    "Waybuilders' Rest", "First Pillar", "Cradle of the Way", "The Last Waybuilder",
    "The Fifth School", "The First Road", "Legacy of the Waybuilders", "Stair of Names",
    "Well of the Way", "Keystone of the Way", "The Unbroken Way", "Threshold of the Way",
    "The Waybuilders' Ledger", "Cornerstone of the Way", "The Way Beneath",
    "Hearth of the Waybuilders", "The Waybuilders' Vigil", "Oath of the Waybuilders",
    "The Way Remembered", "Where the Way Divides", "The Waymakers' Pledge",
    "Stone of the Long Journey", "The Second Pillar", "The Hundredth Stone",
    "The Waybuilders' Compass", "Meeting of the Schools", "The Masons' Rest",
    "Hall of the Five Schools", "The Way Unfinished", "The Founder's Marker",
    "Seat of the Master Mason", "Toll of the Waybuilders", "The Apprentice Stone",
    "The Journeyman's Gate", "The Way Made Whole", "Vigil of the First School",
    "Rest of the Wayfinders", "The Carved Covenant", "The Waybuilders' Sorrow",
    "Stone of the Parting", "The Last Road Laid", "Marker of the Old Survey",
    "The Surveyor's Rest", "Plinth of the Founders", "The Waybuilders' Promise",
    "End of the First Road", "The Quarry Stone", "Milestone of the Schools",
    "The Way Forgotten", "Gate of the Waybuilders", "Watch of the Waybuilders",
    "The Masons' Mark", "The Way Between Worlds", "The Long Way Home",
    "Rest of the First Builders", "Stone of the Silent Guild", "The Guildhall Marker",
    "The Waybuilders' Reckoning", "Anchor of the Way", "The Way Endures",
]

# ---------------------------------------------------------------- antiquity (cross-school)
ANTIQUITY = [
    "Athena's Repose", "The White Tholos", "The Glazed Gate", "The Silent Ziggurat",
    "Runegate of the Ancients", "The Colossus Steps", "The Painted Vault", "The Blue Gate",
    "The Sand King's Rest", "The Jade Steps", "Oracle's Threshold", "The Sunken Pantheon",
    "The Quiet Legion", "Gate of Reeds", "The Fallen Colossus", "The Marble Forum",
    "The Lapis Court", "The Broken Aqueduct", "Court of the Sphinxes", "The Bronze Age Marker",
    "The Tin Road", "The Amber Road Stone", "The Incense Road", "The Salt Caravan Rest",
    "The Papyrus Gate", "The Basalt Stele", "The Lion Gate", "The Cedar Hall",
    "The Alabaster Seat", "The Terracotta Legion", "The Faience Shrine", "The Electrum Marker",
    "The Gilded Sarcophagus", "The Hippodrome Stone", "The Necropolis Gate", "The Sacred Way",
    "The Votive Stair", "The Granary Vault", "The Mosaic Court", "The Tribute Road",
]

# ---------------------------------------------------------------- the five schools
EGYPTIAN_RUIN = [
    "The Pharaoh's Waygate", "Rest of the Golden Scarab", "The Obelisk Road",
    "Shrine of the Setting Sun", "The Ferryman's Toll", "Gate of Two Horizons",
    "The Sandworn Sphinx", "Court of the Ibis", "The Painted Tomb",
    "Threshold of Reeds", "The Canopic Vault", "Way of the Jackal",
    "Sekh-Amara", "Ankh-Neferu", "Djed-Hotep's Rest", "Khet-Nubara",
    "The Steps of Ausar", "Meret-Sokar", "Path of Khepri", "Wadj-Halla",
    "Setep-Ra's Landing", "Naqada Stone", "Iunu Crossing", "Heka-Sematawy",
]
EGYPTIAN_WILD = [
    "The Sunboat Landing", "Rest of the Reed Scribe", "The Lotus Threshold",
    "Gate of the Western Bank", "The Alabaster Sphinx", "Court of the Cataract",
    "The Scarab Road", "Shrine of the Morning Barque", "The Nilometer Stone",
    "Way of the Falcon", "The Hyena Tomb", "The Pylon of Dusk",
    "Neb-Kheru", "Ahmes-Ra's Rest", "Ta-Senet Crossing", "Hor-Aha Stone",
    "Kemet-Nefer", "Abdju Landing", "The Steps of Sobek", "Wadi-Hemen",
    "Men-Nefer Gate", "Sen-Useret's Toll", "Iteru Ford", "Per-Bastet Marker",
]

GREEK_RUIN = [
    "The Marble Tholos", "Oracle of the Cherry Grove", "The Broken Agora",
    "Landing of a Thousand Ships", "The Olive Gate", "Stair of the Muses",
    "The Laurel Crossing", "Temple of the Western Wind", "The Amphora Rest",
    "Colonnade's End", "The Shepherd King's Seat", "Harbor of Heroes",
    "Tholos of Argeia", "Delphikon", "Naxopolis Gate", "Kythera Stone",
    "The Argonaut's Anchor", "Petralonia", "Stoa of Lysandros", "Thermon Rest",
    "Akrothea", "Ophellas' Milestone", "Eleutheria Gate", "Kastraki Point",
]
GREEK_WILD = [
    "The Cypress Stair", "Rest of the Olive Press", "The Bronze Charioteer",
    "Gate of the Twelve Labors", "The Sea-Nymph's Landing", "Court of the Kithara",
    "The Delian Road", "Shrine of the Hearth Goddess", "The Fig Tree Milestone",
    "Way of the Hoplite", "The Dolphin Mosaic", "The Owl Plinth",
    "Heliokrene", "Arkadios' Rest", "Thalassa Point", "Myrtos Stone",
    "Keramion Gate", "Pelagon Crossing", "The Stoa of Nikandros", "Orthia's Toll",
    "Leukippe Landing", "Amphion Stair", "Ionikos Marker", "Erythrai Crossing",
]

BABYLONIAN_RUIN = [
    "The Sunken Ziggurat", "Gate of the Lion Frieze", "The Glazed Blue Gate",
    "Hanging Garden's Rest", "The Cuneiform Stone", "Court of the Star-Readers",
    "The Bitumen Road", "Tower of the Seven Tiers", "The Euphrat Ford",
    "Seat of the Sky Scribe", "The Clay Tablet Toll", "Walls of the First City",
    "Nabu-Etemen", "Etemenanki's Shadow", "Ishtar-Kalla", "Marduk's Waymark",
    "Bab-Ilim Crossing", "Sin-Ahara", "Uruk's Last Gate", "Nippur Stone",
    "Tiamat's Rest", "Enlil-Zakar", "Akkad-Nur", "Zigg-Aratta",
]
BABYLONIAN_WILD = [
    "The Reed-Mat Road", "Rest of the Date Palm", "The Lamassu Gate",
    "Gate of the Fourth Wall", "The Winged Bull Stone", "Court of the Canal Lords",
    "The Kudurru Marker", "Shrine of the Evening Star", "The Ziggurat Stair",
    "Way of the Water Clock", "The Tamarisk Toll", "The Brickmakers' Court",
    "Kish-Amurru", "Ninlil's Rest", "Larsa Crossing", "Eridu Stone",
    "Sippar Gate", "Shamash-Nadin's Toll", "Anu-Tishpak", "Borsip Landing",
    "Esagil's Shadow", "Ur-Nammu Ford", "Lagash Marker", "Nergal-Sharru's Seat",
]

# Norse & Celtic: the fifth school is a northern pairing - drystone brochs,
# henges and passage tombs beside the longhouses and ship settings.
NORSE_RUIN = [
    "The Longship's Landing", "Runestone of the North Sea", "The Mead Hall Marker",
    "Fjordwatch", "The Whalebone Arch", "Shieldwall Rest",
    "The Frost-Braided Gate", "Cairn of the Nine Winters", "The Wolfpelt Camp",
    "Saga Stone", "The Ice-Bound Wharf", "Hall of the Salt Wind",
    "Jarnvik Stone", "Skjoldheim", "Ulfgard Crossing", "Hrafnastad",
    "Vestrfjord Toll", "Eiriksmark", "Thorvald's Rest", "Ymirfell",
    "Draugholt", "Solvang Gate", "Kolgrim's Cairn", "Nordrvegr",
]
CELTIC_RUIN = [
    "The Standing Stones", "Rest of the Ninth Wave", "The Ogham Stone",
    "Gate of the Hazel Grove", "The Rowan Ford", "Cairn of the Three Sisters",
    "The Dolmen Road", "Shrine of the Salmon Pool", "The Torc Marker",
    "Way of the Wren", "The Cauldron Seat", "The Mistbound Rath",
    "Dun Brannoc", "Caer Lludd", "Rath Fionnan", "Lios na Greine",
    "Inis Ceol", "Bryn Ysgeir", "Carreg Dhu", "Aber Tywi Crossing",
    "Cill Ronan's Rest", "Tor Maen", "Dun Scaith", "Pen Gwyn Stone",
]
NORSE_CELTIC_RUIN = NORSE_RUIN + CELTIC_RUIN
NORSE_CELTIC_WILD = [
    "The Raven Banner Rest", "Gate of the Nine Worlds", "The Bearskin Marker",
    "Rest of the Salt-Grey Sea", "The Rune-Cut Stair", "Way of the Wolf's Tooth",
    "Gunnarsvik", "Ingridsholm", "Haraldsgard Crossing", "Brekkafell",
    "Ormstad Gate", "Sigrun's Toll",
    "The Holly Ford", "Rest of the Hooded Crow", "Gate of the Otherworld",
    "The Fern Bank Marker", "Court of the Bards", "The Mistletoe Toll",
    "Glen Aithne", "Loch Dubhan Stone", "Bryn Dathyl", "Caer Oisin",
    "Rath Bregha Crossing", "Ard Fionnuala",
]

MAYAN_RUIN = [
    "Temple of the Feathered Way", "The Jade Stair", "Altar of the Howler Kings",
    "The Vine-Choked Pyramid", "Court of the Ballgame", "The Cenote Shrine",
    "Stone of the Long Count", "The Obsidian Butterfly", "The Smoking Mirror Gate",
    "Rest of the Maize God", "The Stelae Field", "Crossing of the Sacred Ceiba",
    "Yaxha'kul", "Itzam-Naab", "Chak-Balam Rest", "K'inich Gate",
    "Xibal-Ha Door", "Tikal-Muul", "Nakum Stone", "Copan-Witz",
    "Zac-Nicte Crossing", "Ah-Puch's Toll", "Uxben Waymark", "Kukul-Chan's Seat",
]
MAYAN_WILD = [
    "The Cacao Road", "Rest of the Jaguar Priest", "The Quetzal Stair",
    "Gate of the Thirteen Skies", "The Turquoise Mask Stone", "Court of the Rain Bringers",
    "The Copal Shrine", "Shrine of the Twin Heroes", "The Stucco Frieze",
    "Way of the Hummingbird", "The Chultun Toll", "The Corn Mother's Seat",
    "Ixchel's Rest", "Yax-Mutul Gate", "Bonampak Stone", "Kaan-Chak Crossing",
    "Ek-Balam Marker", "Lakam-Ha Toll", "Ha'-Tun", "Muyil Landing",
    "Calakmul Stair", "Wak-Kab'nal", "Pakal's Landing", "Xunan-Tunich Crossing",
]

# ---------------------------------------------------------------- the far ruins
NETHER_RUIN = [
    "The Soul Forge Landing", "Vault of Burning Bone", "The Basalt Span",
    "Bridge of the Crimson Deep", "The Weeping Obsidian Gate", "Ashgate of the Under-Road",
    "Ghast-Song Rest", "The Molten Milestone", "Netherrack Nave",
    "The Sulfur Court", "Piglin's Bane Crossing", "The Cinder Ferry",
]
NETHER_WILD = [
    "The Lava Ford", "Rest of the Blackstone Kings", "The Warped Toll",
    "Gate of the Sightless Deep", "The Glowstone Stair", "Way of the Strider",
    "The Bastion Road", "The Magma Court", "Shrine of the Fungus Spire",
    "The Quartz Vein Marker", "Crimson Gate", "Hoglin's Rest",
]
END_RUIN = [
    "The Chorus Rest", "Gate at the World's End", "The Void-Touched Plinth",
    "Ender Pilgrim's Stone", "The Purpur Vault", "Levitant Steps",
    "The Shulker's Toll", "Isle of the Silent Flight", "The Dragon's Wake Gate",
    "The Starless Crossing", "Obsidian Pillar Rest", "The Endstone Causeway",
]
END_WILD = [
    "The Chorus Fruit Road", "Rest of the Void Watchers", "The Levitation Stair",
    "Gate of the Outer Isles", "The Purpur Colonnade", "Way of the End Ship",
    "The Gateway Marker", "Court of the Ender Pearl", "Shrine of the Elytra",
    "The Obsidian Spire Toll", "The Endermite Ford", "The Last Crystal Rest",
]

# ---------------------------------------------------------------- v2.1: names in each culture's tongue
# Justin 2026-09-08: "add a lot of names from the cultures using their language,
# double the naming pool". Pure pseudo-language place names (ASCII only), a
# travel noun on most so they still read as waystones. Nether and End use two
# invented tongues: a guttural piglin one and a sibilant End one.

EGYPTIAN_LANG_RUIN = [
    "Waset Landing", "Ipet-Sut Gate", "Nekhen Stone", "Khmun Crossing", "Ta-Mery Rest",
    "Shedet Ford", "Zawty Marker", "Nubt-Seshat", "Maat-Kheru Toll", "Hut-Waret Gate",
    "Sau-Neith Stone", "Behdet Landing", "Iunet-Hathor", "Gebtu Crossing", "Tjenu Rest",
    "Nekheb Stair", "Pa-Sekhem", "Kha-Merut Toll", "Ren-Ankhet", "Djoser-Nub Marker",
    "Seshen-Ra Landing", "Tawy-Hekat", "Amun-Weset Gate", "Ipu-Min Stone",
]
EGYPTIAN_LANG_WILD = [
    "Kha-Sutekh Rest", "Neferet-Iry Crossing", "Sobek-Shedty Ford", "Weret-Hekau Gate",
    "Ankh-Tawy Stone", "Meri-Ptah Landing", "Hesy-Ra Marker", "Nub-Hotep Toll",
    "Sat-Amun Rest", "Khnum-Hotep Crossing", "Iset-Nofret Gate", "Peribsen Stone",
    "Sekhem-Ka Landing", "Wadjet-Ineb Marker", "Nakht-Min Rest", "Ra-Hotep Crossing",
    "Djehuty-Nakht Stone", "Ipuwer's Toll", "Kagemni Gate", "Ptah-Shepses Landing",
    "Hemiunu Stone", "Senenmut's Rest", "Amenemhat Crossing", "Nebet-Tawy Marker",
    "Merit-Neith Gate", "Ka-Aper Stone", "Sabu-Tjety Rest", "Weni-Djau Ford",
    "Qar-Meryre Landing", "Rahotep-Nofret Toll", "Ankhtifi Stone", "Baket-Amun Crossing",
    "Meketre's Rest", "Nefer-Senut Gate", "Djefa-Hapi Marker", "Kheti-Sa Ford",
    "Sat-Hathor Landing", "Intef-Iqer Stone", "Hor-Djedef Toll", "Nefer-Maat Rest",
    "Iry-Hor Crossing", "Khaba-Seth Gate", "Sneferu-Ka Landing", "Netjer-Aperef Stone",
    "Unas-Ankh Marker", "Teti-Meri Rest", "Pepi-Nakht Crossing", "Sankh-Kare Gate",
]

GREEK_LANG_RUIN = [
    "Kallipolis Gate", "Hieron of Phaidros", "Oreithyia Stone", "Lykosoura", "Panakton Crossing",
    "Thermopylion Rest", "Anthedon Landing", "Kyparissia Stone", "Melanthos' Milestone",
    "Pleuron Gate", "Aigosthena Point", "Demetrias Crossing", "Oinoe Rest", "Halieis Landing",
    "Tegyra Stone", "Kleitor Gate", "Stymphalos Crossing", "Psophis Marker", "Thyrea Rest",
    "Alalkomenai", "Eutresis Stone", "Skillous Gate", "Lepreon Landing", "Phigaleia",
]
GREEK_LANG_WILD = [
    "Theodoros' Stair", "Kalliste Landing", "Herakleia Gate", "Orchomenos Stone",
    "Nauplion Crossing", "Xenokrates' Rest", "Aristeia Marker", "Zephyria Point",
    "Dionysias Gate", "Polyxena's Toll", "Chalkeia Stone", "Brauron Landing",
    "Eresos Crossing", "Methymna Rest", "Kydonia Gate", "Aptera Stone",
    "Lyttos Marker", "Praisos Landing", "Gortyna Crossing", "Phaistion Rest",
    "Hyria Gate", "Onchestos Stone", "Tanagra Crossing", "Chaironeia Rest",
    "Elateia Marker", "Hyampolis Gate", "Abai Stone", "Daulis Landing",
    "Amphissa Crossing", "Naupaktos Rest", "Kalydon Gate", "Olenos Stone",
    "Stratos Marker", "Amphilochia Landing", "Ambrakia Crossing", "Dodona Rest",
    "Kassope Gate", "Elea Stone", "Bouthroton Landing", "Phoinike Marker",
    "Antigoneia Crossing", "Pandosia Rest", "Passaron Gate", "Molossis Stone",
    "Orraon Landing", "Gitana Marker", "Eurymenai Crossing", "Thesprotia Rest",
]

BABYLONIAN_LANG_RUIN = [
    "Dur-Kurigal Gate", "Kutha-Nergal Stone", "Dilbat Crossing", "Isin-Gula Rest", "Girsu Marker",
    "Umma-Shara Landing", "Adab Stone", "Shuruppak Ford", "Bad-Tibira Gate", "Akshak Crossing",
    "Mari-Zimri Rest", "Eshnunna Stone", "Der-Ishtaran Toll", "Upi Landing", "Kar-Nabu Gate",
    "Bit-Adini Marker", "Nusku-Ibni Rest", "Zababa-Iddin Crossing", "Ninurta-Apla Stone",
    "Adad-Nirari Gate", "Ea-Nasir's Toll", "Ibbi-Sin Landing", "Rim-Sin Marker", "Hammurapi's Stone",
]
BABYLONIAN_LANG_WILD = [
    "Kudur-Mabuk Gate", "Warad-Sin Rest", "Sumu-Abum Crossing", "Sabium Stone",
    "Apil-Sin Landing", "Samsu-Iluna Marker", "Abi-Eshuh Gate", "Ammi-Ditana Rest",
    "Kurigalzu Stone", "Kadashman Crossing", "Burna-Buriash Toll", "Nazi-Maruttash Gate",
    "Kashtiliash Landing", "Adad-Shuma Rest", "Meli-Shipak Stone", "Marduk-Apla Crossing",
    "Itti-Marduk Gate", "Nabu-Mukin Marker", "Eriba-Marduk Rest", "Ninurta-Kudurri Stone",
    "Shirikti-Shuqamuna Toll", "Nabonassar Landing", "Nabu-Nadin Gate", "Shamash-Shum Crossing",
    "Kandalanu Rest", "Nabopolassar Stone", "Nabu-Kudurri Marker", "Amel-Marduk Gate",
    "Neriglissar Landing", "Labashi Crossing", "Nabu-Naid Rest", "Bel-Sharru Stone",
    "Sin-Leqi Toll", "Uruk-Warka Gate", "Kar-Tukulti Landing", "Dur-Sharrukin Marker",
    "Kalhu Crossing", "Arbail Rest", "Harran Stone", "Mari-Tuttul Gate",
    "Emar Landing", "Nuzi Crossing", "Arrapha Rest", "Ekallatum Stone",
    "Ashur-Uballit Marker", "Til-Barsip Gate", "Guzana Landing", "Nasibina Crossing",
]

NORSE_LANG_RUIN = [
    "Bjornsvik", "Sigurdheim", "Hakonsgard", "Leifsnes", "Ragnarsholt Crossing", "Olafsby Stone",
    "Gunnhildsvang", "Astridsdal Rest", "Freydisfjord", "Helgafell Gate", "Torsteinsmark",
    "Egilsnes Toll", "Snorrastad", "Grimsnes Stone", "Ketilsberg Crossing", "Hallvardsholm",
    "Ivarsdal Rest", "Rolfsund Gate", "Svensfoss Marker", "Tokesvatn", "Arnesheim Crossing",
    "Vidarslund", "Yngvarshamar Rest", "Eyvindseyri",
]
CELTIC_LANG_RUIN = [
    "Dun Conall", "Rath Niamh", "Caer Deirdre", "Lios Aoife", "Cnoc Ciarain Stone",
    "Achadh Eogain", "Baile Brain Crossing", "Tobar Brighde", "Druim Lugha Rest", "Mag Nuadat",
    "Sliabh Macha Gate", "Beann Medbha", "Llan Fergus Marker", "Nant Cormac", "Cwm Ailill Rest",
    "Coed Gwydion", "Pant Rhiannon Crossing", "Mynydd Arianrhod", "Ynys Owain Stone",
    "Bod Taliesin", "Tre Ceridwen Gate", "Kil Bedwyr Toll", "Bal Elffin Landing", "Caer Cai",
]
NORSE_CELTIC_LANG_WILD = [
    "Hjalmarsvik", "Steinarsheim Rest", "Brynjarsgard", "Halfdansnes Crossing", "Ormsfjord Stone",
    "Ulfheim Gate", "Kolbeinsholt", "Asgeirsmark Toll", "Thorfinnsby", "Ragnhildsdal Landing",
    "Sveinnsvang", "Hallfridsberg Rest", "Gudrunsholm Crossing", "Einarsund Stone", "Bardisfoss",
    "Aslaugsvatn Gate", "Hroaldsheim Marker", "Sigvatslund", "Njalsnes Rest", "Arnbjornshamar",
    "Ketilseyri Crossing", "Vigdisfell Stone", "Ottarsgard Toll", "Finnbogastad",
    "Dun Eochaidh Rest", "Rath Grainne", "Caer Meilyr Crossing", "Lios Fiachra Stone",
    "Inis Sadhbh", "Bryn Cadwallon Gate", "Carreg Iorwerth", "Aber Gwenllian Marker",
    "Cill Colman's Rest", "Tor Ysbaddaden", "Pen Idris Landing", "Glen Ruairi Stone",
    "Loch Muirne Crossing", "Ard Diarmaid", "Cnoc Etain Gate", "Achadh Finntan Rest",
    "Baile Odhran", "Tobar Lasair Marker", "Druim Tuathal Stone", "Mag Aodh Crossing",
    "Sliabh Blathnaid Landing", "Beann Cathal Rest", "Llan Geraint Gate", "Nant Elowen Toll",
]

MAYAN_LANG_RUIN = [
    "Yax-K'uk' Gate", "Sak-Witz Stone", "Ik'-Nah Crossing", "Bolon-Tun Rest", "Chan-Ha' Landing",
    "Ox-Witza Marker", "Sa'al Gate", "Uaxac-Tun Stone", "Lamanai Crossing", "Altun-Ha Rest",
    "Dzibanche Landing", "Kohunlich Marker", "Xaman-Ek' Gate", "Nohol-Kab' Stone",
    "Lakin-K'in Crossing", "Chikin-Uh Rest", "Ho'-Balam Landing", "Uuk-Chan Marker",
    "Waxak-Nal Gate", "Lahun-Ahau Stone", "Yaxchilan Crossing", "Po'-Tonina Rest",
    "Seibal Landing", "K'uk'-Mo' Marker",
]
MAYAN_LANG_WILD = [
    "Kan-B'alam Gate", "Yax-Pasaj Stone", "Itzam-K'an Crossing", "Chak-Tok Rest",
    "K'ak'-Tiliw Landing", "Yuknoom Marker", "Tajal-Chan Gate", "Sihyaj Stone",
    "Nuun-Ujol Crossing", "Jasaw-Chan Rest", "Yik'in Landing", "Wak-Chan Marker",
    "Ukit-Took' Gate", "Bahlam-Ajaw Stone", "K'awiil-Chan Crossing", "Ix-Wak Rest",
    "Sak-K'uk' Landing", "Ahkal-Mo' Marker", "Kinich-Janaab Gate", "Butz'aj Stone",
    "K'an-Joy Crossing", "Yohl-Ik'nal Rest", "Muwaan-Mat Landing", "Ajen-Yohl Marker",
    "Tuun-K'ab Gate", "Ek'-Way Stone", "Nal-Kaan Crossing", "Ixim-Te' Rest",
    "Ch'ok-Tun Landing", "Sak-Lakal Marker", "Yax-Ehb Gate", "Chan-Tok' Stone",
    "Ha'-Nal Crossing", "K'in-Balam Rest", "Witz-Ahau Landing", "Uh-Ek' Marker",
    "Ik'-Chan Gate", "Kab'-Muul Stone", "Nah-Ha' Crossing", "Ox-Balam Rest",
    "Tzuk-Nal Landing", "Chich'en Marker", "Uxmal-Nah Gate", "Mayapan Stone",
    "Edzna Crossing", "Becan Rest", "Xpuhil Landing", "Cerros Marker",
]

NETHER_LANG_RUIN = [
    "Grukk-Vhal Landing", "Zol-Thrak Gate", "Ghol-Mor Crossing", "Skar-Dhur Rest",
    "Krath-Ul Stone", "Vrak-Ashun Toll", "Khaz-Gulok Marker", "Dhur-Zathan Span",
    "Morgh-Thul Rest", "Thrakk-Ashgul Gate", "Ulgor-Skath Landing", "Vhal-Krum Ford",
]
NETHER_LANG_WILD = [
    "Zathrak Gate", "Ghulmor Rest", "Skarvhal Crossing", "Dhurgul Stone",
    "Krathum Landing", "Vrakash Toll", "Khazdur Marker", "Morthak Span",
    "Thulgor Rest", "Ulskar Gate", "Ashgrukk Landing", "Vhalzoth Ford",
]
END_LANG_RUIN = [
    "Vel'thae Rest", "Ssiath Gate", "Ilu'un Crossing", "Aeth-Nyx Stone",
    "Ol'thess Landing", "Quss-Xil Marker", "Ythir Rest", "Eir-Sha'al Gate",
    "Th'ess-Vael Crossing", "Nyx-Ilu Stone", "Xil'aeth Landing", "Sha'quss Marker",
]
END_LANG_WILD = [
    "Vaelith Rest", "Ssira'un Gate", "Ilthae Crossing", "Nyxol Stone",
    "Aethquss Landing", "Oleir Marker", "Xilyth Rest", "Thessa'al Gate",
    "Eirvel Crossing", "Qussith Stone", "Ythsha Landing", "Un'aeth Marker",
]

EGYPTIAN_RUIN = EGYPTIAN_RUIN + EGYPTIAN_LANG_RUIN
EGYPTIAN_WILD = EGYPTIAN_WILD + EGYPTIAN_LANG_WILD
GREEK_RUIN = GREEK_RUIN + GREEK_LANG_RUIN
GREEK_WILD = GREEK_WILD + GREEK_LANG_WILD
BABYLONIAN_RUIN = BABYLONIAN_RUIN + BABYLONIAN_LANG_RUIN
BABYLONIAN_WILD = BABYLONIAN_WILD + BABYLONIAN_LANG_WILD
NORSE_CELTIC_RUIN = NORSE_RUIN + NORSE_LANG_RUIN + CELTIC_RUIN + CELTIC_LANG_RUIN
NORSE_CELTIC_WILD = NORSE_CELTIC_WILD + NORSE_CELTIC_LANG_WILD
MAYAN_RUIN = MAYAN_RUIN + MAYAN_LANG_RUIN
MAYAN_WILD = MAYAN_WILD + MAYAN_LANG_WILD
NETHER_RUIN = NETHER_RUIN + NETHER_LANG_RUIN
NETHER_WILD = NETHER_WILD + NETHER_LANG_WILD
END_RUIN = END_RUIN + END_LANG_RUIN
END_WILD = END_WILD + END_LANG_WILD

ORIGIN = ["The First Waystone"]

# key -> (structure tag under waystone_ruins:, Java field name, ruin list, wild list)
# Tag ids are frozen: "school_viking" stays the tag for the Norse & Celtic school
# because shipped structure JSON already references it.
CULTURES = {
    "egyptian":     ("school_egyptian", "EGYPTIAN",     EGYPTIAN_RUIN,     EGYPTIAN_WILD),
    "greek":        ("school_greek",    "GREEK",        GREEK_RUIN,        GREEK_WILD),
    "babylonian":   ("school_babylon",  "BABYLONIAN",   BABYLONIAN_RUIN,   BABYLONIAN_WILD),
    "norse_celtic": ("school_viking",   "NORSE_CELTIC", NORSE_CELTIC_RUIN, NORSE_CELTIC_WILD),
    "mayan":        ("school_mayan",    "MAYAN",        MAYAN_RUIN,        MAYAN_WILD),
    "nether":       ("theme_nether",    "NETHER",       NETHER_RUIN,       NETHER_WILD),
    "end":          ("theme_end",       "END",          END_RUIN,          END_WILD),
}


def wild_pool():
    """The config pool: lore, antiquity and every culture's wild list,
    interleaved round-robin so any prefix of the list is already mixed."""
    columns = [LORE, ANTIQUITY] + [wild for _, _, _, wild in CULTURES.values()]
    out = []
    for i in range(max(len(c) for c in columns)):
        for c in columns:
            if i < len(c):
                out.append(c[i])
    return out


def all_names():
    out = list(LORE) + list(ANTIQUITY) + list(ORIGIN)
    for _, _, ruin, wild in CULTURES.values():
        out += list(ruin) + list(wild)
    return out


def _validate():
    names = all_names()
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, f"duplicate names: {dupes}"
    for n in names:
        assert '"' not in n and "\\" not in n and n == n.strip(), repr(n)
    for key, (_, _, ruin, wild) in CULTURES.items():
        assert not set(ruin) & set(wild), key


_validate()

if __name__ == "__main__":
    print(f"lore {len(LORE)}  antiquity {len(ANTIQUITY)}")
    for key, (tag, _, ruin, wild) in CULTURES.items():
        print(f"{key:13} tag={tag:16} ruin={len(ruin):3} wild={len(wild):3}")
    print(f"config pool: {len(wild_pool())}   companion: "
          f"{sum(len(r) for _, _, r, _ in CULTURES.values()) + len(ORIGIN)}   "
          f"total curated: {len(all_names())}")
