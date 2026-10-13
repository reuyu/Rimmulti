using System;
using System.IO;
using System.Threading;
using WarEconomy.Server.Managers;
using WarEconomy.Server.Network;
using WarEconomy.Server.Pipeline.Data;
using WarEconomy.Server.Pipeline.Recovery;
using WarEconomy.Server.Time;

namespace WarEconomy.Server
{
    class Program
    {
        private static WorldTickManager? _tickManager;
        public static long CurrentTick => _tickManager?.CurrentWorldTick ?? 0;

        static void Main(string[] args)
        {
            Console.WriteLine("======================================================");
            Console.WriteLine("   RimWorld War-Economy & Feudal Dedicated Server     ");
            Console.WriteLine("======================================================");

            // =========================================================================
            // MANDATORY STEP: Startup Readiness & Pipeline Verification
            // Normal server startup must:
            // 1. Open/validate canonical DB;
            // 2. Apply/validate migrations (Schema V3);
            // 3. Verify durability settings (WAL, FULL, application_id, user_version);
            // 4. Run required recovery/convergence;
            // 5. Reach explicit PIPELINE_READY;
            // 6. Only then admit canonical gameplay/domain mutations.
            // =========================================================================
            try
            {
                var canonicalDbContext = new SqliteDatabaseContext();
                PipelineStartupManager.InitializeAndVerifyPipeline(canonicalDbContext);
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[CRITICAL] Server startup halted: Pipeline readiness verification failed: {ex.Message}");
                Console.ResetColor();
                Environment.Exit(2);
                return;
            }

            _tickManager = new WorldTickManager();

            // 1. Register World Systems (180 TPS / 3x speed tick loop)
            _tickManager.RegisterSystem(DiplomacyManager.Instance);
            _tickManager.RegisterSystem(DynamicMarketManager.Instance);
            _tickManager.RegisterSystem(FeudalManager.Instance);

            // Register default neutral fief seeds
            FeudalManager.Instance.InitializeDefaultSettlements();

            // 2. TCP Network Server Startup (Default Port 7777)
            var networkServer = TcpNetworkServer.Instance;
            networkServer.Start(7777);

            // 3. Network Broadcast Event Bindings
            _tickManager.OnBroadcastTickSync += packet => networkServer.BroadcastPacket(packet);
            DiplomacyManager.Instance.OnWarStateUpdated += packet => networkServer.BroadcastPacket(packet);
            DiplomacyManager.Instance.OnBetrayalOccurred += packet => networkServer.BroadcastPacket(packet);
            DynamicMarketManager.Instance.OnMarketSynced += packet => networkServer.BroadcastPacket(packet);
            FeudalManager.Instance.OnTaxDelinquencyChanged += packet => networkServer.BroadcastPacket(packet);
            FeudalManager.Instance.OnFiefTransferExecuted += packet =>
            {
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

            // 4. Start World Clock
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
                    PipelineStartupManager.Shutdown();
                    break;
                }
                else if (input == "status")
                {
                    Console.WriteLine($"[Status] Server World Tick: {_tickManager.CurrentWorldTick}, Clients Active: {networkServer.IsRunning}, Pipeline Ready: {PipelineStartupManager.IsPipelineReady}");
                }
            }
        }
    }
}
