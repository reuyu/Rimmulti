using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace WarEconomy.Client
{
    /// <summary>
    /// RimWorld War-Economy & Feudal Hybrid Multiplayer Mod 클라이언트 진입점
    /// </summary>
    public class WarEconomyMod : Mod
    {
        public const string ModId = "WarEconomy.HybridMultiplayer";
        public static Harmony HarmonyInstance { get; private set; } = null!;

        public WarEconomyMod(ModContentPack content) : base(content)
        {
            HarmonyInstance = new Harmony(ModId);
            try
            {
                HarmonyInstance.PatchAll(Assembly.GetExecutingAssembly());
                Log.Message("[WarEconomyMod] Initialized and Harmony patches applied successfully.");
            }
            catch (Exception ex)
            {
                Log.Error($"[WarEconomyMod] Failed to initialize Harmony patches: {ex}");
            }
        }
    }
}
