using RimWorld;
using Verse;
using WarEconomy.Client.Fief;
using WarEconomy.Client.Networking;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.Feudal;
static void Check(string name,bool ok){Console.WriteLine($"CHECK {name}: {(ok?"PASS":"FAIL")}");if(!ok)throw new Exception(name);}
foreach(string scenario in new[]{"success","area-exception","master-exception"}){
 var old=new Faction{Name="old"};var next=new Faction{Name="new"};
 var map=new Map{Tile=42,Parent=new Thing{Faction=old}};
 var pawn=new Pawn{Faction=old,Map=map};
 object? area=pawn.playerSettings!.AreaRestrictionInPawnCurrentMap,master=pawn.playerSettings.Master;
 pawn.playerSettings.ThrowAreaRestore=scenario=="area-exception";
 pawn.playerSettings.ThrowMasterRestore=scenario=="master-exception";
 pawn.workSettings!.ThrowOnEnable=true;
 map.mapPawns.AllPawnsSpawned.Add(pawn);map.listerThings.AllThings.Add(pawn);
 Current.Game=new Game();Current.Game.Maps.Add(map);
 Find.FactionManager=new FactionManager();Find.FactionManager.AllFactionsListForReading.Add(next);
 Messages.Values.Clear();NetworkClient.Instance.Sent.Clear();
 bool success=AtomicFiefTransferExecutor.Execute(new PKT_FiefTransferExecute("QA-settings",42,"new"));
 var result=(PKT_FiefTransferResult)NetworkClient.Instance.Sent.Last();
 Check($"faction_restored_{scenario}",!success && ReferenceEquals(pawn.Faction,old));
 if(scenario=="success"){
  Check("property_settings_restored",ReferenceEquals(area,pawn.playerSettings.AreaRestrictionInPawnCurrentMap)&&ReferenceEquals(master,pawn.playerSettings.Master));
  Check("clean_rollback_message",Messages.Values.Any(s=>s.Contains("이전 상태로 롤백되었습니다")));
 }else{
  Check($"incomplete_message_{scenario}",!Messages.Values.Any(s=>s.Contains("이전 상태로 롤백되었습니다")) && Messages.Values.Any(s=>s.Contains("일부 객체의 복구가 완료되지 않았습니다")));
  Check($"failure_reason_preserved_{scenario}",result.ErrorMessage.Contains("Incomplete rollback: resync required") && result.ErrorMessage.Contains(scenario=="area-exception"?"Area restriction restore exception":"Master restore exception"));
 }
 byte[] serialized=PacketSerializer.Serialize(result);
 var copy=PacketSerializer.Deserialize<PKT_FiefTransferResult>(serialized[6..])!;
 Check($"result_roundtrip_{scenario}",copy.Success==result.Success && copy.TransferId==result.TransferId && copy.ErrorMessage==result.ErrorMessage);
}
Console.WriteLine("Checks complete. Original executor plus property-shaped fault adapters, not Unity execution.");
