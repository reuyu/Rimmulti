using System;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Storage;

namespace WarEconomy.Server.Pipeline.Coordinator
{
    public interface IPipelineTransactionCoordinator
    {
        PipelineProbeResult ExecuteProbeCas(PipelineProbeRequest request);
        FaultInjectionPoint ActiveFaultPoint { get; set; }
        Action<FaultInjectionPoint, PipelineProbeRequest>? FaultAction { get; set; }
    }

    public class SimulatedCrashException : Exception
    {
        public FaultInjectionPoint Point { get; }
        public SimulatedCrashException(FaultInjectionPoint point, string message) : base(message)
        {
            Point = point;
        }
    }

    public interface IPublicationOutboxDispatcher
    {
        bool DispatchEffect(PublicationOutboxEntry entry);
    }

    public class DefaultPublicationOutboxDispatcher : IPublicationOutboxDispatcher
    {
        public Action<PublicationOutboxEntry>? OnDispatched { get; set; }

        public bool DispatchEffect(PublicationOutboxEntry entry)
        {
            OnDispatched?.Invoke(entry);
            return true;
        }
    }

    public class PipelineTransactionCoordinator : IPipelineTransactionCoordinator
    {
        private readonly SqliteDatabaseContext _dbContext;
        private readonly IOperationJournal _journal;
        private readonly IProbeAggregateStore _probeStore;
        private readonly ICommitReceiptRepository _receipts;
        private readonly IAuditLogRepository _auditLogs;
        private readonly IPublicationOutboxStore _outboxStore;
        private readonly IPublicationOutboxDispatcher _outboxDispatcher;

        public FaultInjectionPoint ActiveFaultPoint { get; set; } = FaultInjectionPoint.None;
        public Action<FaultInjectionPoint, PipelineProbeRequest>? FaultAction { get; set; }

        public PipelineTransactionCoordinator(
            SqliteDatabaseContext dbContext,
            IOperationJournal? journal = null,
            IProbeAggregateStore? probeStore = null,
            ICommitReceiptRepository? receipts = null,
            IAuditLogRepository? auditLogs = null,
            IPublicationOutboxStore? outboxStore = null,
            IPublicationOutboxDispatcher? outboxDispatcher = null)
        {
            _dbContext = dbContext;
            _journal = journal ?? new OperationJournal();
            _probeStore = probeStore ?? new ProbeAggregateStore();
            _receipts = receipts ?? new CommitReceiptRepository();
            _auditLogs = auditLogs ?? new AuditLogRepository();
            _outboxStore = outboxStore ?? new PublicationOutboxStore();
            _outboxDispatcher = outboxDispatcher ?? new DefaultPublicationOutboxDispatcher();
        }

        public PipelineProbeResult ExecuteProbeCas(PipelineProbeRequest request)
        {
            // -----------------------------------------------------------------
            // STEP 1: Validate request and OperationId
            // -----------------------------------------------------------------
            if (string.IsNullOrWhiteSpace(request.OperationId))
                return PipelineProbeResult.Error("INVALID_REQUEST", "OperationId cannot be null or empty.");

            if (string.IsNullOrWhiteSpace(request.ProbeScopeId))
                return PipelineProbeResult.Error("INVALID_REQUEST", "ProbeScopeId cannot be null or empty.");

            if (request.ExpectedProbeRevision < 0)
                return PipelineProbeResult.Error("INVALID_REQUEST", "ExpectedProbeRevision cannot be negative.");

            string computedHash = request.ComputePayloadHash();

            using var conn = _dbContext.CreateOpenConnection();

            // -----------------------------------------------------------------
            // STEP 2: Idempotency & Collision Detection
            // -----------------------------------------------------------------
            var existingRecord = _journal.GetRecord(request.OperationId, conn);
            if (existingRecord != null)
            {
                // Check payload hash collision
                if (!string.Equals(existingRecord.PayloadHash, computedHash, StringComparison.OrdinalIgnoreCase))
                {
                    return PipelineProbeResult.CollisionRejected(request.OperationId,
                        $"PayloadHash mismatch: existing '{existingRecord.PayloadHash}' != requested '{computedHash}'");
                }

                // Return existing terminal or pending status
                if (existingRecord.State == OperationState.COMMITTED || existingRecord.State == OperationState.PUBLISHED)
                {
                    var existingReceipt = _receipts.GetReceiptByOperationId(request.OperationId, conn);
                    if (existingReceipt != null)
                    {
                        return PipelineProbeResult.Ok(existingReceipt, "ALREADY_COMMITTED");
                    }
                }
                else if (existingRecord.State == OperationState.PREPARED)
                {
                    return PipelineProbeResult.InProgressPrepared(request.OperationId);
                }
                else if (existingRecord.State == OperationState.ABORTED)
                {
                    return PipelineProbeResult.Aborted(request.OperationId, existingRecord.FailureReason);
                }
            }

            // -----------------------------------------------------------------
            // STEP 3: Verify ExpectedProbeRevision
            // -----------------------------------------------------------------
            long? currentRevision = _probeStore.GetRevision(request.ProbeScopeId, conn);
            long effectiveCurrent = currentRevision ?? 0L;

            if (effectiveCurrent != request.ExpectedProbeRevision)
            {
                return PipelineProbeResult.StaleRevisionRejected(request.ProbeScopeId, request.ExpectedProbeRevision, effectiveCurrent);
            }

            // -----------------------------------------------------------------
            // STEP 4: Create Durable PREPARED Reservation
            // -----------------------------------------------------------------
            DateTime nowUtc = DateTime.UtcNow;
            var preparedRecord = new OperationRecord
            {
                OperationId = request.OperationId,
                OperationType = "PIPELINE_PROBE_CAS",
                ProbeScopeId = request.ProbeScopeId,
                ExpectedProbeRevision = request.ExpectedProbeRevision,
                PayloadHash = computedHash,
                PayloadJson = request.PayloadJson,
                ContentProfileFingerprint = request.ContentProfileFingerprint,
                ActorId = request.ActorId,
                State = OperationState.PREPARED,
                CreatedAtUtc = nowUtc,
                UpdatedAtUtc = nowUtc
            };

            _journal.InsertPrepared(preparedRecord, conn);

            _auditLogs.InsertAudit(new AuditRecord
            {
                AuditId = Guid.NewGuid().ToString("N"),
                OperationId = request.OperationId,
                ProbeScopeId = request.ProbeScopeId,
                EventType = "PROBE_CAS_PREPARED",
                OldRevision = request.ExpectedProbeRevision,
                NewRevision = request.ExpectedProbeRevision + 1,
                ActorId = request.ActorId,
                DetailsJson = $"{{\"expectedRevision\":{request.ExpectedProbeRevision},\"payloadHash\":\"{computedHash}\"}}",
                TimestampUtc = nowUtc
            }, conn);

            // Fault Injection Point: AfterPrepared
            if (ActiveFaultPoint == FaultInjectionPoint.AfterPrepared)
            {
                FaultAction?.Invoke(FaultInjectionPoint.AfterPrepared, request);
                throw new SimulatedCrashException(FaultInjectionPoint.AfterPrepared, "Simulated crash immediately after PREPARED reservation written.");
            }

            // -----------------------------------------------------------------
            // STEP 5 & 6: Atomic DB Transaction Boundary
            // -----------------------------------------------------------------
            long newRevision = request.ExpectedProbeRevision + 1;
            string receiptId = Guid.NewGuid().ToString("N");
            string outboxId = Guid.NewGuid().ToString("N");
            DateTime committedAtUtc = DateTime.UtcNow;

            string receiptHash = CommitReceipt.ComputeReceiptHash(request.OperationId, request.ProbeScopeId, newRevision, committedAtUtc);

            var receipt = new CommitReceipt
            {
                ReceiptId = receiptId,
                OperationId = request.OperationId,
                ProbeScopeId = request.ProbeScopeId,
                CommittedRevision = newRevision,
                Status = "COMMITTED",
                ReceiptHash = receiptHash,
                CommittedAtUtc = committedAtUtc
            };

            var outboxEntry = new PublicationOutboxEntry
            {
                OutboxId = outboxId,
                OperationId = request.OperationId,
                ProbeScopeId = request.ProbeScopeId,
                EffectType = "PROBE_REVISION_ADVANCED",
                PayloadJson = $"{{\"scopeId\":\"{request.ProbeScopeId}\",\"committedRevision\":{newRevision},\"operationId\":\"{request.OperationId}\"}}",
                Status = "PENDING",
                CreatedAtUtc = committedAtUtc
            };

            using (var tx = conn.BeginTransaction())
            {
                // 1. Advance ProbeRevision atomically via CAS
                bool casSuccess = _probeStore.TryExecuteCas(request.ProbeScopeId, request.ExpectedProbeRevision, newRevision, request.OperationId, conn, tx);
                if (!casSuccess)
                {
                    tx.Rollback();

                    // Mark operation record as aborted due to CAS failure
                    _journal.UpdateState(request.OperationId, OperationState.ABORTED, "CAS failed: expected revision mismatch during atomic commit transaction.", conn);

                    long? postRevision = _probeStore.GetRevision(request.ProbeScopeId, conn);
                    return PipelineProbeResult.StaleRevisionRejected(request.ProbeScopeId, request.ExpectedProbeRevision, postRevision ?? 0L);
                }

                // 2. Advance OperationRecord to COMMITTED
                _journal.UpdateState(request.OperationId, OperationState.COMMITTED, null, conn, tx);

                // 3. Insert stable CommitReceipt
                _receipts.InsertReceipt(receipt, conn, tx);

                // 4. Insert AuditRecord
                _auditLogs.InsertAudit(new AuditRecord
                {
                    AuditId = Guid.NewGuid().ToString("N"),
                    OperationId = request.OperationId,
                    ProbeScopeId = request.ProbeScopeId,
                    EventType = "PROBE_CAS_COMMITTED",
                    OldRevision = request.ExpectedProbeRevision,
                    NewRevision = newRevision,
                    ActorId = request.ActorId,
                    DetailsJson = $"{{\"committedRevision\":{newRevision},\"receiptId\":\"{receiptId}\"}}",
                    TimestampUtc = committedAtUtc
                }, conn, tx);

                // 5. Insert durable Outbox entry in same DB transaction boundary
                _outboxStore.InsertOutboxEntry(outboxEntry, conn, tx);

                // Fault Injection Point: BeforeCommit
                if (ActiveFaultPoint == FaultInjectionPoint.BeforeCommit)
                {
                    FaultAction?.Invoke(FaultInjectionPoint.BeforeCommit, request);
                    tx.Rollback();
                    throw new SimulatedCrashException(FaultInjectionPoint.BeforeCommit, "Simulated crash immediately before atomic commit.");
                }

                // =========================================================================
                // >>> EXACT CANONICAL PROBE COMMIT POINT <<<
                // =========================================================================
                tx.Commit();
                // At this exact point, canonical state has irreversibly advanced.
                // =========================================================================
            }

            // Fault Injection Point: AfterCommitBeforeOutbox
            if (ActiveFaultPoint == FaultInjectionPoint.AfterCommitBeforeOutbox)
            {
                FaultAction?.Invoke(FaultInjectionPoint.AfterCommitBeforeOutbox, request);
                throw new SimulatedCrashException(FaultInjectionPoint.AfterCommitBeforeOutbox, "Simulated crash post-commit before outbox delivery.");
            }

            // -----------------------------------------------------------------
            // STEP 7: Publish/Deliver Derived Outbox Effect
            // -----------------------------------------------------------------
            bool outboxDelivered = false;
            try
            {
                if (ActiveFaultPoint == FaultInjectionPoint.DuringOutboxDelivery)
                {
                    FaultAction?.Invoke(FaultInjectionPoint.DuringOutboxDelivery, request);
                    throw new Exception("Simulated outbox transport error.");
                }

                outboxDelivered = _outboxDispatcher.DispatchEffect(outboxEntry);
            }
            catch (Exception ex)
            {
                _outboxStore.MarkFailed(outboxId, ex.Message, conn);
            }

            // -----------------------------------------------------------------
            // STEP 8: Mark Publication Completion
            // -----------------------------------------------------------------
            if (outboxDelivered)
            {
                _outboxStore.MarkDelivered(outboxId, conn);
                _journal.UpdateState(request.OperationId, OperationState.PUBLISHED, null, conn);
                receipt.Status = "PUBLISHED";
            }

            return PipelineProbeResult.Ok(receipt, receipt.Status);
        }
    }
}
