using System;
using System.Collections.Generic;

namespace WarEconomy.Common.Models
{
    public enum TaxStatus
    {
        Exempt = 0,      // 면세
        Pending = 1,     // 징수 상단 도착/납부 대기 중
        Paid = 2,        // 세금 완납
        Delinquent = 3   // 세금 체납 (거부 또는 기한 초과)
    }

    /// <summary>
    /// 영지별 세금 부과 및 체납 상태 정보 (Thread-Safe)
    /// </summary>
    public class TaxDelinquencyState
    {
        private readonly object _lock = new object();

        public string SettlementId { get; set; } = string.Empty;
        public string FiefLordPlayerId { get; set; } = string.Empty;
        public string OverlordPlayerId { get; set; } = string.Empty;  // 세금을 부과한 상위 영주

        public TaxStatus Status { get; set; } = TaxStatus.Exempt;

        // 세금 요구 목록 (예: "Silver": 1000, "Gold": 50, "Medicine": 20)
        public Dictionary<string, int> DemandedResources { get; set; } = new Dictionary<string, int>();

        public long DueWorldTick { get; set; }          // 납부 기한 (월드 3배속 틱 기준)
        public long LastPaidWorldTick { get; set; }
        public int ConsecutiveDelinquentCount { get; set; } = 0; // 연속 체납 횟수

        public string ActiveTaxCaravanId { get; set; } = string.Empty; // 현재 파견 중인 세금 징수 상단 ID

        /// <summary>
        /// 세금 거부 또는 기한 만료 시 체납 플래그 전환 (스레드 안전)
        /// </summary>
        public void MarkDelinquent()
        {
            lock (_lock)
            {
                Status = TaxStatus.Delinquent;
                ConsecutiveDelinquentCount++;
            }
        }

        /// <summary>
        /// 세금 완납 처리 (스레드 안전)
        /// </summary>
        public void MarkPaid(long currentWorldTick)
        {
            lock (_lock)
            {
                Status = TaxStatus.Paid;
                LastPaidWorldTick = currentWorldTick;
                ConsecutiveDelinquentCount = 0;
                ActiveTaxCaravanId = string.Empty;
            }
        }

        public TaxDelinquencyState CloneSnapshot()
        {
            lock (_lock)
            {
                return new TaxDelinquencyState
                {
                    SettlementId = this.SettlementId,
                    FiefLordPlayerId = this.FiefLordPlayerId,
                    OverlordPlayerId = this.OverlordPlayerId,
                    Status = this.Status,
                    DemandedResources = new Dictionary<string, int>(this.DemandedResources),
                    DueWorldTick = this.DueWorldTick,
                    LastPaidWorldTick = this.LastPaidWorldTick,
                    ConsecutiveDelinquentCount = this.ConsecutiveDelinquentCount,
                    ActiveTaxCaravanId = this.ActiveTaxCaravanId
                };
            }
        }
    }
}
