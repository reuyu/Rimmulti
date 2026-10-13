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

namespace WarEconomy.RemotePresentation.Client
{
    public class PendingClientExternalCommand
    {
        public string Command = "";
        public string Argument = "";
        public string Response = "";
        public ManualResetEvent CompletionEvent = new ManualResetEvent(false);
    }

    public class RemoteClientController : MonoBehaviour
    {
        public static RemoteClientController? Instance { get; private set; }

        public int ListenPort = 7793;
        public string WorkerHost = "127.0.0.1";
        public int WorkerPort = 7792;
        public string ActiveToken = "Player_A_Token";
        public int ClientGeneration = 1;
        public bool IsRunning = false;

        public static bool IsReconciling = false;
        public string ExpectedSessionId = "TAC_SESSION_01";
        public int ExpectedGeneration = 1;
        public string ExpectedMapId = "Map_0";
        public long LastAppliedSnapshotSequence = 0;
        public long TotalSnapshotsApplied = 0;
        public long TotalSnapshotsRejected = 0;

        private TcpListener? _serverListener;
        private Thread? _serverThread;
        private readonly ConcurrentQueue<PendingClientExternalCommand> _extQueue = new ConcurrentQueue<PendingClientExternalCommand>();

        private TcpClient? _tcpClient;
        private NetworkStream? _stream;
        private StreamReader? _reader;
        private StreamWriter? _writer;

        public bool IsConnected => _tcpClient != null && _tcpClient.Connected;

        public ReplicationSnapshot? LatestSnapshot { get; private set; }
        public List<LatencyBenchmarkResult> BenchmarkResults = new List<LatencyBenchmarkResult>();

        private void Awake()
        {
            Instance = this;
            Log.Message("[RemoteClientController] Presentation Client component created.");
        }

        public void StartServer(int port)
        {
            ListenPort = port;
            IsRunning = true;
            _serverThread = new Thread(ListenLoop)
            {
                IsBackground = true,
                Name = "RemoteClientControlListener"
            };
            _serverThread.Start();
            Log.Message($"[RemoteClientController] Control TCP Server listening on port {ListenPort}.");
        }

        private void ListenLoop()
        {
            try
            {
                _serverListener = new TcpListener(IPAddress.Loopback, ListenPort);
                _serverListener.Start();

                while (IsRunning)
                {
                    TcpClient client = _serverListener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleExternalClient, client);
                }
            }
            catch (Exception ex)
            {
                if (IsRunning)
                {
                    Log.Error($"[RemoteClientController] Control listener error: {ex}");
                }
            }
        }

        private void HandleExternalClient(object? state)
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
                    line = line.Trim();
                    if (string.IsNullOrEmpty(line)) continue;

                    string[] parts = line.Split(new[] { ' ' }, 2);
                    string cmd = parts[0].ToUpperInvariant();
                    string arg = parts.Length > 1 ? parts[1] : "";

                    var pending = new PendingClientExternalCommand
                    {
                        Command = cmd,
                        Argument = arg
                    };

                    _extQueue.Enqueue(pending);

                    bool finished = pending.CompletionEvent.WaitOne(60000);
                    if (!finished)
                    {
                        writer.WriteLine("ERROR: Timeout waiting for main thread execution.");
                    }
                    else
                    {
                        writer.WriteLine(pending.Response);
                    }
                }
            }
        }

        public bool ConnectToWorker(string host, int port)
        {
            try
            {
                WorkerHost = host;
                WorkerPort = port;
                _tcpClient = new TcpClient();
                _tcpClient.Connect(WorkerHost, WorkerPort);
                _stream = _tcpClient.GetStream();
                _reader = new StreamReader(_stream, Encoding.UTF8);
                _writer = new StreamWriter(_stream, new UTF8Encoding(false)) { AutoFlush = true };
                Log.Message($"[RemoteClientController] Connected to Tactical Worker at {WorkerHost}:{WorkerPort}.");
                return true;
            }
            catch (Exception ex)
            {
                Log.Error($"[RemoteClientController] Failed to connect to Worker: {ex}");
                return false;
            }
        }

        public CommandResponse SendCommand(RemoteTacticalCommand cmd)
        {
            if (!IsConnected || _writer == null || _reader == null)
            {
                return new CommandResponse
                {
                    CommandId = cmd.CommandId,
                    Success = false,
                    Status = "NOT_CONNECTED",
                    Message = "Client is not connected to Worker."
                };
            }

            cmd.ClientSentTicks = Stopwatch.GetTimestamp().ToString();
            if (string.IsNullOrEmpty(cmd.Token)) cmd.Token = ActiveToken;
            if (cmd.Generation <= 0) cmd.Generation = ClientGeneration;

            string json = Protocols.SerializeCommand(cmd);
            _writer.WriteLine(json);

            string? respJson = _reader.ReadLine();
            long clientReceivedTicks = Stopwatch.GetTimestamp();

            if (string.IsNullOrEmpty(respJson))
            {
                return new CommandResponse
                {
                    CommandId = cmd.CommandId,
                    Success = false,
                    Status = "EMPTY_RESPONSE",
                    Message = "Worker returned empty response."
                };
            }

            CommandResponse resp = Protocols.ParseResponse(respJson);


            // Record latency metrics
            long clientSent = long.TryParse(cmd.ClientSentTicks, out var cs) ? cs : clientReceivedTicks;
            long workerRecv = long.TryParse(resp.WorkerReceivedTicks, out var wr) ? wr : clientSent;
            long workerExec = long.TryParse(resp.WorkerExecutedTicks, out var we) ? we : workerRecv;

            double ticksToMs = 1000.0 / Stopwatch.Frequency;
            float inputToWorkerMs = (float)Math.Max(0, (workerRecv - clientSent) * ticksToMs);
            float workerExecMs = (float)Math.Max(0, (workerExec - workerRecv) * ticksToMs);
            float execToClientMs = (float)Math.Max(0, (clientReceivedTicks - workerExec) * ticksToMs);
            float totalMs = (float)Math.Max(0, (clientReceivedTicks - clientSent) * ticksToMs);

            var benchmark = new LatencyBenchmarkResult
            {
                TestName = $"{cmd.CommandType}_{cmd.TargetPawnId}",
                InputToWorkerReceiptMs = inputToWorkerMs,
                WorkerReceiptToExecutionMs = workerExecMs,
                ExecutionToClientVisibleUpdateMs = execToClientMs,
                TotalEndToEndMs = totalMs,
                SnapshotSizeBytes = respJson.Length
            };
            BenchmarkResults.Add(benchmark);

            // If snapshot is included, validate and reconcile client mirror map
            if (resp.Snapshot != null && resp.Snapshot.Pawns != null && resp.Snapshot.Pawns.Count > 0)
            {
                ValidateAndApplySnapshot(resp.Snapshot, out _);
            }

            return resp;
        }

        public bool ValidateAndApplySnapshot(ReplicationSnapshot snap, out string rejectionReason)
        {
            rejectionReason = "";
            if (snap == null)
            {
                rejectionReason = "NULL_SNAPSHOT";
                TotalSnapshotsRejected++;
                return false;
            }

            // 1. Tactical Session Binding
            if (snap.TacticalSessionId != ExpectedSessionId)
            {
                rejectionReason = $"WRONG_SESSION: snapshot session '{snap.TacticalSessionId}' != expected '{ExpectedSessionId}'";
                Log.Warning($"[CLIENT_REPLICATION] Rejected snapshot: {rejectionReason}");
                TotalSnapshotsRejected++;
                return false;
            }

            // 2. Worker Generation Binding
            if (snap.WorkerGeneration != ExpectedGeneration)
            {
                rejectionReason = $"WRONG_GENERATION: snapshot gen {snap.WorkerGeneration} != expected {ExpectedGeneration}";
                Log.Warning($"[CLIENT_REPLICATION] Rejected snapshot: {rejectionReason}");
                TotalSnapshotsRejected++;
                return false;
            }

            // 3. Target Map Identity Binding
            if (snap.TargetMapId != ExpectedMapId)
            {
                rejectionReason = $"WRONG_MAP: snapshot map '{snap.TargetMapId}' != expected '{ExpectedMapId}'";
                Log.Warning($"[CLIENT_REPLICATION] Rejected snapshot: {rejectionReason}");
                TotalSnapshotsRejected++;
                return false;
            }

            // 4. Monotonic Snapshot Sequence Ordering
            if (snap.SnapshotSequence <= LastAppliedSnapshotSequence)
            {
                rejectionReason = $"OUT_OF_ORDER: snapshot seq {snap.SnapshotSequence} <= last applied {LastAppliedSnapshotSequence}";
                Log.Warning($"[CLIENT_REPLICATION] Rejected snapshot: {rejectionReason}");
                TotalSnapshotsRejected++;
                return false;
            }

            // Valid snapshot accepted: advance sequence and reconcile
            LastAppliedSnapshotSequence = snap.SnapshotSequence;
            LatestSnapshot = snap;
            TotalSnapshotsApplied++;
            ReconcileMirrorMap(snap);
            return true;
        }

        public void ReconcileMirrorMap(ReplicationSnapshot snapshot)
        {
            Map? map = Find.CurrentMap;
            if (map == null && Find.Maps != null && Find.Maps.Count > 0)
            {
                map = Find.Maps[0];
            }
            if (map == null) return;

            IsReconciling = true;
            try
            {
                foreach (var pData in snapshot.Pawns)
                {
                    Pawn? pawn = map.mapPawns.AllPawns.FirstOrDefault(p => p.ThingID == pData.PawnId);
                    if (pawn == null) continue;

                    // 1. Reconcile Position
                    var targetPos = new IntVec3(pData.PosX, pData.PosY, pData.PosZ);
                    if (pawn.Position != targetPos && targetPos.InBounds(map))
                    {
                        pawn.Position = targetPos;
                        if (!map.thingGrid.ThingsAt(targetPos).Contains(pawn))
                        {
                            map.thingGrid.Register(pawn);
                        }
                    }

                    // 2. Reconcile Draft State
                    if (pawn.drafter != null && pawn.drafter.Drafted != pData.Drafted)
                    {
                        pawn.drafter.Drafted = pData.Drafted;
                    }

                    // 3. Reconcile Rotation (canonical wire encoding: "North", "East", "South", "West")
                    Rot4 rot = Rot4.South;
                    if (pData.Rotation == "North") rot = Rot4.North;
                    else if (pData.Rotation == "East") rot = Rot4.East;
                    else if (pData.Rotation == "West") rot = Rot4.West;
                    pawn.Rotation = rot;

                    // 4. Reconcile Current Job Identity / Status
                    // Sufficient to avoid displaying a local-only Goto as authoritative
                    if (pawn.jobs != null)
                    {
                        string curLocalJob = pawn.CurJob?.def?.defName ?? "None";
                        if (string.IsNullOrEmpty(pData.CurJobDef) || pData.CurJobDef == "None")
                        {
                            if (curLocalJob != "None" && curLocalJob != "Wait_MaintainPosture")
                            {
                                pawn.jobs.EndCurrentJob(JobCondition.InterruptForced, false);
                            }
                        }
                        else if (pData.CurJobDef == "Goto")
                        {
                            if (curLocalJob != "Goto")
                            {
                                Job mirrorGoto = JobMaker.MakeJob(JobDefOf.Goto, targetPos);
                                pawn.jobs.TryTakeOrderedJob(mirrorGoto, JobTag.Misc);
                            }
                        }
                    }

                    // 5. Reconcile Health / Hediffs
                    if (pawn.health?.hediffSet != null)
                    {
                        foreach (var hDefName in pData.HediffDefs)
                        {
                            if (!pawn.health.hediffSet.hediffs.Any(h => h.def?.defName == hDefName))
                            {
                                var hDef = DefDatabase<HediffDef>.GetNamedSilentFail(hDefName);
                                if (hDef != null)
                                {
                                    var h = HediffMaker.MakeHediff(hDef, pawn);
                                    pawn.health.AddHediff(h);
                                }
                            }
                        }
                    }
                }
            }
            finally
            {
                IsReconciling = false;
            }
        }

        private void Update()
        {
            while (_extQueue.TryDequeue(out var pending))
            {
                try
                {
                    switch (pending.Command)
                    {
                        case "PING":
                            pending.Response = "PONG: Client alive.";
                            break;

                        case "STATUS":
                            {
                                int maps = Find.Maps?.Count ?? 0;
                                int pawns = Find.CurrentMap?.mapPawns?.AllPawns?.Count ?? 0;
                                int ticks = Find.TickManager?.TicksGame ?? 0;
                                pending.Response = $"STATUS: Maps={maps}, Pawns={pawns}, TicksGame={ticks}, ConnectedToWorker={IsConnected}";
                            }
                            break;

                        case "LOAD_SAVE":
                            {
                                string saveName = string.IsNullOrEmpty(pending.Argument) ? "EngineComplexFixture" : pending.Argument;
                                Log.Message($"[RemoteClientController] Executing LoadGame for '{saveName}'...");
                                GameDataSaveLoader.LoadGame(saveName);
                                pending.Response = $"OK: LoadGame initiated for '{saveName}'.";
                            }
                            break;

                        case "CONNECT_WORKER":
                            {
                                string addr = string.IsNullOrEmpty(pending.Argument) ? RemotePresentationMod.ConnectAddress : pending.Argument;
                                string[] parts = addr.Split(':');
                                string host = parts[0];
                                int port = parts.Length > 1 ? int.Parse(parts[1]) : 7792;
                                bool connected = ConnectToWorker(host, port);
                                pending.Response = connected ? $"OK: Connected to {addr}." : $"ERROR: Failed to connect to {addr}.";
                            }
                            break;

                        case "RUN_POC_SUITE":
                            {
                                if (RemoteClientTestHarness.Instance != null)
                                {
                                    RemoteClientTestHarness.Instance.StartTestSuite();
                                    pending.Response = "OK: PoC test suite started.";
                                }
                                else
                                {
                                    pending.Response = "ERROR: RemoteClientTestHarness instance not found.";
                                }
                            }
                            break;

                        default:
                            pending.Response = $"ERROR: Unknown client command '{pending.Command}'.";
                            break;
                    }
                }
                catch (Exception ex)
                {
                    pending.Response = $"EXCEPTION: {ex.Message}";
                }
                finally
                {
                    pending.CompletionEvent.Set();
                }
            }
        }

        public void Disconnect()
        {
            try
            {
                _writer?.Close();
                _reader?.Close();
                _stream?.Close();
                _tcpClient?.Close();
            }
            catch { }
            _tcpClient = null;
            Log.Message("[RemoteClientController] Disconnected from Worker.");
        }

        private void OnDestroy()
        {
            IsRunning = false;
            try
            {
                _serverListener?.Stop();
                _serverThread?.Abort();
            }
            catch { }
            Disconnect();
            Log.Message("[RemoteClientController] Client component destroyed.");
        }
    }
}
