package dev.agentcraft.waystoneruins.chests;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegisterEvent;

/** Registers waystone_ruins:waystone_chest (SRG f_256983_ = Registries.STRUCTURE_PROCESSOR, m_74481_ = codec). */
@Mod.EventBusSubscriber(modid = "waystone_ruins", bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ChestSetup {
    private ChestSetup() {
    }

    @SubscribeEvent
    public static void register(RegisterEvent event) {
        event.register(Registries.f_256983_, helper ->
                helper.register(new ResourceLocation("waystone_ruins", "waystone_chest"), WaystoneChestProcessor.TYPE));
    }
}
