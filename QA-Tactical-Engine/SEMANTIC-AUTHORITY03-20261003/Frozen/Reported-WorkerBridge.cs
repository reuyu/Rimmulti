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
using Newtonsoft.Json;
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

    [HarmonyPatch(typeof(WorldObjectsHolder), nameof(WorldObjectsHolder.WorldObjectsHolderTick))]
    public static class Patch_WorldObjectsHolderTick
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

    [HarmonyPatch(typeof(IncidentQueue), nameof(IncidentQueue.IncidentQueueTick))]
    public static class Patch_IncidentQueueTick
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

    [HarmonyPatch(typeof(Autosaver), nameof(Autosaver.AutosaverTick))]
    public static class Patch_AutosaverTick
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

    [HarmonyPatch(typeof(QuestManager), nameof(QuestManager.QuestManagerTick))]
    public static class Patch_QuestManagerTick
    {
        public static bool Prefix()
        {
            if (!ScopedTacticalSession.IsActive) return true;
            return false;
        }
    }

    [HarmonyPatch(typeof(FactionManager), nameof(FactionManager.FactionManagerTick))]
    public static class Patch_FactionManagerTick
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

    #endregion

    public class BridgeRequest
    {
        public string Command = "";
        public string Argument = "";
        public TaskCompletionSource<string> ResponseTcs = new TaskCompletionSource<string>();
        public DateTime QueuedTime = DateTime.UtcNow;
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

    public enum SemanticApprovalState
    {
        NONE,
        LOADED_UNTRUSTED,
        VALIDATION_REQUIRED,
        VALIDATION_FAILED,
        INPUT_VALIDATED,
        RESULT_SEALED,
        STAGED_VALIDATED,
        ARTIFACT_APPROVED
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

        // Semantic Authority & Admission (QA-ENGINE-002, QA-ENGINE-006, WP-03)
        private AuthorityBundle? registeredAuthority = null;
        private ResultManifest? sealedResult = null;
        private SemanticApprovalState semanticState = SemanticApprovalState.NONE;
        private bool trustedSimulationReady = false;
        private long currentResultEpoch = 0;
        private string lastValidationSummary = "";
        private string lastStagedPath = "";
        private string lastStagedSha = "";

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
                        // Gate 03: Loaded state is initially UNTRUSTED
                        semanticState = SemanticApprovalState.LOADED_UNTRUSTED;
                        trustedSimulationReady = false;
                        sealedResult = null;
                        lastValidationSummary = "Game loaded. State is LOADED_UNTRUSTED. Authority validation required before simulation.";
                        Log.Message($"[WorkerBridge] Generation {currentGeneration} entered READY state with {Current.Game.Maps.Count} maps. TargetMapIndex={targetIdx}. SemanticState=LOADED_UNTRUSTED");
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
            // Sliced simulation is ONLY allowed when trustedSimulationReady is TRUE!
            if (lifecycleState == WorkerLifecycleState.READY && ScopedTacticalSession.IsActive && Current.ProgramState == ProgramState.Playing && trustedSimulationReady)
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
                    int maxTicksPerFrame = 5;
                    int ticksThisFrame = 0;

                    while (timeAccumulator >= interval && ticksThisFrame < maxTicksPerFrame)
                    {
                        DoSingleScopedTick();
                        timeAccumulator -= interval;
                        ticksThisFrame++;
                    }

                    if (timeAccumulator >= interval * 2)
                    {
                        timeAccumulator = 0f;
                    }
                }
                else if (targetTicksRemaining > 0)
                {
                    var tickSw = Stopwatch.StartNew();
                    int ticksToRun = Math.Min(targetTicksRemaining, ticksPerSlice);
                    for (int i = 0; i < ticksToRun; i++)
                    {
                        DoSingleScopedTick();
                        targetTicksRemaining--;
                        if (tickSw.Elapsed.TotalMilliseconds >= MAX_TICK_BUDGET_MS) break;
                    }
                }
            }
        }

        private void DoSingleScopedTick()
        {
            if (Current.Game?.tickManager != null)
            {
                Current.Game.tickManager.DoSingleTick();
                ScopedTacticalSession.TicksSimulated++;

                // Gate 03: Ticking invalidates any previous sealed result
                if (sealedResult != null)
                {
                    sealedResult = null;
                    semanticState = SemanticApprovalState.INPUT_VALIDATED;
                    lastValidationSummary = "Ticks advanced; sealed result invalidated.";
                }
            }
        }

        private void ListenLoop()
        {
            while (isRunning)
            {
                try
                {
                    if (listener == null) break;
                    var client = listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleClient, client);
                }
                catch (SocketException)
                {
                    if (!isRunning) break;
                }
                catch (Exception ex)
                {
                    Log.Error("[WorkerBridge] Listener exception: " + ex);
                }
            }
        }

        private void HandleClient(object? state)
        {
            using (var client = (TcpClient)state!)
            using (var stream = client.GetStream())
            using (var reader = new StreamReader(stream, Encoding.UTF8))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true })
            {
                try
                {
                    while (isRunning && client.Connected)
                    {
                        string? line = reader.ReadLine();
                        if (line == null) break;

                        line = line.Trim();
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
                            cmd = cmd.ToUpperInvariant();
                        }

                        // Check queue depth
                        if (requestQueue.Count >= MAX_QUEUE_DEPTH)
                        {
                            writer.WriteLine("ERROR: Worker request queue overflow. Try again.");
                            writer.WriteLine("---END---");
                            continue;
                        }

                        var req = new BridgeRequest
                        {
                            Command = cmd,
                            Argument = arg,
                            QueuedTime = DateTime.UtcNow
                        };

                        requestQueue.Enqueue(req);

                        // Wait for completion on main thread with 15s absolute timeout
                        if (req.ResponseTcs.Task.Wait(TimeSpan.FromSeconds(15)))
                        {
                            writer.WriteLine(req.ResponseTcs.Task.Result);
                            writer.WriteLine("---END---");
                        }
                        else
                        {
                            writer.WriteLine("ERROR: Request timed out waiting for main thread execution.");
                            writer.WriteLine("---END---");
                        }
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

                // Gate 03: Input Authority Registry
                case "REGISTER_AUTHORITY":
                    return HandleRegisterAuthority(arg);

                case "GET_AUTHORITY":
                    return HandleGetAuthority();

                case "LOAD_SAVE":
                    return HandleLoadSave(arg);

                case "VALIDATE_INPUT":
                    return HandleValidateInput();

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

                // Gate 03: Result Sealing, Staging & Atomic Promotion
                case "SEAL_RESULT":
                    return HandleSealResult(arg);

                case "GET_SEALED_RESULT":
                    return HandleGetSealedResult();

                case "STAGE_SAVE":
                    return HandleStageSave(arg);

                case "PROMOTE_STAGED":
                    return HandlePromoteStaged(arg);

                case "EXPORT_SAVE":
                case "EXPORT_APPROVED_SAVE":
                    return HandleExportApprovedSave(arg);

                // Gate 03: APPROVE_SEMANTIC is deprecated and rejected
                case "APPROVE_SEMANTIC":
                    return "ERROR: APPROVE_SEMANTIC is deprecated and rejected under Gate 03 authority model. Register an AuthorityBundle and use VALIDATE_INPUT.";

                case "VALIDATE_SEMANTIC":
                    return HandleValidateSemantic(arg);

                case "GET_SEMANTIC_STATUS":
                    return GetSemanticStatus();

                case "GET_CENSUS_JSON":
                    return HandleGetCensusJson(arg);

                case "EXPORT_CENSUS":
                    return HandleExportCensus(arg);

                case "PROBE_LOCAL_CLOCKS":
                    return HandleProbeLocalClocks();

                case "QA_MUTATE_LIVE":
                    return HandleQaMutateLive(arg);

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
            string sealedHash = sealedResult?.sealedManifestHash ?? "None";
            return $"STATE: {lifecycleState}, SemanticState={semanticState}, SimulationReady={trustedSimulationReady}, SealedHash={sealedHash}, Gen={currentGeneration}, Maps={maps}, TicksGame={ticks}, SimActive={ScopedTacticalSession.IsActive}, TargetMap={ScopedTacticalSession.TargetMapIndex}, TicksSim={ScopedTacticalSession.TicksSimulated}, IsRealtime={isRealtimeSimulating}, RemainingStep={targetTicksRemaining}, LastFailure='{lastFailureReason}'";
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

                // Caller-declared required Defs
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

        private string HandleValidateManifest(string arg)
        {
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

        #region Gate 03: Input Authority Registry

        private string HandleRegisterAuthority(string arg)
        {
            try
            {
                if (string.IsNullOrEmpty(arg))
                {
                    return "ERROR: Missing AuthorityBundle JSON payload.";
                }

                var bundle = JsonConvert.DeserializeObject<AuthorityBundle>(arg);
                if (bundle == null)
                {
                    return "ERROR: Failed to parse AuthorityBundle JSON.";
                }

                if (string.IsNullOrEmpty(bundle.authorityId))
                {
                    return "ERROR: AuthorityBundle requires a non-empty AuthorityId.";
                }

                if (bundle.manifestVersion != "3.0")
                {
                    return $"ERROR: Unsupported manifest version '{bundle.manifestVersion}' (Expected: 3.0).";
                }

                if (string.IsNullOrEmpty(bundle.expectedManifestHash) || bundle.expectedManifestHash.Length != 64)
                {
                    return "ERROR: AuthorityBundle requires a valid 64-char SHA-256 ExpectedManifestHash.";
                }

                // Store immutable bundle
                registeredAuthority = bundle;
                Log.Message($"[WorkerBridge] Registered AuthorityBundle: Id={bundle.authorityId}, ExpectedHash={bundle.expectedManifestHash}, Gen={bundle.workerGeneration}, Map={bundle.targetMapId}");

                return $"AUTHORITY_REGISTERED: Id={bundle.authorityId}, ExpectedHash={bundle.expectedManifestHash}, Gen={bundle.workerGeneration}, Map={bundle.targetMapId}";
            }
            catch (Exception ex)
            {
                return $"ERROR: RegisterAuthority exception: {ex.Message}";
            }
        }

        private string HandleGetAuthority()
        {
            if (registeredAuthority == null)
            {
                return "ERROR: No AuthorityBundle currently registered.";
            }
            return JsonConvert.SerializeObject(registeredAuthority, Newtonsoft.Json.Formatting.Indented);
        }

        private string HandleLoadSave(string arg)
        {
            if (lifecycleState == WorkerLifecycleState.LOADING || lifecycleState == WorkerLifecycleState.VALIDATING)
            {
                return $"ERROR: Load operation already in progress (Gen={currentGeneration}, State={lifecycleState}).";
            }

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

            // Invalidate simulation and sealing states on reload
            trustedSimulationReady = false;
            sealedResult = null;
            semanticState = SemanticApprovalState.NONE;

            // Check Authority Source Artifact SHA if registered
            string savePath = GenFilePaths.FilePathForSavedGame(saveName);
            if (!File.Exists(savePath))
            {
                lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                lastFailureReason = $"Save file not found at '{savePath}'";
                return $"LOAD_REJECTED: Save file not found.";
            }

            if (registeredAuthority != null && !string.IsNullOrEmpty(registeredAuthority.expectedSourceArtifactHash))
            {
                string actualSaveSha;
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(savePath))
                {
                    actualSaveSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }

                if (actualSaveSha != registeredAuthority.expectedSourceArtifactHash)
                {
                    lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                    lastFailureReason = $"Source artifact SHA mismatch. Expected {registeredAuthority.expectedSourceArtifactHash}, got {actualSaveSha}";
                    return $"LOAD_REJECTED: Source artifact SHA mismatch. Expected {registeredAuthority.expectedSourceArtifactHash}, got {actualSaveSha}";
                }
            }

            lifecycleState = WorkerLifecycleState.LOAD_REQUESTED;

            // Phase 1: Pre-load Manifest Validation
            lifecycleState = WorkerLifecycleState.VALIDATING;
            if (!ValidateManifestInternal(saveName, reqDefs, reqMods, out string failReason))
            {
                lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                lastFailureReason = failReason;
                Log.Warning($"[WorkerBridge] Load rejected for '{saveName}': {failReason}");
                return $"LOAD_REJECTED: Gen={currentGeneration}, Reason={failReason}";
            }

            // Phase 2: Game Loading with Error Tracking
            loadErrorCount = 0;
            firstLoadError = "";
            isTrackingLoadErrors = true;

            lifecycleState = WorkerLifecycleState.LOADING;
            Log.Message($"[WorkerBridge] Initiating load for save '{saveName}' (Gen={currentGeneration}, TargetMap={targetMap})...");
            GameDataSaveLoader.LoadGame(saveName);

            return $"QUEUED: Gen={currentGeneration}, LoadGame queued for '{saveName}'. TargetMapIndex={targetMap}. Poll STATUS to monitor.";
        }

        private string HandleValidateInput()
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Worker is not READY (State={lifecycleState}). Cannot validate input.";
            }

            if (Current.ProgramState != ProgramState.Playing || Current.Game == null || Current.Game.Maps.NullOrEmpty())
            {
                return "ERROR: Game not playing or no maps loaded.";
            }

            if (registeredAuthority == null)
            {
                return "ERROR: No AuthorityBundle registered. Control plane must register authority before input admission.";
            }

            if (registeredAuthority.workerGeneration != currentGeneration)
            {
                return $"ERROR: Authority generation mismatch (AuthorityGen={registeredAuthority.workerGeneration}, CurrentGen={currentGeneration}).";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            if (registeredAuthority.targetMapId != mapIdx)
            {
                return $"ERROR: Authority target map mismatch (AuthorityMap={registeredAuthority.targetMapId}, CurrentMap={mapIdx}).";
            }

            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            var liveCensus = EngineHostCensus.GenerateCensus(map);
            string liveHash = liveCensus.ComputeManifestHash();

            if (liveHash == registeredAuthority.expectedManifestHash)
            {
                semanticState = SemanticApprovalState.INPUT_VALIDATED;
                trustedSimulationReady = true;
                lastValidationSummary = $"INPUT_VALIDATED: Live manifest matches AuthorityBundle {registeredAuthority.authorityId}.";
                Log.Message($"[WorkerBridge] INPUT_VALIDATED: AuthorityId={registeredAuthority.authorityId}, Hash={liveHash}");
                return $"INPUT_VALIDATED: AuthorityId={registeredAuthority.authorityId}, ManifestHash={liveHash}, SimulationReady=true";
            }
            else
            {
                semanticState = SemanticApprovalState.VALIDATION_FAILED;
                trustedSimulationReady = false;
                lastValidationSummary = $"INPUT_REJECTED: Hash mismatch. Expected {registeredAuthority.expectedManifestHash}, got {liveHash}.";
                Log.Warning($"[WorkerBridge] INPUT_REJECTED: Expected {registeredAuthority.expectedManifestHash}, got {liveHash}");
                return $"INPUT_REJECTED: Hash mismatch. Expected {registeredAuthority.expectedManifestHash}, got {liveHash}";
            }
        }

        #endregion

        #region Gate 03: Sliced Simulation & Control

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

            if (!trustedSimulationReady)
            {
                return "ERROR: Cannot simulate untrusted state. Must pass VALIDATE_INPUT against registered authority first.";
            }

            if (float.TryParse(arg, out float tps) && tps > 0)
            {
                simulationTps = tps;
            }

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

            if (!trustedSimulationReady)
            {
                return "ERROR: Cannot simulate untrusted state. Must pass VALIDATE_INPUT against registered authority first.";
            }

            string[] parts = arg.Split(' ');
            if (!int.TryParse(parts[0], out int count) || count <= 0)
            {
                return "ERROR: Invalid tick count. Usage: STEP_TICKS <Count> [maxPerSlice=10]";
            }

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

            if (!trustedSimulationReady)
            {
                return "ERROR: Cannot simulate untrusted state. Must pass VALIDATE_INPUT first.";
            }

            if (!int.TryParse(arg, out int count) || count <= 0)
            {
                return "ERROR: Invalid tick count. Usage: QA_DIAGNOSTIC_RUN_TICKS <positive integer>";
            }

            long startTick = Find.TickManager.TicksGame;
            var sw = Stopwatch.StartNew();

            for (int i = 0; i < count; i++)
            {
                DoSingleScopedTick();
            }

            sw.Stop();
            long endTick = Find.TickManager.TicksGame;
            double ms = Math.Max(0.1, sw.Elapsed.TotalMilliseconds);
            double tps = count * 1000.0 / ms;

            return $"OK: QA Diagnostic ran {count} ticks in {ms:F1} ms ({tps:F1} TPS). TargetMap={ScopedTacticalSession.TargetMapIndex}, TicksSimTotal={ScopedTacticalSession.TicksSimulated}, StartTick={startTick}, EndTick={endTick}";
        }

        #endregion

        #region Gate 03: Result Sealing, Staging & Atomic Promotion

        private string HandleSealResult(string grantId)
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Worker is not READY (State={lifecycleState}). Cannot seal result.";
            }

            if (!trustedSimulationReady)
            {
                return "ERROR: Untrusted state. Cannot seal simulation result without valid input admission.";
            }

            if (registeredAuthority == null)
            {
                return "ERROR: No registered authority bundle.";
            }

            if (registeredAuthority.workerGeneration != currentGeneration)
            {
                return $"ERROR: Authority generation mismatch (AuthorityGen={registeredAuthority.workerGeneration}, CurrentGen={currentGeneration}).";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];

            var liveCensus = EngineHostCensus.GenerateCensus(map);
            string sealedHash = liveCensus.ComputeManifestHash();

            currentResultEpoch++;
            var res = new ResultManifest
            {
                grantId = string.IsNullOrEmpty(grantId) ? $"GRANT-{DateTime.UtcNow:yyyyMMdd-HHmmss}" : grantId.Trim(),
                authorityId = registeredAuthority.authorityId,
                sealedManifestHash = sealedHash,
                contentProfileFingerprint = registeredAuthority.contentProfileFingerprint,
                workerGeneration = currentGeneration,
                targetMapId = mapIdx,
                ticksGame = Find.TickManager.TicksGame,
                resultEpoch = currentResultEpoch,
                sealedAt = DateTime.UtcNow.ToString("O"),
                manifestJson = liveCensus.ToJson()
            };

            sealedResult = res;
            semanticState = SemanticApprovalState.RESULT_SEALED;
            lastValidationSummary = $"RESULT_SEALED: Epoch={currentResultEpoch}, Hash={sealedHash}, Ticks={res.ticksGame}.";
            Log.Message($"[WorkerBridge] RESULT_SEALED: Epoch={currentResultEpoch}, Grant={res.grantId}, Hash={sealedHash}, Ticks={res.ticksGame}, Gen={currentGeneration}");

            return $"RESULT_SEALED: Epoch={currentResultEpoch}, Grant={res.grantId}, ManifestHash={sealedHash}, Ticks={res.ticksGame}, Gen={currentGeneration}";
        }

        private string HandleGetSealedResult()
        {
            if (sealedResult == null)
            {
                return "ERROR: No active ResultManifest sealed.";
            }
            return JsonConvert.SerializeObject(sealedResult, Newtonsoft.Json.Formatting.Indented);
        }

        private string HandleStageSave(string saveName)
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"STAGE_BLOCKED: Worker state is {lifecycleState} (Must be READY).";
            }

            if (semanticState != SemanticApprovalState.RESULT_SEALED || sealedResult == null)
            {
                return $"STAGE_BLOCKED: Semantic state is '{semanticState}' (Must be RESULT_SEALED). Run SEAL_RESULT first.";
            }

            // Binding re-checks
            if (currentGeneration != sealedResult.workerGeneration)
            {
                return $"STAGE_BLOCKED: Generation mismatch (ApprovedGen={sealedResult.workerGeneration}, CurrentGen={currentGeneration}).";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            if (mapIdx != sealedResult.targetMapId)
            {
                return $"STAGE_BLOCKED: TargetMap mismatch (ApprovedMap={sealedResult.targetMapId}, CurrentMap={mapIdx}).";
            }

            int curTicks = Find.TickManager.TicksGame;
            if (curTicks != sealedResult.ticksGame)
            {
                return $"STAGE_BLOCKED: Tick mismatch (SealedTicks={sealedResult.ticksGame}, CurrentTicks={curTicks}).";
            }

            // CRITICAL: Live Recensus immediately before stage-save (Catches same-tick non-tick mutation!)
            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            var liveCensus = EngineHostCensus.GenerateCensus(map);
            string liveHash = liveCensus.ComputeManifestHash();

            if (liveHash != sealedResult.sealedManifestHash)
            {
                semanticState = SemanticApprovalState.VALIDATION_REQUIRED;
                sealedResult = null;
                lastFailureReason = $"Live state mutated after result was sealed! SealedHash={sealedResult?.sealedManifestHash}, CurrentLiveHash={liveHash}";
                Log.Warning($"[WorkerBridge] STAGE_BLOCKED: {lastFailureReason}");
                return $"STAGE_BLOCKED: Live state mutated after result was sealed! SealedHash={sealedResult?.sealedManifestHash}, CurrentLiveHash={liveHash}";
            }

            if (string.IsNullOrEmpty(saveName))
            {
                saveName = $"ApprovedExport_{DateTime.UtcNow:yyyyMMdd_HHmmss}";
            }

            string timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmssfff");
            string stagingSaveName = $"Staging_{saveName}_{timestamp}";
            string stagingPath = GenFilePaths.FilePathForSavedGame(stagingSaveName);
            string quarantineSaveName = $"Quarantine_{saveName}_{timestamp}";
            string quarantinePath = GenFilePaths.FilePathForSavedGame(quarantineSaveName);

            Log.Message($"[WorkerBridge] Initiating gated export to staging: '{stagingPath}'...");

            int saveErrors = 0;
            string firstSaveError = "";
            void SaveLogHandler(string condition, string stackTrace, LogType type)
            {
                if (type == LogType.Error || type == LogType.Exception)
                {
                    saveErrors++;
                    if (string.IsNullOrEmpty(firstSaveError)) firstSaveError = condition;
                }
            }

            Application.logMessageReceived += SaveLogHandler;
            var sw = Stopwatch.StartNew();
            Exception? saveEx = null;

            try
            {
                GameDataSaveLoader.SaveGame(stagingSaveName);
            }
            catch (Exception ex)
            {
                saveEx = ex;
            }
            finally
            {
                Application.logMessageReceived -= SaveLogHandler;
                sw.Stop();
            }

            // Gate 4: Inspect Save Exceptions and Unity Log Errors
            if (saveEx != null || saveErrors > 0 || !File.Exists(stagingPath))
            {
                if (File.Exists(stagingPath))
                {
                    try { File.Move(stagingPath, quarantinePath); } catch { }
                }
                semanticState = SemanticApprovalState.VALIDATION_FAILED;
                lastFailureReason = $"Save execution failed with {saveErrors} error(s). Exception: {saveEx?.Message}. FirstLog: {firstSaveError}";
                Log.Error($"[WorkerBridge] Export failed and quarantined: {lastFailureReason}");
                return $"STAGE_FAILED: Staged save encountered errors. Quarantined. Errors={saveErrors}, Detail={lastFailureReason}";
            }

            // Gate 5: Saved-Byte Proof (Full XML parse to EOF + Staged Semantic Validation)
            if (!EngineHostCensus.ValidateStagedXml(stagingPath, sealedResult.sealedManifestHash, out string xmlErr, out string stagedHash))
            {
                try { File.Move(stagingPath, quarantinePath); } catch { }
                semanticState = SemanticApprovalState.VALIDATION_FAILED;
                lastFailureReason = $"Staged XML validation failed: {xmlErr}";
                Log.Warning($"[WorkerBridge] Staged save validation failed and quarantined: {lastFailureReason}");
                return $"STAGE_FAILED: Staged XML validation failed: {lastFailureReason}";
            }

            string stagedSha;
            using (var sha = SHA256.Create())
            using (var fs = File.OpenRead(stagingPath))
            {
                stagedSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
            }

            lastStagedPath = stagingPath;
            lastStagedSha = stagedSha;
            semanticState = SemanticApprovalState.STAGED_VALIDATED;

            Log.Message($"[WorkerBridge] STAGED_OK: '{stagingPath}', StagedSha={stagedSha}, ManifestHash={stagedHash}, Epoch={sealedResult.resultEpoch}");
            return $"STAGED_OK: File='{stagingPath}', StagingName='{stagingSaveName}', StagedSha={stagedSha}, ManifestHash={stagedHash}, Epoch={sealedResult.resultEpoch}";
        }

        private string HandlePromoteStaged(string arg)
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"PROMOTION_BLOCKED: Worker state is {lifecycleState}.";
            }

            if (sealedResult == null || (semanticState != SemanticApprovalState.STAGED_VALIDATED && semanticState != SemanticApprovalState.RESULT_SEALED))
            {
                return $"PROMOTION_BLOCKED: Invalid semantic state '{semanticState}'. Must be STAGED_VALIDATED.";
            }

            string[] parts = arg.Split(' ');
            string stagingSaveName = parts[0];
            string finalSaveName = parts.Length > 1 ? parts[1] : stagingSaveName.Replace("Staging_", "");

            string stagingPath = GenFilePaths.FilePathForSavedGame(stagingSaveName);
            if (!File.Exists(stagingPath))
            {
                return $"PROMOTION_BLOCKED: Staged file not found at '{stagingPath}'.";
            }

            // Re-verify bindings
            if (currentGeneration != sealedResult.workerGeneration)
            {
                return $"PROMOTION_BLOCKED: Generation mismatch (ApprovedGen={sealedResult.workerGeneration}, CurrentGen={currentGeneration}).";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            if (mapIdx != sealedResult.targetMapId)
            {
                return $"PROMOTION_BLOCKED: TargetMap mismatch (ApprovedMap={sealedResult.targetMapId}, CurrentMap={mapIdx}).";
            }

            // CRITICAL: Live Recensus immediately before promotion
            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            var liveCensus = EngineHostCensus.GenerateCensus(map);
            string liveHash = liveCensus.ComputeManifestHash();

            if (liveHash != sealedResult.sealedManifestHash)
            {
                semanticState = SemanticApprovalState.VALIDATION_REQUIRED;
                return $"PROMOTION_BLOCKED: Live state mutated before promotion! SealedHash={sealedResult.sealedManifestHash}, CurrentLiveHash={liveHash}";
            }

            // Verify Staged File SHA
            string stagedSha;
            using (var sha = SHA256.Create())
            using (var fs = File.OpenRead(stagingPath))
            {
                stagedSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
            }

            if (!string.IsNullOrEmpty(lastStagedSha) && stagedSha != lastStagedSha)
            {
                return $"PROMOTION_BLOCKED: Staged file SHA altered since validation! Expected {lastStagedSha}, got {stagedSha}";
            }

            string finalPath = GenFilePaths.FilePathForSavedGame(finalSaveName);
            string backupPath = GenFilePaths.FilePathForSavedGame(finalSaveName + ".bak");

            // Atomic promotion with backup preservation
            try
            {
                if (File.Exists(finalPath))
                {
                    File.Replace(stagingPath, finalPath, backupPath);
                }
                else
                {
                    File.Move(stagingPath, finalPath);
                }
            }
            catch (Exception ex)
            {
                semanticState = SemanticApprovalState.VALIDATION_FAILED;
                lastFailureReason = $"Atomic promotion failed: {ex.Message}";
                return $"PROMOTION_FAILED: Atomic promotion exception: {ex.Message}";
            }

            var fi = new FileInfo(finalPath);
            string finalSha;
            using (var sha = SHA256.Create())
            using (var fs = File.OpenRead(finalPath))
            {
                finalSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
            }

            semanticState = SemanticApprovalState.ARTIFACT_APPROVED;
            Log.Message($"[WorkerBridge] ARTIFACT_APPROVED: '{finalPath}', SHA={finalSha}, ManifestHash={sealedResult.sealedManifestHash}, Epoch={sealedResult.resultEpoch}");

            return $"ARTIFACT_APPROVED: File='{finalPath}', Name='{finalSaveName}', Size={fi.Length} bytes, SHA256={finalSha}, SealedManifestHash={sealedResult.sealedManifestHash}, Epoch={sealedResult.resultEpoch}";
        }

        private string HandleExportApprovedSave(string saveName)
        {
            // Execute StageSave then PromoteStaged
            string stageRes = HandleStageSave(saveName);
            if (!stageRes.StartsWith("STAGED_OK"))
            {
                return stageRes;
            }

            // Extract StagingName
            string stagingName = "";
            var tokens = stageRes.Split(',');
            foreach (var tok in tokens)
            {
                var kv = tok.Trim().Split('=');
                if (kv.Length == 2 && kv[0] == "StagingName")
                {
                    stagingName = kv[1].Trim('\'', ' ');
                }
            }

            if (string.IsNullOrEmpty(stagingName))
            {
                return "EXPORT_FAILED: Could not parse staging name from stage result.";
            }

            string finalName = string.IsNullOrEmpty(saveName) ? stagingName.Replace("Staging_", "") : saveName.Trim();
            return HandlePromoteStaged($"{stagingName} {finalName}");
        }

        #endregion

        #region Observability & Telemetry

        private string GetSemanticStatus()
        {
            string sealedHash = sealedResult?.sealedManifestHash ?? "None";
            string authId = registeredAuthority?.authorityId ?? "None";
            return $"SEMANTIC_STATUS: State={semanticState}, SimulationReady={trustedSimulationReady}, AuthorityId={authId}, SealedHash={sealedHash}, Epoch={currentResultEpoch}, Summary='{lastValidationSummary.Replace("\r", "").Replace("\n", " | ")}'";
        }

        private string HandleValidateSemantic(string arg)
        {
            if (Current.ProgramState != ProgramState.Playing || Current.Game == null || Current.Game.Maps.NullOrEmpty())
            {
                return "ERROR: Game not playing or no maps loaded.";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];

            string manifestPath = arg.Trim();
            if (string.IsNullOrEmpty(manifestPath))
            {
                manifestPath = Path.Combine(GenFilePaths.SaveDataFolderPath, "Saves", (activeSaveName ?? "TargetSettlement") + ".census.json");
            }

            var expected = EngineHostCensus.LoadFromFile(manifestPath);
            if (expected == null)
            {
                return $"ERROR: Could not load expected manifest from '{manifestPath}'.";
            }

            var actual = EngineHostCensus.GenerateCensus(map);
            var result = EngineHostCensus.CompareCensus(expected, actual);

            if (result.isPass)
            {
                return $"VALIDATION_PASS: Map[{map.Index}] matches manifest '{manifestPath}'. Hash={result.manifestHashActual}, Entities={actual.entityCount}, Errors=0.";
            }
            else
            {
                return $"VALIDATION_FAIL: Map[{map.Index}] failed comparison with '{manifestPath}'. ExpectedHash={result.manifestHashExpected}, ActualHash={result.manifestHashActual}, Errors={result.errors.Count}.\n{result.ToSummaryString()}";
            }
        }

        private string HandleGetCensusJson(string arg)
        {
            if (Current.ProgramState != ProgramState.Playing || Current.Game == null || Current.Game.Maps.NullOrEmpty())
            {
                return "ERROR: Game not playing or no maps loaded.";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            if (!string.IsNullOrEmpty(arg) && int.TryParse(arg.Trim(), out int parsed))
            {
                mapIdx = parsed;
            }

            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            var census = EngineHostCensus.GenerateCensus(map);
            return census.ToJson();
        }

        private string HandleExportCensus(string arg)
        {
            if (Current.ProgramState != ProgramState.Playing || Current.Game == null || Current.Game.Maps.NullOrEmpty())
            {
                return "ERROR: Game not playing or no maps loaded.";
            }

            string saveName = string.IsNullOrEmpty(arg) ? "CensusExport" : arg.Trim();
            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;

            var parts = saveName.Split(' ');
            if (parts.Length > 1 && int.TryParse(parts[1], out int parsedIdx))
            {
                saveName = parts[0];
                mapIdx = parsedIdx;
            }

            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            var census = EngineHostCensus.GenerateCensus(map);
            string json = census.ToJson();
            string hash = census.ComputeManifestHash();

            string path = Path.Combine(GenFilePaths.SaveDataFolderPath, "Saves", saveName + ".census.json");
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            File.WriteAllText(path, json, Encoding.UTF8);

            return $"EXPORT_CENSUS_OK: Path='{path}', ManifestHash={hash}, Size={json.Length}, Entities={census.entityCount}";
        }

        private string HandleProbeLocalClocks()
        {
            if (Current.ProgramState != ProgramState.Playing || Current.Game == null)
            {
                return "ERROR: Game not playing.";
            }

            var sb = new StringBuilder();
            int ticksGame = Find.TickManager.TicksGame;
            int ticksAbs = GenTicks.TicksAbs;
            sb.AppendLine($"=== LOCAL CLOCK & MULTI-MAP PROBE ===");
            sb.AppendLine($"Global_TicksGame: {ticksGame}");
            sb.AppendLine($"Global_TicksAbs: {ticksAbs}");
            sb.AppendLine($"MapsCount: {Find.Maps.Count}");

            for (int i = 0; i < Find.Maps.Count; i++)
            {
                var m = Find.Maps[i];
                bool isTarget = (m == ScopedTacticalSession.TargetMap);
                int localHour = GenDate.HourOfDay(ticksAbs, Find.WorldGrid.LongLatOf(m.Tile).x);
                int localDay = GenDate.DayOfTwelfth(ticksAbs, Find.WorldGrid.LongLatOf(m.Tile).x);
                Season season = GenDate.Season(ticksAbs, Find.WorldGrid.LongLatOf(m.Tile));
                float skyLight = m.skyManager?.CurSkyGlow ?? -1f;

                var colonist = m.mapPawns.AllPawns.FirstOrDefault(p => p.IsColonist);
                long ageBioTicks = colonist?.ageTracker?.AgeBiologicalTicks ?? -1;
                long ageChronoTicks = colonist?.ageTracker?.AgeChronologicalTicks ?? -1;
                float restLevel = colonist?.needs?.rest?.CurLevel ?? -1f;

                var plant = m.listerThings.AllThings.OfType<Plant>().FirstOrDefault();
                float plantGrowth = plant?.Growth ?? -1f;

                sb.AppendLine($"Map[{m.Index}]: Tile={m.Tile}, IsTarget={isTarget}, LocalHour={localHour}, Day={localDay}, Season={season}, SkyGlow={skyLight:F2}, Colonist='{colonist?.LabelShort ?? "None"}', BioTicks={ageBioTicks}, ChronoTicks={ageChronoTicks}, Rest={restLevel:F3}, PlantGrowth={plantGrowth:F3}");
            }

            return sb.ToString();
        }

        private string HandleQaMutateLive(string arg)
        {
            if (Current.ProgramState != ProgramState.Playing || Current.Game == null || Current.Game.Maps.NullOrEmpty())
            {
                return "ERROR: Game not playing or no maps loaded.";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            string[] parts = arg.Split(' ');
            string target = parts[0].ToLowerInvariant();

            switch (target)
            {
                case "skill":
                    string skDef = parts.Length > 1 ? parts[1] : "Shooting";
                    int skLvl = parts.Length > 2 && int.TryParse(parts[2], out int sl) ? sl : 15;
                    var colonist = map.mapPawns.FreeColonists.FirstOrDefault(p => p.ThingID == "Human302") ?? map.mapPawns.FreeColonists.FirstOrDefault();
                    if (colonist?.skills != null)
                    {
                        var skRecord = colonist.skills.GetSkill(DefDatabase<SkillDef>.GetNamedSilentFail(skDef));
                        if (skRecord != null)
                        {
                            skRecord.Level = skLvl;
                            return $"OK: Mutated live skill '{skDef}' of {colonist.ThingID} to {skLvl}. TicksGame={Find.TickManager.TicksGame}";
                        }
                    }
                    return "ERROR: Could not find colonist or skill.";

                case "hediff":
                    float sev = parts.Length > 1 && float.TryParse(parts[1], out float s) ? s : 1.0f;
                    var col = map.mapPawns.FreeColonists.FirstOrDefault(p => p.ThingID == "Human302") ?? map.mapPawns.FreeColonists.FirstOrDefault();
                    var stab = col?.health?.hediffSet?.hediffs?.FirstOrDefault(h => h.def.defName == "Stab");
                    if (stab != null)
                    {
                        stab.Severity = sev;
                        return $"OK: Mutated live hediff Stab severity to {sev:F2}. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find Stab hediff.";

                case "inventory":
                    int count = parts.Length > 1 && int.TryParse(parts[1], out int cnt) ? cnt : 4;
                    var cPawn = map.mapPawns.FreeColonists.FirstOrDefault(p => p.ThingID == "Human302") ?? map.mapPawns.FreeColonists.FirstOrDefault();
                    var med = cPawn?.inventory?.innerContainer?.FirstOrDefault(i => i.def.defName == "MedicineIndustrial");
                    if (med != null)
                    {
                        med.stackCount = count;
                        return $"OK: Mutated live inventory MedicineIndustrial count to {count}. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find MedicineIndustrial in inventory.";

                case "zone":
                    var zone = map.zoneManager?.AllZones?.FirstOrDefault(z => z is Zone_Growing);
                    if (zone != null && zone.cells.Count > 0)
                    {
                        var cell = zone.cells[0];
                        zone.RemoveCell(cell);
                        return $"OK: Removed cell {cell} from Growing Zone. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find growing zone cells.";

                case "designation":
                    var desig = map.designationManager?.AllDesignations?.FirstOrDefault(d => d.def.defName == "Mine");
                    if (desig != null && map.designationManager != null)
                    {
                        map.designationManager.RemoveDesignation(desig);
                        return $"OK: Removed Mine designation. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find Mine designation.";

                case "relation":
                    var pwn = map.mapPawns.FreeColonists.FirstOrDefault(p => p.ThingID == "Human302") ?? map.mapPawns.FreeColonists.FirstOrDefault();
                    var rel = pwn?.relations?.DirectRelations?.FirstOrDefault(r => r.def.defName == "Spouse");
                    if (rel != null && pwn?.relations != null)
                    {
                        pwn.relations.RemoveDirectRelation(rel);
                        return $"OK: Removed Spouse relation. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find Spouse relation.";

                case "bed":
                    var bedPawn = map.mapPawns.FreeColonists.FirstOrDefault(p => p.ThingID == "Human302") ?? map.mapPawns.FreeColonists.FirstOrDefault();
                    if (bedPawn?.ownership?.OwnedBed != null)
                    {
                        bedPawn.ownership.UnclaimBed();
                        return $"OK: Unclaimed owned bed for {bedPawn.ThingID}. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Pawn has no owned bed.";

                case "animal":
                    var dog = map.mapPawns.AllPawns.FirstOrDefault(p => p.RaceProps.Animal && p.playerSettings != null);
                    if (dog?.playerSettings != null)
                    {
                        dog.playerSettings.followFieldwork = !dog.playerSettings.followFieldwork;
                        return $"OK: Toggled followFieldwork={dog.playerSettings.followFieldwork} for {dog.ThingID}. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find animal with playerSettings.";

                case "plant":
                    int pAge = parts.Length > 2 && int.TryParse(parts[2], out int pa) ? pa : 12001;
                    var plant = map.listerThings.AllThings.OfType<Plant>().FirstOrDefault(p => p.def.defName == "Plant_Rice");
                    if (plant != null)
                    {
                        plant.Age = pAge;
                        return $"OK: Set plant {plant.ThingID} Age to {pAge}. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find Plant_Rice.";

                case "bill":
                    var table = map.listerBuildings.allBuildingsColonist.OfType<Building_WorkTable>().FirstOrDefault();
                    var bill = table?.BillStack?.Bills?.FirstOrDefault();
                    if (bill != null)
                    {
                        bill.suspended = true;
                        return $"OK: Set bill {bill.recipe?.defName} suspended=true. TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find worktable bill.";

                default:
                    return $"ERROR: Unknown mutation target '{target}'.";
            }
        }

        #endregion

        void OnDestroy()
        {
            isRunning = false;
            try { Application.logMessageReceived -= HandleUnityLogMessage; } catch { }
            try { listener?.Stop(); } catch { }
            try { listenerThread?.Abort(); } catch { }
        }
    }
}
