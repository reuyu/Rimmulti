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
        STAGED_PENDING_VALIDATION,
        STAGED_VALIDATED,
        ARTIFACT_APPROVED
    }

    public class WorkerBridgeComponent : MonoBehaviour
    {
        public static string? CustomSaveDataPathOverride = null;

        public static string SafeSaveDataFolderPath
        {
            get
            {
                if (!string.IsNullOrEmpty(CustomSaveDataPathOverride))
                {
                    return CustomSaveDataPathOverride!;
                }
                try
                {
                    return GenFilePaths.SaveDataFolderPath;
                }
                catch
                {
                    return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RimWorld");
                }
            }
        }

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

        // Semantic Authority, Grant & Promotion (QA-ENGINE-002, QA-ENGINE-006, WP-04, WP-05)
        private AuthorityBundle? registeredAuthority = null;
        private string registeredAuthorityJson = "";
        private SimulationGrant? activeGrant = null;
        private string activeGrantJson = "";
        private long ticksSimulatedUnderGrant = 0;
        private ResultManifest? sealedResult = null;
        private ValidatorTask? currentValidatorTask = null;
        private string currentValidatorTaskJson = "";
        private string currentValidatorTaskPath = "";
        private StageValidationReceipt? currentStageValidationReceipt = null;
        private SemanticApprovalState semanticState = SemanticApprovalState.NONE;
        private bool trustedSimulationReady = false;
        private long currentResultEpoch = 0;
        private string lastValidationSummary = "";
        private string lastStagedPath = "";
        private string lastStagedSha = "";

        // G05-S01 / Gate05-R2: Operator-launched and owned fresh validator process instance
        private Process? operatorLaunchedValidatorProcess = null;
        private int operatorLaunchedValidatorPid = 0;
        private string operatorLaunchedValidatorStartTimeUtc = "";
        private string operatorLaunchedValidatorExecutable = "";
        private string operatorChannelSecretToken = "";
        private int registeredValidatorProcessId = 0;
        private string registeredValidatorStartTime = "";
        private string registeredValidatorExecutable = "";

        private void RevokeReadiness(string reason)
        {
            trustedSimulationReady = false;
            semanticState = SemanticApprovalState.VALIDATION_FAILED;
            sealedResult = null;
            currentValidatorTask = null;
            currentValidatorTaskJson = "";
            currentValidatorTaskPath = "";
            currentStageValidationReceipt = null;
            if (operatorLaunchedValidatorProcess != null)
            {
                try { if (!operatorLaunchedValidatorProcess.HasExited) operatorLaunchedValidatorProcess.Kill(); } catch { }
                try { operatorLaunchedValidatorProcess.Dispose(); } catch { }
                operatorLaunchedValidatorProcess = null;
            }
            operatorLaunchedValidatorPid = 0;
            operatorLaunchedValidatorStartTimeUtc = "";
            operatorLaunchedValidatorExecutable = "";
            operatorChannelSecretToken = "";
            registeredValidatorProcessId = 0;
            registeredValidatorStartTime = "";
            registeredValidatorExecutable = "";
            activeGrant = null;
            activeGrantJson = "";
            ticksSimulatedUnderGrant = 0;
            currentResultEpoch++; // Any failure advances/invalidates epoch to prevent replay
            lastFailureReason = reason;
            Log.Warning($"[WorkerBridge] READINESS REVOKED: {reason}");
        }

        public static string GetActualContentProfileFingerprint()
        {
            return ContentProfileProvider.GetActualContentProfileFingerprint();
        }

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
                ticksSimulatedUnderGrant++;

                // Gate 03/05: Ticking invalidates any previous sealed result, task, receipt, and epoch
                if (sealedResult != null)
                {
                    sealedResult = null;
                    currentValidatorTask = null;
                    currentValidatorTaskJson = "";
                    currentValidatorTaskPath = "";
                    currentStageValidationReceipt = null;
                    currentResultEpoch++; // Monotonic epoch advance invalidates any outstanding tasks/receipts
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

                // Gate 04: Profile & Grant Registry
                case "GET_PROFILE_FINGERPRINT":
                    return $"PROFILE_FINGERPRINT: {GetActualContentProfileFingerprint()}";

                case "REGISTER_GRANT":
                    return HandleRegisterGrant(arg);

                case "GET_GRANT":
                    return HandleGetGrant();

                case "RESET_WORKER":
                    return HandleResetWorker();

                // Gate 04: Input Authority Registry
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

                // Gate 04/05: Result Sealing, Staging & Fresh Pre-Promotion Validation
                case "SEAL_RESULT":
                    return HandleSealResult(arg);

                case "GET_SEALED_RESULT":
                    return HandleGetSealedResult();

                case "STAGE_SAVE":
                    return HandleStageSave(arg);

                case "REGISTER_VALIDATOR_PROCESS":
                    return HandleRegisterValidatorProcess(arg);

                case "LAUNCH_OPERATOR_VALIDATOR":
                    return HandleLaunchOperatorValidator(arg);

                case "GET_ACTIVE_VALIDATOR_TASK":
                    return HandleGetActiveValidatorTask();

                case "EXECUTE_VALIDATOR_TASK":
                    return HandleExecuteValidatorTask(arg);

                case "COMPLETE_STAGE_VALIDATION":
                    return HandleCompleteStageValidation(arg);

                case "VALIDATE_AS_PRE_PROMOTION_VALIDATOR":
                    return HandleValidateAsPrePromotionValidator(arg);

                case "SUBMIT_STAGE_VALIDATION_RECEIPT":
                    return HandleSubmitStageValidationReceipt(arg);

                case "GET_STAGE_VALIDATION_RECEIPT":
                    return HandleGetStageValidationReceipt();

                case "PROMOTE_STAGED":
                    return HandlePromoteStaged(arg);

                case "QA_MUTATE_EPOCH":
                    return HandleQaMutateEpoch(arg);

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

        #region Gate 04: Authority, Grant, Sliced Simulation & Pre-Promotion Validation

        private string HandleRegisterAuthority(string arg)
        {
            try
            {
                if (string.IsNullOrEmpty(arg))
                {
                    RevokeReadiness("Missing AuthorityBundle JSON payload.");
                    return "ERROR: Missing AuthorityBundle JSON payload.";
                }

                // Rule: register only before input admission / game load
                if (Current.ProgramState == ProgramState.Playing && Current.Game != null && trustedSimulationReady)
                {
                    RevokeReadiness("Authority modification attempted after game load and input admission.");
                    return "ERROR: Cannot register or modify AuthorityBundle after game load and input admission. Worker reset required.";
                }

                var bundle = JsonConvert.DeserializeObject<AuthorityBundle>(arg);
                if (bundle == null)
                {
                    RevokeReadiness("Failed to parse AuthorityBundle JSON.");
                    return "ERROR: Failed to parse AuthorityBundle JSON.";
                }

                if (string.IsNullOrEmpty(bundle.authorityId))
                {
                    RevokeReadiness("AuthorityBundle requires a non-empty AuthorityId.");
                    return "ERROR: AuthorityBundle requires a non-empty AuthorityId.";
                }

                if (bundle.manifestVersion != "4.0")
                {
                    RevokeReadiness($"Unsupported manifest version '{bundle.manifestVersion}' (Expected: 4.0).");
                    return $"ERROR: Unsupported manifest version '{bundle.manifestVersion}' (Expected: 4.0).";
                }

                if (string.IsNullOrEmpty(bundle.expectedManifestHash) || bundle.expectedManifestHash.Length != 64)
                {
                    RevokeReadiness("AuthorityBundle requires a valid 64-char SHA-256 ExpectedManifestHash.");
                    return "ERROR: AuthorityBundle requires a valid 64-char SHA-256 ExpectedManifestHash.";
                }

                if (string.IsNullOrEmpty(bundle.expectedSourceArtifactHash) || bundle.expectedSourceArtifactHash.Length != 64)
                {
                    RevokeReadiness("AuthorityBundle requires a valid 64-char SHA-256 ExpectedSourceArtifactHash.");
                    return "ERROR: AuthorityBundle requires a valid 64-char SHA-256 ExpectedSourceArtifactHash.";
                }

                if (string.IsNullOrEmpty(bundle.storeIncarnation))
                {
                    RevokeReadiness("AuthorityBundle requires a non-empty storeIncarnation.");
                    return "ERROR: AuthorityBundle requires a non-empty storeIncarnation.";
                }

                if (string.IsNullOrEmpty(bundle.baseLineage))
                {
                    RevokeReadiness("AuthorityBundle requires a non-empty baseLineage.");
                    return "ERROR: AuthorityBundle requires a non-empty baseLineage.";
                }

                // Actual ContentProfile binding
                if (string.IsNullOrEmpty(bundle.contentProfileFingerprint) || bundle.contentProfileFingerprint == "UNKNOWN_PROFILE")
                {
                    RevokeReadiness("AuthorityBundle contains unadmitted UNKNOWN_PROFILE (G05-S02).");
                    return "ERROR: UNKNOWN_PROFILE is unadmitted. Full content profile required.";
                }
                if (bundle.contentProfileFingerprint.Length != 64)
                {
                    RevokeReadiness("AuthorityBundle contentProfileFingerprint must be 64-char SHA256.");
                    return "ERROR: contentProfileFingerprint must be 64-char SHA256.";
                }

                ContentProfileProvider.InvalidateCache();
                string activeProfile;
                try
                {
                    activeProfile = GetActualContentProfileFingerprint();
                }
                catch (Exception ex)
                {
                    RevokeReadiness($"ContentProfile computation failed: {ex.Message}");
                    return $"ERROR: ContentProfile computation failed: {ex.Message}";
                }

                if (bundle.contentProfileFingerprint != activeProfile)
                {
                    RevokeReadiness($"ContentProfileFingerprint mismatch. Active={activeProfile}, Provided={bundle.contentProfileFingerprint}");
                    return $"ERROR: ContentProfileFingerprint mismatch. Active={activeProfile}, Provided={bundle.contentProfileFingerprint}";
                }

                if (bundle.allowedOperationMode != "SIMULATION" && bundle.allowedOperationMode != "READ_ONLY")
                {
                    RevokeReadiness($"Invalid allowedOperationMode '{bundle.allowedOperationMode}'. Must be SIMULATION or READ_ONLY.");
                    return $"ERROR: Invalid allowedOperationMode '{bundle.allowedOperationMode}'. Must be SIMULATION or READ_ONLY.";
                }

                // Immutable Authority check (Requirement 7)
                if (registeredAuthority != null)
                {
                    // Same AuthorityId + byte/canonical identical bundle may idempotently ACK
                    if (registeredAuthority.authorityId == bundle.authorityId)
                    {
                        if (registeredAuthority.expectedSourceArtifactHash == bundle.expectedSourceArtifactHash &&
                            registeredAuthority.expectedManifestHash == bundle.expectedManifestHash &&
                            registeredAuthority.contentProfileFingerprint == bundle.contentProfileFingerprint &&
                            registeredAuthority.targetMapId == bundle.targetMapId &&
                            registeredAuthority.workerGeneration == bundle.workerGeneration &&
                            registeredAuthority.allowedOperationMode == bundle.allowedOperationMode &&
                            registeredAuthority.targetScopeId == bundle.targetScopeId &&
                            registeredAuthority.storeIncarnation == bundle.storeIncarnation &&
                            registeredAuthority.baseLineage == bundle.baseLineage &&
                            registeredAuthority.manifestVersion == bundle.manifestVersion)
                        {
                            return $"AUTHORITY_ACK_UNCHANGED: Id={bundle.authorityId}, ExpectedHash={bundle.expectedManifestHash}, Gen={bundle.workerGeneration}, Map={bundle.targetMapId}";
                        }
                        else
                        {
                            RevokeReadiness("AuthorityId re-registration with modified parameters detected without reset.");
                            return "ERROR: AuthorityId already registered with different bundle parameters. In-place overwrite prohibited.";
                        }
                    }
                    else
                    {
                        RevokeReadiness("Different AuthorityId registration attempted on active worker without reset.");
                        return "ERROR: Authority already registered for this generation. Reset worker required before registering a new AuthorityId.";
                    }
                }

                registeredAuthority = bundle;
                registeredAuthorityJson = arg.Trim();
                Log.Message($"[WorkerBridge] Registered AuthorityBundle: Id={bundle.authorityId}, ExpectedHash={bundle.expectedManifestHash}, Gen={bundle.workerGeneration}, Map={bundle.targetMapId}");

                return $"AUTHORITY_REGISTERED: Id={bundle.authorityId}, ExpectedHash={bundle.expectedManifestHash}, Gen={bundle.workerGeneration}, Map={bundle.targetMapId}";
            }
            catch (Exception ex)
            {
                RevokeReadiness($"RegisterAuthority exception: {ex.Message}");
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

        private string HandleRegisterGrant(string arg)
        {
            try
            {
                if (string.IsNullOrEmpty(arg))
                {
                    RevokeReadiness("Missing SimulationGrant JSON payload.");
                    return "ERROR: Missing SimulationGrant JSON payload.";
                }

                if (registeredAuthority == null)
                {
                    RevokeReadiness("Cannot register simulation grant before authority bundle is established.");
                    return "ERROR: Cannot register simulation grant before authority bundle is established.";
                }

                var grant = JsonConvert.DeserializeObject<SimulationGrant>(arg);
                if (grant == null)
                {
                    RevokeReadiness("Failed to parse SimulationGrant JSON.");
                    return "ERROR: Failed to parse SimulationGrant JSON.";
                }

                if (string.IsNullOrEmpty(grant.grantId))
                {
                    RevokeReadiness("SimulationGrant requires a non-empty GrantId.");
                    return "ERROR: SimulationGrant requires a non-empty GrantId.";
                }

                if (grant.authorityId != registeredAuthority.authorityId)
                {
                    RevokeReadiness($"Grant authorityId '{grant.authorityId}' does not match registered authority '{registeredAuthority.authorityId}'");
                    return $"ERROR: Grant authorityId '{grant.authorityId}' does not match registered authority '{registeredAuthority.authorityId}'.";
                }

                long expectedGen = registeredAuthority.workerGeneration;
                if (grant.workerGeneration != expectedGen)
                {
                    RevokeReadiness($"Grant generation {grant.workerGeneration} does not match expected generation {expectedGen}");
                    return $"ERROR: Grant generation {grant.workerGeneration} does not match expected generation {expectedGen}.";
                }

                if (grant.targetMapIndex != registeredAuthority.targetMapId)
                {
                    RevokeReadiness($"Grant targetMapIndex {grant.targetMapIndex} does not match authority targetMapId {registeredAuthority.targetMapId}");
                    return $"ERROR: Grant targetMapIndex {grant.targetMapIndex} does not match authority targetMapId {registeredAuthority.targetMapId}.";
                }

                if (grant.scopeId != registeredAuthority.targetScopeId)
                {
                    RevokeReadiness($"Grant scopeId '{grant.scopeId}' does not match authority targetScopeId '{registeredAuthority.targetScopeId}'");
                    return $"ERROR: Grant scopeId '{grant.scopeId}' does not match authority targetScopeId '{registeredAuthority.targetScopeId}'.";
                }

                if (grant.allowedMode != "SIMULATION" && grant.allowedMode != "READ_ONLY")
                {
                    RevokeReadiness($"Invalid allowedMode '{grant.allowedMode}' in grant. Must be SIMULATION or READ_ONLY.");
                    return $"ERROR: Invalid allowedMode '{grant.allowedMode}' in grant. Must be SIMULATION or READ_ONLY.";
                }

                // Gate 05 Requirement 8: Changing grant after stage/receipt invalidates task/receipt/promotion
                currentValidatorTask = null;
                currentValidatorTaskJson = "";
                currentValidatorTaskPath = "";
                currentStageValidationReceipt = null;
                ticksSimulatedUnderGrant = 0;
                if (semanticState == SemanticApprovalState.STAGED_VALIDATED || semanticState == SemanticApprovalState.STAGED_PENDING_VALIDATION)
                {
                    semanticState = SemanticApprovalState.RESULT_SEALED;
                }

                activeGrant = grant;
                activeGrantJson = arg.Trim();
                Log.Message($"[WorkerBridge] Registered SimulationGrant: GrantId={grant.grantId}, AuthorityId={grant.authorityId}, Scope={grant.scopeId}, Mode={grant.allowedMode}, Gen={grant.workerGeneration}, Budget={grant.tickBudget}");

                return $"GRANT_REGISTERED: GrantId={grant.grantId}, AuthorityId={grant.authorityId}, Scope={grant.scopeId}, Mode={grant.allowedMode}, Gen={grant.workerGeneration}, Budget={grant.tickBudget}";
            }
            catch (Exception ex)
            {
                RevokeReadiness($"RegisterGrant exception: {ex.Message}");
                return $"ERROR: RegisterGrant exception: {ex.Message}";
            }
        }

        private string HandleGetGrant()
        {
            if (activeGrant == null)
            {
                return "ERROR: No SimulationGrant currently registered.";
            }
            return JsonConvert.SerializeObject(activeGrant, Newtonsoft.Json.Formatting.Indented);
        }

        private string HandleResetWorker()
        {
            registeredAuthority = null;
            registeredAuthorityJson = "";
            activeGrant = null;
            activeGrantJson = "";
            ticksSimulatedUnderGrant = 0;
            sealedResult = null;
            currentValidatorTask = null;
            currentValidatorTaskJson = "";
            currentValidatorTaskPath = "";
            currentStageValidationReceipt = null;
            lastStagedPath = "";
            lastStagedSha = "";
            registeredValidatorProcessId = 0;
            registeredValidatorStartTime = "";
            registeredValidatorExecutable = "";
            ContentProfileProvider.InvalidateCache();
            trustedSimulationReady = false;
            semanticState = SemanticApprovalState.NONE;
            // Preserves monotonic currentGeneration across resets
            currentResultEpoch = 0;
            lastFailureReason = "";
            Log.Message($"[WorkerBridge] Worker reset cleanly. Current generation: {currentGeneration}.");
            return "OK: Worker reset cleanly.";
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
            currentStageValidationReceipt = null;
            semanticState = SemanticApprovalState.NONE;

            // Check Authority Source Artifact SHA if registered
            string savePath = GenFilePaths.FilePathForSavedGame(saveName);
            if (!File.Exists(savePath))
            {
                lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                lastFailureReason = $"Save file not found at '{savePath}'";
                return $"LOAD_REJECTED: Save file not found.";
            }

            if (registeredAuthority == null)
            {
                lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                lastFailureReason = "Cannot load save without pre-registered AuthorityBundle.";
                return "LOAD_REJECTED: No AuthorityBundle registered.";
            }

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
                RevokeReadiness(lastFailureReason);
                return $"LOAD_REJECTED: Source artifact SHA mismatch. Expected {registeredAuthority.expectedSourceArtifactHash}, got {actualSaveSha}";
            }

            ContentProfileProvider.InvalidateCache();
            string actualProfile;
            try
            {
                actualProfile = GetActualContentProfileFingerprint();
            }
            catch (Exception ex)
            {
                lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                lastFailureReason = $"ContentProfile computation failed: {ex.Message}";
                RevokeReadiness(lastFailureReason);
                return $"LOAD_REJECTED: {lastFailureReason}";
            }

            if (registeredAuthority.contentProfileFingerprint != actualProfile)
            {
                lifecycleState = WorkerLifecycleState.LOAD_FAILED;
                lastFailureReason = "ContentProfileFingerprint mismatch at load time.";
                RevokeReadiness(lastFailureReason);
                return "LOAD_REJECTED: ContentProfileFingerprint mismatch.";
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
                RevokeReadiness("No AuthorityBundle registered.");
                return "ERROR: No AuthorityBundle registered. Control plane must register authority before input admission.";
            }

            if (registeredAuthority.workerGeneration != currentGeneration)
            {
                RevokeReadiness($"Authority generation mismatch (AuthorityGen={registeredAuthority.workerGeneration}, CurrentGen={currentGeneration}).");
                return $"ERROR: Authority generation mismatch (AuthorityGen={registeredAuthority.workerGeneration}, CurrentGen={currentGeneration}).";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            if (registeredAuthority.targetMapId != mapIdx)
            {
                RevokeReadiness($"Authority target map mismatch (AuthorityMap={registeredAuthority.targetMapId}, CurrentMap={mapIdx}).");
                return $"ERROR: Authority target map mismatch (AuthorityMap={registeredAuthority.targetMapId}, CurrentMap={mapIdx}).";
            }

            if (registeredAuthority.contentProfileFingerprint != GetActualContentProfileFingerprint())
            {
                RevokeReadiness("ContentProfileFingerprint mismatch during input validation.");
                return "INPUT_REJECTED: ContentProfileFingerprint mismatch.";
            }

            // Re-verify active source file on disk
            string savePath = GenFilePaths.FilePathForSavedGame(activeSaveName);
            if (File.Exists(savePath))
            {
                string diskSha;
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(savePath))
                {
                    diskSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
                if (diskSha != registeredAuthority.expectedSourceArtifactHash)
                {
                    RevokeReadiness($"Source artifact SHA mismatch on disk (Expected {registeredAuthority.expectedSourceArtifactHash}, got {diskSha}).");
                    return $"INPUT_REJECTED: Source artifact SHA mismatch.";
                }
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
                string expectedHash = registeredAuthority.expectedManifestHash;
                RevokeReadiness($"Hash mismatch. Expected {expectedHash}, got {liveHash}");
                Log.Warning($"[WorkerBridge] INPUT_REJECTED: Expected {expectedHash}, got {liveHash}");
                return $"INPUT_REJECTED: Hash mismatch. Expected {expectedHash}, got {liveHash}";
            }
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

            if (!trustedSimulationReady || semanticState == SemanticApprovalState.VALIDATION_FAILED)
            {
                return "ERROR: Cannot simulate untrusted state. Must pass VALIDATE_INPUT against registered authority first.";
            }

            if (registeredAuthority == null || activeGrant == null)
            {
                return "ERROR: No authorized simulation grant registered.";
            }

            if (registeredAuthority.allowedOperationMode == "READ_ONLY" || activeGrant.allowedMode == "READ_ONLY")
            {
                return "ERROR: OPERATION_NOT_PERMITTED_IN_READ_ONLY_MODE: Simulation is prohibited under READ_ONLY grant.";
            }

            if (registeredAuthority.contentProfileFingerprint != GetActualContentProfileFingerprint())
            {
                RevokeReadiness("ContentProfileFingerprint mismatch during simulation start.");
                return "ERROR: ContentProfileFingerprint mismatch.";
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

            if (!trustedSimulationReady || semanticState == SemanticApprovalState.VALIDATION_FAILED)
            {
                return "ERROR: Cannot simulate untrusted state. Must pass VALIDATE_INPUT against registered authority first.";
            }

            if (registeredAuthority == null || activeGrant == null)
            {
                return "ERROR: No authorized simulation grant registered.";
            }

            if (activeGrant.scopeId != registeredAuthority.targetScopeId)
            {
                RevokeReadiness($"Grant scope mismatch during step ticks (GrantScope={activeGrant.scopeId}, AuthScope={registeredAuthority.targetScopeId}).");
                return "ERROR: Grant scope mismatch during step ticks.";
            }

            if (registeredAuthority.allowedOperationMode == "READ_ONLY" || activeGrant.allowedMode == "READ_ONLY")
            {
                return "ERROR: OPERATION_NOT_PERMITTED_IN_READ_ONLY_MODE: Sliced simulation is prohibited under READ_ONLY grant.";
            }

            if (registeredAuthority.contentProfileFingerprint != GetActualContentProfileFingerprint())
            {
                RevokeReadiness("ContentProfileFingerprint mismatch during step ticks.");
                return "ERROR: ContentProfileFingerprint mismatch.";
            }

            string[] parts = arg.Split(' ');
            if (!int.TryParse(parts[0], out int count) || count <= 0)
            {
                return "ERROR: Invalid tick count. Usage: STEP_TICKS <Count> [maxPerSlice=10]";
            }

            // Gate 05 Requirement 8: Enforce tickBudget if defined (> 0)
            if (activeGrant.tickBudget > 0 && (ticksSimulatedUnderGrant + count > activeGrant.tickBudget))
            {
                return $"ERROR: TICK_BUDGET_EXCEEDED: Requested {count} ticks exceeds remaining grant budget ({Math.Max(0, activeGrant.tickBudget - ticksSimulatedUnderGrant)} remaining of {activeGrant.tickBudget}).";
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

            if (!trustedSimulationReady || semanticState == SemanticApprovalState.VALIDATION_FAILED)
            {
                return "ERROR: Cannot simulate untrusted state. Must pass VALIDATE_INPUT first.";
            }

            if (registeredAuthority == null || activeGrant == null)
            {
                return "ERROR: No authorized simulation grant registered.";
            }

            if (activeGrant.scopeId != registeredAuthority.targetScopeId)
            {
                RevokeReadiness($"Grant scope mismatch during diagnostic run (GrantScope={activeGrant.scopeId}, AuthScope={registeredAuthority.targetScopeId}).");
                return "ERROR: Grant scope mismatch during diagnostic run.";
            }

            if (registeredAuthority.allowedOperationMode == "READ_ONLY" || activeGrant.allowedMode == "READ_ONLY")
            {
                return "ERROR: OPERATION_NOT_PERMITTED_IN_READ_ONLY_MODE: Diagnostic run is prohibited under READ_ONLY grant.";
            }

            if (!int.TryParse(arg, out int count) || count <= 0)
            {
                return "ERROR: Invalid tick count. Usage: QA_DIAGNOSTIC_RUN_TICKS <positive integer>";
            }

            if (activeGrant.tickBudget > 0 && (ticksSimulatedUnderGrant + count > activeGrant.tickBudget))
            {
                return $"ERROR: TICK_BUDGET_EXCEEDED: Requested {count} ticks exceeds remaining grant budget ({Math.Max(0, activeGrant.tickBudget - ticksSimulatedUnderGrant)} remaining of {activeGrant.tickBudget}).";
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

        private string HandleSealResult(string grantId)
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"ERROR: Worker is not READY (State={lifecycleState}). Cannot seal result.";
            }

            if (!trustedSimulationReady || semanticState == SemanticApprovalState.VALIDATION_FAILED)
            {
                return "ERROR: Untrusted state. Cannot seal simulation result without valid input admission.";
            }

            if (registeredAuthority == null)
            {
                return "ERROR: No registered authority bundle.";
            }

            if (activeGrant == null)
            {
                RevokeReadiness("No active SimulationGrant registered.");
                return "ERROR: No registered simulation grant matches grantId (No active grant registered).";
            }

            string gid = grantId?.Trim() ?? "";
            if (string.IsNullOrEmpty(gid))
            {
                RevokeReadiness("Blank grant ID rejected at seal boundary.");
                return "ERROR: Missing grantId: grant ID cannot be blank.";
            }

            if (gid != activeGrant.grantId)
            {
                RevokeReadiness($"Grant ID '{gid}' does not match registered active grant '{activeGrant.grantId}'.");
                return $"ERROR: No registered simulation grant matches grantId '{gid}' (Expected '{activeGrant.grantId}').";
            }

            if (activeGrant.authorityId != registeredAuthority.authorityId)
            {
                RevokeReadiness($"Grant authority '{activeGrant.authorityId}' does not match registered authority '{registeredAuthority.authorityId}'.");
                return "ERROR: Cross-authority grant detected.";
            }

            if (activeGrant.workerGeneration != currentGeneration)
            {
                RevokeReadiness($"Grant generation {activeGrant.workerGeneration} does not match current generation {currentGeneration}.");
                return "ERROR: Stale simulation grant detected.";
            }

            if (activeGrant.scopeId != registeredAuthority.targetScopeId)
            {
                RevokeReadiness($"Grant scopeId '{activeGrant.scopeId}' does not match authority targetScopeId '{registeredAuthority.targetScopeId}'.");
                return "ERROR: Scope mismatch between grant and authority.";
            }

            if (activeGrant.allowedMode == "READ_ONLY" || registeredAuthority.allowedOperationMode == "READ_ONLY")
            {
                RevokeReadiness("Attempted to seal simulation result under READ_ONLY mode.");
                return "ERROR: OPERATION_NOT_PERMITTED_IN_READ_ONLY_MODE: Cannot seal simulation result with READ_ONLY grant.";
            }

            if (registeredAuthority.contentProfileFingerprint != GetActualContentProfileFingerprint())
            {
                RevokeReadiness("ContentProfileFingerprint mismatch during seal.");
                return "ERROR: ContentProfileFingerprint mismatch.";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            if (registeredAuthority.targetMapId != mapIdx || activeGrant.targetMapIndex != mapIdx)
            {
                RevokeReadiness($"TargetMap mismatch during seal (TargetMap={mapIdx}, AuthMap={registeredAuthority.targetMapId}, GrantMap={activeGrant.targetMapIndex}).");
                return "ERROR: Target map mismatch during seal.";
            }

            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            var liveCensus = EngineHostCensus.GenerateCensus(map);
            string sealedHash = liveCensus.ComputeManifestHash();

            // RESEAL INVALIDATES PREVIOUS STAGED RECEIPTS AND TASKS
            currentStageValidationReceipt = null;
            currentValidatorTask = null;
            currentValidatorTaskJson = "";
            currentValidatorTaskPath = "";
            lastStagedPath = "";
            lastStagedSha = "";

            currentResultEpoch++;
            string sealedResultId = $"SEAL_E{currentResultEpoch}_{Guid.NewGuid():N}";

            var res = new ResultManifest
            {
                sealedResultId = sealedResultId,
                grantId = activeGrant.grantId,
                authorityId = registeredAuthority.authorityId,
                storeIncarnation = registeredAuthority.storeIncarnation,
                baseLineage = registeredAuthority.baseLineage,
                manifestVersion = registeredAuthority.manifestVersion,
                sealedManifestHash = sealedHash,
                contentProfileFingerprint = GetActualContentProfileFingerprint(),
                targetScopeId = registeredAuthority.targetScopeId,
                workerGeneration = currentGeneration,
                targetMapId = mapIdx,
                ticksGame = Find.TickManager.TicksGame,
                resultEpoch = currentResultEpoch,
                sealedAt = DateTime.UtcNow.ToString("O"),
                sourceArtifactHash = registeredAuthority.expectedSourceArtifactHash,
                manifestJson = liveCensus.ToJson()
            };

            sealedResult = res;
            semanticState = SemanticApprovalState.RESULT_SEALED;
            lastValidationSummary = $"RESULT_SEALED: Epoch={currentResultEpoch}, SealedResultId={sealedResultId}, Hash={sealedHash}, Ticks={res.ticksGame}.";
            Log.Message($"[WorkerBridge] RESULT_SEALED: Epoch={currentResultEpoch}, SealedResultId={sealedResultId}, Grant={res.grantId}, Hash={sealedHash}, Ticks={res.ticksGame}, Gen={currentGeneration}");

            return $"RESULT_SEALED: Epoch={currentResultEpoch}, SealedResultId={sealedResultId}, Grant={res.grantId}, ManifestHash={sealedHash}, Ticks={res.ticksGame}, Gen={currentGeneration}";
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
                RevokeReadiness($"Generation mismatch during stage-save (ApprovedGen={sealedResult.workerGeneration}, CurrentGen={currentGeneration}).");
                return $"STAGE_BLOCKED: Generation mismatch (ApprovedGen={sealedResult.workerGeneration}, CurrentGen={currentGeneration}).";
            }

            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            if (mapIdx != sealedResult.targetMapId)
            {
                RevokeReadiness($"TargetMap mismatch during stage-save (ApprovedMap={sealedResult.targetMapId}, CurrentMap={mapIdx}).");
                return $"STAGE_BLOCKED: TargetMap mismatch (ApprovedMap={sealedResult.targetMapId}, CurrentMap={mapIdx}).";
            }

            int curTicks = Find.TickManager.TicksGame;
            if (curTicks != sealedResult.ticksGame)
            {
                RevokeReadiness($"Tick mismatch during stage-save (SealedTicks={sealedResult.ticksGame}, CurrentTicks={curTicks}).");
                return $"STAGE_BLOCKED: Tick mismatch (SealedTicks={sealedResult.ticksGame}, CurrentTicks={curTicks}).";
            }

            // Live Recensus immediately before stage-save (Catches same-tick non-tick mutation!)
            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            var liveCensus = EngineHostCensus.GenerateCensus(map);
            string liveHash = liveCensus.ComputeManifestHash();

            if (liveHash != sealedResult.sealedManifestHash)
            {
                // Capture expectedHash before RevokeReadiness clears sealedResult! (Gate 04 G04-07 fix)
                string expectedHash = sealedResult.sealedManifestHash;
                RevokeReadiness($"Live state mutated after result was sealed! SealedHash={expectedHash}, CurrentLiveHash={liveHash}");
                return $"STAGE_BLOCKED: Live state mutated after result was sealed! SealedHash={expectedHash}, CurrentLiveHash={liveHash}";
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
                RevokeReadiness($"Save execution failed with {saveErrors} error(s). Exception: {saveEx?.Message}. FirstLog: {firstSaveError}");
                return $"STAGE_FAILED: Staged save encountered errors. Quarantined. Errors={saveErrors}, Detail={lastFailureReason}";
            }

            // Gate 5: Saved-Byte Proof (Full XML parse to EOF + Deep Saved-Byte Semantic Validation)
            if (!EngineHostCensus.ValidateStagedXml(stagingPath, sealedResult.manifestJson, sealedResult.sealedManifestHash, out string xmlErr, out string stagedHash))
            {
                try { File.Move(stagingPath, quarantinePath); } catch { }
                RevokeReadiness($"Staged XML validation failed: {xmlErr}");
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

            // Gate 05 Requirement 1 & 2: Simulator-Owned ValidatorTask with Protected Result Channel
            string validatorTaskId = $"VT_{DateTime.UtcNow:yyyyMMdd_HHmmss}_{Guid.NewGuid():N}";
            string capabilityNonce;
            string channelSecretToken;
            using (var rng = RandomNumberGenerator.Create())
            {
                byte[] bytes1 = new byte[32];
                rng.GetBytes(bytes1);
                capabilityNonce = BitConverter.ToString(bytes1).Replace("-", "").ToLowerInvariant();

                byte[] bytes2 = new byte[32];
                rng.GetBytes(bytes2);
                channelSecretToken = BitConverter.ToString(bytes2).Replace("-", "").ToLowerInvariant();
            }

            string taskDir = Path.Combine(SafeSaveDataFolderPath, "Tasks");
            if (!Directory.Exists(taskDir))
            {
                Directory.CreateDirectory(taskDir);
            }
            string taskFile = Path.Combine(taskDir, $"{validatorTaskId}.task.json");
            string resultChannelFile = Path.Combine(taskDir, $"{validatorTaskId}.protected_result.json");

            var task = new ValidatorTask
            {
                validatorTaskId = validatorTaskId,
                capabilityNonce = capabilityNonce,
                channelSecretToken = channelSecretToken,
                resultChannelPath = resultChannelFile,
                simulatorProcessId = Process.GetCurrentProcess().Id.ToString(),
                simulatorGeneration = currentGeneration,
                authorityId = registeredAuthority!.authorityId,
                storeIncarnation = registeredAuthority.storeIncarnation,
                baseLineage = registeredAuthority.baseLineage,
                grantId = activeGrant!.grantId,
                workerGeneration = currentGeneration,
                scopeId = registeredAuthority.targetScopeId,
                targetMapIndex = mapIdx,
                allowedMode = "READ_ONLY",
                contentProfileFingerprint = GetActualContentProfileFingerprint(),
                sourceArtifactHash = registeredAuthority.expectedSourceArtifactHash,
                manifestVersion = registeredAuthority.manifestVersion,
                sealedResultId = sealedResult!.sealedResultId,
                resultEpoch = sealedResult.resultEpoch,
                sealedManifestHash = sealedResult.sealedManifestHash,
                stagedFilePath = stagingPath,
                stagedSha = stagedSha,
                createdAtUtc = DateTime.UtcNow.ToString("O"),
                isConsumed = false
            };

            File.WriteAllText(taskFile, JsonConvert.SerializeObject(task, Newtonsoft.Json.Formatting.Indented));

            currentValidatorTask = task;
            currentValidatorTaskPath = taskFile;
            currentValidatorTaskJson = JsonConvert.SerializeObject(task, Newtonsoft.Json.Formatting.Indented);
            operatorChannelSecretToken = channelSecretToken;
            currentStageValidationReceipt = null;
            semanticState = SemanticApprovalState.STAGED_PENDING_VALIDATION;

            Log.Message($"[WorkerBridge] STAGED_OK: '{stagingPath}', StagedSha={stagedSha}, ManifestHash={stagedHash}, Epoch={sealedResult.resultEpoch}, TaskId={validatorTaskId}");
            return $"STAGED_OK: File='{stagingPath}', StagingName='{stagingSaveName}', StagedSha={stagedSha}, SealedResultId={sealedResult.sealedResultId}, Epoch={sealedResult.resultEpoch}, ManifestHash={stagedHash}, ValidatorTaskId={validatorTaskId}, TaskPath='{taskFile}', ResultChannel='{resultChannelFile}'";
        }

        private string HandleGetActiveValidatorTask()
        {
            if (currentValidatorTask == null)
            {
                return "ERROR: No active ValidatorTask issued.";
            }
            var publicTask = new
            {
                validatorTaskId = currentValidatorTask.validatorTaskId,
                capabilityNonce = "[REDACTED_PROTECTED_OPERATOR_CAPABILITY]",
                channelSecretToken = "[REDACTED_PROTECTED_CHANNEL_SECRET]",
                resultChannelPath = currentValidatorTask.resultChannelPath,
                simulatorProcessId = currentValidatorTask.simulatorProcessId,
                simulatorGeneration = currentValidatorTask.simulatorGeneration,
                authorityId = currentValidatorTask.authorityId,
                storeIncarnation = currentValidatorTask.storeIncarnation,
                baseLineage = currentValidatorTask.baseLineage,
                grantId = currentValidatorTask.grantId,
                workerGeneration = currentValidatorTask.workerGeneration,
                scopeId = currentValidatorTask.scopeId,
                targetMapIndex = currentValidatorTask.targetMapIndex,
                allowedMode = currentValidatorTask.allowedMode,
                contentProfileFingerprint = currentValidatorTask.contentProfileFingerprint,
                sourceArtifactHash = currentValidatorTask.sourceArtifactHash,
                manifestVersion = currentValidatorTask.manifestVersion,
                sealedResultId = currentValidatorTask.sealedResultId,
                resultEpoch = currentValidatorTask.resultEpoch,
                sealedManifestHash = currentValidatorTask.sealedManifestHash,
                stagedFilePath = currentValidatorTask.stagedFilePath,
                stagedSha = currentValidatorTask.stagedSha,
                createdAtUtc = currentValidatorTask.createdAtUtc,
                isConsumed = currentValidatorTask.isConsumed,
                registeredValidatorProcessId = currentValidatorTask.registeredValidatorProcessId,
                registeredValidatorStartTimeUtc = currentValidatorTask.registeredValidatorStartTimeUtc,
                registeredValidatorExecutable = currentValidatorTask.registeredValidatorExecutable
            };
            return JsonConvert.SerializeObject(publicTask, Newtonsoft.Json.Formatting.Indented);
        }

        private string HandleRegisterValidatorProcess(string arg)
        {
            RevokeReadiness("Public caller registration of validator process is prohibited (MD-126/127). Simulator/operator must launch and own the validator process.");
            return "ERROR: REGISTER_VALIDATOR_PROCESS by public caller is prohibited under Gate05-R2 (MD-126/MD-127). Validator process must be launched and owned by operator/simulator directly.";
        }

        private string HandleLaunchOperatorValidator(string arg)
        {
            try
            {
                if (currentValidatorTask == null)
                {
                    RevokeReadiness("No active ValidatorTask outstanding to launch validator for.");
                    return "ERROR: No active ValidatorTask issued.";
                }

                if (currentValidatorTask.isConsumed)
                {
                    RevokeReadiness("Attempted to launch validator for already consumed ValidatorTask.");
                    return "ERROR: ValidatorTask already consumed.";
                }

                if (string.IsNullOrEmpty(arg))
                {
                    RevokeReadiness("Missing arguments for LAUNCH_OPERATOR_VALIDATOR.");
                    return "ERROR: Usage: LAUNCH_OPERATOR_VALIDATOR <operatorCapabilityNonce> <executablePath> [arguments]";
                }

                // Operator capability nonce authorization check (MD-126/127)
                string trimmed = arg.Trim();
                int firstSpace = trimmed.IndexOf(' ');
                if (firstSpace <= 0)
                {
                    RevokeReadiness("Missing capability nonce or executable path in LAUNCH_OPERATOR_VALIDATOR.");
                    return "ERROR: Usage: LAUNCH_OPERATOR_VALIDATOR <operatorCapabilityNonce> <executablePath> [arguments]";
                }

                string providedNonce = trimmed.Substring(0, firstSpace);
                string remaining = trimmed.Substring(firstSpace + 1).Trim();

                if (providedNonce != currentValidatorTask.capabilityNonce)
                {
                    RevokeReadiness("Operator capability nonce verification failed for LAUNCH_OPERATOR_VALIDATOR (MD-126/127). Public requester launch prohibited.");
                    return "ERROR: Unauthorized: CapabilityNonce mismatch.";
                }

                string exePath = "";
                string args = "";
                if (remaining.StartsWith("\""))
                {
                    int endQuote = remaining.IndexOf('\"', 1);
                    if (endQuote > 1)
                    {
                        exePath = remaining.Substring(1, endQuote - 1);
                        args = remaining.Substring(endQuote + 1).Trim();
                    }
                    else
                    {
                        exePath = remaining.Trim('\"');
                    }
                }
                else
                {
                    int spaceIdx = remaining.IndexOf(' ');
                    if (spaceIdx > 0)
                    {
                        exePath = remaining.Substring(0, spaceIdx);
                        args = remaining.Substring(spaceIdx + 1).Trim();
                    }
                    else
                    {
                        exePath = remaining;
                    }
                }

                if (!File.Exists(exePath))
                {
                    RevokeReadiness($"Validator executable not found at '{exePath}'.");
                    return $"ERROR: Validator executable not found at '{exePath}'.";
                }

                var psi = new ProcessStartInfo
                {
                    FileName = exePath,
                    Arguments = args,
                    CreateNoWindow = true,
                    UseShellExecute = false
                };

                Process proc = Process.Start(psi);
                if (proc == null || proc.HasExited)
                {
                    RevokeReadiness($"Failed to start operator validator process from '{exePath}'.");
                    return "ERROR: Failed to start operator validator process.";
                }

                int myPid = Process.GetCurrentProcess().Id;
                if (proc.Id == myPid)
                {
                    RevokeReadiness("Self-validation prohibited. Validator PID cannot equal simulator PID.");
                    return "ERROR: Self-validation prohibited. Validator PID cannot equal simulator PID.";
                }

                string procStartTime = "";
                try
                {
                    procStartTime = proc.StartTime.ToUniversalTime().ToString("O");
                }
                catch
                {
                    procStartTime = DateTime.UtcNow.ToString("O");
                }

                operatorLaunchedValidatorProcess = proc;
                operatorLaunchedValidatorPid = proc.Id;
                operatorLaunchedValidatorStartTimeUtc = procStartTime;
                operatorLaunchedValidatorExecutable = exePath;

                registeredValidatorProcessId = proc.Id;
                registeredValidatorStartTime = procStartTime;
                registeredValidatorExecutable = exePath;

                currentValidatorTask.registeredValidatorProcessId = proc.Id.ToString();
                currentValidatorTask.registeredValidatorStartTimeUtc = procStartTime;
                currentValidatorTask.registeredValidatorExecutable = exePath;

                Log.Message($"[WorkerBridge] OPERATOR_VALIDATOR_LAUNCHED: TaskId={currentValidatorTask.validatorTaskId}, Pid={proc.Id}, StartTime={procStartTime}, Exe='{exePath}'");
                return $"OPERATOR_VALIDATOR_LAUNCHED: TaskId={currentValidatorTask.validatorTaskId}, Pid={proc.Id}, StartTime={procStartTime}, Exe='{exePath}'";
            }
            catch (Exception ex)
            {
                RevokeReadiness($"LaunchOperatorValidator exception: {ex.Message}");
                return $"ERROR: LaunchOperatorValidator exception: {ex.Message}";
            }
        }

        public static string BindOperatorLaunchedProcess(WorkerBridgeComponent comp, Process proc, string exePath, string capabilityNonce)
        {
            if (comp is null || comp.currentValidatorTask == null) return "ERROR: No active ValidatorTask";
            if (string.IsNullOrEmpty(capabilityNonce) || comp.currentValidatorTask.capabilityNonce != capabilityNonce)
            {
                comp.RevokeReadiness("BindOperatorLaunchedProcess authorization failed: CapabilityNonce mismatch.");
                return "ERROR: CapabilityNonce mismatch.";
            }
            if (proc == null || proc.HasExited) return "ERROR: Process null or exited";
            int myPid = Process.GetCurrentProcess().Id;
            if (proc.Id == myPid)
            {
                comp.RevokeReadiness("Self-validation prohibited.");
                return "ERROR: Self-validation prohibited.";
            }
            string procStartTime = "";
            try { procStartTime = proc.StartTime.ToUniversalTime().ToString("O"); }
            catch { procStartTime = DateTime.UtcNow.ToString("O"); }

            comp.operatorLaunchedValidatorProcess = proc;
            comp.operatorLaunchedValidatorPid = proc.Id;
            comp.operatorLaunchedValidatorStartTimeUtc = procStartTime;
            comp.operatorLaunchedValidatorExecutable = exePath;
            comp.registeredValidatorProcessId = proc.Id;
            comp.registeredValidatorStartTime = procStartTime;
            comp.registeredValidatorExecutable = exePath;
            comp.currentValidatorTask.registeredValidatorProcessId = proc.Id.ToString();
            comp.currentValidatorTask.registeredValidatorStartTimeUtc = procStartTime;
            comp.currentValidatorTask.registeredValidatorExecutable = exePath;
            return $"OPERATOR_VALIDATOR_LAUNCHED: TaskId={comp.currentValidatorTask.validatorTaskId}, Pid={proc.Id}, StartTime={procStartTime}, Exe='{exePath}'";
        }

        public static string BindOperatorLaunchedProcess(WorkerBridgeComponent comp, Process proc, string exePath)
        {
            if (comp is null) return "ERROR: WorkerBridgeComponent is null";
            string nonce = comp.currentValidatorTask?.capabilityNonce ?? "";
            return BindOperatorLaunchedProcess(comp, proc, exePath, nonce);
        }

        private string HandleExecuteValidatorTask(string arg)
        {
            try
            {
                string[] parts = arg.Split(' ');
                if (parts.Length < 2)
                {
                    return "ERROR: Usage: EXECUTE_VALIDATOR_TASK <taskFilePath> <capabilityNonce>";
                }

                string taskFilePath = parts[0];
                string capabilityNonce = parts[1];

                if (!File.Exists(taskFilePath))
                {
                    return $"VALIDATION_FAILED: Task file not found at '{taskFilePath}'.";
                }

                var task = JsonConvert.DeserializeObject<ValidatorTask>(File.ReadAllText(taskFilePath));
                if (task == null)
                {
                    return "VALIDATION_FAILED: Failed to deserialize ValidatorTask JSON.";
                }

                if (task.capabilityNonce != capabilityNonce)
                {
                    return "VALIDATION_FAILED: CapabilityNonce mismatch. Unauthorized task execution.";
                }

                string activeProfile = GetActualContentProfileFingerprint();
                if (task.contentProfileFingerprint != activeProfile)
                {
                    return $"VALIDATION_FAILED: ContentProfileFingerprint mismatch. Task={task.contentProfileFingerprint}, Loaded={activeProfile}";
                }

                if (!File.Exists(task.stagedFilePath))
                {
                    return $"VALIDATION_FAILED: Staged file not found at '{task.stagedFilePath}'.";
                }

                string diskSha;
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(task.stagedFilePath))
                {
                    diskSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }

                if (diskSha != task.stagedSha)
                {
                    return $"VALIDATION_FAILED: Staged file SHA mismatch (Expected {task.stagedSha}, got {diskSha}).";
                }

                // Verify that staged save is loaded in validator engine
                string stagingSaveName = Path.GetFileNameWithoutExtension(task.stagedFilePath);
                if (Current.Game == null || Current.ProgramState != ProgramState.Playing || !string.Equals(activeSaveName, stagingSaveName, StringComparison.OrdinalIgnoreCase))
                {
                    return $"VALIDATION_FAILED: Staged save '{stagingSaveName}' must be loaded into validator engine first (Active='{activeSaveName}', Playing={Current.ProgramState == ProgramState.Playing}).";
                }

                if (loadErrorCount > 0)
                {
                    return $"VALIDATION_FAILED: Engine encountered {loadErrorCount} error(s) loading staged save. First: {firstLoadError}";
                }

                if (Current.Game.Maps.NullOrEmpty())
                {
                    return "VALIDATION_FAILED: Engine failed to load maps from staged save.";
                }

                // Saved-byte XML check (G04-02 check)
                if (!EngineHostCensus.ValidateStagedXml(task.stagedFilePath, null, task.sealedManifestHash, out string xmlErr, out string stagedHash))
                {
                    return $"VALIDATION_FAILED: Staged XML validation failed: {xmlErr}";
                }

                int targetMapIdx = Math.Min(task.targetMapIndex, Current.Game.Maps.Count - 1);
                var map = Current.Game.Maps[targetMapIdx];
                var liveCensus = EngineHostCensus.GenerateCensus(map);
                string liveHash = liveCensus.ComputeManifestHash();

                if (liveHash != task.sealedManifestHash)
                {
                    return $"VALIDATION_FAILED: Loaded live manifest hash mismatch: Expected {task.sealedManifestHash}, got {liveHash}";
                }

                string currentPid = Process.GetCurrentProcess().Id.ToString();
                string procStartTime = "";
                try
                {
                    procStartTime = Process.GetCurrentProcess().StartTime.ToUniversalTime().ToString("O");
                }
                catch
                {
                    procStartTime = DateTime.UtcNow.ToString("O");
                }

                string currentExe = "";
                try
                {
                    currentExe = Process.GetCurrentProcess().MainModule?.FileName ?? "";
                }
                catch
                {
                    currentExe = "";
                }

                var result = new ValidatorResult
                {
                    validatorTaskId = task.validatorTaskId,
                    capabilityNonce = capabilityNonce,
                    channelSecretToken = task.channelSecretToken,
                    validatorProcessId = currentPid,
                    validatorProcessStartTimeUtc = procStartTime,
                    validatorExecutable = currentExe,
                    authorityId = task.authorityId,
                    storeIncarnation = task.storeIncarnation,
                    baseLineage = task.baseLineage,
                    grantId = task.grantId,
                    workerGeneration = task.workerGeneration,
                    scopeId = task.scopeId,
                    targetMapIndex = task.targetMapIndex,
                    allowedMode = task.allowedMode,
                    manifestVersion = task.manifestVersion,
                    sealedResultId = task.sealedResultId,
                    resultEpoch = task.resultEpoch,
                    sealedManifestHash = task.sealedManifestHash,
                    sourceArtifactHash = task.sourceArtifactHash,
                    validatorResult = "PASS",
                    actualContentProfileFingerprint = activeProfile,
                    actualManifestHash = liveHash,
                    stagedSha = diskSha,
                    stagedFilePath = task.stagedFilePath,
                    validatedAtUtc = DateTime.UtcNow.ToString("O")
                };

                // G05-S01 / Gate05-R3: Write result directly to operator-owned protected result channel
                string resultFile = !string.IsNullOrEmpty(task.resultChannelPath)
                    ? task.resultChannelPath
                    : Path.Combine(Path.GetDirectoryName(taskFilePath) ?? Path.Combine(SafeSaveDataFolderPath, "Tasks"), $"{task.validatorTaskId}.protected_result.json");
                File.WriteAllText(resultFile, JsonConvert.SerializeObject(result, Newtonsoft.Json.Formatting.Indented));

                return $"VALIDATOR_RESULT: ResultJson={JsonConvert.SerializeObject(result)}, ResultFile='{resultFile}'";
            }
            catch (Exception ex)
            {
                return $"VALIDATION_FAILED: Validator exception: {ex.Message}";
            }
        }

        private string HandleCompleteStageValidation(string arg)
        {
            try
            {
                if (currentValidatorTask == null)
                {
                    RevokeReadiness("No active ValidatorTask outstanding.");
                    return "STAGE_VALIDATION_REJECTED: No active ValidatorTask outstanding.";
                }

                if (currentValidatorTask.isConsumed)
                {
                    RevokeReadiness("Replay of consumed ValidatorTask detected.");
                    return "STAGE_VALIDATION_REJECTED: ValidatorTask already consumed. Replay prohibited.";
                }

                // G05-S01 / MD-127: Reject caller-supplied payload
                if (!string.IsNullOrEmpty(arg) && arg.Trim() != currentValidatorTask.validatorTaskId)
                {
                    if (arg.Trim().StartsWith("{"))
                    {
                        RevokeReadiness("Caller-supplied validation result payload is prohibited (MD-127). Authority must originate from operator-owned validator task and protected channel.");
                        return "STAGE_VALIDATION_REJECTED: Caller-supplied payload prohibited under MD-127.";
                    }
                    else
                    {
                        RevokeReadiness($"ValidatorTaskId mismatch in completion argument (Provided='{arg.Trim()}', Expected='{currentValidatorTask.validatorTaskId}').");
                        return "STAGE_VALIDATION_REJECTED: ValidatorTaskId mismatch.";
                    }
                }

                // Operator must have launched and registered a fresh validator process instance
                int expectedPid = operatorLaunchedValidatorPid > 0 ? operatorLaunchedValidatorPid : registeredValidatorProcessId;
                if (expectedPid <= 0)
                {
                    RevokeReadiness("No operator-owned validator process registered for this task (MD-126/127).");
                    return "STAGE_VALIDATION_REJECTED: No operator-owned validator process registered.";
                }

                // Read result exclusively from protected result channel (No unauthorized fallback paths, MD-126/127)
                string resultFile = currentValidatorTask.resultChannelPath;
                if (string.IsNullOrEmpty(resultFile) || !File.Exists(resultFile))
                {
                    RevokeReadiness("Protected validator result channel file not found at configured path (MD-126/127).");
                    return "STAGE_VALIDATION_REJECTED: Protected validator result channel file not found.";
                }

                ValidatorResult? res;
                try
                {
                    res = JsonConvert.DeserializeObject<ValidatorResult>(File.ReadAllText(resultFile));
                }
                catch (Exception ex)
                {
                    RevokeReadiness($"Failed to parse ValidatorResult JSON from protected channel: {ex.Message}");
                    return "STAGE_VALIDATION_REJECTED: Failed to parse ValidatorResult JSON.";
                }

                if (res == null)
                {
                    RevokeReadiness("Parsed ValidatorResult from protected channel is null.");
                    return "STAGE_VALIDATION_REJECTED: Parsed ValidatorResult is null.";
                }

                // 1. Channel Secret Token check
                if (!string.IsNullOrEmpty(currentValidatorTask.channelSecretToken))
                {
                    if (string.IsNullOrEmpty(res.channelSecretToken) || res.channelSecretToken != currentValidatorTask.channelSecretToken)
                    {
                        RevokeReadiness("Protected result channel secret token mismatch. Forged or unauthorized result origin.");
                        return "STAGE_VALIDATION_REJECTED: Channel secret token mismatch.";
                    }
                }

                // 2. Capability Nonce check
                if (res.capabilityNonce != currentValidatorTask.capabilityNonce)
                {
                    RevokeReadiness("CapabilityNonce mismatch in validator result. Unauthorized completion.");
                    return "STAGE_VALIDATION_REJECTED: CapabilityNonce mismatch.";
                }

                // 3. Exact launched validator PID check
                if (res.validatorProcessId != expectedPid.ToString())
                {
                    RevokeReadiness($"Validator PID mismatch. Expected registered PID {expectedPid}, got {res.validatorProcessId}.");
                    return "STAGE_VALIDATION_REJECTED: Unregistered validator PID.";
                }

                // 4. Exact launched validator Process Start Time check (MD-126/127)
                string expectedStartTime = !string.IsNullOrEmpty(operatorLaunchedValidatorStartTimeUtc)
                    ? operatorLaunchedValidatorStartTimeUtc
                    : registeredValidatorStartTime;
                if (string.IsNullOrEmpty(res.validatorProcessStartTimeUtc) || res.validatorProcessStartTimeUtc != expectedStartTime)
                {
                    RevokeReadiness($"Validator process start time mismatch (Expected={expectedStartTime}, Got={res.validatorProcessStartTimeUtc}). Forged or unregistered process instance.");
                    return "STAGE_VALIDATION_REJECTED: Validator process start time mismatch.";
                }

                // 5. Self-validation check
                string myPid = Process.GetCurrentProcess().Id.ToString();
                if (res.validatorProcessId == myPid)
                {
                    RevokeReadiness("Self-validation or empty validator PID detected!");
                    return "STAGE_VALIDATION_REJECTED: Fresh independent validator required (Self-PID prohibited).";
                }

                // 6. Validator Result verdict check
                if (res.validatorResult != "PASS")
                {
                    RevokeReadiness($"Validator reported failure: {res.validatorResult}");
                    return $"STAGE_VALIDATION_REJECTED: Validator result is '{res.validatorResult}'";
                }

                if (sealedResult == null)
                {
                    RevokeReadiness("No active sealed result to bind against.");
                    return "STAGE_VALIDATION_REJECTED: No active sealed result.";
                }

                // 7. MD-128: Complete Closed-Context Equality (16 distinct authority dimensions)
                if (res.validatorTaskId != currentValidatorTask.validatorTaskId)
                {
                    RevokeReadiness($"ValidatorTaskId mismatch (Provided={res.validatorTaskId}, Expected={currentValidatorTask.validatorTaskId}).");
                    return "STAGE_VALIDATION_REJECTED: ValidatorTaskId mismatch.";
                }
                if (res.stagedFilePath != currentValidatorTask.stagedFilePath)
                {
                    RevokeReadiness("Validator result stagedFilePath mismatch.");
                    return "STAGE_VALIDATION_REJECTED: stagedFilePath mismatch.";
                }
                if (res.stagedSha != currentValidatorTask.stagedSha)
                {
                    RevokeReadiness("Validator result stagedSha mismatch.");
                    return "STAGE_VALIDATION_REJECTED: stagedSha mismatch.";
                }
                if (res.authorityId != currentValidatorTask.authorityId || (registeredAuthority != null && res.authorityId != registeredAuthority.authorityId))
                {
                    RevokeReadiness($"AuthorityId mismatch (Result={res.authorityId}, Task={currentValidatorTask.authorityId}, Registered={(registeredAuthority != null ? registeredAuthority.authorityId : "null")}).");
                    return "STAGE_VALIDATION_REJECTED: AuthorityId mismatch.";
                }
                if (res.storeIncarnation != currentValidatorTask.storeIncarnation || (registeredAuthority != null && res.storeIncarnation != registeredAuthority.storeIncarnation))
                {
                    RevokeReadiness("StoreIncarnation mismatch.");
                    return "STAGE_VALIDATION_REJECTED: StoreIncarnation mismatch.";
                }
                if (res.baseLineage != currentValidatorTask.baseLineage || (registeredAuthority != null && res.baseLineage != registeredAuthority.baseLineage))
                {
                    RevokeReadiness("BaseLineage mismatch.");
                    return "STAGE_VALIDATION_REJECTED: BaseLineage mismatch.";
                }
                if (res.grantId != currentValidatorTask.grantId || (activeGrant != null && res.grantId != activeGrant.grantId))
                {
                    RevokeReadiness("GrantId mismatch.");
                    return "STAGE_VALIDATION_REJECTED: GrantId mismatch.";
                }
                if (res.workerGeneration != currentValidatorTask.workerGeneration || (activeGrant != null && res.workerGeneration != activeGrant.workerGeneration))
                {
                    RevokeReadiness("WorkerGeneration mismatch.");
                    return "STAGE_VALIDATION_REJECTED: WorkerGeneration mismatch.";
                }
                if (res.scopeId != currentValidatorTask.scopeId || (activeGrant != null && res.scopeId != (activeGrant.scopeId ?? "SETTLEMENT-B")))
                {
                    RevokeReadiness("ScopeId mismatch.");
                    return "STAGE_VALIDATION_REJECTED: ScopeId mismatch.";
                }
                if (res.targetMapIndex != currentValidatorTask.targetMapIndex || (activeGrant != null && res.targetMapIndex != activeGrant.targetMapIndex))
                {
                    RevokeReadiness("TargetMapIndex mismatch.");
                    return "STAGE_VALIDATION_REJECTED: TargetMapIndex mismatch.";
                }
                if (res.allowedMode != currentValidatorTask.allowedMode || (activeGrant != null && res.allowedMode != (activeGrant.allowedMode ?? "READ_ONLY")))
                {
                    RevokeReadiness("AllowedMode mismatch.");
                    return "STAGE_VALIDATION_REJECTED: AllowedMode mismatch.";
                }
                if (res.manifestVersion != currentValidatorTask.manifestVersion || res.manifestVersion != sealedResult.manifestVersion)
                {
                    RevokeReadiness("ManifestVersion mismatch.");
                    return "STAGE_VALIDATION_REJECTED: ManifestVersion mismatch.";
                }
                if (res.sealedResultId != currentValidatorTask.sealedResultId || res.sealedResultId != sealedResult.sealedResultId)
                {
                    RevokeReadiness("SealedResultId mismatch.");
                    return "STAGE_VALIDATION_REJECTED: SealedResultId mismatch.";
                }
                if (res.resultEpoch != currentValidatorTask.resultEpoch || res.resultEpoch != currentResultEpoch || res.resultEpoch != sealedResult.resultEpoch)
                {
                    RevokeReadiness("ResultEpoch mismatch.");
                    return "STAGE_VALIDATION_REJECTED: ResultEpoch mismatch.";
                }
                if (res.sourceArtifactHash != currentValidatorTask.sourceArtifactHash || res.sourceArtifactHash != sealedResult.sourceArtifactHash)
                {
                    RevokeReadiness("SourceArtifactHash mismatch.");
                    return "STAGE_VALIDATION_REJECTED: SourceArtifactHash mismatch.";
                }
                if (res.actualContentProfileFingerprint != currentValidatorTask.contentProfileFingerprint ||
                    res.actualContentProfileFingerprint != GetActualContentProfileFingerprint())
                {
                    RevokeReadiness("ContentProfileFingerprint mismatch in validator result.");
                    return "STAGE_VALIDATION_REJECTED: ContentProfileFingerprint mismatch.";
                }
                if (res.actualManifestHash != currentValidatorTask.sealedManifestHash ||
                    res.actualManifestHash != sealedResult.sealedManifestHash ||
                    res.sealedManifestHash != sealedResult.sealedManifestHash)
                {
                    RevokeReadiness($"Manifest hash mismatch (ValidatorActual={res.actualManifestHash}, SealedExpected={sealedResult.sealedManifestHash}).");
                    return "STAGE_VALIDATION_REJECTED: Manifest hash mismatch.";
                }

                // Mark task consumed
                currentValidatorTask.isConsumed = true;

                // Move result file to .consumed to prevent replay (Atomic Consumption, Fail-Closed)
                try
                {
                    if (File.Exists(resultFile))
                    {
                        string consumedPath = resultFile + ".consumed";
                        if (File.Exists(consumedPath)) File.Delete(consumedPath);
                        File.Move(resultFile, consumedPath);
                    }
                    else
                    {
                        RevokeReadiness("Result channel file vanished during consumption.");
                        return "STAGE_VALIDATION_REJECTED: Result channel file vanished during consumption.";
                    }
                }
                catch (Exception ex)
                {
                    RevokeReadiness($"Failed to atomically consume validator result channel: {ex.Message}");
                    return $"STAGE_VALIDATION_REJECTED: Failed to atomically consume validator result channel: {ex.Message}";
                }

                // Simulator internally materializes StageValidationReceipt bound directly to verified ValidatorResult
                var receipt = new StageValidationReceipt
                {
                    receiptId = $"VR_{DateTime.UtcNow:yyyyMMdd_HHmmss}_{Guid.NewGuid():N}",
                    validatorTaskId = res.validatorTaskId,
                    stagedFilePath = res.stagedFilePath,
                    stagedSha = res.stagedSha,
                    sealedResultId = res.sealedResultId,
                    resultEpoch = res.resultEpoch,
                    manifestVersion = res.manifestVersion,
                    sealedManifestHash = res.sealedManifestHash,
                    authorityId = res.authorityId,
                    storeIncarnation = res.storeIncarnation,
                    baseLineage = res.baseLineage,
                    grantId = res.grantId,
                    workerGeneration = res.workerGeneration,
                    scopeId = res.scopeId,
                    targetMapIndex = res.targetMapIndex,
                    allowedMode = res.allowedMode,
                    contentProfileFingerprint = res.actualContentProfileFingerprint,
                    sourceArtifactHash = res.sourceArtifactHash,
                    validatorProcessId = res.validatorProcessId,
                    validatorProcessStartTimeUtc = res.validatorProcessStartTimeUtc,
                    validatorExecutable = res.validatorExecutable,
                    validatorResult = res.validatorResult,
                    validatedAt = res.validatedAtUtc
                };

                // Clear operator-launched validator state for next cycle
                if (operatorLaunchedValidatorProcess != null)
                {
                    try { if (!operatorLaunchedValidatorProcess.HasExited) operatorLaunchedValidatorProcess.Dispose(); } catch { }
                    operatorLaunchedValidatorProcess = null;
                }
                operatorLaunchedValidatorPid = 0;
                operatorLaunchedValidatorStartTimeUtc = "";
                operatorLaunchedValidatorExecutable = "";
                operatorChannelSecretToken = "";
                registeredValidatorProcessId = 0;
                registeredValidatorStartTime = "";
                registeredValidatorExecutable = "";

                currentStageValidationReceipt = receipt;
                semanticState = SemanticApprovalState.STAGED_VALIDATED;
                Log.Message($"[WorkerBridge] STAGE_VALIDATION_ACCEPTED: ReceiptId={receipt.receiptId}, ValidatorPid={res.validatorProcessId}, TaskId={currentValidatorTask.validatorTaskId}");

                return $"STAGE_VALIDATION_ACCEPTED: ReceiptId={receipt.receiptId}, ValidatorPid={res.validatorProcessId}, TaskId={currentValidatorTask.validatorTaskId}";
            }
            catch (Exception ex)
            {
                RevokeReadiness($"CompleteStageValidation exception: {ex}");
                return $"ERROR: CompleteStageValidation exception: {ex}";
            }
        }

        private string HandleValidateAsPrePromotionValidator(string arg)
        {
            return "ERROR: VALIDATE_AS_PRE_PROMOTION_VALIDATOR is deprecated and rejected under Gate 05. Caller cannot nominate expected manifest/result. Use EXECUTE_VALIDATOR_TASK <taskFilePath> <capabilityNonce>.";
        }

        private string HandleSubmitStageValidationReceipt(string arg)
        {
            RevokeReadiness("Attempted unauthorized caller submission of stage validation receipt (MD-127).");
            return "STAGE_VALIDATION_REJECTED: Public/caller receipt submission is deprecated and prohibited under Gate05-R1 / MD-127. Authority must originate from registered operator-owned validator task and protected channel.";
        }

        private string HandleGetStageValidationReceipt()
        {
            if (currentStageValidationReceipt == null)
            {
                return "ERROR: No active StageValidationReceipt stored.";
            }
            return JsonConvert.SerializeObject(currentStageValidationReceipt, Newtonsoft.Json.Formatting.Indented);
        }

        private string HandlePromoteStaged(string arg)
        {
            if (lifecycleState != WorkerLifecycleState.READY)
            {
                return $"PROMOTION_BLOCKED: Worker state is {lifecycleState}.";
            }

            if (currentStageValidationReceipt == null || semanticState != SemanticApprovalState.STAGED_VALIDATED || sealedResult == null)
            {
                return $"PROMOTION_BLOCKED: No valid StageValidationReceipt found. State is '{semanticState}'. Must pass STAGE_SAVE and fresh pre-promotion validation first.";
            }

            if (currentValidatorTask == null)
            {
                RevokeReadiness("No ValidatorTask associated with current stage.");
                return "PROMOTION_BLOCKED: No ValidatorTask associated with current stage.";
            }

            var receipt = currentStageValidationReceipt;
            var sealedRes = sealedResult;
            var task = currentValidatorTask;

            string[] parts = arg.Split(' ');
            string stagingSaveName = parts[0];
            string finalSaveName = parts.Length > 1 ? parts[1] : stagingSaveName.Replace("Staging_", "");

            string callerStagingPath = GenFilePaths.FilePathForSavedGame(stagingSaveName);

            // Caller path substitution check
            if (!string.Equals(callerStagingPath, receipt.stagedFilePath, StringComparison.OrdinalIgnoreCase))
            {
                RevokeReadiness($"Caller path substitution detected. Expected '{receipt.stagedFilePath}', got '{callerStagingPath}'");
                return $"PROMOTION_BLOCKED: Caller path substitution detected. Expected exact staged path '{receipt.stagedFilePath}', got '{callerStagingPath}'";
            }

            if (!File.Exists(receipt.stagedFilePath))
            {
                return $"PROMOTION_BLOCKED: Staged file not found at '{receipt.stagedFilePath}'.";
            }

            // Verify ALL fields across receipt, task, sealedRes, authority, grant, and current engine state:
            // 1. validatorTaskId
            if (receipt.validatorTaskId != task.validatorTaskId)
            {
                RevokeReadiness("ValidatorTaskId mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: ValidatorTaskId mismatch.";
            }

            // 2. Generation
            if (currentGeneration != sealedRes.workerGeneration || currentGeneration != receipt.workerGeneration || currentGeneration != task.workerGeneration)
            {
                RevokeReadiness("Generation mismatch at promotion boundary.");
                return $"PROMOTION_BLOCKED: Generation mismatch (ReceiptGen={receipt.workerGeneration}, CurrentGen={currentGeneration}).";
            }

            // 3. Epoch invariant (Requirement 12)
            if (receipt.resultEpoch != task.resultEpoch ||
                receipt.resultEpoch != sealedRes.resultEpoch ||
                receipt.resultEpoch != currentResultEpoch)
            {
                RevokeReadiness($"ResultEpoch invariant violated: ReceiptEpoch={receipt.resultEpoch}, TaskEpoch={task.resultEpoch}, SealedEpoch={sealedRes.resultEpoch}, CurrentEpoch={currentResultEpoch}");
                return "PROMOTION_BLOCKED: ResultEpoch invariant violated.";
            }

            // 4. SealedResultId
            if (sealedRes.sealedResultId != receipt.sealedResultId || sealedRes.sealedResultId != task.sealedResultId)
            {
                RevokeReadiness("SealedResultId mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: SealedResultId mismatch.";
            }

            // 5. AuthorityId
            if (registeredAuthority == null || registeredAuthority.authorityId != receipt.authorityId || registeredAuthority.authorityId != task.authorityId)
            {
                RevokeReadiness("Authority mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: AuthorityId mismatch.";
            }

            // 6. StoreIncarnation & BaseLineage
            if (receipt.storeIncarnation != registeredAuthority.storeIncarnation || receipt.storeIncarnation != task.storeIncarnation)
            {
                RevokeReadiness("StoreIncarnation mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: StoreIncarnation mismatch.";
            }
            if (receipt.baseLineage != registeredAuthority.baseLineage || receipt.baseLineage != task.baseLineage)
            {
                RevokeReadiness("BaseLineage mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: BaseLineage mismatch.";
            }

            // 7. GrantId & Grant Scope
            if (activeGrant == null || activeGrant.grantId != receipt.grantId || activeGrant.grantId != task.grantId)
            {
                RevokeReadiness("Grant mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: GrantId mismatch.";
            }
            if (activeGrant.scopeId != registeredAuthority.targetScopeId || receipt.scopeId != registeredAuthority.targetScopeId || task.scopeId != registeredAuthority.targetScopeId)
            {
                RevokeReadiness("ScopeId mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: ScopeId mismatch.";
            }

            // 8. ManifestVersion
            if (receipt.manifestVersion != registeredAuthority.manifestVersion || receipt.manifestVersion != task.manifestVersion)
            {
                RevokeReadiness("ManifestVersion mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: ManifestVersion mismatch.";
            }

            // 9. SourceArtifactHash
            if (receipt.sourceArtifactHash != registeredAuthority.expectedSourceArtifactHash || receipt.sourceArtifactHash != task.sourceArtifactHash)
            {
                RevokeReadiness("SourceArtifactHash mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: SourceArtifactHash mismatch.";
            }

            // 10. ContentProfile
            string currentProfile = GetActualContentProfileFingerprint();
            if (currentProfile != receipt.contentProfileFingerprint || currentProfile != task.contentProfileFingerprint || currentProfile != registeredAuthority.contentProfileFingerprint)
            {
                RevokeReadiness("ContentProfile mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: ContentProfileFingerprint mismatch.";
            }

            // 11. TargetMap
            int mapIdx = ScopedTacticalSession.TargetMapIndex >= 0 ? ScopedTacticalSession.TargetMapIndex : 0;
            if (mapIdx != sealedRes.targetMapId || mapIdx != receipt.targetMapIndex || mapIdx != task.targetMapIndex)
            {
                RevokeReadiness("TargetMap mismatch at promotion boundary.");
                return $"PROMOTION_BLOCKED: TargetMap mismatch (ApprovedMap={sealedRes.targetMapId}, CurrentMap={mapIdx}).";
            }

            // 12. SealedManifestHash equality
            if (receipt.sealedManifestHash != sealedRes.sealedManifestHash || receipt.sealedManifestHash != task.sealedManifestHash)
            {
                RevokeReadiness("SealedManifestHash mismatch at promotion boundary.");
                return "PROMOTION_BLOCKED: SealedManifestHash mismatch.";
            }

            // 13. Live Recensus immediately before promotion
            var map = Current.Game.Maps.FirstOrDefault(m => m.Index == mapIdx) ?? Current.Game.Maps[0];
            var liveCensus = EngineHostCensus.GenerateCensus(map);
            string liveHash = liveCensus.ComputeManifestHash();

            if (liveHash != sealedRes.sealedManifestHash)
            {
                string expectedHash = sealedRes.sealedManifestHash;
                RevokeReadiness($"Live state mutated before promotion! SealedHash={expectedHash}, CurrentLiveHash={liveHash}");
                return $"PROMOTION_BLOCKED: Live state mutated before promotion! SealedHash={expectedHash}, CurrentLiveHash={liveHash}";
            }

            // 14. Verify Staged File SHA
            string diskStagedSha;
            using (var sha = SHA256.Create())
            using (var fs = File.OpenRead(receipt.stagedFilePath))
            {
                diskStagedSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
            }

            if (diskStagedSha != receipt.stagedSha || diskStagedSha != task.stagedSha)
            {
                RevokeReadiness($"Staged file SHA altered since validation! Expected {receipt.stagedSha}, got {diskStagedSha}");
                return $"PROMOTION_BLOCKED: Staged file SHA altered since validation! Expected {receipt.stagedSha}, got {diskStagedSha}";
            }

            string finalPath = GenFilePaths.FilePathForSavedGame(finalSaveName);
            string backupPath = GenFilePaths.FilePathForSavedGame(finalSaveName + ".bak");

            // Safe promotion with backup preservation (Requirement 13)
            // NO UNSAFE COPY-OVERWRITE FALLBACK!
            try
            {
                if (File.Exists(finalPath))
                {
                    // 1. Create/update backup copy of current final
                    File.Copy(finalPath, backupPath, overwrite: true);

                    // 2. Safe same-volume atomic replace
                    try
                    {
                        File.Replace(receipt.stagedFilePath, finalPath, backupPath);
                    }
                    catch (Exception ex)
                    {
                        RevokeReadiness($"Atomic promotion replace failed: {ex.Message}. Existing final preserved.");
                        return $"PROMOTION_FAILED: Atomic File.Replace failed: {ex.Message}. Existing final preserved.";
                    }
                }
                else
                {
                    // First-time final path uses atomic File.Move
                    File.Move(receipt.stagedFilePath, finalPath);
                }
            }
            catch (Exception ex)
            {
                RevokeReadiness($"Promotion failed: {ex.Message}");
                return $"PROMOTION_FAILED: Promotion exception: {ex.Message}";
            }

            var fi = new FileInfo(finalPath);
            string finalSha;
            using (var sha = SHA256.Create())
            using (var fs = File.OpenRead(finalPath))
            {
                finalSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
            }

            semanticState = SemanticApprovalState.ARTIFACT_APPROVED;
            Log.Message($"[WorkerBridge] ARTIFACT_APPROVED: '{finalPath}', SHA={finalSha}, ManifestHash={sealedResult.sealedManifestHash}, Epoch={sealedResult.resultEpoch}, ReceiptId={currentStageValidationReceipt.receiptId}");

            return $"ARTIFACT_APPROVED: File='{finalPath}', Name='{finalSaveName}', Size={fi.Length} bytes, SHA256={finalSha}, SealedManifestHash={sealedResult.sealedManifestHash}, Epoch={sealedResult.resultEpoch}, ReceiptId={currentStageValidationReceipt.receiptId}";
        }

        private string HandleQaMutateEpoch(string arg)
        {
            if (long.TryParse(arg.Trim(), out long ep))
            {
                currentResultEpoch = ep;
                return $"OK: currentResultEpoch mutated to {currentResultEpoch}.";
            }
            return "ERROR: Usage: QA_MUTATE_EPOCH <int64>";
        }

        private string HandleExportApprovedSave(string saveName)
        {
            return "ERROR: Direct EXPORT_APPROVED_SAVE bypass is deprecated and prohibited under Gate 04. Mandatory workflow: STAGE_SAVE -> fresh pre-promotion validation -> SUBMIT_STAGE_VALIDATION_RECEIPT -> PROMOTE_STAGED.";
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
                manifestPath = Path.Combine(SafeSaveDataFolderPath, "Saves", (activeSaveName ?? "TargetSettlement") + ".census.json");
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

            string path = Path.Combine(SafeSaveDataFolderPath, "Saves", saveName + ".census.json");
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

                case "activejob":
                case "job":
                case "strange":
                    var jp = map.mapPawns.FreeColonists.FirstOrDefault(p => p.CurJob != null) ?? map.mapPawns.FreeColonists.FirstOrDefault();
                    if (jp != null)
                    {
                        int jx = 139, jy = 0, jz = 143;
                        for (int i = 1; i < parts.Length; i++)
                        {
                            if (parts[i].Contains(","))
                            {
                                var coords = parts[i].Split(',');
                                if (coords.Length == 3 && int.TryParse(coords[0], out int cx) && int.TryParse(coords[1], out int cy) && int.TryParse(coords[2], out int cz))
                                {
                                    jx = cx; jy = cy; jz = cz;
                                    break;
                                }
                            }
                        }
                        if (jp.CurJob == null)
                        {
                            jp.jobs.StartJob(new Verse.AI.Job(JobDefOf.Goto, new IntVec3(jx, jy, jz)));
                        }
                        else
                        {
                            jp.CurJob.targetA = new LocalTargetInfo(new IntVec3(jx, jy, jz));
                        }
                        return $"OK: Mutated live ActiveJobTarget of {jp.ThingID} to ({jx}, {jy}, {jz}). TicksGame={Find.TickManager.TicksGame}";
                    }
                    return "ERROR: Could not find colonist for job mutation.";

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
