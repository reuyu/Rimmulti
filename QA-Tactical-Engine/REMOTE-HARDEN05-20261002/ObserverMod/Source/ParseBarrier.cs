using System;
using System.Threading;
using HarmonyLib;
using WarEconomy.RemotePresentation;
using WarEconomy.RemotePresentation.Common;
namespace QAHarden05 {
 public static class ParseBarrier {public static volatile bool Armed,Waiting;public static ManualResetEvent Gate=new ManualResetEvent(true);}
 [HarmonyPatch(typeof(Protocols),nameof(Protocols.ParseResponse))] public static class ReceiveBarrier {
  [HarmonyPriority(Priority.Last)] public static void Postfix(CommandResponse __result){if(RemotePresentationMod.Role=="CLIENT"&&ParseBarrier.Armed&&__result?.Snapshot!=null&&(__result.CommandId??"").StartsWith("AUTO_REP_")){ParseBarrier.Armed=false;ParseBarrier.Waiting=true;Extended.ThreadEvent("PARSED_OLD_RESPONSE_BARRIER seq="+__result.Snapshot.SnapshotSequence+" command="+__result.CommandId);ParseBarrier.Gate.WaitOne(20000);ParseBarrier.Waiting=false;Extended.ThreadEvent("PARSED_OLD_RESPONSE_RELEASE seq="+__result.Snapshot.SnapshotSequence);}}
 }
}
