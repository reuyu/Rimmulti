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
using System.Reflection;
using UnityEngine;
using Verse;
using Verse.AI;
using RimWorld;
using WarEconomy.RemotePresentation.Common;
using WarEconomy.RemotePresentation.Worker;

namespace WarEconomy.RemotePresentation.Client
{
    public class PendingClientExternalCommand
    {
        public string Command = "";
        public string Argument = "";
        public string Response = "";
        public ManualResetEvent CompletionEvent = new ManualResetEvent(false);
    }

    [Serializable]
    public class PeriodicReplicationMetric
    {
        public long Sequence = 0;
        public int AuthoritativeTick = 0;
        public int PayloadBytes = 0;
        public float CadenceIntervalMs = 0f;
        public float LoopbackReceiveToApplyMs = 0f;
        public float TotalRoundtripMs = 0f;
        public string ReconcileStatus = "";
        public string PawnPositions = "";
    }

    public class RemoteClientController : MonoBehaviour
    {
        public static RemoteClientController? Instance { get; private set; }

        public int ListenPort = 7793;
        public string WorkerHost = "127.0.0.1";
        public int WorkerPort = 7792;
        public int WorkerControlPort = 7794;
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

        // Presentation-only correction reflection cache
        private static readonly FieldInfo? TweenedPosField = 
            typeof(PawnTweener).GetField("tweenedPos", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);

        // Requirement 1 & 3: Non-blocking periodic replication off Unity main thread
        public bool ReplicationActive = false;
        public float ReplicationInterval = 0.15f; // ~150ms (~6.67 Hz) bounded cadence
        private long _autoRepSequence = 0;
        private double _lastPeriodicReceiveTime = 0;
        public readonly List<PeriodicReplicationMetric> PeriodicMetrics = new List<PeriodicReplicationMetric>();

        // Background replication worker state
        private Thread? _replicationThread;
        private volatile bool _stopReplicationThread = false;
        private TcpClient? _repClient;
        private NetworkStream? _repStream;
        private StreamReader? _repReader;
        private StreamWriter? _repWriter;
        private readonly object _snapshotLock = new object();
        private ReplicationSnapshot? _pendingSnapshotToApply;
        private int _pendingSnapshotBytes = 0;
        private float _pendingSnapshotRoundtripMs = 0f;

        // Liveness & fault detection
        public bool ReplicationDegraded { get; private set; } = false;
        public float MaxMainThreadFrameMs { get; private set; } = 0f;
        private float _lastFrameTimestamp = 0f;

        // Control TCP Server for orchestrator / python commands
        private TcpListener? _serverListener;
        private Thread? _serverThread;
        private readonly ConcurrentQueue<PendingClientExternalCommand> _extQueue = new ConcurrentQueue<PendingClientExternalCommand>();

        // Command RPC socket for interactive gameplay commands (separate from replication)
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

            // Start dedicated non-blocking periodic replication thread
            _stopReplicationThread = false;
            _replicationThread = new Thread(ReplicationThreadLoop)
            {
                IsBackground = true,
                Name = "RemoteClientReplicationLoop"
            };
            _replicationThread.Start();

            Log.Message($"[RemoteClientController] Control TCP Server listening on port {ListenPort}. Replication thread started.");
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

            // Record latency metrics using accurate UTF-8 byte count
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
                SnapshotSizeBytes = Protocols.GetUtf8ByteCount(respJson)
            };
            BenchmarkResults.Add(benchmark);

            // If snapshot is included, validate and reconcile client mirror map
            if (resp.Snapshot != null && resp.Snapshot.Pawns != null && resp.Snapshot.Pawns.Count > 0)
            {
                ValidateAndApplySnapshot(resp.Snapshot, out _);
            }

            return resp;
        }

        /// <summary>
        /// Sends a command to the Worker's privileged QA control port (default 7794).
        /// Used by automated test fixture/harness for out-of-band control operations.
        /// </summary>
        public CommandResponse SendCommandToControlPort(RemoteTacticalCommand cmd)
        {
            try
            {
                using (var client = new TcpClient())
                {
                    client.ReceiveTimeout = 5000;
                    client.SendTimeout = 5000;
                    client.Connect(WorkerHost, WorkerControlPort);
                    using (var stream = client.GetStream())
                    using (var reader = new StreamReader(stream, Encoding.UTF8))
                    using (var writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true })
                    {
                        if (string.IsNullOrEmpty(cmd.Token)) cmd.Token = RemoteWorkerController.PrivilegedQaToken;
                        cmd.ClientSentTicks = Stopwatch.GetTimestamp().ToString();
                        string json = Protocols.SerializeCommand(cmd);
                        writer.WriteLine(json);

                        string? respJson = reader.ReadLine();
                        if (string.IsNullOrEmpty(respJson))
                        {
                            return new CommandResponse
                            {
                                CommandId = cmd.CommandId,
                                Success = false,
                                Status = "EMPTY_RESPONSE",
                                Message = "Worker control port returned empty response."
                            };
                        }
                        return Protocols.ParseResponse(respJson);
                    }
                }
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    CommandId = cmd.CommandId,
                    Success = false,
                    Status = "CONNECTION_ERROR",
                    Message = $"Error connecting to control port {WorkerControlPort}: {ex.Message}"
                };
            }
        }

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

            // 3. Target Map Identity Binding (QA-PRESENT-010 fix)
            if (snap.TargetMapId != ExpectedMapId)
            {
                rejectionReason = $"WRONG_MAP: snapshot map '{snap.TargetMapId}' != expected '{ExpectedMapId}'";
                Log.Warning($"[CLIENT_REPLICATION] Rejected snapshot: {rejectionReason}");
                TotalSnapshotsRejected++;
                return false;
            }

            Map? targetMap = ResolveTargetMap(snap.TargetMapId);
            if (targetMap == null)
            {
                rejectionReason = $"UNRESOLVED_MAP: target map '{snap.TargetMapId}' cannot be resolved locally";
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
            // Bind strictly to snapshot.TargetMapId, never Find.CurrentMap (QA-PRESENT-010)
            Map? map = ResolveTargetMap(snapshot.TargetMapId);
            if (map == null)
            {
                Log.Warning($"[CLIENT_REPLICATION] Cannot reconcile mirror map: target '{snapshot.TargetMapId}' cannot be resolved.");
                return;
            }

            IsReconciling = true;
            try
            {
                foreach (var pData in snapshot.Pawns)
                {
                    Pawn? pawn = map.mapPawns.AllPawns.FirstOrDefault(p => p.ThingID == pData.PawnId);
                    if (pawn == null) continue;

                    // 1. Reconcile Canonical Position
                    var targetPos = new IntVec3(pData.PosX, pData.PosY, pData.PosZ);
                    if (pawn.Position != targetPos && targetPos.InBounds(map))
                    {
                        pawn.Position = targetPos;
                        if (!map.thingGrid.ThingsAt(targetPos).Contains(pawn))
                        {
                            map.thingGrid.Register(pawn);
                        }
                    }

                    // 2. Presentation-Only Correction (CRITICAL E2 FIX)
                    // Native state touched:
                    //  a. pawn.Drawer.tweener.ResetTweenedPosToRoot(): forces tweener to synchronize with pawn.Position immediately.
                    //  b. PawnTweener.tweenedPos: if authoritative DrawPos was supplied, sets exact sub-cell coordinate.
                    //  c. pawn.pather.StopDead(): suppresses un-ticked local pathing from fighting or anchoring the tweener.
                    // Why presentation-only:
                    //  Does not advance local tactical physics or grant simulation authority. PawnTweener is solely
                    //  used by Pawn_DrawTracker for rendering sprite coordinates and GenUI.ThingsUnderMouse hit testing.
                    if (pawn.Drawer?.tweener != null)
                    {
                        pawn.Drawer.tweener.ResetTweenedPosToRoot();
                        if (pData.DrawPosX > 0.001f && TweenedPosField != null)
                        {
                            Vector3 authDrawPos = new Vector3(pData.DrawPosX, pData.DrawPosY, pData.DrawPosZ);
                            TweenedPosField.SetValue(pawn.Drawer.tweener, authDrawPos);
                        }
                    }

                    // Stop local dead pathing if any so it doesn't fight presentation
                    if (pawn.pather != null && pawn.pather.Moving)
                    {
                        pawn.pather.StopDead();
                    }

                    // 3. Reconcile Draft State
                    if (pawn.drafter != null && pawn.drafter.Drafted != pData.Drafted)
                    {
                        pawn.drafter.Drafted = pData.Drafted;
                    }

                    // 4. Reconcile Rotation (canonical wire contract: 0=North, 1=East, 2=South, 3=West)
                    int rotInt = RotationWireContract.FromWire(pData.Rotation);
                    pawn.Rotation = new Rot4(rotInt);

                    // 5. Narrow Job Reconcile (Goto / Destination / Idle)
                    if (pawn.jobs != null)
                    {
                        string curLocalJob = pawn.CurJob?.def?.defName ?? "None";
                        if (pData.CurJobDef == "Goto")
                        {
                            var destCell = new IntVec3(pData.JobTargetX, 0, pData.JobTargetZ);
                            if (destCell.IsValid && destCell.InBounds(map))
                            {
                                bool isMatchingGoto = pawn.CurJob != null &&
                                                      pawn.CurJob.def == JobDefOf.Goto &&
                                                      pawn.CurJob.targetA.Cell == destCell;
                                if (!isMatchingGoto)
                                {
                                    Job mirrorGoto = JobMaker.MakeJob(JobDefOf.Goto, destCell);
                                    pawn.jobs.TryTakeOrderedJob(mirrorGoto, JobTag.Misc);
                                }
                            }
                        }
                        else
                        {
                            // Worker is NOT in Goto (e.g. reached destination, idle, Wait_Combat)
                            if (curLocalJob == "Goto")
                            {
                                pawn.jobs.EndCurrentJob(JobCondition.Succeeded, false);
                            }
                            else if (curLocalJob != "None" && curLocalJob != "Wait_Combat" && curLocalJob != "Wait_MaintainPosture")
                            {
                                pawn.jobs.EndCurrentJob(JobCondition.InterruptForced, false);
                            }
                        }
                    }

                    // 6. Reconcile Health / Hediffs
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

        /// <summary>
        /// Dedicated background replication loop running off the Unity main thread.
        /// Handles socket I/O, network read waits, timeouts, and bounded request dispatch.
        /// Never mutates Unity/RimWorld objects directly; queues snapshots for main-thread application.
        /// </summary>
        private void ReplicationThreadLoop()
        {
            while (IsRunning && !_stopReplicationThread)
            {
                try
                {
                    if (!ReplicationActive)
                    {
                        Thread.Sleep(50);
                        continue;
                    }

                    if (!IsConnected)
                    {
                        ReplicationDegraded = true;
                        Thread.Sleep(200);
                        continue;
                    }

                    // Ensure dedicated replication socket is connected to gameplay port
                    if (_repClient == null || !_repClient.Connected)
                    {
                        try
                        {
                            _repClient = new TcpClient();
                            _repClient.ReceiveTimeout = 3500; // 3.5s timeout for simulated delays
                            _repClient.SendTimeout = 2000;
                            _repClient.Connect(WorkerHost, WorkerPort);
                            _repStream = _repClient.GetStream();
                            _repReader = new StreamReader(_repStream, Encoding.UTF8);
                            _repWriter = new StreamWriter(_repStream, new UTF8Encoding(false)) { AutoFlush = true };
                            ReplicationDegraded = false;
                        }
                        catch (Exception)
                        {
                            ReplicationDegraded = true;
                            Thread.Sleep(500);
                            continue;
                        }
                    }

                    // Bounded in-flight replication request (exactly 1 at a time)
                    long reqSeq = Interlocked.Increment(ref _autoRepSequence);
                    var cmd = new RemoteTacticalCommand
                    {
                        CommandId = "AUTO_REP_" + reqSeq,
                        TacticalSessionId = ExpectedSessionId,
                        Token = ActiveToken,
                        Generation = ClientGeneration,
                        CommandType = "GET_SNAPSHOT",
                        Source = "OPERATIONAL_PERIODIC_SUBSCRIPTION"
                    };

                    if (_repWriter == null || _repReader == null)
                    {
                        Thread.Sleep(100);
                        continue;
                    }

                    long tSend = Stopwatch.GetTimestamp();
                    cmd.ClientSentTicks = tSend.ToString();
                    string json = Protocols.SerializeCommand(cmd);

                    _repWriter.WriteLine(json);

                    // Network read wait occurs off the Unity main thread!
                    string? respJson = _repReader.ReadLine();
                    long tRecv = Stopwatch.GetTimestamp();

                    if (string.IsNullOrEmpty(respJson))
                    {
                        ReplicationDegraded = true;
                        CloseRepClient();
                        Thread.Sleep(200);
                        continue;
                    }

                    int updateBytes = Protocols.GetUtf8ByteCount(respJson);
                    CommandResponse resp = Protocols.ParseResponse(respJson);

                    if (resp.Snapshot != null)
                    {
                        // Coalescing queue: keep latest snapshot for main thread to apply
                        lock (_snapshotLock)
                        {
                            _pendingSnapshotToApply = resp.Snapshot;
                            _pendingSnapshotBytes = updateBytes;
                            _pendingSnapshotRoundtripMs = (float)((tRecv - tSend) * (1000.0 / Stopwatch.Frequency));
                        }
                        ReplicationDegraded = false;
                    }

                    // Cadence interval sleep
                    int sleepMs = (int)(ReplicationInterval * 1000f);
                    if (sleepMs > 0) Thread.Sleep(sleepMs);
                }
                catch (SocketException)
                {
                    ReplicationDegraded = true;
                    CloseRepClient();
                    Thread.Sleep(500);
                }
                catch (IOException)
                {
                    ReplicationDegraded = true;
                    CloseRepClient();
                    Thread.Sleep(500);
                }
                catch (Exception ex)
                {
                    Log.Warning($"[CLIENT_REPLICATION] Background loop exception: {ex.Message}");
                    Thread.Sleep(500);
                }
            }
        }

        private void CloseRepClient()
        {
            try
            {
                _repWriter?.Close();
                _repReader?.Close();
                _repStream?.Close();
                _repClient?.Close();
            }
            catch { }
            _repClient = null;
            _repStream = null;
            _repReader = null;
            _repWriter = null;
        }

        public void ResetFrameMetrics()
        {
            MaxMainThreadFrameMs = 0f;
            _lastFrameTimestamp = Time.realtimeSinceStartup;
        }

        private void Update()
        {
            // Measure Unity main thread frame time to prove non-blocking liveness
            float now = Time.realtimeSinceStartup;
            if (_lastFrameTimestamp > 0f)
            {
                float frameMs = (now - _lastFrameTimestamp) * 1000f;
                if (frameMs > MaxMainThreadFrameMs)
                {
                    MaxMainThreadFrameMs = frameMs;
                }
            }
            _lastFrameTimestamp = now;

            // Process external control queue
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
                                pending.Response = $"STATUS: Maps={maps}, Pawns={pawns}, TicksGame={ticks}, ConnectedToWorker={IsConnected}, AutoRepActive={ReplicationActive}, RepCount={PeriodicMetrics.Count}, MaxFrameMs={MaxMainThreadFrameMs:F1}, RepDegraded={ReplicationDegraded}";
                            }
                            break;

                        case "SET_REPLICATION":
                            {
                                ReplicationActive = pending.Argument == "1" || pending.Argument.ToLowerInvariant() == "true";
                                pending.Response = $"OK: ReplicationActive={ReplicationActive}";
                            }
                            break;

                        case "RESET_FRAME_METRICS":
                            {
                                ResetFrameMetrics();
                                pending.Response = "OK: Frame metrics reset.";
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

            // Apply coalesced pending snapshot strictly on the Unity main thread!
            ReplicationSnapshot? snapToApply = null;
            int snapBytes = 0;
            float snapRoundtripMs = 0f;
            lock (_snapshotLock)
            {
                if (_pendingSnapshotToApply != null)
                {
                    snapToApply = _pendingSnapshotToApply;
                    snapBytes = _pendingSnapshotBytes;
                    snapRoundtripMs = _pendingSnapshotRoundtripMs;
                    _pendingSnapshotToApply = null;
                }
            }

            if (snapToApply != null)
            {
                long tBeforeApply = Stopwatch.GetTimestamp();
                bool applied = ValidateAndApplySnapshot(snapToApply, out string rejReason);
                long tAfterApply = Stopwatch.GetTimestamp();

                float applyMs = (float)((tAfterApply - tBeforeApply) * (1000.0 / Stopwatch.Frequency));
                float intervalMs = _lastPeriodicReceiveTime > 0 ? (float)((now - _lastPeriodicReceiveTime) * 1000.0) : 0f;
                _lastPeriodicReceiveTime = now;

                string pawnPosSummary = "";
                if (snapToApply.Pawns != null)
                {
                    pawnPosSummary = string.Join("; ", snapToApply.Pawns.Select(p => $"{p.PawnId}@{p.PosX},{p.PosZ} DrawPos=({p.DrawPosX:F2},{p.DrawPosZ:F2}) Job={p.CurJobDef} Rot={p.Rotation}"));
                }

                var metric = new PeriodicReplicationMetric
                {
                    Sequence = snapToApply.SnapshotSequence,
                    AuthoritativeTick = snapToApply.AuthoritativeTick,
                    PayloadBytes = snapBytes,
                    CadenceIntervalMs = intervalMs,
                    LoopbackReceiveToApplyMs = applyMs,
                    TotalRoundtripMs = snapRoundtripMs,
                    ReconcileStatus = applied ? "APPLIED" : $"REJECTED_{rejReason}",
                    PawnPositions = pawnPosSummary
                };
                PeriodicMetrics.Add(metric);
            }
        }

        public void Disconnect()
        {
            ReplicationDegraded = true;
            try
            {
                _writer?.Close();
                _reader?.Close();
                _stream?.Close();
                _tcpClient?.Close();
            }
            catch { }
            _tcpClient = null;
            CloseRepClient();
            Log.Message("[RemoteClientController] Disconnected from Worker. State set to DEGRADED.");
        }

        private void OnDestroy()
        {
            IsRunning = false;
            _stopReplicationThread = true;
            try
            {
                _serverListener?.Stop();
                _serverThread?.Abort();
            }
            catch { }
            try
            {
                _replicationThread?.Abort();
            }
            catch { }
            Disconnect();
            Log.Message("[RemoteClientController] Client component destroyed.");
        }
    }
}
