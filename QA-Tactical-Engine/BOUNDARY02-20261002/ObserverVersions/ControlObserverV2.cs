using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Linq;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Reflection;
using System.Globalization;
using System.Xml.Linq;
using HarmonyLib;
using UnityEngine;
using Verse;
using RimWorld;
using RimWorld.Planet;
using WarEconomy.WorkerBridge;
namespace QABoundary02 {
 public class ObserverMod:Mod {public ObserverMod(ModContentPack c):base(c){new Harmony("qacodex.boundary02.observe").PatchAll();}}
 [StaticConstructorOnStartup] public static class Boot {static Boot(){var o=new GameObject("Boundary02Observer");UnityEngine.Object.DontDestroyOnLoad(o);o.AddComponent<Observer>();}}
 // These counters observe dispatch and store only QA-owned state, not gameplay objects.
 public class GlobalProbe:GameComponent {public int ticks;public GlobalProbe(Game g){} public override void GameComponentTick(){ticks++;} public override void ExposeData(){Scribe_Values.Look(ref ticks,"boundary02GlobalTicks");}}
 public class WorldProbe:WorldComponent {public int ticks;public WorldProbe(World w):base(w){} public override void WorldComponentTick(){ticks++;} public override void ExposeData(){Scribe_Values.Look(ref ticks,"boundary02WorldTicks");}}
 public class MapProbe:MapComponent {public int ticks,lastGlobalRead;public long lastForeignChronological;public MapProbe(Map m):base(m){} public override void MapComponentTick(){ticks++;lastGlobalRead=Current.Game.GetComponent<GlobalProbe>().ticks;var other=Find.Maps.FirstOrDefault(x=>x!=map);var p=other?.mapPawns?.AllPawns.FirstOrDefault(x=>x.RaceProps.Humanlike);if(p!=null)lastForeignChronological=p.ageTracker.AgeChronologicalTicks;}public override void ExposeData(){Scribe_Values.Look(ref ticks,"boundary02MapTicks");Scribe_Values.Look(ref lastGlobalRead,"boundary02LastGlobalRead");Scribe_Values.Look(ref lastForeignChronological,"boundary02LastForeignChronological");}}
 public static class Audit {
  public static readonly Stopwatch Time=Stopwatch.StartNew();public static int tickCalls;public static readonly List<string> Events=new List<string>();
  public class Frame{public int frame,calls,startG;public double ms;}
  public static readonly Dictionary<int,Frame> Frames=new Dictionary<int,Frame>();
  public static void RecordTick(){tickCalls++;int key=UnityEngine.Time.frameCount;Frame f;if(!Frames.TryGetValue(key,out f)){f=new Frame{frame=key,calls=0,startG=Current.Game?.tickManager?.TicksGame??-1,ms=Time.Elapsed.TotalMilliseconds};Frames.Add(key,f);}f.calls++;}
  public static object Field(object o,string n){if(o==null)return null;for(var t=o.GetType();t!=null;t=t.BaseType){var f=t.GetField(n,BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance);if(f!=null)return f.GetValue(o);}return null;}
  public static string Val(object x){return x==null?"null":Convert.ToString(x,CultureInfo.InvariantCulture);}
  public static XElement Scalars(string name,object o){var e=new XElement(name,new XAttribute("Type",o?.GetType().FullName??"null"));if(o==null)return e;for(var t=o.GetType();t!=null;t=t.BaseType)foreach(var f in t.GetFields(BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.DeclaredOnly)){try{var v=f.GetValue(o);if(v==null||f.FieldType.IsPrimitive||f.FieldType.IsEnum||v is string||v is decimal)e.Add(new XElement("field",new XAttribute("name",f.Name),new XAttribute("value",Val(v))));else if(v is ICollection)e.Add(new XElement("collection",new XAttribute("name",f.Name),new XAttribute("count",((ICollection)v).Count)));}catch{}}return e;}
  public static void Event(string label){try{var line=Val(Time.Elapsed.TotalMilliseconds)+"\t"+label+"\tProgram="+Current.ProgramState+"\tG="+(Current.Game?.tickManager?.TicksGame??-1)+"\tTickCalls="+tickCalls+"\tScope="+ScopedTacticalSession.IsActive+"\tL="+ScopedTacticalSession.TicksSimulated;Events.Add(line);File.AppendAllText(GenFilePaths.SaveDataFolderPath+"/observer-lifecycle.tsv",line+"\n");}catch{}}
  public static XElement PawnState(Pawn p,bool chrono){var e=new XElement("pawn",new XAttribute("id",p.ThingID),new XAttribute("def",p.def.defName),new XAttribute("dead",p.Dead),new XAttribute("biological",p.ageTracker?.AgeBiologicalTicks??-1),new XAttribute("chronological",chrono?(p.ageTracker?.AgeChronologicalTicks??-1):-1),new XAttribute("bed",p.ownership?.OwnedBed?.ThingID??"null"),new XAttribute("master",p.playerSettings?.Master?.ThingID??"null"),new XAttribute("pos",p.Position),new XAttribute("faction",p.Faction?.GetUniqueLoadID()??"null"));
   e.Add(Scalars("age",p.ageTracker),Scalars("job",p.CurJob),Scalars("driver",p.jobs?.curDriver));
   if(p.needs!=null)foreach(var n in p.needs.AllNeeds)e.Add(new XElement("need",new XAttribute("def",n.def.defName),new XAttribute("value",Val(n.CurLevel))));
   if(p.health?.hediffSet!=null)foreach(var h in p.health.hediffSet.hediffs)e.Add(new XElement("hediff",new XAttribute("id",h.GetUniqueLoadID()),new XAttribute("def",h.def.defName),new XAttribute("part",h.Part?.def?.defName??"null"),new XAttribute("partIndex",h.Part?.Index??-1),new XAttribute("severity",Val(h.Severity)),Scalars("state",h)));
   if(p.equipment!=null)foreach(var w in p.equipment.AllEquipmentListForReading)e.Add(new XElement("weapon",new XAttribute("id",w.ThingID),new XAttribute("def",w.def.defName),new XAttribute("hp",w.HitPoints)));
   if(p.apparel!=null)foreach(var a in p.apparel.WornApparel)e.Add(new XElement("apparel",new XAttribute("id",a.ThingID),new XAttribute("def",a.def.defName),new XAttribute("hp",a.HitPoints)));
   if(p.inventory!=null)foreach(var a in p.inventory.innerContainer)e.Add(new XElement("inventory",new XAttribute("id",a.ThingID),new XAttribute("def",a.def.defName),new XAttribute("count",a.stackCount),new XAttribute("hp",a.HitPoints),Scalars("rot",a.TryGetComp<CompRottable>())));
   if(p.training!=null)foreach(var d in DefDatabase<TrainableDef>.AllDefsListForReading)e.Add(new XElement("training",new XAttribute("def",d.defName),new XAttribute("learned",p.training.HasLearned(d))));
   return e;
  }
  public static string Snapshot(){var root=new XElement("observation",new XAttribute("program",Current.ProgramState),new XAttribute("G",Current.Game?.tickManager?.TicksGame??-1),new XAttribute("L",ScopedTacticalSession.TicksSimulated),new XAttribute("scope",ScopedTacticalSession.IsActive),new XAttribute("tickCalls",tickCalls));if(Current.Game==null)return root.ToString(SaveOptions.DisableFormatting);
   bool chrono=Current.ProgramState==ProgramState.Playing;root.Add(Scalars("clock",Current.Game.tickManager));
   if(Current.Game.components!=null)foreach(var c in Current.Game.components)root.Add(Scalars("gameComponent",c));
   var world=Current.Game.World;if(world!=null){root.Add(Scalars("world",world),Scalars("factionManager",Find.FactionManager),Scalars("history",Find.History),Scalars("tales",Find.TaleManager),Scalars("worldPawns",Find.WorldPawns));var components=Field(world,"components") as IEnumerable;if(components!=null)foreach(var c in components)root.Add(Scalars("worldComponent",c));foreach(var f in Find.FactionManager.AllFactionsListForReading){var fx=Scalars("faction",f);fx.SetAttributeValue("id",f.GetUniqueLoadID());var relations=Field(f,"relations") as IEnumerable;if(relations!=null)foreach(var r in relations)fx.Add(Scalars("relation",r));root.Add(fx);}foreach(var obj in Find.WorldObjects.AllWorldObjects){var wo=Scalars("worldObject",obj);wo.SetAttributeValue("id",obj.GetUniqueLoadID());wo.SetAttributeValue("tile",obj.Tile);if(obj is Caravan ca){wo.Add(Scalars("path",ca.pather));foreach(var p in ca.PawnsListForReading)wo.Add(PawnState(p,chrono));}root.Add(wo);}foreach(var p in Find.WorldPawns.AllPawnsAliveOrDead)root.Add(new XElement("offMapPawn",PawnState(p,chrono)));}
   foreach(var map in Current.Game.Maps){var m=new XElement("map",new XAttribute("index",map.Index),new XAttribute("id",map.uniqueID));if(map.components!=null)foreach(var c in map.components)m.Add(Scalars("mapComponent",c));if(map.mapPawns!=null)foreach(var p in map.mapPawns.AllPawns)m.Add(PawnState(p,chrono));if(map.listerThings!=null)foreach(var t in map.listerThings.AllThings){if(t is Plant plant)m.Add(new XElement("plant",new XAttribute("id",plant.ThingID),new XAttribute("def",plant.def.defName),new XAttribute("age",Val(Field(plant,"ageInt"))),new XAttribute("ageFallback",Val(Field(plant,"age"))),new XAttribute("growth",Val(plant.Growth)),new XAttribute("isCrop",plant.IsCrop),new XAttribute("sowable",plant.def.plant?.Sowable??false),new XAttribute("pos",plant.Position)));if(t is Building build){var e=new XElement("building",new XAttribute("id",t.ThingID),new XAttribute("def",t.def.defName),new XAttribute("hp",t.HitPoints));var battery=t.TryGetComp<CompPowerBattery>();if(battery!=null)e.SetAttributeValue("power",Val(battery.StoredEnergy));if(t is Building_Bed bed)foreach(var owner in bed.OwnersForReading)e.Add(new XElement("owner",owner.ThingID));if(t is Building_WorkTable table)foreach(var bill in table.BillStack.Bills)e.Add(new XElement("bill",new XAttribute("id",bill.GetUniqueLoadID()),new XAttribute("recipe",bill.recipe?.defName??"null"),new XAttribute("validRecipe",table.def.AllRecipes.Contains(bill.recipe)),Scalars("state",bill)));if(t is Building_Casket cas){e.SetAttributeValue("contained",cas.ContainedThing?.ThingID??"null");if(cas.ContainedThing is Corpse body)e.Add(new XElement("corpse",new XAttribute("id",body.ThingID),PawnState(body.InnerPawn,chrono)));}m.Add(e);}}
   root.Add(m);}return root.ToString(SaveOptions.DisableFormatting);
  }
 }
 [HarmonyPatch(typeof(TickManager),nameof(TickManager.DoSingleTick))] public static class TickObserver {static void Prefix(){Audit.RecordTick();}}
 [HarmonyPatch(typeof(Game),nameof(Game.FinalizeInit))] public static class InitObserver {static void Prefix(){Audit.Event("FinalizeInit.Prefix");try{File.WriteAllText(GenFilePaths.SaveDataFolderPath+"/observer-finalize-before.xml",Audit.Snapshot());}catch(Exception e){File.WriteAllText(GenFilePaths.SaveDataFolderPath+"/observer-finalize-before-error.txt",e.ToString());}} [HarmonyPriority(Priority.Last)] static void Postfix(){Audit.Event("FinalizeInit.Postfix.AfterPause");try{File.WriteAllText(GenFilePaths.SaveDataFolderPath+"/observer-finalize-after.xml",Audit.Snapshot());}catch(Exception e){File.WriteAllText(GenFilePaths.SaveDataFolderPath+"/observer-finalize-after-error.txt",e.ToString());}}}
 [HarmonyPatch] public static class LoaderObserver {static IEnumerable<MethodBase> TargetMethods(){return typeof(GameDataSaveLoader).GetMethods(BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic).Where(x=>x.Name=="LoadGame");}static void Prefix(){Audit.Event("Loader.Prefix");}static void Postfix(){Audit.Event("Loader.Postfix.Queued");}}
 [HarmonyPatch] public static class CommandObserver {static MethodBase TargetMethod(){return typeof(WorkerBridgeComponent).GetMethod("ProcessCommandMainThread",BindingFlags.NonPublic|BindingFlags.Instance);}static void Prefix(string cmd){if(cmd=="LOAD_SAVE")Audit.Event("LOAD.request");}static void Postfix(string cmd){if(cmd=="LOAD_SAVE")Audit.Event("LOAD.response");}}
 public class Observer:MonoBehaviour {
  class Req{public string cmd;public TaskCompletionSource<string> answer=new TaskCompletionSource<string>();}
  readonly ConcurrentQueue<Req> queue=new ConcurrentQueue<Req>();TcpListener listener;bool running=true;string previous="";
  void Awake(){int port=31600;string arg;if(GenCommandLine.TryGetCommandLineArg("obsport",out arg))int.TryParse(arg,out port);listener=new TcpListener(IPAddress.Loopback,port);listener.Start();new Thread(()=>{while(running){try{var c=listener.AcceptTcpClient();new Thread(()=>Client(c)){IsBackground=true}.Start();}catch{break;}}}){IsBackground=true}.Start();}
  void Client(TcpClient c){using(c)using(var s=c.GetStream())using(var r=new StreamReader(s))using(var w=new StreamWriter(s,new UTF8Encoding(false)){AutoFlush=true}){try{string line;while((line=r.ReadLine())!=null){var req=new Req{cmd=line};queue.Enqueue(req);if(req.answer.Task.Wait(90000)){w.WriteLine(req.answer.Task.Result);w.WriteLine("---END---");}}}catch{}}}
  void Update(){var bridge=UnityEngine.Object.FindObjectOfType<WorkerBridgeComponent>();var state=Audit.Val(Audit.Field(bridge,"lifecycleState"))+"/"+Current.ProgramState;if(state!=previous){previous=state;Audit.Event("State="+state);}Req r;if(!queue.TryDequeue(out r))return;try{var words=r.cmd.Split(' ');string result;
   if(words[0]=="SNAP")result=Audit.Snapshot();
   else if(words[0]=="EVENTS")result=string.Join("\n",Audit.Events);
   else if(words[0]=="FRAME_RESET"){Audit.Frames.Clear();result="RESET";}
   else if(words[0]=="FRAME_STATS")result=string.Join("\n",Audit.Frames.Values.OrderBy(f=>f.frame).Select(f=>f.frame+","+Audit.Val(f.ms)+","+f.calls+","+f.startG));
   else if(words[0]=="BLOCKQUEUE"){int duration=int.Parse(words[1]);bool sampling=true;var counts=new List<string>();var rq=Audit.Field(bridge,"requestQueue");var countProp=rq.GetType().GetProperty("Count");var sampler=new Thread(()=>{while(sampling){counts.Add(Audit.Val(Audit.Time.Elapsed.TotalMilliseconds)+","+countProp.GetValue(rq,null));Thread.Sleep(1);}}){IsBackground=true};sampler.Start();File.WriteAllText(GenFilePaths.SaveDataFolderPath+"/observer-block-entered.txt",Audit.Val(Audit.Time.Elapsed.TotalMilliseconds));Thread.Sleep(duration);sampling=false;sampler.Join();File.WriteAllLines(GenFilePaths.SaveDataFolderPath+"/observer-queue-depth.csv",counts);result="UNBLOCKED_QUEUE_SAMPLED";}
   else if(words[0]=="BLOCK"){File.WriteAllText(GenFilePaths.SaveDataFolderPath+"/observer-block-entered.txt",Audit.Val(Audit.Time.Elapsed.TotalMilliseconds));Thread.Sleep(int.Parse(words[1]));result="UNBLOCKED";}
   else if(words[0]=="THREADS"){int a,b;ThreadPool.GetMinThreads(out a,out b);int oldA=a,oldB=b;if(words.Length>1)ThreadPool.SetMinThreads(int.Parse(words[1]),b);ThreadPool.GetMinThreads(out a,out b);result="MinWorkerBefore="+oldA+",MinIOBefore="+oldB+",MinWorkerNow="+a+",MinIONow="+b;}
   else if(words[0]=="CARAVAN"){var pawn=PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist,Faction.OfPlayer);var tile=Find.Maps[0].Tile;var method=typeof(CaravanMaker).GetMethods(BindingFlags.Static|BindingFlags.Public).First(x=>x.Name=="MakeCaravan"&&x.GetParameters().Length==4);var caravan=(Caravan)method.Invoke(null,new object[]{new List<Pawn>{pawn},Faction.OfPlayer,tile,true});var layer=tile.Layer;var neighbors=new List<PlanetTile>();layer.GetTileNeighbors(tile,neighbors);var next=neighbors.First(x=>!Find.World.Impassable(x));var start=caravan.pather.GetType().GetMethods().First(x=>x.Name=="StartPath");var pars=start.GetParameters();var args=new object[pars.Length];args[0]=next;for(int i=1;i<pars.Length;i++)args[i]=pars[i].ParameterType==typeof(bool)?(object)true:pars[i].HasDefaultValue?pars[i].DefaultValue:null;start.Invoke(caravan.pather,args);result="CARAVAN="+caravan.GetUniqueLoadID()+" Pawn="+pawn.ThingID+" Tile="+tile+" Next="+next+" Signature="+start;}
   else result="UNKNOWN";r.answer.TrySetResult(result);
  }catch(Exception e){r.answer.TrySetResult("OBSERVER_ERROR: "+e);}}
  void OnDestroy(){running=false;try{listener.Stop();}catch{}}
 }
}
