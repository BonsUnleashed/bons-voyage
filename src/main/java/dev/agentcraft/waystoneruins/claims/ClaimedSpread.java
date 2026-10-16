package dev.agentcraft.waystoneruins.claims;

import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.agentcraft.waystoneruins.VoyageConfig;
import java.util.Optional;
import net.minecraft.core.Vec3i;
import net.minecraft.world.level.chunk.ChunkGeneratorStructureState;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadType;
import net.minecraft.world.level.levelgen.structure.placement.StructurePlacement;
import net.minecraft.world.level.levelgen.structure.placement.StructurePlacementType;

/**
 * Bons Voyage 1.19.1: vanilla random_spread plus a claim. A candidate chunk is refused when a structure set of the
 * same claim group that outranks this one (higher rank, ties by set id) generates a ruin within `radius` chunks of it
 * (candidate chunk to candidate chunk). Ruins of different sets therefore never share a site, while every set keeps
 * its own grid, spacing (Structurify overrides still apply: spacing(), separation() and getPotentialStructureChunk are
 * inherited), exclusion zone and weights. See {@link Claims}.
 *
 * 1.20.0: config worldgen.spacing_multiplier scales spacing, separation and the claim radius here, once, when the set
 * is decoded. The scaled values go into the inherited fields, so Structurify's hooks still act on top of them (its
 * per-set overrides replace them, its global modifier multiplies them). The codec keeps writing the authored values.
 *
 * Minecraft is referenced by SRG name (production mappings, Forge 1.20.1):
 *   m_227041_ StructurePlacement.placementCodec   m_255071_ StructurePlacement.isStructureChunk
 *   m_203443_ StructurePlacement.type              m_205003_/m_205004_/m_205005_ spacing/separation/spreadType
 *   f_205014_ RandomSpreadType.CODEC
 */
public class ClaimedSpread extends RandomSpreadStructurePlacement {

    /** group: realm whose ruins may not share a site; rank: higher wins; radius: chunks, centre to centre. */
    public record Claim(String group, int rank, int radius) {
        public static final Codec<Claim> CODEC = RecordCodecBuilder.create(i -> i.group(
                Codec.STRING.fieldOf("group").forGetter(Claim::group),
                Codec.INT.fieldOf("rank").forGetter(Claim::rank),
                Codec.intRange(0, 64).fieldOf("radius").forGetter(Claim::radius)).apply(i, Claim::new));
    }

    // Vanilla's five base fields + spacing, separation, claim (DFU's P5 combines with at most three more fields, so
    // spread_type is not a field here: Bons Voyage sets are all linear). The validation must stay on the MapCodec:
    // StructurePlacement.CODEC is a key dispatch that inlines a type's fields only for a map-based codec; a plain
    // Codec (e.g. after Codec#comapFlatMap) makes it look for a separate "value" object ("Not a JSON object: null").
    public static final Codec<ClaimedSpread> CODEC = RecordCodecBuilder.<ClaimedSpread>mapCodec(i -> m_227041_(i)
            .and(i.group(
                    Codec.intRange(0, 4096).fieldOf("spacing").forGetter(ClaimedSpread::authoredSpacing),
                    Codec.intRange(0, 4096).fieldOf("separation").forGetter(ClaimedSpread::authoredSeparation),
                    Claim.CODEC.fieldOf("claim").forGetter(ClaimedSpread::claim)))
            .apply(i, ClaimedSpread::new))
            .flatXmap(c -> c.authoredSpacing() <= c.authoredSeparation()
                    ? DataResult.<ClaimedSpread>error(() -> "Spacing has to be larger than separation")
                    : DataResult.success(c), DataResult::success)
            .codec();

    private final Claim claim;
    private final int authoredSpacing;
    private final int authoredSeparation;
    private final int claimRadius;

    public ClaimedSpread(Vec3i locateOffset, StructurePlacement.FrequencyReductionMethod frequencyReductionMethod,
                         float frequency, int salt, Optional<StructurePlacement.ExclusionZone> exclusionZone,
                         int spacing, int separation, Claim claim) {
        this(locateOffset, frequencyReductionMethod, frequency, salt, exclusionZone, spacing, separation, claim,
                VoyageConfig.spacingMultiplier());
    }

    private ClaimedSpread(Vec3i locateOffset, StructurePlacement.FrequencyReductionMethod frequencyReductionMethod,
                          float frequency, int salt, Optional<StructurePlacement.ExclusionZone> exclusionZone,
                          int spacing, int separation, Claim claim, double scale) {
        super(locateOffset, frequencyReductionMethod, frequency, salt, exclusionZone, scaledSpacing(spacing, scale),
                scaledSeparation(spacing, separation, scale), RandomSpreadType.LINEAR);
        this.claim = claim;
        this.authoredSpacing = spacing;
        this.authoredSeparation = separation;
        this.claimRadius = Math.min(64, (int) Math.round(claim.radius() * scale));
    }

    private static int scaledSpacing(int spacing, double scale) {
        return scale == 1.0 ? spacing : Math.max(2, (int) Math.round(spacing * scale));
    }

    /** Always at least one below the scaled spacing: random_spread draws an offset in [0, spacing - separation). */
    private static int scaledSeparation(int spacing, int separation, double scale) {
        if (scale == 1.0) return separation;
        return Math.max(0, Math.min(scaledSpacing(spacing, scale) - 1, (int) Math.round(separation * scale)));
    }

    public Claim claim() {
        return claim;
    }

    public int authoredSpacing() {
        return authoredSpacing;
    }

    public int authoredSeparation() {
        return authoredSeparation;
    }

    /** The claim radius in chunks after worldgen.spacing_multiplier. */
    public int claimRadius() {
        return claimRadius;
    }

    @Override
    public boolean m_255071_(ChunkGeneratorStructureState state, int x, int z) {
        return super.m_255071_(state, x, z) && !Claims.blocked(this, state, x, z);
    }

    @Override
    public StructurePlacementType<?> m_203443_() {
        return ClaimsSetup.TYPE;
    }
}
