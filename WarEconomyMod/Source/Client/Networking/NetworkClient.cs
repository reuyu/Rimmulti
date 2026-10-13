using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using Verse;
using WarEconomy.Client.Fief;
using WarEconomy.Client.Time;
using WarEconomy.Client.UI;
using WarEconomy.Client.Threading;
using WarEconomy.Common.Packets;
using WarEconomy.Common.Packets.Auth;
using WarEconomy.Common.Packets.Diplomacy;
using WarEconomy.Common.Packets.Economy;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets.Vision;
using WarEconomy.Common.Packets.Visit;
using WarEconomy.Common.Packets.World;

namespace WarEconomy.Client.Networking
{
    /// <summary>
    /// 클라이언트 비동기 TCP 네트워크 관리자.
    /// 세션 격리(SessionId)를 통해 재연결 시 이전 수신 루프의 간섭을 원천 차단하고,
    /// 백그라운드 수신 스레드에서 수신된 패킷을 MainThreadQueue로 라우팅하여
    /// Unity 메인 스레드 안전성(Thread-Safety)을 100% 보장함.
    /// </summary>
    public class NetworkClient
    {
        private static NetworkClient? _instance;
        public static NetworkClient Instance => _instance ??= new NetworkClient();

        private TcpClient? _tcpClient;
        private NetworkStream? _stream;
        private readonly PacketReceiver _receiver = new PacketReceiver();
        private CancellationTokenSource? _cts;

        // [세션 격리]: 연결 시마다 고유 SessionId 부여
        public string CurrentSessionId { get; private set; } = string.Empty;

        public bool IsConnected => _tcpClient != null && _tcpClient.Connected && _cts != null && !_cts.IsCancellationRequested;
        public string LocalPlayerId { get; set; } = "Player_" + Guid.NewGuid().ToString().Substring(0, 6);

        public event Action? OnConnected;
        public event Action? OnDisconnected;

        public async Task ConnectAsync(string host, int port)
        {
            try
            {
                // 이전 연결 완전 종료
                Disconnect();

                string newSessionId = Guid.NewGuid().ToString("N");
                CurrentSessionId = newSessionId;

                _tcpClient = new TcpClient();
                await _tcpClient.ConnectAsync(host, port);
                _stream = _tcpClient.GetStream();
                _cts = new CancellationTokenSource();

                Log.Message($"[NetworkClient] Connected to Dedicated Server at {host}:{port} (Session: {newSessionId})");
                OnConnected?.Invoke();

                // [핸드셰이크] 연결 성공 직후 닉네임과 클라이언트 버전을 서버로 발송
                SendHandshake();

                _ = Task.Run(() => ReceiveLoop(newSessionId, _cts.Token));
            }
            catch (Exception ex)
            {
                Log.Error($"[NetworkClient] Connection failed: {ex.Message}");
            }
        }

        public void SendHandshake()
        {
            if (!IsConnected) return;

            string nick = LocalPlayerId;
            if (string.IsNullOrEmpty(nick) || nick.StartsWith("Player_"))
            {
                string persona = SteamUtility.SteamPersonaName;
                if (!string.IsNullOrEmpty(persona) && persona != "???")
                {
                    nick = persona;
                }
                else
                {
                    nick = Environment.UserName;
                }
                if (string.IsNullOrEmpty(nick)) nick = "Colonist";
                LocalPlayerId = nick;
            }

            string version = typeof(NetworkClient).Assembly.GetName().Version?.ToString() ?? "1.6.0";
            var handshake = new PKT_PlayerHandshake(nick, version, LocalPlayerId);
            SendPacket(handshake);
            Log.Message($"[NetworkClient] Sent Handshake (Nickname: {nick}, Version: {version})");

            // 연결 성공 시 메인 스레드에서 1회 로컬 정착지 등록 시도
            MainThreadQueue.Enqueue(() => RegisterAllLocalSettlements());
        }

        /// <summary>
        /// 연결 해제. targetSessionId가 주어진 경우 일치할 때만 해제하여 이전 루프의 오작동 방지
        /// </summary>
        public void Disconnect(string? targetSessionId = null)
        {
            if (targetSessionId != null && CurrentSessionId != targetSessionId) return;

            CurrentSessionId = string.Empty;
            _cts?.Cancel();
            try { _stream?.Close(); } catch { }
            try { _tcpClient?.Close(); } catch { }
            _tcpClient = null;
            _stream = null;
            Patches.SettlementBorderProximityValidator.Clear();
            _registeredSettlementIds.Clear();
            OnDisconnected?.Invoke();
        }

        public void SendPacket<T>(T packet) where T : IPacket
        {
            if (!IsConnected || _stream == null) return;

            try
            {
                byte[] raw = PacketSerializer.Serialize(packet);
                _stream.Write(raw, 0, raw.Length);
            }
            catch (Exception ex)
            {
                Log.Error($"[NetworkClient] SendPacket failed: {ex.Message}");
                Disconnect(CurrentSessionId);
            }
        }

        private async Task ReceiveLoop(string sessionId, CancellationToken token)
        {
            byte[] readBuffer = new byte[8192];

            while (!token.IsCancellationRequested && IsConnected && _stream != null)
            {
                // [세션 격리 가드]: 새로운 연결이 시작되었으면 이전 루프 즉시 종료
                if (CurrentSessionId != sessionId) break;

                try
                {
                    int bytesRead = await _stream.ReadAsync(readBuffer, 0, readBuffer.Length, token);
                    if (bytesRead == 0)
                    {
                        Log.Warning($"[NetworkClient] Server disconnected gracefully (Session: {sessionId}).");
                        break;
                    }

                    if (CurrentSessionId != sessionId) break;

                    var packets = _receiver.ReceiveBytes(readBuffer, bytesRead);
                    foreach (var (header, body) in packets)
                    {
                        // [핵심] 수신된 패킷 처리를 반드시 Unity 메인 스레드 큐로 디스패치!
                        MainThreadQueue.Enqueue(() => DispatchPacketOnMainThread(header, body));
                    }
                }
                catch (Exception ex)
                {
                    if (!token.IsCancellationRequested && CurrentSessionId == sessionId)
                    {
                        Log.Error($"[NetworkClient] Receive loop error: {ex.Message}");
                    }
                    break;
                }
            }

            Disconnect(sessionId);
        }

        /// <summary>
        /// Unity 메인 스레드에서 안전하게 실행되는 패킷 디스패처
        /// </summary>
        private void DispatchPacketOnMainThread(PacketHeader header, byte[] body)
        {
            try
            {
                switch (header)
                {
                    case PacketHeader.WorldTickSync:
                        var tickPacket = PacketSerializer.Deserialize<PKT_WorldTickSync>(body);
                        if (tickPacket != null)
                        {
                            ClientWorldTickManager.Instance.ApplyServerSync(tickPacket);
                        }
                        break;

                    case PacketHeader.SettlementListSync:
                        var settleListPkt = PacketSerializer.Deserialize<PKT_SettlementListSync>(body);
                        if (settleListPkt != null)
                        {
                            // 서버로부터 수신된 영지 목록 스냅샷만 갱신 (역등록 무한 루프 원천 차단)
                            Patches.SettlementBorderProximityValidator.UpdateSettlements(settleListPkt.Settlements);
                        }
                        break;

                    case PacketHeader.FiefTransferExecute:

                        var fiefExec = PacketSerializer.Deserialize<PKT_FiefTransferExecute>(body);
                        if (fiefExec != null)
                        {
                            // 메인 스레드에서 안전하게 폰 및 맵 소유권 원자적 이전 실행
                            AtomicFiefTransferExecutor.Execute(fiefExec);
                        }
                        break;

                    case PacketHeader.VisitRequest:
                        var visitReq = PacketSerializer.Deserialize<PKT_VisitRequest>(body);
                        if (visitReq != null)
                        {
                            // 영주 화면에 방문 승인/거절 대화상자 노출
                            Find.WindowStack?.Add(new Dialog_VisitRequest(visitReq.RequestData));
                        }
                        break;

                    case PacketHeader.VisitCancel:
                        var visitCancel = PacketSerializer.Deserialize<PKT_VisitCancel>(body);
                        if (visitCancel != null)
                        {
                            Dialog_VisitRequest.HandleCancel(visitCancel);
                        }
                        break;

                    case PacketHeader.VisitResponse:
                        var visitRes = PacketSerializer.Deserialize<PKT_VisitResponse>(body);
                        if (visitRes != null)
                        {
                            Dialog_VisitWait.HandleResponse(visitRes);
                        }
                        break;

                    case PacketHeader.WarStateUpdate:
                        var warState = PacketSerializer.Deserialize<PKT_WarStateUpdate>(body);
                        if (warState != null)
                        {
                            string msg = warState.WarData.State == Common.Models.WarState.Active
                                ? $"[전쟁 발발] {warState.WarData.AttackerFactionId} 세력이 {warState.WarData.DefenderFactionId} 세력에 전면전을 개시했습니다!"
                                : $"[선전포고] {warState.WarData.AttackerFactionId} 세력이 {warState.WarData.DefenderFactionId} 세력에 선전포고했습니다! (유예 대기 중)";
                            Messages.Message(msg, MessageTypeDefOf.ThreatBig, true);
                        }
                        break;

                    case PacketHeader.TaxDelinquencyBroadcast:
                        var taxPkt = PacketSerializer.Deserialize<PKT_TaxDelinquencyBroadcast>(body);
                        if (taxPkt != null && taxPkt.DelinquencyState.Status == Common.Models.TaxStatus.Delinquent)
                        {
                            Messages.Message($"[세금 체납] 영지 {taxPkt.DelinquencyState.SettlementId}가 세금 납부를 거부하여 체납 상태로 전환되었습니다!", MessageTypeDefOf.NegativeEvent, true);
                        }
                        break;

                    case PacketHeader.DynamicMarketSync:
                        var marketPkt = PacketSerializer.Deserialize<PKT_DynamicMarketSync>(body);
                        if (marketPkt != null)
                        {
                            Economy.ClientMarketManager.Instance.ApplyMarketSync(marketPkt);
                        }
                        break;

                    case PacketHeader.FogOfWarSync:
                        var fogPkt = PacketSerializer.Deserialize<PKT_FogOfWarSync>(body);
                        if (fogPkt != null)
                        {
                            Patches.ClientFogOfWarManager.ApplyFogSync(fogPkt);
                        }
                        break;
                }
            }
            catch (Exception ex)
            {
                Log.Error($"[NetworkClient] Error dispatching packet {header}: {ex}");
            }
        }

        private readonly HashSet<string> _registeredSettlementIds = new HashSet<string>();

        /// <summary>
        /// 현재 게임에 존재하는 플레이어 정착지들을 서버에 등록 (이미 등록된 영지는 중복 전송 방지)
        /// </summary>
        public void RegisterAllLocalSettlements()
        {
            if (!IsConnected || Current.ProgramState != ProgramState.Playing || Find.WorldObjects?.Settlements == null) return;

            foreach (var settlement in Find.WorldObjects.Settlements)
            {
                if (settlement != null && settlement.Faction != null && settlement.Faction.IsPlayer)
                {
                    string settlementId = settlement.GetUniqueLoadID();
                    if (_registeredSettlementIds.Contains(settlementId)) continue; // 이미 등록 완료된 정착지는 중복 전송 차단

                    string name = settlement.LabelCap;
                    string factionId = settlement.Faction.GetUniqueLoadID();
                    string lordPlayerId = LocalPlayerId;
                    var tile = settlement.Tile;

                    int layerId = 0;
                    try { layerId = tile.Layer?.LayerID ?? 0; } catch { }

                    var data = new SettlementData(settlementId, name, tile.tileId, factionId, lordPlayerId, NobilityTitle.Baron)
                    {
                        LayerId = layerId
                    };
                    _registeredSettlementIds.Add(settlementId);
                    SendPacket(new PKT_SettlementRegister(data));
                    Log.Message($"[WarEconomy] Registered existing settlement '{name}' ({settlementId}) to server.");
                }
            }
        }
    }
}
