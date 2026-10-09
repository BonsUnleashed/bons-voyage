package dev.agentcraft.waystoneruins.claims;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.ChunkGeneratorStructureState;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;

/**
 * The claim rule of {@link ClaimedSpread}, evaluated per dimension.
 *
 * blocked(S, c): some set T of S's claim group outranks S and generates at one of its own candidate chunks within
 * S's radius of c. generates(T, t) = T's placement accepts t (vanilla checks + T's own claims, recursively; the
 * recursion only climbs to strictly higher-ranked sets, so it ends) and one of T's structures fits there (biome
 * check, then Lithostitched's site condition: Structure#findValidGenerationPoint, as ChunkGenerator does).
 * Everything is a pure function of seed and terrain noise: no chunk is loaded, nothing depends on generation order
 * or thread timing, and the cache only memoises. Structurify's own checks inside tryGenerateStructure (flatness,
 * overlap claims) are not consulted, so a higher-ranked candidate that only Structurify rejects still claims its
 * area (rare; measured 2 of 21 in the 1.19.1 rig's real-generation box).
 *
 * SRG: m_7726_ getChunkSource, m_255415_ getGeneratorState, m_8481_ getGenerator, m_62218_ getBiomeSource,
 * m_214994_ randomState, m_9598_ registryAccess, m_7654_ getServer, m_236738_ getStructureManager, m_7328_ getSeed,
 * m_175515_ registryOrThrow, m_6579_ entrySet, m_135782_ location, f_210004_/f_210003_ StructureSet placement/
 * structures, f_210026_ entry structure, m_203334_ value, m_227008_ getPotentialStructureChunk, m_226559_ biomes,
 * m_203333_ HolderSet.contains, m_262864_ findValidGenerationPoint, f_45578_/f_45579_ ChunkPos x/z.
 */
public final class Claims {
    private Claims() {
    }

    private static final int CACHE_MAX = 200_000;

    private record Member(int index, ClaimedSpread placement, String id, ClaimedSpread.Claim claim,
                          List<Structure> structures) {
    }

    private record Key(int member, int x, int z) {
    }

    private static final class Ctx {
        final ServerLevel level;
        final ChunkGenerator generator;
        final BiomeSource biomes;
        final RandomState randomState;
        final RegistryAccess registries;
        final StructureTemplateManager templates;
        final long seed;
        final ChunkGeneratorStructureState state;
        final List<Member> members = new ArrayList<>();
        final Map<ClaimedSpread, Member> byPlacement = new HashMap<>();
        final ConcurrentHashMap<Key, Boolean> cache = new ConcurrentHashMap<>();

        Ctx(ServerLevel level) {
            var source = level.m_7726_();
            this.level = level;
            this.state = source.m_255415_();
            this.generator = source.m_8481_();
            this.biomes = generator.m_62218_();
            this.randomState = source.m_214994_();
            this.registries = level.m_9598_();
            this.templates = level.m_7654_().m_236738_();
            this.seed = level.m_7328_();
        }
    }

    private static final Map<ChunkGeneratorStructureState, Ctx> CONTEXTS = new ConcurrentHashMap<>();

    static void attach(ServerLevel level) {
        Ctx ctx = new Ctx(level);
        var sets = new ArrayList<>(ctx.registries.m_175515_(Registries.f_256998_).m_6579_());
        sets.sort(Comparator.comparing(e -> e.getKey().m_135782_().toString()));
        for (var e : sets) {
            StructureSet set = e.getValue();
            if (set.f_210004_() instanceof ClaimedSpread placement) {
                List<Structure> structures = new ArrayList<>();
                for (var entry : set.f_210003_()) structures.add(entry.f_210026_().m_203334_());
                Member m = new Member(ctx.members.size(), placement, e.getKey().m_135782_().toString(),
                        placement.claim(), List.copyOf(structures));
                ctx.members.add(m);
                ctx.byPlacement.put(placement, m);
            }
        }
        CONTEXTS.put(ctx.state, ctx);
        if (!ctx.members.isEmpty() && level.m_46472_() == net.minecraft.world.level.Level.f_46428_) {
            Map<String, Integer> sizes = new java.util.TreeMap<>(groupSizes(ctx.state));
            org.apache.logging.log4j.LogManager.getLogger("Bons Voyage").info(
                    "Bons Voyage placement claims active: {} claimed structure sets, groups {}", ctx.members.size(), sizes);
        }
    }

    static void detach(ServerLevel level) {
        CONTEXTS.remove(level.m_7726_().m_255415_());
    }

    /** Members of each claim group in this dimension, for diagnostics. */
    public static Map<String, Integer> groupSizes(ChunkGeneratorStructureState state) {
        Map<String, Integer> out = new HashMap<>();
        Ctx ctx = CONTEXTS.get(state);
        if (ctx != null) for (Member m : ctx.members) out.merge(m.claim().group(), 1, Integer::sum);
        return out;
    }

    static boolean blocked(ClaimedSpread self, ChunkGeneratorStructureState state, int x, int z) {
        Ctx ctx = CONTEXTS.get(state);
        if (ctx == null) return false;                       // not a server level's own generator state
        Member me = ctx.byPlacement.get(self);
        if (me == null || me.claim().radius() <= 0) return false;
        int r = me.claim().radius();
        long r2 = (long) r * r;
        for (Member m : ctx.members) {
            if (m == me || !m.claim().group().equals(me.claim().group()) || !outranks(m, me)) continue;
            int s = m.placement().m_205003_();
            for (int i = Math.floorDiv(x - r, s); i <= Math.floorDiv(x + r, s); i++) {
                for (int j = Math.floorDiv(z - r, s); j <= Math.floorDiv(z + r, s); j++) {
                    ChunkPos c = m.placement().m_227008_(ctx.seed, i * s, j * s);
                    long dx = c.f_45578_ - x, dz = c.f_45579_ - z;
                    if (dx * dx + dz * dz <= r2 && generates(ctx, m, c.f_45578_, c.f_45579_)) return true;
                }
            }
        }
        return false;
    }

    private static boolean outranks(Member a, Member b) {
        int ra = a.claim().rank(), rb = b.claim().rank();
        return ra != rb ? ra > rb : a.id().compareTo(b.id()) < 0;
    }

    private static boolean generates(Ctx ctx, Member m, int x, int z) {
        Key key = new Key(m.index(), x, z);
        Boolean known = ctx.cache.get(key);
        if (known != null) return known;
        boolean result = m.placement().m_255071_(ctx.state, x, z) && fits(ctx, m, x, z);
        if (ctx.cache.size() > CACHE_MAX) ctx.cache.clear();
        ctx.cache.put(key, result);
        return result;
    }

    private static boolean fits(Ctx ctx, Member m, int x, int z) {
        ChunkPos pos = new ChunkPos(x, z);
        for (Structure s : m.structures()) {
            var context = new Structure.GenerationContext(ctx.registries, ctx.generator, ctx.biomes, ctx.randomState,
                    ctx.templates, ctx.seed, pos, ctx.level, s.m_226559_()::m_203333_);
            if (s.m_262864_(context).isPresent()) return true;
        }
        return false;
    }
}
