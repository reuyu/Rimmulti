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

Console.WriteLine("=== [Round 5 Re-Verification: All R5 Defects Fixed] ===");

// ----------------------------------------------------------------------------------------
// 1. R5-1: 실제 API 형태의 소유권(OwnedBed) 복원 및 최종 상태 비교 검증 (Success / Reject / Throw)
// ----------------------------------------------------------------------------------------
foreach (string scenario in new[] { "success", "reject", "throw" })
{
    var oldFac = new Faction { Name = "old-faction" };
    var newFac = new Faction { Name = "new-faction" };
    var map = new Map { Tile = 42, Parent = new Thing { Faction = oldFac } };
    var pawn = new Pawn { Faction = oldFac, Map = map };
    
    var previousBed = pawn.ownership!.OwnedBed;
    pawn.ownership.RejectClaim = scenario == "reject";
    pawn.ownership.ThrowOnClaim = scenario == "throw";
    pawn.workSettings!.ThrowOnEnable = true;

    object area = pawn.playerSettings!.AreaRestrictionInPawnCurrentMap!;
    object master = pawn.playerSettings.Master!;

    map.mapPawns.AllPawnsSpawned.Add(pawn);
    map.listerThings.AllThings.Add(pawn);
    Current.Game = new Game();
    Current.Game.Maps.Add(map);
    Find.FactionManager = new FactionManager();
    Find.FactionManager.AllFactionsListForReading.Add(newFac);
    Messages.Values.Clear();
    NetworkClient.Instance.Sent.Clear();

    bool success = AtomicFiefTransferExecutor.Execute(new PKT_FiefTransferExecute("QA-r5-bed", 42, "new-faction"));
    var result = (PKT_FiefTransferResult)NetworkClient.Instance.Sent.Last();

    Check($"R5_forward_failure_and_faction_recovered_{scenario}", !success && ReferenceEquals(pawn.Faction, oldFac));

    if (scenario == "success")
    {
        // 침대 및 설정 정상 복구 확인
        Check("R5_owned_bed_successfully_restored", ReferenceEquals(previousBed, pawn.ownership.OwnedBed));
        Check("R5_area_restriction_restored", ReferenceEquals(pawn.playerSettings.AreaRestrictionInPawnCurrentMap, area));
        Check("R5_master_restored", ReferenceEquals(pawn.playerSettings.Master, master));
        Check("R5_ui_reports_clean_rollback_on_success", Messages.Values.Any(s => s.Contains("이전 상태로 롤백되었습니다")));
        Check("R5_packet_omits_incomplete_marker_on_success", !result.ErrorMessage.Contains("Incomplete rollback"));
    }
    else
    {
        // 복구 실패(거절 또는 예외) 시 침대 미복원 확인
        Check($"R5_bed_remains_unowned_{scenario}", pawn.ownership.OwnedBed == null);
        
        // 침대가 복원되지 않았으므로 "이전 상태로 롤백되었습니다" 문구는 절대 출력되지 않아야 함!
        Check($"R5_ui_does_NOT_report_clean_rollback_{scenario}", !Messages.Values.Any(s => s.Contains("이전 상태로 롤백되었습니다")));
        
        // 불완전 복구 경고 메시지가 출력되어야 함!
        Check($"R5_ui_reports_incomplete_rollback_warning_{scenario}", Messages.Values.Any(s => s.Contains("일부 객체의 복구가 완료되지 않았습니다")));
        
        // 서버 결과 패킷에 Incomplete rollback 플래그 및 원인 포함 확인
        Check($"R5_packet_flags_incomplete_resync_required_{scenario}", result.ErrorMessage.Contains("Incomplete rollback: resync required"));
    }
}

// ----------------------------------------------------------------------------------------
// 2. R5-2: 파괴된 객체(Destroyed Target) 복원 불가능 시 불완전 복구 처리 검증
// ----------------------------------------------------------------------------------------
{
    var oldFac = new Faction { Name = "old-faction" };
    var newFac = new Faction { Name = "new-faction" };
    var map = new Map { Tile = 43, Parent = new Thing { Faction = oldFac } };
    var pawn = new Pawn { Faction = oldFac, Map = map };

    // 침대 역할을 하는 파괴된 Thing 생성
    var destroyedBed = new Thing { Destroyed = true };
    // Ownership.OwnedBed에 대입
    typeof(Ownership).GetProperty("OwnedBed")!.SetValue(pawn.ownership, destroyedBed);
    pawn.workSettings!.ThrowOnEnable = true;

    map.mapPawns.AllPawnsSpawned.Add(pawn);
    map.listerThings.AllThings.Add(pawn);
    Current.Game = new Game();
    Current.Game.Maps.Add(map);
    Find.FactionManager = new FactionManager();
    Find.FactionManager.AllFactionsListForReading.Add(newFac);
    Messages.Values.Clear();
    NetworkClient.Instance.Sent.Clear();

    bool success = AtomicFiefTransferExecutor.Execute(new PKT_FiefTransferExecute("QA-r5-destroyed", 43, "new-faction"));
    var result = (PKT_FiefTransferResult)NetworkClient.Instance.Sent.Last();

    Check("R5_destroyed_bed_causes_incomplete_rollback", !success && ReferenceEquals(pawn.Faction, oldFac));
    Check("R5_destroyed_bed_packet_flags_incomplete", result.ErrorMessage.Contains("Incomplete rollback: resync required") && result.ErrorMessage.Contains("destroyed"));
    Check("R5_destroyed_bed_ui_reports_incomplete_warning", Messages.Values.Any(s => s.Contains("일부 객체의 복구가 완료되지 않았습니다")));
}

// ----------------------------------------------------------------------------------------
// 3. R3-1: 영지 목록 동기화 멱등성 및 무한 루프 차단 검증
// ----------------------------------------------------------------------------------------
var fmIdemp = new FeudalManager();
var sampleFief = new SettlementData("fief-idemp", "IdempCity", 10, "fac-a", "lord-a", NobilityTitle.Baron);
fmIdemp.RegisterSettlement(sampleFief);

int syncEventCount = 0;
fmIdemp.OnSettlementListUpdated += _ => syncEventCount++;

for (int i = 0; i < 10; i++)
{
    fmIdemp.RegisterSettlement(sampleFief);
}
Check("R3_1_unchanged_registration_emits_zero_sync_events", syncEventCount == 0);

var modifiedFief = new SettlementData("fief-idemp", "IdempCity-Renamed", 10, "fac-a", "lord-a", NobilityTitle.Baron);
fmIdemp.RegisterSettlement(modifiedFief);
Check("R3_1_changed_registration_emits_single_sync_event", syncEventCount == 1);

// ----------------------------------------------------------------------------------------
// 4. R3-3: TransferId 필수 검증 및 폴백 완전 제거 검증
// ----------------------------------------------------------------------------------------
var fmTransfer = new FeudalManager();
var fiefTransferData = new SettlementData("fief-tx", "TxCity", 88, "fac-old", "owner-a", NobilityTitle.Baron);
fmTransfer.RegisterSettlement(fiefTransferData);

fmTransfer.ExecuteFiefTransfer(new PKT_FiefTransferOffer("fief-tx", "owner-a", "new-b", NobilityTitle.Baron, "fac-new", "tx-valid"), 1, "session-a");
Check("R3_3_pending_preserves_owner_before_ack", fiefTransferData.LordPlayerId == "owner-a");

var emptyTxResult = new PKT_FiefTransferResult("fief-tx", 88, true, 1, 0, null, "");
fmTransfer.ProcessFiefTransferResult(emptyTxResult, "session-a");
Check("R3_3_empty_transfer_id_rejected_no_fallback", fiefTransferData.LordPlayerId == "owner-a");

var wrongTxResult = new PKT_FiefTransferResult("fief-tx", 88, true, 1, 0, null, "tx-wrong-id");
fmTransfer.ProcessFiefTransferResult(wrongTxResult, "session-a");
Check("R3_3_mismatched_transfer_id_rejected", fiefTransferData.LordPlayerId == "owner-a");

var correctTxResult = new PKT_FiefTransferResult("fief-tx", 88, true, 1, 0, null, "tx-valid");
fmTransfer.ProcessFiefTransferResult(correctTxResult, "session-a");
Check("R3_3_matching_transfer_id_commits_owner", fiefTransferData.LordPlayerId == "new-b");

// ----------------------------------------------------------------------------------------
// 5. R3-4 & R3-5: 소유권 탈취 차단, 방문 취소 권한 검증, 세션 종료 정리 검증
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

    await Send(visitor, new PKT_PlayerHandshake("visitor-player", "1.6", "visitor-player"));
    await Read(visitor);
    await Send(host, new PKT_PlayerHandshake("host-player", "1.6", "host-player"));
    await Read(host);
    await Send(observer, new PKT_PlayerHandshake("observer-player", "1.6", "observer-player"));
    await Read(observer);

    // 탈취 시도 차단 검증
    await Send(observer, new PKT_SettlementRegister(new SettlementData("owned-fief", "Hacked Castle", 101, "fac-observer", "observer-player", NobilityTitle.Baron)));
    await Send(observer, new PKT_VisitRequest(new VisitRequestData("barrier-req", "observer-player", "fac-obs", "NPC-test")));
    await Read(observer);

    var checkedFief = fmGlobal.GetSettlement("owned-fief")!;
    Check("R3_4_observer_cannot_steal_ownership_via_register", checkedFief.LordPlayerId == "host-player");

    // 방문 취소 권한 검증
    await Send(visitor, new PKT_VisitRequest(new VisitRequestData("visit-test-1", "visitor-player", "fac-vis", "owned-fief")));
    var hostReceivedReq = await Read(host);
    Check("R3_5_valid_request_arrived_at_host", hostReceivedReq.header == PacketHeader.VisitRequest);

    await Send(observer, new PKT_VisitCancel("visit-test-1", "visitor-player", "owned-fief"));
    Check("R3_5_unauthorized_cancel_by_observer_dropped", await NoData(host));

    await Send(visitor, new PKT_VisitCancel("visit-test-1", "visitor-player", "owned-fief"));
    var cancelReceived = await Read(host);
    Check("R3_5_authorized_cancel_forwarded_to_host", cancelReceived.header == PacketHeader.VisitCancel);

    var activeRequestsMap = typeof(TcpNetworkServer).GetField("_activeVisitRequests", BindingFlags.NonPublic | BindingFlags.Instance)!.GetValue(server)!;
    int remainingCount = (int)activeRequestsMap.GetType().GetProperty("Count")!.GetValue(activeRequestsMap)!;
    Check("R3_5_active_visit_requests_cleaned_up_zero_leak", remainingCount == 0);
}
finally
{
    server.Stop();
}

Console.WriteLine("ALL ROUND 5 VERIFICATION TESTS PASSED 100%!");

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
