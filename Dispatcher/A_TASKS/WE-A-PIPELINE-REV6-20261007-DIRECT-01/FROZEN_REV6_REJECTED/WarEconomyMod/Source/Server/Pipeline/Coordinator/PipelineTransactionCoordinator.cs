using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Channels;
using System.Threading.Tasks;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Storage;

namespace WarEconomy.Server.Pipeline.Coordinator
{
    public interface IPipelineTransactionCoordinator : IDisposable
    {
        PipelineProbeResult ExecuteProbeCas(PipelineProbeRequest request);
        Task<PipelineProbeResult> ExecuteProbeCasAsync(PipelineProbeRequest request);
        PipelineProbeResult ExecuteAdmittedCommand(ImmutablePipelineProbeCommand command);
        Task<PipelineProbeResult> ExecuteAdmittedCommandAsync(ImmutablePipelineProbeCommand command);
    }

    internal class WriterWorkItem
    {
        public ImmutablePipelineProbeCommand Command { get; }
        public TaskCompletionSource<PipelineProbeResult> Tcs { get; }

        public WriterWorkItem(ImmutablePipelineProbeCommand command)
        {
            Command = command;
            Tcs = new TaskCompletionSource<PipelineProbeResult>(TaskCreationOptions.RunContinuationsAsynchronously);
        }
    }

    public class PipelineTransactionCoordinatorOptions
    {
        public int BoundedCapacity { get; set; } = 1000;
        public TimeSpan AdmissionTimeout { get; set; } = TimeSpan.FromSeconds(2);
        public int SimulatedWriterDelayMs { get; set; } = 0;
    }

    public class PipelineTransactionCoordinator : IPipelineTransactionCoordinator
    {
        private readonly SqliteDatabaseContext _dbContext;
        private readonly IOperationJournal _journal;
        private readonly IProbeAggregateStore _probeStore;
        private readonly ICommitReceiptRepository _receipts;
        private readonly IAuditLogRepository _auditLogs;
        private readonly IPublicationEventStore _eventStore;
        private readonly PipelineTransactionCoordinatorOptions _options;

        private readonly Channel<WriterWorkItem> _channel;
        private readonly Thread _writerThread;
        private readonly CancellationTokenSource _cts = new();

        private volatile bool _isDisposed = false;
        private volatile bool _shutdownInitiated = false;

        public bool IsDisposed => _isDisposed;
        public bool IsShutdownInitiated => _shutdownInitiated;

        public PipelineTransactionCoordinator(
            SqliteDatabaseContext dbContext,
            IOperationJournal? journal = null,
            IProbeAggregateStore? probeStore = null,
            ICommitReceiptRepository? receipts = null,
            IAuditLogRepository? auditLogs = null,
            IPublicationEventStore? eventStore = null,
            PipelineTransactionCoordinatorOptions? options = null)
        {
            _dbContext = dbContext ?? throw new ArgumentNullException(nameof(dbContext));
            _journal = journal ?? new OperationJournal();
            _probeStore = probeStore ?? new ProbeAggregateStore();
            _receipts = receipts ?? new CommitReceiptRepository();
            _auditLogs = auditLogs ?? new AuditLogRepository();
            _eventStore = eventStore ?? new PublicationEventStore();
            _options = options ?? new PipelineTransactionCoordinatorOptions();

            // Bounded ingress channel
            _channel = Channel.CreateBounded<WriterWorkItem>(new BoundedChannelOptions(_options.BoundedCapacity)
            {
                SingleReader = true,
                SingleWriter = false,
                FullMode = BoundedChannelFullMode.Wait
            });

            // Dedicated writer thread independent of ThreadPool starvation
            _writerThread = new Thread(WriterThreadMain)
            {
                Name = "PipelineTransactionWriter",
                IsBackground = true
            };
            _writerThread.Start();
        }

        private volatile WriterWorkItem? _currentInFlightItem;
        private volatile SqliteConnection? _activeWorkerConnection;

        public PipelineProbeResult ExecuteProbeCas(PipelineProbeRequest request)
        {
            return ExecuteProbeCasAsync(request).GetAwaiter().GetResult();
        }

        public async Task<PipelineProbeResult> ExecuteProbeCasAsync(PipelineProbeRequest request)
        {
            if (request == null)
            {
                return PipelineProbeResult.Error(PipelineProbeOutcome.INVALID_REQUEST, "Request cannot be null.");
            }

            if (_isDisposed || _shutdownInitiated)
            {
                return PipelineProbeResult.StorageBusyRetryable("SERVER_SHUTTING_DOWN: Coordinator is shutting down. Admission closed.");
            }

            // 1. Immutable Admission Validation & Normalization
            // Every mutating request MUST supply a non-null, non-empty, non-whitespace StoreIncarnationId.
            // Do NOT fill missing values from the current store incarnation.
            ImmutablePipelineProbeCommand command;
            try
            {
                command = ImmutablePipelineProbeCommand.FromRequest(request);
            }
            catch (ArgumentException aex)
            {
                return PipelineProbeResult.Error(PipelineProbeOutcome.INVALID_REQUEST, aex.Message);
            }
            catch (Exception ex)
            {
                return PipelineProbeResult.StorageFailure($"Admission validation failed: {ex.Message}");
            }

            return await ExecuteAdmittedCommandAsync(command).ConfigureAwait(false);
        }

        public PipelineProbeResult ExecuteAdmittedCommand(ImmutablePipelineProbeCommand command)
        {
            return ExecuteAdmittedCommandAsync(command).GetAwaiter().GetResult();
        }

        public async Task<PipelineProbeResult> ExecuteAdmittedCommandAsync(ImmutablePipelineProbeCommand command)
        {
            if (command == null)
            {
                return PipelineProbeResult.Error(PipelineProbeOutcome.INVALID_REQUEST, "Command cannot be null.");
            }

            if (_isDisposed || _shutdownInitiated)
            {
                return PipelineProbeResult.StorageBusyRetryable("SERVER_SHUTTING_DOWN: Coordinator is shutting down. Admission closed.");
            }

            var item = new WriterWorkItem(command);

            // Bounded ingress contract: immediate TryWrite admission
            // Do NOT create producer waiters whose TCS is outside the channel and invisible to drain
            if (!_channel.Writer.TryWrite(item))
            {
                if (_isDisposed || _shutdownInitiated)
                {
                    return PipelineProbeResult.StorageBusyRetryable("SERVER_SHUTTING_DOWN: Admission rejected during shutdown.");
                }
                return PipelineProbeResult.StorageBusyRetryable(
                    $"SERVER_BUSY_RETRYABLE: Writer queue at maximum capacity ({_options.BoundedCapacity}). Backpressure rejection.");
            }

            return await item.Tcs.Task.ConfigureAwait(false);
        }

        private void WriterThreadMain()
        {
            var reader = _channel.Reader;

            while (!_cts.IsCancellationRequested)
            {
                try
                {
                    // Wait for work item
                    if (!reader.WaitToReadAsync(_cts.Token).AsTask().GetAwaiter().GetResult())
                    {
                        break;
                    }

                    while (reader.TryRead(out var item))
                    {
                        if (_shutdownInitiated || _cts.IsCancellationRequested)
                        {
                            item.Tcs.TrySetResult(PipelineProbeResult.StorageBusyRetryable(
                                "SERVER_SHUTTING_DOWN: Work item drained during coordinator termination."));
                            continue;
                        }

                        _currentInFlightItem = item;
                        if (_options.SimulatedWriterDelayMs > 0)
                        {
                            Thread.Sleep(_options.SimulatedWriterDelayMs);
                        }

                        try
                        {
                            var result = ExecuteSingleWriterCommit(item.Command);
                            item.Tcs.TrySetResult(result);
                        }
                        catch (Exception ex)
                        {
                            item.Tcs.TrySetException(ex);
                        }
                        finally
                        {
                            _currentInFlightItem = null;
                        }
                    }
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception)
                {
                    // Catch unexpected writer loop exception and continue
                }
            }

            // Drain any remaining items in channel during shutdown
            while (reader.TryRead(out var pendingItem))
            {
                pendingItem.Tcs.TrySetResult(PipelineProbeResult.StorageBusyRetryable(
                    "SERVER_SHUTTING_DOWN: Work item drained during coordinator termination."));
            }

            _isDisposed = true;
        }

        public PipelineProbeResult ExecuteSingleWriterCommit(ImmutablePipelineProbeCommand command)
        {
            try
            {
                using var conn = _dbContext.CreateOpenConnection();
                _activeWorkerConnection = conn;
                try
                {
                    // -----------------------------------------------------------------
                    // STEP 1: BEGIN IMMEDIATE atomic transaction
                    // -----------------------------------------------------------------
                    using var tx = conn.BeginTransaction();

                // -----------------------------------------------------------------
                // STEP 2: In-Transaction StoreIncarnation Fence
                // Must be read under the exact same write lock as the commit!
                // -----------------------------------------------------------------
                string activeIncarnation = _dbContext.GetActiveStoreIncarnationId(conn, tx);
                if (!string.Equals(command.StoreIncarnationId, activeIncarnation, StringComparison.Ordinal))
                {
                    tx.Rollback();
                    return PipelineProbeResult.IncarnationMismatch(activeIncarnation, command.StoreIncarnationId);
                }

                // -----------------------------------------------------------------
                // STEP 3: Arbitrate Operation Identity (PrincipalId, OperationId)
                // -----------------------------------------------------------------
                var existingRecord = _journal.GetRecord(command.PrincipalId, command.OperationId, conn, tx);
                if (existingRecord != null)
                {
                    // Verify RequestFingerprint matches
                    if (!string.Equals(existingRecord.RequestFingerprint, command.RequestFingerprint, StringComparison.Ordinal))
                    {
                        tx.Rollback();
                        return PipelineProbeResult.CollisionRejected(
                            command.PrincipalId,
                            command.OperationId,
                            "Request envelope or payload does not match previously recorded operation with this key.");
                    }

                    // Identical fingerprint: return stored terminal decision
                    if (existingRecord.State == OperationState.COMMITTED)
                    {
                        var existingReceipt = _receipts.GetReceipt(command.PrincipalId, command.OperationId, conn, tx);
                        tx.Rollback();
                        if (existingReceipt != null)
                        {
                            return PipelineProbeResult.Ok(existingReceipt, alreadyCommitted: true);
                        }
                    }
                    else if (existingRecord.State == OperationState.ABORTED)
                    {
                        tx.Rollback();
                        return PipelineProbeResult.Aborted(command.OperationId, existingRecord.FailureReason);
                    }
                }

                // -----------------------------------------------------------------
                // STEP 4: Validate ExpectedProbeRevision
                // -----------------------------------------------------------------
                long? curRev = _probeStore.GetRevision(command.ProbeScopeId, conn, tx);
                long effectiveCurrent = curRev ?? 0L;

                if (effectiveCurrent != command.ExpectedProbeRevision)
                {
                    // CAS mismatch -> Atomically record terminal ABORTED state
                    long nowEpochMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
                    string failureReason = $"STALE_REVISION: expected {command.ExpectedProbeRevision} != actual {effectiveCurrent}";

                    var abortedRecord = new OperationRecord
                    {
                        PrincipalId = command.PrincipalId,
                        OperationId = command.OperationId,
                        OperationType = command.OperationType,
                        OperationSchemaVersion = command.OperationSchemaVersion,
                        ProbeScopeId = command.ProbeScopeId,
                        ExpectedProbeRevision = command.ExpectedProbeRevision,
                        RequestFingerprint = command.RequestFingerprint,
                        PayloadJson = command.CanonicalPayloadJson,
                        ContentProfileFingerprint = command.ContentProfileFingerprint,
                        ConfigSnapshotRef = command.ConfigSnapshotRef,
                        State = OperationState.ABORTED,
                        FailureReason = failureReason,
                        StoreIncarnationId = activeIncarnation,
                        CreatedAtEpochMs = nowEpochMs,
                        UpdatedAtEpochMs = nowEpochMs
                    };

                    _journal.InsertRecord(abortedRecord, conn, tx);

                    string rejectDetailsJson = System.Text.Json.JsonSerializer.Serialize(new
                    {
                        reason = failureReason,
                        status = "STALE_REVISION",
                        expectedRevision = command.ExpectedProbeRevision,
                        observedRevision = effectiveCurrent,
                        scopeId = command.ProbeScopeId,
                        principalId = command.PrincipalId,
                        operationId = command.OperationId
                    });

                    _auditLogs.InsertAudit(new AuditRecord
                    {
                        AuditId = Guid.NewGuid().ToString("N"),
                        PrincipalId = command.PrincipalId,
                        OperationId = command.OperationId,
                        ProbeScopeId = command.ProbeScopeId,
                        EventType = "PROBE_CAS_REJECTED",
                        OldRevision = effectiveCurrent,
                        NewRevision = null,
                        DetailsJson = rejectDetailsJson,
                        TimestampEpochMs = nowEpochMs
                    }, conn, tx);

                    tx.Commit();

                    return PipelineProbeResult.StaleRevisionRejected(command.ProbeScopeId, command.ExpectedProbeRevision, effectiveCurrent);
                }

                long commitEpochMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();

                // -----------------------------------------------------------------
                // STEP 5: Insert Terminal COMMITTED OperationRecord
                // Must be inserted first so child tables satisfy foreign key constraints!
                // -----------------------------------------------------------------
                var committedRecord = new OperationRecord
                {
                    PrincipalId = command.PrincipalId,
                    OperationId = command.OperationId,
                    OperationType = command.OperationType,
                    OperationSchemaVersion = command.OperationSchemaVersion,
                    ProbeScopeId = command.ProbeScopeId,
                    ExpectedProbeRevision = command.ExpectedProbeRevision,
                    RequestFingerprint = command.RequestFingerprint,
                    PayloadJson = command.CanonicalPayloadJson,
                    ContentProfileFingerprint = command.ContentProfileFingerprint,
                    ConfigSnapshotRef = command.ConfigSnapshotRef,
                    State = OperationState.COMMITTED,
                    FailureReason = null,
                    StoreIncarnationId = activeIncarnation,
                    CreatedAtEpochMs = commitEpochMs,
                    UpdatedAtEpochMs = commitEpochMs
                };
                _journal.InsertRecord(committedRecord, conn, tx);

                // -----------------------------------------------------------------
                // STEP 6: CAS Increment Revision and Append to ProbeRevisionHistory
                // -----------------------------------------------------------------
                long newRevision = command.ExpectedProbeRevision + 1;
                bool casSuccess = _probeStore.TryExecuteCas(command.ProbeScopeId, command.ExpectedProbeRevision, newRevision, command.PrincipalId, command.OperationId, conn, tx);
                if (!casSuccess)
                {
                    tx.Rollback();
                    long? postRev = _probeStore.GetRevision(command.ProbeScopeId, conn);
                    return PipelineProbeResult.StaleRevisionRejected(command.ProbeScopeId, command.ExpectedProbeRevision, postRev ?? 0L);
                }

                // -----------------------------------------------------------------
                // STEP 7: Insert Immutable CommitReceipt
                // -----------------------------------------------------------------
                string receiptId = DerivativeIdGenerator.GenerateReceiptId(command.PrincipalId, command.OperationId, newRevision);
                string receiptHash = CommitReceipt.ComputeReceiptHash(
                    receiptId,
                    command.PrincipalId,
                    command.OperationId,
                    command.ProbeScopeId,
                    newRevision,
                    activeIncarnation,
                    commitEpochMs
                );

                var receipt = new CommitReceipt
                {
                    ReceiptId = receiptId,
                    PrincipalId = command.PrincipalId,
                    OperationId = command.OperationId,
                    ProbeScopeId = command.ProbeScopeId,
                    CommittedRevision = newRevision,
                    StoreIncarnationId = activeIncarnation,
                    CommittedAtEpochMs = commitEpochMs,
                    ReceiptHash = receiptHash
                };
                _receipts.InsertReceipt(receipt, conn, tx);

                // -----------------------------------------------------------------
                // STEP 8: Append PublicationEvent (Ordered, Monotonic Seq in Same Tx)
                // -----------------------------------------------------------------
                string eventId = DerivativeIdGenerator.GenerateEventId(command.PrincipalId, command.OperationId, newRevision);
                _eventStore.AppendEvent(
                    streamId: command.ProbeScopeId,
                    eventId: eventId,
                    principalId: command.PrincipalId,
                    operationId: command.OperationId,
                    eventType: "PROBE_REVISION_ADVANCED",
                    payloadJson: command.CanonicalPayloadJson,
                    storeIncarnationId: activeIncarnation,
                    conn: conn,
                    tx: tx
                );

                // -----------------------------------------------------------------
                // STEP 9: Insert Audit Record with typed details
                // -----------------------------------------------------------------
                string committedDetailsJson = System.Text.Json.JsonSerializer.Serialize(new
                {
                    receiptId = receiptId,
                    eventId = eventId,
                    fingerprint = command.RequestFingerprint,
                    scopeId = command.ProbeScopeId,
                    principalId = command.PrincipalId,
                    operationId = command.OperationId,
                    oldRevision = command.ExpectedProbeRevision,
                    newRevision = newRevision
                });

                _auditLogs.InsertAudit(new AuditRecord
                {
                    AuditId = Guid.NewGuid().ToString("N"),
                    PrincipalId = command.PrincipalId,
                    OperationId = command.OperationId,
                    ProbeScopeId = command.ProbeScopeId,
                    EventType = "PROBE_CAS_COMMITTED",
                    OldRevision = command.ExpectedProbeRevision,
                    NewRevision = newRevision,
                    DetailsJson = committedDetailsJson,
                    TimestampEpochMs = commitEpochMs
                }, conn, tx);

                // -----------------------------------------------------------------
                // STEP 10: Commit Atomic Transaction
                // -----------------------------------------------------------------
                tx.Commit();

                return PipelineProbeResult.Ok(receipt, alreadyCommitted: false);
            }
            finally
            {
                _activeWorkerConnection = null;
            }
        }
        catch (SqliteException ex)
        {
            if (ex.SqliteErrorCode == 5 || ex.SqliteErrorCode == 6 || ex.SqliteErrorCode == 9)
            {
                return PipelineProbeResult.StorageBusyRetryable($"SQLite Lock/Interrupt [{ex.SqliteErrorCode}]: {ex.Message}");
            }

            // Explicitly preserve real storage error without converting to revision conflict
            return PipelineProbeResult.StorageFailure($"SqliteException [{ex.SqliteErrorCode}]: {ex.Message}");
        }
        catch (Exception ex)
        {
            return PipelineProbeResult.StorageFailure($"Unexpected storage exception: {ex.Message}");
        }
    }

    public bool TryShutdown(int timeoutMs)
    {
        if (_isDisposed) return true;
        _shutdownInitiated = true;

        // 1. Close channel writer atomically (stop admission)
        _channel.Writer.TryComplete();

        // 2. Mark pipeline as not ready
        if (ReferenceEquals(Recovery.PipelineStartupManager.ActiveCoordinator, this))
        {
            Recovery.PipelineStartupManager.MarkNotReady();
        }

        // 3. Immediately drain unstarted items
        while (_channel.Reader.TryRead(out var pendingItem))
        {
            pendingItem.Tcs.TrySetResult(PipelineProbeResult.StorageBusyRetryable(
                "SERVER_SHUTTING_DOWN: Work item completed during coordinator shutdown."));
        }

        // 4. Bounded response check
        int callerDeadlineMs = Math.Min(1000, timeoutMs);
        bool threadExited = _writerThread.Join(callerDeadlineMs);

        if (!threadExited)
        {
            // Caller completion: complete in-flight caller with UNKNOWN_QUERY_REQUIRED
            var inFlight = _currentInFlightItem;
            if (inFlight != null)
            {
                inFlight.Tcs.TrySetResult(PipelineProbeResult.Error(
                    PipelineProbeOutcome.UNKNOWN_QUERY_REQUIRED,
                    "Shutdown response deadline expired while operation was in-flight. Query operation status before retry."));
            }

            int remainingMs = Math.Max(0, timeoutMs - callerDeadlineMs);
            if (remainingMs > 0)
            {
                threadExited = _writerThread.Join(remainingMs);
            }
        }

        if (threadExited)
        {
            _isDisposed = true;
            _cts.Dispose();
            return true;
        }

        // Timeout expired: writer is still alive. Return false (TERMINATION_PENDING) without completing disposal.
        return false;
    }

    public void Dispose()
    {
        if (_isDisposed) return;
        _shutdownInitiated = true;

        // 1. Close admission
        _channel.Writer.TryComplete();

        // 2. Mark pipeline as not ready
        if (ReferenceEquals(Recovery.PipelineStartupManager.ActiveCoordinator, this))
        {
            Recovery.PipelineStartupManager.MarkNotReady();
        }

        // 3. Drain queued not-started callers
        while (_channel.Reader.TryRead(out var pendingItem))
        {
            pendingItem.Tcs.TrySetResult(PipelineProbeResult.StorageBusyRetryable(
                "SERVER_SHUTTING_DOWN: Work item completed during coordinator shutdown."));
        }

        // 4. Caller completion: after response deadline (1000ms), caller receives UNKNOWN_QUERY_REQUIRED
        bool threadExited = _writerThread.Join(1000);
        if (!threadExited)
        {
            var inFlight = _currentInFlightItem;
            if (inFlight != null)
            {
                inFlight.Tcs.TrySetResult(PipelineProbeResult.Error(
                    PipelineProbeOutcome.UNKNOWN_QUERY_REQUIRED,
                    "Shutdown response deadline expired while operation was in-flight. Query operation status before retry."));
            }

            // 5. Service termination: WAIT INDEFINITELY for writer thread to actually exit!
            // In-flight operation must be allowed to complete its durable transaction to disk.
            // Dispose/ShutdownCompletion must not report success while writer is alive.
            _writerThread.Join();
        }

        // Drain any remaining items just in case
        while (_channel.Reader.TryRead(out var remainingItem))
        {
            remainingItem.Tcs.TrySetResult(PipelineProbeResult.StorageBusyRetryable(
                "SERVER_SHUTTING_DOWN: Work item completed during coordinator shutdown."));
        }

        // 6. Only after writer thread has definitively exited:
        _isDisposed = true;
        _cts.Dispose();
    }
}
}
