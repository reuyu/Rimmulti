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
namespace QAHarden02 {
 public class ObserverMod:Mod {public ObserverMod(ModContentPack c):base(c){new Harmony("qacodex.remote.harden02.observer").PatchAll();}}
 [StaticConstructorOnStartup] public static class Boot {static Boot(){var o=new GameObject("QAHarden02");UnityEngine.Object.DontDestroyOnLoad(o);o.AddComponent<Observe>();}}
 public static class Audit {
  public static readonly List<string> events=new List<string>();
  public static readonly List<string> slices=new List<string>();
  public static int ticks,draws,guis,rpcs;
  public static string Role=>RemotePresentationMod.Role;
  public static Pawn Pawn(string id){return Find.Maps?.SelectMany(m=>m.mapPawns.AllPawns).FirstOrDefault(p=>p.ThingID==id);}
  public static string State(string id){var p=Pawn(id);return p==null?"missing":$"id={p.ThingID} map={p.Map?.uniqueID} pos={p.Position} draft={p.Drafted} job={p.CurJob?.def?.defName??"None"} rotation={p.Rotation.AsInt}";}
  public static void Event(string label){events.Add(DateTime.UtcNow.ToString("o")+"\tFrame="+Time.frameCount+"\tRole="+Role+"\tGUI="+(UnityEngine.Event.current?.type.ToString()??"null")+"\tReconciling="+RemoteClientController.IsReconciling+"\t"+label);}
  public static XElement PawnState(Pawn p){return new XElement("pawn",new XAttribute("id",p.ThingID),new XAttribute("map",p.Map?.uniqueID??-1),new XAttribute("position",p.Position),new XAttribute("rotation",p.Rotation.AsInt),new XAttribute("drafted",p.Drafted),new XAttribute("job",p.CurJob?.def?.defName??"None"),new XAttribute("jobTarget",p.CurJob?.targetA.ToString()??"None"),new XAttribute("dead",p.Dead),new XAttribute("downed",p.Downed),new XAttribute("health",p.health?.summaryHealth?.SummaryHealthPercent??-1),new XAttribute("selected",Find.Selector?.SelectedObjects.Contains(p)??false),p.health?.hediffSet?.hediffs.Select(h=>new XElement("hediff",new XAttribute("id",h.GetUniqueLoadID()),new XAttribute("def",h.def.defName),new XAttribute("severity",h.Severity),new XAttribute("part",h.Part?.def?.defName??"None"))));}
  public static string Snap(){var c=RemoteClientController.Instance;var w=RemoteWorkerController.Instance;
   var root=new XElement("observation",new XAttribute("role",Role),new XAttribute("G",Find.TickManager?.TicksGame??-1),new XAttribute("map",Find.CurrentMap?.uniqueID??-1),new XAttribute("ticks",ticks),new XAttribute("draws",draws),new XAttribute("guis",guis),new XAttribute("rpcs",rpcs),new XAttribute("graphics",SystemInfo.graphicsDeviceType),new XAttribute("lastSequence",c?.LastAppliedSnapshotSequence??-1),new XAttribute("applied",c?.TotalSnapshotsApplied??0),new XAttribute("rejected",c?.TotalSnapshotsRejected??0),new XAttribute("progression",w?.OperationalProgressionEnabled??false),new XAttribute("paused",Find.TickManager?.Paused??false));
   foreach(var map in Find.Maps??new List<Map>()){
    var node=new XElement("mapState",new XAttribute("id",map.uniqueID),new XAttribute("things",map.spawnedThings.Count),new XAttribute("duplicateIds",map.spawnedThings.GroupBy(t=>t.ThingID).Count(g=>g.Count()>1)));
    foreach(var p in map.mapPawns.AllPawns){node.Add(PawnState(p));if(p.ThingID=="Human302"||p.ThingID=="Human305"){int n=0;foreach(var cell in map.AllCells)n+=map.thingGrid.ThingsListAt(cell).Count(x=>object.ReferenceEquals(x,p));node.Add(new XElement("grid",new XAttribute("pawn",p.ThingID),new XAttribute("references",n)));}}
    root.Add(node);
   }return root.ToString(SaveOptions.DisableFormatting);
  }
  public static void Flush(){var dir=GenFilePaths.SaveDataFolderPath;File.WriteAllLines(Path.Combine(dir,"qa-events.tsv"),events);File.WriteAllLines(Path.Combine(dir,"qa-worker-slices.tsv"),slices);}
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
  public static void Postfix(string json,CommandResponse __result){if(Audit.Role!="CLIENT")return;var b=new StringBuilder();Protocols.SerializeSnapshot(__result.Snapshot,b);Audit.Event("WIRE_RESPONSE status="+__result.Status+" bytes="+Encoding.UTF8.GetByteCount(json)+" snapshotBytes="+Encoding.UTF8.GetByteCount(b.ToString())+" pawns="+__result.Snapshot.Pawns.Count+" seq="+__result.Snapshot.SnapshotSequence+" ownBeforeApply="+Audit.State("Human302"));}
 }
 [HarmonyPatch(typeof(RemoteClientController),nameof(RemoteClientController.ValidateAndApplySnapshot))] public static class Validate {
  public static void Prefix(ReplicationSnapshot snap){Audit.Event("APPLY_ENTER seq="+snap?.SnapshotSequence+" own="+Audit.State("Human302"));}
  public static void Postfix(bool __result,string rejectionReason){Audit.Event("APPLY_EXIT accepted="+__result+" reason="+rejectionReason+" own="+Audit.State("Human302"));}
 }
 [HarmonyPatch(typeof(RemoteWorkerController),"Update")] public static class WorkerUpdate {
  public struct Sample {public long begin;public int ticks;}
  public static void Prefix(out Sample __state){__state=new Sample{begin=Stopwatch.GetTimestamp(),ticks=Audit.ticks};}
  public static void Postfix(Sample __state){int n=Audit.ticks-__state.ticks;if(n>0)Audit.slices.Add("frame="+Time.frameCount+" ticks="+n+" elapsedMs="+((Stopwatch.GetTimestamp()-__state.begin)*1000.0/Stopwatch.Frequency).ToString("F4",System.Globalization.CultureInfo.InvariantCulture));}
 }
 public class Pending {public string cmd;public string result;public ManualResetEvent done=new ManualResetEvent(false);}
 public class Observe:MonoBehaviour {
  ConcurrentQueue<Pending> queue=new ConcurrentQueue<Pending>();TcpListener listener;bool run=true;
  void Awake(){int port=31800;var a=Environment.GetCommandLineArgs();for(int i=0;i<a.Length-1;i++)if(a[i]=="-qa-port")port=int.Parse(a[i+1]);listener=new TcpListener(IPAddress.Loopback,port);listener.Start();new Thread(()=>{while(run){try{var c=listener.AcceptTcpClient();ThreadPool.QueueUserWorkItem(_=>Client(c));}catch{}}}){IsBackground=true}.Start();
   var asm=typeof(RemoteClientController).Assembly;File.WriteAllText(Path.Combine(GenFilePaths.SaveDataFolderPath,"qa-module.txt"),asm.Location+"\nMVID="+asm.ManifestModule.ModuleVersionId+"\nSHA256="+BitConverter.ToString(System.Security.Cryptography.SHA256.Create().ComputeHash(File.ReadAllBytes(asm.Location))).Replace("-",""));}
  void Client(TcpClient c){using(c)using(var r=new StreamReader(c.GetStream(),Encoding.UTF8))using(var w=new StreamWriter(c.GetStream(),new UTF8Encoding(false)){AutoFlush=true}){string s;while((s=r.ReadLine())!=null){var p=new Pending{cmd=s};queue.Enqueue(p);w.WriteLine(p.done.WaitOne(45000)?p.result:"ERROR QA timeout");}}}
  void OnGUI(){Audit.guis++;}
  void Update(){while(queue.TryDequeue(out var p)){try{var a=p.cmd.Split(new[]{' '},2);var arg=a.Length>1?a[1]:"";switch(a[0]){
   case "SNAP":p.result=Audit.Snap();break;
   case "DUMP":Audit.Flush();p.result=Audit.Snap();break;
   case "RPC":var cmd=Protocols.ParseCommand(Encoding.UTF8.GetString(Convert.FromBase64String(arg)));p.result=Protocols.SerializeResponse(RemoteClientController.Instance.SendCommand(cmd));break;
   case "VALIDATE":var resp=Protocols.ParseResponse(Encoding.UTF8.GetString(Convert.FromBase64String(arg)));var ok=RemoteClientController.Instance.ValidateAndApplySnapshot(resp.Snapshot,out var reason);p.result="OK="+ok+" REASON="+reason+"\t"+Audit.Snap();break;
   case "ROTATE":if(Audit.Role!="WORKER")throw new Exception("Worker QA fault injection only");var v=arg.Split(' ');Audit.Pawn(v[0]).Rotation=new Rot4(int.Parse(v[1]));p.result=Audit.Snap();break;
   case "SEVERITY":var v2=arg.Split(' ');Audit.Pawn(v2[0]).health.hediffSet.hediffs.First(h=>h.def.defName==v2[1]).Severity=float.Parse(v2[2],System.Globalization.CultureInfo.InvariantCulture);p.result=Audit.Snap();break;
   case "PAUSE":if(arg=="1")Find.TickManager.Pause();else Find.TickManager.CurTimeSpeed=TimeSpeed.Normal;p.result=Audit.Snap();break;
   default:p.result="ERROR unknown QA command";break;}}
   catch(Exception ex){p.result="ERROR "+ex;}finally{p.done.Set();}}}
  void OnDestroy(){run=false;try{listener.Stop();Audit.Flush();}catch{}}
 }
}
