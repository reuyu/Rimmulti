using System;
using System.Collections.Concurrent;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;
using WarEconomy.Common.Models;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.Auth;
using WarEconomy.Common.Packets.Diplomacy;
using WarEconomy.Common.Packets.Economy;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Packets.Visit;
using WarEconomy.Common.Packets.World;
using WarEconomy.Server.Managers;


namespace WarEconomy.Server.Network
{
    /// <summary>
    /// 전용 데디케이트 서버 비동기 TCP 네트워크 엔진.
    /// 클라이언트 수락, 세션 풀링, 라우팅 및 브로드캐스트 총괄.
    /// </summary>
    public class TcpNetworkServer
    {
        private static TcpNetworkServer? _instance;
        public static TcpNetworkServer Instance => _instance ??= new TcpNetworkServer();

        private TcpListener? _listener;
        private readonly ConcurrentDictionary<string, ServerClientSession> _sessions = new ConcurrentDictionary<string, ServerClientSession>();
        private readonly ConcurrentDictionary<string, VisitRequestData> _activeVisitRequests = new ConcurrentDictionary<string, VisitRequestData>();
        private CancellationTokenSource? _cts;

        public int Port { get; private set; } = 7777;
        public bool IsRunning { get; private set; }

        public void Start(int port = 7777)
        {
            Port = port;
            _cts = new CancellationTokenSource();
            _listener = new TcpListener(IPAddress.Any, Port);
            _listener.Start();
            IsRunning = true;

            Console.WriteLine($"[TcpNetworkServer] Listening for RimWorld clients on port {Port}...");
            _ = Task.Run(() => AcceptLoop(_cts.Token));
        }

        public void Stop()
        {
            IsRunning = false;
            _cts?.Cancel();
            _listener?.Stop();

            foreach (var session in _sessions.Values)
            {
                session.Disconnect();
            }
            _sessions.Clear();
            Console.WriteLine("[TcpNetworkServer] Stopped.");
        }

        public void BroadcastPacket<T>(T packet, ServerClientSession? exclude = null) where T : IPacket
        {
            foreach (var session in _sessions.Values)
            {
                if (session == exclude) continue;
                session.SendPacket(packet);
            }
        }

        public bool SendToPlayer<T>(string playerId, T packet) where T : IPacket
        {
            var targetSession = _sessions.Values.FirstOrDefault(s => s.PlayerId == playerId);
            if (targetSession != null)
            {
                targetSession.SendPacket(packet);
                return true;
            }
            return false;
        }

        private async Task AcceptLoop(CancellationToken token)
        {
            while (!token.IsCancellationRequested && IsRunning && _listener != null)
            {
                try
                {
                    TcpClient client = await _listener.AcceptTcpClientAsync(token);
                    var session = new ServerClientSession(client);
                    _sessions[session.SessionId] = session;

                    session.OnPacketReceived += HandlePacket;
                    session.OnDisconnected += s =>
                    {
                        _sessions.TryRemove(s.SessionId, out _);
                        CleanupVisitRequestsForSession(s.PlayerId);
                    };

                    Console.WriteLine($"[TcpNetworkServer] Client connected: {session.SessionId}. Total clients: {_sessions.Count}");
                    session.Start();
                }
                catch (Exception ex)
                {
                    if (!token.IsCancellationRequested)
                    {
                        Console.WriteLine($"[TcpNetworkServer] Accept error: {ex.Message}");
                    }
                    break;
                }
            }
        }

        private void HandlePacket(ServerClientSession sender, PacketHeader header, byte[] body)
        {
            try
            {
                switch (header)
                {
                    case PacketHeader.Handshake:
                        var handshake = PacketSerializer.Deserialize<PKT_PlayerHandshake>(body);
                        if (handshake != null)
                        {
                            sender.PlayerId = !string.IsNullOrEmpty(handshake.PlayerId) ? handshake.PlayerId : handshake.PlayerNickname;
                            Console.WriteLine($"[Auth] Player {handshake.PlayerNickname} registered.");

                            // 신규 접속 플레이어에게 전체 정착지(영지) 국경 목록 즉시 동기화 (빈 목록이어도 전송하여 캐시 리셋 보장)
                            var settlements = FeudalManager.Instance.GetAllSettlements();
                            sender.SendPacket(new PKT_SettlementListSync(settlements));
                        }
                        break;

                    case PacketHeader.SettlementRegister:
                        var regPkt = PacketSerializer.Deserialize<PKT_SettlementRegister>(body);
                        if (regPkt != null && regPkt.Settlement != null && !string.IsNullOrEmpty(regPkt.Settlement.SettlementId))
                        {
                            var existing = FeudalManager.Instance.GetSettlement(regPkt.Settlement.SettlementId);
                            if (existing != null)
                            {
                                // 기존 영지가 존재하는 경우: 발신자 세션이 기존 영주와 일치하지 않으면 등록/수정 거부 (소유권 탈취 차단)
                                if (!string.IsNullOrEmpty(existing.LordPlayerId) && existing.LordPlayerId != sender.PlayerId)
                                {
                                    Console.WriteLine($"[Feudal] Unauthorized settlement overwrite attempt for '{regPkt.Settlement.SettlementId}' by '{sender.PlayerId}' (current lord: '{existing.LordPlayerId}'). Rejected.");
                                    break;
                                }

                                // 기존 소유자의 재등록이더라도 소유권은 FiefTransfer 절차로만 변경 가능하므로 기존 소유자/세력 유지
                                regPkt.Settlement.LordPlayerId = existing.LordPlayerId;
                                regPkt.Settlement.FactionId = existing.FactionId;
                            }
                            else
                            {
                                // 신규 영지 등록인 경우: 발신 세션의 PlayerId를 소유자로 강제 바인딩 (타인 사칭 차단)
                                regPkt.Settlement.LordPlayerId = sender.PlayerId;
                            }

                            FeudalManager.Instance.RegisterSettlement(regPkt.Settlement);
                            Console.WriteLine($"[Feudal] Registered settlement '{regPkt.Settlement.SettlementId}' on tile {regPkt.Settlement.TileId} from session '{sender.PlayerId}'.");
                        }
                        break;

                    case PacketHeader.VisitRequest:
                        var visitReq = PacketSerializer.Deserialize<PKT_VisitRequest>(body);
                        if (visitReq != null)
                        {
                            // 발신자의 PlayerId를 요청 데이터의 방문자로 고정 (위조/사칭 차단)
                            visitReq.RequestData.VisitorPlayerId = sender.PlayerId;

                            // 1. 대상 정착지 소유자 판별 (호스트 ID가 없으면 FeudalManager 등록 영지 조회)
                            string hostPlayerId = visitReq.RequestData.HostPlayerId;
                            if (string.IsNullOrEmpty(hostPlayerId))
                            {
                                var settlement = FeudalManager.Instance.GetSettlement(visitReq.RequestData.TargetSettlementId);
                                if (settlement != null && !string.IsNullOrEmpty(settlement.LordPlayerId))
                                {
                                    hostPlayerId = settlement.LordPlayerId;
                                    visitReq.RequestData.HostPlayerId = hostPlayerId;
                                }
                            }

                            // 2. 실제 해당 호스트 플레이어 온라인 세션 탐색
                            ServerClientSession? hostSession = null;
                            if (!string.IsNullOrEmpty(hostPlayerId))
                            {
                                hostSession = _sessions.Values.FirstOrDefault(s => s.PlayerId == hostPlayerId);
                            }

                            if (hostSession != null && hostSession != sender)
                            {
                                // 요청 상태 등록 (Pending) 후 실제 온라인 플레이어 영주 세션으로만 정확히 단독 포워딩
                                _activeVisitRequests[visitReq.RequestData.RequestId] = visitReq.RequestData;
                                Console.WriteLine($"[Visit] Request {visitReq.RequestData.RequestId} forwarded to host player '{hostPlayerId}'.");
                                hostSession.SendPacket(visitReq);
                            }
                            else if (!string.IsNullOrEmpty(hostPlayerId))
                            {
                                // 등록된 플레이어 영주가 오프라인인 경우: NPC로 오인 자동 승인하지 않고 거절 회신
                                Console.WriteLine($"[Visit] Target settlement '{visitReq.RequestData.TargetSettlementId}' owner '{hostPlayerId}' is offline. Rejecting request {visitReq.RequestData.RequestId}.");
                                sender.SendPacket(new PKT_VisitResponse(
                                    visitReq.RequestData.RequestId,
                                    visitReq.RequestData.TargetSettlementId,
                                    visitReq.RequestData.VisitorPlayerId,
                                    false,
                                    "영주가 현재 부재 중(오프라인)이어서 입국이 불가능합니다."
                                ));
                            }
                            else
                            {
                                // 진정한 NPC 정착지인 경우: 요청자에게 NPC 자동 승인 회신
                                Console.WriteLine($"[Visit] Target settlement '{visitReq.RequestData.TargetSettlementId}' is NPC settlement. Auto-approving request {visitReq.RequestData.RequestId}.");
                                sender.SendPacket(new PKT_VisitResponse(
                                    visitReq.RequestData.RequestId,
                                    visitReq.RequestData.TargetSettlementId,
                                    visitReq.RequestData.VisitorPlayerId,
                                    true,
                                    "NPC 영주가 기지 방문을 승인했습니다."
                                ));
                            }
                        }
                        break;

                    case PacketHeader.VisitCancel:
                        var visitCancel = PacketSerializer.Deserialize<PKT_VisitCancel>(body);
                        if (visitCancel != null)
                        {
                            if (_activeVisitRequests.TryGetValue(visitCancel.RequestId, out var req))
                            {
                                // [권한 검증]: 실제 요청을 생성한 방문자(Visitor) 세션만 취소 가능!
                                if (req.VisitorPlayerId != sender.PlayerId)
                                {
                                    Console.WriteLine($"[Visit] Unauthorized cancel attempt for request {visitCancel.RequestId} by session '{sender.PlayerId}' (actual requester: '{req.VisitorPlayerId}'). Dropping.");
                                    break;
                                }

                                if (_activeVisitRequests.TryRemove(visitCancel.RequestId, out _))
                                {
                                    req.Status = VisitStatus.Cancelled;
                                    Console.WriteLine($"[Visit] Request {visitCancel.RequestId} cancelled by authorized visitor {sender.PlayerId}.");
                                    // 해당 호스트 세션으로만 취소 통지
                                    if (!string.IsNullOrEmpty(req.HostPlayerId))
                                    {
                                        SendToPlayer(req.HostPlayerId, visitCancel);
                                    }
                                }
                            }
                            else
                            {
                                Console.WriteLine($"[Visit] Cancel ignored for unknown/completed request {visitCancel.RequestId}.");
                            }
                        }
                        break;

                    case PacketHeader.VisitResponse:
                        var visitRes = PacketSerializer.Deserialize<PKT_VisitResponse>(body);
                        if (visitRes != null)
                        {
                            if (_activeVisitRequests.TryGetValue(visitRes.RequestId, out var req))
                            {
                                // [권한 검증]: 실제 해당 호스트 플레이어만 응답 가능
                                if (!string.IsNullOrEmpty(req.HostPlayerId) && req.HostPlayerId != sender.PlayerId)
                                {
                                    Console.WriteLine($"[Visit] Unauthorized response from {sender.PlayerId} for request {visitRes.RequestId} owned by {req.HostPlayerId}. Dropping.");
                                    break;
                                }

                                // [상태 검증]: 오직 Pending 상태인 요청만 응답 수락 (취소되었거나 이미 완료된 요청의 중복 응답 방어)
                                if (req.Status != VisitStatus.Pending)
                                {
                                    Console.WriteLine($"[Visit] Request {visitRes.RequestId} is not Pending (Status: {req.Status}). Dropping duplicate/late response.");
                                    break;
                                }

                                req.Status = visitRes.IsAccepted ? VisitStatus.Accepted : VisitStatus.Denied;
                                Console.WriteLine($"[Visit] Response for {visitRes.RequestId}: Accepted={visitRes.IsAccepted}, Reason='{visitRes.RejectionReason}' to {req.VisitorPlayerId}");
                                SendToPlayer(req.VisitorPlayerId, visitRes);

                                // 완료된 요청은 메모리 누수 방지를 위해 활성 목록에서 즉시 제거
                                _activeVisitRequests.TryRemove(visitRes.RequestId, out _);
                            }
                            else
                            {
                                Console.WriteLine($"[Visit] Dropping response for unknown or already completed request {visitRes.RequestId}.");
                            }
                        }
                        break;

                    case PacketHeader.WarDeclarationRequest:
                        var warReq = PacketSerializer.Deserialize<PKT_WarDeclarationRequest>(body);
                        if (warReq != null)
                        {
                            DiplomacyManager.Instance.DeclareWar(warReq.AttackerFactionId, warReq.DefenderFactionId, Program.CurrentTick);
                        }
                        break;

                    case PacketHeader.NPCTradeReport:
                        var tradeReport = PacketSerializer.Deserialize<PKT_NPCTradeReport>(body);
                        if (tradeReport != null)
                        {
                            DynamicMarketManager.Instance.ProcessTrade(tradeReport, Program.CurrentTick);
                        }
                        break;

                    case PacketHeader.TaxPaymentSubmit:
                        var taxSubmit = PacketSerializer.Deserialize<PKT_TaxPaymentSubmit>(body);
                        if (taxSubmit != null)
                        {
                            FeudalManager.Instance.ProcessTaxPayment(taxSubmit, Program.CurrentTick);
                        }
                        break;

                    case PacketHeader.FiefTransferOffer:
                        var fiefOffer = PacketSerializer.Deserialize<PKT_FiefTransferOffer>(body);
                        if (fiefOffer != null)
                        {
                            var settlement = FeudalManager.Instance.GetSettlement(fiefOffer.SettlementId);
                            if (settlement == null)
                            {
                                Console.WriteLine($"[FiefTransfer] Offer rejected: Settlement '{fiefOffer.SettlementId}' not found.");
                                break;
                            }

                            // 제안 발신자가 실제 해당 영지의 현재 등록 영주인지 검증
                            if (!string.IsNullOrEmpty(settlement.LordPlayerId) && settlement.LordPlayerId != sender.PlayerId)
                            {
                                Console.WriteLine($"[FiefTransfer] Unauthorized offer attempt for '{fiefOffer.SettlementId}' by '{sender.PlayerId}' (actual lord: '{settlement.LordPlayerId}'). Rejected.");
                                break;
                            }

                            // 실행 권한 세션은 현재 영주의 세션으로 바인딩
                            FeudalManager.Instance.ExecuteFiefTransfer(fiefOffer, Program.CurrentTick, sender.SessionId);
                        }
                        break;

                    case PacketHeader.FiefTransferResult:
                        var fiefRes = PacketSerializer.Deserialize<PKT_FiefTransferResult>(body);
                        if (fiefRes != null)
                        {
                            Console.WriteLine($"[FiefTransfer] Result received: TransferId={fiefRes.TransferId}, Settlement={fiefRes.SettlementId}, Success={fiefRes.Success}, Pawns={fiefRes.TransferredPawnsCount}, Things={fiefRes.TransferredThingsCount}, Error='{fiefRes.ErrorMessage}'");
                            FeudalManager.Instance.ProcessFiefTransferResult(fiefRes, sender.SessionId);
                        }
                        break;

                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[TcpNetworkServer] Error handling packet {header}: {ex.Message}");
            }
        }

        /// <summary>
        /// 특정 플레이어가 접속 종료 시 해당 플레이어가 관여된 모든 대기 중인(Pending) 방문 요청 정리
        /// </summary>
        private void CleanupVisitRequestsForSession(string playerId)
        {
            if (string.IsNullOrEmpty(playerId)) return;

            foreach (var kvp in _activeVisitRequests)
            {
                var req = kvp.Value;
                if (req.VisitorPlayerId == playerId)
                {
                    if (_activeVisitRequests.TryRemove(req.RequestId, out _))
                    {
                        req.Status = VisitStatus.Cancelled;
                        if (!string.IsNullOrEmpty(req.HostPlayerId))
                        {
                            SendToPlayer(req.HostPlayerId, new PKT_VisitCancel(req.RequestId, req.VisitorPlayerId, req.TargetSettlementId));
                        }
                    }
                }
                else if (req.HostPlayerId == playerId)
                {
                    if (_activeVisitRequests.TryRemove(req.RequestId, out _))
                    {
                        req.Status = VisitStatus.Denied;
                        if (!string.IsNullOrEmpty(req.VisitorPlayerId))
                        {
                            SendToPlayer(req.VisitorPlayerId, new PKT_VisitResponse(req.RequestId, req.TargetSettlementId, req.VisitorPlayerId, false, "영주 연결 끊김 (오프라인)"));
                        }
                    }
                }
            }
        }
    }
}
