using System;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using Verse;
using WarEconomy.Client.Fief;
using WarEconomy.Client.Networking;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.Auth;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Packets.Visit;
using WarEconomy.Common.Packets.World;
using WarEconomy.Server.Managers;
using WarEconomy.Server.Network;

static void Check(string name, bool value)
{
    Console.WriteLine($"CHECK {name}: {(value ? "PASS" : "FAIL")}");
    if (!value) throw new Exception($"Assertion failed: {name}");
}

Console.WriteLine("=== [Round 3 Re-Verification: All 5 Defects Fixed] ===");

// ----------------------------------------------------------------------------------------
// 1. R3-1: 영지 목록 동기화 멱등성 및 무한 루프 차단 검증
// ----------------------------------------------------------------------------------------
var fmIdemp = new FeudalManager();
var sampleFief = new SettlementData("fief-idemp", "IdempCity", 10, "fac-a", "lord-a", NobilityTitle.Baron);
fmIdemp.RegisterSettlement(sampleFief);

int syncEventCount = 0;
fmIdemp.OnSettlementListUpdated += _ => syncEventCount++;

// 동일한 데이터를 10회 연속 등록 시도
for (int i = 0; i < 10; i++)
{
    fmIdemp.RegisterSettlement(sampleFief);
}
Check("R3_1_unchanged_registration_emits_zero_sync_events", syncEventCount == 0);

// 속성 변경 시(예: 영지 이름 갱신)에는 1회 정상 발행
var modifiedFief = new SettlementData("fief-idemp", "IdempCity-Renamed", 10, "fac-a", "lord-a", NobilityTitle.Baron);
fmIdemp.RegisterSettlement(modifiedFief);
Check("R3_1_changed_registration_emits_single_sync_event", syncEventCount == 1);

// ----------------------------------------------------------------------------------------
// 2. R3-2: 원자적 영지 양도 롤백 추적 시점 보정 검증 (SetFaction/WorkSettings 예외 시 100% 롤백)
// ----------------------------------------------------------------------------------------
foreach (bool callbackFailure in new[] { false, true })
{
    var oldFac = new Faction { Name = "old-faction" };
    var newFac = new Faction { Name = "new-faction" };
    var map = new Map { Tile = 77, Parent = new Thing { Faction = oldFac } };
    var testPawn = new Pawn { Faction = oldFac, Map = map, ThrowAfterFactionMutation = callbackFailure };
    testPawn.workSettings!.ThrowOnEnable = !callbackFailure;

    map.mapPawns.AllPawnsSpawned.Add(testPawn);
    map.listerThings.AllThings.Add(testPawn);
    Current.Game = new Game();
    Current.Game.Maps.Add(map);
    Find.FactionManager = new FactionManager();
    Find.FactionManager.AllFactionsListForReading.Add(newFac);

    bool execSuccess = AtomicFiefTransferExecutor.Execute(new PKT_FiefTransferExecute("fief-rollback-test", 77, "new-faction"));
    Check($"R3_2_exec_fails_on_mutation_error_cb_{callbackFailure}", !execSuccess);
    Check($"R3_2_pawn_rolled_back_to_old_faction_cb_{callbackFailure}", ReferenceEquals(testPawn.Faction, oldFac));
    Check($"R3_2_map_parent_preserved_old_faction_cb_{callbackFailure}", ReferenceEquals(map.ParentFaction, oldFac));

    var sentResult = (PKT_FiefTransferResult)NetworkClient.Instance.Sent.Last();
    Check($"R3_2_result_packet_reports_tracked_pawns_cb_{callbackFailure}", !sentResult.Success && sentResult.TransferredPawnsCount == 1);
}

// ----------------------------------------------------------------------------------------
// 3. R3-3: TransferId 필수 검증 및 폴백 완전 제거 검증
// ----------------------------------------------------------------------------------------
var fmTransfer = new FeudalManager();
var fiefTransferData = new SettlementData("fief-tx", "TxCity", 88, "fac-old", "owner-a", NobilityTitle.Baron);
fmTransfer.RegisterSettlement(fiefTransferData);

// 정상 트랜잭션 등록 (TransferId: tx-valid)
fmTransfer.ExecuteFiefTransfer(new PKT_FiefTransferOffer("fief-tx", "owner-a", "new-b", NobilityTitle.Baron, "fac-new", "tx-valid"), 1, "session-a");
Check("R3_3_pending_preserves_owner_before_ack", fiefTransferData.LordPlayerId == "owner-a");

// (A) TransferId가 누락된 결과(null/empty) 회신 시 -> 폴백 없이 반드시 거부되어야 함!
var emptyTxResult = new PKT_FiefTransferResult("fief-tx", 88, true, 1, 0, null, "");
fmTransfer.ProcessFiefTransferResult(emptyTxResult, "session-a");
Check("R3_3_empty_transfer_id_rejected_no_fallback", fiefTransferData.LordPlayerId == "owner-a");

// (B) 일치하지 않는 임의의 TransferId 회신 시 -> 거부되어야 함!
var wrongTxResult = new PKT_FiefTransferResult("fief-tx", 88, true, 1, 0, null, "tx-wrong-id");
fmTransfer.ProcessFiefTransferResult(wrongTxResult, "session-a");
Check("R3_3_mismatched_transfer_id_rejected", fiefTransferData.LordPlayerId == "owner-a");

// (C) 정확히 일치하는 tx-valid 회신 시 -> 정상 확정
var correctTxResult = new PKT_FiefTransferResult("fief-tx", 88, true, 1, 0, null, "tx-valid");
fmTransfer.ProcessFiefTransferResult(correctTxResult, "session-a");
Check("R3_3_matching_transfer_id_commits_owner", fiefTransferData.LordPlayerId == "new-b");

// ----------------------------------------------------------------------------------------
// 4. R3-4 & R3-5: 소유권 탈취 차단 및 방문 취소 권한 검증 (네트워크 통합 테스트)
// ----------------------------------------------------------------------------------------
var server = new TcpNetworkServer();
server.Start(0);

try
{
    var listener = (TcpListener)typeof(TcpNetworkServer).GetField("_listener", BindingFlags.NonPublic | BindingFlags.Instance)!.GetValue(server)!;
    int port = ((IPEndPoint)listener.LocalEndpoint).Port;
    Console.WriteLine($"Test server running on port {port}");

    var fmGlobal = FeudalManager.Instance;
    fmGlobal.RegisterSettlement(new SettlementData("owned-fief", "Host Castle", 101, "fac-host", "host-player", NobilityTitle.Baron));

    using var visitor = new TcpClient();
    await visitor.ConnectAsync(IPAddress.Loopback, port);
    using var host = new TcpClient();
    await host.ConnectAsync(IPAddress.Loopback, port);
    using var observer = new TcpClient();
    await observer.ConnectAsync(IPAddress.Loopback, port);

    // 핸드셰이크
    await Send(visitor, new PKT_PlayerHandshake("visitor-player", "1.6", "visitor-player"));
    await Read(visitor);
    await Send(host, new PKT_PlayerHandshake("host-player", "1.6", "host-player"));
    await Read(host);
    await Send(observer, new PKT_PlayerHandshake("observer-player", "1.6", "observer-player"));
    await Read(observer);

    // [R3-4 검증]: observer가 host 소유의 owned-fief를 가로채려는 등록 패킷 전송 시도
    await Send(observer, new PKT_SettlementRegister(new SettlementData("owned-fief", "Hacked Castle", 101, "fac-observer", "observer-player", NobilityTitle.Baron)));

    // 배리어 동기화 패킷
    await Send(observer, new PKT_VisitRequest(new VisitRequestData("barrier-req", "observer-player", "fac-obs", "NPC-test")));
    await Read(observer);

    // 서버의 영주가 여전히 host-player로 보존되었는지 검증!
    var checkedFief = fmGlobal.GetSettlement("owned-fief")!;
    Check("R3_4_observer_cannot_steal_ownership_via_register", checkedFief.LordPlayerId == "host-player");

    // [R3-5 검증]: 방문 취소 권한 검증
    await Send(visitor, new PKT_VisitRequest(new VisitRequestData("visit-test-1", "visitor-player", "fac-vis", "owned-fief")));
    var hostReceivedReq = await Read(host);
    Check("R3_5_valid_request_arrived_at_host", hostReceivedReq.header == PacketHeader.VisitRequest);

    // 제3자(observer)가 해당 요청을 무단 취소 시도 -> 서버에서 거부되고 host에게 취소 패킷이 전달되지 않아야 함!
    await Send(observer, new PKT_VisitCancel("visit-test-1", "visitor-player", "owned-fief"));
    Check("R3_5_unauthorized_cancel_by_observer_dropped", await NoData(host));

    // 실제 방문자(visitor)가 취소 요청 -> 정상 승인 및 host에게 취소 패킷 전달
    await Send(visitor, new PKT_VisitCancel("visit-test-1", "visitor-player", "owned-fief"));
    var cancelReceived = await Read(host);
    Check("R3_5_authorized_cancel_forwarded_to_host", cancelReceived.header == PacketHeader.VisitCancel);

    // 메모리 누수 검증: 취소된 요청은 _activeVisitRequests에서 0건으로 완전 정리됨
    var activeRequestsMap = typeof(TcpNetworkServer).GetField("_activeVisitRequests", BindingFlags.NonPublic | BindingFlags.Instance)!.GetValue(server)!;
    int remainingCount = (int)activeRequestsMap.GetType().GetProperty("Count")!.GetValue(activeRequestsMap)!;
    Check("R3_5_active_visit_requests_cleaned_up_zero_leak", remainingCount == 0);
}
finally
{
    server.Stop();
}

Console.WriteLine("ALL 5 DEFECT RE-VERIFICATION TESTS PASSED 100%!");

static async Task Send<T>(TcpClient client, T packet) where T : IPacket
{
    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
    await client.GetStream().WriteAsync(PacketSerializer.Serialize(packet), cts.Token);
}

static async Task<(PacketHeader header, byte[] body)> Read(TcpClient client)
{
    using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(5));
    var header = new byte[6];
    await client.GetStream().ReadExactlyAsync(header, timeout.Token);
    int length = BitConverter.ToInt32(header, 2);
    if (length < 0 || length > 1048576) throw new Exception("Invalid frame");
    var body = new byte[length];
    await client.GetStream().ReadExactlyAsync(body, timeout.Token);
    return ((PacketHeader)BitConverter.ToUInt16(header), body);
}

static async Task<bool> NoData(TcpClient client)
{
    await Task.Delay(300);
    return client.Available == 0;
}
