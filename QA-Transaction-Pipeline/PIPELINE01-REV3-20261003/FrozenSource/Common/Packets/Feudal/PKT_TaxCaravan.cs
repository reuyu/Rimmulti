using System;
using System.Collections.Generic;
using WarEconomy.Common.Models;

namespace WarEconomy.Common.Packets.Feudal
{
    /// <summary>
    /// 세금 징수 상단(Tax Caravan) 파견 패킷 (상위 영주 -> 서버 -> 하위 영지)
    /// </summary>
    public class PKT_TaxCaravanDispatch : IPacket
    {
        public PacketHeader Header => PacketHeader.TaxCaravanDispatch;

        public string CaravanId { get; set; } = string.Empty;
        public string OverlordPlayerId { get; set; } = string.Empty;
        public string TargetSettlementId { get; set; } = string.Empty;
        public Dictionary<string, int> DemandedTaxes { get; set; } = new Dictionary<string, int>();

        public PKT_TaxCaravanDispatch() { }

        public PKT_TaxCaravanDispatch(string caravanId, string overlord, string targetSettlement, Dictionary<string, int> demandedTaxes)
        {
            CaravanId = caravanId;
            OverlordPlayerId = overlord;
            TargetSettlementId = targetSettlement;
            DemandedTaxes = demandedTaxes;
        }
    }

    /// <summary>
    /// 세금 납부 또는 거부 패킷 (하위 영지 -> 서버)
    /// </summary>
    public class PKT_TaxPaymentSubmit : IPacket
    {
        public PacketHeader Header => PacketHeader.TaxPaymentSubmit;

        public string SettlementId { get; set; } = string.Empty;
        public string FiefLordPlayerId { get; set; } = string.Empty;
        public bool IsPaid { get; set; } // true: 완납, false: 납부 거부(체납 전환)
        public Dictionary<string, int> PaidResources { get; set; } = new Dictionary<string, int>();

        public PKT_TaxPaymentSubmit() { }

        public PKT_TaxPaymentSubmit(string settlementId, string lordId, bool isPaid, Dictionary<string, int> paidResources)
        {
            SettlementId = settlementId;
            FiefLordPlayerId = lordId;
            IsPaid = isPaid;
            PaidResources = paidResources;
        }
    }

    /// <summary>
    /// 세금 체납(Tax Delinquent) 상태 브로드캐스트 (서버 -> 세력 관리창)
    /// </summary>
    public class PKT_TaxDelinquencyBroadcast : IPacket
    {
        public PacketHeader Header => PacketHeader.TaxDelinquencyBroadcast;

        public TaxDelinquencyState DelinquencyState { get; set; } = new TaxDelinquencyState();

        public PKT_TaxDelinquencyBroadcast() { }

        public PKT_TaxDelinquencyBroadcast(TaxDelinquencyState state)
        {
            DelinquencyState = state;
        }
    }
}
