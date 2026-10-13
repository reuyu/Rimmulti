using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Recovery;
using WarEconomy.Server.Pipeline.Security;
using WarEconomy.Server.Pipeline.Storage;

namespace WarEconomy.Server.Pipeline.Testing
{
    public class TestAssertionResult
    {
        public string TestId { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public bool Passed { get; set; }
        public double DurationMs { get; set; }
        public string Details { get; set; } = string.Empty;
    }

    public class PipelineE1BatteryReport
    {
        public bool OverallSuccess { get; set; }
        public string DatabasePath { get; set; } = string.Empty;
        public string JournalMode { get; set; } = string.Empty;
        public string SynchronousMode { get; set; } = string.Empty;
        public int SchemaVersion { get; set; }
        public string IntegrityCheck { get; set; } = string.Empty;
        public List<TestAssertionResult> Tests { get; set; } = new List<TestAssertionResult>();
        public DateTime TimestampUtc { get; set; } = DateTime.UtcNow;
    }

    public class PipelineE1TestBattery
    {
        private readonly string _testDbPath;
        private readonly SqliteDatabaseContext _dbContext;
        private readonly IOperationJournal _journal;
        private readonly IProbeAggregateStore _probeStore;
        private readonly ICommitReceiptRepository _receipts;
        private readonly IAuditLogRepository _auditLogs;
        private readonly IPublicationOutboxStore _outboxStore;
        private readonly DefaultPublicationOutboxDispatcher _outboxDispatcher;
        private readonly PipelineTransactionCoordinator _coordinator;
        private readonly RecoveryReconciler _reconciler;
        private readonly InternalProbeTestSurface _testSurface;

        public PipelineE1TestBattery(string? testDbPath = null)
        {
            if (string.IsNullOrEmpty(testDbPath))
            {
                _testDbPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "test_pipeline_e1.db");
                if (File.Exists(_testDbPath))
                {
                    File.Delete(_testDbPath);
                }
            }
            else
            {
                _testDbPath = testDbPath;
            }

            _dbContext = new SqliteDatabaseContext(_testDbPath);
            _dbContext.InitializeDatabase();

            _journal = new OperationJournal();
            _probeStore = new ProbeAggregateStore();
            _receipts = new CommitReceiptRepository();
            _auditLogs = new AuditLogRepository();
            _outboxStore = new PublicationOutboxStore();
            _outboxDispatcher = new DefaultPublicationOutboxDispatcher();

            _coordinator = new PipelineTransactionCoordinator(
                _dbContext, _journal, _probeStore, _receipts, _auditLogs, _outboxStore, _outboxDispatcher);

            _reconciler = new RecoveryReconciler(
                _dbContext, _journal, _probeStore, _receipts, _auditLogs, _outboxStore, _outboxDispatcher);

            _testSurface = new InternalProbeTestSurface(_coordinator);
        }

        public async Task<PipelineE1BatteryReport> RunAllTestsAsync()
        {
            var report = new PipelineE1BatteryReport
            {
                DatabasePath = _testDbPath,
                JournalMode = _dbContext.GetJournalMode(),
                SynchronousMode = _dbContext.GetSynchronousMode(),
                SchemaVersion = _dbContext.GetUserVersion(),
                IntegrityCheck = _dbContext.RunIntegrityCheck()
            };

            Console.WriteLine("==================================================================");
            Console.WriteLine("  WP-PROD-TRANSACTION-PIPELINE-01: E1 Developer Test Battery");
            Console.WriteLine("==================================================================");
            Console.WriteLine($"Database Path:    {report.DatabasePath}");
            Console.WriteLine($"Journal Mode:     {report.JournalMode}");
            Console.WriteLine($"Synchronous Mode: {report.SynchronousMode}");
            Console.WriteLine($"Schema Version:   {report.SchemaVersion}");
            Console.WriteLine($"Integrity Check:  {report.IntegrityCheck}");
            Console.WriteLine("------------------------------------------------------------------\n");

            // Test 1: Normal commit advances ProbeRevision once
            report.Tests.Add(RunTest("E1_01_NORMAL_COMMIT_ADVANCES_REVISION", "1. Normal commit advances ProbeRevision once", () =>
            {
                var req = new PipelineProbeRequest
                {
                    OperationId = "OP_NORMAL_01",
                    ProbeScopeId = "SCOPE_NORMAL_01",
                    ExpectedProbeRevision = 0,
                    PayloadJson = "{\"testKey\":\"initialValue\"}",
                    ActorId = "TEST_HARNESS_ACTOR"
                };

                var res = _coordinator.ExecuteProbeCas(req);
                using var conn = _dbContext.CreateOpenConnection();
                long? rev = _probeStore.GetRevision("SCOPE_NORMAL_01", conn);
                var opRec = _journal.GetRecord("OP_NORMAL_01", conn);
                var receipt = _receipts.GetReceiptByOperationId("OP_NORMAL_01", conn);
                var outbox = _outboxStore.GetEntryByOperationId("OP_NORMAL_01", conn);

                bool pass = res.Success &&
                            res.Receipt?.CommittedRevision == 1 &&
                            rev == 1 &&
                            opRec?.State == OperationState.PUBLISHED &&
                            receipt?.CommittedRevision == 1 &&
                            outbox?.Status == "DELIVERED";

                return (pass, $"Success={res.Success}, CommittedRev={res.Receipt?.CommittedRevision}, DBRev={rev}, OpState={opRec?.State}, OutboxStatus={outbox?.Status}");
            }));

            // Test 2: Same OperationId + same payload retry returns stable receipt
            report.Tests.Add(RunTest("E1_02_SAME_ID_SAME_PAYLOAD_IDEMPOTENT_RECEIPT", "2. Same OperationId + same payload retry returns stable receipt", () =>
            {
                var req = new PipelineProbeRequest
                {
                    OperationId = "OP_NORMAL_01",
                    ProbeScopeId = "SCOPE_NORMAL_01",
                    ExpectedProbeRevision = 0, // Even if caller passes 0, it recognizes existing committed operation
                    PayloadJson = "{\"testKey\":\"initialValue\"}",
                    ActorId = "TEST_HARNESS_ACTOR"
                };

                var res = _coordinator.ExecuteProbeCas(req);
                using var conn = _dbContext.CreateOpenConnection();
                long? rev = _probeStore.GetRevision("SCOPE_NORMAL_01", conn);

                bool pass = res.Success &&
                            res.Status == "ALREADY_COMMITTED" &&
                            res.Receipt?.CommittedRevision == 1 &&
                            rev == 1; // Revision MUST NOT advance to 2

                return (pass, $"Success={res.Success}, Status={res.Status}, CommittedRev={res.Receipt?.CommittedRevision}, DBRev={rev} (did not advance: {rev == 1})");
            }));

            // Test 3: Same OperationId + different payload rejects (Collision)
            report.Tests.Add(RunTest("E1_03_SAME_ID_DIFFERENT_PAYLOAD_COLLISION", "3. Same OperationId + different payload rejects (Collision)", () =>
            {
                var req = new PipelineProbeRequest
                {
                    OperationId = "OP_NORMAL_01",
                    ProbeScopeId = "SCOPE_NORMAL_01",
                    ExpectedProbeRevision = 1,
                    PayloadJson = "{\"tamperedKey\":\"tamperedPayload\"}",
                    ActorId = "ATTACKER_ACTOR"
                };

                var res = _coordinator.ExecuteProbeCas(req);
                using var conn = _dbContext.CreateOpenConnection();
                long? rev = _probeStore.GetRevision("SCOPE_NORMAL_01", conn);

                bool pass = (!res.Success) &&
                            res.Collision &&
                            res.Status == "COLLISION_REJECTED" &&
                            rev == 1;

                return (pass, $"Success={res.Success}, Collision={res.Collision}, Status={res.Status}, Message='{res.Message}'");
            }));

            // Test 4: Stale ExpectedProbeRevision rejects
            report.Tests.Add(RunTest("E1_04_STALE_EXPECTED_REVISION_REJECTED", "4. Stale ExpectedProbeRevision rejects", () =>
            {
                var req = new PipelineProbeRequest
                {
                    OperationId = "OP_STALE_01",
                    ProbeScopeId = "SCOPE_STALE_01",
                    ExpectedProbeRevision = 99, // Stale! Actual is 0
                    PayloadJson = "{\"foo\":\"bar\"}",
                    ActorId = "TEST_HARNESS_ACTOR"
                };

                var res = _coordinator.ExecuteProbeCas(req);
                using var conn = _dbContext.CreateOpenConnection();
                long? rev = _probeStore.GetRevision("SCOPE_STALE_01", conn);

                bool pass = (!res.Success) &&
                            res.StaleRevision &&
                            res.Status == "STALE_REVISION_REJECTED" &&
                            (rev == null || rev == 0);

                return (pass, $"Success={res.Success}, StaleRevision={res.StaleRevision}, Status={res.Status}, Expected=99, Actual={res.CurrentRevision}");
            }));

            // Test 5: 20+ concurrent operations against one expected revision -> exactly one winner
            report.Tests.Add(await RunTestAsync("E1_05_CONCURRENT_RACE_EXACTLY_ONE_WINNER", "5. 20+ concurrent operations against one expected revision -> exactly one winner", async () =>
            {
                const string scopeId = "SCOPE_CONCURRENT_RACE_01";
                const int taskCount = 25;

                var tasks = new List<Task<PipelineProbeResult>>();
                var barrier = new TaskCompletionSource<bool>();

                for (int i = 0; i < taskCount; i++)
                {
                    int index = i;
                    tasks.Add(Task.Run(async () =>
                    {
                        await barrier.Task;
                        var coord = new PipelineTransactionCoordinator(_dbContext);
                        return coord.ExecuteProbeCas(new PipelineProbeRequest
                        {
                            OperationId = $"OP_RACE_{index:D2}_{Guid.NewGuid():N}",
                            ProbeScopeId = scopeId,
                            ExpectedProbeRevision = 0,
                            PayloadJson = $"{{\"taskIndex\":{index}}}",
                            ActorId = $"CONCURRENT_WORKER_{index}"
                        });
                    }));
                }

                // Unleash all 25 tasks concurrently
                barrier.SetResult(true);
                var results = await Task.WhenAll(tasks);

                int successCount = results.Count(r => r.Success);
                int staleCount = results.Count(r => r.StaleRevision);

                using var conn = _dbContext.CreateOpenConnection();
                long? finalRev = _probeStore.GetRevision(scopeId, conn);

                bool pass = successCount == 1 &&
                            staleCount == (taskCount - 1) &&
                            finalRev == 1;

                return (pass, $"TotalTasks={taskCount}, Winners={successCount}, StaleRejections={staleCount}, FinalDBRevision={finalRev} (Pass: Exactly 1 winner)");
            }));

            // Test 6: Two independent ProbeScopeIds can commit independently
            report.Tests.Add(RunTest("E1_06_INDEPENDENT_SCOPES_COMMIT_INDEPENDENTLY", "6. Two independent ProbeScopeIds can commit independently", () =>
            {
                var reqA = new PipelineProbeRequest
                {
                    OperationId = "OP_INDEP_A_01",
                    ProbeScopeId = "SCOPE_INDEP_A",
                    ExpectedProbeRevision = 0,
                    PayloadJson = "{\"scope\":\"A\"}",
                    ActorId = "ACTOR_A"
                };

                var reqB = new PipelineProbeRequest
                {
                    OperationId = "OP_INDEP_B_01",
                    ProbeScopeId = "SCOPE_INDEP_B",
                    ExpectedProbeRevision = 0,
                    PayloadJson = "{\"scope\":\"B\"}",
                    ActorId = "ACTOR_B"
                };

                var resA = _coordinator.ExecuteProbeCas(reqA);
                var resB = _coordinator.ExecuteProbeCas(reqB);

                using var conn = _dbContext.CreateOpenConnection();
                long? revA = _probeStore.GetRevision("SCOPE_INDEP_A", conn);
                long? revB = _probeStore.GetRevision("SCOPE_INDEP_B", conn);

                bool pass = resA.Success && resB.Success &&
                            revA == 1 && revB == 1;

                return (pass, $"ScopeA: Success={resA.Success}, Rev={revA} | ScopeB: Success={resB.Success}, Rev={revB}");
            }));

            // Test 7: Crash/process termination after PREPARED
            report.Tests.Add(RunTest("E1_07_CRASH_AFTER_PREPARED_RECONCILED", "7. Crash/process termination after PREPARED; reconciler restores deterministic state", () =>
            {
                const string opId = "OP_CRASH_PREPARED_01";
                const string scopeId = "SCOPE_CRASH_01";

                _coordinator.ActiveFaultPoint = FaultInjectionPoint.AfterPrepared;
                bool crashed = false;

                try
                {
                    _coordinator.ExecuteProbeCas(new PipelineProbeRequest
                    {
                        OperationId = opId,
                        ProbeScopeId = scopeId,
                        ExpectedProbeRevision = 0,
                        PayloadJson = "{\"crashPoint\":\"AfterPrepared\"}",
                        ActorId = "CRASH_TEST_ACTOR"
                    });
                }
                catch (SimulatedCrashException)
                {
                    crashed = true;
                    _coordinator.ActiveFaultPoint = FaultInjectionPoint.None;
                }

                // Verify pre-recovery state: PREPARED in DB, but DB revision still uncommitted (0)
                using var connPre = _dbContext.CreateOpenConnection();
                var opPre = _journal.GetRecord(opId, connPre);
                long? revPre = _probeStore.GetRevision(scopeId, connPre);
                var receiptPre = _receipts.GetReceiptByOperationId(opId, connPre);

                bool preCrashVerified = crashed &&
                                        opPre?.State == OperationState.PREPARED &&
                                        (revPre == null || revPre == 0) &&
                                        receiptPre == null;

                // Run recovery reconciler (simulates restart)
                var recoveryReport = _reconciler.ReconcilePendingOperations();

                // Verify post-recovery state: Autonomous probe resumed and committed cleanly
                using var connPost = _dbContext.CreateOpenConnection();
                var opPost = _journal.GetRecord(opId, connPost);
                long? revPost = _probeStore.GetRevision(scopeId, connPost);
                var receiptPost = _receipts.GetReceiptByOperationId(opId, connPost);

                bool pass = preCrashVerified &&
                            recoveryReport.PreparedResumedAndCommittedCount == 1 &&
                            opPost?.State == OperationState.PUBLISHED &&
                            revPost == 1 &&
                            receiptPost?.CommittedRevision == 1;

                return (pass, $"CrashedAtPrepared={crashed}, PreRecoveryState={opPre?.State}, PreRev={revPre}, RecoveredCount={recoveryReport.PreparedResumedAndCommittedCount}, PostRev={revPost}, PostState={opPost?.State}");
            }));

            // Test 8: Crash immediately before COMMIT boundary (BeforeCommit)
            report.Tests.Add(RunTest("E1_08_CRASH_BEFORE_COMMIT_ROLLED_BACK", "8. Crash immediately before COMMIT boundary; transaction rolled back", () =>
            {
                const string opId = "OP_CRASH_BEFORE_COMMIT_01";
                const string scopeId = "SCOPE_CRASH_02";

                _coordinator.ActiveFaultPoint = FaultInjectionPoint.BeforeCommit;
                bool crashed = false;

                try
                {
                    _coordinator.ExecuteProbeCas(new PipelineProbeRequest
                    {
                        OperationId = opId,
                        ProbeScopeId = scopeId,
                        ExpectedProbeRevision = 0,
                        PayloadJson = "{\"crashPoint\":\"BeforeCommit\"}",
                        ActorId = "CRASH_TEST_ACTOR"
                    });
                }
                catch (SimulatedCrashException)
                {
                    crashed = true;
                    _coordinator.ActiveFaultPoint = FaultInjectionPoint.None;
                }

                // Verify rolled-back state
                using var conn = _dbContext.CreateOpenConnection();
                long? rev = _probeStore.GetRevision(scopeId, conn);
                bool hasHistory = _probeStore.HasCommittedRevision(scopeId, 1, conn);
                var receipt = _receipts.GetReceiptByOperationId(opId, conn);

                bool pass = crashed &&
                            (rev == null || rev == 0) &&
                            !hasHistory &&
                            receipt == null;

                return (pass, $"CrashedBeforeCommit={crashed}, DBRevisionAfterRollback={rev ?? 0}, HasHistory={hasHistory}, ReceiptExists={receipt != null}");
            }));

            // Test 9: Crash after COMMITTED before outbox delivery
            report.Tests.Add(RunTest("E1_09_CRASH_AFTER_COMMIT_BEFORE_OUTBOX", "9. Crash after COMMITTED before outbox delivery", () =>
            {
                const string opId = "OP_CRASH_AFTER_COMMIT_01";
                const string scopeId = "SCOPE_CRASH_03";

                _coordinator.ActiveFaultPoint = FaultInjectionPoint.AfterCommitBeforeOutbox;
                bool crashed = false;

                try
                {
                    _coordinator.ExecuteProbeCas(new PipelineProbeRequest
                    {
                        OperationId = opId,
                        ProbeScopeId = scopeId,
                        ExpectedProbeRevision = 0,
                        PayloadJson = "{\"crashPoint\":\"AfterCommitBeforeOutbox\"}",
                        ActorId = "CRASH_TEST_ACTOR"
                    });
                }
                catch (SimulatedCrashException)
                {
                    crashed = true;
                    _coordinator.ActiveFaultPoint = FaultInjectionPoint.None;
                }

                // Verify state: DB revision IS COMMITTED, but Outbox is PENDING and OpState is COMMITTED
                using var conn = _dbContext.CreateOpenConnection();
                var op = _journal.GetRecord(opId, conn);
                long? rev = _probeStore.GetRevision(scopeId, conn);
                var receipt = _receipts.GetReceiptByOperationId(opId, conn);
                var outbox = _outboxStore.GetEntryByOperationId(opId, conn);

                bool pass = crashed &&
                            op?.State == OperationState.COMMITTED &&
                            rev == 1 &&
                            receipt?.CommittedRevision == 1 &&
                            outbox?.Status == "PENDING";

                return (pass, $"CrashedPostCommit={crashed}, OpState={op?.State}, CommittedRev={rev}, OutboxStatus={outbox?.Status}");
            }));

            // Test 10: Restart reconciler restores deterministic status
            report.Tests.Add(RunTest("E1_10_RESTART_RECONCILER_DELIVERS_OUTBOX", "10. Restart reconciler restores deterministic status by replaying outbox", () =>
            {
                const string opId = "OP_CRASH_AFTER_COMMIT_01";
                const string scopeId = "SCOPE_CRASH_03";

                var recoveryReport = _reconciler.ReconcilePendingOperations();

                using var conn = _dbContext.CreateOpenConnection();
                var op = _journal.GetRecord(opId, conn);
                long? rev = _probeStore.GetRevision(scopeId, conn);
                var outbox = _outboxStore.GetEntryByOperationId(opId, conn);

                bool pass = recoveryReport.OutboxDeliveredCount >= 1 &&
                            op?.State == OperationState.PUBLISHED &&
                            rev == 1 &&
                            outbox?.Status == "DELIVERED";

                return (pass, $"OutboxReplayedCount={recoveryReport.OutboxDeliveredCount}, OpState={op?.State}, OutboxStatus={outbox?.Status}, ProbeRev={rev}");
            }));

            // Test 11: Outbox replay does not advance ProbeRevision again
            report.Tests.Add(RunTest("E1_11_OUTBOX_REPLAY_DOES_NOT_ADVANCE_REVISION", "11. Outbox replay does not advance ProbeRevision again (Strict Idempotency)", () =>
            {
                const string opId = "OP_CRASH_AFTER_COMMIT_01";
                const string scopeId = "SCOPE_CRASH_03";

                // Re-run reconciler again to ensure multiple recovery passes are strictly idempotent
                var secondRecovery = _reconciler.ReconcilePendingOperations();

                using var conn = _dbContext.CreateOpenConnection();
                long? rev = _probeStore.GetRevision(scopeId, conn);

                // Re-send same operation as client retry
                var retryResult = _coordinator.ExecuteProbeCas(new PipelineProbeRequest
                {
                    OperationId = opId,
                    ProbeScopeId = scopeId,
                    ExpectedProbeRevision = 0,
                    PayloadJson = "{\"crashPoint\":\"AfterCommitBeforeOutbox\"}",
                    ActorId = "CLIENT_RETRY_ACTOR"
                });

                long? revAfterRetry = _probeStore.GetRevision(scopeId, conn);

                bool pass = secondRecovery.OutboxDeliveredCount == 0 && // Nothing to replay
                            rev == 1 &&
                            revAfterRetry == 1 && // Still 1! Never incremented again
                            retryResult.Success &&
                            retryResult.Status == "ALREADY_COMMITTED";

                return (pass, $"Pass2Delivered={secondRecovery.OutboxDeliveredCount}, RevBefore={rev}, RevAfterRetry={revAfterRetry}, ClientRetryStatus={retryResult.Status}");
            }));

            // Test 12: Release/gameplay transport cannot invoke PIPELINE_PROBE_CAS
            report.Tests.Add(RunTest("E1_12_GAMEPLAY_TRANSPORT_PROBE_ACCESS_DENIED", "12. Release/gameplay transport cannot invoke PIPELINE_PROBE_CAS", () =>
            {
                bool denied = _testSurface.TryInvokeFromGameplayTransport("TcpNetworkServer", new object(), out string rejectionReason);

                bool pass = (!denied) &&
                            rejectionReason.Contains("ACCESS_DENIED") &&
                            rejectionReason.Contains("PIPELINE_PROBE_CAS");

                return (pass, $"AccessAllowed={denied}, RejectionReason='{rejectionReason}'");
            }));

            // Test 13: SQLite WAL mode, synchronous setting, and integrity verification
            report.Tests.Add(RunTest("E1_13_SQLITE_PRAGMA_AND_INTEGRITY_CHECK", "13. SQLite WAL mode, synchronous setting, and integrity check", () =>
            {
                string jMode = _dbContext.GetJournalMode();
                string sMode = _dbContext.GetSynchronousMode();
                int uVer = _dbContext.GetUserVersion();
                string integ = _dbContext.RunIntegrityCheck();

                bool pass = string.Equals(jMode, "wal", StringComparison.OrdinalIgnoreCase) &&
                            (string.Equals(sMode, "1", StringComparison.OrdinalIgnoreCase) ||
                             string.Equals(sMode, "normal", StringComparison.OrdinalIgnoreCase) ||
                             string.Equals(sMode, "full", StringComparison.OrdinalIgnoreCase) ||
                             string.Equals(sMode, "2", StringComparison.OrdinalIgnoreCase)) &&
                            uVer >= 1 &&
                            string.Equals(integ, "ok", StringComparison.OrdinalIgnoreCase);

                return (pass, $"JournalMode='{jMode}', Synchronous='{sMode}', UserVersion={uVer}, Integrity='{integ}'");
            }));

            report.OverallSuccess = report.Tests.All(t => t.Passed);

            Console.WriteLine("\n------------------------------------------------------------------");
            Console.WriteLine($"E1 Battery Finished. Passed: {report.Tests.Count(t => t.Passed)} / {report.Tests.Count}. OverallSuccess: {report.OverallSuccess}");
            Console.WriteLine("==================================================================\n");

            return report;
        }

        private static TestAssertionResult RunTest(string id, string title, Func<(bool pass, string details)> testFunc)
        {
            var sw = Stopwatch.StartNew();
            try
            {
                var (pass, details) = testFunc();
                sw.Stop();
                var result = new TestAssertionResult
                {
                    TestId = id,
                    Title = title,
                    Passed = pass,
                    DurationMs = sw.Elapsed.TotalMilliseconds,
                    Details = details
                };

                Console.WriteLine($"  [{(pass ? "PASS" : "FAIL")}] {id}: {title} ({result.DurationMs:F1} ms)");
                Console.WriteLine($"      Details: {details}");
                return result;
            }
            catch (Exception ex)
            {
                sw.Stop();
                var result = new TestAssertionResult
                {
                    TestId = id,
                    Title = title,
                    Passed = false,
                    DurationMs = sw.Elapsed.TotalMilliseconds,
                    Details = $"EXCEPTION: {ex.GetType().Name}: {ex.Message}"
                };

                Console.WriteLine($"  [FAIL] {id}: {title} ({result.DurationMs:F1} ms)");
                Console.WriteLine($"      Exception: {ex.Message}");
                return result;
            }
        }

        private static async Task<TestAssertionResult> RunTestAsync(string id, string title, Func<Task<(bool pass, string details)>> testFunc)
        {
            var sw = Stopwatch.StartNew();
            try
            {
                var (pass, details) = await testFunc();
                sw.Stop();
                var result = new TestAssertionResult
                {
                    TestId = id,
                    Title = title,
                    Passed = pass,
                    DurationMs = sw.Elapsed.TotalMilliseconds,
                    Details = details
                };

                Console.WriteLine($"  [{(pass ? "PASS" : "FAIL")}] {id}: {title} ({result.DurationMs:F1} ms)");
                Console.WriteLine($"      Details: {details}");
                return result;
            }
            catch (Exception ex)
            {
                sw.Stop();
                var result = new TestAssertionResult
                {
                    TestId = id,
                    Title = title,
                    Passed = false,
                    DurationMs = sw.Elapsed.TotalMilliseconds,
                    Details = $"EXCEPTION: {ex.GetType().Name}: {ex.Message}"
                };

                Console.WriteLine($"  [FAIL] {id}: {title} ({result.DurationMs:F1} ms)");
                Console.WriteLine($"      Exception: {ex.Message}");
                return result;
            }
        }
    }
}
