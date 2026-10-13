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

    #region Harmony Patches for Target Map Isolation & World Suppression

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
            return false; // Suppress world ticking
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
            return false; // No random raids/events from storyteller
        }
    }

    [HarmonyPatch(typeof(Autosaver), nameof(Autosaver.AutosaverTick))]
    public static class Patch_AutosaverTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false; // Autosaver disabled
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
        private bool hasForcedInitialPause = false;

        // Lifecycle & Correlation
        private WorkerLifecycleState lifecycleState = WorkerLifecycleState.NO_GAME;
        private long currentGeneration = 0;
        private string lastFailureReason = "";
        private string activeSaveName = "";
        private int designatedTargetMapIndex = 0;

        // Sliced Simulation Loop (QA-ENGINE-003)
        private bool isRealtimeSimulating = false;
        private float simulationTps = 60f;
        private int targetTicksRemaining = 0;
        private int ticksPerSlice = 10;
        private float timeAccumulator = 0f;

        void Awake()
        {
            try
            {
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

        void Update()
        {
            // Update Loading transition to READY
            if (lifecycleState == WorkerLifecycleState.LOADING)
            {
                if (Current.Game != null && Current.ProgramState == ProgramState.Playing && !LongEventHandler.AnyEventNowOrWaiting)
                {
                    if (Current.Game.Maps != null && Current.Game.Maps.Count > 0)
                    {
                        // Enforce initial pause
                        if (Current.Game.tickManager != null)
                        {
                            Current.Game.tickManager.CurTimeSpeed = TimeSpeed.Paused;
                        }

                        // Activate target map isolation
                        int targetIdx = Math.Min(designatedTargetMapIndex, Current.Game.Maps.Count - 1);
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

            // 1. Process pending TCP commands first (sub-millisecond latency)
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

                if (commandsServiced >= 20) break; // Yield if huge batch
            }

            // 2. Real-time / Sliced Ticking (QA-ENGINE-003)
            if (lifecycleState == WorkerLifecycleState.READY && ScopedTacticalSession.IsActive && Current.ProgramState == ProgramState.Playing)
            {
                if (isRealtimeSimulating)
                {
                    timeAccumulator += Time.unscaledDeltaTime;
                    float interval = 1f / simulationTps;
                    int ticksDue = Mathf.Min(10, Mathf.FloorToInt(timeAccumulator / interval));

                    for (int i = 0; i < ticksDue; i++)
                    {
                        Find.TickManager.DoSingleTick();
                        ScopedTacticalSession.TicksSimulated++;
                        timeAccumulator -= interval;
                    }
                }
                else if (targetTicksRemaining > 0)
                {
                    int toRun = Math.Min(targetTicksRemaining, ticksPerSlice);
                    for (int i = 0; i < toRun; i++)
                    {
                        Find.TickManager.DoSingleTick();
                        ScopedTacticalSession.TicksSimulated++;
                    }
                    targetTicksRemaining -= toRun;
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

                case "STEP_TICKS":
                    return HandleStepTicks(arg);

                case "RUN_TICKS":
                    return HandleRunTicks(arg);

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
            return $"STATE: {lifecycleState}, Gen={currentGeneration}, Maps={maps}, TicksGame={ticks}, SimActive={ScopedTacticalSession.IsActive}, TargetMap={ScopedTacticalSession.TargetMapIndex}, TicksSim={ScopedTacticalSession.TicksSimulated}, IsRealtime={isRealtimeSimulating}, RemainingStep={targetTicksRemaining}";
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
                // Parse save XML meta section
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

                            // Check required mods in manifest
                            var modIdNodes = metaDoc.SelectNodes("meta/modIds/li");
                            var saveModIds = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                            if (modIdNodes != null)
                            {
                                foreach (XmlNode n in modIdNodes) saveModIds.Add(n.InnerText);
                            }

                            var activeMods = ModsConfig.ActiveModsInLoadOrder.Select(m => m.PackageIdNonUnique).ToHashSet(StringComparer.OrdinalIgnoreCase);

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

                // Check required Defs in DefDatabase (MANIFEST-03)
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
            designatedTargetMapIndex = targetMap;
            hasForcedInitialPause = false;

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

            // Phase 2: Game Loading
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

            designatedTargetMapIndex = idx;
            var map = Current.Game.Maps[idx];
            ScopedTacticalSession.Activate(map);
            return $"OK: TargetMap set to Map[{idx}] (Tile={map.Tile})";
        }

        private string HandleStartSimulation(string arg)
        {
            // Invariant: Only READY generation can simulate
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Cannot simulate while worker state is {lifecycleState}.";
            }

            if (float.TryParse(arg, out float tps) && tps > 0)
            {
                simulationTps = tps;
            }

            isRealtimeSimulating = true;
            timeAccumulator = 0f;
            return $"OK: Simulation started at {simulationTps:F0} TPS on TargetMap[{ScopedTacticalSession.TargetMapIndex}].";
        }

        private string HandlePauseSimulation()
        {
            isRealtimeSimulating = false;
            targetTicksRemaining = 0;
            return $"OK: Simulation paused at TicksSimulated={ScopedTacticalSession.TicksSimulated}.";
        }

        private string HandleStepTicks(string arg)
        {
            // Invariant check
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Cannot simulate while worker state is {lifecycleState}.";
            }

            string[] parts = arg.Split(' ');
            if (!int.TryParse(parts[0], out int count) || count <= 0)
            {
                return "ERROR: Invalid tick count. Usage: STEP_TICKS <Count> [maxPerSlice=10]";
            }

            if (parts.Length > 1 && int.TryParse(parts[1], out int slice) && slice > 0)
            {
                ticksPerSlice = slice;
            }

            targetTicksRemaining = count;
            return $"OK: Queued {count} sliced ticks (SliceSize={ticksPerSlice}) on TargetMap[{ScopedTacticalSession.TargetMapIndex}].";
        }

        private string HandleRunTicks(string arg)
        {
            // LIFE-01: RUN while LOADING
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Cannot run ticks while state is {lifecycleState}. (Only READY state permitted).";
            }

            if (!int.TryParse(arg, out int count) || count <= 0)
            {
                return "ERROR: Invalid tick count. Usage: RUN_TICKS <positive integer>";
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

            return $"OK: Ran {count} ticks in {ms:F1} ms ({tps:F1} TPS). TargetMap={ScopedTacticalSession.TargetMapIndex}, TicksSimTotal={ScopedTacticalSession.TicksSimulated}, StartTick={startTick}, EndTick={endTick}";
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

            // 1. Colonists & Humanlikes with full complex graph
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
                    sb.AppendLine($"Animal ID={a.ThingID}, Def={a.def?.defName ?? "unknown"}, Faction={faction}, Pos=({a.Position.x},{a.Position.z}), Job={jobStr}");
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

                    sb.AppendLine($"Building ID={b.ThingID}, Def={b.def?.defName ?? "unknown"}, Pos=({b.Position.x},{b.Position.z}), HP={b.HitPoints}/{b.MaxHitPoints}, Power={power}, Owners={owners}");
                }
                catch (Exception ex)
                {
                    sb.AppendLine($"Building ID={b.ThingID}, ERROR={ex.Message}");
                }
            }

            // 4. Containers & Storage
            var containers = map.listerBuildings.allBuildingsColonist.OfType<Building_Storage>().OrderBy(s => s.ThingID).ToList();
            sb.AppendLine($"\n[STORAGE_CONTAINERS: Count={containers.Count}]");
            foreach (var c in containers)
            {
                try
                {
                    var stored = new List<Thing>();
                    try
                    {
                        var group = c.GetSlotGroup();
                        if (group?.HeldThings != null) stored.AddRange(group.HeldThings);
                    }
                    catch { }

                    sb.AppendLine($"Storage ID={c.ThingID}, Def={c.def?.defName ?? "unknown"}, Pos=({c.Position.x},{c.Position.z}), StoredCount={stored.Count}, Items=[{string.Join(",", stored.Select(t => $"{t.def?.defName ?? "unknown"}x{t.stackCount}"))}]");
                }
                catch { }
            }

            // 5. Growing Crops
            var crops = map.listerThings.AllThings.OfType<Plant>().Where(p => p.IsCrop).OrderBy(p => p.ThingID).Take(20).ToList();
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
            // Invariant (LIFE-02): Only READY state can canonical export
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Cannot export save while worker state is {lifecycleState}. (Only READY state permitted).";
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
            try { listener?.Stop(); } catch { }
            try { listenerThread?.Abort(); } catch { }
        }
    }
}
