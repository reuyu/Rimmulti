using System;

namespace WarEconomy.Common.Packets.Diplomacy
{
    public enum AllianceAction
    {
        Request = 0,
        Accept = 1,
        Deny = 2,
        Break = 3
    }

    /// <summary>
    /// 동맹 신청, 수락, 파기 처리 패킷
    /// </summary>
    public class PKT_AllianceAction : IPacket
    {
        public PacketHeader Header => PacketHeader.AllianceRequest;

        public AllianceAction Action { get; set; }
        public string SenderFactionId { get; set; } = string.Empty;
        public string TargetFactionId { get; set; } = string.Empty;

        // 동맹 재신청 쿨타임: 인게임 3일 (180,000 월드틱)
        public const long ReapplyCooldownTicks = 180000;

        public PKT_AllianceAction() { }

        public PKT_AllianceAction(AllianceAction action, string sender, string target)
        {
            Action = action;
            SenderFactionId = sender;
            TargetFactionId = target;
        }
    }

    /// <summary>
    /// 평화 방문 인스턴스 내 선제 공격 시 배신자 세력 낙인 브로드캐스트 패킷
    /// </summary>
    public class PKT_BetrayalNotification : IPacket
    {
        public PacketHeader Header => PacketHeader.BetrayalNotification;

        public string BetrayerFactionId { get; set; } = string.Empty;
        public string VictimFactionId { get; set; } = string.Empty;
        public string IncidentSettlementId { get; set; } = string.Empty;
        public long BetrayalWorldTick { get; set; }

        public PKT_BetrayalNotification() { }

        public PKT_BetrayalNotification(string betrayer, string victim, string settlementId, long tick)
        {
            BetrayerFactionId = betrayer;
            VictimFactionId = victim;
            IncidentSettlementId = settlementId;
            BetrayalWorldTick = tick;
        }
    }
}
