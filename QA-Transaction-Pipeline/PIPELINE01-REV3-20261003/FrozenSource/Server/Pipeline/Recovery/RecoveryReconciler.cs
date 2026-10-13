using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Server.Pipeline.Recovery
{
    public class ReconciliationReport
    {
        public bool Success { get; set; }
        public string ActiveStoreIncarnationId { get; set; } = string.Empty;
        public int CommittedOperationsChecked { get; set; }
        public int PublicationEventsChecked { get; set; }
        public List<string> Details { get; set; } = new List<string>();
    }

    public interface IRecoveryReconciler
    {
        ReconciliationReport ReconcileAndVerify();
    }

    public class RecoveryReconciler : IRecoveryReconciler
    {
        private readonly SqliteDatabaseContext _dbContext;

        public RecoveryReconciler(SqliteDatabaseContext dbContext)
        {
            _dbContext = dbContext ?? throw new ArgumentNullException(nameof(dbContext));
        }

        public ReconciliationReport ReconcileAndVerify()
        {
            var report = new ReconciliationReport();

            try
            {
                // 1. Validate DB readiness, WAL/FULL, recursive_triggers, schema structure, and active incarnation
                _dbContext.ValidateReadiness();
                report.ActiveStoreIncarnationId = _dbContext.GetActiveStoreIncarnationId();
                report.Details.Add($"Active StoreIncarnation: {report.ActiveStoreIncarnationId}");

                // 2. Canonical Cross-Table Consistency Audit
                using var conn = _dbContext.CreateOpenConnection();

                // Check 2a: Every COMMITTED operation has a corresponding CommitReceipt
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM OperationRecords o
                        LEFT JOIN CommitReceipts r ON o.PrincipalId = r.PrincipalId AND o.OperationId = r.OperationId
                        WHERE o.State = 'COMMITTED' AND r.ReceiptId IS NULL;
                    ";
                    long missingReceipts = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (missingReceipts > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {missingReceipts} COMMITTED operation(s) missing CommitReceipt.");
                    }
                }

                // Check 2b: Every COMMITTED operation has a corresponding PublicationEvent
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM OperationRecords o
                        LEFT JOIN PublicationEvents e ON o.PrincipalId = e.PrincipalId AND o.OperationId = e.OperationId
                        WHERE o.State = 'COMMITTED' AND e.EventId IS NULL;
                    ";
                    long missingEvents = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (missingEvents > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {missingEvents} COMMITTED operation(s) missing PublicationEvent.");
                    }
                }

                // Check 2c: Every COMMITTED operation has matching ProbeRevisionHistory and AuditRecords
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM OperationRecords o
                        LEFT JOIN ProbeRevisionHistory h ON o.ProbeScopeId = h.ProbeScopeId AND o.OperationId = h.OperationId
                        WHERE o.State = 'COMMITTED' AND h.ProbeRevision IS NULL;
                    ";
                    long missingHistory = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (missingHistory > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {missingHistory} COMMITTED operation(s) missing ProbeRevisionHistory.");
                    }

                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM OperationRecords o
                        LEFT JOIN AuditRecords a ON o.PrincipalId = a.PrincipalId AND o.OperationId = a.OperationId AND a.EventType = 'PROBE_CAS_COMMITTED'
                        WHERE o.State = 'COMMITTED' AND a.AuditId IS NULL;
                    ";
                    long missingAudits = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (missingAudits > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {missingAudits} COMMITTED operation(s) missing AuditRecord.");
                    }
                }

                // Check 2d: ABORTED operation with success receipt or event
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM OperationRecords o
                        JOIN CommitReceipts r ON o.PrincipalId = r.PrincipalId AND o.OperationId = r.OperationId
                        WHERE o.State = 'ABORTED';
                    ";
                    long abortedWithReceipt = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (abortedWithReceipt > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {abortedWithReceipt} ABORTED operation(s) with CommitReceipt.");
                    }

                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM OperationRecords o
                        JOIN PublicationEvents e ON o.PrincipalId = e.PrincipalId AND o.OperationId = e.OperationId
                        WHERE o.State = 'ABORTED';
                    ";
                    long abortedWithEvent = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (abortedWithEvent > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {abortedWithEvent} ABORTED operation(s) with PublicationEvent.");
                    }
                }

                // Check 2e: Orphan receipts or events pointing at nonexistent/non-committed operations
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM CommitReceipts r
                        LEFT JOIN OperationRecords o ON r.PrincipalId = o.PrincipalId AND r.OperationId = o.OperationId
                        WHERE o.OperationId IS NULL OR o.State != 'COMMITTED';
                    ";
                    long orphanReceipts = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (orphanReceipts > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {orphanReceipts} orphan CommitReceipt(s).");
                    }

                    cmd.CommandText = @"
                        SELECT COUNT(*)
                        FROM PublicationEvents e
                        LEFT JOIN OperationRecords o ON e.PrincipalId = o.PrincipalId AND e.OperationId = o.OperationId
                        WHERE o.OperationId IS NULL OR o.State != 'COMMITTED';
                    ";
                    long orphanEvents = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                    if (orphanEvents > 0)
                    {
                        throw new InvalidOperationException($"Consistency error: found {orphanEvents} orphan PublicationEvent(s).");
                    }
                }

                // Check 2f: Receipt hash and revision verification
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT r.ReceiptId, r.PrincipalId, r.OperationId, r.ProbeScopeId, r.CommittedRevision,
                               r.StoreIncarnationId, r.CommittedAtEpochMs, r.ReceiptHash, h.ProbeRevision
                        FROM CommitReceipts r
                        JOIN ProbeRevisionHistory h ON r.ProbeScopeId = h.ProbeScopeId AND r.OperationId = h.OperationId;
                    ";
                    using var reader = cmd.ExecuteReader();
                    while (reader.Read())
                    {
                        string rId = reader.GetString(0);
                        string pId = reader.GetString(1);
                        string opId = reader.GetString(2);
                        string scope = reader.GetString(3);
                        long rev = reader.GetInt64(4);
                        string inc = reader.GetString(5);
                        long epoch = reader.GetInt64(6);
                        string hash = reader.GetString(7);
                        long histRev = reader.GetInt64(8);

                        if (rev != histRev)
                        {
                            throw new InvalidOperationException($"Consistency error: receipt '{rId}' revision {rev} does not match history revision {histRev}.");
                        }

                        string expectedHash = CommitReceipt.ComputeReceiptHash(rId, pId, opId, scope, rev, inc, epoch);
                        if (!string.Equals(hash, expectedHash, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException($"Consistency error: receipt '{rId}' hash mismatch. Stored '{hash}', computed '{expectedHash}'.");
                        }
                    }
                }

                // Check 2g: PublicationEvents payload and fingerprint verification
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT e.EventId, e.CanonicalPayload, e.PayloadFingerprint, o.RequestFingerprint, o.PayloadJson
                        FROM PublicationEvents e
                        JOIN OperationRecords o ON e.PrincipalId = o.PrincipalId AND e.OperationId = o.OperationId;
                    ";
                    using var reader = cmd.ExecuteReader();
                    while (reader.Read())
                    {
                        string evtId = reader.GetString(0);
                        string canonicalPayload = reader.GetString(1);
                        string storedFp = reader.GetString(2);
                        string opRawPayload = reader.GetString(4);

                        string expectedPayloadFp = PublicationEvent.ComputePayloadFingerprint(canonicalPayload);
                        if (!string.Equals(storedFp, expectedPayloadFp, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException($"Consistency error: event '{evtId}' payload fingerprint mismatch.");
                        }

                        string expectedFromRaw = PublicationEvent.ComputePayloadFingerprint(opRawPayload);
                        if (!string.Equals(storedFp, expectedFromRaw, StringComparison.Ordinal))
                        {
                            throw new InvalidOperationException($"Consistency error: event '{evtId}' payload contradicts OperationRecords payload.");
                        }
                    }
                }

                // Check 2h: ProbeAggregates revision equals MAX(ProbeRevision) in history
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        SELECT p.ProbeScopeId, p.ProbeRevision, COALESCE(MAX(h.ProbeRevision), 0)
                        FROM ProbeAggregates p
                        LEFT JOIN ProbeRevisionHistory h ON p.ProbeScopeId = h.ProbeScopeId
                        GROUP BY p.ProbeScopeId;
                    ";
                    using var reader = cmd.ExecuteReader();
                    while (reader.Read())
                    {
                        string scope = reader.GetString(0);
                        long aggRev = reader.GetInt64(1);
                        long maxHistRev = reader.GetInt64(2);

                        if (aggRev != maxHistRev)
                        {
                            throw new InvalidOperationException($"Consistency error: aggregate scope '{scope}' revision {aggRev} contradicts history max revision {maxHistRev}.");
                        }
                    }
                }

                // Count totals
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords WHERE State = 'COMMITTED';";
                    report.CommittedOperationsChecked = Convert.ToInt32(cmd.ExecuteScalar() ?? 0);

                    cmd.CommandText = "SELECT COUNT(*) FROM PublicationEvents;";
                    report.PublicationEventsChecked = Convert.ToInt32(cmd.ExecuteScalar() ?? 0);
                }

                report.Details.Add($"Consistency verified: {report.CommittedOperationsChecked} committed operation(s), {report.PublicationEventsChecked} publication event(s).");
                report.Success = true;
            }
            catch (Exception ex)
            {
                report.Success = false;
                report.Details.Add($"Readiness verification failure: {ex.Message}");
            }

            return report;
        }
    }

    public static class PipelineStartupManager
    {
        public static bool IsPipelineReady { get; private set; } = false;
        public static string ActiveStoreIncarnationId { get; private set; } = string.Empty;
        public static PipelineTransactionCoordinator? ActiveCoordinator { get; private set; }

        public static void InitializeAndVerifyPipeline(SqliteDatabaseContext dbContext)
        {
            IsPipelineReady = false;

            // 1. Open/validate canonical DB & apply migrations
            dbContext.InitializeDatabase();

            // 2. Validate readiness & run consistency audit
            var reconciler = new RecoveryReconciler(dbContext);
            var report = reconciler.ReconcileAndVerify();

            if (!report.Success)
            {
                throw new InvalidOperationException($"Pipeline startup verification failed: {string.Join("; ", report.Details)}");
            }

            ActiveStoreIncarnationId = report.ActiveStoreIncarnationId;

            // 3. Create/start the actual service-lifetime Pipeline coordinator/writer
            ActiveCoordinator = new PipelineTransactionCoordinator(dbContext);

            // 4. Reach explicit PIPELINE_READY
            IsPipelineReady = true;
            Console.WriteLine($"[Pipeline] PIPELINE_READY reached. Dedicated writer active. Active StoreIncarnation: {ActiveStoreIncarnationId}");
        }

        public static void ResetReadinessForTesting()
        {
            IsPipelineReady = false;
            ActiveStoreIncarnationId = string.Empty;
            ActiveCoordinator?.Dispose();
            ActiveCoordinator = null;
        }
    }
}
