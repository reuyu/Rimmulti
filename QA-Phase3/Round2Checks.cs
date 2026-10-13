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
using WarEconomy.Client.UI;

static void Check(string name,bool value) {Console.WriteLine($"CHECK {name}: {(value?"PASS":"FAIL")}"); if(!value)throw new Exception(name);}
var manager=new FeudalManager();
var data=new SettlementData("QA-fief","QA",42,"old-faction","old-lord",NobilityTitle.Baron);
manager.RegisterSettlement(data);
PKT_FiefTransferOffer Offer(string lord)=>new("QA-fief","old-lord",lord,NobilityTitle.Baron,lord+"-faction");
PKT_FiefTransferResult Result(bool success)=>new("QA-fief",42,success,3,4);
manager.ExecuteFiefTransfer(Offer("A"),1);
Check("pending_preserves_owner",data.LordPlayerId=="old-lord");
manager.ProcessFiefTransferResult(Result(false));
Check("failure_preserves_owner",data.LordPlayerId=="old-lord");
manager.ExecuteFiefTransfer(Offer("A"),2);
manager.ProcessFiefTransferResult(Result(true));
Check("success_commits_owner",data.LordPlayerId=="A");
manager.ExecuteFiefTransfer(Offer("B"),3);
manager.ExecuteFiefTransfer(Offer("C"),4);
// Success generated for transfer B cannot carry a transaction ID; it commits C instead.
manager.ProcessFiefTransferResult(Result(true));
Check("REPRO_old_ack_commits_overwritten_transfer",data.LordPlayerId=="C");
manager.ExecuteFiefTransfer(Offer("D"),5);
// Program broadcasts execute to all clients. First client without the map reports failure.
manager.ProcessFiefTransferResult(new PKT_FiefTransferResult("QA-fief",42,false,0,0,"Target map not loaded locally"));
manager.ProcessFiefTransferResult(Result(true));
Check("REPRO_unrelated_failure_consumes_pending_before_owner_success",data.LordPlayerId=="C");

var request=new VisitRequestData("QA-cancel","visitor","vf","npc");
var dialog=new Dialog_VisitWait(request);
typeof(Dialog_VisitWait).GetMethod("CancelRequest",BindingFlags.NonPublic|BindingFlags.Instance)!.Invoke(dialog,null);
Check("cancel_clears_reference",typeof(Dialog_VisitWait).GetField("_currentInstance",BindingFlags.NonPublic|BindingFlags.Static)!.GetValue(null)==null);
Dialog_VisitWait.HandleResponse(new PKT_VisitResponse(request.RequestId,"npc","visitor",true));
Check("cancel_ignores_late_UI_response",dialog.CloseCalls==1 && request.Status==VisitStatus.Cancelled && !Verse.Messages.Values.Any(s=>s.Contains("방문을 승인")));

foreach(bool success in new[]{true,false}) {
 var original=new PKT_FiefTransferResult("QA영지",42,success,3,17,"테스트");
 var bytes=PacketSerializer.Serialize(original);
 var copy=PacketSerializer.Deserialize<PKT_FiefTransferResult>(bytes[6..])!;
 Check($"result_roundtrip_{success}",copy.Success==success && copy.TileId==42 && copy.TransferredPawnsCount==3 && copy.TransferredThingsCount==17 && copy.ErrorMessage=="테스트");
}
var server=new TcpNetworkServer(); server.Start(0);
try {
 var listener=(TcpListener)typeof(TcpNetworkServer).GetField("_listener",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(server)!;
 int port=((IPEndPoint)listener.LocalEndpoint).Port;
 Console.WriteLine($"QA isolated port={port}; 7777 untouched");
 var fm=FeudalManager.Instance;
 fm.RegisterSettlement(new SettlementData("online","Online",1,"hf","host",NobilityTitle.Baron){LayerId=2});
 fm.RegisterSettlement(new SettlementData("offline","Offline",2,"of","offline-host",NobilityTitle.Baron));
 using var visitor=new TcpClient(); await visitor.ConnectAsync(IPAddress.Loopback,port);
 using var host=new TcpClient(); await host.ConnectAsync(IPAddress.Loopback,port);
 using var observer=new TcpClient(); await observer.ConnectAsync(IPAddress.Loopback,port);
 foreach(var pair in new[]{(visitor,"visitor"),(host,"host"),(observer,"observer")}) {
  await Send(pair.Item1,new PKT_PlayerHandshake(pair.Item2,"1.6",pair.Item2));
  var sync=await Read(pair.Item1);
  Check("handshake_list_sync_"+pair.Item2,sync.header==PacketHeader.SettlementListSync && PacketSerializer.Deserialize<PKT_SettlementListSync>(sync.body)!.Settlements.Any(s=>s.SettlementId=="online" && s.LayerId==2));
 }
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("npc","visitor","vf","npc")));
 Check("NPC_auto_accept_with_other_clients",(await Read(visitor)).header==PacketHeader.VisitResponse);
 Check("no_NPC_forward_to_observer",await NoData(observer));
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("cancel","visitor","vf","online")));
 Check("route_to_owner",(await Read(host)).header==PacketHeader.VisitRequest);
 Check("no_forward_to_observer",await NoData(observer));
 await Send(visitor,new PKT_VisitCancel("cancel","visitor","online"));
 Check("cancel_to_owner",(await Read(host)).header==PacketHeader.VisitCancel);
 await Send(host,new PKT_VisitResponse("cancel","online","visitor",true));
 Check("server_drops_late_cancelled_response",await NoData(visitor));
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("offline","visitor","vf","offline")));
 var offline=await Read(visitor);
 Check("REPRO_offline_player_auto_approved_as_NPC",PacketSerializer.Deserialize<PKT_VisitResponse>(offline.body)!.IsAccepted);
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("spoof","visitor","vf","online")));
 await Read(host);
 await Send(observer,new PKT_VisitResponse("spoof","online","visitor",true));
 var spoof=await Read(visitor);
 Check("REPRO_unrelated_session_response_accepted",PacketSerializer.Deserialize<PKT_VisitResponse>(spoof.body)!.IsAccepted);
 await Send(host,new PKT_VisitResponse("spoof","online","visitor",false,"second response"));
 var duplicate=await Read(visitor);
 Check("REPRO_completed_request_responded_twice",!PacketSerializer.Deserialize<PKT_VisitResponse>(duplicate.body)!.IsAccepted);
 var active=typeof(TcpNetworkServer).GetField("_activeVisitRequests",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(server)!;
 int retained=(int)active.GetType().GetProperty("Count")!.GetValue(active)!;
 Check("REPRO_terminal_requests_retained",retained==4);
 Console.WriteLine($"OBSERVED retained_terminal_requests={retained}");
} finally {server.Stop();}
Console.WriteLine("Completed. REPRO PASS means defect reproduced, not release accepted.");
static async Task Send<T>(TcpClient client,T packet) where T:IPacket {
 using var timeout=new CancellationTokenSource(TimeSpan.FromSeconds(5));
 await client.GetStream().WriteAsync(PacketSerializer.Serialize(packet),timeout.Token);
}
static async Task<(PacketHeader header,byte[] body)> Read(TcpClient client) {
 using var timeout=new CancellationTokenSource(TimeSpan.FromSeconds(5));
 var header=new byte[6]; await client.GetStream().ReadExactlyAsync(header,timeout.Token);
 int length=BitConverter.ToInt32(header,2); if(length<0 || length>1048576)throw new Exception("Invalid frame");
 var body=new byte[length]; await client.GetStream().ReadExactlyAsync(body,timeout.Token);
 return ((PacketHeader)BitConverter.ToUInt16(header),body);
}
static async Task<bool> NoData(TcpClient client) {
 await Task.Delay(300); return client.Available==0;
}
