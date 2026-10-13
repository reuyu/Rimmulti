using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Collections.Concurrent;
using System.Threading.Channels;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.Auth;
using WarEconomy.Common.Packets.Diplomacy;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Packets.Visit;
using WarEconomy.Common.Packets.World;
using WarEconomy.Server.Managers;
using WarEconomy.Server.Network;
using WarEconomy.Server.Time;

// Current source is compiled directly; this runner does not start the production entry point.
// REPRO_CONFIRMED means a defect is present, never a requirement acceptance PASS.
int confirmed = 0;
void Repro(string id, string requirement, bool present, string observed)
{
    Console.WriteLine($"{id} [{requirement}] {(present ? "REPRO_CONFIRMED" : "NOT_REPRODUCED")}: {observed}");
    if (!present) throw new Exception($"Baseline changed or reproduction failed: {id}");
    confirmed++;
}
T Private<T>(object target, string name) => (T)target.GetType().GetField(name, BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(target)!;
void Handle<T>(TcpNetworkServer server, ServerClientSession session, T packet) where T : IPacket
{
    var frame = PacketSerializer.Serialize(packet);
    typeof(TcpNetworkServer).GetMethod("HandlePacket", BindingFlags.Instance | BindingFlags.NonPublic)!
        .Invoke(server, new object[] { session, packet.Header, frame[6..] });
}
async Task<(ServerClientSession session, TcpClient client)> Pair()
{
    var listener = new TcpListener(IPAddress.Loopback, 0);
    listener.Start();
    var client = new TcpClient();
    try
    {
        await client.ConnectAsync(IPAddress.Loopback, ((IPEndPoint)listener.LocalEndpoint).Port);
        var accepted = await listener.AcceptTcpClientAsync();
        return (new ServerClientSession(accepted), client);
    }
    finally { listener.Stop(); }
}

var diplomacy = new DiplomacyManager();
diplomacy.SetFactionTier("attacker-empire", FactionTier.Empire);
diplomacy.SetFactionTier("defender-tribe", FactionTier.Tribe);
var war = diplomacy.DeclareWar("attacker-empire", "defender-tribe", 100);
Repro("BASE-01", "FR-110", war.State == WarState.Active && war.CountdownEndWorldTick == 100,
    $"attacker=Empire defender=Tribe state={war.State} prepTicks={war.CountdownEndWorldTick - 100}; uses defender tier");

var taxes = new FeudalManager();
taxes.DispatchTaxCaravan(new PKT_TaxCaravanDispatch("unarrived-caravan", "superior", "tax-target", new() { ["Steel"] = 500 }), 0);
taxes.OnWorldTick(180000);
var tax = Private<ConcurrentDictionary<string, TaxDelinquencyState>>(taxes, "_taxStates")["tax-target"];
Repro("BASE-02", "BR-018;FR-192", tax.Status == TaxStatus.Delinquent,
    $"no arrival/no collection, tick=180000 status={tax.Status} count={tax.ConsecutiveDelinquentCount}");

var transfers = new FeudalManager();
var first = new SettlementData("first", "First", 1, "old", "owner", NobilityTitle.Baron);
var second = new SettlementData("second", "Second", 2, "old", "owner", NobilityTitle.Baron);
transfers.RegisterSettlement(first); transfers.RegisterSettlement(second);
transfers.ExecuteFiefTransfer(new PKT_FiefTransferOffer("first", "owner", "new-first", NobilityTitle.Baron, "new", "same-id"), 1, "session");
transfers.ExecuteFiefTransfer(new PKT_FiefTransferOffer("second", "owner", "new-second", NobilityTitle.Baron, "new", "same-id"), 2, "session");
transfers.ProcessFiefTransferResult(new PKT_FiefTransferResult("first", 1, true, 1, 1, "", "same-id"), "session");
transfers.ProcessFiefTransferResult(new PKT_FiefTransferResult("second", 2, true, 1, 1, "", "same-id"), "session");
var active = Private<ConcurrentDictionary<string, string>>(transfers, "_activeTransferBySettlement");
Repro("BASE-03", "NFR-005;ER-002", first.LordPlayerId == "owner" && second.LordPlayerId == "new-second" && active.ContainsKey("first"),
    $"first={first.LordPlayerId} second={second.LordPlayerId} danglingFirst={active.ContainsKey("first")}");

var server = new TcpNetworkServer();
var pair = await Pair();
var hostPair = await Pair();
try
{
    var globalDiplomacy = DiplomacyManager.Instance;
    var wars = Private<ConcurrentDictionary<string, WarDeclarationData>>(globalDiplomacy, "_activeWars");
    int before = wars.Count;
    Handle(server, pair.session, new PKT_WarDeclarationRequest("victim-faction-impersonated", "target"));
    Repro("BASE-04", "FR-108;BR-011;NFR-007", string.IsNullOrEmpty(pair.session.PlayerId) && wars.Count == before + 1,
        $"unauthenticated PlayerId='{pair.session.PlayerId}' createdWars={wars.Count - before}");

    var globalFeudal = FeudalManager.Instance;
    globalFeudal.RegisterSettlement(new SettlementData("spoof-owned", "Original", 10, "owned-faction", "victim-player", NobilityTitle.Baron));
    Handle(server, pair.session, new PKT_PlayerHandshake("intruder", "INCOMPATIBLE-VERSION", "victim-player"));
    Handle(server, pair.session, new PKT_SettlementRegister(new SettlementData("spoof-owned", "HijackedMetadata", 999, "fake", "ignored", NobilityTitle.Baron)));
    var spoofed = globalFeudal.GetSettlement("spoof-owned")!;
    Repro("BASE-05", "FR-004~007;NFR-007", pair.session.PlayerId == "victim-player" && spoofed.Name == "HijackedMetadata" && spoofed.TileId == 999,
        $"claimedPlayer={pair.session.PlayerId} incompatible version accepted; settlementName={spoofed.Name} tile={spoofed.TileId}");

    hostPair.session.PlayerId = "unrelated-online-host";
    Private<ConcurrentDictionary<string, ServerClientSession>>(server, "_sessions")[hostPair.session.SessionId] = hostPair.session;
    globalFeudal.RegisterSettlement(new SettlementData("offline-owned", "Offline", 20, "offline-faction", "actual-offline-owner", NobilityTitle.Baron));
    Handle(server, pair.session, new PKT_VisitRequest(new VisitRequestData("forged-host-request", "ignored", "visitor-faction", "offline-owned", "unrelated-online-host")));
    var hostQueue = Private<Channel<byte[]>>(hostPair.session, "_reliableChannel");
    bool routed = hostQueue.Reader.TryRead(out var hostFrame) && BitConverter.ToUInt16(hostFrame!, 0) == (ushort)PacketHeader.VisitRequest;
    Repro("BASE-06", "FR-091;FR-095", routed,
        $"actual owner offline; caller-specified unrelated HostPlayerId received request={routed}");
}
finally
{
    pair.session.Disconnect(); pair.client.Dispose();
    hostPair.session.Disconnect(); hostPair.client.Dispose();
}

var staleReceiver = new PacketReceiver();
var oldFrame = PacketSerializer.Serialize(new PKT_PlayerHandshake("old-session", "1.6", "old"));
staleReceiver.ReceiveBytes(oldFrame, 7);
var newFrame = PacketSerializer.Serialize(new PKT_WorldTickSync(180, 5500, 0, 0));
var staleResult = staleReceiver.ReceiveBytes(newFrame, newFrame.Length);
var freshResult = new PacketReceiver().ReceiveBytes(newFrame, newFrame.Length);
bool corrupted = staleResult.Count != 1 || staleResult[0].header != PacketHeader.WorldTickSync || !staleResult[0].body.SequenceEqual(freshResult[0].body);
Repro("BASE-07", "NFR-004;NFR-007", corrupted,
    $"receiver reused after partial old frame: staleFrames={staleResult.Count} freshFrames={freshResult.Count} staleHeader={(staleResult.Count > 0 ? staleResult[0].header : PacketHeader.None)}");

var clock = new WorldTickManager();
clock.Start(); await Task.Delay(200); clock.Stop();
if (clock.CurrentWorldTick <= 0) throw new Exception("zero-client world clock did not advance");
Console.WriteLine($"SANITY FR-001: zero-client WorldTickManager advanced to {clock.CurrentWorldTick}; not a persistence or sustained TPS certification.");
Console.WriteLine($"SUMMARY confirmedCounterexamples={confirmed}/7; these are requirement failures, not product PASS. No Unity runtime execution. No production server process restarted.");

namespace WarEconomy.Server
{
    // Production entry-point clock dependency only; authority logic is original source.
    internal static class Program { public static long CurrentTick => 100; }
}
