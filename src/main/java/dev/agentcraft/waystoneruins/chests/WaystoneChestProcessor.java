package dev.agentcraft.waystoneruins.chests;

import com.mojang.serialization.Codec;
import dev.agentcraft.waystoneruins.VoyageConfig;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureProcessor;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureProcessorType;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;

/**
 * Bons Voyage 1.20.0: the optional chest beside each ruin's waystone (config waystone_chests.enabled, default off).
 *
 * The generator authors the chest into every waystone template with the marker loot table
 * waystone_ruins:chests/waystone_chest/[realm], on a cell that held air, a decor block (recorded in WasBlock) or no
 * block at all (WasVoid). This processor runs first in each of those templates' processor lists. Switched off, it
 * returns the cell exactly as it was before 1.20.0: air, the recorded block, or nothing (null drops the voxel, as an
 * absent one is dropped). Switched on, it keeps the chest, removes the two helper tags and gives it one of the realm's
 * configured loot tables, picked from the block position so every chunk of a ruin agrees.
 *
 * SRG: m_7382_ processBlock, m_6953_ getType, f_74675_/f_74676_/f_74677_ StructureBlockInfo pos/state/nbt,
 * m_60713_ BlockState.is, f_50087_ Blocks.CHEST, f_50016_ Blocks.AIR, m_49966_ defaultBlockState,
 * m_128461_ getString, m_128359_ putString, m_128441_ contains, m_128425_ contains(key, type), m_128469_ getCompound,
 * m_128473_ remove, m_6426_ copy, m_247651_ NbtUtils.readBlockState, f_256975_ BuiltInRegistries.BLOCK,
 * m_255303_ asLookup, m_216335_ RandomSource.create(long), m_188503_ nextInt(int), m_14057_ Mth.getSeed(Vec3i).
 */
public final class WaystoneChestProcessor extends StructureProcessor {
    public static final String MARKER = "waystone_ruins:chests/waystone_chest/";
    public static final String WAS_BLOCK = "WasBlock";
    public static final String WAS_VOID = "WasVoid";
    public static final WaystoneChestProcessor INSTANCE = new WaystoneChestProcessor();
    public static final Codec<WaystoneChestProcessor> CODEC = Codec.unit(() -> INSTANCE);
    public static final StructureProcessorType<WaystoneChestProcessor> TYPE = () -> CODEC;

    private WaystoneChestProcessor() {
    }

    @Override
    public StructureTemplate.StructureBlockInfo m_7382_(LevelReader level, BlockPos offset, BlockPos pivot,
                                                        StructureTemplate.StructureBlockInfo raw,
                                                        StructureTemplate.StructureBlockInfo info,
                                                        StructurePlaceSettings settings) {
        CompoundTag nbt = info.f_74677_();
        if (nbt == null || !info.f_74676_().m_60713_(Blocks.f_50087_)) return info;
        String table = nbt.m_128461_("LootTable");
        if (!table.startsWith(MARKER)) return info;
        if (!VoyageConfig.waystoneChests()) {
            if (nbt.m_128441_(WAS_VOID)) return null;
            BlockState was = nbt.m_128425_(WAS_BLOCK, 10)
                    ? NbtUtils.m_247651_(BuiltInRegistries.f_256975_.m_255303_(), nbt.m_128469_(WAS_BLOCK))
                    : Blocks.f_50016_.m_49966_();
            return new StructureTemplate.StructureBlockInfo(info.f_74675_(), was, null);
        }
        CompoundTag chest = nbt.m_6426_();
        chest.m_128473_(WAS_BLOCK);
        chest.m_128473_(WAS_VOID);
        List<String> tables = VoyageConfig.chestLoot(table.substring(MARKER.length()));
        if (!tables.isEmpty()) {
            RandomSource random = RandomSource.m_216335_(Mth.m_14057_(info.f_74675_()));
            chest.m_128359_("LootTable", tables.get(random.m_188503_(tables.size())));
        }
        return new StructureTemplate.StructureBlockInfo(info.f_74675_(), info.f_74676_(), chest);
    }

    @Override
    protected StructureProcessorType<?> m_6953_() {
        return TYPE;
    }
}
