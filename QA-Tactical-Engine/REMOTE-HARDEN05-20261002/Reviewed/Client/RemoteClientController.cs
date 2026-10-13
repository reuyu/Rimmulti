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
        private int _pendingSnapshotEpoch = 0;
        private int _pendingSnapshotBytes = 0;
        private float _pendingSnapshotRoundtripMs = 0f;

        // Transport Epoch & Fencing (Section 2 & 5)
        public int TransportEpoch { get; private set; } = 1;

        // Async interactive command queue & worker (Section 1 & 4)
        public enum CommandState
        {
            Pending,
            Executing,
            Accepted,
            Rejected,
            TimedOut,
            TransportFailed,
            EpochInvalidated
        }

        public class PendingInteractiveCommand
        {
            public RemoteTacticalCommand Command = new RemoteTacticalCommand();
            public int SentTransportEpoch = 1;
            public long EnqueuedTimestamp = 0;
            public float TimeoutMs = 1500f; // Bounded deadline (1.5 seconds)
            public CommandState State = CommandState.Pending;
            public CommandResponse? Response;
            public Action<CommandResponse>? OnCompleted; // Called strictly on main thread!
            public ManualResetEvent? SyncWaitHandle;
        }

        private readonly ConcurrentQueue<PendingInteractiveCommand> _cmdSendQueue = new ConcurrentQueue<PendingInteractiveCommand>();
        private readonly ConcurrentQueue<PendingInteractiveCommand> _cmdResultQueue = new ConcurrentQueue<PendingInteractiveCommand>();
        public const int MaxPendingCommands = 32;

        private Thread? _commandWorkerThread;
        private volatile bool _stopCommandWorkerThread = false;

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
            Application.runInBackground = true;
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = 60;
            Log.Message("[RemoteClientController] Presentation Client component created. RunInBackground=true, TargetFrameRate=60.");
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

            // Start dedicated non-blocking interactive command worker thread
            _stopCommandWorkerThread = false;
            _commandWorkerThread = new Thread(CommandWorkerLoop)
            {
                IsBackground = true,
                Name = "RemoteClientCommandLoop"
            };
            _commandWorkerThread.Start();

            Log.Message($"[RemoteClientController] Control TCP Server listening on port {ListenPort}. Replication & Command threads started.");
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

                    if (_extQueue.Count >= 32)
                    {
                        writer.WriteLine("ERROR: External command queue full (max 32).");
                        continue;
                    }

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

        public void CloseTcpClient()
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
            _stream = null;
            _reader = null;
            _writer = null;
        }

        public bool ConnectCommandSocket(string host, int port)
        {
            try
            {
                CloseTcpClient();
                WorkerHost = host;
                WorkerPort = port;
                _tcpClient = new TcpClient();
                _tcpClient.Connect(WorkerHost, WorkerPort);
                _stream = _tcpClient.GetStream();
                _reader = new StreamReader(_stream, Encoding.UTF8);
                _writer = new StreamWriter(_stream, new UTF8Encoding(false)) { AutoFlush = true };
                Log.Message($"[RemoteClientController] Command socket connected to {WorkerHost}:{WorkerPort}.");
                return true;
            }
            catch (Exception ex)
            {
                Log.Error($"[RemoteClientController] Failed to connect command socket: {ex.Message}");
                return false;
            }
        }

        public bool ConnectToWorker(string host, int port)
        {
            try
            {
                Disconnect(); // Advance epoch, clear pending snapshots, cancel old commands
                bool ok = ConnectCommandSocket(host, port);
                ReplicationDegraded = !ok;
                Log.Message($"[RemoteClientController] Connected to Tactical Worker at {WorkerHost}:{WorkerPort}. TransportEpoch={TransportEpoch}.");
                return ok;
            }
            catch (Exception ex)
            {
                Log.Error($"[RemoteClientController] Failed to connect to Worker: {ex}");
                ReplicationDegraded = true;
                return false;
            }
        }

        /// <summary>
        /// Non-blocking interactive command submission (Section 1).
        /// Unity GUI callbacks invoke this and return immediately without waiting on socket I/O.
        /// </summary>
        public bool SubmitCommandAsync(RemoteTacticalCommand cmd, Action<CommandResponse>? onCompleted = null, float timeoutMs = 4000f, ManualResetEvent? syncWaitHandle = null)
        {
            if (string.IsNullOrEmpty(cmd.CommandId))
            {
                cmd.CommandId = "CMD_" + Guid.NewGuid().ToString("N").Substring(0, 8);
            }

            if (!IsConnected)
            {
                onCompleted?.Invoke(new CommandResponse
                {
                    CommandId = cmd.CommandId,
                    Success = false,
                    Status = "NOT_CONNECTED",
                    Message = "Client is not connected to Worker.",
                    TransportEpoch = TransportEpoch,
                    CommandState = "TransportFailed"
                });
                syncWaitHandle?.Set();
                return false;
            }

            if (_cmdSendQueue.Count >= MaxPendingCommands)
            {
                Log.Warning($"[CLIENT_CMD] Interactive command queue full ({_cmdSendQueue.Count}/{MaxPendingCommands}). Dropping command {cmd.CommandId}.");
                onCompleted?.Invoke(new CommandResponse
                {
                    CommandId = cmd.CommandId,
                    Success = false,
                    Status = "QUEUE_FULL",
                    Message = "Client interactive command send queue is full.",
                    TransportEpoch = TransportEpoch,
                    CommandState = "TransportFailed"
                });
                syncWaitHandle?.Set();
                return false;
            }

            cmd.TransportEpoch = TransportEpoch;
            if (string.IsNullOrEmpty(cmd.Token)) cmd.Token = ActiveToken;
            if (cmd.Generation <= 0) cmd.Generation = ClientGeneration;
            if (string.IsNullOrEmpty(cmd.TacticalSessionId)) cmd.TacticalSessionId = ExpectedSessionId;

            var pending = new PendingInteractiveCommand
            {
                Command = cmd,
                SentTransportEpoch = TransportEpoch,
                EnqueuedTimestamp = Stopwatch.GetTimestamp(),
                TimeoutMs = timeoutMs,
                State = CommandState.Pending,
                OnCompleted = onCompleted,
                SyncWaitHandle = syncWaitHandle
            };

            _cmdSendQueue.Enqueue(pending);
            Log.Message($"[CLIENT_CMD] Enqueued async command {cmd.CommandType} (ID={cmd.CommandId}, Epoch={cmd.TransportEpoch}, Timeout={timeoutMs}ms). QueueSize={_cmdSendQueue.Count}.");
            return true;
        }

        /// <summary>
        /// Synchronous wrapper for test harnesses and external orchestrators.
        /// Enqueues command to background worker thread and waits on wait handle with timeout.
        /// </summary>
        public CommandResponse SendCommand(RemoteTacticalCommand cmd, float timeoutMs = 4000f)
        {
            if (!IsConnected)
            {
                return new CommandResponse
                {
                    CommandId = cmd.CommandId,
                    Success = false,
                    Status = "NOT_CONNECTED",
                    Message = "Client is not connected to Worker.",
                    TransportEpoch = TransportEpoch,
                    CommandState = "TransportFailed"
                };
            }

            var handle = new ManualResetEvent(false);
            if (string.IsNullOrEmpty(cmd.CommandId))
            {
                cmd.CommandId = "CMD_" + Guid.NewGuid().ToString("N").Substring(0, 8);
            }
            cmd.TransportEpoch = TransportEpoch;
            if (string.IsNullOrEmpty(cmd.Token)) cmd.Token = ActiveToken;
            if (cmd.Generation <= 0) cmd.Generation = ClientGeneration;
            if (string.IsNullOrEmpty(cmd.TacticalSessionId)) cmd.TacticalSessionId = ExpectedSessionId;

            var pending = new PendingInteractiveCommand
            {
                Command = cmd,
                SentTransportEpoch = TransportEpoch,
                EnqueuedTimestamp = Stopwatch.GetTimestamp(),
                TimeoutMs = timeoutMs,
                State = CommandState.Pending,
                SyncWaitHandle = handle
            };

            if (_cmdSendQueue.Count >= MaxPendingCommands)
            {
                return new CommandResponse
                {
                    CommandId = cmd.CommandId,
                    Success = false,
                    Status = "QUEUE_FULL",
                    Message = "Failed to enqueue command.",
                    TransportEpoch = TransportEpoch,
                    CommandState = "TransportFailed"
                };
            }

            _cmdSendQueue.Enqueue(pending);

            bool completed = handle.WaitOne((int)(timeoutMs + 500));
            if (!completed)
            {
                return new CommandResponse
                {
                    CommandId = cmd.CommandId,
                    Success = false,
                    Status = "TIMEOUT",
                    Message = $"Timed out after {timeoutMs}ms waiting for command response.",
                    TransportEpoch = TransportEpoch,
                    CommandState = "TimedOut"
                };
            }

            if (pending.Response != null && pending.Response.Success && pending.Response.Snapshot != null)
            {
                ValidateAndApplySnapshot(pending.Response.Snapshot, out _);
            }

            return pending.Response ?? new CommandResponse
            {
                CommandId = cmd.CommandId,
                Success = false,
                Status = "NO_RESPONSE",
                Message = "No response received.",
                TransportEpoch = TransportEpoch,
                CommandState = "TransportFailed"
            };
        }

        /// <summary>
        /// Dedicated background loop for off-main-thread command serialization, socket write, and socket read.
        /// (Section 1 CRITICAL requirement).
        /// </summary>
        private void CommandWorkerLoop()
        {
            while (IsRunning && !_stopCommandWorkerThread)
            {
                try
                {
                    if (_cmdSendQueue.TryDequeue(out var pending))
                    {
                        ProcessInteractiveCommandOffMainThread(pending);
                    }
                    else
                    {
                        Thread.Sleep(5);
                    }
                }
                catch (Exception ex)
                {
                    Log.Error($"[CLIENT_CMD_THREAD] Exception in command worker loop: {ex}");
                    Thread.Sleep(50);
                }
            }
        }

        private void ProcessInteractiveCommandOffMainThread(PendingInteractiveCommand pending)
        {
            // 1. Check if transport epoch changed before write
            if (pending.SentTransportEpoch != TransportEpoch)
            {
                pending.State = CommandState.EpochInvalidated;
                pending.Response = new CommandResponse
                {
                    CommandId = pending.Command.CommandId,
                    Success = false,
                    Status = "EPOCH_INVALIDATED",
                    Message = $"Transport epoch changed ({pending.SentTransportEpoch} != {TransportEpoch}) before socket write.",
                    TransportEpoch = pending.SentTransportEpoch,
                    CommandState = "EpochInvalidated"
                };
                _cmdResultQueue.Enqueue(pending);
                pending.SyncWaitHandle?.Set();
                return;
            }

            // 2. Check if deadline expired before writing
            double elapsedBeforeWrite = (Stopwatch.GetTimestamp() - pending.EnqueuedTimestamp) * (1000.0 / Stopwatch.Frequency);
            if (elapsedBeforeWrite >= pending.TimeoutMs)
            {
                pending.State = CommandState.TimedOut;
                pending.Response = new CommandResponse
                {
                    CommandId = pending.Command.CommandId,
                    Success = false,
                    Status = "TIMEOUT",
                    Message = $"Command deadline exceeded before socket write ({elapsedBeforeWrite:F1}ms >= {pending.TimeoutMs}ms).",
                    TransportEpoch = pending.SentTransportEpoch,
                    CommandState = "TimedOut"
                };
                _cmdResultQueue.Enqueue(pending);
                pending.SyncWaitHandle?.Set();
                return;
            }

            // 3. Check connection / auto-reconnect if needed
            if (!IsConnected || _writer == null || _reader == null)
            {
                if (!string.IsNullOrEmpty(WorkerHost) && WorkerPort > 0)
                {
                    ConnectCommandSocket(WorkerHost, WorkerPort);
                }

                if (!IsConnected || _writer == null || _reader == null)
                {
                    pending.State = CommandState.TransportFailed;
                    pending.Response = new CommandResponse
                    {
                        CommandId = pending.Command.CommandId,
                        Success = false,
                        Status = "NOT_CONNECTED",
                        Message = "Worker socket not connected.",
                        TransportEpoch = pending.SentTransportEpoch,
                        CommandState = "TransportFailed"
                    };
                    _cmdResultQueue.Enqueue(pending);
                    pending.SyncWaitHandle?.Set();
                    return;
                }
            }

            try
            {
                int remainingTimeout = Math.Max(50, (int)(pending.TimeoutMs - elapsedBeforeWrite));
                if (_tcpClient != null)
                {
                    _tcpClient.ReceiveTimeout = remainingTimeout;
                    _tcpClient.SendTimeout = remainingTimeout;
                }

                pending.Command.ClientSentTicks = Stopwatch.GetTimestamp().ToString();
                string json = Protocols.SerializeCommand(pending.Command);
                _writer.WriteLine(json);

                string? respJson = null;
                try
                {
                    respJson = _reader.ReadLine();
                }
                catch (IOException) // socket read timeout
                {
                    Log.Warning($"[CLIENT_CMD_THREAD] Worker socket read timed out after {pending.TimeoutMs}ms. Closing socket to prevent stream desync.");
                    CloseTcpClient();
                    pending.State = CommandState.TimedOut;
                    pending.Response = new CommandResponse
                    {
                        CommandId = pending.Command.CommandId,
                        Success = false,
                        Status = "TIMEOUT",
                        Message = $"Worker socket read timed out after {pending.TimeoutMs}ms.",
                        TransportEpoch = pending.SentTransportEpoch,
                        CommandState = "TimedOut"
                    };
                    _cmdResultQueue.Enqueue(pending);
                    pending.SyncWaitHandle?.Set();
                    return;
                }

                long clientReceivedTicks = Stopwatch.GetTimestamp();
                if (string.IsNullOrEmpty(respJson))
                {
                    CloseTcpClient();
                    pending.State = CommandState.TransportFailed;
                    pending.Response = new CommandResponse
                    {
                        CommandId = pending.Command.CommandId,
                        Success = false,
                        Status = "EMPTY_RESPONSE",
                        Message = "Worker returned empty response or closed socket.",
                        TransportEpoch = pending.SentTransportEpoch,
                        CommandState = "TransportFailed"
                    };
                    _cmdResultQueue.Enqueue(pending);
                    pending.SyncWaitHandle?.Set();
                    return;
                }

                CommandResponse resp = Protocols.ParseResponse(respJson);

                // 4. Validate epoch after read (Section 2 & 5)
                if (pending.SentTransportEpoch != TransportEpoch)
                {
                    Log.Warning($"[CLIENT_CMD_THREAD] Dropping late response for {pending.Command.CommandId}: connection epoch changed ({pending.SentTransportEpoch} != {TransportEpoch}).");
                    pending.State = CommandState.EpochInvalidated;
                    resp.Success = false;
                    resp.Status = "EPOCH_INVALIDATED";
                    resp.Message = "Response arrived after connection epoch advanced.";
                    resp.CommandState = "EpochInvalidated";
                }
                else
                {
                    // 5. Validate deadline after read (Section 3)
                    double totalElapsed = (clientReceivedTicks - pending.EnqueuedTimestamp) * (1000.0 / Stopwatch.Frequency);
                    if (totalElapsed > pending.TimeoutMs)
                    {
                        Log.Warning($"[CLIENT_CMD_THREAD] Response for {pending.Command.CommandId} arrived late ({totalElapsed:F1}ms > {pending.TimeoutMs}ms). Discarding authoritative apply.");
                        pending.State = CommandState.TimedOut;
                        resp.Success = false;
                        resp.Status = "TIMEOUT";
                        resp.Message = $"Late response arrived after deadline ({totalElapsed:F1}ms > {pending.TimeoutMs}ms).";
                        resp.CommandState = "TimedOut";
                    }
                    else
                    {
                        pending.State = resp.Success ? CommandState.Accepted : CommandState.Rejected;
                        resp.CommandState = "Completed";
                    }
                }

                pending.Response = resp;
                _cmdResultQueue.Enqueue(pending);
                pending.SyncWaitHandle?.Set();
            }
            catch (Exception ex)
            {
                pending.State = CommandState.TransportFailed;
                pending.Response = new CommandResponse
                {
                    CommandId = pending.Command.CommandId,
                    Success = false,
                    Status = "TRANSPORT_EXCEPTION",
                    Message = ex.Message,
                    TransportEpoch = pending.SentTransportEpoch,
                    CommandState = "TransportFailed"
                };
                _cmdResultQueue.Enqueue(pending);
                pending.SyncWaitHandle?.Set();
            }
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
                            _pendingSnapshotEpoch = TransportEpoch;
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
                float frameMs = Time.unscaledDeltaTime * 1000f;
                if (frameMs > MaxMainThreadFrameMs)
                {
                    MaxMainThreadFrameMs = frameMs;
                }
            }
            _lastFrameTimestamp = now;

            // 1. Drain interactive command result queue strictly on Unity main thread (Section 1 & 4: bounded budget of max 5 per frame)
            int cmdDrainCount = 0;
            while (cmdDrainCount < 5 && _cmdResultQueue.TryDequeue(out var finishedCmd))
            {
                cmdDrainCount++;
                try
                {
                    // Section 2 & 5: Transport Epoch fencing
                    if (finishedCmd.SentTransportEpoch != TransportEpoch)
                    {
                        Log.Warning($"[CLIENT_CMD_MAIN] Discarding result for command {finishedCmd.Command.CommandId}: TransportEpoch changed ({finishedCmd.SentTransportEpoch} != {TransportEpoch}).");
                        if (finishedCmd.Response != null)
                        {
                            finishedCmd.Response.Success = false;
                            finishedCmd.Response.Status = "EPOCH_INVALIDATED";
                            finishedCmd.Response.CommandState = "EpochInvalidated";
                        }
                    }
                    else
                    {
                        // If command succeeded and returned an authoritative snapshot, apply it on the main thread
                        if (finishedCmd.Response != null && finishedCmd.Response.Success && finishedCmd.Response.Snapshot != null)
                        {
                            ValidateAndApplySnapshot(finishedCmd.Response.Snapshot, out _);
                        }
                    }

                    // Fire OnCompleted callback strictly on Unity main thread!
                    try
                    {
                        finishedCmd.OnCompleted?.Invoke(finishedCmd.Response ?? new CommandResponse
                        {
                            CommandId = finishedCmd.Command.CommandId,
                            Success = false,
                            Status = "NO_RESPONSE",
                            Message = "Command completed without response object.",
                            TransportEpoch = finishedCmd.SentTransportEpoch,
                            CommandState = "TransportFailed"
                        });
                    }
                    catch (Exception cbEx)
                    {
                        Log.Error($"[CLIENT_CMD_MAIN] Exception in OnCompleted callback for {finishedCmd.Command.CommandId}: {cbEx}");
                    }
                }
                catch (Exception ex)
                {
                    Log.Error($"[CLIENT_CMD_MAIN] Exception processing command result for {finishedCmd.Command.CommandId}: {ex}");
                }
            }

            // 2. Process external control queue
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
                                pending.Response = $"STATUS: Maps={maps}, Pawns={pawns}, TicksGame={ticks}, ConnectedToWorker={IsConnected}, AutoRepActive={ReplicationActive}, RepCount={PeriodicMetrics.Count}, MaxFrameMs={MaxMainThreadFrameMs:F1}, RepDegraded={ReplicationDegraded}, Epoch={TransportEpoch}";
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

            // 3. Apply coalesced pending snapshot strictly on the Unity main thread!
            ReplicationSnapshot? snapToApply = null;
            int snapEpoch = 0;
            int snapBytes = 0;
            float snapRoundtripMs = 0f;
            lock (_snapshotLock)
            {
                if (_pendingSnapshotToApply != null)
                {
                    snapToApply = _pendingSnapshotToApply;
                    snapEpoch = _pendingSnapshotEpoch;
                    snapBytes = _pendingSnapshotBytes;
                    snapRoundtripMs = _pendingSnapshotRoundtripMs;
                    _pendingSnapshotToApply = null;
                }
            }

            if (snapToApply != null)
            {
                // Section 5: Disconnect epoch / pending snapshot lifecycle
                // Invalidate if snapshot was received under an older transport epoch
                if (snapEpoch != TransportEpoch)
                {
                    Log.Warning($"[CLIENT_REPLICATION] Dropping coalesced snapshot {snapToApply.SnapshotSequence}: epoch mismatch (snapEpoch={snapEpoch} != currentEpoch={TransportEpoch}).");
                    TotalSnapshotsRejected++;
                }
                else
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
                        pawnPosSummary = string.Join("; ", snapToApply.Pawns.Select(p => $"{p.PawnId}@{p.PosX},{p.PosZ} DrawPos=({p.DrawPosX:F2},{p.DrawPosZ:F2}) Job={p.CurJobDef} Rot={p.Rotation} Pose={p.PoseSource}"));
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

                    // Section 4: bounded retention (max 100 entries)
                    if (PeriodicMetrics.Count > 100)
                    {
                        PeriodicMetrics.RemoveAt(0);
                    }
                }
            }
        }

        public void Disconnect()
        {
            ReplicationDegraded = true;
            int oldEpoch = TransportEpoch;
            TransportEpoch++;
            Log.Message($"[RemoteClientController] Disconnecting from Worker. Advancing TransportEpoch from {oldEpoch} to {TransportEpoch}.");

            // Invalidate coalesced pending snapshot from old epoch (Section 5)
            lock (_snapshotLock)
            {
                _pendingSnapshotToApply = null;
            }

            // Drain & invalidate any pending commands in send queue (Section 2 & 5)
            while (_cmdSendQueue.TryDequeue(out var pending))
            {
                pending.State = CommandState.EpochInvalidated;
                pending.Response = new CommandResponse
                {
                    CommandId = pending.Command.CommandId,
                    Success = false,
                    Status = "EPOCH_INVALIDATED",
                    Message = "Connection disconnected before command could be sent.",
                    TransportEpoch = pending.SentTransportEpoch,
                    CommandState = "EpochInvalidated"
                };
                _cmdResultQueue.Enqueue(pending);
                pending.SyncWaitHandle?.Set();
            }

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
            _stopCommandWorkerThread = true;
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
            try
            {
                _commandWorkerThread?.Abort();
            }
            catch { }
            Disconnect();
            Log.Message("[RemoteClientController] Client component destroyed.");
        }
    }
}
