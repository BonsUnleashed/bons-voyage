package dev.agentcraft.waystoneruins.protect;

import dev.agentcraft.waystoneruins.VoyageConfig;
import dev.worldgen.lithostitched.worldgen.structure.DelegatingStructure;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.Set;
import net.blay09.mods.waystones.api.WaystoneOrigin;
import net.blay09.mods.waystones.block.WaystoneBlockBase;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraftforge.event.entity.living.LivingDestroyBlockEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Bons Voyage 1.20.0: the waystone of a ruin cannot be broken (server config waystones.unbreakable, default on).
 *
 * Since 1.20.0 the ruins generate their stones with origin=dungeon. That block state reaches the client, so client
 * and server both refuse the dig (no crack, no break-and-reappear), the same way Waystones' own
 * generatedWaystonesUnbreakable does. Stones of ruins generated before 1.20.0 carry origin=wilderness; the server
 * protects those when they stand inside a Bons Voyage structure piece. Creative players may still break them, as
 * with Waystones; player-placed stones (origin=player) are never protected.
 *
 * SRG: m_150110_ getAbilities, f_35937_ instabuild, m_9236_ Entity.level, m_8055_ getBlockState, m_60734_ getBlock,
 * m_61138_ hasProperty, m_61143_ getValue, m_215010_ structureManager, m_220477_ startsForStructure(ChunkPos,
 * Predicate), m_220497_ structureHasPieceAt, m_73603_ StructureStart.isValid, m_9598_ registryAccess,
 * m_175515_ registryOrThrow, f_256944_ Registries.STRUCTURE, m_6579_ entrySet, m_135782_ location,
 * m_135827_ getNamespace.
 */
@Mod.EventBusSubscriber(modid = "waystone_ruins", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class WaystoneProtection {
    private WaystoneProtection() {
    }

    @SubscribeEvent
    public static void breakSpeed(PlayerEvent.BreakSpeed event) {
        Player player = event.getEntity();
        if (player.m_150110_().f_35937_) return;
        BlockPos pos = event.getPosition().orElse(null);
        if (pos != null && isProtected(player.m_9236_(), pos, event.getState())) event.setCanceled(true);
    }

    /** Covers machines and fake players too, which destroy without digging. */
    @SubscribeEvent
    public static void blockBreak(BlockEvent.BreakEvent event) {
        Player player = event.getPlayer();
        if (player != null && player.m_150110_().f_35937_) return;
        if (isProtected(event.getLevel(), event.getPos(), event.getState())) event.setCanceled(true);
    }

    /** Withers and the ender dragon. */
    @SubscribeEvent
    public static void mobGrief(LivingDestroyBlockEvent event) {
        if (isProtected(event.getEntity().m_9236_(), event.getPos(), event.getState())) event.setCanceled(true);
    }

    /** Waystones resist 2000; this only matters for modded blasts that ignore resistance. */
    @SubscribeEvent
    public static void explosion(ExplosionEvent.Detonate event) {
        Level level = event.getLevel();
        event.getAffectedBlocks().removeIf(p -> isProtected(level, p, level.m_8055_(p)));
    }

    public static boolean isProtected(LevelAccessor level, BlockPos pos, BlockState state) {
        if (!(state.m_60734_() instanceof WaystoneBlockBase) || !state.m_61138_(WaystoneBlockBase.ORIGIN)) return false;
        if (!VoyageConfig.unbreakableWaystones()) return false;
        WaystoneOrigin origin = state.m_61143_(WaystoneBlockBase.ORIGIN);
        if (origin == WaystoneOrigin.DUNGEON) return true;
        return origin == WaystoneOrigin.WILDERNESS && level instanceof ServerLevel server && insideRuin(server, pos);
    }

    private static Object cachedRegistry;
    private static Set<Structure> ruins = Set.of();

    /** Every Bons Voyage structure, as registered and as Lithostitched's delegate (chunk references can hold either). */
    private static synchronized Set<Structure> ruins(ServerLevel level) {
        var registry = level.m_9598_().m_175515_(Registries.f_256944_);
        if (registry != cachedRegistry) {
            Set<Structure> found = Collections.newSetFromMap(new IdentityHashMap<>());
            for (var e : registry.m_6579_()) {
                if (!"waystone_ruins".equals(e.getKey().m_135782_().m_135827_())) continue;
                Structure s = e.getValue();
                found.add(s);
                while (s instanceof DelegatingStructure wrapped) {
                    s = wrapped.delegate();
                    found.add(s);
                }
            }
            ruins = found;
            cachedRegistry = registry;
        }
        return ruins;
    }

    static boolean insideRuin(ServerLevel level, BlockPos pos) {
        Set<Structure> ours = ruins(level);
        if (ours.isEmpty()) return false;
        var manager = level.m_215010_();
        for (StructureStart start : manager.m_220477_(new ChunkPos(pos), ours::contains)) {
            if (start.m_73603_() && manager.m_220497_(pos, start)) return true;
        }
        return false;
    }
}
