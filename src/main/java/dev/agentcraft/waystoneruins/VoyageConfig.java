package dev.agentcraft.waystoneruins;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.common.ForgeConfigSpec;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.config.ModConfigEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.apache.logging.log4j.LogManager;

/**
 * Bons Voyage 1.20.0 settings.
 *
 * config/bons_voyage-common.toml, read before any world loads:
 *   worldgen.spacing_multiplier  scales every ruin set's spacing, separation and claim radius. It is applied when
 *                                the structure sets are decoded, so Structurify and datapacks still act on top.
 *   waystone_chests.enabled      one chest beside the waystone of every newly generated ruin (default off)
 *   waystone_chests.[realm]      the loot tables such a chest draws from, one picked per chest
 * serverconfig/bons_voyage-server.toml, per world and synced to clients:
 *   waystones.unbreakable        survival players cannot break the waystone of a ruin (default on)
 *
 * Worldgen threads read the volatile snapshots below, never the config objects.
 */
public final class VoyageConfig {
    private VoyageConfig() {
    }

    /** Realm suffix of a template chest's marker loot table -> the vanilla tables a placed chest draws from. */
    public static final Map<String, List<String>> DEFAULT_LOOT = new LinkedHashMap<>();

    static {
        DEFAULT_LOOT.put("surface", List.of("minecraft:chests/simple_dungeon", "minecraft:chests/abandoned_mineshaft",
                "minecraft:chests/ruined_portal"));
        DEFAULT_LOOT.put("underground", List.of("minecraft:chests/simple_dungeon", "minecraft:chests/abandoned_mineshaft"));
        DEFAULT_LOOT.put("water", List.of("minecraft:chests/shipwreck_supply", "minecraft:chests/shipwreck_treasure"));
        DEFAULT_LOOT.put("nether", List.of("minecraft:chests/nether_bridge", "minecraft:chests/ruined_portal"));
        DEFAULT_LOOT.put("end", List.of("minecraft:chests/end_city_treasure"));
    }

    private static final Map<String, String> REALM_COMMENT = Map.of(
            "surface", "Ruins on the surface and half-buried ruins:",
            "underground", "Underground crypts:",
            "water", "Ruins on river beds:",
            "nether", "Nether ruins:",
            "end", "End ruins:");

    private static final ForgeConfigSpec COMMON_SPEC;
    private static final ForgeConfigSpec SERVER_SPEC;
    private static final ForgeConfigSpec.DoubleValue SPACING;
    private static final ForgeConfigSpec.BooleanValue CHESTS;
    private static final Map<String, ForgeConfigSpec.ConfigValue<List<? extends String>>> LOOT = new LinkedHashMap<>();
    private static final ForgeConfigSpec.BooleanValue UNBREAKABLE;

    static {
        ForgeConfigSpec.Builder b = new ForgeConfigSpec.Builder();
        b.comment("World generation. Changes apply to chunks generated after the next world load.").push("worldgen");
        SPACING = b.comment("Distance between Bons Voyage ruins, as a multiplier on the spacing, separation and claim",
                        "radius of every ruin set. 1.0 = the mod's own spacing; 1.5 = about 1.5x as far apart (roughly",
                        "half as many ruins); 0.75 = closer together. Structurify or datapack settings for the same",
                        "structure sets still apply on top of this.")
                .defineInRange("spacing_multiplier", 1.0, 0.25, 4.0);
        b.pop();
        b.comment("One chest with random loot beside the waystone of every newly generated ruin.").push("waystone_chests");
        CHESTS = b.comment("Off by default.").define("enabled", false);
        for (Map.Entry<String, List<String>> e : DEFAULT_LOOT.entrySet()) {
            String[] comment = e.getKey().equals("surface")
                    ? new String[]{"Loot tables a chest draws from; each chest picks one at random. Vanilla chest tables also",
                                   "roll the items other mods add to them. An empty list uses the mod's own table for that realm.",
                                   REALM_COMMENT.get(e.getKey())}
                    : new String[]{REALM_COMMENT.get(e.getKey())};
            List<String> defaults = e.getValue();
            LOOT.put(e.getKey(), b.comment(comment).defineListAllowEmpty(e.getKey(), () -> defaults,
                    o -> o instanceof String s && ResourceLocation.m_135820_(s) != null));
        }
        b.pop();
        COMMON_SPEC = b.build();

        ForgeConfigSpec.Builder s = new ForgeConfigSpec.Builder();
        s.push("waystones");
        UNBREAKABLE = s.comment("Survival players cannot break the waystone of a Bons Voyage ruin (creative mode can).",
                        "Works whatever Waystones' own generatedWaystonesUnbreakable setting says.")
                .define("unbreakable", true);
        s.pop();
        SERVER_SPEC = s.build();
    }

    private static volatile double spacing = 1.0;
    private static volatile boolean chests = false;
    private static volatile Map<String, List<String>> loot = DEFAULT_LOOT;
    // Off until a server config is loaded or synced: a client never protects a stone its server does not protect.
    private static volatile boolean unbreakable = false;

    public static void register() {
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, COMMON_SPEC, "bons_voyage-common.toml");
        ModLoadingContext.get().registerConfig(ModConfig.Type.SERVER, SERVER_SPEC, "bons_voyage-server.toml");
        var bus = FMLJavaModLoadingContext.get().getModEventBus();
        bus.addListener((ModConfigEvent.Loading e) -> refresh(e.getConfig()));
        bus.addListener((ModConfigEvent.Reloading e) -> refresh(e.getConfig()));
        bus.addListener((ModConfigEvent.Unloading e) -> {
            if (e.getConfig().getSpec() == SERVER_SPEC) unbreakable = false;
        });
    }

    private static void refresh(ModConfig config) {
        if (config.getSpec() == COMMON_SPEC) {
            spacing = SPACING.get();
            chests = CHESTS.get();
            Map<String, List<String>> next = new LinkedHashMap<>();
            for (Map.Entry<String, ForgeConfigSpec.ConfigValue<List<? extends String>>> e : LOOT.entrySet()) {
                List<String> tables = new ArrayList<>();
                for (String t : e.getValue().get()) {
                    ResourceLocation id = ResourceLocation.m_135820_(t);
                    if (id != null) tables.add(id.toString());
                }
                next.put(e.getKey(), List.copyOf(tables));
            }
            loot = next;
            LogManager.getLogger("Bons Voyage").info("Bons Voyage settings: spacing multiplier {}, waystone chests {}",
                    spacing, chests ? "on" : "off");
        } else if (config.getSpec() == SERVER_SPEC) {
            unbreakable = UNBREAKABLE.get();
        }
    }

    public static double spacingMultiplier() {
        return spacing;
    }

    public static boolean waystoneChests() {
        return chests;
    }

    /** Loot tables for a realm's waystone chest; empty = keep the template's own table. */
    public static List<String> chestLoot(String realm) {
        return loot.getOrDefault(realm, List.of());
    }

    public static boolean unbreakableWaystones() {
        return unbreakable;
    }
}
