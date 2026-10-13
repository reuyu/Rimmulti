using System;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Diagnostics;
using System.Xml.Linq;
using HarmonyLib;
using UnityEngine;
using Verse;
using WarEconomy.RemotePresentation.Client;
using WarEconomy.RemotePresentation.Common;
using WarEconomy.RemotePresentation.Worker;
namespace QAHarden05 {
 public static class Extended {
  public static bool Hold,Race;public static float TimeoutMs=4000;public static int sendHigh,resultHigh,maxDrain;
  public static object F(object o,string n)=>o==null?null:AccessTools.Field(o.GetType(),n)?.GetValue(o);
  public static int Count(object o)=>o==null?0:(int)o.GetType().GetProperty("Count").GetValue(o);
  public static void ThreadEvent(string s)=>Audit.events.Enqueue(DateTime.UtcNow.ToString("o")+"\tThread="+Thread.CurrentThread.ManagedThreadId+"\t"+s);
  public static string Light(){var c=RemoteClientController.Instance;return new XElement("light",new XAttribute("utc",DateTime.UtcNow.ToString("o")),new XAttribute("epoch",c?.TransportEpoch??0),new XAttribute("connected",c?.IsConnected??false),new XAttribute("maxFrame",c?.MaxMainThreadFrameMs??0),new XAttribute("pending",Count(F(c,"_cmdSendQueue"))),new XAttribute("results",Count(F(c,"_cmdResultQueue"))),new XAttribute("sendHigh",sendHigh),new XAttribute("resultHigh",resultHigh),new XAttribute("maxDrain",maxDrain),new XAttribute("coalesced",F(c,"_pendingSnapshotToApply")!=null),new XAttribute("coalescedEpoch",F(c,"_pendingSnapshotEpoch")??0),new XAttribute("periodic",c?.PeriodicMetrics.Count??0),new XAttribute("guiHistory",RemoteGuiCommandAdapter.EventHistory.Count),new XAttribute("seq",c?.LastAppliedSnapshotSequence??0),new XAttribute("frame",Time.frameCount),new XAttribute("graphics",SystemInfo.graphicsDeviceType),new XAttribute("resolution",Screen.width+"x"+Screen.height),new XAttribute("ticks",Audit.ticks),Find.Maps?.SelectMany(m=>m.mapPawns.AllPawns).Where(p=>p.ThingID=="Human302"||p.ThingID=="Human305").Select(Audit.PawnState)).ToString(SaveOptions.DisableFormatting);}
  public static string Stress(int n){var c=RemoteClientController.Instance;int admitted=0,rejected=0;for(int i=0;i<n;i++){var cmd=new RemoteTacticalCommand{CommandId="QA_STRESS_"+Guid.NewGuid().ToString("N"),CommandType="PING",Token="Player_A_Token",Generation=1,TacticalSessionId="TAC_SESSION_01"};if(c.SubmitCommandAsync(cmd,r=>Audit.Event("QA_STRESS_RESULT "+r.Status),4000))admitted++;else rejected++;sendHigh=Math.Max(sendHigh,Count(F(c,"_cmdSendQueue")));}return "admitted="+admitted+" rejected="+rejected+" "+Light();}
 }
 [HarmonyPatch(typeof(RemoteClientController),nameof(RemoteClientController.SubmitCommandAsync))] public static class Submit {
  public static void Prefix(RemoteTacticalCommand cmd,out long __state){__state=Stopwatch.GetTimestamp();Audit.rpcs++;Audit.Event("ASYNC_ENTER "+cmd.CommandType+" ID="+cmd.CommandId+" "+Audit.State(cmd.TargetPawnId));}
  public static void Postfix(RemoteTacticalCommand cmd,bool __result,long __state){Audit.Event("ASYNC_EXIT admitted="+__result+" ID="+cmd.CommandId+" epoch="+cmd.TransportEpoch+" callbackMs="+((Stopwatch.GetTimestamp()-__state)*1000.0/Stopwatch.Frequency)+" "+Audit.State(cmd.TargetPawnId));}
 }
 [HarmonyPatch(typeof(RemoteClientController),"ProcessInteractiveCommandOffMainThread")] public static class CommandIO {
  public static void Prefix(RemoteClientController.PendingInteractiveCommand pending,out long __state){__state=Stopwatch.GetTimestamp();Extended.ThreadEvent("NETWORK_BEGIN ID="+pending.Command.CommandId+" epoch="+pending.SentTransportEpoch+" timeout="+pending.TimeoutMs);}
  public static void Postfix(RemoteClientController.PendingInteractiveCommand pending,long __state){Extended.resultHigh=Math.Max(Extended.resultHigh,Extended.Count(Extended.F(RemoteClientController.Instance,"_cmdResultQueue")));Extended.ThreadEvent("NETWORK_END ID="+pending.Command.CommandId+" state="+pending.State+" ms="+((Stopwatch.GetTimestamp()-__state)*1000.0/Stopwatch.Frequency)+" response="+Protocols.SerializeResponse(pending.Response));}
 }
 [HarmonyPatch(typeof(RemoteClientController),nameof(RemoteClientController.ConnectCommandSocket))] public static class Connect {
  public static void Prefix(){Extended.ThreadEvent("CONNECT_SOCKET");}
 }
 [HarmonyPatch(typeof(Protocols),nameof(Protocols.SerializeCommand))] public static class Serialize {
  public static void Prefix(RemoteTacticalCommand cmd){Extended.ThreadEvent("SERIALIZE_COMMAND type="+cmd.CommandType+" id="+cmd.CommandId);}
 }
 [HarmonyPatch(typeof(RemoteClientController),"Update")] public static class ClientUpdate {
  public static bool Prefix(RemoteClientController __instance,out int __state){__state=Extended.Count(Extended.F(__instance,"_cmdResultQueue"));Extended.resultHigh=Math.Max(Extended.resultHigh,__state);
   if(Extended.Race&&Extended.F(__instance,"_pendingSnapshotToApply") is ReplicationSnapshot old){Extended.Race=false;var host=__instance.WorkerHost;var port=__instance.WorkerPort;Audit.Event("COALESCED_BEFORE_DISCONNECT seq="+old.SnapshotSequence+" epoch="+__instance.TransportEpoch);__instance.Disconnect();__instance.ConnectToWorker(host,port);Audit.Event("COALESCED_AFTER_RECONNECT oldseq="+old.SnapshotSequence+" currentEpoch="+__instance.TransportEpoch+" slot="+(Extended.F(__instance,"_pendingSnapshotToApply")!=null));}
   return !Extended.Hold;
  }
  public static void Postfix(RemoteClientController __instance,int __state){int drained=__state-Extended.Count(Extended.F(__instance,"_cmdResultQueue"));Extended.maxDrain=Math.Max(Extended.maxDrain,drained);if(drained>0)Audit.Event("RESULT_DRAIN count="+drained);}
 }
 [HarmonyPatch(typeof(RemoteWorkerController),nameof(RemoteWorkerController.BuildReplicationSnapshot))] public static class WorkerPose {
  public static void Postfix(ReplicationSnapshot __result){var p=Audit.Pawn("Human302");var d=__result.Pawns.FirstOrDefault(x=>x.PawnId=="Human302");if(p==null||d==null)return;Audit.Event("WORKER_POSE seq="+__result.SnapshotSequence+" pos="+p.Position+" next="+p.pather?.nextCell+" moving="+p.pather?.Moving+" nativeRot="+p.Rotation.AsInt+" wireRot="+d.Rotation+" pose="+d.PoseSource+" stance="+p.stances?.curStance?.GetType().Name+" focus="+(p.stances?.curStance is Verse.Stance_Busy b ? b.focusTarg.ToString():"None"));}
 }
}
