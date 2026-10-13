using System.Diagnostics;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Threading.Channels;
using WarEconomy.Common.Models;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.World;
using WarEconomy.Server.Network;
using WarEconomy.Client.Time;
class Program {
 static object QueueCount(Channel<byte[]> channel) { var items=channel.GetType().GetField("_items",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(channel)!; return items.GetType().GetProperty("Count",BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(items)!; }
 static async Task Main() {
  async Task<(ServerClientSession,TcpClient,Channel<byte[]>,Channel<byte[]>)> Pair() {
   var l=new TcpListener(IPAddress.Loopback,0);l.Start();var c=new TcpClient();
   await c.ConnectAsync(IPAddress.Loopback,((IPEndPoint)l.LocalEndpoint).Port);var a=await l.AcceptTcpClientAsync();l.Stop();
   var session=new ServerClientSession(a);
   Channel<byte[]> Q(string name)=>(Channel<byte[]>)typeof(ServerClientSession).GetField(name,BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(session)!;
   return(session,c,Q("_reliableChannel"),Q("_tickChannel"));
  }
  foreach(int total in new[]{2100}) {
   var (session,client,reliable,ticks)=await Pair();
   Parallel.Invoke(
    ()=>{for(int i=0;i<100000;i++)session.SendPacket(new PKT_WorldTickSync{ServerWorldTick=i});},
    ()=>{for(int i=0;i<total;i++)session.SendPacket(new ProbePacket{Id=i,Header=(PacketHeader)new[]{45,60,21}[i%3]});});
   int relQueued=(int)QueueCount(reliable),tickQueued=ticks.Reader.Count;
   Console.WriteLine($"FLOOD inputReliable={total} inputTicks=100000 queuedReliable={relQueued} queuedTicks={tickQueued} connected={session.IsConnected}");
   session.Start();using var deadline=new CancellationTokenSource(TimeSpan.FromSeconds(10));var stream=client.GetStream();var ids=new HashSet<int>();int[] perHeader=new int[3];
   for(int i=0;i<relQueued+tickQueued;i++) {
    byte[] h=new byte[6];await stream.ReadExactlyAsync(h,deadline.Token);int n=BitConverter.ToInt32(h,2);byte[] body=new byte[n];await stream.ReadExactlyAsync(body,deadline.Token);
    if(BitConverter.ToUInt16(h,0)!=10){var packet=PacketSerializer.Deserialize<ProbePacket>(body)!;ids.Add(packet.Id);perHeader[packet.Id%3]++;}
   }
   Console.WriteLine($"WIRE reliableReceived={ids.Count}/{total} fief={perHeader[0]} trade={perHeader[1]} diplomacy={perHeader[2]} connected={session.IsConnected}");
   int pending=(int)typeof(ServerClientSession).GetField("_pendingReliableCount",BindingFlags.NonPublic|BindingFlags.Instance)!.GetValue(session)!;
   Console.WriteLine($"DRAIN pendingReliable={pending} remainingReliable={QueueCount(reliable)}");
   if(ids.Count!=total || ids.Any(id=>id<0 || id>=total) || perHeader.Any(n=>n!=700) || pending!=0 || !session.IsConnected) throw new Exception("Stress assertions failed");
   session.Disconnect();client.Dispose();
  }

 }
}
public class ProbePacket:IPacket {public PacketHeader Header{get;set;} public int Id{get;set;}}
public class LargePacket:IPacket{public PacketHeader Header=>PacketHeader.WorldTickSync;public string Payload{get;set;}="";}
namespace Verse { public static class Find {public static RimWorld.Planet.World World=new();} public static class Log {public static void Error(string text)=>Console.WriteLine(text);} }
namespace RimWorld.Planet {public class World {public Holder worldObjects=new();} public class Holder {public int Count;public void WorldObjectsHolderTick(){Count++;}}}
namespace WarEconomy.Client.Networking {public class NetworkClient {public static NetworkClient Instance=new();public bool IsConnected=>true;}}
namespace WarEconomy.Client.Patches {public static class Patch_WorldObjectsHolder_WorldObjectsHolderTick {public static bool AllowWorldTickExecution;}}


