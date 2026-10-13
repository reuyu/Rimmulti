using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Storage;

namespace WarEconomy.Server.Pipeline.Recovery
{
    public class ReconciliationReport
    {
        public int PreparedFoundCount { get; set; }
        public int PreparedResumedAndCommittedCount { get; set; }
        public int PreparedAbortedCount { get; set; }
        public int OutboxPendingFoundCount { get; set; }
        public int OutboxDeliveredCount { get; set; }
        public int OutboxFailedCount { get; set; }
        public List<string> Details { get; set; } = new List<string>();
    }

    public interface IRecoveryReconciler
    {
        ReconciliationReport ReconcilePendingOperations();
    }

    public class RecoveryReconciler : IRecoveryReconciler
    {
        private readonly SqliteDatabaseContext _dbContext;
        private readonly IOperationJournal _journal;
        private readonly IProbeAggregateStore _probeStore;
        private readonly ICommitReceiptRepository _receipts;
        private readonly IAuditLogRepository _auditLogs;
        private readonly IPublicationOutboxStore _outboxStore;
        private readonly IPublicationOutboxDispatcher _outboxDispatcher;

        public RecoveryReconciler(
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

        public ReconciliationReport ReconcilePendingOperations()
        {
            var report = new ReconciliationReport();
            using var conn = _dbContext.CreateOpenConnection();

            // =========================================================================
            // PHASE 1: Reconcile PREPARED Records
            // Deterministic Rule for Autonomous Probe:
            // - If incomplete/invalid -> ABORT
            // - If complete and ExpectedProbeRevision still matches current -> RESUME COMMIT
            // - If ExpectedProbeRevision superseded -> ABORT
            // =========================================================================
            var preparedRecords = _journal.GetRecordsByState(OperationState.PREPARED, conn);
            report.PreparedFoundCount = preparedRecords.Count;

            foreach (var rec in preparedRecords)
            {
                // Incompleteness check
                if (string.IsNullOrWhiteSpace(rec.PayloadHash) || string.IsNullOrWhiteSpace(rec.ProbeScopeId))
                {
                    _journal.UpdateState(rec.OperationId, OperationState.ABORTED, "INCOMPLETE_PREPARED_RECORD", conn);
                    _auditLogs.InsertAudit(new AuditRecord
                    {
                        AuditId = Guid.NewGuid().ToString("N"),
                        OperationId = rec.OperationId,
                        ProbeScopeId = rec.ProbeScopeId,
                        EventType = "PROBE_RECOVERY_ABORTED",
                        OldRevision = rec.ExpectedProbeRevision,
                        NewRevision = null,
                        ActorId = "SYSTEM_RECOVERY_RECONCILER",
                        DetailsJson = "{\"reason\":\"Incomplete prepared record\"}",
                        TimestampUtc = DateTime.UtcNow
                    }, conn);

                    report.PreparedAbortedCount++;
                    report.Details.Add($"Prepared {rec.OperationId}: Aborted (incomplete payload).");
                    continue;
                }

                long? curRev = _probeStore.GetRevision(rec.ProbeScopeId, conn);
                long effectiveCurrent = curRev ?? 0L;

                if (effectiveCurrent == rec.ExpectedProbeRevision)
                {
                    // Revision is still current: resume autonomous probe commit
                    long newRevision = rec.ExpectedProbeRevision + 1;
                    string receiptId = Guid.NewGuid().ToString("N");
                    string outboxId = Guid.NewGuid().ToString("N");
                    DateTime committedAtUtc = DateTime.UtcNow;

                    string receiptHash = CommitReceipt.ComputeReceiptHash(rec.OperationId, rec.ProbeScopeId, newRevision, committedAtUtc);

                    var receipt = new CommitReceipt
                    {
                        ReceiptId = receiptId,
                        OperationId = rec.OperationId,
                        ProbeScopeId = rec.ProbeScopeId,
                        CommittedRevision = newRevision,
                        Status = "COMMITTED",
                        ReceiptHash = receiptHash,
                        CommittedAtUtc = committedAtUtc
                    };

                    var outboxEntry = new PublicationOutboxEntry
                    {
                        OutboxId = outboxId,
                        OperationId = rec.OperationId,
                        ProbeScopeId = rec.ProbeScopeId,
                        EffectType = "PROBE_REVISION_ADVANCED",
                        PayloadJson = $"{{\"scopeId\":\"{rec.ProbeScopeId}\",\"committedRevision\":{newRevision},\"operationId\":\"{rec.OperationId}\"}}",
                        Status = "PENDING",
                        CreatedAtUtc = committedAtUtc
                    };

                    using (var tx = conn.BeginTransaction())
                    {
                        bool casOk = _probeStore.TryExecuteCas(rec.ProbeScopeId, rec.ExpectedProbeRevision, newRevision, rec.OperationId, conn, tx);
                        if (!casOk)
                        {
                            tx.Rollback();
                            _journal.UpdateState(rec.OperationId, OperationState.ABORTED, "REVISION_SUPERSEDED_DURING_RECOVERY_CAS", conn);
                            report.PreparedAbortedCount++;
                            report.Details.Add($"Prepared {rec.OperationId}: Aborted (CAS race during recovery).");
                            continue;
                        }

                        _journal.UpdateState(rec.OperationId, OperationState.COMMITTED, null, conn, tx);
                        _receipts.InsertReceipt(receipt, conn, tx);
                        _auditLogs.InsertAudit(new AuditRecord
                        {
                            AuditId = Guid.NewGuid().ToString("N"),
                            OperationId = rec.OperationId,
                            ProbeScopeId = rec.ProbeScopeId,
                            EventType = "PROBE_RECOVERY_COMMITTED",
                            OldRevision = rec.ExpectedProbeRevision,
                            NewRevision = newRevision,
                            ActorId = "SYSTEM_RECOVERY_RECONCILER",
                            DetailsJson = $"{{\"committedRevision\":{newRevision},\"recovered\":true}}",
                            TimestampUtc = committedAtUtc
                        }, conn, tx);

                        _outboxStore.InsertOutboxEntry(outboxEntry, conn, tx);
                        tx.Commit();
                    }

                    report.PreparedResumedAndCommittedCount++;
                    report.Details.Add($"Prepared {rec.OperationId}: Resumed and committed to revision {newRevision}.");
                }
                else
                {
                    // Expected revision was superseded by another commit
                    _journal.UpdateState(rec.OperationId, OperationState.ABORTED, $"REVISION_SUPERSEDED: Expected {rec.ExpectedProbeRevision} != Current {effectiveCurrent}", conn);
                    _auditLogs.InsertAudit(new AuditRecord
                    {
                        AuditId = Guid.NewGuid().ToString("N"),
                        OperationId = rec.OperationId,
                        ProbeScopeId = rec.ProbeScopeId,
                        EventType = "PROBE_RECOVERY_ABORTED",
                        OldRevision = rec.ExpectedProbeRevision,
                        NewRevision = effectiveCurrent,
                        ActorId = "SYSTEM_RECOVERY_RECONCILER",
                        DetailsJson = $"{{\"reason\":\"Revision superseded\",\"currentRevision\":{effectiveCurrent}}}",
                        TimestampUtc = DateTime.UtcNow
                    }, conn);

                    report.PreparedAbortedCount++;
                    report.Details.Add($"Prepared {rec.OperationId}: Aborted (expected revision {rec.ExpectedProbeRevision} != current {effectiveCurrent}).");
                }
            }

            // =========================================================================
            // PHASE 2: Reconcile Pending Outbox Entries (At-Least-Once Delivery Replay)
            // CRITICAL: Replays delivery without advancing or re-committing ProbeRevision!
            // =========================================================================
            var pendingOutbox = _outboxStore.GetPendingEntries(conn);
            report.OutboxPendingFoundCount = pendingOutbox.Count;

            foreach (var outbox in pendingOutbox)
            {
                bool delivered = false;
                try
                {
                    delivered = _outboxDispatcher.DispatchEffect(outbox);
                }
                catch (Exception ex)
                {
                    _outboxStore.MarkFailed(outbox.OutboxId, ex.Message, conn);
                    report.OutboxFailedCount++;
                    report.Details.Add($"Outbox {outbox.OutboxId}: Dispatch failed ({ex.Message}).");
                }

                if (delivered)
                {
                    _outboxStore.MarkDelivered(outbox.OutboxId, conn);
                    _journal.UpdateState(outbox.OperationId, OperationState.PUBLISHED, null, conn);
                    report.OutboxDeliveredCount++;
                    report.Details.Add($"Outbox {outbox.OutboxId}: Replayed and marked DELIVERED (ProbeRevision preserved).");
                }
            }

            return report;
        }
    }
}
