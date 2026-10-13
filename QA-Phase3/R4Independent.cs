using System.Net;
using System.Net.Sockets;
using System.Reflection;
using RimWorld;
using Verse;
using WarEconomy.Client.Fief;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.Auth;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Packets.Visit;
using WarEconomy.Server.Managers;
using WarEconomy.Server.Network;

static void Check(string name,bool value){Console.WriteLine($"CHECK {name}: {(value?"PASS":"FAIL")}");if(!value)throw new Exception(name);}
foreach(bool reverseFailure in new[]{false,true}){
 var old=new Faction{Name="old"};var next=new Faction{Name="new"};
 var map=new Map{Tile=42,Parent=new Thing{Faction=old}};
 Pawn pawn=reverseFailure?new ReverseFailPawn():new Pawn();
 pawn.Faction=old;pawn.Map=map;pawn.workSettings!.ThrowOnEnable=true;
 object area=pawn.playerSettings!.AreaRestrictionInPawnCurrentMap!;
 object master=pawn.playerSettings.Master!;
 map.mapPawns.AllPawnsSpawned.Add(pawn);map.listerThings.AllThings.Add(pawn);
 Current.Game=new Game();Current.Game.Maps.Add(map);
 Find.FactionManager=new FactionManager();Find.FactionManager.AllFactionsListForReading.Add(next);
 Messages.Values.Clear();
 bool success=AtomicFiefTransferExecutor.Execute(new PKT_FiefTransferExecute("rollback",42,"new"));
 if(!reverseFailure){
  Check("forward_failure_restores_faction",!success && ReferenceEquals(pawn.Faction,old));
  Check("REPRO_cleanup_state_not_restored",!pawn.ownership!.Claimed && pawn.playerSettings.AreaRestrictionInPawnCurrentMap==null && pawn.playerSettings.Master==null);
 }else{
  Check("REPRO_reverse_failure_leaves_new_faction",!success && ReferenceEquals(pawn.Faction,next));
  Check("REPRO_reverse_failure_reports_rollback_completed",Messages.Values.Any(s=>s.Contains("이전 상태로 롤백되었습니다")));
 }
}
var server=new TcpNetworkServer();server.Start(0);
try{
 int port=((IPEndPoint)((TcpListener)typeof(TcpNetworkServer).GetField("_listener",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(server)!).LocalEndpoint).Port;
 Console.WriteLine($"isolated_port={port}; 7777 untouched");
 FeudalManager.Instance.RegisterSettlement(new SettlementData("owned","Owned",101,"hf","host",NobilityTitle.Baron));
 using var visitor=new TcpClient();await visitor.ConnectAsync(IPAddress.Loopback,port);
 using var host=new TcpClient();await host.ConnectAsync(IPAddress.Loopback,port);
 await Handshake(visitor,"visitor");await Handshake(host,"host");
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("host-exit","visitor","vf","owned")));
 Check("request_routed_to_host",(await Read(host)).header==PacketHeader.VisitRequest);
 host.Close();
 var denied=await Read(visitor);
 Check("host_disconnect_rejects_waiting_visit",denied.header==PacketHeader.VisitResponse && !PacketSerializer.Deserialize<PKT_VisitResponse>(denied.body)!.IsAccepted);
 await WaitEmpty(server);
 Check("host_disconnect_clears_pending",Count(server)==0);
 using var host2=new TcpClient();await host2.ConnectAsync(IPAddress.Loopback,port);await Handshake(host2,"host");
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("visitor-exit","visitor","vf","owned")));await Read(host2);
 visitor.Close();
 Check("visitor_disconnect_notifies_host",(await Read(host2)).header==PacketHeader.VisitCancel);
 await WaitEmpty(server);
 Check("visitor_disconnect_clears_pending",Count(server)==0);
}finally{server.Stop();}
Console.WriteLine("REPRO PASS means defect reproduced. Rollback uses original production source with fault-injection adapters, not Unity runtime.");
static int Count(TcpNetworkServer server){var active=typeof(TcpNetworkServer).GetField("_activeVisitRequests",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(server)!;return(int)active.GetType().GetProperty("Count")!.GetValue(active)!;}
static async Task WaitEmpty(TcpNetworkServer server){using var t=new CancellationTokenSource(5000);while(Count(server)!=0)await Task.Delay(10,t.Token);}
static async Task Handshake(TcpClient c,string id){await Send(c,new PKT_PlayerHandshake(id,"1.6",id));await Read(c);}
static async Task Send<T>(TcpClient c,T packet)where T:IPacket{using var t=new CancellationTokenSource(5000);await c.GetStream().WriteAsync(PacketSerializer.Serialize(packet),t.Token);}
static async Task<(PacketHeader header,byte[] body)> Read(TcpClient c){using var t=new CancellationTokenSource(5000);var h=new byte[6];await c.GetStream().ReadExactlyAsync(h,t.Token);int n=BitConverter.ToInt32(h,2);if(n<0||n>1048576)throw new Exception("frame");var b=new byte[n];await c.GetStream().ReadExactlyAsync(b,t.Token);return((PacketHeader)BitConverter.ToUInt16(h),b);}
class ReverseFailPawn:Pawn{
 public override void SetFaction(Faction faction){if(faction.Name=="old")throw new Exception("injected failure before reverse faction mutation");base.SetFaction(faction);}
}
