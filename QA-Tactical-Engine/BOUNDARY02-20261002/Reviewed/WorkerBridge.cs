using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Xml;
using System.Security.Cryptography;
using HarmonyLib;
using UnityEngine;
using Verse;
using RimWorld;
using RimWorld.Planet;

namespace WarEconomy.WorkerBridge
{
    public class WorkerBridgeMod : Mod
    {
        public WorkerBridgeMod(ModContentPack content) : base(content)
        {
            Log.Message("[WorkerBridge] Mod constructor initialized. Applying Harmony patches...");
            try
            {
                var harmony = new Harmony("wareconomy.workerbridge.poc");
                harmony.PatchAll();
                Log.Message("[WorkerBridge] All Harmony patches applied successfully.");
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Failed to apply Harmony patches: " + ex);
            }
        }
    }

    [StaticConstructorOnStartup]
    public static class WorkerBridgeBootstrapper
    {
        static WorkerBridgeBootstrapper()
        {
            try
            {
                Log.Message("[WorkerBridge] StaticConstructorOnStartup fired. Attaching GameObject...");
                var go = new GameObject("WorkerBridgeController");
                UnityEngine.Object.DontDestroyOnLoad(go);
                go.AddComponent<WorkerBridgeComponent>();
                Log.Message("[WorkerBridge] Controller GameObject attached.");
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Bootstrapper error: " + ex);
            }
        }
    }

    public static class ScopedTacticalSession
    {
        public static bool IsActive = false;
        public static Map? TargetMap = null;
        public static int TargetMapIndex = -1;
        public static long TicksSimulated = 0;

        public static void Activate(Map targetMap)
        {
            TargetMap = targetMap;
            TargetMapIndex = targetMap?.Index ?? -1;
            IsActive = true;
            TicksSimulated = 0;
            Log.Message($"[WorkerBridge] ScopedTacticalSession ACTIVATED on Map[{TargetMapIndex}] (Tile={targetMap?.Tile})");
        }

        public static void Deactivate()
        {
            IsActive = false;
            TargetMap = null;
            TargetMapIndex = -1;
            Log.Message("[WorkerBridge] ScopedTacticalSession DEACTIVATED.");
        }
    }

    #region Harmony Patches for Tactical Isolation & Suppression

    // QA-ENGINE-007 Mechanical Scope Fence: Disable vanilla autonomous frame ticking.
    // In WorkerBridge, ticks are cooperatively driven by WorkerBridge via DoSingleTick().
    [HarmonyPatch(typeof(TickManager), nameof(TickManager.TickManagerUpdate))]
    public static class Patch_TickManager_TickManagerUpdate
    {
        public static bool Prefix()
        {
            return false;
        }
    }

    // QA-ENGINE-005: Reject fastEcology debug bypass in DoSingleTick
    [HarmonyPatch(typeof(TickManager), nameof(TickManager.DoSingleTick))]
    public static class Patch_TickManager_DoSingleTick
    {
        public static void Prefix()
        {
            if (DebugSettings.fastEcology)
            {
                Log.WarningOnce("[WorkerBridge] fastEcology is unsupported in Tactical Worker. Forcing false in DoSingleTick.", 98125);
                DebugSettings.fastEcology = false;
            }
        }
    }

    // QA-ENGINE-005: Reject fastEcology debug bypass in TickList.Tick
    [HarmonyPatch(typeof(TickList), nameof(TickList.Tick))]
    public static class Patch_TickList_Tick
    {
        public static void Prefix()
        {
            if (DebugSettings.fastEcology)
            {
                Log.WarningOnce("[WorkerBridge] fastEcology is unsupported in Tactical Worker. Forcing false in TickList.Tick.", 98126);
                DebugSettings.fastEcology = false;
            }
        }
    }

    // QA-ENGINE-007: Mechanical Pause immediately upon Game initialization
    [HarmonyPatch(typeof(Game), nameof(Game.FinalizeInit))]
    public static class Patch_Game_FinalizeInit
    {
        public static void Postfix(Game __instance)
        {
            if (__instance.tickManager != null)
            {
                __instance.tickManager.CurTimeSpeed = TimeSpeed.Paused;
            }
        }
    }

    [HarmonyPatch(typeof(Map), nameof(Map.MapPreTick))]
    public static class Patch_MapPreTick
    {
        public static bool Prefix(Map __instance)
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return __instance == ScopedTacticalSession.TargetMap;
        }
    }

    [HarmonyPatch(typeof(Map), nameof(Map.MapPostTick))]
    public static class Patch_MapPostTick
    {
        public static bool Prefix(Map __instance)
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return __instance == ScopedTacticalSession.TargetMap;
        }
    }

    [HarmonyPatch(typeof(Thing), nameof(Thing.DoTick))]
    public static class Patch_Thing_DoTick
    {
        public static bool Prefix(Thing __instance)
        {
            if (!ScopedTacticalSession.IsActive) return true;
            Map m = __instance.Map ?? __instance.MapHeld;
            if (m != null)
            {
                return m == ScopedTacticalSession.TargetMap;
            }
            // Skip world pawns, caravans, unspawned things during tactical session
            return false;
        }
    }

    [HarmonyPatch(typeof(World), nameof(World.WorldTick))]
    public static class Patch_World_WorldTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(World), nameof(World.WorldPostTick))]
    public static class Patch_World_WorldPostTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(Storyteller), nameof(Storyteller.StorytellerTick))]
    public static class Patch_StorytellerTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(Autosaver), nameof(Autosaver.AutosaverTick))]
    public static class Patch_AutosaverTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(QuestManager), nameof(QuestManager.QuestManagerTick))]
    public static class Patch_QuestManagerTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(DateNotifier), nameof(DateNotifier.DateNotifierTick))]
    public static class Patch_DateNotifierTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(TaleManager), nameof(TaleManager.TaleManagerTick))]
    public static class Patch_TaleManagerTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(History), nameof(History.HistoryTick))]
    public static class Patch_HistoryTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    // QA-ENGINE-005: Guarded Escape Paths
    [HarmonyPatch(typeof(Scenario), nameof(Scenario.TickScenario))]
    public static class Patch_ScenarioTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(StoryWatcher), nameof(StoryWatcher.StoryWatcherTick))]
    public static class Patch_StoryWatcherTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(GameEnder), nameof(GameEnder.GameEndTick))]
    public static class Patch_GameEndTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(LetterStack), nameof(LetterStack.LetterStackTick))]
    public static class Patch_LetterStackTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch]
    public static class Patch_FilthMonitorTick
    {
        public static System.Reflection.MethodBase? TargetMethod()
        {
            return AccessTools.Method("RimWorld.FilthMonitor:FilthMonitorTick");
        }

        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(TransportShipManager), nameof(TransportShipManager.ShipObjectsTick))]
    public static class Patch_ShipObjectsTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    #endregion

    public class BridgeRequest
    {
        public string Command = "";
        public string Argument = "";
        public long CorrelationId = 0;
        public DateTime QueuedTime = DateTime.UtcNow;
        public TaskCompletionSource<string> ResponseTcs = new TaskCompletionSource<string>();
    }

    public enum WorkerLifecycleState
    {
        NO_GAME,
        LOAD_REQUESTED,
        VALIDATING,
        LOADING,
        READY,
        LOAD_FAILED,
        SHUTTING_DOWN
    }

    public class WorkerBridgeComponent : MonoBehaviour
    {
        private TcpListener? listener;
        private Thread? listenerThread;
        private volatile bool isRunning = true;
        private readonly ConcurrentQueue<BridgeRequest> requestQueue = new ConcurrentQueue<BridgeRequest>();

        private int port = 29100;

        // Lifecycle & Correlation
        private WorkerLifecycleState lifecycleState = WorkerLifecycleState.NO_GAME;
        private long currentGeneration = 0;
        private string lastFailureReason = "";
        private string activeSaveName = "";
        public static int DesignatedTargetMapIndex = 0;

        // Post-load Semantic & Error Gate (QA-ENGINE-002, QA-ENGINE-007)
        private bool isTrackingLoadErrors = false;
        private int loadErrorCount = 0;
        private string firstLoadError = "";

        // Sliced Simulation Loop & Hard Bounds (QA-ENGINE-003, QA-ENGINE-008)
        private const int MAX_SLICE_SIZE = 20;
        private const double MAX_TICK_BUDGET_MS = 10.0;
        private const int MAX_QUEUE_DEPTH = 100;

        private bool isRealtimeSimulating = false;
        private float simulationTps = 60f;
        private int targetTicksRemaining = 0;
        private int ticksPerSlice = 10;
        private float timeAccumulator = 0f;
        private float lastSimFrameTime = 0f;
        private bool isFirstSimFrame = true;

        void Awake()
        {
            try
            {
                // Explicitly disable fastEcology
                DebugSettings.fastEcology = false;

                // Subscribe to Unity log callback for post-load error gating
                Application.logMessageReceived += HandleUnityLogMessage;

                if (GenCommandLine.TryGetCommandLineArg("bridgeport", out string portStr) && int.TryParse(portStr, out int customPort))
                {
                    port = customPort;
                }

                Log.Message($"[WorkerBridge] Component Awake. Listening port: {port}");

                listener = new TcpListener(IPAddress.Loopback, port);
                listener.Start();

                listenerThread = new Thread(ListenLoop)
                {
                    IsBackground = true,
                    Name = "WorkerBridge_Listener"
                };
                listenerThread.Start();
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Failed to start TCP listener: " + ex);
            }
        }

        private void HandleUnityLogMessage(string condition, string stackTrace, LogType type)
        {
            if (isTrackingLoadErrors && (type == LogType.Error || type == LogType.Exception))
            {
                loadErrorCount++;
                if (string.IsNullOrEmpty(firstLoadError))
                {
                    firstLoadError = condition;
                }
            }
        }

        void Update()
        {
            // Enforce fastEcology suppression
            if (DebugSettings.fastEcology)
            {
                DebugSettings.fastEcology = false;
            }

            // Update Loading transition to READY with post-load semantic gate (QA-ENGINE-002, QA-ENGINE-007)
            if (lifecycleState == WorkerLifecycleState.LOADING)
            {
                if (Current.Game != null && Current.ProgramState == ProgramState.Playing && !LongEventHandler.AnyEventNowOrWaiting)
                {
                    isTrackingLoadErrors = false;

                    // Enforce pause
                    if (Current.Game.tickManager != null)
                    {
                        Current.Game.tickManager.CurTimeSpeed = TimeSpeed.Paused;
                    }

                    // Check post-load errors
                    if (loadErrorCount > 0)
                    {
                        lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                        lastFailureReason = $"Load completed with {loadErrorCount} error(s). First error: {firstLoadError}";
                        Log.Error($"[WorkerBridge] Gen {currentGeneration} LOAD_FAILED post-load error gate: {lastFailureReason}");
                    }
                    else if (Current.Game.Maps == null || Current.Game.Maps.Count == 0)
                    {
                        lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                        lastFailureReason = "No maps found in loaded game.";
                        Log.Error($"[WorkerBridge] Gen {currentGeneration} LOAD_FAILED: No maps.");
                    }
                    else
                    {
                        int targetIdx = Math.Min(DesignatedTargetMapIndex, Current.Game.Maps.Count - 1);
                        var targetMap = Current.Game.Maps[targetIdx];
                        ScopedTacticalSession.Activate(targetMap);

                        lifecycleState = WorkerLifecycleState.READY;
                        Log.Message($"[WorkerBridge] Generation {currentGeneration} entered READY state with {Current.Game.Maps.Count} maps. TargetMapIndex={targetIdx}");
                    }
                }
            }

            // Always enforce pause if not actively simulating
            if (lifecycleState == WorkerLifecycleState.READY && !isRealtimeSimulating && targetTicksRemaining == 0)
            {
                if (Current.Game?.tickManager != null && Current.Game.tickManager.CurTimeSpeed != TimeSpeed.Paused)
                {
                    Current.Game.tickManager.CurTimeSpeed = TimeSpeed.Paused;
                }
            }

            // 1. Process pending TCP commands with main-thread time budget
            var cmdSw = Stopwatch.StartNew();
            int commandsServiced = 0;
            while (requestQueue.TryDequeue(out var req))
            {
                commandsServiced++;
                try
                {
                    // Check timeout (LIFE-05)
                    if ((DateTime.UtcNow - req.QueuedTime).TotalSeconds > 10.0)
                    {
                        req.ResponseTcs.TrySetResult("ERROR: Request timed out in worker queue.");
                        continue;
                    }

                    string res = ProcessCommandMainThread(req.Command, req.Argument);
                    req.ResponseTcs.TrySetResult(res);
                }
                catch (Exception ex)
                {
                    Log.Error($"[WorkerBridge] Error processing '{req.Command}': {ex}");
                    req.ResponseTcs.TrySetResult($"ERROR: {ex.GetType().Name}: {ex.Message}");
                }

                if (commandsServiced >= 20 || cmdSw.Elapsed.TotalMilliseconds > 5.0) break;
            }

            // 2. Real-time / Sliced Ticking with Wall-clock Budget & Start Debt Fix (QA-ENGINE-003, QA-ENGINE-008)
            if (lifecycleState == WorkerLifecycleState.READY && ScopedTacticalSession.IsActive && Current.ProgramState == ProgramState.Playing)
            {
                if (isRealtimeSimulating)
                {
                    if (isFirstSimFrame)
                    {
                        isFirstSimFrame = false;
                        lastSimFrameTime = Time.realtimeSinceStartup;
                    }
                    else
                    {
                        float now = Time.realtimeSinceStartup;
                        float dt = now - lastSimFrameTime;
                        lastSimFrameTime = now;
                        timeAccumulator += dt;
                    }

                    float interval = 1f / simulationTps;
                    // Clamp timeAccumulator to prevent catch-up bursts (QA-ENGINE-008)
                    timeAccumulator = Mathf.Min(timeAccumulator, interval * 1.5f);

                    int ticksDue = Mathf.Min(2, Mathf.FloorToInt(timeAccumulator / interval));
                    var tickSw = Stopwatch.StartNew();

                    for (int i = 0; i < ticksDue; i++)
                    {
                        Find.TickManager.DoSingleTick();
                        ScopedTacticalSession.TicksSimulated++;
                        timeAccumulator -= interval;

                        if (tickSw.Elapsed.TotalMilliseconds >= MAX_TICK_BUDGET_MS)
                        {
                            break;
                        }
                    }
                }
                else if (targetTicksRemaining > 0)
                {
                    int toRun = Math.Min(targetTicksRemaining, ticksPerSlice);
                    var tickSw = Stopwatch.StartNew();
                    int ran = 0;

                    for (int i = 0; i < toRun; i++)
                    {
                        Find.TickManager.DoSingleTick();
                        ScopedTacticalSession.TicksSimulated++;
                        ran++;

                        if (tickSw.Elapsed.TotalMilliseconds >= MAX_TICK_BUDGET_MS)
                        {
                            break;
                        }
                    }
                    targetTicksRemaining -= ran;
                }
            }
        }

        private void ListenLoop()
        {
            while (isRunning && listener != null)
            {
                try
                {
                    var client = listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleClient, client);
                }
                catch
                {
                    if (!isRunning) break;
                }
            }
        }

        private void HandleClient(object? state)
        {
            if (state is not TcpClient client) return;
            using (client)
            using (var stream = client.GetStream())
            using (var reader = new StreamReader(stream, Encoding.UTF8))
            using (var writer = new StreamWriter(stream, Encoding.UTF8) { AutoFlush = true })
            {
                try
                {
                    while (isRunning && client.Connected)
                    {
                        string? line = reader.ReadLine();
                        if (line == null) break;
                        line = line.Trim().Trim('\uFEFF', '\u200B', '\0');
                        if (string.IsNullOrEmpty(line)) continue;

                        string cmd = line;
                        string arg = "";
                        int spaceIdx = line.IndexOf(' ');
                        if (spaceIdx > 0)
                        {
                            cmd = line.Substring(0, spaceIdx).ToUpperInvariant();
                            arg = line.Substring(spaceIdx + 1);
                        }
                        else
                        {
                            cmd = line.ToUpperInvariant();
                        }

                        if (requestQueue.Count >= MAX_QUEUE_DEPTH)
                        {
                            writer.WriteLine("ERROR: Request queue capacity exceeded.");
                            writer.WriteLine("---END---");
                            continue;
                        }

                        var req = new BridgeRequest { Command = cmd, Argument = arg };
                        requestQueue.Enqueue(req);

                        if (req.ResponseTcs.Task.Wait(30000))
                        {
                            writer.WriteLine(req.ResponseTcs.Task.Result);
                            writer.WriteLine("---END---");
                        }
                        else
                        {
                            writer.WriteLine("ERROR: Timeout waiting for main thread execution.");
                            writer.WriteLine("---END---");
                        }

                        if (cmd == "SHUTDOWN") break;
                    }
                }
                catch (Exception ex)
                {
                    Log.Warning($"[WorkerBridge] Client handling exception: {ex.Message}");
                }
            }
        }

        private string ProcessCommandMainThread(string cmd, string arg)
        {
            // Global check during shutdown (LIFE-06)
            if (lifecycleState == WorkerLifecycleState.SHUTTING_DOWN && cmd != "STATUS" && cmd != "SHUTDOWN")
            {
                return "ERROR: Worker is shutting down.";
            }

            switch (cmd)
            {
                case "HELLO":
                case "PING":
                    return $"READY: RimWorld {VersionControl.CurrentVersionStringWithRev}, Gen={currentGeneration}, State={lifecycleState}, TargetMap={ScopedTacticalSession.TargetMapIndex}, TicksSim={ScopedTacticalSession.TicksSimulated}";

                case "STATUS":
                case "LOAD_STATUS":
                    return GetLifecycleStatus();

                case "GET_ENVIRONMENT_MANIFEST":
                    return GetEnvironmentManifest();

                case "VALIDATE_MANIFEST":
                    return HandleValidateManifest(arg);

                case "LOAD_SAVE":
                    return HandleLoadSave(arg);

                case "SET_TARGET_MAP":
                    return HandleSetTargetMap(arg);

                case "START_SIMULATION":
                    return HandleStartSimulation(arg);

                case "PAUSE_SIMULATION":
                    return HandlePauseSimulation();

                case "CANCEL_SIMULATION":
                    return HandleCancelSimulation();

                case "STEP_TICKS":
                    return HandleStepTicks(arg);

                // QA-ENGINE-003: RUN_TICKS quarantined from normal Tactical Worker protocol
                case "RUN_TICKS":
                    return "ERROR: RUN_TICKS has been quarantined from normal Tactical Worker protocol due to monolithic main-thread starvation (QA-ENGINE-003). Use cooperative STEP_TICKS or START_SIMULATION. For explicit diagnostic QA only, use QA_DIAGNOSTIC_RUN_TICKS.";

                case "QA_DIAGNOSTIC_RUN_TICKS":
                    return HandleDiagnosticRunTicks(arg);

                case "GENERATE_COMPLEX_FIXTURE":
                    return HandleGenerateComplexFixture(arg);

                case "GET_WORLD_INFO":
                    return GetWorldInfo();

                case "GET_MAP_INFO":
                    return GetMapInfo();

                case "GET_ALL_MAPS_SUMMARY":
                    return GetAllMapsSummary();

                case "GET_MAP_DETAILED_SUMMARY":
                    return GetMapDetailedSummary(arg);

                case "GET_ENTITY_SUMMARY":
                    return GetEntitySummary();

                case "EXPORT_SAVE":
                    return ExportSave(arg);

                case "SHUTDOWN":
                    lifecycleState = WorkerLifecycleState.SHUTTING_DOWN;
                    isRunning = false;
                    try { listener?.Stop(); } catch { }
                    Application.Quit();
                    return "BYE: Worker shutting down.";

                default:
                    return $"ERROR: Unknown command '{cmd}'";
            }
        }

        private string GetLifecycleStatus()
        {
            int maps = Current.Game?.Maps?.Count ?? 0;
            int ticks = Current.Game?.tickManager?.TicksGame ?? 0;
            return $"STATE: {lifecycleState}, Gen={currentGeneration}, Maps={maps}, TicksGame={ticks}, SimActive={ScopedTacticalSession.IsActive}, TargetMap={ScopedTacticalSession.TargetMapIndex}, TicksSim={ScopedTacticalSession.TicksSimulated}, IsRealtime={isRealtimeSimulating}, RemainingStep={targetTicksRemaining}, LastFailure='{lastFailureReason}'";
        }

        private string GetEnvironmentManifest()
        {
            var sb = new StringBuilder();
            sb.AppendLine("=== TACTICAL WORKER ENVIRONMENT MANIFEST ===");
            sb.AppendLine($"EngineVersion: {VersionControl.CurrentVersionStringWithRev}");
            sb.AppendLine($"UnityVersion: {Application.unityVersion}");
            sb.AppendLine($"Platform: {Application.platform}");

            // DLCs
            sb.AppendLine("\n[DLC_STATUS]");
            sb.AppendLine($"Royalty: {ModLister.RoyaltyInstalled}");
            sb.AppendLine($"Ideology: {ModLister.IdeologyInstalled}");
            sb.AppendLine($"Biotech: {ModLister.BiotechInstalled}");
            sb.AppendLine($"Anomaly: {ModLister.AnomalyInstalled}");
            sb.AppendLine($"Odyssey: {ModLister.GetActiveModWithIdentifier("ludeon.rimworld.odyssey") != null}");

            // Active Mods
            sb.AppendLine("\n[ACTIVE_MODS]");
            foreach (var mod in ModsConfig.ActiveModsInLoadOrder)
            {
                sb.AppendLine($"Mod: PackageId={mod.PackageIdNonUnique}, Name='{mod.Name}'");
            }

            // Def Registries
            sb.AppendLine("\n[DEF_REGISTRIES]");
            sb.AppendLine($"ThingDef: {DefDatabase<ThingDef>.DefCount}");
            sb.AppendLine($"HediffDef: {DefDatabase<HediffDef>.DefCount}");
            sb.AppendLine($"RecipeDef: {DefDatabase<RecipeDef>.DefCount}");
            sb.AppendLine($"PawnKindDef: {DefDatabase<PawnKindDef>.DefCount}");
            sb.AppendLine($"BiomeDef: {DefDatabase<BiomeDef>.DefCount}");

            return sb.ToString().TrimEnd();
        }

        private string HandleValidateManifest(string arg)
        {
            // Syntax: VALIDATE_MANIFEST <SaveName> [RequiredDef1,RequiredDef2,...] [RequiredMod1,RequiredMod2,...]
            string[] parts = arg.Split(' ');
            string saveName = parts[0];
            var reqDefs = new List<string>();
            var reqMods = new List<string>();

            if (parts.Length > 1 && !string.IsNullOrEmpty(parts[1]))
            {
                reqDefs.AddRange(parts[1].Split(','));
            }
            if (parts.Length > 2 && !string.IsNullOrEmpty(parts[2]))
            {
                reqMods.AddRange(parts[2].Split(','));
            }

            if (ValidateManifestInternal(saveName, reqDefs, reqMods, out string err))
            {
                return $"MANIFEST_OK: Valid for '{saveName}'.";
            }
            return $"MANIFEST_REJECTED: {err}";
        }

        private bool ValidateManifestInternal(string saveName, List<string> reqDefs, List<string> reqMods, out string failureReason)
        {
            string savePath = GenFilePaths.FilePathForSavedGame(saveName);
            if (!File.Exists(savePath))
            {
                failureReason = $"Save file not found at '{savePath}'";
                return false;
            }

            try
            {
                var activeMods = ModsConfig.ActiveModsInLoadOrder.Select(m => m.PackageIdNonUnique).ToHashSet(StringComparer.OrdinalIgnoreCase);

                using (var reader = XmlReader.Create(savePath, new XmlReaderSettings { IgnoreWhitespace = true }))
                {
                    while (reader.Read())
                    {
                        if (reader.NodeType == XmlNodeType.Element && reader.Name == "meta")
                        {
                            var metaDoc = new XmlDocument();
                            metaDoc.LoadXml(reader.ReadOuterXml());

                            string gameVersion = metaDoc.SelectSingleNode("meta/gameVersion")?.InnerText ?? "";
                            if (!string.IsNullOrEmpty(gameVersion) && !gameVersion.StartsWith("1.6"))
                            {
                                failureReason = $"Incompatible engine version '{gameVersion}' (Expected: 1.6.x)";
                                return false;
                            }

                            // QA-ENGINE-002: Check that ALL mods in save's meta/modIds are active!
                            var modIdNodes = metaDoc.SelectNodes("meta/modIds/li");
                            if (modIdNodes != null)
                            {
                                foreach (XmlNode n in modIdNodes)
                                {
                                    string modId = n.InnerText.Trim();
                                    if (!string.IsNullOrEmpty(modId) && !activeMods.Contains(modId))
                                    {
                                        failureReason = $"Save requires mod '{modId}' which is not active in current configuration.";
                                        return false;
                                    }
                                }
                            }

                            // Caller-declared required mods
                            foreach (var reqMod in reqMods)
                            {
                                if (!activeMods.Contains(reqMod))
                                {
                                    failureReason = $"Required Mod '{reqMod}' is not active in current configuration.";
                                    return false;
                                }
                            }

                            break;
                        }
                    }
                }

                // QA-ENGINE-002: Pre-flight scan save XML for missing/unregistered Defs across all registries
                using (var reader = XmlReader.Create(savePath, new XmlReaderSettings { IgnoreWhitespace = true }))
                {
                    while (reader.Read())
                    {
                        if (reader.NodeType == XmlNodeType.Element && reader.Name == "def")
                        {
                            string defName = reader.ReadElementContentAsString().Trim();
                            if (!string.IsNullOrEmpty(defName))
                            {
                                if (DefDatabase<ThingDef>.GetNamedSilentFail(defName) == null)
                                {
                                    bool foundAny = false;
                                    foreach (var defType in GenDefDatabase.AllDefTypesWithDatabases())
                                    {
                                        if (GenDefDatabase.GetDefSilentFail(defType, defName, false) != null)
                                        {
                                            foundAny = true;
                                            break;
                                        }
                                    }

                                    if (!foundAny)
                                    {
                                        failureReason = $"Save contains undeclared missing Def '{defName}'.";
                                        return false;
                                    }
                                }
                            }
                        }
                    }
                }

                // Caller-declared required Defs (MANIFEST-03)
                foreach (var reqDef in reqDefs)
                {
                    var thingDef = DefDatabase<ThingDef>.GetNamedSilentFail(reqDef);
                    if (thingDef == null)
                    {
                        failureReason = $"Required Def '{reqDef}' was not found in active DefDatabase<ThingDef>.";
                        return false;
                    }
                }

                failureReason = "";
                return true;
            }
            catch (Exception ex)
            {
                failureReason = $"XML parse error in manifest: {ex.Message}";
                return false;
            }
        }

        private string HandleLoadSave(string arg)
        {
            // LIFE-03: LOAD while LOADING
            if (lifecycleState == WorkerLifecycleState.LOADING || lifecycleState == WorkerLifecycleState.VALIDATING)
            {
                return $"ERROR: Load operation already in progress (Gen={currentGeneration}, State={lifecycleState}).";
            }

            // Syntax: LOAD_SAVE <SaveName> [TargetMapIndex] [RequiredDefs] [RequiredMods]
            string[] parts = arg.Split(' ');
            string saveName = parts[0];
            int targetMap = 0;
            var reqDefs = new List<string>();
            var reqMods = new List<string>();

            if (parts.Length > 1 && int.TryParse(parts[1], out int tm)) targetMap = tm;
            if (parts.Length > 2 && !string.IsNullOrEmpty(parts[2])) reqDefs.AddRange(parts[2].Split(','));
            if (parts.Length > 3 && !string.IsNullOrEmpty(parts[3])) reqMods.AddRange(parts[3].Split(','));

            currentGeneration++;
            activeSaveName = saveName;
            DesignatedTargetMapIndex = targetMap;

            lifecycleState = WorkerLifecycleState.LOAD_REQUESTED;

            // Phase 1: Pre-load Manifest Validation (MANIFEST-01 ~ 04)
            lifecycleState = WorkerLifecycleState.VALIDATING;
            if (!ValidateManifestInternal(saveName, reqDefs, reqMods, out string failReason))
            {
                lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                lastFailureReason = failReason;
                Log.Warning($"[WorkerBridge] Load rejected for '{saveName}': {failReason}");
                return $"LOAD_REJECTED: Gen={currentGeneration}, Reason={failReason}";
            }

            // Phase 2: Game Loading with Error Tracking (QA-ENGINE-002, QA-ENGINE-007)
            loadErrorCount = 0;
            firstLoadError = "";
            isTrackingLoadErrors = true;

            lifecycleState = WorkerLifecycleState.LOADING;
            Log.Message($"[WorkerBridge] Initiating load for save '{saveName}' (Gen={currentGeneration}, TargetMap={targetMap})...");
            GameDataSaveLoader.LoadGame(saveName);

            return $"QUEUED: Gen={currentGeneration}, LoadGame queued for '{saveName}'. TargetMapIndex={targetMap}. Poll STATUS to monitor.";
        }

        private string HandleSetTargetMap(string arg)
        {
            if (Current.Game == null || Current.Game.Maps == null || Current.Game.Maps.Count == 0)
            {
                return "ERROR: No active Game/Maps loaded.";
            }

            if (!int.TryParse(arg, out int idx) || idx < 0 || idx >= Current.Game.Maps.Count)
            {
                return $"ERROR: Invalid map index '{arg}'. Total maps: {Current.Game.Maps.Count}";
            }

            DesignatedTargetMapIndex = idx;
            var map = Current.Game.Maps[idx];
            ScopedTacticalSession.Activate(map);
            return $"OK: TargetMap set to Map[{idx}] (Tile={map.Tile})";
        }

        private string HandleStartSimulation(string arg)
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Cannot simulate while worker state is {lifecycleState}.";
            }

            if (float.TryParse(arg, out float tps) && tps > 0)
            {
                simulationTps = tps;
            }

            // QA-ENGINE-008: Monotonic start time tracking to eliminate start debt
            isRealtimeSimulating = true;
            timeAccumulator = 0f;
            lastSimFrameTime = Time.realtimeSinceStartup;
            isFirstSimFrame = true;
            return $"OK: Simulation started at {simulationTps:F0} TPS on TargetMap[{ScopedTacticalSession.TargetMapIndex}].";
        }

        private string HandlePauseSimulation()
        {
            isRealtimeSimulating = false;
            targetTicksRemaining = 0;
            timeAccumulator = 0f;
            isFirstSimFrame = true;
            return $"OK: Simulation paused at TicksSimulated={ScopedTacticalSession.TicksSimulated}.";
        }

        private string HandleCancelSimulation()
        {
            isRealtimeSimulating = false;
            targetTicksRemaining = 0;
            timeAccumulator = 0f;
            isFirstSimFrame = true;
            return $"OK: Simulation cancelled. RemainingTicks cleared. TicksSimulated={ScopedTacticalSession.TicksSimulated}.";
        }

        private string HandleStepTicks(string arg)
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Cannot simulate while worker state is {lifecycleState}.";
            }

            string[] parts = arg.Split(' ');
            if (!int.TryParse(parts[0], out int count) || count <= 0)
            {
                return "ERROR: Invalid tick count. Usage: STEP_TICKS <Count> [maxPerSlice=10]";
            }

            // QA-ENGINE-003: Hard-cap slice size
            int slice = 10;
            if (parts.Length > 1 && int.TryParse(parts[1], out int s) && s > 0)
            {
                slice = Math.Min(s, MAX_SLICE_SIZE);
            }
            ticksPerSlice = slice;

            targetTicksRemaining = count;
            return $"OK: Queued {count} sliced ticks (SliceSize={ticksPerSlice}, HardCap={MAX_SLICE_SIZE}) on TargetMap[{ScopedTacticalSession.TargetMapIndex}].";
        }

        private string HandleDiagnosticRunTicks(string arg)
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Cannot run diagnostic ticks while state is {lifecycleState}.";
            }

            if (!int.TryParse(arg, out int count) || count <= 0)
            {
                return "ERROR: Invalid tick count. Usage: QA_DIAGNOSTIC_RUN_TICKS <positive integer>";
            }

            long startTick = Find.TickManager.TicksGame;
            var sw = Stopwatch.StartNew();

            for (int i = 0; i < count; i++)
            {
                Find.TickManager.DoSingleTick();
                ScopedTacticalSession.TicksSimulated++;
            }

            sw.Stop();
            long endTick = Find.TickManager.TicksGame;
            double ms = Math.Max(0.1, sw.Elapsed.TotalMilliseconds);
            double tps = count * 1000.0 / ms;

            return $"OK: QA Diagnostic ran {count} ticks in {ms:F1} ms ({tps:F1} TPS). TargetMap={ScopedTacticalSession.TargetMapIndex}, TicksSimTotal={ScopedTacticalSession.TicksSimulated}, StartTick={startTick}, EndTick={endTick}";
        }

        // QA-ENGINE-006: Engine-Generated Complex Fixture using native RimWorld APIs
        private string HandleGenerateComplexFixture(string saveName)
        {
            if (Current.Game == null || Find.Maps == null || Find.Maps.Count < 2)
            {
                return "ERROR: Cannot generate complex fixture; requires at least 2 loaded maps.";
            }

            try
            {
                if (string.IsNullOrEmpty(saveName)) saveName = "EngineComplexFixture";

                var map0 = Find.Maps[0];
                var map1 = Find.Maps[1];

                // 1. Colonist with weapon, apparel, and inventory on Map 0
                var colonist = map0.mapPawns.FreeColonists.FirstOrDefault();
                if (colonist == null)
                {
                    colonist = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
                    GenSpawn.Spawn(colonist, new IntVec3(100, 0, 100), map0);
                }

                // Primary weapon
                if (colonist.equipment.Primary == null)
                {
                    var gunDef = ThingDef.Named("Gun_Autopistol");
                    var gun = (ThingWithComps)ThingMaker.MakeThing(gunDef);
                    colonist.equipment.MakeRoomFor(gun);
                    colonist.equipment.AddEquipment(gun);
                }

                // Apparel
                var vestDef = ThingDef.Named("Apparel_FlakVest");
                if (!colonist.apparel.WornApparel.Any(a => a.def == vestDef))
                {
                    var vest = (Apparel)ThingMaker.MakeThing(vestDef);
                    colonist.apparel.Wear(vest, true, true);
                }

                // Inventory
                var medDef = ThingDefOf.MedicineIndustrial;
                var med = ThingMaker.MakeThing(medDef);
                med.stackCount = 5;
                colonist.inventory.innerContainer.TryAdd(med);

                var meatDef = DefDatabase<ThingDef>.AllDefsListForReading.FirstOrDefault(d => d.defName == "Meat_Muffalo") ?? ThingDefOf.MealSurvivalPack;
                var meat = ThingMaker.MakeThing(meatDef);
                meat.stackCount = 5;
                colonist.inventory.innerContainer.TryAdd(meat);

                // Nontrivial health
                var torsoPart = colonist.RaceProps.body.AllParts.FirstOrDefault(p => p.def == BodyPartDefOf.Torso);
                var stabDef = DefDatabase<HediffDef>.GetNamedSilentFail("Stab");
                if (torsoPart != null && stabDef != null && !colonist.health.hediffSet.hediffs.Any(h => h.def == stabDef))
                {
                    var stab = (Hediff_Injury)HediffMaker.MakeHediff(stabDef, colonist, torsoPart);
                    stab.loadID = Find.UniqueIDsManager.GetNextHediffID();
                    stab.Severity = 3.0f;
                    colonist.health.AddHediff(stab);
                }

                var eyePart = colonist.RaceProps.body.AllParts.FirstOrDefault(p => p.def == BodyPartDefOf.Eye);
                var bionicDef = DefDatabase<HediffDef>.GetNamedSilentFail("BionicEye");
                if (eyePart != null && bionicDef != null && !colonist.health.hediffSet.hediffs.Any(h => h.def == bionicDef))
                {
                    var bionic = HediffMaker.MakeHediff(bionicDef, colonist, eyePart);
                    bionic.loadID = Find.UniqueIDsManager.GetNextHediffID();
                    colonist.health.AddHediff(bionic);
                }

                // Bed assignment
                var bedPos = colonist.Position + new IntVec3(2, 0, 0);
                var bed = map0.listerThings.AllThings.OfType<Building_Bed>().FirstOrDefault();
                if (bed == null)
                {
                    bed = (Building_Bed)ThingMaker.MakeThing(ThingDefOf.Bed);
                    GenSpawn.Spawn(bed, bedPos, map0);
                }
                bed.CompAssignableToPawn.TryAssignPawn(colonist);

                // Animal Master & Training (Labrador with Obedience)
                var dogKind = DefDatabase<PawnKindDef>.GetNamedSilentFail("LabradorRetriever") ?? DefDatabase<PawnKindDef>.GetNamedSilentFail("Husky");
                if (dogKind != null)
                {
                    var dog = PawnGenerator.GeneratePawn(dogKind, Faction.OfPlayer);
                    GenSpawn.Spawn(dog, colonist.Position + new IntVec3(1, 0, 1), map0);
                    var tamenessDef = DefDatabase<TrainableDef>.GetNamedSilentFail("Tameness");
                    if (tamenessDef != null)
                    {
                        dog.training.Train(tamenessDef, colonist, true);
                    }
                    var obedienceDef = TrainableDefOf.Obedience;
                    if (obedienceDef != null)
                    {
                        dog.training.Train(obedienceDef, colonist, true);
                    }
                    if (dog.playerSettings != null)
                    {
                        dog.playerSettings.Master = colonist;
                    }
                }

                // Nonempty Bill on Workbench
                var tailorDef = ThingDef.Named("TableSculpting") ?? ThingDef.Named("HandTailoringBench");
                var table = map0.listerThings.AllThings.OfType<Building_WorkTable>().FirstOrDefault();
                if (table == null && tailorDef != null)
                {
                    table = (Building_WorkTable)ThingMaker.MakeThing(tailorDef);
                    GenSpawn.Spawn(table, colonist.Position + new IntVec3(3, 0, 0), map0);
                }
                if (table != null && table.BillStack.Count == 0)
                {
                    var recipe = table.def.AllRecipes?.FirstOrDefault() ?? DefDatabase<RecipeDef>.AllDefsListForReading.FirstOrDefault();
                    if (recipe != null)
                    {
                        var bill = recipe.MakeNewBill();
                        table.BillStack.AddBill(bill);
                    }
                }

                // Power & Battery
                var batteryDef = ThingDef.Named("Battery");
                var battery = map0.listerThings.AllThings.OfType<Building>().FirstOrDefault(b => b.def == batteryDef);
                if (battery == null && batteryDef != null)
                {
                    battery = (Building)ThingMaker.MakeThing(batteryDef);
                    GenSpawn.Spawn(battery, colonist.Position + new IntVec3(5, 0, 0), map0);
                }
                if (battery != null)
                {
                    var comp = battery.GetComp<CompPowerBattery>();
                    if (comp != null) comp.SetStoredEnergyPct(0.5f);
                }

                // Crops on fertile soil in a growing zone
                var cropCell = colonist.Position + new IntVec3(0, 0, 3);
                map0.terrainGrid.SetTerrain(cropCell, TerrainDefOf.Soil);
                var riceDef = ThingDef.Named("Plant_Rice");
                if (riceDef != null)
                {
                    var zone = new Zone_Growing(map0.zoneManager);
                    map0.zoneManager.RegisterZone(zone);
                    zone.AddCell(cropCell);
                    zone.SetPlantDefToGrow(riceDef);

                    var crop = (Plant)ThingMaker.MakeThing(riceDef);
                    crop.Growth = 0.5f;
                    GenSpawn.Spawn(crop, cropCell, map0);
                }

                // Corpse in Sarcophagus
                var sarcophagusDef = ThingDef.Named("Sarcophagus");
                if (sarcophagusDef != null)
                {
                    var sarcCell = colonist.Position + new IntVec3(-3, 0, 0);
                    var sarcophagus = (Building_Grave)ThingMaker.MakeThing(sarcophagusDef, ThingDefOf.WoodLog);
                    GenSpawn.Spawn(sarcophagus, sarcCell, map0);
                    var drifterKind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Drifter") ?? PawnKindDefOf.Colonist;
                    var deadGuy = PawnGenerator.GeneratePawn(drifterKind, Faction.OfPlayer);
                    GenSpawn.Spawn(deadGuy, colonist.Position + new IntVec3(-2, 0, 0), map0);
                    deadGuy.Kill(null);
                    if (deadGuy.Corpse != null)
                    {
                        sarcophagus.GetStoreSettings().filter.SetAllow(ThingCategoryDefOf.Corpses, true);
                        sarcophagus.CompAssignableToPawn.TryAssignPawn(deadGuy);
                        sarcophagus.TryAcceptThing(deadGuy.Corpse);
                    }
                }

                // Native Save
                string savePath = GenFilePaths.FilePathForSavedGame(saveName);
                GameDataSaveLoader.SaveGame(saveName);

                return $"OK: Engine complex fixture generated and saved to '{saveName}' ({savePath}). All IDs engine-valid.";
            }
            catch (Exception ex)
            {
                return $"ERROR: Failed to generate engine complex fixture: {ex}";
            }
        }

        private string GetWorldInfo()
        {
            if (Current.Game == null || Find.World == null)
            {
                return "ERROR: No active Game/World loaded.";
            }

            var w = Find.World;
            var sb = new StringBuilder();
            sb.AppendLine($"WorldSeed: {w.info.seedString}");
            sb.AppendLine($"WorldTicks: {Find.TickManager.TicksGame}");
            sb.AppendLine($"FactionsCount: {Find.FactionManager.AllFactions.Count()}");
            sb.AppendLine($"MapsCount: {Find.Maps.Count}");
            sb.AppendLine($"TargetMapIndex: {ScopedTacticalSession.TargetMapIndex}");
            sb.AppendLine($"TicksSimulated: {ScopedTacticalSession.TicksSimulated}");
            return sb.ToString().TrimEnd();
        }

        private string GetMapInfo()
        {
            if (Current.Game == null || Find.Maps == null || Find.Maps.Count == 0)
            {
                return "ERROR: No active Map loaded.";
            }

            var sb = new StringBuilder();
            for (int i = 0; i < Find.Maps.Count; i++)
            {
                var map = Find.Maps[i];
                bool isTarget = (map == ScopedTacticalSession.TargetMap);
                sb.AppendLine($"Map[{i}]: Index={map.Index}, Tile={map.Tile}, Size={map.Size.x}x{map.Size.z}, IsTarget={isTarget}, Pawns={map.mapPawns.AllPawns.Count}, Colonists={map.mapPawns.FreeColonists.Count}, Buildings={map.listerBuildings.allBuildingsColonist.Count}");
            }
            return sb.ToString().TrimEnd();
        }

        private string GetAllMapsSummary()
        {
            if (Current.Game == null || Find.Maps == null || Find.Maps.Count == 0)
            {
                return "ERROR: No active Map loaded.";
            }

            var sb = new StringBuilder();
            sb.AppendLine("=== ALL MAPS COMPARISON SNAPSHOT ===");
            sb.AppendLine($"TicksGame: {Find.TickManager.TicksGame}, TicksSimulated: {ScopedTacticalSession.TicksSimulated}");

            for (int mIdx = 0; mIdx < Find.Maps.Count; mIdx++)
            {
                var map = Find.Maps[mIdx];
                bool isTarget = (map == ScopedTacticalSession.TargetMap);
                sb.AppendLine($"\n--- MAP [{mIdx}] (Tile={map.Tile}, Size={map.Size.x}x{map.Size.z}, IsTarget={isTarget}) ---");

                // Colonists
                var colonists = map.mapPawns.FreeColonists.OrderBy(p => p.ThingID).ToList();
                sb.AppendLine($"[COLONISTS: Count={colonists.Count}]");
                foreach (var c in colonists)
                {
                    string job = c.CurJob != null ? $"{c.CurJob.def?.defName ?? "null"}({c.CurJob.targetA})" : "Idle";
                    float food = c.needs?.food?.CurLevelPercentage ?? -1f;
                    float rest = c.needs?.rest?.CurLevelPercentage ?? -1f;
                    string wep = c.equipment?.Primary?.def?.defName ?? "None";
                    string bed = c.ownership?.OwnedBed?.ThingID ?? "None";
                    int hediffs = c.health?.hediffSet?.hediffs?.Count ?? 0;
                    sb.AppendLine($"Colonist ID={c.ThingID}, Name='{c.LabelShort}', Pos=({c.Position.x},{c.Position.z}), Job={job}, Food={food:F4}, Rest={rest:F4}, Weapon={wep}, Bed={bed}, Hediffs={hediffs}");
                }

                // Animals
                var animals = map.mapPawns.AllPawns.Where(p => p.RaceProps.Animal).OrderBy(p => p.ThingID).Take(20).ToList();
                sb.AppendLine($"[ANIMALS: Count={map.mapPawns.AllPawns.Count(p => p.RaceProps.Animal)} (Sample 20)]");
                foreach (var a in animals)
                {
                    string faction = a.Faction?.def?.defName ?? "Wild";
                    string job = a.CurJob?.def?.defName ?? "Idle";
                    sb.AppendLine($"Animal ID={a.ThingID}, Def={a.def.defName}, Faction={faction}, Pos=({a.Position.x},{a.Position.z}), Job={job}");
                }

                // Buildings & Power
                var buildings = map.listerBuildings.allBuildingsColonist.Take(30).ToList();
                sb.AppendLine($"[BUILDINGS: Count={map.listerBuildings.allBuildingsColonist.Count} (Sample 30)]");
                foreach (var b in buildings)
                {
                    sb.AppendLine($"Building ID={b.ThingID}, Def={b.def.defName}, Pos=({b.Position.x},{b.Position.z}), HP={b.HitPoints}/{b.MaxHitPoints}");
                }

                // Plants / Crops
                var plants = map.listerThings.AllThings.OfType<Plant>().Where(p => p.IsCrop).Take(10).ToList();
                sb.AppendLine($"[CROPS: Count={plants.Count}]");
                foreach (var p in plants)
                {
                    sb.AppendLine($"Plant ID={p.ThingID}, Def={p.def.defName}, Pos=({p.Position.x},{p.Position.z}), Growth={p.Growth:F4}");
                }
            }

            return sb.ToString().TrimEnd();
        }

        private string GetMapDetailedSummary(string arg)
        {
            if (Current.Game == null || Find.Maps == null || Find.Maps.Count == 0)
            {
                return "ERROR: No active Map loaded.";
            }

            int mIdx = 0;
            if (!string.IsNullOrEmpty(arg) && int.TryParse(arg, out int parsed)) mIdx = parsed;
            if (mIdx < 0 || mIdx >= Find.Maps.Count) return $"ERROR: Map index {mIdx} out of range.";

            var map = Find.Maps[mIdx];
            return BuildMapDetailedString(map);
        }

        private string GetEntitySummary()
        {
            var map = ScopedTacticalSession.TargetMap ?? Find.CurrentMap ?? Find.Maps[0];
            return BuildMapDetailedString(map);
        }

        private string BuildMapDetailedString(Map map)
        {
            var sb = new StringBuilder();
            bool isTarget = (map == ScopedTacticalSession.TargetMap);
            sb.AppendLine($"=== DETAILED MAP GRAPH SNAPSHOT ===");
            sb.AppendLine($"MapIndex: {map.Index}, Tile: {map.Tile}, Size: {map.Size.x}x{map.Size.z}, IsTarget: {isTarget}");
            sb.AppendLine($"TicksGame: {Find.TickManager.TicksGame}, TicksSimulated: {ScopedTacticalSession.TicksSimulated}");

            // 1. Colonists & Humanlikes
            var pawns = map.mapPawns.AllPawns.Where(p => p.RaceProps.Humanlike).OrderBy(p => p.ThingID).ToList();
            sb.AppendLine($"\n[PAWNS: Count={pawns.Count}]");
            foreach (var p in pawns)
            {
                try
                {
                    string jobStr = "Idle";
                    try { if (p.CurJob != null) jobStr = $"{p.CurJob.def?.defName ?? "null"}({p.CurJob.targetA})"; } catch { }
                    float food = p.needs?.food?.CurLevelPercentage ?? -1f;
                    float rest = p.needs?.rest?.CurLevelPercentage ?? -1f;
                    string weapon = p.equipment?.Primary?.def?.defName ?? "None";
                    var apparelList = p.apparel?.WornApparel?.Where(a => a != null).Select(a => a.def?.defName ?? "unknown").ToList() ?? new List<string>();
                    var invList = p.inventory?.innerContainer?.Where(i => i != null).Select(i => $"{i.def?.defName ?? "unknown"}x{i.stackCount}").ToList() ?? new List<string>();
                    string bedId = p.ownership?.OwnedBed?.ThingID ?? "None";
                    string faction = p.Faction?.def?.defName ?? "None";

                    var hediffs = p.health?.hediffSet?.hediffs?.Where(h => h != null).Select(h => $"{h.def?.defName ?? "unknown"}{(h.Part != null ? $"[{h.Part.def?.defName ?? "part"}]" : "")}").ToList() ?? new List<string>();

                    sb.AppendLine($"Pawn ID={p.ThingID}, Name='{p.LabelShort}', Faction={faction}, Pos=({p.Position.x},{p.Position.z}), Downed={p.Downed}, Dead={p.Dead}, Job={jobStr}, Food={food:F4}, Rest={rest:F4}, Weapon={weapon}, Apparel=[{string.Join(",", apparelList)}], Inv=[{string.Join(",", invList)}], Bed={bedId}, Hediffs=[{string.Join(",", hediffs)}]");
                }
                catch (Exception ex)
                {
                    sb.AppendLine($"Pawn ID={p.ThingID}, Name='{p.LabelShort}', ERROR={ex.Message}");
                }
            }

            // 2. Animals
            var animals = map.mapPawns.AllPawns.Where(p => p.RaceProps.Animal).OrderBy(p => p.ThingID).ToList();
            sb.AppendLine($"\n[ANIMALS: Count={animals.Count}]");
            foreach (var a in animals.Take(50))
            {
                try
                {
                    string faction = a.Faction?.def?.defName ?? "Wild";
                    string jobStr = a.CurJob?.def?.defName ?? "Idle";
                    string master = a.playerSettings?.Master?.LabelShort ?? "None";
                    sb.AppendLine($"Animal ID={a.ThingID}, Def={a.def?.defName ?? "unknown"}, Faction={faction}, Master={master}, Pos=({a.Position.x},{a.Position.z}), Job={jobStr}");
                }
                catch { }
            }

            // 3. Buildings & Power
            var buildings = map.listerBuildings.allBuildingsColonist.OrderBy(b => b.ThingID).ToList();
            sb.AppendLine($"\n[COLONIST_BUILDINGS: Count={buildings.Count}]");
            foreach (var b in buildings)
            {
                try
                {
                    string power = "None";
                    var compPower = b.TryGetComp<CompPowerTrader>();
                    if (compPower != null) power = compPower.PowerOn ? "On" : "Off";
                    var compBattery = b.TryGetComp<CompPowerBattery>();
                    if (compBattery != null) power = $"Battery({compBattery.StoredEnergy:F0}/{compBattery.Props?.storedEnergyMax ?? 1000:F0})";

                    string owners = "None";
                    if (b is Building_Bed bed && bed.OwnersForReading != null)
                    {
                        owners = string.Join(",", bed.OwnersForReading.Where(o => o != null).Select(o => o.LabelShort));
                    }

                    int bills = (b as Building_WorkTable)?.BillStack?.Count ?? 0;

                    sb.AppendLine($"Building ID={b.ThingID}, Def={b.def?.defName ?? "unknown"}, Pos=({b.Position.x},{b.Position.z}), HP={b.HitPoints}/{b.MaxHitPoints}, Power={power}, Owners={owners}, Bills={bills}");
                }
                catch (Exception ex)
                {
                    sb.AppendLine($"Building ID={b.ThingID}, ERROR={ex.Message}");
                }
            }

            // 4. Containers & Storage
            var containers = map.listerThings.AllThings.OfType<Building_Casket>().OrderBy(s => s.ThingID).ToList();
            sb.AppendLine($"\n[CASKET_CONTAINERS: Count={containers.Count}]");
            foreach (var c in containers)
            {
                try
                {
                    string contained = "Empty";
                    if (c.ContainedThing is Corpse corpse)
                    {
                        contained = $"Corpse({corpse.LabelShort})";
                    }
                    else if (c.ContainedThing != null)
                    {
                        contained = c.ContainedThing.LabelShort;
                    }
                    sb.AppendLine($"Casket ID={c.ThingID}, Def={c.def?.defName ?? "unknown"}, Pos=({c.Position.x},{c.Position.z}), Contained={contained}");
                }
                catch { }
            }

            // 5. Growing Crops
            var crops = map.listerThings.AllThings.OfType<Plant>().Where(p => p.def?.defName == "Plant_Rice" || p.IsCrop || (p.def?.plant != null && p.def.plant.Sowable)).OrderBy(p => p.ThingID).Take(20).ToList();
            sb.AppendLine($"\n[CROPS: Sample={crops.Count}]");
            foreach (var c in crops)
            {
                try
                {
                    sb.AppendLine($"Crop ID={c.ThingID}, Def={c.def?.defName ?? "unknown"}, Pos=({c.Position.x},{c.Position.z}), Growth={c.Growth:F4}");
                }
                catch { }
            }

            return sb.ToString().TrimEnd();
        }

        private string ExportSave(string saveName)
        {
            // QA-ENGINE-002, QA-ENGINE-007: Only READY state can canonical export!
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Cannot export save while worker state is {lifecycleState} (Reason: {lastFailureReason}). (Only READY state permitted).";
            }

            if (Current.Game == null)
            {
                return "ERROR: Cannot export save; no active Game loaded.";
            }

            if (string.IsNullOrEmpty(saveName))
            {
                saveName = $"WorkerExport_{DateTime.UtcNow:yyyyMMdd_HHmmss}";
            }

            string savePath = GenFilePaths.FilePathForSavedGame(saveName);
            Log.Message($"[WorkerBridge] Exporting save to '{savePath}'...");

            if (Current.Game?.tickManager != null)
            {
                Current.Game.tickManager.CurTimeSpeed = TimeSpeed.Paused;
            }

            timeAccumulator = 0f;
            isFirstSimFrame = true;

            var sw = Stopwatch.StartNew();
            GameDataSaveLoader.SaveGame(saveName);
            sw.Stop();

            if (!File.Exists(savePath))
            {
                return $"ERROR: Save file '{savePath}' was not created on disk.";
            }

            var fi = new FileInfo(savePath);
            string hash;
            using (var sha = SHA256.Create())
            using (var fs = File.OpenRead(savePath))
            {
                hash = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "");
            }

            return $"SAVED: File='{savePath}', Name='{saveName}', Size={fi.Length} bytes, SHA256={hash}, Elapsed={sw.ElapsedMilliseconds} ms, TicksSimulated={ScopedTacticalSession.TicksSimulated}";
        }

        void OnDestroy()
        {
            isRunning = false;
            try { Application.logMessageReceived -= HandleUnityLogMessage; } catch { }
            try { listener?.Stop(); } catch { }
            try { listenerThread?.Abort(); } catch { }
        }
    }
}
