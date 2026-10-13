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
using System.Xml.Linq;
using HarmonyLib;
using UnityEngine;
using Verse;
using Verse.AI;
using RimWorld;
using WarEconomy.RemotePresentation;
using WarEconomy.RemotePresentation.Common;
using WarEconomy.RemotePresentation.Client;
namespace QARemote {
 public class ObserveMod:Mod {public ObserveMod(ModContentPack c):base(c){new Harmony("qacodex.remote.observation").PatchAll();}}
 [StaticConstructorOnStartup] public static class Boot {static Boot(){var o=new GameObject("QARemoteObserver");UnityEngine.Object.DontDestroyOnLoad(o);o.AddComponent<Observe>();}}
 public static class Audit {
  public static int rpcCalls,tickCalls,drawCalls,dynamicDrawCalls,guiCalls;
  public static readonly List<string> events=new List<string>();
  public static object Field(object o,string n){return o==null?null:AccessTools.Field(o.GetType(),n)?.GetValue(o);}
  public static void Event(string label){try{string e=DateTime.UtcNow.ToString("o")+"\tFrame="+Time.frameCount+"\tRole="+RemotePresentationMod.Role+"\tGUI="+(UnityEngine.Event.current?.type.ToString()??"null")+"\t"+label;events.Add(e);File.AppendAllText(Path.Combine(GenFilePaths.SaveDataFolderPath,"qa-events.tsv"),e+"\n");}catch{}}
  public static XElement PawnState(Pawn p){return new XElement("pawn",new XAttribute("id",p.ThingID),new XAttribute("position",p.Position),new XAttribute("drafted",p.Drafted),new XAttribute("job",p.CurJob?.def?.defName??"null"),new XAttribute("dead",p.Dead),new XAttribute("downed",p.Downed),new XAttribute("health",p.health?.summaryHealth?.SummaryHealthPercent??-1),new XAttribute("selected",Find.Selector?.SelectedObjects.Contains(p)??false),p.health?.hediffSet?.hediffs.Select(h=>new XElement("hediff",new XAttribute("id",h.GetUniqueLoadID()),new XAttribute("def",h.def.defName),new XAttribute("severity",h.Severity),new XAttribute("part",h.Part?.def?.defName??"null"))));}
  public static string Snap(){var e=new XElement("observation",new XAttribute("role",RemotePresentationMod.Role),new XAttribute("program",Current.ProgramState),new XAttribute("G",Current.Game?.tickManager?.TicksGame??-1),new XAttribute("rpcCalls",rpcCalls),new XAttribute("tickCalls",tickCalls),new XAttribute("drawCalls",drawCalls),new XAttribute("dynamicDrawCalls",dynamicDrawCalls),new XAttribute("guiCalls",guiCalls),new XAttribute("graphics",SystemInfo.graphicsDeviceType),new XAttribute("resolution",Screen.width+"x"+Screen.height),new XAttribute("camera",Find.CameraDriver?.MapPosition.ToString()??"null"));
   if(Find.CurrentMap!=null){var map=Find.CurrentMap;e.Add(new XAttribute("map",map.uniqueID));e.Add(new XAttribute("spawnedThings",map.spawnedThings.Count));e.Add(new XAttribute("duplicateSpawnedThingIds",map.spawnedThings.GroupBy(t=>t.ThingID).Count(g=>g.Count()>1)));foreach(var p in map.mapPawns.AllPawns){e.Add(PawnState(p));int n=0;foreach(var c in map.AllCells)n+=map.thingGrid.ThingsListAt(c).Count(x=>object.ReferenceEquals(x,p));e.Add(new XElement("grid",new XAttribute("pawn",p.ThingID),new XAttribute("references",n)));}}return e.ToString(SaveOptions.DisableFormatting);}
 }
 [HarmonyPatch(typeof(TickManager),nameof(TickManager.DoSingleTick))]public static class Ticks {public static void Prefix(){Audit.tickCalls++;}}
 [HarmonyPatch(typeof(MapDrawer),nameof(MapDrawer.DrawMapMesh))]public static class Draw {public static void Prefix(){Audit.drawCalls++;}}
 [HarmonyPatch]public static class DynDraw {public static IEnumerable<MethodBase> TargetMethods(){return AccessTools.GetDeclaredMethods(typeof(DynamicDrawManager)).Where(m=>m.Name=="DrawDynamicThings");}public static void Prefix(){Audit.dynamicDrawCalls++;}}
 [HarmonyPatch(typeof(RemoteClientController),nameof(RemoteClientController.SendCommand))]public static class Rpc {public static void Prefix(RemoteTacticalCommand cmd){Audit.rpcCalls++;Audit.Event("RPC "+Protocols.SerializeCommand(cmd));}public static void Postfix(CommandResponse __result){Audit.Event("RPC_REPLY "+Protocols.SerializeResponse(__result));}}
 [HarmonyPatch(typeof(Pawn_DraftController),"Drafted",MethodType.Setter)]public static class Draft {public static void Prefix(Pawn_DraftController __instance,bool value){var p=Audit.Field(__instance,"pawn") as Pawn;Audit.Event("DRAFT_SET Pawn="+p?.ThingID+" Value="+value);}}
 [HarmonyPatch]public static class Jobs {public static IEnumerable<MethodBase> TargetMethods(){return AccessTools.GetDeclaredMethods(typeof(Pawn_JobTracker)).Where(m=>m.Name=="TryTakeOrderedJob");}public static void Prefix(Pawn_JobTracker __instance,Job __0){var p=Audit.Field(__instance,"pawn") as Pawn;Audit.Event("ORDER_JOB Pawn="+p?.ThingID+" Job="+__0?.def?.defName);}}
 [HarmonyPatch]public static class GizmoInput {public static IEnumerable<MethodBase> TargetMethods(){return AccessTools.GetDeclaredMethods(typeof(Command_Toggle)).Where(m=>m.Name=="ProcessInput");}public static void Prefix(Command_Toggle __instance){Audit.Event("GIZMO_PROCESS Label="+__instance.defaultLabel);}}
 public class Pending{public string cmd;public string result;public ManualResetEvent done=new ManualResetEvent(false);}
 public class Observe:MonoBehaviour {
  ConcurrentQueue<Pending> queue=new ConcurrentQueue<Pending>();TcpListener listener;bool run=true;
  void Awake(){int port=31700;var args=Environment.GetCommandLineArgs();for(int i=0;i<args.Length-1;i++)if(args[i]=="-qa-port")port=int.Parse(args[i+1]);listener=new TcpListener(IPAddress.Loopback,port);listener.Start();new Thread(()=>{while(run){try{var c=listener.AcceptTcpClient();ThreadPool.QueueUserWorkItem(_=>Client(c));}catch{}}}){IsBackground=true}.Start();
   var a=typeof(RemoteClientController).Assembly;File.WriteAllText(Path.Combine(GenFilePaths.SaveDataFolderPath,"qa-module.txt"),a.Location+"\nMVID="+a.ManifestModule.ModuleVersionId+"\nSHA256="+BitConverter.ToString(System.Security.Cryptography.SHA256.Create().ComputeHash(File.ReadAllBytes(a.Location))).Replace("-",""));}
  void Client(TcpClient c){using(c)using(var r=new StreamReader(c.GetStream(),Encoding.UTF8))using(var w=new StreamWriter(c.GetStream(),new UTF8Encoding(false)){AutoFlush=true}){string s;while((s=r.ReadLine())!=null){var p=new Pending{cmd=s};queue.Enqueue(p);w.WriteLine(p.done.WaitOne(60000)?p.result:"ERROR QA timeout");}}}
  void OnGUI(){Audit.guiCalls++;}
  void Update(){while(queue.TryDequeue(out var p)){try{var a=p.cmd.Split(new[]{' '},2);string arg=a.Length>1?a[1]:"";switch(a[0]){
   case "SNAP":p.result=Audit.Snap();break;
   case "RPC":var cmd=Protocols.ParseCommand(Encoding.UTF8.GetString(Convert.FromBase64String(arg)));p.result=Protocols.SerializeResponse(RemoteClientController.Instance.SendCommand(cmd));break;
   case "LOCAL_TICKS":int n=int.Parse(arg);for(int i=0;i<n;i++)Find.TickManager.DoSingleTick();p.result=Audit.Snap();break;
   case "PERTURB":var v=arg.Split(' ');var pawn=Find.CurrentMap.mapPawns.AllPawns.First(x=>x.ThingID==v[0]);Find.Selector.Select(pawn);pawn.Position=new IntVec3(int.Parse(v[1]),0,int.Parse(v[2]));p.result=Audit.Snap();break;
   case "SEVERITY":var v2=arg.Split(' ');var pawn2=Find.CurrentMap.mapPawns.AllPawns.First(x=>x.ThingID==v2[0]);pawn2.health.hediffSet.hediffs.First().Severity=float.Parse(v2[1],System.Globalization.CultureInfo.InvariantCulture);p.result=Audit.Snap();break;
   case "RECONCILE":var response=Protocols.ParseResponse(Encoding.UTF8.GetString(Convert.FromBase64String(arg)));RemoteClientController.Instance.ReconcileMirrorMap(response.Snapshot);p.result=Audit.Snap();break;
   case "FOCUS":var focus=Find.CurrentMap.mapPawns.AllPawns.First(x=>x.ThingID==arg);CameraJumper.TryJump(focus);Find.Selector.Select(focus);p.result=Audit.Snap();break;
   case "EVENTS":p.result=string.Join("\\n",Audit.events);break;
   default:p.result="ERROR unknown QA command";break;}}
   catch(Exception e){p.result="ERROR "+e;}finally{p.done.Set();}}}
  void OnDestroy(){run=false;try{listener.Stop();}catch{}}
 }
}
