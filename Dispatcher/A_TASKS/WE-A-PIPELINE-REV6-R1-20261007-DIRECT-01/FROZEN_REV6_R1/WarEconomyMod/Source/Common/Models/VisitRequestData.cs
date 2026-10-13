using System;

namespace WarEconomy.Common.Models
{
    public enum VisitStatus
    {
        Pending = 0,    // 요청 후 대기 중
        Accepted = 1,   // 영주 수락 (전술 평화 인스턴스 생성/진입 허용)
        Denied = 2,     // 영주 거절
        Cancelled = 3,  // 요청자(방문객)가 수락 전 자율 철회/취소
        Expired = 4     // 응답 시간 초과 (자동 취소)
    }

    /// <summary>
    /// 정착지 방문 프로토콜 상태 데이터 (취소 기능 포함)
    /// </summary>
    public class VisitRequestData
    {
        public string RequestId { get; set; } = string.Empty;
        public string VisitorPlayerId { get; set; } = string.Empty;
        public string VisitorFactionId { get; set; } = string.Empty;
        public string CaravanId { get; set; } = string.Empty;

        public string TargetSettlementId { get; set; } = string.Empty;
        public string HostPlayerId { get; set; } = string.Empty;

        public VisitStatus Status { get; set; } = VisitStatus.Pending;

        public long CreatedWorldTick { get; set; }
        public long ExpireWorldTick { get; set; }

        public VisitRequestData() { }

        public VisitRequestData(string requestId, string visitorPlayerId, string visitorFactionId, string targetSettlementId, string hostPlayerId = "", string caravanId = "", long currentTick = 0)
        {
            RequestId = requestId;
            VisitorPlayerId = visitorPlayerId;
            VisitorFactionId = visitorFactionId;
            TargetSettlementId = targetSettlementId;
            HostPlayerId = hostPlayerId;
            CaravanId = caravanId;
            CreatedWorldTick = currentTick;
            ExpireWorldTick = currentTick + 54000;
        }

        /// <summary>
        /// 요청자 취소(Cancel) 처리: 상대 수락 전 언제든 철회 가능
        /// </summary>
        public bool TryCancel(string requestingPlayerId)
        {
            if (VisitorPlayerId != requestingPlayerId) return false;
            if (Status != VisitStatus.Pending) return false;

            Status = VisitStatus.Cancelled;
            return true;
        }
    }
}
