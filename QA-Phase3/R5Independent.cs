using RimWorld;
using Verse;
using WarEconomy.Client.Fief;
using WarEconomy.Client.Networking;
using WarEconomy.Common.Packets.Feudal;

static void Check(string name,bool value){Console.WriteLine($"CHECK {name}: {(value?"PASS":"FAIL")}");if(!value)throw new Exception(name);}
// Actual API-shaped OwnedBed property and bool Claim method; no test-only Claimed field.
foreach(string scenario in new[]{"success","reject","throw"}) {
 var old=new Faction{Name="old"};var next=new Faction{Name="new"};
 var map=new Map{Tile=42,Parent=new Thing{Faction=old}};
 var pawn=new Pawn{Faction=old,Map=map};
 var previousBed=pawn.ownership!.OwnedBed;
 pawn.ownership.RejectClaim=scenario=="reject";
 pawn.ownership.ThrowOnClaim=scenario=="throw";
 pawn.workSettings!.ThrowOnEnable=true;
 map.mapPawns.AllPawnsSpawned.Add(pawn);map.listerThings.AllThings.Add(pawn);
 Current.Game=new Game();Current.Game.Maps.Add(map);
 Find.FactionManager=new FactionManager();Find.FactionManager.AllFactionsListForReading.Add(next);
 Messages.Values.Clear();NetworkClient.Instance.Sent.Clear();
 bool success=AtomicFiefTransferExecutor.Execute(new PKT_FiefTransferExecute("QA-owned-bed",42,"new"));
 var result=(PKT_FiefTransferResult)NetworkClient.Instance.Sent.Last();
 Check($"forward_failure_and_faction_recovered_{scenario}",!success && ReferenceEquals(pawn.Faction,old));
 if(scenario=="success") {
  Check("owned_bed_successfully_restored",ReferenceEquals(previousBed,pawn.ownership.OwnedBed));
 } else {
  Check($"REPRO_bed_remains_unowned_{scenario}",pawn.ownership.OwnedBed==null);
  Check($"REPRO_UI_falsely_reports_complete_rollback_{scenario}",Messages.Values.Any(s=>s.Contains("이전 상태로 롤백되었습니다")));
  Check($"REPRO_packet_omits_incomplete_marker_{scenario}",!result.ErrorMessage.Contains("Incomplete rollback"));
 }
}
Console.WriteLine("Original executor with API-shaped fault adapters; not Unity runtime. REPRO PASS confirms remaining defect.");
