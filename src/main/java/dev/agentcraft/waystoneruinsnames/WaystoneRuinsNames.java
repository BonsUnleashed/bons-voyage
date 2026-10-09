package dev.agentcraft.waystoneruinsnames;

import net.blay09.mods.balm.api.Balm;
import dev.worldgen.lithostitched.worldgen.structure.DelegatingStructure;
import net.blay09.mods.waystones.api.GenerateWaystoneNameEvent;
import net.blay09.mods.waystones.api.IWaystone;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Names wild waystones after the Waybuilder school whose ruin they stand in.
 * Fires on Waystones' GenerateWaystoneNameEvent (Balm event bus); if the
 * waystone is not inside any waystone_ruins structure, the event is left
 * untouched and normal Waystones naming applies.
 *
 * MC internals are invoked via SRG names (production mappings, Forge 1.20.1):
 *   m_129880_ = MinecraftServer.getLevel
 *   m_215010_ = ServerLevel.structureManager
 *   m_220491_ = StructureManager.getStructureWithPieceAt(BlockPos, TagKey)
 *   m_73603_  = StructureStart.isValid
 *   m_203882_ = TagKey.create
 *   m_135788_ = ResourceKey.createRegistryKey
 */
@Mod("waystone_ruins")
public class WaystoneRuinsNames {

    private static final ResourceKey<net.minecraft.core.Registry<Structure>> STRUCTURE_REGISTRY =
            ResourceKey.m_135788_(new ResourceLocation("minecraft", "worldgen/structure"));

    private static final String[] EGYPTIAN = { "The Pharaoh's Waygate", "Rest of the Golden Scarab", "The Obelisk Road", "Shrine of the Setting Sun", "The Ferryman's Toll", "Gate of Two Horizons", "The Sandworn Sphinx", "Court of the Ibis", "The Painted Tomb", "Threshold of Reeds", "The Canopic Vault", "Way of the Jackal", "Sekh-Amara", "Ankh-Neferu", "Djed-Hotep's Rest", "Khet-Nubara", "The Steps of Ausar", "Meret-Sokar", "Path of Khepri", "Wadj-Halla", "Setep-Ra's Landing", "Naqada Stone", "Iunu Crossing", "Heka-Sematawy", "Waset Landing", "Ipet-Sut Gate", "Nekhen Stone", "Khmun Crossing", "Ta-Mery Rest", "Shedet Ford", "Zawty Marker", "Nubt-Seshat", "Maat-Kheru Toll", "Hut-Waret Gate", "Sau-Neith Stone", "Behdet Landing", "Iunet-Hathor", "Gebtu Crossing", "Tjenu Rest", "Nekheb Stair", "Pa-Sekhem", "Kha-Merut Toll", "Ren-Ankhet", "Djoser-Nub Marker", "Seshen-Ra Landing", "Tawy-Hekat", "Amun-Weset Gate", "Ipu-Min Stone" };
    private static final String[] GREEK = { "The Marble Tholos", "Oracle of the Cherry Grove", "The Broken Agora", "Landing of a Thousand Ships", "The Olive Gate", "Stair of the Muses", "The Laurel Crossing", "Temple of the Western Wind", "The Amphora Rest", "Colonnade's End", "The Shepherd King's Seat", "Harbor of Heroes", "Tholos of Argeia", "Delphikon", "Naxopolis Gate", "Kythera Stone", "The Argonaut's Anchor", "Petralonia", "Stoa of Lysandros", "Thermon Rest", "Akrothea", "Ophellas' Milestone", "Eleutheria Gate", "Kastraki Point", "Kallipolis Gate", "Hieron of Phaidros", "Oreithyia Stone", "Lykosoura", "Panakton Crossing", "Thermopylion Rest", "Anthedon Landing", "Kyparissia Stone", "Melanthos' Milestone", "Pleuron Gate", "Aigosthena Point", "Demetrias Crossing", "Oinoe Rest", "Halieis Landing", "Tegyra Stone", "Kleitor Gate", "Stymphalos Crossing", "Psophis Marker", "Thyrea Rest", "Alalkomenai", "Eutresis Stone", "Skillous Gate", "Lepreon Landing", "Phigaleia" };
    private static final String[] BABYLONIAN = { "The Sunken Ziggurat", "Gate of the Lion Frieze", "The Glazed Blue Gate", "Hanging Garden's Rest", "The Cuneiform Stone", "Court of the Star-Readers", "The Bitumen Road", "Tower of the Seven Tiers", "The Euphrat Ford", "Seat of the Sky Scribe", "The Clay Tablet Toll", "Walls of the First City", "Nabu-Etemen", "Etemenanki's Shadow", "Ishtar-Kalla", "Marduk's Waymark", "Bab-Ilim Crossing", "Sin-Ahara", "Uruk's Last Gate", "Nippur Stone", "Tiamat's Rest", "Enlil-Zakar", "Akkad-Nur", "Zigg-Aratta", "Dur-Kurigal Gate", "Kutha-Nergal Stone", "Dilbat Crossing", "Isin-Gula Rest", "Girsu Marker", "Umma-Shara Landing", "Adab Stone", "Shuruppak Ford", "Bad-Tibira Gate", "Akshak Crossing", "Mari-Zimri Rest", "Eshnunna Stone", "Der-Ishtaran Toll", "Upi Landing", "Kar-Nabu Gate", "Bit-Adini Marker", "Nusku-Ibni Rest", "Zababa-Iddin Crossing", "Ninurta-Apla Stone", "Adad-Nirari Gate", "Ea-Nasir's Toll", "Ibbi-Sin Landing", "Rim-Sin Marker", "Hammurapi's Stone" };
    private static final String[] NORSE_CELTIC = { "The Longship's Landing", "Runestone of the North Sea", "The Mead Hall Marker", "Fjordwatch", "The Whalebone Arch", "Shieldwall Rest", "The Frost-Braided Gate", "Cairn of the Nine Winters", "The Wolfpelt Camp", "Saga Stone", "The Ice-Bound Wharf", "Hall of the Salt Wind", "Jarnvik Stone", "Skjoldheim", "Ulfgard Crossing", "Hrafnastad", "Vestrfjord Toll", "Eiriksmark", "Thorvald's Rest", "Ymirfell", "Draugholt", "Solvang Gate", "Kolgrim's Cairn", "Nordrvegr", "Bjornsvik", "Sigurdheim", "Hakonsgard", "Leifsnes", "Ragnarsholt Crossing", "Olafsby Stone", "Gunnhildsvang", "Astridsdal Rest", "Freydisfjord", "Helgafell Gate", "Torsteinsmark", "Egilsnes Toll", "Snorrastad", "Grimsnes Stone", "Ketilsberg Crossing", "Hallvardsholm", "Ivarsdal Rest", "Rolfsund Gate", "Svensfoss Marker", "Tokesvatn", "Arnesheim Crossing", "Vidarslund", "Yngvarshamar Rest", "Eyvindseyri", "The Standing Stones", "Rest of the Ninth Wave", "The Ogham Stone", "Gate of the Hazel Grove", "The Rowan Ford", "Cairn of the Three Sisters", "The Dolmen Road", "Shrine of the Salmon Pool", "The Torc Marker", "Way of the Wren", "The Cauldron Seat", "The Mistbound Rath", "Dun Brannoc", "Caer Lludd", "Rath Fionnan", "Lios na Greine", "Inis Ceol", "Bryn Ysgeir", "Carreg Dhu", "Aber Tywi Crossing", "Cill Ronan's Rest", "Tor Maen", "Dun Scaith", "Pen Gwyn Stone", "Dun Conall", "Rath Niamh", "Caer Deirdre", "Lios Aoife", "Cnoc Ciarain Stone", "Achadh Eogain", "Baile Brain Crossing", "Tobar Brighde", "Druim Lugha Rest", "Mag Nuadat", "Sliabh Macha Gate", "Beann Medbha", "Llan Fergus Marker", "Nant Cormac", "Cwm Ailill Rest", "Coed Gwydion", "Pant Rhiannon Crossing", "Mynydd Arianrhod", "Ynys Owain Stone", "Bod Taliesin", "Tre Ceridwen Gate", "Kil Bedwyr Toll", "Bal Elffin Landing", "Caer Cai" };
    private static final String[] MAYAN = { "Temple of the Feathered Way", "The Jade Stair", "Altar of the Howler Kings", "The Vine-Choked Pyramid", "Court of the Ballgame", "The Cenote Shrine", "Stone of the Long Count", "The Obsidian Butterfly", "The Smoking Mirror Gate", "Rest of the Maize God", "The Stelae Field", "Crossing of the Sacred Ceiba", "Yaxha'kul", "Itzam-Naab", "Chak-Balam Rest", "K'inich Gate", "Xibal-Ha Door", "Tikal-Muul", "Nakum Stone", "Copan-Witz", "Zac-Nicte Crossing", "Ah-Puch's Toll", "Uxben Waymark", "Kukul-Chan's Seat", "Yax-K'uk' Gate", "Sak-Witz Stone", "Ik'-Nah Crossing", "Bolon-Tun Rest", "Chan-Ha' Landing", "Ox-Witza Marker", "Sa'al Gate", "Uaxac-Tun Stone", "Lamanai Crossing", "Altun-Ha Rest", "Dzibanche Landing", "Kohunlich Marker", "Xaman-Ek' Gate", "Nohol-Kab' Stone", "Lakin-K'in Crossing", "Chikin-Uh Rest", "Ho'-Balam Landing", "Uuk-Chan Marker", "Waxak-Nal Gate", "Lahun-Ahau Stone", "Yaxchilan Crossing", "Po'-Tonina Rest", "Seibal Landing", "K'uk'-Mo' Marker" };
    private static final String[] NETHER = { "The Soul Forge Landing", "Vault of Burning Bone", "The Basalt Span", "Bridge of the Crimson Deep", "The Weeping Obsidian Gate", "Ashgate of the Under-Road", "Ghast-Song Rest", "The Molten Milestone", "Netherrack Nave", "The Sulfur Court", "Piglin's Bane Crossing", "The Cinder Ferry", "Grukk-Vhal Landing", "Zol-Thrak Gate", "Ghol-Mor Crossing", "Skar-Dhur Rest", "Krath-Ul Stone", "Vrak-Ashun Toll", "Khaz-Gulok Marker", "Dhur-Zathan Span", "Morgh-Thul Rest", "Thrakk-Ashgul Gate", "Ulgor-Skath Landing", "Vhal-Krum Ford" };
    private static final String[] END = { "The Chorus Rest", "Gate at the World's End", "The Void-Touched Plinth", "Ender Pilgrim's Stone", "The Purpur Vault", "Levitant Steps", "The Shulker's Toll", "Isle of the Silent Flight", "The Dragon's Wake Gate", "The Starless Crossing", "Obsidian Pillar Rest", "The Endstone Causeway", "Vel'thae Rest", "Ssiath Gate", "Ilu'un Crossing", "Aeth-Nyx Stone", "Ol'thess Landing", "Quss-Xil Marker", "Ythir Rest", "Eir-Sha'al Gate", "Th'ess-Vael Crossing", "Nyx-Ilu Stone", "Xil'aeth Landing", "Sha'quss Marker" };
    private static final String[] ORIGIN = { "The First Waystone" };

    private final Map<TagKey<Structure>, String[]> cultures = new LinkedHashMap<>();
    private final Set<String> usedNames = ConcurrentHashMap.newKeySet();
    private final Map<String, Integer> reuseCount = new ConcurrentHashMap<>();
    private final Random random = new Random();

    public WaystoneRuinsNames() {
        register("school_egyptian", EGYPTIAN);
        register("school_greek", GREEK);
        register("school_babylon", BABYLONIAN);
        register("school_viking", NORSE_CELTIC);
        register("school_mayan", MAYAN);
        register("theme_nether", NETHER);
        register("theme_end", END);
        register("the_origin", ORIGIN);
        Balm.getEvents().onEvent(GenerateWaystoneNameEvent.class, this::onGenerateName);
    }

    private void register(String tagPath, String[] names) {
        cultures.put(TagKey.m_203882_(STRUCTURE_REGISTRY,
                new ResourceLocation("waystone_ruins", tagPath)), names);
    }

    private void onGenerateName(GenerateWaystoneNameEvent event) {
        try {
            IWaystone waystone = event.getWaystone();
            MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
            if (server == null) return;
            ServerLevel level = server.m_129880_(waystone.getDimension());
            if (level == null) return;
            BlockPos pos = waystone.getPos();
            for (Map.Entry<TagKey<Structure>, String[]> e : cultures.entrySet()) {
                if (containsCulture(level, pos, e.getKey())) {
                    event.setName(pick(e.getValue()));
                    return;
                }
            }
        } catch (Throwable t) {
            // never break waystone activation over a naming nicety
        }
    }

    private static Structure unwrap(Structure structure) {
        while (structure instanceof DelegatingStructure wrapped) {
            structure = wrapped.delegate();
        }
        return structure;
    }

    private static boolean containsCulture(ServerLevel level, BlockPos pos, TagKey<Structure> tag) {
        var manager = level.m_215010_();
        StructureStart direct = manager.m_220491_(pos, tag);
        if (direct != null && direct.m_73603_()) return true;

        // Lithostitched registers a wrapper, while chunk references can use its
        // delegate. Vanilla's registry-holder tag filter misses that identity.
        // Compare the actual delegates, retaining the exact piece containment test.
        var registry = manager.m_220521_().m_175515_(STRUCTURE_REGISTRY);
        for (var member : registry.m_206058_(tag)) {
            Structure expected = unwrap(member.m_203334_());
            for (StructureStart start : manager.m_220477_(new ChunkPos(pos),
                    structure -> unwrap(structure) == expected)) {
                if (start.m_73603_() && manager.m_220497_(pos, start)) return true;
            }
        }
        return false;
    }

    private synchronized String pick(String[] names) {
        List<String> fresh = new ArrayList<>();
        for (String n : names) {
            if (!usedNames.contains(n)) fresh.add(n);
        }
        String name;
        if (!fresh.isEmpty()) {
            name = fresh.get(random.nextInt(fresh.size()));
        } else {
            String base = names[random.nextInt(names.length)];
            int c = reuseCount.merge(base, 1, Integer::sum) + 1;
            name = base + " " + roman(c);
        }
        usedNames.add(name);
        return name;
    }

    private static String roman(int n) {
        String[] r = {"", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"};
        return n < r.length ? r[n] : "#" + n;
    }
}
