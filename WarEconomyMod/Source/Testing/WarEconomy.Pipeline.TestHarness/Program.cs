using System;
using System.IO;
using WarEconomy.Server.Pipeline.Coordinator;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Models;

namespace WarEconomy.Pipeline.TestHarness
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length > 0 && args[0] == "--test-pipeline-e1")
            {
                string? jsonPath = null;
                string? dbPath = null;
                for (int i = 0; i < args.Length; i++)
                {
                    if (args[i] == "--json" && i + 1 < args.Length) jsonPath = args[i + 1];
                    if (args[i] == "--db" && i + 1 < args.Length) dbPath = args[i + 1];
                }

                Console.WriteLine("================================================================================");
                Console.WriteLine("   WarEconomy Pipeline REV2 E1 Test Battery (22 Mandatory Categories)           ");
                Console.WriteLine("================================================================================");

                var battery = new PipelineE1TestBattery(dbPath);
                var report = battery.RunAllTestsAsync().GetAwaiter().GetResult();

                if (!string.IsNullOrEmpty(jsonPath))
                {
                    string? dir = Path.GetDirectoryName(jsonPath);
                    if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    {
                        Directory.CreateDirectory(dir);
                    }
                    string json = Newtonsoft.Json.JsonConvert.SerializeObject(report, Newtonsoft.Json.Formatting.Indented);
                    File.WriteAllText(jsonPath, json);
                    Console.WriteLine($"[PipelineE1] Wrote report JSON to: {jsonPath}");
                }

                Environment.Exit(report.OverallSuccess ? 0 : 1);
                return;
            }
            else if (args.Length > 0 && args[0] == "--crash-worker")
            {
                // Crash worker for testing multi-process races and failfast
                string dbPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "crash_worker.db");
                string scopeId = "SCOPE_HARD_CRASH";
                string opId = "OP_HARD_CRASH";
                string principalId = "CRASH_WORKER_PRINCIPAL";
                long expectedRev = 0;

                for (int i = 0; i < args.Length; i++)
                {
                    if (args[i] == "--db" && i + 1 < args.Length) dbPath = args[i + 1];
                    if (args[i] == "--scope" && i + 1 < args.Length) scopeId = args[i + 1];
                    if (args[i] == "--op" && i + 1 < args.Length) opId = args[i + 1];
                    if (args[i] == "--principal" && i + 1 < args.Length) principalId = args[i + 1];
                    if (args[i] == "--expected" && i + 1 < args.Length) expectedRev = long.Parse(args[i + 1]);
                }

                var dbContext = new SqliteDatabaseContext(dbPath);
                dbContext.InitializeDatabase();

                using var coord = new PipelineTransactionCoordinator(dbContext);

                try
                {
                    var result = coord.ExecuteProbeCas(new PipelineProbeRequest
                    {
                        PrincipalId = principalId,
                        OperationId = opId,
                        ProbeScopeId = scopeId,
                        ExpectedProbeRevision = expectedRev,
                        PayloadJson = "{\"worker\": 1}"
                    });

                    Console.WriteLine($"[CrashWorker] Result: {result.Status} Success={result.Success}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[CrashWorker] Caught {ex.Message}");
                }
                return;
            }

            Console.WriteLine("WarEconomy.Pipeline.TestHarness: Usage:");
            Console.WriteLine("  --test-pipeline-e1 [--json <reportPath>] [--db <dbPath>]");
            Console.WriteLine("  --crash-worker --db <dbPath> --scope <scopeId> --op <opId> --principal <pId> --expected <rev>");
        }
    }
}
