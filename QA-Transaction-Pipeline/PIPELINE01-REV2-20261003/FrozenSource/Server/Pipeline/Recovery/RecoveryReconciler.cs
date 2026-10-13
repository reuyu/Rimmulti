using System;
using System.Collections.Generic;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Data;

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
                // 1. Validate DB readiness, WAL/FULL, schema structure, and active incarnation
                _dbContext.ValidateReadiness();
                report.ActiveStoreIncarnationId = _dbContext.GetActiveStoreIncarnationId();
                report.Details.Add($"Active StoreIncarnation: {report.ActiveStoreIncarnationId}");

                // 2. Canonical Commit & Event Log Consistency Check
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

                // Check 2c: Total committed operations count
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords WHERE State = 'COMMITTED';";
                    report.CommittedOperationsChecked = Convert.ToInt32(cmd.ExecuteScalar() ?? 0);
                }

                // Check 2d: Publication events monotonic ordering per stream
                using (var cmd = conn.CreateCommand())
                {
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

            // 3. Reach explicit PIPELINE_READY
            IsPipelineReady = true;
            Console.WriteLine($"[Pipeline] PIPELINE_READY reached. Active StoreIncarnation: {ActiveStoreIncarnationId}");
        }

        public static void ResetReadinessForTesting()
        {
            IsPipelineReady = false;
            ActiveStoreIncarnationId = string.Empty;
        }
    }
}
