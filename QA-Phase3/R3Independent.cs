using System.Net;
using System.Net.Sockets;
using System.Reflection;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.Auth;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Packets.Visit;
using WarEconomy.Common.Packets.World;
using WarEconomy.Server.Managers;
using WarEconomy.Server.Network;
using WarEconomy.Client.Fief;
using WarEconomy.Client.Networking;
using Verse;
using RimWorld;

static void Check(string name,bool expected) {Console.WriteLine($"CHECK {name}: {(expected?"PASS":"FAIL")}");if(!expected)throw new Exception(name);}
foreach(bool callbackFailure in new[]{false,true}) {
 var old=new Faction{Name="old"}; var next=new Faction{Name="next"};
 var map=new Map{Tile=42,Parent=new Thing{Faction=old}};
 var pawn=new Pawn{Faction=old,Map=map,ThrowAfterFactionMutation=callbackFailure};
 pawn.workSettings!.ThrowOnEnable=!callbackFailure;
 map.mapPawns.AllPawnsSpawned.Add(pawn); map.listerThings.AllThings.Add(pawn);
 Current.Game=new Game();Current.Game.Maps.Add(map);
 Find.FactionManager=new FactionManager();Find.FactionManager.AllFactionsListForReading.Add(next);
 bool success=AtomicFiefTransferExecutor.Execute(new PKT_FiefTransferExecute("QA",42,"next"));
 Check($"REPRO_rollback_misses_mutated_pawn_callback_{callbackFailure}",!success && ReferenceEquals(pawn.Faction,next) && ReferenceEquals(map.ParentFaction,old));
 var result=(PKT_FiefTransferResult)NetworkClient.Instance.Sent.Last();
 Check($"REPRO_failure_claims_zero_changes_callback_{callbackFailure}",!result.Success && result.TransferredPawnsCount==0);
}
var manager=new FeudalManager();
var fief=new SettlementData("fief","fief",42,"old","owner",NobilityTitle.Baron);manager.RegisterSettlement(fief);
manager.ExecuteFiefTransfer(new PKT_FiefTransferOffer("fief","owner","new",NobilityTitle.Baron,"next","tx-current"),1,"owner-session");
manager.ProcessFiefTransferResult(new PKT_FiefTransferResult("fief",42,true,1,0),"owner-session");
Check("REPRO_missing_transfer_id_commits_current_pending",fief.LordPlayerId=="new");
int syncEvents=0;
manager.OnSettlementListUpdated += _=>syncEvents++;
for(int i=0;i<10;i++)manager.RegisterSettlement(fief);
Check("REPRO_unchanged_registration_emits_sync_every_time",syncEvents==10);
Console.WriteLine($"unchanged_registrations=10, sync_events={syncEvents}; bounded check of sync/register feedback path");

var server=new TcpNetworkServer();server.Start(0);
try {
 int port=((IPEndPoint)((TcpListener)typeof(TcpNetworkServer).GetField("_listener",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(server)!).LocalEndpoint).Port;
 Console.WriteLine($"isolated_port={port}; production_7777_untouched");
 FeudalManager.Instance.RegisterSettlement(new SettlementData("owned","Owned",101,"hf","host",NobilityTitle.Baron));
 using var visitor=new TcpClient();await visitor.ConnectAsync(IPAddress.Loopback,port);
 using var host=new TcpClient();await host.ConnectAsync(IPAddress.Loopback,port);
 using var observer=new TcpClient();await observer.ConnectAsync(IPAddress.Loopback,port);
 foreach(var pair in new[]{(visitor,"visitor"),(host,"host"),(observer,"observer")}) {await Send(pair.Item1,new PKT_PlayerHandshake(pair.Item2,"1.6",pair.Item2));await Read(pair.Item1);}
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("cancel-other","visitor","vf","owned")));await Read(host);
 await Send(observer,new PKT_VisitCancel("cancel-other","visitor","owned"));
 Check("REPRO_unrelated_session_cancels_request",(await Read(host)).header==PacketHeader.VisitCancel);
 // Registration has no owner check; reconnect/game registration can replace committed owner too.
 await Send(observer,new PKT_SettlementRegister(new SettlementData("owned","Overwrite",101,"xf","observer",NobilityTitle.Baron)));
 // Same-stream next request is a processing barrier, avoiding arbitrary delay assertions.
 await Send(observer,new PKT_VisitRequest(new VisitRequestData("barrier","observer","xf","unregistered-NPC")));
 await Read(observer);
 Check("REPRO_registration_overwrites_other_owner",FeudalManager.Instance.GetSettlement("owned")!.LordPlayerId=="observer");
} finally {server.Stop();}
Console.WriteLine("REPRO PASS confirms remaining defects, not release acceptance. Engine boundary tests use fault-injection stubs.");
static async Task Send<T>(TcpClient c,T packet)where T:IPacket {using var t=new CancellationTokenSource(5000);await c.GetStream().WriteAsync(PacketSerializer.Serialize(packet),t.Token);}
static async Task<(PacketHeader header,byte[] body)> Read(TcpClient c){using var t=new CancellationTokenSource(5000);var h=new byte[6];await c.GetStream().ReadExactlyAsync(h,t.Token);int n=BitConverter.ToInt32(h,2);if(n<0||n>1048576)throw new Exception("frame");var b=new byte[n];await c.GetStream().ReadExactlyAsync(b,t.Token);return((PacketHeader)BitConverter.ToUInt16(h),b);}
