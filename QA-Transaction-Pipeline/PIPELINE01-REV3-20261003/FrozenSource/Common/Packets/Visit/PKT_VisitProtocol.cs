using System;
using WarEconomy.Common.Models;

namespace WarEconomy.Common.Packets.Visit
{
    /// <summary>
    /// 타 세력 기지 방문 요청 패킷 (방문자 -> 서버 -> 기지 영주)
    /// </summary>
    public class PKT_VisitRequest : IPacket
    {
        public PacketHeader Header => PacketHeader.VisitRequest;

        public VisitRequestData RequestData { get; set; } = new VisitRequestData();

        public PKT_VisitRequest() { }

        public PKT_VisitRequest(VisitRequestData requestData)
        {
            RequestData = requestData;
        }
    }

    /// <summary>
    /// 영주가 수락하기 전, 방문자가 요청을 철회/취소하는 패킷 (방문자 -> 서버 -> 영주)
    /// </summary>
    public class PKT_VisitCancel : IPacket
    {
        public PacketHeader Header => PacketHeader.VisitCancel;

        public string RequestId { get; set; } = string.Empty;
        public string VisitorPlayerId { get; set; } = string.Empty;
        public string TargetSettlementId { get; set; } = string.Empty;

        public PKT_VisitCancel() { }

        public PKT_VisitCancel(string requestId, string visitorPlayerId, string targetSettlementId)
        {
            RequestId = requestId;
            VisitorPlayerId = visitorPlayerId;
            TargetSettlementId = targetSettlementId;
        }
    }

    /// <summary>
    /// 기지 영주의 방문 요청 승인/거절 응답 패킷 (영주 -> 서버 -> 방문자)
    /// </summary>
    public class PKT_VisitResponse : IPacket
    {
        public PacketHeader Header => PacketHeader.VisitResponse;

        public string RequestId { get; set; } = string.Empty;
        public string TargetSettlementId { get; set; } = string.Empty;
        public string VisitorPlayerId { get; set; } = string.Empty;
        public bool IsAccepted { get; set; }
        public string RejectionReason { get; set; } = string.Empty;

        public PKT_VisitResponse() { }

        public PKT_VisitResponse(string requestId, string targetSettlementId, string visitorPlayerId, bool isAccepted, string rejectionReason = "")
        {
            RequestId = requestId;
            TargetSettlementId = targetSettlementId;
            VisitorPlayerId = visitorPlayerId;
            IsAccepted = isAccepted;
            RejectionReason = rejectionReason;
        }
    }
}
