using System.Net;
using System.Net.Sockets;
using System.Reflection;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Packets.Visit;
using WarEconomy.Server.Managers;
using WarEconomy.Server.Network;
using WarEconomy.Client.UI;

static void Check(string name,bool value) {Console.WriteLine($"CHECK {name}: {(value?"PASS":"FAIL")}"); if(!value)throw new Exception(name);}
foreach(bool success in new[]{true,false}) {
 var source=new PKT_FiefTransferResult("QA영지",42,success,3,17,"실패 원인 / unicode");
 var bytes=PacketSerializer.Serialize(source);
 var copy=PacketSerializer.Deserialize<PKT_FiefTransferResult>(bytes[6..])!;
 Check($"result_roundtrip_{success}",BitConverter.ToUInt16(bytes)==(ushort)PacketHeader.FiefTransferResult && BitConverter.ToInt32(bytes,2)==bytes.Length-6 && copy.SettlementId==source.SettlementId && copy.TileId==42 && copy.Success==success && copy.TransferredPawnsCount==3 && copy.TransferredThingsCount==17 && copy.ErrorMessage==source.ErrorMessage);
}
var manager=new FeudalManager();
var settlement=new SettlementData("QA-fief","QA",42,"old-faction","old-lord",NobilityTitle.Baron);
manager.RegisterSettlement(settlement);
manager.ExecuteFiefTransfer(new PKT_FiefTransferOffer("QA-fief","old-lord","new-lord",NobilityTitle.Baron,"new-faction"),1);
manager.ProcessFiefTransferResult(new PKT_FiefTransferResult("QA-fief",42,false,0,0,"injected client failure"));
Check("REPRO_failed_transfer_keeps_new_owner",settlement.LordPlayerId=="new-lord" && settlement.FactionId=="new-faction");
Console.WriteLine($"OBSERVED owner_after_failure={settlement.LordPlayerId}");

var request=new VisitRequestData("QA-cancel","QA-visitor","QA-faction","QA-NPC");
var dialog=new Dialog_VisitWait(request);
typeof(Dialog_VisitWait).GetMethod("CancelRequest",BindingFlags.NonPublic|BindingFlags.Instance)!.Invoke(dialog,null);
Check("REPRO_cancel_retains_dialog_reference",ReferenceEquals(typeof(Dialog_VisitWait).GetField("_currentInstance",BindingFlags.NonPublic|BindingFlags.Static)!.GetValue(null),dialog));
Dialog_VisitWait.HandleResponse(new PKT_VisitResponse(request.RequestId,"QA-NPC","QA-visitor",true));
Check("REPRO_late_accept_after_cancel",dialog.CloseCalls==2 && Verse.Messages.Values.Any(s=>s.Contains("방문을 승인")) && request.Status==VisitStatus.Pending);
Console.WriteLine($"OBSERVED close_calls={dialog.CloseCalls}, request_status={request.Status}");

var server=new TcpNetworkServer();
server.Start(0);
try {
 var listener=(TcpListener)typeof(TcpNetworkServer).GetField("_listener",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(server)!;
 int port=((IPEndPoint)listener.LocalEndpoint).Port;
 Console.WriteLine($"QA isolated server actual port={port}; existing 7777 server untouched");
 using var visitor=new TcpClient(); await visitor.ConnectAsync(IPAddress.Loopback,port);
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("QA-solo","QA-visitor","QA-faction","QA-NPC")));
 var solo=await Read(visitor);
 Check("single_client_NPC_auto_accept",solo.header==PacketHeader.VisitResponse && PacketSerializer.Deserialize<PKT_VisitResponse>(solo.body)!.IsAccepted);
 using var observer=new TcpClient(); await observer.ConnectAsync(IPAddress.Loopback,port);
 var sessions=typeof(TcpNetworkServer).GetField("_sessions",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(server)!;
 using var timeout=new CancellationTokenSource(TimeSpan.FromSeconds(5));
 while((int)sessions.GetType().GetProperty("Count")!.GetValue(sessions)!<2) await Task.Delay(10,timeout.Token);
 await Send(visitor,new PKT_VisitRequest(new VisitRequestData("QA-multi","QA-visitor","QA-faction","QA-NPC")));
 var forwarded=await Read(observer);
 Check("REPRO_NPC_request_forwarded_to_unrelated_client",forwarded.header==PacketHeader.VisitRequest);
 await Send(visitor,new PKT_VisitCancel("QA-multi","QA-visitor","QA-NPC"));
 Check("cancel_forwarded",(await Read(observer)).header==PacketHeader.VisitCancel);
 await Send(observer,new PKT_VisitResponse("QA-multi","QA-NPC","QA-visitor",true));
 var late=await Read(visitor);
 Check("REPRO_server_forwards_accept_after_cancel",late.header==PacketHeader.VisitResponse && PacketSerializer.Deserialize<PKT_VisitResponse>(late.body)!.IsAccepted);
} finally {server.Stop();}
Console.WriteLine("Completed. REPRO checks confirm defects; they are not acceptance passes.");

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
