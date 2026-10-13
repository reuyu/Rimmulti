using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using Verse;
using WarEconomy.WorkerBridge;
namespace QAEngine02 {
 public class ProbeMod : Mod {public ProbeMod(ModContentPack c):base(c){} }
 [StaticConstructorOnStartup] public static class Boot {static Boot(){var g=new GameObject("QAProbe");UnityEngine.Object.DontDestroyOnLoad(g);g.AddComponent<Probe>();}}
 public class GameProbe:GameComponent {public int ticks;public GameProbe(Game g){} public override void GameComponentTick(){ticks++;}public override void ExposeData(){Scribe_Values.Look(ref ticks,"qaGlobalTicks");}}
 public class MapProbe:MapComponent {public int ticks;public MapProbe(Map m):base(m){}public override void MapComponentTick(){ticks++;}public override void ExposeData(){Scribe_Values.Look(ref ticks,"qaMapTicks");}}
 public class Probe:MonoBehaviour {
  class Request{public string cmd;public TaskCompletionSource<string> result=new TaskCompletionSource<string>();}
  ConcurrentQueue<Request> queue=new ConcurrentQueue<Request>();TcpListener listener;volatile bool running=true;
  void Awake(){int port=30340;string s;if(GenCommandLine.TryGetCommandLineArg("qaport",out s))int.TryParse(s,out port);listener=new TcpListener(IPAddress.Loopback,port);listener.Start();new Thread(()=>{while(running){try{var c=listener.AcceptTcpClient();ThreadPool.QueueUserWorkItem(_=>Client(c));}catch{break;}}}){IsBackground=true}.Start();}
  void Client(TcpClient c){using(c)using(var s=c.GetStream())using(var r=new StreamReader(s))using(var w=new StreamWriter(s,new UTF8Encoding(false)){AutoFlush=true}){try{string l;while((l=r.ReadLine())!=null){var q=new Request{cmd=l};queue.Enqueue(q);if(q.result.Task.Wait(60000)){w.WriteLine(q.result.Task.Result);w.WriteLine("---END---");}}}catch{}}}
  void Update(){Request q;if(!queue.TryDequeue(out q))return;try{var p=q.cmd.Split(' ');string ans="";if(p[0]=="SNAP"){
    var b=new StringBuilder();b.AppendLine("Tick="+Find.TickManager.TicksGame+" GlobalProbe="+Current.Game.GetComponent<GameProbe>().ticks);
    foreach(var m in Find.Maps){b.AppendLine("Map="+m.Index+" MapProbe="+m.GetComponent<MapProbe>().ticks);foreach(var pawn in m.mapPawns.AllPawns){if(pawn.RaceProps.Humanlike)b.AppendLine(pawn.ThingID+" Chronological="+pawn.ageTracker.AgeChronologicalTicks+" Biological="+pawn.ageTracker.AgeBiologicalTicks+" Food="+pawn.needs.food.CurLevel+" Job="+pawn.CurJob?.def.defName);}
     foreach(var plant in m.thingGrid.ThingsListAt(new IntVec3(145,0,145)).OfType<RimWorld.Plant>())b.AppendLine("GridPlant="+plant.ThingID+" Def="+plant.def.defName+" Growth="+plant.Growth);
     foreach(var thing in m.listerThings.AllThings.Where(x=>x.def.defName=="Fire"))b.AppendLine("Fire="+thing.ThingID+" HP="+thing.HitPoints);
    }
    ans=b.ToString();
   }else if(p[0]=="BLOCK"){File.WriteAllText(GenFilePaths.SaveDataFolderPath+"/qa-block-entered.txt",DateTime.UtcNow.ToString("O"));Thread.Sleep(int.Parse(p[1]));ans="UNBLOCKED";
   }else if(p[0]=="ECOLOGY"){bool prev=DebugSettings.fastEcology;try{DebugSettings.fastEcology=true;Find.TickManager.DoSingleTick();ans="ECOLOGY_DONE";}finally{DebugSettings.fastEcology=prev;}
   }else if(p[0]=="RESUME_UNSCOPED"){var m=ScopedTacticalSession.TargetMap;ScopedTacticalSession.Deactivate();try{for(int i=0;i<int.Parse(p[1]);i++)Find.TickManager.DoSingleTick();ans="UNSCOPED_DONE";}finally{ScopedTacticalSession.Activate(m);}
   }else ans="UNKNOWN";q.result.TrySetResult(ans);}catch(Exception ex){q.result.TrySetResult("ERROR: "+ex);}}
  void OnDestroy(){running=false;try{listener.Stop();}catch{}}
 }
}
