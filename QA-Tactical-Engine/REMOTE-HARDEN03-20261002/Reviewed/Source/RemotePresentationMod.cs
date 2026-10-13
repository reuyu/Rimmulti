using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using HarmonyLib;
using UnityEngine;
using Verse;
using Verse.AI;
using RimWorld;
using WarEconomy.RemotePresentation.Common;
using WarEconomy.RemotePresentation.Worker;
using WarEconomy.RemotePresentation.Client;

namespace WarEconomy.RemotePresentation
{
    public class RemotePresentationMod : Mod
    {
        public static string Role = "NONE"; // WORKER, CLIENT, NONE
        public static int WorkerPort = 7792;
        public static int ClientPort = 7793;
        public static string ConnectAddress = "127.0.0.1:7792";
        public static bool AutoRunPoC = false;
        public static string AutoLoadSave = "";

        public RemotePresentationMod(ModContentPack content) : base(content)
        {
            Log.Message("[RemotePresentationMod] Constructor initialized. Applying Harmony patches...");
            try
            {
                var harmony = new Harmony("wareconomy.remotepresentation.poc");
                harmony.PatchAll();
                Log.Message("[RemotePresentationMod] Harmony patches applied.");
            }
            catch (Exception ex)
            {
                Log.Error("[RemotePresentationMod] Harmony patch error: " + ex);
            }

            ParseCommandLine();
        }

        private void ParseCommandLine()
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length; i++)
            {
                string arg = args[i];
                if (arg.Equals("-remote-worker", StringComparison.OrdinalIgnoreCase))
                {
                    Role = "WORKER";
                }
                else if (arg.Equals("-remote-client", StringComparison.OrdinalIgnoreCase))
                {
                    Role = "CLIENT";
                }
                else if (arg.Equals("-worker-port", StringComparison.OrdinalIgnoreCase) && i + 1 < args.Length)
                {
                    int.TryParse(args[++i], out WorkerPort);
                }
                else if (arg.Equals("-client-port", StringComparison.OrdinalIgnoreCase) && i + 1 < args.Length)
                {
                    int.TryParse(args[++i], out ClientPort);
                }
                else if (arg.Equals("-connect", StringComparison.OrdinalIgnoreCase) && i + 1 < args.Length)
                {
                    ConnectAddress = args[++i];
                }
                else if (arg.Equals("-run-remote-poc", StringComparison.OrdinalIgnoreCase))
                {
                    AutoRunPoC = true;
                }
                else if (arg.Equals("-load-save", StringComparison.OrdinalIgnoreCase) && i + 1 < args.Length)
                {
                    AutoLoadSave = args[++i];
                }
            }
            Log.Message($"[RemotePresentationMod] Parsed CommandLine: Role={Role}, WorkerPort={WorkerPort}, ClientPort={ClientPort}, Connect={ConnectAddress}, AutoRun={AutoRunPoC}, LoadSave={AutoLoadSave}");
        }
    }

    [StaticConstructorOnStartup]
    public static class RemotePresentationBootstrapper
    {
        static RemotePresentationBootstrapper()
        {
            try
            {
                Log.Message($"[RemotePresentationBootstrapper] Initializing GameObject for Role={RemotePresentationMod.Role}...");
                var go = new GameObject("RemotePresentationController");
                UnityEngine.Object.DontDestroyOnLoad(go);

                if (RemotePresentationMod.Role == "WORKER")
                {
                    var worker = go.AddComponent<RemoteWorkerController>();
                    worker.StartServer(RemotePresentationMod.WorkerPort);
                }
                else if (RemotePresentationMod.Role == "CLIENT")
                {
                    var client = go.AddComponent<RemoteClientController>();
                    client.StartServer(RemotePresentationMod.ClientPort);
                    go.AddComponent<RemoteClientTestHarness>();
                }
                else
                {
                    Log.Message("[RemotePresentationBootstrapper] No specific remote role specified on commandline.");
                }

                // If AutoLoadSave specified, queue load
                if (!string.IsNullOrEmpty(RemotePresentationMod.AutoLoadSave))
                {
                    LongEventHandler.QueueLongEvent(() =>
                    {
                        Log.Message($"[RemotePresentationBootstrapper] Auto-loading save: {RemotePresentationMod.AutoLoadSave}");
                        GameDataSaveLoader.LoadGame(RemotePresentationMod.AutoLoadSave);
                    }, "LoadingAutoSave", true, null);
                }
            }
            catch (Exception ex)
            {
                Log.Error("[RemotePresentationBootstrapper] Bootstrapper exception: " + ex);
            }
        }
    }

    #region Harmony Patches

    // Suppress autonomous frame ticking on both Worker and Presentation Client.
    // Worker ticks explicitly via DoSingleTick().
    // Client does not tick canonically at all (runs paused / non-authoritative presentation).
    [HarmonyPatch(typeof(TickManager), nameof(TickManager.TickManagerUpdate))]
    public static class Patch_TickManager_TickManagerUpdate
    {
        public static bool Prefix()
        {
            if (RemotePresentationMod.Role == "WORKER" || RemotePresentationMod.Role == "CLIENT")
            {
                return false;
            }
            return true;
        }
    }

    #endregion
}
