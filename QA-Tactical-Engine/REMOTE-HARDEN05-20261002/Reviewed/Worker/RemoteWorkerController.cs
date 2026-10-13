using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using UnityEngine;
using Verse;
using Verse.AI;
using RimWorld;
using WarEconomy.RemotePresentation.Common;

namespace WarEconomy.RemotePresentation.Worker
{
    public class PendingWorkerCommand
    {
        public RemoteTacticalCommand Command = new RemoteTacticalCommand();
        public CommandResponse Response = new CommandResponse();
        public ManualResetEvent CompletionEvent = new ManualResetEvent(false);
        public bool IsControlSurface = false;
    }

    public class RemoteWorkerController : MonoBehaviour
    {
        public static RemoteWorkerController? Instance { get; private set; }

        public int ListenPort = 7792;
        public int ControlPort = 7794;
        public int CurrentGeneration = 1;
        public string ActiveSessionId = "TAC_SESSION_01";
        public bool OperationalProgressionEnabled = false;
        public bool IsRunning = false;
        public static volatile int SimulatedDelayMs = 0;
        public static volatile string DelayTargetCommandType = "";

        private long _snapshotSequence = 0;
        private float _progressionAccumulator = 0f;
        private TcpListener? _gameplayListener;
        private Thread? _gameplayThread;
        private TcpListener? _controlListener;
        private Thread? _controlThread;
        private readonly ConcurrentQueue<PendingWorkerCommand> _commandQueue = new ConcurrentQueue<PendingWorkerCommand>();
        private readonly Dictionary<string, CommandResponse> _commandHistory = new Dictionary<string, CommandResponse>();
        private readonly Queue<string> _commandHistoryOrder = new Queue<string>();

        private void Awake()
        {
            Instance = this;
            Log.Message("[RemoteWorkerController] Worker component created.");
        }

        public void StartServers(int gameplayPort, int controlPort)
        {
            ListenPort = gameplayPort;
            ControlPort = controlPort;
            IsRunning = true;

            _gameplayThread = new Thread(ListenGameplayLoop)
            {
                IsBackground = true,
                Name = "RemoteWorker_GameplayListener"
            };
            _gameplayThread.Start();

            _controlThread = new Thread(ListenControlLoop)
            {
                IsBackground = true,
                Name = "RemoteWorker_ControlListener"
            };
            _controlThread.Start();

            Log.Message($"[RemoteWorkerController] Worker Gameplay TCP listening on port {ListenPort}. Control TCP listening on port {ControlPort}. Generation={CurrentGeneration}.");
        }

        public void StartServer(int port)
        {
            StartServers(port, port + 2);
        }

        private void ListenGameplayLoop()
        {
            try
            {
                _gameplayListener = new TcpListener(IPAddress.Loopback, ListenPort);
                _gameplayListener.Start();

                while (IsRunning)
                {
                    TcpClient client = _gameplayListener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleGameplayClientConnection, client);
                }
            }
            catch (SocketException ex)
            {
                if (IsRunning)
                {
                    Log.Error($"[RemoteWorkerController] Gameplay socket error: {ex}");
                }
            }
            catch (Exception ex)
            {
                Log.Error($"[RemoteWorkerController] Gameplay listener exception: {ex}");
            }
        }

        private void HandleGameplayClientConnection(object? state)
        {
            if (state is not TcpClient client) return;

            using (client)
            using (var stream = client.GetStream())
            using (var reader = new StreamReader(stream, Encoding.UTF8))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true })
            {
                while (IsRunning && client.Connected)
                {
                    string? line = reader.ReadLine();
                    if (line == null) break;
                    if (string.IsNullOrWhiteSpace(line)) continue;

                    long receivedTime = Stopwatch.GetTimestamp();

                    RemoteTacticalCommand? cmd;
                    try
                    {
                        cmd = Protocols.ParseCommand(line);
                    }
                    catch (Exception ex)
                    {
                        var errResp = new CommandResponse
                        {
                            Success = false,
                            Status = "JSON_PARSE_ERROR",
                            Message = ex.Message
                        };
                        writer.WriteLine(Protocols.SerializeResponse(errResp));
                        continue;
                    }

                    if (cmd == null) continue;

                    // Security Gate: Gameplay transport unconditionally rejects privileged control commands (QA-PRESENT-006 fix)
                    bool isPrivileged = cmd.CommandType == "LOAD_SAVE" || 
                                        cmd.CommandType == "SET_GENERATION" || 
                                        cmd.CommandType == "SET_PROGRESSION" || 
                                        cmd.CommandType == "SET_ROTATION" ||
                                        cmd.CommandType == "SIMULATE_DELAY";
                    if (isPrivileged)
                    {
                        var rejResp = new CommandResponse
                        {
                            CommandId = cmd.CommandId,
                            Success = false,
                            Status = "PRIVILEGE_REJECTED",
                            Message = $"Privileged control command '{cmd.CommandType}' is rejected on gameplay transport. Physically separate control surface required.",
                            TestSurface = true,
                            WorkerReceivedTicks = receivedTime.ToString(),
                            WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString()
                        };
                        writer.WriteLine(Protocols.SerializeResponse(rejResp));
                        continue;
                    }

                    var pending = new PendingWorkerCommand
                    {
                        Command = cmd,
                        IsControlSurface = false,
                        Response = new CommandResponse
                        {
                            CommandId = cmd.CommandId,
                            TransportEpoch = cmd.TransportEpoch,
                            WorkerReceivedTicks = receivedTime.ToString()
                        }
                    };

                    _commandQueue.Enqueue(pending);

                    // Wait for main thread to process the command
                    bool finished = pending.CompletionEvent.WaitOne(10000);
                    if (!finished)
                    {
                        pending.Response.Success = false;
                        pending.Response.Status = "TIMEOUT";
                        pending.Response.Message = "Timed out waiting for main thread execution.";
                    }

                    // Check for injected delay (supports DRAFT, MOVE, GET_SNAPSHOT, etc.)
                    if (SimulatedDelayMs > 0 && (string.IsNullOrEmpty(DelayTargetCommandType) || DelayTargetCommandType == cmd.CommandType))
                    {
                        int delay = SimulatedDelayMs;
                        SimulatedDelayMs = 0; // One-shot delay
                        DelayTargetCommandType = "";
                        Log.Message($"[RemoteWorkerController] Injecting {delay}ms delay into {cmd.CommandType} response...");
                        Thread.Sleep(delay);
                    }

                    string responseJson = Protocols.SerializeResponse(pending.Response);
                    writer.WriteLine(responseJson);
                }
            }
        }

        private void ListenControlLoop()
        {
            try
            {
                _controlListener = new TcpListener(IPAddress.Loopback, ControlPort);
                _controlListener.Start();

                while (IsRunning)
                {
                    TcpClient client = _controlListener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleControlClientConnection, client);
                }
            }
            catch (SocketException ex)
            {
                if (IsRunning)
                {
                    Log.Error($"[RemoteWorkerController] Control socket error: {ex}");
                }
            }
            catch (Exception ex)
            {
                Log.Error($"[RemoteWorkerController] Control listener exception: {ex}");
            }
        }

        private void HandleControlClientConnection(object? state)
        {
            if (state is not TcpClient client) return;

            using (client)
            using (var stream = client.GetStream())
            using (var reader = new StreamReader(stream, Encoding.UTF8))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true })
            {
                while (IsRunning && client.Connected)
                {
                    string? line = reader.ReadLine();
                    if (line == null) break;
                    if (string.IsNullOrWhiteSpace(line)) continue;

                    long receivedTime = Stopwatch.GetTimestamp();

                    RemoteTacticalCommand? cmd;
                    try
                    {
                        cmd = Protocols.ParseCommand(line);
                    }
                    catch (Exception ex)
                    {
                        var errResp = new CommandResponse
                        {
                            Success = false,
                            Status = "JSON_PARSE_ERROR",
                            Message = ex.Message
                        };
                        writer.WriteLine(Protocols.SerializeResponse(errResp));
                        continue;
                    }

                    if (cmd == null) continue;

                    var pending = new PendingWorkerCommand
                    {
                        Command = cmd,
                        IsControlSurface = true,
                        Response = new CommandResponse
                        {
                            CommandId = cmd.CommandId,
                            WorkerReceivedTicks = receivedTime.ToString()
                        }
                    };

                    _commandQueue.Enqueue(pending);

                    // Wait for main thread to process the command
                    bool finished = pending.CompletionEvent.WaitOne(10000);
                    if (!finished)
                    {
                        pending.Response.Success = false;
                        pending.Response.Status = "TIMEOUT";
                        pending.Response.Message = "Timed out waiting for main thread execution.";
                    }

                    string responseJson = Protocols.SerializeResponse(pending.Response);
                    writer.WriteLine(responseJson);
                }
            }
        }

        private void Update()
        {
            // 1. Process queued commands on the main Unity thread
            while (_commandQueue.TryDequeue(out var pending))
            {
                ProcessCommandOnMainThread(pending);
                pending.CompletionEvent.Set();
            }

            // 2. Operational Worker Progression (ADR-006A compliant bounded execution)
            // Autonomous cadence sufficient for an accepted remote Move to progress
            // without requiring an external test harness to manually step every single tick.
            if (OperationalProgressionEnabled && Find.TickManager != null)
            {
                Map? map = ResolveTargetMap(TargetMapId);
                if (map != null)
                {
                    _progressionAccumulator += Time.deltaTime;
                    int desiredTicks = (int)(_progressionAccumulator * 60f); // 60 TPS standard rate
                    if (desiredTicks > 0)
                    {
                        // Bounded slice size: max 5 ticks per frame, hard wall-clock budget 8.0ms
                        int ticksToRun = Math.Min(desiredTicks, 5);
                        int executedTicks = 0;
                        long startTicks = Stopwatch.GetTimestamp();
                        double ticksToMs = 1000.0 / Stopwatch.Frequency;
                        for (int i = 0; i < ticksToRun; i++)
                        {
                            Find.TickManager.DoSingleTick();
                            executedTicks++;
                            if ((Stopwatch.GetTimestamp() - startTicks) * ticksToMs >= 8.0)
                            {
                                break;
                            }
                        }
                        // Requirement 8: Subtract actual executed ticks, preserving remaining cadence debt!
                        _progressionAccumulator -= executedTicks / 60f;
                    }
                }
            }
        }

        public const string PrivilegedQaToken = "QA_CONTROL_SURFACE_KEY_PRIVILEGED";
        public string TargetMapId = "Map_0";

        public Map? ResolveTargetMap(string mapId)
        {
            if (Find.Maps == null || Find.Maps.Count == 0) return null;
            if (string.IsNullOrEmpty(mapId)) return null;

            foreach (var m in Find.Maps)
            {
                if (m != null && ("Map_" + m.uniqueID == mapId || m.uniqueID.ToString() == mapId))
                {
                    return m;
                }
            }
            return null;
        }

        private void ProcessCommandOnMainThread(PendingWorkerCommand pending)
        {
            var cmd = pending.Command;
            var resp = pending.Response;
            resp.TransportEpoch = cmd.TransportEpoch;

            long startExecTicks = Stopwatch.GetTimestamp();

            // Check duplicate command idempotency for interactive commands (DRAFT, MOVE, ATTACK)
            if (!string.IsNullOrEmpty(cmd.CommandId) && _commandHistory.TryGetValue(cmd.CommandId, out var cachedResp))
            {
                resp.Success = cachedResp.Success;
                resp.Status = cachedResp.Status;
                resp.Message = cachedResp.Message + " (IDEMPOTENT_RETRY)";
                resp.Snapshot = BuildReplicationSnapshot();
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                return;
            }

            // Security Gate: Test-control isolation. Privileged endpoints only (QA-PRESENT-006 fix).
            bool isPrivilegedCommand = cmd.CommandType == "LOAD_SAVE" || 
                                       cmd.CommandType == "SET_GENERATION" || 
                                       cmd.CommandType == "SET_PROGRESSION" || 
                                       cmd.CommandType == "SET_ROTATION" ||
                                       cmd.CommandType == "SIMULATE_DELAY";
            if (isPrivilegedCommand)
            {
                if (!pending.IsControlSurface)
                {
                    resp.Success = false;
                    resp.Status = "PRIVILEGE_REJECTED";
                    resp.Message = $"Test/control command '{cmd.CommandType}' is rejected on gameplay transport. Dedicated control surface required.";
                    resp.TestSurface = true;
                    resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                    return;
                }

                if (cmd.Token != PrivilegedQaToken)
                {
                    resp.Success = false;
                    resp.Status = "PRIVILEGE_REJECTED";
                    resp.Message = $"Test/control command '{cmd.CommandType}' requires valid privileged token. Provided token rejected.";
                    resp.TestSurface = true;
                    resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                    return;
                }
            }

            if (cmd.CommandType == "SIMULATE_DELAY")
            {
                int delay = 2000;
                if (!string.IsNullOrEmpty(cmd.CustomData) && int.TryParse(cmd.CustomData, out var d))
                {
                    delay = d;
                }
                SimulatedDelayMs = delay;
                DelayTargetCommandType = cmd.TargetPawnId ?? "";
                resp.Success = true;
                resp.Status = "ACCEPTED";
                resp.Message = $"Configured simulated periodic response delay of {delay}ms for '{DelayTargetCommandType}'.";
                resp.TestSurface = true;
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                return;
            }

            // 1. System & Test Commands (no active map or pawn ownership required)
            if (cmd.CommandType == "PING")
            {
                resp.Success = true;
                resp.Status = "PONG";
                resp.Message = "Worker alive and ready.";
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                return;
            }

            if (cmd.CommandType == "STATUS")
            {
                int mapCount = Find.Maps?.Count ?? 0;
                int pawnCount = ResolveTargetMap(TargetMapId)?.mapPawns?.AllPawns?.Count ?? 0;
                int ticks = Find.TickManager?.TicksGame ?? 0;
                resp.Success = true;
                resp.Status = "ACCEPTED";
                resp.Message = $"MAPS={mapCount}, PAWNS={pawnCount}, TICKS={ticks}, GEN={CurrentGeneration}, PROGRESSION={OperationalProgressionEnabled}";
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                return;
            }

            if (cmd.CommandType == "LOAD_SAVE")
            {
                string saveName = string.IsNullOrEmpty(cmd.CustomData) ? "EngineComplexFixture" : cmd.CustomData;
                Log.Message($"[RemoteWorkerController] Executing LoadGame for '{saveName}' (Privileged TestSurface)...");
                GameDataSaveLoader.LoadGame(saveName);
                resp.Success = true;
                resp.Status = "ACCEPTED";
                resp.Message = $"Queued LoadGame for '{saveName}'.";
                resp.TestSurface = true;
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                return;
            }

            if (cmd.CommandType == "SET_GENERATION")
            {
                CurrentGeneration = cmd.Generation;
                resp.Success = true;
                resp.Status = "ACCEPTED";
                resp.Message = $"Generation updated to {CurrentGeneration}.";
                resp.TestSurface = true;
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                resp.Snapshot = BuildReplicationSnapshot();
                return;
            }

            if (cmd.CommandType == "SET_PROGRESSION")
            {
                OperationalProgressionEnabled = cmd.CustomData == "1" || cmd.CustomData.Equals("true", StringComparison.OrdinalIgnoreCase);
                if (Find.TickManager != null)
                {
                    Find.TickManager.CurTimeSpeed = OperationalProgressionEnabled ? TimeSpeed.Normal : TimeSpeed.Paused;
                }
                resp.Success = true;
                resp.Status = "ACCEPTED";
                resp.Message = $"Operational progression set to {OperationalProgressionEnabled}.";
                resp.TestSurface = true;
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                resp.Snapshot = BuildReplicationSnapshot();
                return;
            }

            if (cmd.CommandType == "SET_ROTATION")
            {
                Map? mapTarget = ResolveTargetMap(TargetMapId);
                Pawn? p = mapTarget != null ? FindPawn(mapTarget, cmd.TargetPawnId) : null;
                if (p != null)
                {
                    int rotVal = RotationWireContract.FromWire(cmd.CustomData);
                    p.Rotation = new Rot4(rotVal);
                    resp.Success = true;
                    resp.Status = "ACCEPTED";
                    resp.Message = $"Pawn '{p.LabelShort}' rotation set to {p.Rotation} (wire='{cmd.CustomData}').";
                }
                else
                {
                    resp.Success = false;
                    resp.Status = "PAWN_NOT_FOUND";
                    resp.Message = $"Pawn '{cmd.TargetPawnId}' not found on target map.";
                }
                resp.TestSurface = true;
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                resp.Snapshot = BuildReplicationSnapshot();
                return;
            }

            // 2. Tactical Generation Check (for tactical commands)
            if (cmd.Generation != CurrentGeneration)
            {
                resp.Success = false;
                resp.Status = "STALE_GENERATION_REJECTED";
                resp.Message = $"Command generation {cmd.Generation} is stale. Active generation is {CurrentGeneration}.";
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                resp.Snapshot = BuildReplicationSnapshot();
                return;
            }

            // 3. Ownership / Authorization Boundary Check
            if (!OwnershipRegistry.AuthorizeCommand(cmd.Token, cmd.TargetPawnId, out string playerId, out string authFailure))
            {
                resp.Success = false;
                resp.Status = "AUTH_REJECTED";
                resp.Message = authFailure;
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                resp.Snapshot = BuildReplicationSnapshot();
                return;
            }


            // 4. Engine Readiness Check for Map-Specific Operations
            Map? map = ResolveTargetMap(TargetMapId);
            if (map == null)
            {
                resp.Success = false;
                resp.Status = "NO_ACTIVE_MAP";
                resp.Message = $"Authority target map '{TargetMapId}' not found on Worker.";
                resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
                return;
            }

            // 5. Command Execution
            try
            {
                switch (cmd.CommandType)
                {
                    case "GET_SNAPSHOT":
                        resp.Success = true;
                        resp.Status = "ACCEPTED";
                        resp.Message = "Snapshot retrieved.";
                        break;

                    case "DRAFT":
                        {
                            Pawn? pawn = FindPawn(map, cmd.TargetPawnId);
                            if (pawn == null)
                            {
                                resp.Success = false;
                                resp.Status = "PAWN_NOT_FOUND";
                                resp.Message = $"Pawn '{cmd.TargetPawnId}' not found on target map.";
                            }
                            else
                            {
                                if (pawn.drafter == null)
                                {
                                    resp.Success = false;
                                    resp.Status = "NOT_DRAFTABLE";
                                    resp.Message = $"Pawn '{cmd.TargetPawnId}' has no draft controller.";
                                }
                                else
                                {
                                    pawn.drafter.Drafted = !pawn.drafter.Drafted;
                                    resp.Success = true;
                                    resp.Status = "ACCEPTED";
                                    resp.Message = $"Pawn '{pawn.LabelShort}' Drafted toggled to {pawn.drafter.Drafted}.";
                                }
                            }
                        }
                        break;

                    case "MOVE":
                        {
                            Pawn? pawn = FindPawn(map, cmd.TargetPawnId);
                            if (pawn == null)
                            {
                                resp.Success = false;
                                resp.Status = "PAWN_NOT_FOUND";
                                resp.Message = $"Pawn '{cmd.TargetPawnId}' not found.";
                            }
                            else
                            {
                                var dest = new IntVec3(cmd.TargetCellX, 0, cmd.TargetCellZ);
                                Job gotoJob = JobMaker.MakeJob(JobDefOf.Goto, dest);
                                bool taken = pawn.jobs.TryTakeOrderedJob(gotoJob, JobTag.Misc);
                                resp.Success = taken;
                                resp.Status = taken ? "ACCEPTED" : "JOB_REJECTED";
                                resp.Message = $"Ordered Pawn '{pawn.LabelShort}' to move to {dest}. Taken={taken}.";
                            }
                        }
                        break;

                    case "ATTACK":
                        {
                            Pawn? pawn = FindPawn(map, cmd.TargetPawnId);
                            Thing? targetThing = FindThing(map, cmd.TargetThingId);

                            if (pawn == null || targetThing == null)
                            {
                                resp.Success = false;
                                resp.Status = "TARGET_NOT_FOUND";
                                resp.Message = $"Attacker '{cmd.TargetPawnId}' or Target '{cmd.TargetThingId}' not found.";
                            }
                            else
                            {
                                Job attackJob = JobMaker.MakeJob(JobDefOf.AttackMelee, targetThing);
                                attackJob.maxNumMeleeAttacks = 5;
                                attackJob.expiryInterval = 2000;
                                bool taken = pawn.jobs.TryTakeOrderedJob(attackJob, JobTag.Misc);
                                resp.Success = taken;
                                resp.Status = taken ? "ACCEPTED" : "JOB_REJECTED";
                                resp.Message = $"Ordered Pawn '{pawn.LabelShort}' to attack '{targetThing.Label}'. Taken={taken}.";
                            }
                        }
                        break;

                    case "JOB":
                        {
                            Pawn? pawn = FindPawn(map, cmd.TargetPawnId);
                            if (pawn == null)
                            {
                                resp.Success = false;
                                resp.Status = "PAWN_NOT_FOUND";
                                resp.Message = $"Pawn '{cmd.TargetPawnId}' not found.";
                            }
                            else
                            {
                                pawn.pather?.StopDead();
                                Job waitJob = JobMaker.MakeJob(JobDefOf.Wait_MaintainPosture, 500);
                                bool taken = pawn.jobs.TryTakeOrderedJob(waitJob, JobTag.Misc);
                                resp.Success = taken;
                                resp.Status = taken ? "ACCEPTED" : "JOB_REJECTED";
                                resp.Message = $"Ordered Pawn '{pawn.LabelShort}' Job: Wait_MaintainPosture. Taken={taken}.";
                            }
                        }
                        break;

                    case "APPLY_DAMAGE":
                        {
                            Pawn? pawn = FindPawn(map, cmd.TargetPawnId);
                            if (pawn == null)
                            {
                                resp.Success = false;
                                resp.Status = "PAWN_NOT_FOUND";
                                resp.Message = $"Pawn '{cmd.TargetPawnId}' not found.";
                            }
                            else
                            {
                                var dinfo = new DamageInfo(DamageDefOf.Cut, 12, 0, -1, null, pawn.health.hediffSet.GetNotMissingParts().FirstOrDefault());
                                pawn.TakeDamage(dinfo);
                                resp.Success = true;
                                resp.Status = "ACCEPTED";
                                resp.Message = $"Applied Cut damage to '{pawn.LabelShort}'. Health summary={pawn.health.summaryHealth.SummaryHealthPercent:P0}.";
                            }
                        }
                        break;

                    case "STEP_TICKS":
                        {
                            int count = Math.Max(1, cmd.TicksToSimulate);
                            for (int i = 0; i < count; i++)
                            {
                                Find.TickManager.DoSingleTick();
                            }
                            resp.Success = true;
                            resp.Status = "ACCEPTED";
                            resp.Message = $"Simulated {count} authoritative ticks. Current TicksGame={Find.TickManager.TicksGame}.";
                        }
                        break;

                    default:
                        resp.Success = false;
                        resp.Status = "UNKNOWN_COMMAND";
                        resp.Message = $"Unknown CommandType '{cmd.CommandType}'.";
                        break;
                }

                // If ticks requested to advance simulation after command
                if (cmd.TicksToSimulate > 0 && cmd.CommandType != "STEP_TICKS")
                {
                    for (int i = 0; i < cmd.TicksToSimulate; i++)
                    {
                        Find.TickManager.DoSingleTick();
                    }
                }
            }
            catch (Exception ex)
            {
                resp.Success = false;
                resp.Status = "EXECUTION_EXCEPTION";
                resp.Message = ex.ToString();
            }

            resp.WorkerExecutedTicks = Stopwatch.GetTimestamp().ToString();
            resp.Snapshot = BuildReplicationSnapshot();

            // Cache for idempotency if CommandId is provided
            if (!string.IsNullOrEmpty(cmd.CommandId))
            {
                if (_commandHistory.Count >= 100 && _commandHistoryOrder.Count > 0)
                {
                    string oldest = _commandHistoryOrder.Dequeue();
                    _commandHistory.Remove(oldest);
                }
                _commandHistory[cmd.CommandId] = resp;
                _commandHistoryOrder.Enqueue(cmd.CommandId);
            }
        }

        private Pawn? FindPawn(Map map, string pawnId)
        {
            if (string.IsNullOrEmpty(pawnId)) return null;
            return map.mapPawns.AllPawns.FirstOrDefault(p => p.ThingID == pawnId);
        }

        private Thing? FindThing(Map map, string thingId)
        {
            if (string.IsNullOrEmpty(thingId)) return null;
            return map.spawnedThings.FirstOrDefault(t => t.ThingID == thingId);
        }

        public ReplicationSnapshot BuildReplicationSnapshot()
        {
            Map? map = ResolveTargetMap(TargetMapId);
            if (map == null && Find.Maps != null && Find.Maps.Count > 0)
            {
                map = Find.Maps[0];
            }

            var snap = new ReplicationSnapshot
            {
                TacticalSessionId = ActiveSessionId,
                WorkerGeneration = CurrentGeneration,
                TargetMapId = map != null ? ("Map_" + map.uniqueID) : TargetMapId,
                SnapshotSequence = ++_snapshotSequence,
                AuthoritativeTick = Find.TickManager?.TicksGame ?? 0,
                ServerTicks = Stopwatch.GetTimestamp().ToString()
            };

            if (map != null)
            {
                foreach (var p in map.mapPawns.AllPawns)
                {
                    if (p == null || p.Destroyed) continue;

                    // Authoritative pose classification and facing enforcement (QA-PRESENT-011)
                    string poseSource = "StationaryIdle";
                    int focusTargetX = 0;
                    int focusTargetZ = 0;

                    if (p.stances?.curStance is Stance_Busy busy && busy.focusTarg.IsValid)
                    {
                        poseSource = "Aiming";
                        focusTargetX = busy.focusTarg.Cell.x;
                        focusTargetZ = busy.focusTarg.Cell.z;
                        IntVec3 aimDelta = busy.focusTarg.Cell - p.Position;
                        if (Math.Abs(aimDelta.x) >= Math.Abs(aimDelta.z))
                        {
                            if (aimDelta.x != 0) p.Rotation = aimDelta.x > 0 ? Rot4.East : Rot4.West;
                        }
                        else
                        {
                            if (aimDelta.z != 0) p.Rotation = aimDelta.z > 0 ? Rot4.North : Rot4.South;
                        }
                    }
                    else if (p.pather != null && p.pather.Moving)
                    {
                        poseSource = "Movement";
                        IntVec3 dest = p.pather.nextCell;
                        if (!dest.IsValid || dest == p.Position)
                        {
                            if (p.pather.curPath != null && p.pather.curPath.NodesLeftCount > 0)
                            {
                                dest = p.pather.curPath.Peek(0);
                            }
                        }
                        if (!dest.IsValid || dest == p.Position)
                        {
                            if (p.pather.Destination.IsValid)
                            {
                                dest = p.pather.Destination.Cell;
                            }
                            else if (p.CurJob != null && p.CurJob.targetA.IsValid)
                            {
                                dest = p.CurJob.targetA.Cell;
                            }
                        }

                        if (dest.IsValid && dest != p.Position)
                        {
                            IntVec3 delta = dest - p.Position;
                            if (Math.Abs(delta.x) >= Math.Abs(delta.z))
                            {
                                if (delta.x != 0) p.Rotation = delta.x > 0 ? Rot4.East : Rot4.West;
                            }
                            else
                            {
                                if (delta.z != 0) p.Rotation = delta.z > 0 ? Rot4.North : Rot4.South;
                            }
                        }
                    }
                    else if (p.Drafted)
                    {
                        poseSource = "StationaryDrafted";
                    }

                    int targetX = 0;
                    int targetZ = 0;
                    if (p.CurJob != null && p.CurJob.targetA.IsValid)
                    {
                        targetX = p.CurJob.targetA.Cell.x;
                        targetZ = p.CurJob.targetA.Cell.z;
                    }

                    var pData = new PawnReplicationData
                    {
                        PawnId = p.ThingID,
                        DefName = p.def?.defName ?? "Pawn",
                        Name = p.LabelShort,
                        Faction = p.Faction?.Name ?? "None",
                        PosX = p.Position.x,
                        PosY = p.Position.y,
                        PosZ = p.Position.z,
                        DrawPosX = p.DrawPos.x,
                        DrawPosY = p.DrawPos.y,
                        DrawPosZ = p.DrawPos.z,
                        Rotation = RotationWireContract.ToWire(p.Rotation.AsInt),
                        PoseSource = poseSource,
                        FocusTargetX = focusTargetX,
                        FocusTargetZ = focusTargetZ,
                        Drafted = p.Drafted,
                        CurJobDef = p.CurJob?.def?.defName ?? "None",
                        CurJobReport = p.jobs?.curDriver?.GetReport() ?? "",
                        JobTargetX = targetX,
                        JobTargetZ = targetZ,
                        HealthPercent = p.health?.summaryHealth?.SummaryHealthPercent ?? 1.0f,
                        Downed = p.Downed,
                        Dead = p.Dead
                    };

                    if (p.health?.hediffSet != null)
                    {
                        foreach (var h in p.health.hediffSet.hediffs)
                        {
                            if (h?.def != null)
                            {
                                pData.HediffDefs.Add(h.def.defName);
                            }
                        }
                    }

                    snap.Pawns.Add(pData);
                }
            }

            return snap;
        }

        private void OnDestroy()
        {
            IsRunning = false;
            try
            {
                _gameplayListener?.Stop();
                _gameplayThread?.Abort();
            }
            catch { }
            try
            {
                _controlListener?.Stop();
                _controlThread?.Abort();
            }
            catch { }
            Log.Message("[RemoteWorkerController] Worker component destroyed.");
        }
    }
}
