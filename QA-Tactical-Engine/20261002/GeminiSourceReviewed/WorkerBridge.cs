using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Security.Cryptography;
using UnityEngine;
using Verse;
using RimWorld;

namespace WarEconomy.WorkerBridge
{
    public class WorkerBridgeMod : Mod
    {
        public WorkerBridgeMod(ModContentPack content) : base(content)
        {
            Log.Message("[WorkerBridge] Mod constructor initialized.");
        }
    }

    [StaticConstructorOnStartup]
    public static class WorkerBridgeBootstrapper
    {
        static WorkerBridgeBootstrapper()
        {
            try
            {
                Log.Message("[WorkerBridge] StaticConstructorOnStartup fired. Creating GameObject controller...");
                var go = new GameObject("WorkerBridgeController");
                UnityEngine.Object.DontDestroyOnLoad(go);
                go.AddComponent<WorkerBridgeComponent>();
                Log.Message("[WorkerBridge] Controller GameObject attached.");
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Bootstrapper error: " + ex);
            }
        }
    }

    public class BridgeRequest
    {
        public string Command = "";
        public string Argument = "";
        public TaskCompletionSource<string> ResponseTcs = new TaskCompletionSource<string>();
    }

    public class WorkerBridgeComponent : MonoBehaviour
    {
        private TcpListener? listener;
        private Thread? listenerThread;
        private volatile bool isRunning = true;
        private readonly ConcurrentQueue<BridgeRequest> requestQueue = new ConcurrentQueue<BridgeRequest>();

        private int port = 29100;
        private string autoLoadSave = "";
        private bool autoLoadTriggered = false;
        private bool hasForcedInitialPause = false;

        void Awake()
        {
            try
            {
                if (GenCommandLine.TryGetCommandLineArg("bridgeport", out string portStr) && int.TryParse(portStr, out int customPort))
                {
                    port = customPort;
                }
                if (GenCommandLine.TryGetCommandLineArg("autoloadsave", out string saveStr))
                {
                    autoLoadSave = saveStr;
                }

                Log.Message($"[WorkerBridge] Component Awake. Listening port: {port}, Autoload save: '{autoLoadSave}'");

                listener = new TcpListener(IPAddress.Loopback, port);
                listener.Start();

                listenerThread = new Thread(ListenLoop)
                {
                    IsBackground = true,
                    Name = "WorkerBridge_Listener"
                };
                listenerThread.Start();
            }
            catch (Exception ex)
            {
                Log.Error("[WorkerBridge] Failed to start TCP listener: " + ex);
            }
        }

        void Update()
        {
            // Handle autoload if specified
            if (!autoLoadTriggered && !string.IsNullOrEmpty(autoLoadSave))
            {
                if (Current.Game == null && !LongEventHandler.AnyEventNowOrWaiting)
                {
                    autoLoadTriggered = true;
                    Log.Message($"[WorkerBridge] Triggering autoload for '{autoLoadSave}'...");
                    try
                    {
                        GameDataSaveLoader.LoadGame(autoLoadSave);
                    }
                    catch (Exception ex)
                    {
                        Log.Error($"[WorkerBridge] Autoload exception: {ex}");
                    }
                }
            }

            // Enforce pause state for tactical worker
            if (Current.Game != null && Current.ProgramState == ProgramState.Playing && Current.Game.tickManager != null)
            {
                if (!hasForcedInitialPause)
                {
                    hasForcedInitialPause = true;
                    Current.Game.tickManager.CurTimeSpeed = TimeSpeed.Paused;
                    Log.Message("[WorkerBridge] Enforced default pause state for tactical worker.");
                }
            }

            // Process requests on main thread
            while (requestQueue.TryDequeue(out var req))
            {
                try
                {
                    string res = ProcessCommandMainThread(req.Command, req.Argument);
                    req.ResponseTcs.TrySetResult(res);
                }
                catch (Exception ex)
                {
                    Log.Error($"[WorkerBridge] Error processing '{req.Command}': {ex}");
                    req.ResponseTcs.TrySetResult($"ERROR: {ex.GetType().Name}: {ex.Message}");
                }
            }
        }

        private void ListenLoop()
        {
            while (isRunning && listener != null)
            {
                try
                {
                    var client = listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleClient, client);
                }
                catch
                {
                    if (!isRunning) break;
                }
            }
        }

        private void HandleClient(object? state)
        {
            if (state is not TcpClient client) return;
            using (client)
            using (var stream = client.GetStream())
            using (var reader = new StreamReader(stream, Encoding.UTF8))
            using (var writer = new StreamWriter(stream, Encoding.UTF8) { AutoFlush = true })
            {
                try
                {
                    while (isRunning && client.Connected)
                    {
                        string? line = reader.ReadLine();
                        if (line == null) break;
                        line = line.Trim().Trim('\uFEFF', '\u200B', '\0');
                        if (string.IsNullOrEmpty(line)) continue;

                        string cmd = line;
                        string arg = "";
                        int spaceIdx = line.IndexOf(' ');
                        if (spaceIdx > 0)
                        {
                            cmd = line.Substring(0, spaceIdx).ToUpperInvariant();
                            arg = line.Substring(spaceIdx + 1);
                        }
                        else
                        {
                            cmd = line.ToUpperInvariant();
                        }

                        var req = new BridgeRequest { Command = cmd, Argument = arg };
                        requestQueue.Enqueue(req);

                        // Wait for main thread response
                        if (req.ResponseTcs.Task.Wait(30000))
                        {
                            string response = req.ResponseTcs.Task.Result;
                            writer.WriteLine(response);
                            writer.WriteLine("---END---");
                        }
                        else
                        {
                            writer.WriteLine("ERROR: Timeout waiting for main thread execution.");
                            writer.WriteLine("---END---");
                        }

                        if (cmd == "SHUTDOWN")
                        {
                            break;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Log.Warning($"[WorkerBridge] Client handling error: {ex.Message}");
                }
            }
        }

        private string ProcessCommandMainThread(string cmd, string arg)
        {
            switch (cmd)
            {
                case "HELLO":
                    return $"READY: RimWorld {VersionControl.CurrentVersionStringWithRev}, Unity {Application.unityVersion}, FrameTime={Time.smoothDeltaTime * 1000:F1}ms";

                case "LOAD_STATUS":
                case "STATUS":
                    return GetStatus();

                case "LOAD_SAVE":
                    return LoadSave(arg);

                case "GET_WORLD_INFO":
                    return GetWorldInfo();

                case "GET_MAP_INFO":
                    return GetMapInfo();

                case "RUN_TICKS":
                    return RunTicks(arg);

                case "GET_ENTITY_SUMMARY":
                    return GetEntitySummary();

                case "EXPORT_SAVE":
                    return ExportSave(arg);

                case "SHUTDOWN":
                    Log.Message("[WorkerBridge] Shutdown command received. Quitting Application...");
                    isRunning = false;
                    try { listener?.Stop(); } catch { }
                    Application.Quit();
                    return "BYE: Worker shutting down.";

                default:
                    return $"ERROR: Unknown command '{cmd}'";
            }
        }

        private string GetStatus()
        {
            bool isBusy = LongEventHandler.AnyEventNowOrWaiting;
            if (Current.Game == null)
            {
                return $"STATE: {(isBusy ? "Loading" : "NoGame")}, Maps=0, TicksGame=0";
            }

            int mapCount = Current.Game.Maps?.Count ?? 0;
            int ticks = Current.Game.tickManager?.TicksGame ?? 0;

            if (isBusy || mapCount == 0 || Current.ProgramState != ProgramState.Playing)
            {
                string subState = isBusy ? "Loading" : "MapInitializing";
                return $"STATE: {subState}, Maps={mapCount}, TicksGame={ticks}";
            }

            bool isPaused = Current.Game.tickManager?.Paused ?? true;
            return $"STATE: Playing, Maps={mapCount}, TicksGame={ticks}, Paused={isPaused}";
        }

        private string LoadSave(string saveName)
        {
            if (string.IsNullOrEmpty(saveName))
            {
                return "ERROR: Save name cannot be empty.";
            }

            hasForcedInitialPause = false;
            Log.Message($"[WorkerBridge] Initiating load for save '{saveName}'...");
            GameDataSaveLoader.LoadGame(saveName);
            return $"QUEUED: LoadGame queued for '{saveName}'. Poll LOAD_STATUS to monitor completion.";
        }

        private string GetWorldInfo()
        {
            if (Current.Game == null || Find.World == null)
            {
                return "ERROR: No active Game/World loaded.";
            }

            var w = Find.World;
            var sb = new StringBuilder();
            sb.AppendLine($"WorldSeed: {w.info.seedString}");
            sb.AppendLine($"WorldTicks: {Find.TickManager.TicksGame}");
            sb.AppendLine($"FactionsCount: {Find.FactionManager.AllFactions.Count()}");
            sb.AppendLine($"MapsCount: {Find.Maps.Count}");
            return sb.ToString().TrimEnd();
        }

        private string GetMapInfo()
        {
            if (Current.Game == null || Find.Maps == null || Find.Maps.Count == 0)
            {
                return "ERROR: No active Map loaded.";
            }

            var sb = new StringBuilder();
            for (int i = 0; i < Find.Maps.Count; i++)
            {
                var map = Find.Maps[i];
                sb.AppendLine($"Map[{i}]: Index={map.Index}, Tile={map.Tile}, Size={map.Size.x}x{map.Size.z}, Pawns={map.mapPawns.AllPawns.Count}, Colonists={map.mapPawns.FreeColonists.Count}, Buildings={map.listerBuildings.allBuildingsColonist.Count}");
            }
            return sb.ToString().TrimEnd();
        }

        private string RunTicks(string arg)
        {
            if (Current.Game == null || Find.TickManager == null)
            {
                return "ERROR: No active Game/TickManager.";
            }

            if (!int.TryParse(arg, out int tickCount) || tickCount <= 0)
            {
                return "ERROR: Invalid tick count. Usage: RUN_TICKS <positive integer>";
            }

            long startTick = Find.TickManager.TicksGame;
            var sw = Stopwatch.StartNew();

            for (int i = 0; i < tickCount; i++)
            {
                Find.TickManager.DoSingleTick();
            }

            sw.Stop();
            long endTick = Find.TickManager.TicksGame;
            double ms = Math.Max(1.0, sw.Elapsed.TotalMilliseconds);
            double tps = tickCount * 1000.0 / ms;

            return $"OK: Ran {tickCount} ticks in {ms:F1} ms ({tps:F1} TPS). StartTick={startTick}, EndTick={endTick}";
        }

        private string GetEntitySummary()
        {
            if (Current.Game == null || Find.Maps == null || Find.Maps.Count == 0)
            {
                return "ERROR: No active Map loaded.";
            }

            var map = Find.CurrentMap ?? Find.Maps[0];
            var sb = new StringBuilder();
            sb.AppendLine($"=== MAP SEMANTIC SNAPSHOT ===");
            sb.AppendLine($"MapIndex: {map.Index}, Tile: {map.Tile}, Size: {map.Size.x}x{map.Size.z}");
            sb.AppendLine($"TicksGame: {Find.TickManager.TicksGame}");

            // 1. Colonists & Humanlikes
            var pawns = map.mapPawns.AllPawns.Where(p => p.RaceProps.Humanlike).OrderBy(p => p.ThingID).ToList();
            sb.AppendLine($"\n[PAWNS: Count={pawns.Count}]");
            foreach (var p in pawns)
            {
                string jobStr = p.CurJob != null ? $"{p.CurJob.def?.defName ?? "null"}({p.CurJob.targetA})" : "Idle";
                float food = p.needs?.food?.CurLevelPercentage ?? -1f;
                float rest = p.needs?.rest?.CurLevelPercentage ?? -1f;
                string weapon = p.equipment?.Primary?.def?.defName ?? "None";
                int apparelCount = p.apparel?.WornApparelCount ?? 0;
                int invCount = p.inventory?.innerContainer?.Count ?? 0;
                string bedId = p.ownership?.OwnedBed?.ThingID ?? "None";
                string faction = p.Faction?.def?.defName ?? "None";

                sb.AppendLine($"Pawn ID={p.ThingID}, Name='{p.LabelShort}', Faction={faction}, Pos=({p.Position.x},{p.Position.z}), Downed={p.Downed}, Dead={p.Dead}, Job={jobStr}, Food={food:F2}, Rest={rest:F2}, Weapon={weapon}, Apparel={apparelCount}, Inv={invCount}, Bed={bedId}");
            }

            // 2. Animals
            var animals = map.mapPawns.AllPawns.Where(p => p.RaceProps.Animal).OrderBy(p => p.ThingID).ToList();
            sb.AppendLine($"\n[ANIMALS: Count={animals.Count}]");
            foreach (var a in animals.Take(50)) // sample first 50 if huge
            {
                string faction = a.Faction?.def?.defName ?? "Wild";
                string jobStr = a.CurJob != null ? a.CurJob.def?.defName ?? "null" : "Idle";
                sb.AppendLine($"Animal ID={a.ThingID}, Def={a.def.defName}, Faction={faction}, Pos=({a.Position.x},{a.Position.z}), Job={jobStr}");
            }

            // 3. Buildings
            var buildings = map.listerBuildings.allBuildingsColonist.OrderBy(b => b.ThingID).ToList();
            sb.AppendLine($"\n[COLONIST_BUILDINGS: Count={buildings.Count}]");
            foreach (var b in buildings)
            {
                sb.AppendLine($"Building ID={b.ThingID}, Def={b.def.defName}, Pos=({b.Position.x},{b.Position.z}), HP={b.HitPoints}/{b.MaxHitPoints}");
            }

            // 4. Loose Haulable Items
            var looseItems = map.listerThings.AllThings.Where(t => t.def.category == ThingCategory.Item && t.Spawned).OrderBy(t => t.ThingID).ToList();
            sb.AppendLine($"\n[LOOSE_ITEMS: Count={looseItems.Count}]");
            foreach (var item in looseItems.Take(60))
            {
                sb.AppendLine($"Item ID={item.ThingID}, Def={item.def.defName}, Stack={item.stackCount}, Pos=({item.Position.x},{item.Position.z})");
            }

            // 5. Containers (Shelves/Storage)
            var containers = map.listerBuildings.allBuildingsColonist.OfType<Building_Storage>().OrderBy(s => s.ThingID).ToList();
            sb.AppendLine($"\n[STORAGE_CONTAINERS: Count={containers.Count}]");
            foreach (var c in containers)
            {
                var stored = c.slotGroup?.HeldThings?.ToList() ?? new List<Thing>();
                sb.AppendLine($"Storage ID={c.ThingID}, Def={c.def.defName}, Pos=({c.Position.x},{c.Position.z}), StoredCount={stored.Count}, Items=[{string.Join(",", stored.Select(t => $"{t.def.defName}x{t.stackCount}"))}]");
            }

            return sb.ToString().TrimEnd();
        }

        private string ExportSave(string saveName)
        {
            if (Current.Game == null)
            {
                return "ERROR: Cannot export save; no active Game loaded.";
            }

            if (string.IsNullOrEmpty(saveName))
            {
                saveName = $"WorkerExport_{DateTime.UtcNow:yyyyMMdd_HHmmss}";
            }

            string savePath = GenFilePaths.FilePathForSavedGame(saveName);
            Log.Message($"[WorkerBridge] Exporting save to '{savePath}'...");

            var sw = Stopwatch.StartNew();
            GameDataSaveLoader.SaveGame(saveName);
            sw.Stop();

            if (!File.Exists(savePath))
            {
                return $"ERROR: Save file '{savePath}' was not created on disk.";
            }

            var fi = new FileInfo(savePath);
            string hash;
            using (var sha = SHA256.Create())
            using (var fs = File.OpenRead(savePath))
            {
                hash = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "");
            }

            return $"SAVED: File='{savePath}', Name='{saveName}', Size={fi.Length} bytes, SHA256={hash}, Elapsed={sw.ElapsedMilliseconds} ms";
        }

        void OnDestroy()
        {
            isRunning = false;
            try { listener?.Stop(); } catch { }
            try { listenerThread?.Abort(); } catch { }
        }
    }
}
