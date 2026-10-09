package dev.agentcraft.waystoneruins.claims;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.levelgen.structure.placement.StructurePlacementType;
import net.minecraftforge.event.level.LevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegisterEvent;

/** Registers waystone_ruins:claimed_spread (SRG f_256888_ = Registries.STRUCTURE_PLACEMENT, m_205049_ = codec). */
@Mod.EventBusSubscriber(modid = "waystone_ruins", bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ClaimsSetup {
    private ClaimsSetup() {
    }

    public static final StructurePlacementType<ClaimedSpread> TYPE = () -> ClaimedSpread.CODEC;

    @SubscribeEvent
    public static void register(RegisterEvent event) {
        event.register(Registries.f_256888_, helper ->
                helper.register(new ResourceLocation("waystone_ruins", "claimed_spread"), TYPE));
    }

    /** Each server level's generator state gets its claim context when the level loads (before any chunk). */
    @Mod.EventBusSubscriber(modid = "waystone_ruins", bus = Mod.EventBusSubscriber.Bus.FORGE)
    public static final class Levels {
        private Levels() {
        }

        @SubscribeEvent
        public static void load(LevelEvent.Load event) {
            if (event.getLevel() instanceof ServerLevel level) Claims.attach(level);
        }

        @SubscribeEvent
        public static void unload(LevelEvent.Unload event) {
            if (event.getLevel() instanceof ServerLevel level) Claims.detach(level);
        }
    }
}
