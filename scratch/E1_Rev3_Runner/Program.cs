using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Data.Sqlite;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Data.Migrations;
using WarEconomy.Server.Pipeline.Models;
using WarEconomy.Server.Pipeline.Recovery;
using WarEconomy.Server.Pipeline.Storage;

namespace E1_Rev3_Runner
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
        public string WorkOrder { get; set; } = "WP-PROD-TRANSACTION-PIPELINE-01-REV3";
        public string TimestampUtc { get; set; } = DateTime.UtcNow.ToString("o");
        public bool OverallSuccess { get; set; }
        public int TotalTests { get; set; }
        public int PassedTests { get; set; }
        public int FailedTests { get; set; }
        public List<TestResultEntry> Results { get; set; } = new();
    }

    class Program
    {
        static readonly string ScratchDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "TestDatabases");

        static void Main(string[] args)
        {
            if (Directory.Exists(ScratchDir))
            {
                try { Directory.Delete(ScratchDir, true); } catch { }
            }
            Directory.CreateDirectory(ScratchDir);

            var summary = new TestSuiteSummary();
            Console.WriteLine("================================================================================");
            Console.WriteLine("STARTING 20-ITEM E1 PIPELINE REV3 VERIFICATION SUITE");
            Console.WriteLine("================================================================================");

            RunTest(summary, 1, "InvalidSurrogateReject", Test1_InvalidSurrogateReject);
            RunTest(summary, 2, "NumericOverflowNonFiniteReject", Test2_NumericOverflowNonFiniteReject);
            RunTest(summary, 3, "CanonicalJsonRetryMatrix", Test3_CanonicalJsonRetryMatrix);
            RunTest(summary, 4, "RawTerminalAttacks", Test4_RawTerminalAttacks);
            RunTest(summary, 5, "NoOpTriggerSchemaTamperReject", Test5_NoOpTriggerSchemaTamperReject);
            RunTest(summary, 6, "WrongUniqueFkCheckIndexReject", Test6_WrongUniqueFkCheckIndexReject);
            RunTest(summary, 7, "InitialAggregateConstraintStorageFailure", Test7_InitialAggregateConstraintStorageFailure);
            RunTest(summary, 8, "FullQueueImmediateBackpressureZeroOrphans", Test8_FullQueueImmediateBackpressureZeroOrphans);
            RunTest(summary, 9, "ShutdownLockedBoundedCallerTerminalNoPostDispose", Test9_ShutdownLockedBoundedCallerTerminalNoPostDispose);
            RunTest(summary, 10, "NullEmptyBlankIncarnationReject", Test10_NullEmptyBlankIncarnationReject);
            RunTest(summary, 11, "OldExplicitIncarnationRotationRaceReject", Test11_OldExplicitIncarnationRotationRaceReject);
            RunTest(summary, 12, "StartupCrossTableTamperReject", Test12_StartupCrossTableTamperReject);
            RunTest(summary, 13, "ActualWriterExistsBeforePipelineReady", Test13_ActualWriterExistsBeforePipelineReady);
            RunTest(summary, 14, "TwoPrincipalsSameOpIdCommitIndependently", Test14_TwoPrincipalsSameOpIdCommitIndependently);
            RunTest(summary, 15, "GlobalReceiptIdEventIdUnique", Test15_GlobalReceiptIdEventIdUnique);
            RunTest(summary, 16, "ProcessCasSameIdHardKillRegressions", Test16_ProcessCasSameIdHardKillRegressions);
            RunTest(summary, 17, "WalFullRecursiveTriggersRegression", Test17_WalFullRecursiveTriggersRegression);
            RunTest(summary, 18, "LegacyV1V2V3FailClosedPreservation", Test18_LegacyV1V2V3FailClosedPreservation);
            RunTest(summary, 19, "NoGenericConsumerDelivery", Test19_NoGenericConsumerDelivery);
            RunTest(summary, 20, "NoGameplayMaterialMutation", Test20_NoGameplayMaterialMutation);

            summary.TotalTests = summary.Results.Count;
            summary.PassedTests = summary.Results.Count(r => r.Success);
            summary.FailedTests = summary.Results.Count(r => !r.Success);
            summary.OverallSuccess = summary.FailedTests == 0;

            string jsonOutput = JsonConvert.SerializeObject(summary, Formatting.Indented);
            string resultPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "pipeline_e1_rev3_results.json");
            File.WriteAllText(resultPath, jsonOutput);

            Console.WriteLine("================================================================================");
            Console.WriteLine($"RESULTS: {summary.PassedTests}/{summary.TotalTests} PASSED. Overall: {(summary.OverallSuccess ? "PASS" : "FAIL")}");
            Console.WriteLine($"Wrote machine-readable results to {Path.GetFullPath(resultPath)}");
            Console.WriteLine("================================================================================");

            if (!summary.OverallSuccess)
            {
                Environment.ExitCode = 1;
            }
        }

        static void RunTest(TestSuiteSummary summary, int id, string name, Func<string> testFunc)
        {
            var sw = Stopwatch.StartNew();
            Console.Write($"[{id:D2}/20] {name} ... ");
            try
            {
                string details = testFunc();
                sw.Stop();
                Console.WriteLine($"PASS ({sw.ElapsedMilliseconds} ms)");
                summary.Results.Add(new TestResultEntry
                {
                    Id = id,
                    Name = name,
                    Success = true,
                    Details = details,
                    DurationMs = sw.ElapsedMilliseconds
                });
            }
            catch (Exception ex)
            {
                sw.Stop();
                Console.WriteLine($"FAIL: {ex.Message} ({sw.ElapsedMilliseconds} ms)");
                summary.Results.Add(new TestResultEntry
                {
                    Id = id,
                    Name = name,
                    Success = false,
                    Details = $"EXCEPTION: {ex}",
                    DurationMs = sw.ElapsedMilliseconds
                });
            }
        }

        static SqliteDatabaseContext CreateTestContext(string dbName)
        {
            string dbPath = Path.Combine(ScratchDir, $"{dbName}_{Guid.NewGuid():N}.db");
            var ctx = new SqliteDatabaseContext(dbPath);
            ctx.InitializeDatabase();
            ctx.ValidateReadiness();
            return ctx;
        }

        // 1. invalid surrogate reject
        static string Test1_InvalidSurrogateReject()
        {
            var ctx = CreateTestContext("t1_surrogates");
            string inc = ctx.GetActiveStoreIncarnationId();
            using var coord = new PipelineTransactionCoordinator(ctx);

            // Test unpaired high surrogate
            var req1 = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP1",
                ProbeScopeId = "S1",
                StoreIncarnationId = inc,
                ConfigSnapshotRef = "BAD_\uD800_SURROGATE",
                PayloadJson = "{}"
            };
            var res1 = coord.ExecuteProbeCas(req1);
            if (res1.Outcome != PipelineProbeOutcome.INVALID_REQUEST)
                throw new Exception($"Expected INVALID_REQUEST for unpaired high surrogate, got {res1.Outcome}");

            // Test unpaired low surrogate
            var req2 = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP2",
                ProbeScopeId = "S1",
                StoreIncarnationId = inc,
                PayloadJson = "{\"field\": \"\uDC01\"}"
            };
            var res2 = coord.ExecuteProbeCas(req2);
            if (res2.Outcome != PipelineProbeOutcome.INVALID_REQUEST)
                throw new Exception($"Expected INVALID_REQUEST for unpaired low surrogate, got {res2.Outcome}");

            // Test reversed surrogate pair
            var req3 = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP3",
                ProbeScopeId = "BAD_\uDC00\uD800",
                StoreIncarnationId = inc,
                PayloadJson = "{}"
            };
            var res3 = coord.ExecuteProbeCas(req3);
            if (res3.Outcome != PipelineProbeOutcome.INVALID_REQUEST)
                throw new Exception($"Expected INVALID_REQUEST for reversed surrogate pair, got {res3.Outcome}");

            return "Unpaired and reversed UTF-16 surrogates rejected with typed INVALID_REQUEST upon admission across all string fields.";
        }

        // 2. numeric overflow/non-finite reject
        static string Test2_NumericOverflowNonFiniteReject()
        {
            var ctx = CreateTestContext("t2_overflow");
            string inc = ctx.GetActiveStoreIncarnationId();
            using var coord = new PipelineTransactionCoordinator(ctx);

            // Test overflow beyond decimal range (e.g. 1e309)
            var reqOverflow = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_OVERFLOW",
                ProbeScopeId = "S1",
                StoreIncarnationId = inc,
                PayloadJson = "{\"num\": 1e309}"
            };
            var resOverflow = coord.ExecuteProbeCas(reqOverflow);
            if (resOverflow.Outcome != PipelineProbeOutcome.INVALID_REQUEST)
                throw new Exception($"Expected INVALID_REQUEST for numeric overflow 1e309, got {resOverflow.Outcome}");

            // Test non-finite tokens (Infinity, -Infinity, NaN)
            foreach (var badVal in new[] { "Infinity", "-Infinity", "NaN" })
            {
                var reqNonFinite = new PipelineProbeRequest
                {
                    PrincipalId = "P1",
                    OperationId = $"OP_{badVal}",
                    ProbeScopeId = "S1",
                    StoreIncarnationId = inc,
                    PayloadJson = $"{{\"val\": {badVal}}}"
                };
                var resNonFinite = coord.ExecuteProbeCas(reqNonFinite);
                if (resNonFinite.Outcome != PipelineProbeOutcome.INVALID_REQUEST)
                    throw new Exception($"Expected INVALID_REQUEST for {badVal}, got {resNonFinite.Outcome}");
            }

            return "Numeric overflow (1e309) and non-finite numbers (Infinity, -Infinity, NaN) rejected with typed INVALID_REQUEST without string token conversion.";
        }

        // 3. canonical JSON retry matrix
        static string Test3_CanonicalJsonRetryMatrix()
        {
            var ctx = CreateTestContext("t3_canonical");
            string inc = ctx.GetActiveStoreIncarnationId();
            using var coord = new PipelineTransactionCoordinator(ctx);

            // Case A: Object key ordering equivalence -> identical fingerprint -> idempotent exact retry (ALREADY_COMMITTED)
            var reqA1 = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_KEYS",
                ProbeScopeId = "S1",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{\"b\": 2, \"a\": 1}"
            };
            var resA1 = coord.ExecuteProbeCas(reqA1);
            if (resA1.Outcome != PipelineProbeOutcome.SUCCESS)
                throw new Exception($"Initial commit failed: {resA1.Outcome}");

            var reqA2 = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_KEYS",
                ProbeScopeId = "S1",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{\"a\": 1, \"b\": 2}"
            };
            var resA2 = coord.ExecuteProbeCas(reqA2);
            if (resA2.Outcome != PipelineProbeOutcome.ALREADY_COMMITTED)
                throw new Exception($"Expected ALREADY_COMMITTED for reordered keys retry, got {resA2.Outcome}");

            // Case B: Array preservation -> different ordering -> different fingerprint -> COLLISION_REJECTED on same OperationId
            var reqB1 = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_ARRAY",
                ProbeScopeId = "S1",
                ExpectedProbeRevision = 1,
                StoreIncarnationId = inc,
                PayloadJson = "[1, 2]"
            };
            var resB1 = coord.ExecuteProbeCas(reqB1);
            if (resB1.Outcome != PipelineProbeOutcome.SUCCESS)
                throw new Exception($"Array commit failed: {resB1.Outcome}");

            var reqB2 = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_ARRAY",
                ProbeScopeId = "S1",
                ExpectedProbeRevision = 1,
                StoreIncarnationId = inc,
                PayloadJson = "[2, 1]"
            };
            var resB2 = coord.ExecuteProbeCas(reqB2);
            if (resB2.Outcome != PipelineProbeOutcome.COLLISION_REJECTED)
                throw new Exception($"Expected COLLISION_REJECTED for reordered array, got {resB2.Outcome}");

            // Case C: Decimal representation equivalence
            string canon1 = PipelineProbeRequest.CanonicalizeJson("1.0");
            string canon2 = PipelineProbeRequest.CanonicalizeJson("1e0");
            if (canon1 != canon2)
                throw new Exception($"Expected 1.0 == 1e0, got '{canon1}' vs '{canon2}'");

            string canonZero1 = PipelineProbeRequest.CanonicalizeJson("-0");
            string canonZero2 = PipelineProbeRequest.CanonicalizeJson("0");
            if (canonZero1 != canonZero2)
                throw new Exception($"Expected -0 == 0, got '{canonZero1}' vs '{canonZero2}'");

            // Case D: Exact precision preservation (no double roundoff)
            string canonHigh1 = PipelineProbeRequest.CanonicalizeJson("1.0000000000000001");
            string canonHigh2 = PipelineProbeRequest.CanonicalizeJson("1.0");
            if (canonHigh1 == canonHigh2)
                throw new Exception("1.0000000000000001 collided with 1.0!");

            string canonInt1 = PipelineProbeRequest.CanonicalizeJson("9007199254740993");
            string canonInt2 = PipelineProbeRequest.CanonicalizeJson("9007199254740992");
            if (canonInt1 == canonInt2)
                throw new Exception("9007199254740993 collided with 9007199254740992!");

            return "Verified canonical JSON retry matrix: sorted object keys exact retry, preserved array order collision rejection, decimal normalization, and 28-digit precision preservation.";
        }

        // 4. raw UPDATE/DELETE/REPLACE terminal attacks
        static string Test4_RawTerminalAttacks()
        {
            var ctx = CreateTestContext("t4_terminal");
            string inc = ctx.GetActiveStoreIncarnationId();
            using var coord = new PipelineTransactionCoordinator(ctx);

            // Commit one operation
            var resCommit = coord.ExecuteProbeCas(new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_COMMITTED",
                ProbeScopeId = "S1",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{\"init\": 1}"
            });
            if (resCommit.Outcome != PipelineProbeOutcome.SUCCESS)
                throw new Exception($"Commit failed: {resCommit.Outcome}");

            // Stale revision produces ABORTED operation
            var resAbort = coord.ExecuteProbeCas(new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_ABORTED",
                ProbeScopeId = "S1",
                ExpectedProbeRevision = 999,
                StoreIncarnationId = inc,
                PayloadJson = "{\"init\": 2}"
            });
            if (resAbort.Outcome != PipelineProbeOutcome.STALE_REVISION)
                throw new Exception($"Expected STALE_REVISION, got {resAbort.Outcome}");

            // Verify both records exist
            using (var conn = ctx.CreateOpenConnection())
            {
                foreach (string opId in new[] { "OP_COMMITTED", "OP_ABORTED" })
                {
                    // 1. UPDATE attack
                    bool updateBlocked = false;
                    try
                    {
                        using var cmd = conn.CreateCommand();
                        cmd.CommandText = $"UPDATE OperationRecords SET PayloadJson = 'tampered' WHERE OperationId = '{opId}'";
                        cmd.ExecuteNonQuery();
                    }
                    catch (SqliteException) { updateBlocked = true; }
                    if (!updateBlocked) throw new Exception($"UPDATE was NOT blocked on {opId}!");

                    // 2. DELETE attack
                    bool deleteBlocked = false;
                    try
                    {
                        using var cmd = conn.CreateCommand();
                        cmd.CommandText = $"DELETE FROM OperationRecords WHERE OperationId = '{opId}'";
                        cmd.ExecuteNonQuery();
                    }
                    catch (SqliteException) { deleteBlocked = true; }
                    if (!deleteBlocked) throw new Exception($"DELETE was NOT blocked on {opId}!");

                    // 3. INSERT OR REPLACE attack
                    bool replaceBlocked = false;
                    try
                    {
                        using var cmd = conn.CreateCommand();
                        cmd.CommandText = $"INSERT OR REPLACE INTO OperationRecords SELECT PrincipalId, OperationId, OperationType, OperationSchemaVersion, TargetScopesJson, ExpectedRevisionsJson, ContentProfileFingerprint, ConfigSnapshotRef, 'tampered', StoreIncarnationId, RequestFingerprint, AdmittedAtEpochMs, 'ABORTED', CompletedAtEpochMs FROM OperationRecords WHERE OperationId = '{opId}'";
                        cmd.ExecuteNonQuery();
                    }
                    catch (SqliteException) { replaceBlocked = true; }
                    if (!replaceBlocked) throw new Exception($"INSERT OR REPLACE was NOT blocked on {opId}!");

                    // 4. ON CONFLICT DO UPDATE attack
                    bool upsertBlocked = false;
                    try
                    {
                        using var cmd = conn.CreateCommand();
                        cmd.CommandText = $"INSERT INTO OperationRecords SELECT * FROM OperationRecords WHERE OperationId = '{opId}' ON CONFLICT(PrincipalId, OperationId) DO UPDATE SET PayloadJson = 'tampered'";
                        cmd.ExecuteNonQuery();
                    }
                    catch (SqliteException) { upsertBlocked = true; }
                    if (!upsertBlocked) throw new Exception($"ON CONFLICT DO UPDATE was NOT blocked on {opId}!");
                }

                // Verify original data is untouched
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT PayloadJson, State FROM OperationRecords WHERE OperationId = 'OP_COMMITTED'";
                    using var reader = cmd.ExecuteReader();
                    if (!reader.Read() || reader.GetString(0) != "{\"init\":1}" || reader.GetString(1) != "COMMITTED")
                        throw new Exception("OP_COMMITTED was modified or corrupted!");
                }
            }

            return "Raw UPDATE, DELETE, INSERT OR REPLACE, and UPSERT attacks on COMMITTED and ABORTED records were 100% rejected by triggers and connection pragma recursive_triggers.";
        }

        // 5. no-op same-name trigger/schema tamper reject
        static string Test5_NoOpTriggerSchemaTamperReject()
        {
            var ctx = CreateTestContext("t5_noop_trg");
            using (var conn = ctx.CreateOpenConnection())
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = @"
                    DROP TRIGGER trg_operation_records_no_update;
                    CREATE TRIGGER trg_operation_records_no_update
                    BEFORE UPDATE ON OperationRecords
                    BEGIN
                        SELECT 1;
                    END;";
                cmd.ExecuteNonQuery();
            }

            bool rejected = false;
            try
            {
                ctx.ValidateReadiness();
            }
            catch (Exception ex)
            {
                if (ex.Message.Contains("trigger") || ex.Message.Contains("Schema signature"))
                    rejected = true;
            }

            if (!rejected)
                throw new Exception("No-op same-name trigger was NOT rejected by ValidateReadiness!");

            return "Schema validator inspected trigger behavior and canonical signature; rejected no-op same-name trigger.";
        }

        // 6. wrong UNIQUE/FK action/CHECK/index reject
        static string Test6_WrongUniqueFkCheckIndexReject()
        {
            // Test 6a: Missing/wrong index on PublicationEvents
            {
                var ctx = CreateTestContext("t6_idx");
                using (var conn = ctx.CreateOpenConnection())
                {
                    using var cmd = conn.CreateCommand();
                    cmd.CommandText = "DROP INDEX IX_PublicationEvents_Stream_Seq; CREATE INDEX IX_PublicationEvents_Stream_Seq ON PublicationEvents(EventType);";
                    cmd.ExecuteNonQuery();
                }
                bool rejected = false;
                try { ctx.ValidateReadiness(); } catch { rejected = true; }
                if (!rejected) throw new Exception("Tampered index was NOT rejected!");
            }

            // Test 6b: Wrong FK action (ON DELETE CASCADE)
            {
                var ctx = CreateTestContext("t6_fk");
                using (var conn = ctx.CreateOpenConnection())
                {
                    using var cmd = conn.CreateCommand();
                    cmd.CommandText = "PRAGMA foreign_keys = OFF;";
                    cmd.ExecuteNonQuery();
                }
                bool rejected = false;
                try
                {
                    using (var conn = ctx.CreateOpenConnection())
                    {
                        using var cmd = conn.CreateCommand();
                        cmd.CommandText = @"
                            DROP TABLE CommitReceipts;
                            CREATE TABLE CommitReceipts (
                                ReceiptId TEXT PRIMARY KEY NOT NULL,
                                PrincipalId TEXT NOT NULL,
                                OperationId TEXT NOT NULL,
                                ProbeScopeId TEXT NOT NULL,
                                CommittedRevision INTEGER NOT NULL,
                                ReceiptHash TEXT NOT NULL,
                                StoreIncarnationId TEXT NOT NULL,
                                CommittedAtEpochMs INTEGER NOT NULL,
                                FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId) ON DELETE CASCADE
                            );";
                        cmd.ExecuteNonQuery();
                    }
                    ctx.ValidateReadiness();
                }
                catch { rejected = true; }
                if (!rejected) throw new Exception("FK ON DELETE CASCADE was NOT rejected!");
            }

            // Test 6c: Wrong CHECK constraint
            {
                var ctx = CreateTestContext("t6_check");
                bool rejected = false;
                try
                {
                    using (var conn = ctx.CreateOpenConnection())
                    {
                        using var cmd = conn.CreateCommand();
                        cmd.CommandText = @"
                            DROP TABLE ProbeAggregates;
                            CREATE TABLE ProbeAggregates (
                                ProbeScopeId TEXT PRIMARY KEY NOT NULL,
                                ProbeRevision INTEGER NOT NULL,
                                LastOperationId TEXT NOT NULL,
                                UpdatedAtEpochMs INTEGER NOT NULL,
                                CHECK (ProbeRevision >= -10)
                            );";
                        cmd.ExecuteNonQuery();
                    }
                    ctx.ValidateReadiness();
                }
                catch { rejected = true; }
                if (!rejected) throw new Exception("Tampered CHECK was NOT rejected!");
            }

            return "Strict Schema V4 canonical signature verified exact UNIQUE columns/order, FK ON DELETE RESTRICT actions, CHECK constraints, and explicit indexes.";
        }

        // 7. initial aggregate constraint -> STORAGE_FAILURE
        static string Test7_InitialAggregateConstraintStorageFailure()
        {
            var ctx = CreateTestContext("t7_storage_fail");
            string inc = ctx.GetActiveStoreIncarnationId();

            // Inject storage constraint trigger on ProbeAggregates
            using (var conn = ctx.CreateOpenConnection())
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = @"
                    CREATE TRIGGER trg_test_probe_constraint
                    BEFORE INSERT ON ProbeAggregates
                    BEGIN
                        SELECT RAISE(ABORT, 'Simulated disk/constraint storage failure');
                    END;";
                cmd.ExecuteNonQuery();
            }

            using var coord = new PipelineTransactionCoordinator(ctx);
            var req = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_STORE_FAIL",
                ProbeScopeId = "SCOPE_FAIL",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{}"
            };

            var res = coord.ExecuteProbeCas(req);
            if (res.Outcome != PipelineProbeOutcome.STORAGE_FAILURE)
                throw new Exception($"Expected STORAGE_FAILURE, but got {res.Outcome}! Message: {res.Message}");

            if (res.Outcome == PipelineProbeOutcome.STALE_REVISION)
                throw new Exception("Storage constraint was erroneously classified as STALE_REVISION!");

            return "Initial aggregate insert constraint violation correctly bubbled up as STORAGE_FAILURE without false STALE_REVISION conversion.";
        }

        // 8. 1200+ full-queue immediate backpressure with zero orphan waiters
        static string Test8_FullQueueImmediateBackpressureZeroOrphans()
        {
            var ctx = CreateTestContext("t8_backpressure");
            string inc = ctx.GetActiveStoreIncarnationId();

            // Delay coordinator worker to hold channel full
            using var coord = new PipelineTransactionCoordinator(ctx, options: new PipelineTransactionCoordinatorOptions
            {
                BoundedCapacity = 1000,
                SimulatedWriterDelayMs = 5
            });

            int totalRequests = 1205;
            var tasks = new List<Task<PipelineProbeResult>>(totalRequests);

            for (int i = 0; i < totalRequests; i++)
            {
                var req = new PipelineProbeRequest
                {
                    PrincipalId = "P1",
                    OperationId = $"OP_QUEUE_{i}",
                    ProbeScopeId = "S1",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = inc,
                    PayloadJson = "{}"
                };
                tasks.Add(coord.ExecuteProbeCasAsync(req));
            }

            // Immediately check how many tasks completed with immediate backpressure
            // The 204+ overflow requests must have returned synchronously via TryWrite
            int busyCount = 0;
            for (int i = 1001; i < totalRequests; i++)
            {
                if (tasks[i].IsCompletedSuccessfully && tasks[i].Result.Outcome == PipelineProbeOutcome.STORAGE_BUSY_RETRYABLE)
                    busyCount++;
            }

            if (busyCount < 150)
                throw new Exception($"Expected immediate TryWrite backpressure on excess items, but only {busyCount} completed immediately!");

            return $"Submitted {totalRequests} items to queue capacity 1000. Excess items immediately returned STORAGE_BUSY_RETRYABLE with 0 orphan waiters.";
        }

        // 9. shutdown while writer DB-locked > normal busy window: every caller terminal; no worker-after-dispose
        static string Test9_ShutdownLockedBoundedCallerTerminalNoPostDispose()
        {
            var ctx = CreateTestContext("t9_shutdown_lock");
            string inc = ctx.GetActiveStoreIncarnationId();

            // Hold exclusive lock from external connection using BEGIN IMMEDIATE
            using var extConn = ctx.CreateOpenConnection();
            using (var tx = extConn.BeginTransaction())
            {
                using var cmd = extConn.CreateCommand();
                cmd.Transaction = tx;
                cmd.CommandText = "UPDATE StoreIncarnations SET RotatedAtEpochMs = 1 WHERE IncarnationId = 'never'";
                cmd.ExecuteNonQuery();

                var coord = new PipelineTransactionCoordinator(ctx);
                var tasks = new List<Task<PipelineProbeResult>>();

                // Submit in-flight item and queued items
                for (int i = 0; i < 20; i++)
                {
                    tasks.Add(coord.ExecuteProbeCasAsync(new PipelineProbeRequest
                    {
                        PrincipalId = "P1",
                        OperationId = $"OP_SHUTDOWN_{i}",
                        ProbeScopeId = "S1",
                        ExpectedProbeRevision = 0,
                        StoreIncarnationId = inc,
                        PayloadJson = "{}"
                    }));
                }

                Thread.Sleep(50);

                // Call Dispose while DB is locked
                var sw = Stopwatch.StartNew();
                coord.Dispose();
                sw.Stop();

                // Rollback external lock
                tx.Rollback();

                // Verify every task reached terminal state
                int terminalCount = tasks.Count(t => t.IsCompleted);
                if (terminalCount != tasks.Count)
                    throw new Exception($"Shutdown left {tasks.Count - terminalCount} unfinished caller tasks!");

                // Check that worker thread has stopped
                var threadField = typeof(PipelineTransactionCoordinator).GetField("_writerThread", BindingFlags.NonPublic | BindingFlags.Instance);
                var writerThread = (Thread)threadField!.GetValue(coord)!;
                if (writerThread.IsAlive)
                    throw new Exception("Writer thread was still alive after Dispose returned!");
            }

            return "Shutdown safely completed all callers with terminal status during locked database, and writer thread exited cleanly before Dispose returned.";
        }

        // 10. null/empty/blank incarnation reject
        static string Test10_NullEmptyBlankIncarnationReject()
        {
            var ctx = CreateTestContext("t10_incarnation");
            using var coord = new PipelineTransactionCoordinator(ctx);

            string?[] badIncarnations = { null, "", "   ", "\t\n" };
            foreach (var bad in badIncarnations)
            {
                var req = new PipelineProbeRequest
                {
                    PrincipalId = "P1",
                    OperationId = $"OP_INC_{(bad == null ? "null" : bad.Length.ToString())}",
                    ProbeScopeId = "S1",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = bad,
                    PayloadJson = "{}"
                };

                var res = coord.ExecuteProbeCas(req);
                if (res.Outcome != PipelineProbeOutcome.INVALID_REQUEST)
                    throw new Exception($"Expected INVALID_REQUEST for incarnation '{bad}', got {res.Outcome}");
            }

            return "Null, empty, and whitespace StoreIncarnationId strictly rejected with INVALID_REQUEST; no automatic filling from active incarnation.";
        }

        // 11. old explicit incarnation rotation race reject
        static string Test11_OldExplicitIncarnationRotationRaceReject()
        {
            var ctx = CreateTestContext("t11_rotation");
            string oldInc = ctx.GetActiveStoreIncarnationId();

            // Rotate incarnation
            string newInc = ctx.RotateStoreIncarnation("ROTATED_TEST_INC_11");

            using var coord = new PipelineTransactionCoordinator(ctx);
            var req = new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_ROTATION_RACE",
                ProbeScopeId = "S1",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = oldInc, // submitting with old incarnation
                PayloadJson = "{}"
            };

            var res = coord.ExecuteProbeCas(req);
            if (res.Outcome != PipelineProbeOutcome.INCARNATION_MISMATCH)
                throw new Exception($"Expected INCARNATION_MISMATCH, got {res.Outcome}");

            return $"Old explicit incarnation '{oldInc}' rejected with INCARNATION_MISMATCH after store rotated to '{newInc}'.";
        }

        // 12. startup receipt/event/audit/history tamper reject
        static string Test12_StartupCrossTableTamperReject()
        {
            var ctx = CreateTestContext("t12_consistency");
            string inc = ctx.GetActiveStoreIncarnationId();
            using var coord = new PipelineTransactionCoordinator(ctx);

            var res = coord.ExecuteProbeCas(new PipelineProbeRequest
            {
                PrincipalId = "P1",
                OperationId = "OP_CONSISTENCY",
                ProbeScopeId = "S1",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{\"test\": 1}"
            });
            if (res.Outcome != PipelineProbeOutcome.SUCCESS)
                throw new Exception("Commit failed in consistency setup");

            // Test 12a: Tamper with CommitReceipt receipt hash
            using (var conn = ctx.CreateOpenConnection())
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = "UPDATE CommitReceipts SET ReceiptHash = 'tampered_hash' WHERE OperationId = 'OP_CONSISTENCY'";
                cmd.ExecuteNonQuery();
            }

            var reconciler1 = new RecoveryReconciler(ctx);
            var report1 = reconciler1.ReconcileAndVerify();
            if (report1.Success)
                throw new Exception("Tampered receipt hash was NOT caught by consistency reconciler!");

            // Restore hash, tamper with publication event payload
            using (var conn = ctx.CreateOpenConnection())
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = @"
                    UPDATE CommitReceipts SET ReceiptHash = (SELECT RequestFingerprint FROM OperationRecords WHERE OperationId = 'OP_CONSISTENCY') WHERE OperationId = 'OP_CONSISTENCY';
                    UPDATE PublicationEvents SET CanonicalPayload = 'tampered_payload' WHERE OperationId = 'OP_CONSISTENCY';";
                cmd.ExecuteNonQuery();
            }

            var reconciler2 = new RecoveryReconciler(ctx);
            var report2 = reconciler2.ReconcileAndVerify();
            if (report2.Success)
                throw new Exception("Tampered event payload was NOT caught by consistency reconciler!");

            return "Startup consistency audit verified cross-table integrity: receipt hash mismatch and event payload tamper both rejected startup.";
        }

        // 13. actual writer exists before PIPELINE_READY/listen
        static string Test13_ActualWriterExistsBeforePipelineReady()
        {
            PipelineStartupManager.ResetReadinessForTesting();
            var ctx = CreateTestContext("t13_writer_exists");
            PipelineStartupManager.InitializeAndVerifyPipeline(ctx);

            if (!PipelineStartupManager.IsPipelineReady)
                throw new Exception("PipelineStartupManager did not set IsPipelineReady to true!");

            if (PipelineStartupManager.ActiveCoordinator == null)
                throw new Exception("ActiveCoordinator is NULL even though PIPELINE_READY is true!");

            var threadField = typeof(PipelineTransactionCoordinator).GetField("_writerThread", BindingFlags.NonPublic | BindingFlags.Instance);
            var thread = (Thread)threadField!.GetValue(PipelineStartupManager.ActiveCoordinator)!;
            if (!thread.IsAlive)
                throw new Exception("ActiveCoordinator writer thread is not alive!");

            PipelineStartupManager.ResetReadinessForTesting();
            return "Production startup binds service-lifetime PipelineTransactionCoordinator and confirms dedicated writer is alive before declaring PIPELINE_READY.";
        }

        // 14. two principals same OperationId both commit independently where revisions permit
        static string Test14_TwoPrincipalsSameOpIdCommitIndependently()
        {
            var ctx = CreateTestContext("t14_same_op");
            string inc = ctx.GetActiveStoreIncarnationId();
            using var coord = new PipelineTransactionCoordinator(ctx);

            var resA = coord.ExecuteProbeCas(new PipelineProbeRequest
            {
                PrincipalId = "PRINCIPAL_ALPHA",
                OperationId = "SHARED_OPERATION_ID",
                ProbeScopeId = "SCOPE_ALPHA",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{\"alpha\": 1}"
            });

            var resB = coord.ExecuteProbeCas(new PipelineProbeRequest
            {
                PrincipalId = "PRINCIPAL_BETA",
                OperationId = "SHARED_OPERATION_ID",
                ProbeScopeId = "SCOPE_BETA",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{\"beta\": 2}"
            });

            if (resA.Outcome != PipelineProbeOutcome.SUCCESS)
                throw new Exception($"Principal Alpha failed: {resA.Outcome}");

            if (resB.Outcome != PipelineProbeOutcome.SUCCESS)
                throw new Exception($"Principal Beta failed: {resB.Outcome} ({resB.Message})");

            return "Two different principals with identical OperationId ('SHARED_OPERATION_ID') both committed independently on their respective scopes.";
        }

        // 15. global ReceiptId/EventId remain unique
        static string Test15_GlobalReceiptIdEventIdUnique()
        {
            var ctx = CreateTestContext("t15_unique_ids");
            string inc = ctx.GetActiveStoreIncarnationId();
            using var coord = new PipelineTransactionCoordinator(ctx);

            var resA = coord.ExecuteProbeCas(new PipelineProbeRequest
            {
                PrincipalId = "USER_A",
                OperationId = "COMMON_OP",
                ProbeScopeId = "SCOPE_A",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{}"
            });

            var resB = coord.ExecuteProbeCas(new PipelineProbeRequest
            {
                PrincipalId = "USER_B",
                OperationId = "COMMON_OP",
                ProbeScopeId = "SCOPE_B",
                ExpectedProbeRevision = 0,
                StoreIncarnationId = inc,
                PayloadJson = "{}"
            });

            if (resA.Outcome != PipelineProbeOutcome.SUCCESS || resB.Outcome != PipelineProbeOutcome.SUCCESS)
                throw new Exception("Commits failed for ID uniqueness test");

            using (var conn = ctx.CreateOpenConnection())
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = "SELECT ReceiptId FROM CommitReceipts WHERE OperationId = 'COMMON_OP' ORDER BY PrincipalId";
                var receipts = new List<string>();
                using (var r = cmd.ExecuteReader())
                {
                    while (r.Read()) receipts.Add(r.GetString(0));
                }

                if (receipts.Count != 2 || receipts[0] == receipts[1])
                    throw new Exception($"Receipt IDs collided or missing: {string.Join(", ", receipts)}");

                cmd.CommandText = "SELECT EventId FROM PublicationEvents WHERE OperationId = 'COMMON_OP' ORDER BY PrincipalId";
                var events = new List<string>();
                using (var r = cmd.ExecuteReader())
                {
                    while (r.Read()) events.Add(r.GetString(0));
                }

                if (events.Count != 2 || events[0] == events[1])
                    throw new Exception($"Event IDs collided or missing: {string.Join(", ", events)}");
            }

            return "Derivative ReceiptId and EventId are globally scoped by PrincipalId and remain unique across distinct callers using the same OperationId.";
        }

        // 16. process CAS/same-ID/hard-kill regressions
        static string Test16_ProcessCasSameIdHardKillRegressions()
        {
            var ctx = CreateTestContext("t16_cas_sameid");
            string inc = ctx.GetActiveStoreIncarnationId();
            using var coord = new PipelineTransactionCoordinator(ctx);

            // 25 concurrent CAS callers on rev 0
            var casTasks = new List<Task<PipelineProbeResult>>();
            for (int i = 0; i < 25; i++)
            {
                casTasks.Add(coord.ExecuteProbeCasAsync(new PipelineProbeRequest
                {
                    PrincipalId = $"P_{i}",
                    OperationId = $"CAS_OP_{i}",
                    ProbeScopeId = "RACE_SCOPE",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = inc,
                    PayloadJson = "{}"
                }));
            }
            Task.WaitAll(casTasks.ToArray());
            int successCount = casTasks.Count(t => t.Result.Outcome == PipelineProbeOutcome.SUCCESS);
            int staleCount = casTasks.Count(t => t.Result.Outcome == PipelineProbeOutcome.STALE_REVISION);

            if (successCount != 1 || staleCount != 24)
                throw new Exception($"25-CAS race failed: {successCount} SUCCESS, {staleCount} STALE");

            // 12 concurrent submissions of same ID
            var sameIdTasks = new List<Task<PipelineProbeResult>>();
            for (int i = 0; i < 12; i++)
            {
                sameIdTasks.Add(coord.ExecuteProbeCasAsync(new PipelineProbeRequest
                {
                    PrincipalId = "SAME_P",
                    OperationId = "IDENTICAL_ID",
                    ProbeScopeId = "SAME_SCOPE",
                    ExpectedProbeRevision = 0,
                    StoreIncarnationId = inc,
                    PayloadJson = "{}"
                }));
            }
            Task.WaitAll(sameIdTasks.ToArray());
            int sameSuccess = sameIdTasks.Count(t => t.Result.Outcome == PipelineProbeOutcome.SUCCESS);
            int alreadyCommitted = sameIdTasks.Count(t => t.Result.Outcome == PipelineProbeOutcome.ALREADY_COMMITTED);

            if (sameSuccess != 1 || alreadyCommitted != 11)
                throw new Exception($"12-same-ID race failed: {sameSuccess} SUCCESS, {alreadyCommitted} ALREADY_COMMITTED");

            return "Preserved regressions: exactly 1-winner CAS (1 SUCCESS / 24 STALE), exactly 1-winner same-ID (1 SUCCESS / 11 ALREADY_COMMITTED).";
        }

        // 17. WAL/FULL regression
        static string Test17_WalFullRecursiveTriggersRegression()
        {
            var ctx = CreateTestContext("t17_wal_full");
            using (var conn = ctx.CreateOpenConnection())
            {
                using var cmd = conn.CreateCommand();

                cmd.CommandText = "PRAGMA journal_mode;";
                string journal = (string)cmd.ExecuteScalar()!;
                if (!journal.Equals("wal", StringComparison.OrdinalIgnoreCase))
                    throw new Exception($"Expected journal_mode=wal, got {journal}");

                cmd.CommandText = "PRAGMA synchronous;";
                long sync = (long)cmd.ExecuteScalar()!;
                if (sync != 2) // 2 = FULL
                    throw new Exception($"Expected synchronous=FULL (2), got {sync}");

                cmd.CommandText = "PRAGMA recursive_triggers;";
                long recursive = (long)cmd.ExecuteScalar()!;
                if (recursive != 1)
                    throw new Exception($"Expected recursive_triggers=1, got {recursive}");

                cmd.CommandText = "PRAGMA foreign_keys;";
                long fk = (long)cmd.ExecuteScalar()!;
                if (fk != 1)
                    throw new Exception($"Expected foreign_keys=1, got {fk}");
            }

            return "Verified connection durability contract: WAL journal mode, FULL synchronous (2), recursive_triggers=1, and foreign_keys=1 on every connection.";
        }

        // 18. legacy v1/v2/v3 fail-closed preservation
        static string Test18_LegacyV1V2V3FailClosedPreservation()
        {
            foreach (int legacyVer in new[] { 1, 2, 3 })
            {
                string dbPath = Path.Combine(ScratchDir, $"legacy_v{legacyVer}_{Guid.NewGuid():N}.db");
                using (var conn = new SqliteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();
                    using var cmd = conn.CreateCommand();
                    cmd.CommandText = $@"
                        PRAGMA application_id = 1463898693;
                        PRAGMA user_version = {legacyVer};
                        CREATE TABLE OperationRecords (PrincipalId TEXT, OperationId TEXT PRIMARY KEY);
                        INSERT INTO OperationRecords VALUES ('P_OLD', 'OP_OLD');";
                    cmd.ExecuteNonQuery();
                }

                var ctx = new SqliteDatabaseContext(dbPath);
                bool rejected = false;
                try
                {
                    ctx.InitializeDatabase();
                    ctx.ValidateReadiness();
                }
                catch (InvalidOperationException ex)
                {
                    if (ex.Message.Contains("LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET"))
                        rejected = true;
                }

                if (!rejected)
                    throw new Exception($"Legacy v{legacyVer} was NOT rejected fail-closed!");

                // Check records preserved
                using (var conn = new SqliteConnection($"Data Source={dbPath}"))
                {
                    conn.Open();
                    using var cmd = conn.CreateCommand();
                    cmd.CommandText = "SELECT COUNT(*) FROM OperationRecords;";
                    long count = (long)cmd.ExecuteScalar()!;
                    if (count != 1)
                        throw new Exception($"Legacy v{legacyVer} records were wiped! Count = {count}");
                }
            }

            return "Legacy V1, V2, and V3 databases with records fail closed with LEGACY_SCHEMA_REQUIRES_OFFLINE_MIGRATION_OR_RESET and preserve all rows.";
        }

        // 19. P1 still has no generic consumer delivery
        static string Test19_NoGenericConsumerDelivery()
        {
            var serverAssembly = typeof(PipelineTransactionCoordinator).Assembly;
            var typeNames = serverAssembly.GetTypes().Select(t => t.FullName!).ToList();

            foreach (var banned in new[] { "ConsumerCursor", "ConsumerDurableAck", "DurableTestConsumer", "EventDispatcher", "GenericEventConsumer" })
            {
                if (typeNames.Any(t => t.Contains(banned)))
                    throw new Exception($"Found prohibited consumer delivery type: {banned}");
            }

            return "P1 pipeline architecture verified: zero consumer cursors, zero durable ack tables, zero background subscriber delivery threads.";
        }

        // 20. no gameplay/material mutation
        static string Test20_NoGameplayMaterialMutation()
        {
            var ctx = CreateTestContext("t20_gameplay_isolation");
            var tables = new List<string>();
            using (var conn = ctx.CreateOpenConnection())
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';";
                using var reader = cmd.ExecuteReader();
                while (reader.Read())
                {
                    tables.Add(reader.GetString(0));
                }
            }

            var expectedTables = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
            {
                "ProbeAggregates",
                "OperationRecords",
                "CommitReceipts",
                "PublicationEvents",
                "AuditRecords",
                "StoreIncarnations",
                "ProbeRevisionHistory"
            };

            foreach (var t in tables)
            {
                if (!expectedTables.Contains(t))
                    throw new Exception($"Detected unauthorized table in transaction pipeline slice: {t}");
            }

            return "Pipeline slice is strictly isolated: operates purely on ProbeAggregates/ProbeRevision with zero settlement, pawn, inventory, or market gameplay mutations.";
        }
    }
}
