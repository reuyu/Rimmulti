using System;
using System.IO;
using System.Threading;
using WarEconomy.Server.Managers;
using WarEconomy.Server.Network;
using WarEconomy.Server.Time;

namespace WarEconomy.Server
{
    class Program
    {
        private static WorldTickManager? _tickManager;
        public static long CurrentTick => _tickManager?.CurrentWorldTick ?? 0;

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

                var battery = new WarEconomy.Server.Pipeline.Testing.PipelineE1TestBattery(dbPath);
                var report = battery.RunAllTestsAsync().GetAwaiter().GetResult();

                if (!string.IsNullOrEmpty(jsonPath))
                {
                    string json = Newtonsoft.Json.JsonConvert.SerializeObject(report, Newtonsoft.Json.Formatting.Indented);
                    File.WriteAllText(jsonPath, json);
                    Console.WriteLine($"[PipelineE1] Wrote report JSON to: {jsonPath}");
                }

                Environment.Exit(report.OverallSuccess ? 0 : 1);
                return;
            }
            else if (args.Length > 0 && args[0] == "--crash-worker")
            {
                string faultPointStr = args.Length > 1 ? args[1] : "AfterPrepared";
                string dbPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "crash_worker.db");
                string scopeId = "SCOPE_HARD_CRASH";
                string opId = "OP_HARD_CRASH";

                for (int i = 0; i < args.Length; i++)
                {
                    if (args[i] == "--db" && i + 1 < args.Length) dbPath = args[i + 1];
                    if (args[i] == "--scope" && i + 1 < args.Length) scopeId = args[i + 1];
                    if (args[i] == "--op" && i + 1 < args.Length) opId = args[i + 1];
                }

                var faultPoint = Enum.Parse<WarEconomy.Server.Pipeline.Models.FaultInjectionPoint>(faultPointStr);
                var dbContext = new WarEconomy.Server.Pipeline.Data.SqliteDatabaseContext(dbPath);
                dbContext.InitializeDatabase();

                var coord = new WarEconomy.Server.Pipeline.Coordinator.PipelineTransactionCoordinator(dbContext)
                {
                    ActiveFaultPoint = faultPoint,
                    FaultAction = (point, req) =>
                    {
                        Console.WriteLine($"[CrashWorker] Executing hard Process FailFast at fault point: {point}");
                        Environment.FailFast($"Hard Crash at {point}");
                    }
                };

                try
                {
                    coord.ExecuteProbeCas(new WarEconomy.Server.Pipeline.Models.PipelineProbeRequest
                    {
                        OperationId = opId,
                        ProbeScopeId = scopeId,
                        ExpectedProbeRevision = 0,
                        PayloadJson = $"{{\"crash\": \"{faultPoint}\"}}",
                        ActorId = "HARD_CRASH_WORKER"
                    });
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[CrashWorker] Caught {ex.Message}");
                }
                return;
            }
            else if (args.Length > 0 && args[0] == "--run-reconciler")
            {
                string dbPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "war_economy_pipeline.db");
                for (int i = 0; i < args.Length; i++)
                {
                    if (args[i] == "--db" && i + 1 < args.Length) dbPath = args[i + 1];
                }

                var dbContext = new WarEconomy.Server.Pipeline.Data.SqliteDatabaseContext(dbPath);
                dbContext.InitializeDatabase();
                var reconciler = new WarEconomy.Server.Pipeline.Recovery.RecoveryReconciler(dbContext);
                var report = reconciler.ReconcilePendingOperations();
                Console.WriteLine($"[Reconciler] PreparedFound={report.PreparedFoundCount}, ResumedCommitted={report.PreparedResumedAndCommittedCount}, OutboxPending={report.OutboxPendingFoundCount}, OutboxDelivered={report.OutboxDeliveredCount}");
                foreach (var d in report.Details)
                {
                    Console.WriteLine($"  Detail: {d}");
                }
                return;
            }

            Console.WriteLine("======================================================");
            Console.WriteLine("   RimWorld War-Economy & Feudal Dedicated Server     ");
            Console.WriteLine("======================================================");

            _tickManager = new WorldTickManager();

            // 1. 월드 시스템 등록 (초당 180 틱 3배속 루프)
            _tickManager.RegisterSystem(DiplomacyManager.Instance);
            _tickManager.RegisterSystem(DynamicMarketManager.Instance);
            _tickManager.RegisterSystem(FeudalManager.Instance);

            // 기본 중립 영지 시드 등록
            FeudalManager.Instance.InitializeDefaultSettlements();

            // 2. TCP 네트워크 서버 기동 (기본 포트 7777)
            var networkServer = TcpNetworkServer.Instance;
            networkServer.Start(7777);

            // 3. 서버 이벤트 <-> 네트워크 브로드캐스트 연결
            _tickManager.OnBroadcastTickSync += packet => networkServer.BroadcastPacket(packet);
            DiplomacyManager.Instance.OnWarStateUpdated += packet => networkServer.BroadcastPacket(packet);
            DiplomacyManager.Instance.OnBetrayalOccurred += packet => networkServer.BroadcastPacket(packet);
            DynamicMarketManager.Instance.OnMarketSynced += packet => networkServer.BroadcastPacket(packet);
            FeudalManager.Instance.OnTaxDelinquencyChanged += packet => networkServer.BroadcastPacket(packet);
            FeudalManager.Instance.OnFiefTransferExecuted += packet =>
            {
                // 이전 영주(호스트) 세션이 접속 중이면 해당 세션에 우선 타깃팅 전송하고, 없으면 브로드캐스트
                if (!string.IsNullOrEmpty(packet.PreviousLordPlayerId) && networkServer.SendToPlayer(packet.PreviousLordPlayerId, packet))
                {
                    Console.WriteLine($"[Feudal] Targeted FiefTransferExecute packet to host session '{packet.PreviousLordPlayerId}'.");
                }
                else
                {
                    networkServer.BroadcastPacket(packet);
                }
            };
            FeudalManager.Instance.OnSettlementListUpdated += packet => networkServer.BroadcastPacket(packet);

            // 4. 월드 시계 가동

            _tickManager.Start();

            Console.WriteLine("Server ready! Listening for players. Type 'quit' or 'exit' to terminate.");

            while (true)
            {
                string? input = Console.ReadLine();
                if (input == null)
                {
                    Thread.Sleep(500);
                    continue;
                }

                if (input == "quit" || input == "exit")
                {
                    _tickManager.Stop();
                    networkServer.Stop();
                    break;
                }
                else if (input == "status")
                {
                    Console.WriteLine($"[Status] Server World Tick: {_tickManager.CurrentWorldTick}, Clients Active: {networkServer.IsRunning}");
                }
            }
        }
    }
}
