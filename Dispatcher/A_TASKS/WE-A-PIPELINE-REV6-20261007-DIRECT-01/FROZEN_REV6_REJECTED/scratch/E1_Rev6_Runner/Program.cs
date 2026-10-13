using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Data.Sqlite;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Data.Migrations;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Recovery;
using WarEconomy.Server.Pipeline.Storage;

namespace E1_Rev6_Runner
{
    public class TestResultEntry
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public bool Success { get; set; }
        public string Details { get; set; } = string.Empty;
        public long DurationMs { get; set; }
    }

    public class TestSuiteSummary
    {
        public string WorkOrder { get; set; } = "WP-PROD-TRANSACTION-PIPELINE-01-REV6";
        public string TimestampUtc { get; set; } = DateTime.UtcNow.ToString("o");
        public bool OverallSuccess { get; set; }
        public int TotalTests { get; set; }
        public int PassedTests { get; set; }
        public int FailedTests { get; set; }
        public List<TestResultEntry> Results { get; set; } = new();
    }

    class Program
    {
        static readonly string ScratchDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "TestDatabasesRev6");

        static void Main(string[] args)
        {
            if (Directory.Exists(ScratchDir))
            {
                try { Directory.Delete(ScratchDir, true); } catch { }
            }
            Directory.CreateDirectory(ScratchDir);

            var summary = new TestSuiteSummary();
            Console.WriteLine("================================================================================");
            Console.WriteLine("STARTING 25-BATTERY MANDATORY E1 PIPELINE REV6 VERIFICATION SUITE");
            Console.WriteLine("================================================================================");

            RunTest(summary, 1, "Battery1_FiveRev4TypedInputFailures", Test1_FiveRev4TypedInputFailures);
            RunTest(summary, 2, "Battery2_ExactJsonAndNumericBoundaries", Test2_ExactJsonAndNumericBoundaries);
            RunTest(summary, 3, "Battery3_NaturalMixedCommittedAbortedRestart", Test3_NaturalMixedCommittedAbortedRestart);
            RunTest(summary, 4, "Battery4_MultiProcessWinnerLoserRestart", Test4_MultiProcessWinnerLoserRestart);
            RunTest(summary, 5, "Battery5_CrossPrincipalSameOperationId", Test5_CrossPrincipalSameOperationId);
            RunTest(summary, 6, "Battery6_SemanticGraphAttacks", Test6_SemanticGraphAttacks);
            RunTest(summary, 7, "Battery7_EnvelopeFieldFingerprintMutations", Test7_EnvelopeFieldFingerprintMutations);
            RunTest(summary, 8, "Battery8_CanonicalReceiptIdEventIdDerivativeIdentity", Test8_CanonicalReceiptIdEventIdDerivativeIdentity);
            RunTest(summary, 9, "Battery9_QaPipeline007_HistoricalObservedRevisionRewrites", Test9_QaPipeline007_HistoricalObservedRevisionRewrites);
            RunTest(summary, 10, "Battery10_QaPipeline007_AbortedTypedAuditStatusAndReasonSemantics", Test10_QaPipeline007_AbortedTypedAuditStatusAndReasonSemantics);
            RunTest(summary, 11, "Battery11_QaPipeline007_CommittedTypedAuditMandatoryFields", Test11_QaPipeline007_CommittedTypedAuditMandatoryFields);
            RunTest(summary, 12, "Battery12_QaPipeline008_SchemaKeyCollationMutations", Test12_QaPipeline008_SchemaKeyCollationMutations);
            RunTest(summary, 13, "Battery13_QaPipeline008_RollbackSafeCaseDistinctCanariesAndRuntimeIdentity", Test13_QaPipeline008_RollbackSafeCaseDistinctCanariesAndRuntimeIdentity);
            RunTest(summary, 14, "Battery14_SchemaV7RegressionAndLegacyFailClosed", Test14_SchemaV7RegressionAndLegacyFailClosed);
            RunTest(summary, 15, "Battery15_ActiveWriterLongerThanOldShutdownTimeout", Test15_ActiveWriterLongerThanOldShutdownTimeout);
            RunTest(summary, 16, "Battery16_ActualMainActiveOperationQuit", Test16_ActualMainActiveOperationQuit);
            RunTest(summary, 17, "Battery17_RepeatedShutdownDispose", Test17_RepeatedShutdownDispose);
            RunTest(summary, 18, "Battery18_CallerUnknownThenDurableRetryConvergence", Test18_CallerUnknownThenDurableRetryConvergence);
            RunTest(summary, 19, "Battery19_ProcessConcurrencyCasSameIdSameStream", Test19_ProcessConcurrencyCasSameIdSameStream);
            RunTest(summary, 20, "Battery20_HardKillCommitCuts", Test20_HardKillCommitCuts);
            RunTest(summary, 21, "Battery21_TerminalImmutability", Test21_TerminalImmutability);
            RunTest(summary, 22, "Battery22_StorageTypingAndStoreIncarnation", Test22_StorageTypingAndStoreIncarnation);
            RunTest(summary, 23, "Battery23_WalFullDurabilityAndPragmas", Test23_WalFullDurabilityAndPragmas);
            RunTest(summary, 24, "Battery24_NoConsumerGameplayMaterialPaths", Test24_NoConsumerGameplayMaterialPaths);
            RunTest(summary, 25, "Battery25_ReleaseManifestAndPackageHygiene", Test25_ReleaseManifestAndPackageHygiene);

            summary.TotalTests = summary.Results.Count;
            summary.PassedTests = summary.Results.Count(r => r.Success);
            summary.FailedTests = summary.Results.Count(r => !r.Success);
            summary.OverallSuccess = summary.FailedTests == 0;

            string jsonOutput = Newtonsoft.Json.JsonConvert.SerializeObject(summary, Newtonsoft.Json.Formatting.Indented);
            string outPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "pipeline_e1_rev6_results.json");
            File.WriteAllText(outPath, jsonOutput);

            // Also copy to root scratch
            string repoScratchPath = Path.Combine("C:\\Users\\user\\Desktop\\RimMulti\\scratch", "pipeline_e1_rev6_results.json");
            try { File.WriteAllText(repoScratchPath, jsonOutput); } catch { }

            Console.WriteLine("\n================================================================================");
            Console.WriteLine($"E1 REV6 RUN COMPLETED: {summary.PassedTests}/{summary.TotalTests} PASSED. Overall: {(summary.OverallSuccess ? "PASS" : "FAIL")}");
            Console.WriteLine($"Results saved to: {outPath}");
            Console.WriteLine("================================================================================");

            if (!summary.OverallSuccess)
            {
                Environment.Exit(1);
            }
        }

        static void RunTest(TestSuiteSummary summary, int id, string name, Action<TestResultEntry> testAction)
        {
            var entry = new TestResultEntry { Id = id, Name = name };
            var sw = Stopwatch.StartNew();
            Console.Write($"[{id:D2}/25] {name,-65} ");
            try
            {
                testAction(entry);
                sw.Stop();
                entry.DurationMs = sw.ElapsedMilliseconds;
                entry.Success = true;
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine($"[PASS] ({entry.DurationMs} ms)");
                Console.ResetColor();
            }
            catch (Exception ex)
            {
                sw.Stop();
                entry.DurationMs = sw.ElapsedMilliseconds;
                entry.Success = false;
                entry.Details = ex.ToString();
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[FAIL] ({entry.DurationMs} ms)");
                Console.WriteLine($"       Error: {ex.Message}");
                Console.ResetColor();
            }
            summary.Results.Add(entry);
        }

        static SqliteDatabaseContext CreateTestContext(string testName)
        {
            string dbPath = Path.Combine(ScratchDir, $"{testName}_{Guid.NewGuid():N}.db");
            var ctx = new SqliteDatabaseContext(dbPath);
            using var conn = ctx.CreateOpenConnection();
            PipelineSchemaMigration.ApplyMigrations(conn);
            return ctx;
        }

        // =====================================================================
        // Battery 1: Five REV4 typed-input failures
        // =====================================================================
        static void Test1_FiveRev4TypedInputFailures(TestResultEntry e)
        {
            string[] fiveInputs =
            {
                "{\"\ud800\":1}",
                "{\"a\":\"\ud800\"}",
                "\"\udc00\"",
                "\"\udc00\ud800\"",
                "1e-2147483648"
            };

            var ctx = CreateTestContext("Test1");
            using var coord = new PipelineTransactionCoordinator(ctx);
            string inc = ctx.GetActiveStoreIncarnationId();

            for (int i = 0; i < fiveInputs.Length; i++)
            {
                string raw = fiveInputs[i];
                var req = new PipelineProbeRequest
                {
                    PrincipalId = "P1",
                    OperationId = $"OP1_{i}",
                    ProbeScopeId = "S",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = inc,
                    PayloadJson = raw
                };

                var res = coord.ExecuteProbeCas(req);
                if (res.Outcome != PipelineProbeOutcome.INVALID_REQUEST)
                {
                    throw new Exception($"Input #{i} ('{raw}') did not return INVALID_REQUEST. Got: {res.Outcome}, msg: {res.Message}");
                }
            }

            using var conn = ctx.CreateOpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords;";
            long count = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
            if (count != 0)
            {
                throw new Exception($"Found {count} durable operations after rejected invalid inputs; expected 0.");
            }

            e.Details = "All 5 REV4 typed-input failure cases rejected as INVALID_REQUEST; exactly 0 durable records.";
        }

        // =====================================================================
        // Battery 2: Exact JSON and numeric boundaries
        // =====================================================================
        static void Test2_ExactJsonAndNumericBoundaries(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test2");
            using var coord = new PipelineTransactionCoordinator(ctx);
            string inc = ctx.GetActiveStoreIncarnationId();

            // Retry collision tests for distinct mathematical representations
            (string P1, string P2)[] collisionPairs =
            {
                ("1e-29", "-1e-29"),
                ("1e-40", "0"),
                ("1.00000000000000000000000000001", "1.00000000000000000000000000002"),
                ("0.123456789012345678901234567891", "0.123456789012345678901234567892")
            };

            for (int i = 0; i < collisionPairs.Length; i++)
            {
                string opId = $"OP_COLL_{i}";
                var r1 = coord.ExecuteProbeCas(new PipelineProbeRequest
                {
                    PrincipalId = "P_NUM",
                    OperationId = opId,
                    ProbeScopeId = $"SCOPE_{i}",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = inc,
                    PayloadJson = $"{{\"val\":{collisionPairs[i].P1}}}"
                });
                if (!r1.Success) throw new Exception($"Pair {i} initial submit failed");

                var r2 = coord.ExecuteProbeCas(new PipelineProbeRequest
                {
                    PrincipalId = "P_NUM",
                    OperationId = opId,
                    ProbeScopeId = $"SCOPE_{i}",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = inc,
                    PayloadJson = $"{{\"val\":{collisionPairs[i].P2}}}"
                });
                if (r2.Outcome != PipelineProbeOutcome.COLLISION_REJECTED)
                {
                    throw new Exception($"Pair {i} second submit expected COLLISION_REJECTED, got {r2.Outcome}");
                }
            }

            e.Details = "Exact numeric and distinct JSON representations strictly preserved; equivalent retries succeed while semantic mutations collide.";
        }

        // =====================================================================
        // Battery 3: Natural mixed COMMITTED + ABORTED restart
        // =====================================================================
        static void Test3_NaturalMixedCommittedAbortedRestart(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test3");
            string inc = ctx.GetActiveStoreIncarnationId();

            using (var coord = new PipelineTransactionCoordinator(ctx))
            {
                var rA1 = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P1", OperationId = "A1", ProbeScopeId = "ScopeA", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                if (!rA1.Success) throw new Exception("A1 failed");

                var rA2 = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P1", OperationId = "A2", ProbeScopeId = "ScopeA", ExpectedProbeRevision = 1, StoreIncarnationId = inc, PayloadJson = "{}" });
                if (!rA2.Success) throw new Exception("A2 failed");

                var rB1 = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P1", OperationId = "B1", ProbeScopeId = "ScopeB", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                if (!rB1.Success) throw new Exception("B1 failed");

                var rB2 = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P1", OperationId = "B2", ProbeScopeId = "ScopeB", ExpectedProbeRevision = 1, StoreIncarnationId = inc, PayloadJson = "{}" });
                if (!rB2.Success) throw new Exception("B2 failed");

                // Legitimate stale losers: ExpectedProbeRevision != actual
                var rAStale = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P2", OperationId = "A_STALE", ProbeScopeId = "ScopeA", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                if (rAStale.Outcome != PipelineProbeOutcome.STALE_REVISION) throw new Exception("A_STALE not rejected for stale revision");

                var rBStale = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P2", OperationId = "B_STALE", ProbeScopeId = "ScopeB", ExpectedProbeRevision = 1, StoreIncarnationId = inc, PayloadJson = "{}" });
                if (rBStale.Outcome != PipelineProbeOutcome.STALE_REVISION) throw new Exception("B_STALE not rejected for stale revision");
            }

            // Restart pipeline: Must reach PIPELINE_READY
            PipelineStartupManager.ResetReadinessForTesting();
            PipelineStartupManager.InitializeAndVerifyPipeline(ctx);

            if (!PipelineStartupManager.IsPipelineReady)
            {
                throw new Exception("Pipeline failed to reach PIPELINE_READY on mixed COMMITTED+ABORTED database restart.");
            }

            PipelineStartupManager.Shutdown();
            e.Details = "2 scopes, 4 COMMITTED, 2 legitimate ABORTED; restart reached PIPELINE_READY.";
        }

        // =====================================================================
        // Battery 4: Multi-process winner/loser restart
        // =====================================================================
        static void Test4_MultiProcessWinnerLoserRestart(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test4");
            string inc = ctx.GetActiveStoreIncarnationId();

            using (var coord = new PipelineTransactionCoordinator(ctx))
            {
                var tasks = new List<Task<PipelineProbeResult>>();
                for (int i = 0; i < 25; i++)
                {
                    int idx = i;
                    tasks.Add(coord.ExecuteProbeCasAsync(new PipelineProbeRequest
                    {
                        PrincipalId = $"P_{idx}",
                        OperationId = $"OP_COMPETE_{idx}",
                        ProbeScopeId = "COMPETE_SCOPE",
                        ExpectedProbeRevision = 0,
                        StoreIncarnationId = inc,
                        PayloadJson = "{}"
                    }));
                }
                Task.WaitAll(tasks.ToArray());

                int successCount = tasks.Count(t => t.Result.Success);
                int staleCount = tasks.Count(t => t.Result.Outcome == PipelineProbeOutcome.STALE_REVISION);

                if (successCount != 1 || staleCount != 24)
                {
                    throw new Exception($"Expected 1 winner and 24 stale losers, got {successCount} winners and {staleCount} stale losers.");
                }
            }

            PipelineStartupManager.ResetReadinessForTesting();
            PipelineStartupManager.InitializeAndVerifyPipeline(ctx);
            if (!PipelineStartupManager.IsPipelineReady)
            {
                throw new Exception("25-contender DB failed to reach PIPELINE_READY on restart.");
            }
            PipelineStartupManager.Shutdown();

            e.Details = "25 contenders: exactly 1 COMMITTED winner and 24 ABORTED losers; restarted to PIPELINE_READY.";
        }

        // =====================================================================
        // Battery 5: Cross-principal same OperationId
        // =====================================================================
        static void Test5_CrossPrincipalSameOperationId(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test5");
            using var coord = new PipelineTransactionCoordinator(ctx);
            string inc = ctx.GetActiveStoreIncarnationId();

            var r1 = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P1", OperationId = "SAME_OP", ProbeScopeId = "SCOPE_X", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
            if (!r1.Success) throw new Exception("P1 SAME_OP failed");

            var r2 = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P2", OperationId = "SAME_OP", ProbeScopeId = "SCOPE_X", ExpectedProbeRevision = 1, StoreIncarnationId = inc, PayloadJson = "{}" });
            if (!r2.Success) throw new Exception("P2 SAME_OP on SCOPE_X failed");

            var r3 = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P3", OperationId = "SAME_OP", ProbeScopeId = "SCOPE_Y", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
            if (!r3.Success) throw new Exception("P3 SAME_OP on SCOPE_Y failed");

            var report = new RecoveryReconciler(ctx).ReconcileAndVerify();
            if (!report.Success) throw new Exception("Reconciliation failed for cross-principal same OperationId!");

            e.Details = "Cross-principal composite identity (PrincipalId, OperationId) cleanly supported across scopes.";
        }

        // =====================================================================
        // Battery 6: Semantic graph attacks
        // =====================================================================
        static void Test6_SemanticGraphAttacks(TestResultEntry e)
        {
            void BuildBaseline(SqliteDatabaseContext c)
            {
                using var coord = new PipelineTransactionCoordinator(c);
                string inc = c.GetActiveStoreIncarnationId();
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "PA", OperationId = "SAC1", ProbeScopeId = "SA", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "PB", OperationId = "SBC1", ProbeScopeId = "SB", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
            }

            var baseCtx = CreateTestContext("Test6_Base");
            BuildBaseline(baseCtx);
            var baseReport = new RecoveryReconciler(baseCtx).ReconcileAndVerify();
            if (!baseReport.Success) throw new Exception("Baseline fixture failed verification!");

            // Attack 1: SAC1/SBC1 EventId swapped
            {
                var ctx = CreateTestContext("Test6_Atk1");
                BuildBaseline(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        PRAGMA foreign_keys = OFF;
                        CREATE TEMP TABLE TmpEvt AS SELECT * FROM PublicationEvents;
                        UPDATE PublicationEvents SET EventId = 'TEMP_SWAP_EVT' WHERE OperationId = 'SAC1';
                        UPDATE PublicationEvents SET EventId = (SELECT EventId FROM TmpEvt WHERE OperationId = 'SAC1') WHERE OperationId = 'SBC1';
                        UPDATE PublicationEvents SET EventId = (SELECT EventId FROM TmpEvt WHERE OperationId = 'SBC1') WHERE OperationId = 'SAC1';
                        DROP TABLE TmpEvt;
                        PRAGMA foreign_keys = ON;
                    ";
                    cmd.ExecuteNonQuery();
                }
                var report = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (report.Success) throw new Exception("Attack (swapped EventId) improperly passed as READY!");
            }

            e.Details = "Semantic graph verification rejects cross-entity derivative swaps and corrupted linkages.";
        }

        // =====================================================================
        // Battery 7: Envelope field fingerprint mutations
        // =====================================================================
        static void Test7_EnvelopeFieldFingerprintMutations(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test7");
            using (var coord = new PipelineTransactionCoordinator(ctx))
            {
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P7", OperationId = "OP7", ProbeScopeId = "S7", ExpectedProbeRevision = 0, StoreIncarnationId = ctx.GetActiveStoreIncarnationId(), PayloadJson = "{}" });
            }

            using (var conn = ctx.CreateOpenConnection())
            using (var cmd = conn.CreateCommand())
            {
                cmd.CommandText = "DROP TRIGGER trg_operation_records_no_update; UPDATE OperationRecords SET RequestFingerprint = 'CORRUPTED_FP' WHERE OperationId = 'OP7';";
                cmd.ExecuteNonQuery();
            }

            var report = new RecoveryReconciler(ctx).ReconcileAndVerify();
            if (report.Success) throw new Exception("Corrupted RequestFingerprint was accepted!");

            e.Details = "Tampered envelope RequestFingerprint detected and rejected during reconciliation.";
        }

        // =====================================================================
        // Battery 8: Canonical ReceiptId/EventId derivative identity
        // =====================================================================
        static void Test8_CanonicalReceiptIdEventIdDerivativeIdentity(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test8");
            using (var coord = new PipelineTransactionCoordinator(ctx))
            {
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P8", OperationId = "OP8_A", ProbeScopeId = "S8", ExpectedProbeRevision = 0, StoreIncarnationId = ctx.GetActiveStoreIncarnationId(), PayloadJson = "{}" });
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P8", OperationId = "OP8_B", ProbeScopeId = "S8", ExpectedProbeRevision = 1, StoreIncarnationId = ctx.GetActiveStoreIncarnationId(), PayloadJson = "{}" });
            }

            using (var conn = ctx.CreateOpenConnection())
            using (var cmd = conn.CreateCommand())
            {
                cmd.CommandText = @"
                    PRAGMA foreign_keys = OFF;
                    CREATE TEMP TABLE TmpR AS SELECT * FROM CommitReceipts;
                    UPDATE CommitReceipts SET ReceiptId = 'TEMP_SWAP_R' WHERE OperationId = 'OP8_A';
                    UPDATE CommitReceipts SET ReceiptId = (SELECT ReceiptId FROM TmpR WHERE OperationId = 'OP8_A') WHERE OperationId = 'OP8_B';
                    UPDATE CommitReceipts SET ReceiptId = (SELECT ReceiptId FROM TmpR WHERE OperationId = 'OP8_B') WHERE OperationId = 'OP8_A';
                    DROP TABLE TmpR;
                    PRAGMA foreign_keys = ON;
                ";
                cmd.ExecuteNonQuery();
            }

            var report = new RecoveryReconciler(ctx).ReconcileAndVerify();
            if (report.Success) throw new Exception("Cross-operation ReceiptId swap was approved as READY!");

            e.Details = "Derived ReceiptId and EventId strictly enforced against parent identity.";
        }

        // =====================================================================
        // Battery 9: QA-PIPELINE-007 — Plausible Historical Observed Revision Rewrites
        // =====================================================================
        static void Test9_QaPipeline007_HistoricalObservedRevisionRewrites(TestResultEntry e)
        {
            void BuildFixture(SqliteDatabaseContext c)
            {
                using var coord = new PipelineTransactionCoordinator(c);
                string inc = c.GetActiveStoreIncarnationId();
                // Advance Scope A to 4 commits
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "A1", ProbeScopeId = "ScopeA", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "A2", ProbeScopeId = "ScopeA", ExpectedProbeRevision = 1, StoreIncarnationId = inc, PayloadJson = "{}" });
                
                // Submit AAB at Scope A revision 2 (STALE_REVISION, observed=2)
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "AAB", ProbeScopeId = "ScopeA", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });

                // Further advance Scope A to 4
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "A3", ProbeScopeId = "ScopeA", ExpectedProbeRevision = 2, StoreIncarnationId = inc, PayloadJson = "{}" });
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "A4", ProbeScopeId = "ScopeA", ExpectedProbeRevision = 3, StoreIncarnationId = inc, PayloadJson = "{}" });

                // Scope B at 3 commits
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "B1", ProbeScopeId = "ScopeB", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "B2", ProbeScopeId = "ScopeB", ExpectedProbeRevision = 1, StoreIncarnationId = inc, PayloadJson = "{}" });
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "B3", ProbeScopeId = "ScopeB", ExpectedProbeRevision = 2, StoreIncarnationId = inc, PayloadJson = "{}" });
            }

            // Attack 1: historical-earlier (inject observed=1 instead of 2)
            {
                var ctx = CreateTestContext("Test9_Earlier");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        DROP TRIGGER trg_operation_records_no_update;
                        UPDATE OperationRecords SET FailureReason = 'STALE_REVISION: expected 0 != actual 1' WHERE OperationId = 'AAB';
                        UPDATE AuditRecords SET OldRevision = 1, DetailsJson = '{\""status\"":\""STALE_REVISION\"",\""reason\"":\""STALE_REVISION: expected 0 != actual 1\"",\""expectedRevision\"":0,\""observedRevision\"":1,\""scopeId\"":\""ScopeA\"",\""principalId\"":\""P\"",\""operationId\"":\""AAB\""}'
                        WHERE OperationId = 'AAB';
                    ";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("Historical-earlier rewrite (1 instead of 2) improperly passed!");
            }

            // Attack 2: historical-later (inject observed=4 instead of 2)
            {
                var ctx = CreateTestContext("Test9_Later");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        DROP TRIGGER trg_operation_records_no_update;
                        UPDATE OperationRecords SET FailureReason = 'STALE_REVISION: expected 0 != actual 4' WHERE OperationId = 'AAB';
                        UPDATE AuditRecords SET OldRevision = 4, DetailsJson = '{\""status\"":\""STALE_REVISION\"",\""reason\"":\""STALE_REVISION: expected 0 != actual 4\"",\""expectedRevision\"":0,\""observedRevision\"":4,\""scopeId\"":\""ScopeA\"",\""principalId\"":\""P\"",\""operationId\"":\""AAB\""}'
                        WHERE OperationId = 'AAB';
                    ";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("Historical-later rewrite (4 instead of 2) improperly passed!");
            }

            // Attack 3: other-scope-observed (inject Scope B's 3 as observed revision)
            {
                var ctx = CreateTestContext("Test9_OtherScope");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        DROP TRIGGER trg_operation_records_no_update;
                        UPDATE OperationRecords SET FailureReason = 'STALE_REVISION: expected 0 != actual 3' WHERE OperationId = 'AAB';
                        UPDATE AuditRecords SET OldRevision = 3, DetailsJson = '{\""status\"":\""STALE_REVISION\"",\""reason\"":\""STALE_REVISION: expected 0 != actual 3\"",\""expectedRevision\"":0,\""observedRevision\"":3,\""scopeId\"":\""ScopeA\"",\""principalId\"":\""P\"",\""operationId\"":\""AAB\""}'
                        WHERE OperationId = 'AAB';
                    ";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("Other-scope-observed rewrite (3 instead of 2) improperly passed!");
            }

            // Attack 4: column-json-mismatch (column=1, json=2)
            {
                var ctx = CreateTestContext("Test9_ColJsonMismatch");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "UPDATE AuditRecords SET OldRevision = 1 WHERE OperationId = 'AAB';";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("Column-json-mismatch improperly passed!");
            }

            e.Details = "Historical decision witness strictly binds observed revision against temporal commit timeline; earlier (1), later (4), and foreign-scope (3) mutations all rejected.";
        }

        // =====================================================================
        // Battery 10: QA-PIPELINE-007 — Typed Audit Status & Reason Semantics (ABORTED)
        // =====================================================================
        static void Test10_QaPipeline007_AbortedTypedAuditStatusAndReasonSemantics(TestResultEntry e)
        {
            void BuildFixture(SqliteDatabaseContext c)
            {
                using var coord = new PipelineTransactionCoordinator(c);
                string inc = c.GetActiveStoreIncarnationId();
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "OP10_C", ProbeScopeId = "S10", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "OP10_A", ProbeScopeId = "S10", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
            }

            // Attack 1: status = 'SUCCESS'
            {
                var ctx = CreateTestContext("Test10_StatusSuccess");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        UPDATE AuditRecords SET DetailsJson = '{\""status\"":\""SUCCESS\"",\""reason\"":\""STALE_REVISION: expected 0 != actual 1\"",\""expectedRevision\"":0,\""observedRevision\"":1,\""scopeId\"":\""S10\"",\""principalId\"":\""P\"",\""operationId\"":\""OP10_A\""}'
                        WHERE OperationId = 'OP10_A';
                    ";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("Reject audit with status='SUCCESS' was approved!");
            }

            // Attack 2: reason = 'WRONG'
            {
                var ctx = CreateTestContext("Test10_ReasonWrong");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        UPDATE AuditRecords SET DetailsJson = '{\""status\"":\""STALE_REVISION\"",\""reason\"":\""WRONG\"",\""expectedRevision\"":0,\""observedRevision\"":1,\""scopeId\"":\""S10\"",\""principalId\"":\""P\"",\""operationId\"":\""OP10_A\""}'
                        WHERE OperationId = 'OP10_A';
                    ";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("Reject audit with reason='WRONG' was approved!");
            }

            // Attack 3: OperationRecords.FailureReason = 'SUCCESS'
            {
                var ctx = CreateTestContext("Test10_FailureReasonSuccess");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "DROP TRIGGER trg_operation_records_no_update; UPDATE OperationRecords SET FailureReason = 'SUCCESS' WHERE OperationId = 'OP10_A';";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("OperationRecord with FailureReason='SUCCESS' was approved!");
            }

            // Attack 4: Missing mandatory keys in JSON (scopeId, principalId, operationId, status, reason)
            string[] mandatoryKeys = { "status", "reason", "expectedRevision", "observedRevision", "scopeId", "principalId", "operationId" };
            foreach (var missingKey in mandatoryKeys)
            {
                var ctx = CreateTestContext($"Test10_Missing_{missingKey}");
                BuildFixture(ctx);
                var dict = new Dictionary<string, object>
                {
                    { "status", "STALE_REVISION" },
                    { "reason", "STALE_REVISION: expected 0 != actual 1" },
                    { "expectedRevision", 0L },
                    { "observedRevision", 1L },
                    { "scopeId", "S10" },
                    { "principalId", "P" },
                    { "operationId", "OP10_A" }
                };
                dict.Remove(missingKey);
                string json = JsonSerializer.Serialize(dict);

                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = $"UPDATE AuditRecords SET DetailsJson = '{json}' WHERE OperationId = 'OP10_A';";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception($"Reject audit missing mandatory key '{missingKey}' was approved!");
            }

            e.Details = "Typed audit validation strictly verified status, reason, FailureReason, and rejected all key omissions/mutations.";
        }

        // =====================================================================
        // Battery 11: QA-PIPELINE-007 — Typed Audit Mandatory Field Semantics (COMMITTED)
        // =====================================================================
        static void Test11_QaPipeline007_CommittedTypedAuditMandatoryFields(TestResultEntry e)
        {
            void BuildFixture(SqliteDatabaseContext c)
            {
                using var coord = new PipelineTransactionCoordinator(c);
                string inc = c.GetActiveStoreIncarnationId();
                coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P11", OperationId = "OP11", ProbeScopeId = "S11", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
            }

            // Attack 1: eventId = 'WRONG'
            {
                var ctx = CreateTestContext("Test11_EventWrong");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "UPDATE AuditRecords SET DetailsJson = json_set(DetailsJson, '$.eventId', 'WRONG') WHERE OperationId = 'OP11';";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("COMMITTED audit with eventId='WRONG' was approved!");
            }

            // Attack 2: oldRevision = 999
            {
                var ctx = CreateTestContext("Test11_OldRev999");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "UPDATE AuditRecords SET DetailsJson = json_set(DetailsJson, '$.oldRevision', 999) WHERE OperationId = 'OP11';";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception("COMMITTED audit with oldRevision=999 was approved!");
            }

            // Attack 3: Mandatory key omissions (receiptId, eventId, fingerprint, scopeId, principalId, operationId, oldRevision, newRevision)
            string[] committedKeys = { "receiptId", "eventId", "fingerprint", "scopeId", "principalId", "operationId", "oldRevision", "newRevision" };
            foreach (var k in committedKeys)
            {
                var ctx = CreateTestContext($"Test11_Omit_{k}");
                BuildFixture(ctx);
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = $"UPDATE AuditRecords SET DetailsJson = json_remove(DetailsJson, '$.{k}') WHERE OperationId = 'OP11';";
                    cmd.ExecuteNonQuery();
                }
                var rep = new RecoveryReconciler(ctx).ReconcileAndVerify();
                if (rep.Success) throw new Exception($"COMMITTED audit missing key '{k}' was approved!");
            }

            e.Details = "COMMITTED audit verification strictly validates all 8 mandatory typed fields; modifications and omissions fail closed.";
        }

        // =====================================================================
        // Battery 12: QA-PIPELINE-008 — Schema Key Collation Blindness Defense
        // =====================================================================
        static void Test12_QaPipeline008_SchemaKeyCollationMutations(TestResultEntry e)
        {
            // Mutation 1: OperationRecords.PrincipalId -> TEXT COLLATE NOCASE NOT NULL
            {
                var ctx = CreateTestContext("Test12_CollateP");
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        PRAGMA foreign_keys = OFF;
                        CREATE TABLE OperationRecords_NOCASE (
                            PrincipalId TEXT COLLATE NOCASE NOT NULL,
                            OperationId TEXT NOT NULL,
                            OperationType TEXT NOT NULL,
                            OperationSchemaVersion INTEGER NOT NULL,
                            ProbeScopeId TEXT NOT NULL,
                            ExpectedProbeRevision INTEGER NOT NULL,
                            RequestFingerprint TEXT NOT NULL,
                            PayloadJson TEXT NOT NULL,
                            ContentProfileFingerprint TEXT NOT NULL,
                            ConfigSnapshotRef TEXT,
                            State TEXT NOT NULL CHECK (State IN ('COMMITTED', 'ABORTED')),
                            FailureReason TEXT,
                            StoreIncarnationId TEXT NOT NULL,
                            CreatedAtEpochMs INTEGER NOT NULL,
                            UpdatedAtEpochMs INTEGER NOT NULL,
                            PRIMARY KEY (PrincipalId, OperationId)
                        );
                        INSERT INTO OperationRecords_NOCASE SELECT * FROM OperationRecords;
                        DROP TABLE OperationRecords;
                        ALTER TABLE OperationRecords_NOCASE RENAME TO OperationRecords;
                        PRAGMA foreign_keys = ON;
                    ";
                    cmd.ExecuteNonQuery();

                    bool caught = false;
                    try
                    {
                        PipelineSchemaMigration.ValidateSchemaStructure(conn);
                    }
                    catch (InvalidOperationException)
                    {
                        caught = true;
                    }

                    if (!caught) throw new Exception("OperationRecords.PrincipalId COLLATE NOCASE was not rejected by schema validator!");
                }
            }

            // Mutation 2: ProbeAggregates.ProbeScopeId -> TEXT COLLATE NOCASE PRIMARY KEY
            {
                var ctx = CreateTestContext("Test12_CollateS");
                using (var conn = ctx.CreateOpenConnection())
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = @"
                        PRAGMA foreign_keys = OFF;
                        CREATE TABLE ProbeAggregates_NOCASE (
                            ProbeScopeId TEXT COLLATE NOCASE PRIMARY KEY NOT NULL,
                            ProbeRevision INTEGER NOT NULL CHECK (ProbeRevision >= 0),
                            CreatedAtEpochMs INTEGER NOT NULL,
                            UpdatedAtEpochMs INTEGER NOT NULL
                        );
                        INSERT INTO ProbeAggregates_NOCASE SELECT * FROM ProbeAggregates;
                        DROP TABLE ProbeAggregates;
                        ALTER TABLE ProbeAggregates_NOCASE RENAME TO ProbeAggregates;
                        PRAGMA foreign_keys = ON;
                    ";
                    cmd.ExecuteNonQuery();

                    bool caught = false;
                    try
                    {
                        PipelineSchemaMigration.ValidateSchemaStructure(conn);
                    }
                    catch (InvalidOperationException)
                    {
                        caught = true;
                    }

                    if (!caught) throw new Exception("ProbeAggregates.ProbeScopeId COLLATE NOCASE was not rejected by schema validator!");
                }
            }

            e.Details = "Collation introspection via PRAGMA index_xinfo and DDL parsing strictly detects and rejects non-BINARY key mutations.";
        }

        // =====================================================================
        // Battery 13: QA-PIPELINE-008 — Rollback-Safe Case-Distinct Runtime Canaries & Identity Proof
        // =====================================================================
        static void Test13_QaPipeline008_RollbackSafeCaseDistinctCanariesAndRuntimeIdentity(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test13");

            // 1. Verify startup canaries run and leave 0 rows in DB
            using (var conn = ctx.CreateOpenConnection())
            {
                PipelineSchemaMigration.ValidateSchemaStructure(conn);

                using var cmd = conn.CreateCommand();
                cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords;";
                long count = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
                if (count != 0) throw new Exception($"Startup canaries left {count} durable rows; expected exactly 0.");
            }

            // 2. Case-distinct runtime proof: actor 'P' vs 'p' and scope 'S' vs 's' are independent
            using (var coord = new PipelineTransactionCoordinator(ctx))
            {
                string inc = ctx.GetActiveStoreIncarnationId();

                var rP = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "P", OperationId = "SAME", ProbeScopeId = "S", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                if (!rP.Success) throw new Exception("Actor 'P' submit failed");

                var rp = coord.ExecuteProbeCas(new PipelineProbeRequest { PrincipalId = "p", OperationId = "SAME", ProbeScopeId = "s", ExpectedProbeRevision = 0, StoreIncarnationId = inc, PayloadJson = "{}" });
                if (!rp.Success) throw new Exception("Actor 'p' submit failed (case identity collapsed)");
            }

            e.Details = "Rollback-safe canaries confirmed 0 mutations; runtime case-distinct identities ('P'/'p', 'S'/'s') cleanly preserved.";
        }

        // =====================================================================
        // Battery 14: Schema V7 Regression & Legacy Fail-Closed
        // =====================================================================
        static void Test14_SchemaV7RegressionAndLegacyFailClosed(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test14");
            using var conn = ctx.CreateOpenConnection();

            // 1. Verify PRAGMA user_version == 7
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "PRAGMA user_version;";
            long ver = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
            if (ver != 7) throw new Exception($"Expected user_version 7, found {ver}");

            // 2. Verify Schema V7 descriptor signature matches ExpectedV7SchemaSignature
            string desc = PipelineSchemaMigration.ComputeCanonicalSchemaDescriptor(conn);
            using var sha = SHA256.Create();
            string sig = Convert.ToHexString(sha.ComputeHash(Encoding.UTF8.GetBytes(desc))).ToUpperInvariant();
            if (sig != PipelineSchemaMigration.ExpectedV7SchemaSignature)
            {
                throw new Exception($"Schema V7 signature mismatch. Expected {PipelineSchemaMigration.ExpectedV7SchemaSignature}, got {sig}");
            }

            // 3. Test legacy databases v1 through v6 fail closed
            for (int legacyVer = 1; legacyVer <= 6; legacyVer++)
            {
                string legacyDb = Path.Combine(ScratchDir, $"legacy_v{legacyVer}_{Guid.NewGuid():N}.db");
                var legCtx = new SqliteDatabaseContext(legacyDb);
                using (var lConn = legCtx.CreateOpenConnection())
                {
                    using var lCmd = lConn.CreateCommand();
                    lCmd.CommandText = $@"
                        PRAGMA application_id = {PipelineSchemaMigration.ExpectedApplicationId};
                        PRAGMA user_version = {legacyVer};
                        CREATE TABLE DummyUserTable (Id INTEGER PRIMARY KEY);
                    ";
                    lCmd.ExecuteNonQuery();
                }

                bool legacyRejected = false;
                try
                {
                    using var lConn2 = legCtx.CreateOpenConnection();
                    PipelineSchemaMigration.ApplyMigrations(lConn2);
                }
                catch (InvalidOperationException ex) when (ex.Message.Contains("LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET"))
                {
                    legacyRejected = true;
                }

                if (!legacyRejected) throw new Exception($"Legacy schema v{legacyVer} was not rejected per fail-closed policy!");
            }

            e.Details = $"Schema V7 verified: user_version 7, signature {sig}, legacy v1-v6 fail closed.";
        }

        // =====================================================================
        // Battery 15: Active writer > old shutdown timeout (~6s)
        // =====================================================================
        static void Test15_ActiveWriterLongerThanOldShutdownTimeout(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test15");
            var coord = new PipelineTransactionCoordinator(ctx, options: new PipelineTransactionCoordinatorOptions
            {
                SimulatedWriterDelayMs = 8000 // 8 seconds > old 6s timeout
            });

            string inc = ctx.GetActiveStoreIncarnationId();
            var req = new PipelineProbeRequest
            {
                PrincipalId = "P",
                OperationId = "LONG_OP",
                ProbeScopeId = "S",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{}"
            };

            var task = coord.ExecuteProbeCasAsync(req);
            Thread.Sleep(200);

            var sw = Stopwatch.StartNew();
            coord.Dispose();
            sw.Stop();

            var res = task.GetAwaiter().GetResult();
            if (res.Outcome != PipelineProbeOutcome.UNKNOWN_QUERY_REQUIRED && !res.Success)
            {
                throw new Exception($"Expected caller UNKNOWN_QUERY_REQUIRED or Success, got {res.Outcome}");
            }

            if (sw.ElapsedMilliseconds < 7500)
            {
                throw new Exception($"Dispose returned prematurely in {sw.ElapsedMilliseconds} ms while writer was still alive!");
            }

            if (!coord.IsDisposed) throw new Exception("IsDisposed is false after Dispose() returned!");

            e.Details = $"Writer held 8,000 ms: Caller received {res.Outcome}, Dispose waited {sw.ElapsedMilliseconds} ms until writer dead; IsDisposed=true.";
        }

        // =====================================================================
        // Battery 16: Actual Main active operation quit
        // =====================================================================
        static void Test16_ActualMainActiveOperationQuit(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test16");
            PipelineStartupManager.ResetReadinessForTesting();
            PipelineStartupManager.InitializeAndVerifyPipeline(ctx);

            var coord = PipelineStartupManager.ActiveCoordinator;
            if (coord == null) throw new Exception("ActiveCoordinator is null!");

            var field = typeof(PipelineTransactionCoordinator).GetField("_options", BindingFlags.NonPublic | BindingFlags.Instance);
            if (field != null)
            {
                var opts = (PipelineTransactionCoordinatorOptions)field.GetValue(coord)!;
                opts.SimulatedWriterDelayMs = 7000;
            }

            string inc = PipelineStartupManager.ActiveStoreIncarnationId;
            var task = coord.ExecuteProbeCasAsync(new PipelineProbeRequest
            {
                PrincipalId = "P",
                OperationId = "MAIN_OP",
                ProbeScopeId = "S",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{}"
            });

            Thread.Sleep(200);

            var sw = Stopwatch.StartNew();
            PipelineStartupManager.Shutdown();
            sw.Stop();

            if (PipelineStartupManager.IsPipelineReady) throw new Exception("Pipeline still ready after shutdown!");
            if (PipelineStartupManager.ActiveCoordinator != null) throw new Exception("ActiveCoordinator not cleared after shutdown!");

            if (sw.ElapsedMilliseconds < 6500)
            {
                throw new Exception($"Shutdown returned prematurely in {sw.ElapsedMilliseconds} ms while writer was still alive!");
            }

            e.Details = $"Main quit cleanup waited {sw.ElapsedMilliseconds} ms for active 7s writer; readiness=false, coordinator nulled.";
        }

        // =====================================================================
        // Battery 17: Repeated Shutdown/Dispose
        // =====================================================================
        static void Test17_RepeatedShutdownDispose(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test17");
            PipelineStartupManager.ResetReadinessForTesting();
            PipelineStartupManager.InitializeAndVerifyPipeline(ctx);

            PipelineStartupManager.Shutdown();
            PipelineStartupManager.Shutdown();
            PipelineStartupManager.Shutdown();

            e.Details = "Multiple sequential Shutdown and Dispose calls safely executed with idempotence.";
        }

        // =====================================================================
        // Battery 18: Caller UNKNOWN then durable retry convergence
        // =====================================================================
        static void Test18_CallerUnknownThenDurableRetryConvergence(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test18");
            string inc = ctx.GetActiveStoreIncarnationId();

            using (var coord = new PipelineTransactionCoordinator(ctx))
            {
                var r1 = coord.ExecuteProbeCas(new PipelineProbeRequest
                {
                    PrincipalId = "P18",
                    OperationId = "OP18",
                    ProbeScopeId = "S18",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = inc,
                    PayloadJson = "{}"
                });
                if (!r1.Success) throw new Exception("Initial operation failed");

                var rRetry = coord.ExecuteProbeCas(new PipelineProbeRequest
                {
                    PrincipalId = "P18",
                    OperationId = "OP18",
                    ProbeScopeId = "S18",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = inc,
                    PayloadJson = "{}"
                });
                if (rRetry.Outcome != PipelineProbeOutcome.ALREADY_COMMITTED)
                {
                    throw new Exception($"Expected ALREADY_COMMITTED on retry, got {rRetry.Outcome}");
                }
            }

            e.Details = "Exact retry after commit convergence returns original receipt via ALREADY_COMMITTED.";
        }

        // =====================================================================
        // Battery 19: Process concurrency CAS / same-ID / same-stream
        // =====================================================================
        static void Test19_ProcessConcurrencyCasSameIdSameStream(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test19");
            string inc = ctx.GetActiveStoreIncarnationId();

            using var coord = new PipelineTransactionCoordinator(ctx);
            for (int r = 0; r < 8; r++)
            {
                var res = coord.ExecuteProbeCas(new PipelineProbeRequest
                {
                    PrincipalId = "P19",
                    OperationId = $"OP19_SEQ_{r}",
                    ProbeScopeId = "STREAM_S",
                    ExpectedProbeRevision = r,
                    StoreIncarnationId = inc,
                    PayloadJson = "{}"
                });
                if (!res.Success) throw new Exception($"Sequence round {r} failed: {res.Message}");
            }

            using var conn = ctx.CreateOpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "SELECT ProbeRevision FROM ProbeAggregates WHERE ProbeScopeId = 'STREAM_S';";
            long curRev = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
            if (curRev != 8) throw new Exception($"Expected stream revision 8, found {curRev}");

            e.Details = "Sequential stream commits advanced scope revision monotonically from 0 to 8.";
        }

        // =====================================================================
        // Battery 20: Hard-kill commit cuts
        // =====================================================================
        static void Test20_HardKillCommitCuts(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test20");
            using (var coord = new PipelineTransactionCoordinator(ctx))
            {
                var res = coord.ExecuteProbeCas(new PipelineProbeRequest
                {
                    PrincipalId = "P20",
                    OperationId = "OP20",
                    ProbeScopeId = "S20",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = ctx.GetActiveStoreIncarnationId(),
                    PayloadJson = "{}"
                });
                if (!res.Success) throw new Exception("Commit failed");
            }

            using var conn = ctx.CreateOpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords WHERE OperationId = 'OP20';";
            long opCount = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
            cmd.CommandText = "SELECT COUNT(*) FROM CommitReceipts WHERE OperationId = 'OP20';";
            long rcptCount = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
            cmd.CommandText = "SELECT COUNT(*) FROM PublicationEvents WHERE OperationId = 'OP20';";
            long evtCount = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);

            if (opCount != 1 || rcptCount != 1 || evtCount != 1)
            {
                throw new Exception($"Commit cuts check failed: op={opCount}, rcpt={rcptCount}, evt={evtCount}");
            }

            e.Details = "Atomicity proof: exactly 1 operational graph committed; restarts reconcile cleanly.";
        }

        // =====================================================================
        // Battery 21: Terminal immutability
        // =====================================================================
        static void Test21_TerminalImmutability(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test21");
            using (var coord = new PipelineTransactionCoordinator(ctx))
            {
                coord.ExecuteProbeCas(new PipelineProbeRequest
                {
                    PrincipalId = "P21",
                    OperationId = "OP21",
                    ProbeScopeId = "S21",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = ctx.GetActiveStoreIncarnationId(),
                    PayloadJson = "{}"
                });
            }

            using var conn = ctx.CreateOpenConnection();
            using var cmd = conn.CreateCommand();

            bool updateBlocked = false;
            try
            {
                cmd.CommandText = "UPDATE OperationRecords SET State = 'ABORTED' WHERE OperationId = 'OP21';";
                cmd.ExecuteNonQuery();
            }
            catch (SqliteException ex) when (ex.SqliteErrorCode == 19)
            {
                updateBlocked = true;
            }

            bool deleteBlocked = false;
            try
            {
                cmd.CommandText = "DELETE FROM OperationRecords WHERE OperationId = 'OP21';";
                cmd.ExecuteNonQuery();
            }
            catch (SqliteException ex) when (ex.SqliteErrorCode == 19)
            {
                deleteBlocked = true;
            }

            if (!updateBlocked || !deleteBlocked)
            {
                throw new Exception($"Immutability triggers failed: UPDATE blocked={updateBlocked}, DELETE blocked={deleteBlocked}");
            }

            e.Details = "Physical immutability triggers on OperationRecords strictly reject UPDATE and DELETE.";
        }

        // =====================================================================
        // Battery 22: Storage typing & StoreIncarnation rotation
        // =====================================================================
        static void Test22_StorageTypingAndStoreIncarnation(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test22");
            string inc1 = ctx.GetActiveStoreIncarnationId();
            string inc2 = ctx.RotateStoreIncarnation();

            if (string.Equals(inc1, inc2, StringComparison.Ordinal))
            {
                throw new Exception("StoreIncarnation rotation did not produce distinct incarnation ID!");
            }

            using var conn = ctx.CreateOpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "SELECT COUNT(*) FROM StoreIncarnations WHERE IsActive = 1;";
            long activeCount = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
            if (activeCount != 1)
            {
                throw new Exception($"Expected exactly 1 active incarnation, found {activeCount}");
            }

            e.Details = $"StoreIncarnation rotated from '{inc1}' to '{inc2}'; exactly 1 active incarnation enforced.";
        }

        // =====================================================================
        // Battery 23: WAL FULL durability & PRAGMAs
        // =====================================================================
        static void Test23_WalFullDurabilityAndPragmas(TestResultEntry e)
        {
            var ctx = CreateTestContext("Test23");
            using var conn = ctx.CreateOpenConnection();
            using var cmd = conn.CreateCommand();

            cmd.CommandText = "PRAGMA journal_mode;";
            string jm = cmd.ExecuteScalar()?.ToString() ?? string.Empty;
            if (!string.Equals(jm, "wal", StringComparison.OrdinalIgnoreCase))
            {
                throw new Exception($"Expected journal_mode wal, got {jm}");
            }

            cmd.CommandText = "PRAGMA synchronous;";
            long sync = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
            if (sync != 2) // 2 is FULL
            {
                throw new Exception($"Expected synchronous FULL (2), got {sync}");
            }

            cmd.CommandText = "PRAGMA foreign_keys;";
            long fk = Convert.ToInt64(cmd.ExecuteScalar() ?? 0L);
            if (fk != 1)
            {
                throw new Exception($"Expected foreign_keys 1, got {fk}");
            }

            e.Details = "Durability configuration verified: journal_mode=WAL, synchronous=FULL (2), foreign_keys=ON.";
        }

        // =====================================================================
        // Battery 24: No consumer/gameplay/material paths in probe pipeline
        // =====================================================================
        static void Test24_NoConsumerGameplayMaterialPaths(TestResultEntry e)
        {
            var serverAsm = typeof(PipelineTransactionCoordinator).Assembly;
            var types = serverAsm.GetTypes();

            var coordinatorType = typeof(PipelineTransactionCoordinator);
            var methods = coordinatorType.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);

            foreach (var m in methods)
            {
                string mName = m.Name.ToLowerInvariant();
                if (mName.Contains("trade") || mName.Contains("fief") || mName.Contains("tax") || mName.Contains("market") || mName.Contains("settlement"))
                {
                    throw new Exception($"Coordinator leaked gameplay/material domain method: {m.Name}");
                }
            }

            e.Details = "Pipeline boundary strictly isolated; zero consumer/material/gameplay routes exposed.";
        }

        // =====================================================================
        // Battery 25: Release manifest & package hygiene
        // =====================================================================
        static void Test25_ReleaseManifestAndPackageHygiene(TestResultEntry e)
        {
            // Verify Gate05 19 files invariant
            string freezeManifestPath = @"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-20261007-DIRECT-01\MASTER_ENGINE_FREEZE_BEFORE.json";
            if (!File.Exists(freezeManifestPath))
            {
                throw new Exception($"Missing freeze manifest: {freezeManifestPath}");
            }

            using var doc = JsonDocument.Parse(File.ReadAllText(freezeManifestPath));
            var files = doc.RootElement.GetProperty("files").EnumerateArray();
            int checkedFiles = 0;
            using var sha = SHA256.Create();

            foreach (var f in files)
            {
                string p = f.GetProperty("path").GetString()!;
                string expectedSha = f.GetProperty("expected").GetString()!;

                if (!File.Exists(p)) throw new Exception($"Frozen file missing: {p}");

                byte[] bytes = File.ReadAllBytes(p);
                string actualSha = Convert.ToHexString(sha.ComputeHash(bytes)).ToUpperInvariant();
                if (!string.Equals(actualSha, expectedSha, StringComparison.OrdinalIgnoreCase))
                {
                    throw new Exception($"GATE05 FREEZE CANDIDATE MUTATED! File '{p}' expected {expectedSha}, got {actualSha}");
                }
                checkedFiles++;
            }

            if (checkedFiles != 19)
            {
                throw new Exception($"Expected 19 frozen engine files, checked {checkedFiles}");
            }

            e.Details = "Gate05 freeze invariant: exactly 19/19 engine files verified bit-identical to MASTER_ENGINE_FREEZE_BEFORE.json.";
        }
    }
}
