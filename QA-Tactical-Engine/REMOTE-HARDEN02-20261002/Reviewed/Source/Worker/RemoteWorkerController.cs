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
    }

    public class RemoteWorkerController : MonoBehaviour
    {
        public static RemoteWorkerController? Instance { get; private set; }

        public int ListenPort = 7792;
        public int CurrentGeneration = 1;
        public string ActiveSessionId = "TAC_SESSION_01";
        public bool OperationalProgressionEnabled = false;
        public bool IsRunning = false;

        private long _snapshotSequence = 0;
        private float _progressionAccumulator = 0f;
        private TcpListener? _listener;
        private Thread? _listenerThread;
        private readonly ConcurrentQueue<PendingWorkerCommand> _commandQueue = new ConcurrentQueue<PendingWorkerCommand>();

        private void Awake()
        {
            Instance = this;
            Log.Message("[RemoteWorkerController] Worker component created.");
        }

        public void StartServer(int port)
        {
            ListenPort = port;
            IsRunning = true;
            _listenerThread = new Thread(ListenLoop)
            {
                IsBackground = true,
                Name = "RemoteWorkerListenerThread"
            };
            _listenerThread.Start();
            Log.Message($"[RemoteWorkerController] Worker TCP Server listening on port {ListenPort}. Generation={CurrentGeneration}.");
        }

        private void ListenLoop()
        {
            try
            {
                _listener = new TcpListener(IPAddress.Loopback, ListenPort);
                _listener.Start();

                while (IsRunning)
                {
                    TcpClient client = _listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleClientConnection, client);
                }
            }
            catch (SocketException ex)
            {
                if (IsRunning)
                {
                    Log.Error($"[RemoteWorkerController] Socket error: {ex}");
                }
            }
            catch (Exception ex)
            {
                Log.Error($"[RemoteWorkerController] Listener exception: {ex}");
            }
        }

        private void HandleClientConnection(object? state)
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
            if (OperationalProgressionEnabled && Find.CurrentMap != null && Find.TickManager != null && !Find.TickManager.Paused)
            {
                _progressionAccumulator += Time.deltaTime;
                int desiredTicks = (int)(_progressionAccumulator * 60f); // 60 TPS standard rate
                if (desiredTicks > 0)
                {
                    _progressionAccumulator -= desiredTicks / 60f;
                    // Bounded slice size: max 5 ticks per frame, hard wall-clock budget 8.0ms
                    int ticksToRun = Math.Min(desiredTicks, 5);
                    long startTicks = Stopwatch.GetTimestamp();
                    double ticksToMs = 1000.0 / Stopwatch.Frequency;
                    for (int i = 0; i < ticksToRun; i++)
                    {
                        Find.TickManager.DoSingleTick();
                        if ((Stopwatch.GetTimestamp() - startTicks) * ticksToMs >= 8.0)
                        {
                            break;
                        }
                    }
                }
            }
        }

        private void ProcessCommandOnMainThread(PendingWorkerCommand pending)
        {
            var cmd = pending.Command;
            var resp = pending.Response;

            long startExecTicks = Stopwatch.GetTimestamp();

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
                int pawnCount = Find.CurrentMap?.mapPawns?.AllPawns?.Count ?? 0;
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
                Log.Message($"[RemoteWorkerController] Executing LoadGame for '{saveName}' (TestSurface)...");
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
                resp.Success = true;
                resp.Status = "ACCEPTED";
                resp.Message = $"Operational progression set to {OperationalProgressionEnabled}.";
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
            Map? map = Find.CurrentMap;
            if (map == null && Find.Maps != null && Find.Maps.Count > 0)
            {
                map = Find.Maps[0];
            }

            if (map == null)
            {
                resp.Success = false;
                resp.Status = "NO_ACTIVE_MAP";
                resp.Message = "No active RimWorld map loaded on Worker.";
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
                                // Order wait or clear
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
            Map? map = Find.CurrentMap;
            if (map == null && Find.Maps != null && Find.Maps.Count > 0)
            {
                map = Find.Maps[0];
            }

            var snap = new ReplicationSnapshot
            {
                TacticalSessionId = ActiveSessionId,
                WorkerGeneration = CurrentGeneration,
                TargetMapId = map != null ? ("Map_" + map.uniqueID) : "Map_0",
                SnapshotSequence = ++_snapshotSequence,
                AuthoritativeTick = Find.TickManager?.TicksGame ?? 0,
                ServerTicks = Stopwatch.GetTimestamp().ToString()
            };

            if (map != null)
            {
                foreach (var p in map.mapPawns.AllPawns)
                {
                    if (p == null || p.Destroyed) continue;

                    var pData = new PawnReplicationData
                    {
                        PawnId = p.ThingID,
                        DefName = p.def?.defName ?? "Pawn",
                        Name = p.LabelShort,
                        Faction = p.Faction?.Name ?? "None",
                        PosX = p.Position.x,
                        PosY = p.Position.y,
                        PosZ = p.Position.z,
                        Rotation = p.Rotation.ToString(),
                        Drafted = p.Drafted,
                        CurJobDef = p.CurJob?.def?.defName ?? "None",
                        CurJobReport = p.jobs?.curDriver?.GetReport() ?? "",
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
                _listener?.Stop();
                _listenerThread?.Abort();
            }
            catch { }
            Log.Message("[RemoteWorkerController] Worker component destroyed.");
        }
    }
}
