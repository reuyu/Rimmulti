using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using WarEconomy.Common.Models;
using WarEconomy.Common.Models.Enums;
using WarEconomy.Common.Packets.Feudal;
using WarEconomy.Common.Packets.World;
using WarEconomy.Server.Time;

namespace WarEconomy.Server.Managers
{
    public class PendingTransferState
    {
        public string TransferId { get; set; } = string.Empty;
        public string SettlementId { get; set; } = string.Empty;
        public string PreviousLord { get; set; } = string.Empty;
        public string NewLord { get; set; } = string.Empty;
        public string NewFaction { get; set; } = string.Empty;
        public NobilityTitle GrantedTitle { get; set; }
        public string AuthorizedSessionId { get; set; } = string.Empty;
        public long CreatedTick { get; set; }
    }

    /// <summary>
    /// 서버 측 봉건 세금 징수, 체납 판정 및 영지 양도 총괄 관리자
    /// </summary>
    public class FeudalManager : ITickableWorldSystem
    {
        private static FeudalManager? _instance;
        public static FeudalManager Instance => _instance ??= new FeudalManager();

        // 영지별 세금 상태: Key = SettlementId
        private readonly ConcurrentDictionary<string, TaxDelinquencyState> _taxStates = new ConcurrentDictionary<string, TaxDelinquencyState>();

        // 전체 등록 영지: Key = SettlementId
        private readonly ConcurrentDictionary<string, SettlementData> _settlements = new ConcurrentDictionary<string, SettlementData>();

        // 대기 중인 양도 트랜잭션 (TransferId 기준)
        private readonly ConcurrentDictionary<string, PendingTransferState> _pendingTransfersByTransferId 
            = new ConcurrentDictionary<string, PendingTransferState>();

        // 영지별 현재 활성 양도 트랜잭션 매핑 (중복 덮어쓰기 방어)
        private readonly ConcurrentDictionary<string, string> _activeTransferBySettlement 
            = new ConcurrentDictionary<string, string>();

        public event Action<PKT_TaxDelinquencyBroadcast>? OnTaxDelinquencyChanged;
        public event Action<PKT_FiefTransferExecute>? OnFiefTransferExecuted;
        public event Action<PKT_SettlementListSync>? OnSettlementListUpdated;

        public void InitializeDefaultSettlements()
        {
            if (_settlements.IsEmpty)
            {
                RegisterSettlement(new SettlementData("NPC_Empire_Capital", "제국 수도 (Imperial Capital)", 150, "Empire", "NPC_Emperor", NobilityTitle.King, 0));
                RegisterSettlement(new SettlementData("NPC_Outlander_Hub", "외지인 자유 교역항 (Outlander Port)", 220, "OutlanderCivil", "NPC_Mayor", NobilityTitle.Baron, 0));
                Console.WriteLine($"[Feudal] Initialized {_settlements.Count} default world settlements.");
            }
        }

        /// <summary>
        /// 영지 등록 및 갱신. 멱등성을 보장하여 변경 사항이 없을 때는 브로드캐스트를 생략하며,
        /// 정식 양도 절차(TransferOwnership) 없이 LordPlayerId가 임의로 변경되는 것을 차단.
        /// </summary>
        public bool RegisterSettlement(SettlementData data, bool allowOwnerChange = false)
        {
            if (data == null || string.IsNullOrEmpty(data.SettlementId)) return false;

            if (_settlements.TryGetValue(data.SettlementId, out var existing))
            {
                // 소유권 덮어쓰기 방어: 정식 양도 절차 없이 기존 영주 ID를 덮어쓰는 시도 거부
                if (!allowOwnerChange && !string.IsNullOrEmpty(existing.LordPlayerId) && existing.LordPlayerId != data.LordPlayerId)
                {
                    Console.WriteLine($"[Feudal] RegisterSettlement rejected owner overwrite for '{data.SettlementId}' (existing: '{existing.LordPlayerId}', attempted: '{data.LordPlayerId}').");
                    return false;
                }

                // 멱등성 검증: 동일한 속성으로 재등록 시 브로드캐스트 이벤트 발행 건너뜀 (무한 루프 방지)
                bool isUnchanged = existing.Name == data.Name &&
                                   existing.TileId == data.TileId &&
                                   existing.FactionId == data.FactionId &&
                                   existing.LordPlayerId == data.LordPlayerId &&
                                   existing.LordTitle == data.LordTitle &&
                                   existing.LayerId == data.LayerId;

                if (isUnchanged)
                {
                    return false;
                }

                _settlements[data.SettlementId] = data;
                OnSettlementListUpdated?.Invoke(new PKT_SettlementListSync(GetAllSettlements()));
                return true;
            }
            else
            {
                _settlements[data.SettlementId] = data;
                OnSettlementListUpdated?.Invoke(new PKT_SettlementListSync(GetAllSettlements()));
                return true;
            }
        }

        public SettlementData? GetSettlement(string settlementId)
        {
            return _settlements.TryGetValue(settlementId, out var s) ? s : null;
        }

        public List<SettlementData> GetAllSettlements()
        {
            return new List<SettlementData>(_settlements.Values);
        }



        /// <summary>
        /// 상위 영주의 세금 징수 상단 파견 처리
        /// </summary>
        public void DispatchTaxCaravan(PKT_TaxCaravanDispatch dispatch, long currentTick)
        {
            var taxState = _taxStates.GetOrAdd(dispatch.TargetSettlementId, id => new TaxDelinquencyState
            {
                SettlementId = id,
                Status = TaxStatus.Pending
            });

            taxState.OverlordPlayerId = dispatch.OverlordPlayerId;
            taxState.ActiveTaxCaravanId = dispatch.CaravanId;
            taxState.DemandedResources = dispatch.DemandedTaxes;
            taxState.Status = TaxStatus.Pending;

            // 납부 기한: 인게임 3일 (180,000 월드틱)
            taxState.DueWorldTick = currentTick + 180000;

            Console.WriteLine($"[Feudal] Tax caravan {dispatch.CaravanId} dispatched to {dispatch.TargetSettlementId} by Overlord {dispatch.OverlordPlayerId}. Due at: {taxState.DueWorldTick}");
        }

        /// <summary>
        /// 하위 영지의 세금 납부 결과 처리
        /// </summary>
        public void ProcessTaxPayment(PKT_TaxPaymentSubmit payment, long currentTick)
        {
            if (!_taxStates.TryGetValue(payment.SettlementId, out var state)) return;

            if (payment.IsPaid)
            {
                state.MarkPaid(currentTick);
                Console.WriteLine($"[Feudal] Taxes paid in full by settlement {payment.SettlementId}!");
            }
            else
            {
                state.MarkDelinquent();
                Console.WriteLine($"[Feudal] Taxes REFUSED by settlement {payment.SettlementId}! Marked as DELINQUENT.");
            }

            OnTaxDelinquencyChanged?.Invoke(new PKT_TaxDelinquencyBroadcast(state.CloneSnapshot()));
        }

        /// <summary>
        /// 영지 양도 실행 지시 (클라이언트 확인 전까지 Pending 상태 유지)
        /// </summary>
        public void ExecuteFiefTransfer(PKT_FiefTransferOffer offer, long currentTick, string? authorizedSessionId = null)
        {
            if (!_settlements.TryGetValue(offer.SettlementId, out var settlement)) return;

            // 제안 발신자 소유권 검증: CurrentLordPlayerId가 실제 현재 등록 영주와 일치해야 함
            if (!string.IsNullOrEmpty(settlement.LordPlayerId) && settlement.LordPlayerId != offer.CurrentLordPlayerId)
            {
                Console.WriteLine($"[Feudal] Transfer offer rejected: CurrentLord '{offer.CurrentLordPlayerId}' does not match registered lord '{settlement.LordPlayerId}' of '{offer.SettlementId}'.");
                return;
            }

            lock (_activeTransferBySettlement)
            {
                // 중복/경쟁 상태 방어: 영지에 이미 진행 중인 활성 트랜잭션이 있으면 중복 양도 제안 차단
                if (_activeTransferBySettlement.TryGetValue(offer.SettlementId, out var activeTransferId))
                {
                    if (_pendingTransfersByTransferId.ContainsKey(activeTransferId))
                    {
                        Console.WriteLine($"[Feudal] Settlement '{offer.SettlementId}' already has an ongoing transfer ({activeTransferId}). Rejecting overlapping transfer offer.");
                        return;
                    }
                }

                string transferId = !string.IsNullOrEmpty(offer.TransferId) ? offer.TransferId : Guid.NewGuid().ToString();
                string prevLord = settlement.LordPlayerId;

                var pendingState = new PendingTransferState
                {
                    TransferId = transferId,
                    SettlementId = offer.SettlementId,
                    PreviousLord = prevLord,
                    NewLord = offer.TargetLordPlayerId,
                    NewFaction = offer.NewFactionId,
                    GrantedTitle = offer.GrantedTitle,
                    AuthorizedSessionId = authorizedSessionId ?? string.Empty,
                    CreatedTick = currentTick
                };

                _pendingTransfersByTransferId[transferId] = pendingState;
                _activeTransferBySettlement[offer.SettlementId] = transferId;

                Console.WriteLine($"[Feudal] Fief Transfer Initiated: TransferId={transferId}, Settlement={offer.SettlementId} (from {prevLord} to {offer.TargetLordPlayerId}, Title: {offer.GrantedTitle}). Waiting for client execution...");

                var execPacket = new PKT_FiefTransferExecute(
                    offer.SettlementId,
                    settlement.TileId,
                    prevLord,
                    offer.TargetLordPlayerId,
                    offer.NewFactionId,
                    offer.GrantedTitle,
                    currentTick,
                    transferId
                );

                OnFiefTransferExecuted?.Invoke(execPacket);
            }
        }

        /// <summary>
        /// 클라이언트의 영지 양도 실행 결과 수신 (양방향 핸드셰이크)
        /// 트랜잭션 ID 및 권한 세션 일치 여부를 검증한 후, 성공 시에만 최종 소유권 확정
        /// </summary>
        public void ProcessFiefTransferResult(PKT_FiefTransferResult result, string? senderSessionId = null)
        {
            // 1. 비호스트 클라이언트의 단순 맵 미로드 알림은 실패로 간주하지 않고 안전하게 무시
            if (!string.IsNullOrEmpty(result.ErrorMessage) && result.ErrorMessage.Contains("not loaded locally"))
            {
                Console.WriteLine($"[Feudal] Ignored map-not-loaded notification for settlement {result.SettlementId} from non-host client.");
                return;
            }

            // 2. 트랜잭션 매칭: TransferId 필수 엄격 검증 (폴백 완전 제거)
            if (string.IsNullOrEmpty(result.TransferId))
            {
                Console.WriteLine($"[Feudal] Result rejected: Missing TransferId for settlement '{result.SettlementId}'.");
                return;
            }

            if (!_pendingTransfersByTransferId.TryGetValue(result.TransferId, out var pending) || pending == null)
            {
                Console.WriteLine($"[Feudal] No pending transfer found for TransferId '{result.TransferId}' (Settlement: '{result.SettlementId}'). Ignoring.");
                return;
            }

            // 영지 일치 검증
            if (pending.SettlementId != result.SettlementId)
            {
                Console.WriteLine($"[Feudal] TransferId '{result.TransferId}' settlement mismatch (expected '{pending.SettlementId}', got '{result.SettlementId}'). Ignoring.");
                return;
            }

            // 3. 발신 세션 권한 검증 (지정된 실행 세션이 있는 경우)
            if (!string.IsNullOrEmpty(pending.AuthorizedSessionId) && !string.IsNullOrEmpty(senderSessionId))
            {
                if (pending.AuthorizedSessionId != senderSessionId)
                {
                    Console.WriteLine($"[Feudal] Unauthorized result from session {senderSessionId} for transfer {pending.TransferId} (authorized: {pending.AuthorizedSessionId}). Ignoring.");
                    return;
                }
            }

            // 4. 대기 중인 트랜잭션 원자적 제거
            if (!_pendingTransfersByTransferId.TryRemove(pending.TransferId, out _))
            {
                // 이미 다른 스레드에서 처리 완료됨
                return;
            }
            _activeTransferBySettlement.TryRemove(pending.SettlementId, out _);

            if (_settlements.TryGetValue(pending.SettlementId, out var settlement))
            {
                if (result.Success)
                {
                    // 클라이언트 실행 성공 시 비로소 서버 소유권 확정!
                    settlement.TransferOwnership(pending.NewLord, pending.GrantedTitle, pending.NewFaction);
                    Console.WriteLine($"[Feudal] Fief Transfer CONFIRMED for Settlement {pending.SettlementId} (TransferId: {pending.TransferId})! Lord: '{pending.NewLord}', Faction: '{pending.NewFaction}' (Pawns: {result.TransferredPawnsCount}, Things: {result.TransferredThingsCount})");
                    OnSettlementListUpdated?.Invoke(new PKT_SettlementListSync(GetAllSettlements()));
                }
                else
                {
                    // 실패 시 소유권 변경 없이 이전 영주 상태 보존 (롤백)
                    Console.WriteLine($"[Feudal] WARNING: Fief Transfer FAILED for Settlement {pending.SettlementId} (TransferId: {pending.TransferId})! Preserving former lord '{settlement.LordPlayerId}' and faction '{settlement.FactionId}'. Error: {result.ErrorMessage}");
                }
            }
        }


        /// <summary>
        /// 서버 3배속 월드 틱마다 납부 기한 초과 검사 및 자동 체납 전환
        /// </summary>
        public void OnWorldTick(long currentWorldTick)
        {
            foreach (var kvp in _taxStates)
            {
                var state = kvp.Value;
                if (state.Status == TaxStatus.Pending && currentWorldTick >= state.DueWorldTick)
                {
                    state.MarkDelinquent();
                    Console.WriteLine($"[Feudal] Settlement {state.SettlementId} missed tax deadline! Automatically marked as DELINQUENT.");
                    OnTaxDelinquencyChanged?.Invoke(new PKT_TaxDelinquencyBroadcast(state.CloneSnapshot()));
                }
            }
        }
    }
}
