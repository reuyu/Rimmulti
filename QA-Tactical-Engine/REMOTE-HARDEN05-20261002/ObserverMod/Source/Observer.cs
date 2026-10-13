using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Linq;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Reflection;
using System.Diagnostics;
using System.Xml.Linq;
using HarmonyLib;
using UnityEngine;
using Verse;
using Verse.AI;
using RimWorld;
using WarEconomy.RemotePresentation;
using WarEconomy.RemotePresentation.Common;
using WarEconomy.RemotePresentation.Client;
using WarEconomy.RemotePresentation.Worker;
namespace QAHarden05 {
 public class ObserverMod:Mod {public ObserverMod(ModContentPack c):base(c){new Harmony("qacodex.remote.harden05.observer").PatchAll();}}
 [StaticConstructorOnStartup] public static class Boot {static Boot(){var o=new GameObject("QAHarden05");UnityEngine.Object.DontDestroyOnLoad(o);o.AddComponent<Observe>();}}
 public static class Audit {
  public static readonly ConcurrentQueue<string> events=new ConcurrentQueue<string>();
  public static readonly List<string> slices=new List<string>();
  public static int mainThread; public static ConcurrentDictionary<long,long> received=new ConcurrentDictionary<long,long>(); public static int ticks,draws,guis,rpcs,fetches,inflight,maxInflight; public static readonly ConcurrentQueue<string> wires=new ConcurrentQueue<string>(); public static readonly List<string> frames=new List<string>(); public static long lastFrameStamp;
  public static string Role=>RemotePresentationMod.Role;
  public static Pawn Pawn(string id){return Find.Maps?.SelectMany(m=>m.mapPawns.AllPawns).FirstOrDefault(p=>p.ThingID==id);}
  public static string State(string id){var p=Pawn(id);return p==null?"missing":$"id={p.ThingID} map={p.Map?.uniqueID} pos={p.Position} draft={p.Drafted} draw={p.DrawPos} job={p.CurJob?.def?.defName??"None"} rotation={p.Rotation.AsInt}";}
  public static void Event(string label){events.Enqueue(DateTime.UtcNow.ToString("o")+"\tThread="+Thread.CurrentThread.ManagedThreadId+"\tFrame="+Time.frameCount+"\tRole="+Role+"\tGUI="+(UnityEngine.Event.current?.type.ToString()??"null")+"\tReconciling="+RemoteClientController.IsReconciling+"\t"+label);}
  public static XElement PawnState(Pawn p){return new XElement("pawn",new XAttribute("id",p.ThingID),new XAttribute("map",p.Map?.uniqueID??-1),new XAttribute("position",p.Position),new XAttribute("drawPosition",p.DrawPos),new XAttribute("screen",Find.Camera==null?"None":Find.Camera.WorldToScreenPoint(p.DrawPos).ToString()),new XAttribute("pathMoving",p.pather?.Moving??false),new XAttribute("rotation",p.Rotation.AsInt),new XAttribute("drafted",p.Drafted),new XAttribute("job",p.CurJob?.def?.defName??"None"),new XAttribute("nextCell",p.pather?.nextCell.ToString()??"None"),new XAttribute("stance",p.stances?.curStance?.GetType().Name??"None"),new XAttribute("focus",p.stances?.curStance is Stance_Busy busy ? busy.focusTarg.ToString():"None"),new XAttribute("jobTarget",p.CurJob?.targetA.ToString()??"None"),new XAttribute("dead",p.Dead),new XAttribute("downed",p.Downed),new XAttribute("health",p.health?.summaryHealth?.SummaryHealthPercent??-1),new XAttribute("selected",Find.Selector?.SelectedObjects.Contains(p)??false),p.health?.hediffSet?.hediffs.Select(h=>new XElement("hediff",new XAttribute("id",h.GetUniqueLoadID()),new XAttribute("def",h.def.defName),new XAttribute("severity",h.Severity),new XAttribute("part",h.Part?.def?.defName??"None"))));}
  public static string Snap(){var c=RemoteClientController.Instance;var w=RemoteWorkerController.Instance;
   var root=new XElement("observation",new XAttribute("role",Role),new XAttribute("mainThread",Audit.mainThread),new XAttribute("epoch",c?.TransportEpoch??0),new XAttribute("connected",c?.IsConnected??false),new XAttribute("degraded",c?.ReplicationDegraded??false),new XAttribute("maxFrameMs",c?.MaxMainThreadFrameMs??0),new XAttribute("G",Find.TickManager?.TicksGame??-1),new XAttribute("map",Find.CurrentMap?.uniqueID??-1),new XAttribute("ticks",ticks),new XAttribute("draws",draws),new XAttribute("guis",guis),new XAttribute("rpcs",rpcs),new XAttribute("graphics",SystemInfo.graphicsDeviceType),new XAttribute("lastSequence",c?.LastAppliedSnapshotSequence??-1),new XAttribute("applied",c?.TotalSnapshotsApplied??0),new XAttribute("rejected",c?.TotalSnapshotsRejected??0),new XAttribute("periodic",c?.PeriodicMetrics.Count??0),new XAttribute("fetches",fetches),new XAttribute("inflight",inflight),new XAttribute("maxInflight",maxInflight),new XAttribute("replication",c?.ReplicationActive??false),new XAttribute("expectedMap",c?.ExpectedMapId??""),new XAttribute("progression",w?.OperationalProgressionEnabled??false),new XAttribute("paused",Find.TickManager?.Paused??false));
   foreach(var map in Find.Maps??new List<Map>()){
    var node=new XElement("mapState",new XAttribute("id",map.uniqueID),new XAttribute("things",map.spawnedThings.Count),new XAttribute("duplicateIds",map.spawnedThings.GroupBy(t=>t.ThingID).Count(g=>g.Count()>1)));
    foreach(var p in map.mapPawns.AllPawns){node.Add(PawnState(p));if(p.ThingID=="Human302"||p.ThingID=="Human305"){int n=0;foreach(var cell in map.AllCells)n+=map.thingGrid.ThingsListAt(cell).Count(x=>object.ReferenceEquals(x,p));node.Add(new XElement("grid",new XAttribute("pawn",p.ThingID),new XAttribute("references",n)));}}
    root.Add(node);
   }return root.ToString(SaveOptions.DisableFormatting);
  }
  public static void Flush(){var dir=GenFilePaths.SaveDataFolderPath;File.WriteAllLines(Path.Combine(dir,"qa-events.tsv"),events);File.WriteAllLines(Path.Combine(dir,"qa-worker-slices.tsv"),slices);File.WriteAllLines(Path.Combine(dir,"qa-wire.tsv"),wires);File.WriteAllLines(Path.Combine(dir,"qa-frame-gaps.tsv"),frames);}
 }
 [HarmonyPatch(typeof(TickManager),nameof(TickManager.DoSingleTick))] public static class Ticks {public static void Prefix(){Audit.ticks++;}}
 [HarmonyPatch(typeof(MapDrawer),nameof(MapDrawer.DrawMapMesh))] public static class Draw {public static void Prefix(){Audit.draws++;}}
 [HarmonyPatch] public static class Gizmo {
  public static IEnumerable<MethodBase> TargetMethods()=>AccessTools.GetDeclaredMethods(typeof(Command_Toggle)).Where(m=>m.Name=="ProcessInput");
  [HarmonyPriority(Priority.First)] public static void Prefix(Command_Toggle __instance){Audit.Event("NATIVE_GIZMO label="+__instance.defaultLabel);}
 }
 [HarmonyPatch(typeof(Pawn_DraftController),"Drafted",MethodType.Setter)] public static class Draft {
  [HarmonyPriority(Priority.First)] public static void Prefix(Pawn_DraftController __instance,bool value){Audit.Event("DRAFT_ENTER target="+value+" "+Audit.State(__instance.pawn?.ThingID));}
  public static void Postfix(Pawn_DraftController __instance){Audit.Event("DRAFT_EXIT "+Audit.State(__instance.pawn?.ThingID));}
 }
 [HarmonyPatch] public static class JobInput {
  public static IEnumerable<MethodBase> TargetMethods()=>AccessTools.GetDeclaredMethods(typeof(Pawn_JobTracker)).Where(m=>m.Name=="TryTakeOrderedJob");
  [HarmonyPriority(Priority.First)] public static void Prefix(Pawn_JobTracker __instance,Job __0){var p=AccessTools.Field(typeof(Pawn_JobTracker),"pawn").GetValue(__instance) as Pawn;Audit.Event("ORDER_ENTER requested="+__0?.def?.defName+" "+Audit.State(p?.ThingID));}
 }
 [HarmonyPatch(typeof(RemoteClientController),nameof(RemoteClientController.SendCommand))] public static class Rpc {
  public static void Prefix(RemoteTacticalCommand cmd){Audit.rpcs++;Audit.Event("RPC_ENTER type="+cmd.CommandType+" source="+cmd.Source+" "+Audit.State(cmd.TargetPawnId));}
  public static void Postfix(CommandResponse __result){Audit.Event("RPC_EXIT status="+__result?.Status+" own="+Audit.State("Human302"));}
 }
 [HarmonyPatch(typeof(Protocols),nameof(Protocols.ParseResponse))] public static class Incoming {
  public static string WirePawn(ReplicationSnapshot s){var p=s?.Pawns?.FirstOrDefault(x=>x.PawnId=="Human302");return p==null?"missing":$"pos={p.PosX},{p.PosZ} draw={p.DrawPosX},{p.DrawPosY},{p.DrawPosZ} draft={p.Drafted} job={p.CurJobDef} rot={p.Rotation}";}
  public static void Postfix(string json,CommandResponse __result){if(RemotePresentationMod.Role!="CLIENT")return;var s=__result?.Snapshot;long t=Stopwatch.GetTimestamp();if(s!=null)Audit.received[s.SnapshotSequence]=t;Audit.wires.Enqueue(DateTime.UtcNow.ToString("o")+"\tthread="+Thread.CurrentThread.ManagedThreadId+"\tstamp="+t+"\t"+json);Audit.events.Enqueue(DateTime.UtcNow.ToString("o")+"\tThread="+Thread.CurrentThread.ManagedThreadId+"\tWIRE_RESPONSE command="+__result?.CommandId+" bytes="+Encoding.UTF8.GetByteCount(json)+" pawns="+(s?.Pawns?.Count??0)+" seq="+(s?.SnapshotSequence??0));}
 }
 [HarmonyPatch(typeof(RemoteClientController),nameof(RemoteClientController.ValidateAndApplySnapshot))] public static class Validate {
  public static void Prefix(ReplicationSnapshot snap,out long __state){__state=Stopwatch.GetTimestamp();Audit.Event("APPLY_ENTER receiveToEnterMs="+(Audit.received.TryGetValue(snap.SnapshotSequence,out var rx)?((Stopwatch.GetTimestamp()-rx)*1000.0/Stopwatch.Frequency).ToString("F4"):"NA")+" seq="+snap?.SnapshotSequence+" tick="+snap?.AuthoritativeTick+" target="+snap?.TargetMapId+" viewed="+Find.CurrentMap?.uniqueID+" workerOwn="+Incoming.WirePawn(snap)+" own="+Audit.State("Human302"));}
  public static void Postfix(bool __result,string rejectionReason,long __state){Audit.Event("APPLY_EXIT applyMs="+((Stopwatch.GetTimestamp()-__state)*1000.0/Stopwatch.Frequency).ToString("F4",System.Globalization.CultureInfo.InvariantCulture)+" accepted="+__result+" reason="+rejectionReason+" own="+Audit.State("Human302"));}
 }
 [HarmonyPatch(typeof(RemoteWorkerController),"Update")] public static class WorkerUpdate {
  public struct Sample {public long begin;public int ticks;}
  public static void Prefix(out Sample __state){__state=new Sample{begin=Stopwatch.GetTimestamp(),ticks=Audit.ticks};}
  public static void Postfix(Sample __state){int n=Audit.ticks-__state.ticks;if(n>0)Audit.slices.Add("frame="+Time.frameCount+" ticks="+n+" elapsedMs="+((Stopwatch.GetTimestamp()-__state.begin)*1000.0/Stopwatch.Frequency).ToString("F4",System.Globalization.CultureInfo.InvariantCulture));}
 }
 public class Pending {public string cmd;public string result;public ManualResetEvent done=new ManualResetEvent(false);}
 public class Observe:MonoBehaviour {
  ConcurrentQueue<Pending> queue=new ConcurrentQueue<Pending>();TcpListener listener;bool run=true;
  void Awake(){Audit.mainThread=Thread.CurrentThread.ManagedThreadId;int port=31800;var a=Environment.GetCommandLineArgs();for(int i=0;i<a.Length-1;i++)if(a[i]=="-qa-port")port=int.Parse(a[i+1]);listener=new TcpListener(IPAddress.Loopback,port);listener.Start();new Thread(()=>{while(run){try{var c=listener.AcceptTcpClient();ThreadPool.QueueUserWorkItem(_=>Client(c));}catch{}}}){IsBackground=true}.Start();
   var asm=typeof(RemoteClientController).Assembly;File.WriteAllText(Path.Combine(GenFilePaths.SaveDataFolderPath,"qa-module.txt"),asm.Location+"\nMVID="+asm.ManifestModule.ModuleVersionId+"\nSHA256="+BitConverter.ToString(System.Security.Cryptography.SHA256.Create().ComputeHash(File.ReadAllBytes(asm.Location))).Replace("-",""));}
  void Client(TcpClient c){using(c)using(var r=new StreamReader(c.GetStream(),Encoding.UTF8))using(var w=new StreamWriter(c.GetStream(),new UTF8Encoding(false)){AutoFlush=true}){string s;while((s=r.ReadLine())!=null){var p=new Pending{cmd=s};queue.Enqueue(p);w.WriteLine(p.done.WaitOne(45000)?p.result:"ERROR QA timeout");}}}
  void OnGUI(){Audit.guis++;}
  void Update(){long now=Stopwatch.GetTimestamp();if(Audit.Role=="CLIENT"&&Audit.lastFrameStamp!=0)Audit.frames.Add(DateTime.UtcNow.ToString("o")+"\tframe="+Time.frameCount+"\tgapMs="+((now-Audit.lastFrameStamp)*1000.0/Stopwatch.Frequency).ToString("F4",System.Globalization.CultureInfo.InvariantCulture));Audit.lastFrameStamp=now;while(queue.TryDequeue(out var p)){try{var a=p.cmd.Split(new[]{' '},2);var arg=a.Length>1?a[1]:"";switch(a[0]){
   case "SNAP":p.result=Audit.Snap();break;
   case "DUMP":Audit.Flush();p.result=Audit.Snap();break;
   case "PARSE_HOLD":ParseBarrier.Gate.Reset();ParseBarrier.Armed=true;p.result="ARMED";break;
   case "PARSE_RELEASE":ParseBarrier.Gate.Set();p.result="RELEASED";break;
   case "PARSE_STATUS":p.result="armed="+ParseBarrier.Armed+" waiting="+ParseBarrier.Waiting;break;
   case "LIGHT":p.result=Extended.Light();break;
   case "RESET":RemoteClientController.Instance.ResetFrameMetrics();Audit.frames.Clear();p.result="OK";break;
   case "ASYNC":var ac=Protocols.ParseCommand(Encoding.UTF8.GetString(Convert.FromBase64String(arg)));p.result=RemoteClientController.Instance.SubmitCommandAsync(ac, r=>Audit.Event("QA_ASYNC_RESULT "+Protocols.SerializeResponse(r)),Extended.TimeoutMs).ToString();break;
   case "TIMEOUT":Extended.TimeoutMs=float.Parse(arg);p.result="QA async timeout="+Extended.TimeoutMs;break;
   case "STRESS":p.result=Extended.Stress(int.Parse(arg));break;
   case "HOLD_APPLY":Extended.Hold=int.Parse(arg)!=0;p.result="OK";break;
   case "COALESCED_RACE":Extended.Race=true;p.result="ARMED";break;
   case "RPC":var cmd=Protocols.ParseCommand(Encoding.UTF8.GetString(Convert.FromBase64String(arg)));p.result=Protocols.SerializeResponse(RemoteClientController.Instance.SendCommand(cmd));break;
   case "VALIDATE":var resp=Protocols.ParseResponse(Encoding.UTF8.GetString(Convert.FromBase64String(arg)));var ok=RemoteClientController.Instance.ValidateAndApplySnapshot(resp.Snapshot,out var reason);p.result="OK="+ok+" REASON="+reason+"\t"+Audit.Snap();break;
   case "VIEW_MAP":Current.Game.CurrentMap=Find.Maps.Single(m=>m.uniqueID==int.Parse(arg));p.result=Audit.Snap();break;
   case "EXPECT_MAP":RemoteClientController.Instance.ExpectedMapId=arg;p.result=Audit.Snap();break;
   case "DISCONNECT":RemoteClientController.Instance.Disconnect();p.result=Audit.Snap();break;
   case "METRICS":p.result=new XElement("metrics",RemoteClientController.Instance.PeriodicMetrics.Select(m=>new XElement("sample",new XAttribute("seq",m.Sequence),new XAttribute("tick",m.AuthoritativeTick),new XAttribute("bytes",m.PayloadBytes),new XAttribute("cadenceMs",m.CadenceIntervalMs),new XAttribute("applyMs",m.LoopbackReceiveToApplyMs),new XAttribute("rttMs",m.TotalRoundtripMs),new XAttribute("status",m.ReconcileStatus),new XAttribute("pawns",m.PawnPositions)))).ToString(SaveOptions.DisableFormatting);break;
   case "ROTATE":if(Audit.Role!="WORKER")throw new Exception("Worker QA fault injection only");var v=arg.Split(' ');Audit.Pawn(v[0]).Rotation=new Rot4(int.Parse(v[1]));p.result=Audit.Snap();break;
   case "SEVERITY":var v2=arg.Split(' ');Audit.Pawn(v2[0]).health.hediffSet.hediffs.First(h=>h.def.defName==v2[1]).Severity=float.Parse(v2[2],System.Globalization.CultureInfo.InvariantCulture);p.result=Audit.Snap();break;
   case "PAUSE":if(arg=="1")Find.TickManager.Pause();else Find.TickManager.CurTimeSpeed=TimeSpeed.Normal;p.result=Audit.Snap();break;
   default:p.result="ERROR unknown QA command";break;}}
   catch(Exception ex){p.result="ERROR "+ex;}finally{p.done.Set();}}}
  void OnDestroy(){run=false;try{listener.Stop();Audit.Flush();}catch{}}
 }
}


